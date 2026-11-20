"""Run the full 900-scene Track B pipeline: render, free the GPU, detect, sweep, calibrate.

Usage (it runs for hours, so launch it detached and tail the log):
    uv run python scripts/run_production.py > production.log 2>&1

Phases, in order:
    1. render     CARLA renders every manifest scene (planned first if missing).
    2. stop CARLA kill the simulator so the whole GPU is free for PyTorch (SD-003).
    3. detect     YOLO11m, then RT-DETR-L, over every rendered frame.
    4. sweep      Evaluate the policies over the corpus.
    5. calibrate  Fit the offline estimator on practice scenes and print the check.

A failed phase stops the run with a non-zero exit code. To resume, skip the
phases that already finished (--skip-render, --skip-detect). The sweep refuses to
overwrite its output folder, so rerun with a new --out or pass --overwrite-out,
which deletes the previous sweep output (only a folder holding run.json).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

# A sibling script. scripts/ is sys.path[0] when this file is run directly.
import fit_estimator

from evidence_resolution.calibration import split_by_value, split_scenes
from spike_dependence.double_fault import PairedErrorRecord
from spike_dependence.scoring import (
    AgentView,
    Detection,
    GroundTruthObject,
    paired_error_records,
)
from spike_dependence.scoring import BoundingBox as SpikeBox
from sweep.corpus import CorpusTask, load_tasks
from trace_contracts.observations import AgentFrameReport
from trace_contracts.scenario import DetectorPairing
from trace_contracts.truth import TruthObject

SCENES_PER_RENDER_CELL = 50  # 18 render cells x 50 = 900 scenes
CARLA_SHUTDOWN_WAIT_S = 5
IOU_THRESHOLD = 0.5
SWEEP_POLICIES = ("latest-report", "miss-risk")
SWEEP_CAMERA = {
    "--width-px": "800",
    "--height-px": "600",
    "--fov-degrees": "90",
    "--camera-height-m": "14",
}

Runner = Callable[..., subprocess.CompletedProcess]
Logger = Callable[[str], None]


class PipelineError(RuntimeError):
    """A pipeline phase failed; the run must stop rather than use partial output."""


def log(message: str) -> None:
    """Print one timestamped line and flush, so a tailed log stays current."""
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--corpus", type=Path, default=Path("artifacts/corpus_900"))
    parser.add_argument("--out", type=Path, default=Path("artifacts/corpus_900_eval"))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--seed", type=int, default=0, help="Calibration split seed")
    parser.add_argument(
        "--skip-render", action="store_true", help="Reuse the rendered frames"
    )
    parser.add_argument(
        "--skip-detect", action="store_true", help="Reuse the detector reports"
    )
    parser.add_argument(
        "--overwrite-out",
        action="store_true",
        help="Delete a previous sweep output at --out before the sweep",
    )
    return parser.parse_args(argv)


def module_command(module: str, *args: str) -> list[str]:
    """Return a command that runs `python -m module` in this interpreter."""
    return [sys.executable, "-m", module, *args]


def run_phase(name: str, command: Sequence[str], *, run: Runner, log: Logger) -> None:
    """Run one phase to completion, streaming its output, or raise PipelineError."""
    log(f"phase {name}: start")
    started = time.time()
    try:
        result = run(list(command), check=False)
    except OSError as error:
        raise PipelineError(f"{name} could not start: {error}") from error
    if result.returncode != 0:
        raise PipelineError(f"{name} failed with exit code {result.returncode}")
    log(f"phase {name}: done in {time.time() - started:.0f}s")


def stop_carla(
    *, run: Runner, sleep: Callable[[float], None], log: Logger, platform: str
) -> None:
    """Kill every CARLA process, then wait for the GPU to release its memory.

    CARLA and PyTorch compete for the same 8 GB of VRAM (SD-003), so detection
    must not start while the simulator still holds it. Killing is forceful
    because the render phase has already persisted everything it produced.
    "No process found" is fine: the server may already have exited.
    """
    if platform == "win32":
        command, acceptable = ["taskkill", "/F", "/T", "/IM", "CarlaUE4*"], {0, 128}
    else:
        command, acceptable = ["pkill", "-9", "-f", "CarlaUE4"], {0, 1}

    try:
        result = run(command, check=False, capture_output=True)
    except OSError as error:
        raise PipelineError(f"could not stop CARLA: {error}") from error
    if result.returncode not in acceptable:
        raise PipelineError(
            f"could not stop CARLA ({command[0]} exit code {result.returncode})"
        )
    log(f"CARLA stopped; waiting {CARLA_SHUTDOWN_WAIT_S}s for VRAM to be released")
    sleep(CARLA_SHUTDOWN_WAIT_S)


def check_out_is_removable(corpus: Path, out: Path) -> None:
    """Refuse to delete anything that is not a previous sweep output.

    Deletion is irreversible, so the folder must look like sweep output
    (it holds run.json) and must not overlap the corpus that feeds the sweep.
    """
    if not out.exists():
        return
    corpus, out = corpus.resolve(), out.resolve()
    if out == corpus or corpus in out.parents or out in corpus.parents:
        raise PipelineError(f"--out must be separate from the corpus: {out}")
    if not (out / "run.json").is_file():
        raise PipelineError(
            f"refusing to delete {out}: it is not sweep output (no run.json)"
        )


def _agent_view(report: AgentFrameReport, truth: Sequence[TruthObject]) -> AgentView:
    """Convert one corpus report and its truth into the spike scorer's types."""

    def box(raw: Any) -> SpikeBox:
        return SpikeBox(raw.x1, raw.y1, raw.x2, raw.y2)

    return AgentView(
        agent_id=report.source_id,
        visible_truth=[
            GroundTruthObject(t.object_id, t.label, box(t.box)) for t in truth
        ],
        detections=[
            Detection(d.label, d.confidence, box(d.box)) for d in report.detections
        ],
    )


