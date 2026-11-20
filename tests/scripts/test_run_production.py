"""Spec for the 900-scene production pipeline script.

The script drives long GPU jobs, so these tests replace every subprocess and
every sleep with fakes. What is pinned: the phase order, the CARLA shutdown that
frees VRAM before detection (SD-003), fail-fast behaviour, and the conversion
from corpus tasks to the calibration records.
"""

from __future__ import annotations

import importlib
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scenario_gen.corpus import CorpusLayout, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, ScenarioPlan
from scenario_gen.reports import write_report
from scenario_gen.truth_export import write_truth
from sweep.corpus import load_tasks
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)
from trace_contracts.scenario import (
    DetectorPairing,
    ScenarioManifestEntry,
    render_cells,
)
from trace_contracts.truth import TruthObject

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
T0 = datetime(2026, 1, 1, tzinfo=UTC)
BOX = BoundingBox(390, 300, 410, 400)


@pytest.fixture
def production(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    return importlib.import_module("run_production")


class Recorder:
    """Stands in for subprocess.run and time.sleep, keeping one shared timeline."""

    def __init__(self, failing: str | None = None, returncode: int = 1) -> None:
        self.events: list[tuple] = []
        self.failing = failing
        self.returncode = returncode

    def run(self, command, **kwargs):
        self.events.append(("run", tuple(command)))
        failed = self.failing is not None and self.failing in " ".join(command)
        return subprocess.CompletedProcess(command, self.returncode if failed else 0)

    def sleep(self, seconds):
        self.events.append(("sleep", seconds))

    def commands(self) -> list[str]:
        return [" ".join(e[1]) for e in self.events if e[0] == "run"]


def make_args(production, tmp_path):
    corpus = tmp_path / "corpus"
    write_plan(CorpusLayout(corpus), ScenarioPlan(ScenarioGenerationConfig(), ()))
    return production.parse_args(
        ["--corpus", str(corpus), "--out", str(tmp_path / "eval")]
    )


def run_pipeline(production, args, recorder):
    return production.run_pipeline(
        args,
        run=recorder.run,
        sleep=recorder.sleep,
        log=lambda message: None,
        calibrate=lambda corpus, seed: recorder.events.append(("calibrate", corpus)),
    )


def test_phases_run_in_order_with_carla_stopped_before_detection(
    production, tmp_path
) -> None:
    recorder = Recorder()
    run_pipeline(production, make_args(production, tmp_path), recorder)

    kinds = [event[0] for event in recorder.events]
    commands = recorder.commands()
    assert "scenario_gen.runner" in commands[0] and "--skip-detect" in commands[0]
    assert "taskkill" in commands[1] or "pkill" in commands[1]
    assert recorder.events[kinds.index("sleep")] == ("sleep", 5)
    assert kinds.index("sleep") < kinds.index("run", 2)
    assert "scenario_gen.runner" in commands[2]
    assert "--skip-render" in commands[2] and "--device cuda:0" in commands[2]
    assert "harness.sweep" in commands[3]
    assert kinds[-1] == "calibrate"


def test_sweep_command_matches_the_production_settings(production, tmp_path) -> None:
    args = make_args(production, tmp_path)
    recorder = Recorder()
    run_pipeline(production, args, recorder)

    sweep = recorder.commands()[3]
    for fragment in (
        f"--corpus {args.corpus}",
        f"--out {args.out}",
        "--width-px 800",
        "--height-px 600",
        "--fov-degrees 90",
        "--camera-height-m 14",
        "--policies latest-report miss-risk",
    ):
        assert fragment in sweep


def test_a_missing_manifest_is_planned_with_900_scenes_first(
    production, tmp_path
) -> None:
    corpus = tmp_path / "fresh"
    args = production.parse_args(
        ["--corpus", str(corpus), "--out", str(tmp_path / "eval")]
    )
    recorder = Recorder()
    run_pipeline(production, args, recorder)

    plan = recorder.commands()[0]
    assert "scenario_gen" in plan and "--scenes-per-render-cell 50" in plan
    assert len(render_cells()) * 50 == 900


def run_with(production, tmp_path, *flags):
    args = make_args(production, tmp_path)
    args = production.parse_args(
        ["--corpus", str(args.corpus), "--out", str(args.out), *flags]
    )
    recorder = Recorder()
    run_pipeline(production, args, recorder)
    return args, recorder


def test_skip_render_resumes_at_detection_and_still_frees_the_gpu(
    production, tmp_path
) -> None:
    _, recorder = run_with(production, tmp_path, "--skip-render")

    commands = recorder.commands()
    assert not any("--skip-detect" in command for command in commands)
    assert "taskkill" in commands[0] or "pkill" in commands[0]
    assert "--skip-render" in commands[1]
    assert "harness.sweep" in commands[2]


def test_skip_detect_stops_after_rendering_without_killing_carla(
    production, tmp_path
) -> None:
    _, recorder = run_with(production, tmp_path, "--skip-detect")

    commands = recorder.commands()
    assert len(commands) == 2
    assert "--skip-detect" in commands[0]
    assert "harness.sweep" in commands[1]
    assert ("sleep", 5) not in recorder.events


def test_skipping_both_phases_runs_only_the_sweep(production, tmp_path) -> None:
    _, recorder = run_with(production, tmp_path, "--skip-render", "--skip-detect")

    assert len(recorder.commands()) == 1
    assert "harness.sweep" in recorder.commands()[0]


def test_skip_render_does_not_plan_a_missing_manifest(production, tmp_path) -> None:
    args = production.parse_args(
        ["--corpus", str(tmp_path / "fresh"), "--out", str(tmp_path / "eval"), "--skip-render"]
    )
    recorder = Recorder()
    run_pipeline(production, args, recorder)

    assert not any(command.endswith("--scenes-per-render-cell 50") for command in recorder.commands())


def test_overwrite_out_removes_a_previous_sweep_output(production, tmp_path) -> None:
    args = make_args(production, tmp_path)
    (args.out / "traces").mkdir(parents=True)
    (args.out / "run.json").write_text("{}", encoding="utf-8")
    args = production.parse_args(
        ["--corpus", str(args.corpus), "--out", str(args.out), "--overwrite-out"]
    )

    run_pipeline(production, args, Recorder())

    assert not args.out.exists()


def test_without_overwrite_out_a_previous_output_is_left_alone(
    production, tmp_path
) -> None:
    args = make_args(production, tmp_path)
    args.out.mkdir()
    (args.out / "run.json").write_text("{}", encoding="utf-8")

    run_pipeline(production, args, Recorder())

    assert (args.out / "run.json").exists()


def test_overwrite_out_refuses_a_folder_that_is_not_sweep_output(
    production, tmp_path
) -> None:
    args = make_args(production, tmp_path)
    args.out.mkdir()
    (args.out / "precious.txt").write_text("keep", encoding="utf-8")
    args = production.parse_args(
        ["--corpus", str(args.corpus), "--out", str(args.out), "--overwrite-out"]
    )

    with pytest.raises(production.PipelineError, match="sweep output"):
        run_pipeline(production, args, Recorder())

    assert (args.out / "precious.txt").exists()


def test_overwrite_out_refuses_the_corpus_itself(production, tmp_path) -> None:
    args = make_args(production, tmp_path)
    (args.corpus / "run.json").write_text("{}", encoding="utf-8")
    args = production.parse_args(
        ["--corpus", str(args.corpus), "--out", str(args.corpus), "--overwrite-out"]
    )

    with pytest.raises(production.PipelineError, match="corpus"):
        run_pipeline(production, args, Recorder())

    assert (args.corpus / "manifest.json").exists()


def test_a_failed_phase_stops_the_pipeline(production, tmp_path) -> None:
    recorder = Recorder(failing="--skip-detect")

    with pytest.raises(production.PipelineError, match="render"):
        run_pipeline(production, make_args(production, tmp_path), recorder)

    assert len(recorder.commands()) == 1
    assert ("sleep", 5) not in recorder.events


def test_main_returns_nonzero_and_logs_when_a_phase_fails(
    production, tmp_path, monkeypatch, capsys
) -> None:
    args = make_args(production, tmp_path)
    monkeypatch.setattr(subprocess, "run", Recorder(failing="--skip-detect").run)

    code = production.main(["--corpus", str(args.corpus), "--out", str(args.out)])

    assert code == 1
    assert "render" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("platform", "program", "not_found"),
    [("win32", "taskkill", 128), ("linux", "pkill", 1)],
)
def test_stop_carla_tolerates_no_running_server(
    production, platform, program, not_found
) -> None:
    recorder = Recorder(failing="CarlaUE4", returncode=not_found)

    production.stop_carla(
        run=recorder.run, sleep=recorder.sleep, log=lambda m: None, platform=platform
    )

    assert recorder.commands()[0].startswith(program)
    assert "CarlaUE4" in recorder.commands()[0]
    assert recorder.events[-1] == ("sleep", 5)