def paired_records_by_pair(
    tasks: Sequence[CorpusTask], *, iou_threshold: float
) -> dict[tuple[str, str], list[PairedErrorRecord]]:
    """Group per-object error records by detector pair, keyed by scene id."""
    by_pair: dict[tuple[str, str], list[PairedErrorRecord]] = defaultdict(list)
    for task in tasks:
        view_a, view_b = (
            _agent_view(report, task.truth[report.report_id])
            for report in sorted(task.reports, key=lambda r: r.source_id)
        )
        by_pair[task.pairing.models].extend(
            paired_error_records(
                task.entry.scene_id, view_a, view_b, iou_threshold=iou_threshold
            )
        )
    return dict(by_pair)


def calibrate(corpus: Path, seed: int) -> None:
    """Fit the offline estimator on practice scenes and print how it holds up.

    Runs one random split, then one shift test per illumination, holding out
    every scene with that illumination. Prints only; writes nothing.
    """
    tasks = load_tasks(corpus, tuple(DetectorPairing))
    records = paired_records_by_pair(tasks, iou_threshold=IOU_THRESHOLD)
    illumination: Mapping[str, str] = {
        task.entry.scene_id: task.entry.render.illumination.value for task in tasks
    }
    scenes = sorted(illumination)

    fit_estimator.run_split(
        f"random split (seed {seed})", records, *split_scenes(scenes, seed=seed)
    )
    for held_out in sorted(set(illumination.values())):
        practice, exam = split_by_value(scenes, illumination, held_out=held_out)
        fit_estimator.run_split(
            f"shift test, exam = {held_out}", records, practice, exam
        )


def run_pipeline(
    args: argparse.Namespace,
    *,
    run: Runner = subprocess.run,
    sleep: Callable[[float], None] = time.sleep,
    log: Logger = log,
    calibrate: Callable[[Path, int], None] = calibrate,
) -> None:
    """Run every phase in order; raise PipelineError at the first failure."""
    corpus = str(args.corpus)
    if args.overwrite_out:
        check_out_is_removable(args.corpus, args.out)

    if not args.skip_render and not (args.corpus / "manifest.json").exists():
        plan_command = module_command(
            "scenario_gen",
            "--out",
            corpus,
            "--scenes-per-render-cell",
            str(SCENES_PER_RENDER_CELL),
        )
        run_phase("plan", plan_command, run=run, log=log)

    if args.skip_render:
        log("phase render: skipped")
    else:
        render_command = module_command(
            "scenario_gen.runner", "--corpus", corpus, "--skip-detect"
        )
        run_phase("render", render_command, run=run, log=log)

    if args.skip_detect:
        log("phase detect: skipped")
    else:
        # Only detection needs the GPU, so only it needs CARLA gone.
        stop_carla(run=run, sleep=sleep, log=log, platform=sys.platform)
        detect_command = module_command(
            "scenario_gen.runner",
            "--corpus",
            corpus,
            "--skip-render",
            "--device",
            args.device,
        )
        run_phase("detect", detect_command, run=run, log=log)

    if args.overwrite_out and args.out.exists():
        log(f"removing previous sweep output at {args.out}")
        shutil.rmtree(args.out)

    sweep_command = module_command(
        "harness.sweep", "--corpus", corpus, "--out", str(args.out)
    )
    for flag, value in SWEEP_CAMERA.items():
        sweep_command += [flag, value]
    sweep_command += ["--policies", *SWEEP_POLICIES]
    run_phase("sweep", sweep_command, run=run, log=log)

    log("phase calibrate: start")
    calibrate(args.corpus, args.seed)
    log("phase calibrate: done")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    started = time.time()
    try:
        run_pipeline(args, run=subprocess.run, sleep=time.sleep, log=log)
    except (PipelineError, ValueError, KeyError, OSError) as error:
        log(f"FAILED: {error}")
        return 1
    log(f"DONE in {time.time() - started:.0f}s; results under {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