def test_stop_carla_fails_when_the_process_cannot_be_killed(production) -> None:
    recorder = Recorder(failing="CarlaUE4", returncode=1)

    with pytest.raises(production.PipelineError, match="CARLA"):
        production.stop_carla(
            run=recorder.run,
            sleep=recorder.sleep,
            log=lambda m: None,
            platform="win32",
        )

    assert ("sleep", 5) not in recorder.events


def make_corpus_with_two_scenes(root: Path) -> CorpusLayout:
    layout = CorpusLayout(root)
    entries = tuple(
        ScenarioManifestEntry(f"scene-{i:04d}", render_cells()[i], "Town10HD", i)
        for i in range(2)
    )
    write_plan(layout, ScenarioPlan(ScenarioGenerationConfig(), entries))
    for entry in entries:
        for source in ("agent-a", "agent-b"):
            write_truth(
                layout,
                scene_id=entry.scene_id,
                frame_id="frame-000",
                source_id=source,
                objects=[TruthObject("real", entry.scene_id, source, "car", BOX)],
            )
            for detector in ("yolo11m", "rtdetr-l"):
                # agent-a always sees the car; agent-b misses it in scene-0001.
                seen = source == "agent-a" or entry.scene_id == "scene-0000"
                report = AgentFrameReport(
                    f"{entry.scene_id}--frame-000--{source}",
                    source,
                    entry.scene_id,
                    "frame-000",
                    T0,
                    T0,
                    CameraPose(0, 0, 14, 0, -30),
                    detector,
                    (Detection("d", "car", 0.9, BOX),) if seen else (),
                )
                path = layout.detector_report_path(
                    detector, entry.scene_id, "frame-000", source
                )
                write_report(layout, report, path)
    return layout


def test_paired_records_are_keyed_by_detector_pair_and_scene(
    production, tmp_path
) -> None:
    layout = make_corpus_with_two_scenes(tmp_path)
    tasks = load_tasks(layout.root, tuple(DetectorPairing))

    by_pair = production.paired_records_by_pair(tasks, iou_threshold=0.5)

    assert set(by_pair) == {
        ("yolo11m", "yolo11m"),
        ("rtdetr-l", "rtdetr-l"),
        ("yolo11m", "rtdetr-l"),
    }
    records = {record.frame_id: record for record in by_pair[("yolo11m", "yolo11m")]}
    assert set(records) == {"scene-0000", "scene-0001"}
    first, second = records["scene-0000"], records["scene-0001"]
    assert (first.agent_a_wrong, first.agent_b_wrong) == (False, False)
    assert (second.agent_a_wrong, second.agent_b_wrong) == (False, True)


def test_calibration_runs_a_random_split_and_one_shift_test_per_illumination(
    production, tmp_path, monkeypatch
) -> None:
    layout = make_corpus_with_two_scenes(tmp_path)
    fit_estimator = importlib.import_module("fit_estimator")
    calls: list[tuple[str, tuple, tuple]] = []
    monkeypatch.setattr(
        fit_estimator,
        "run_split",
        lambda label, records, practice, exam: calls.append((label, practice, exam)),
    )

    production.calibrate(layout.root, seed=0)

    assert calls[0][0].startswith("random split")
    assert sorted(calls[0][1] + calls[0][2]) == ["scene-0000", "scene-0001"]
    cells = render_cells()
    assert {label for label, _, _ in calls[1:]} == {
        f"shift test, exam = {cells[i].illumination.value}" for i in (0, 1)
    }
