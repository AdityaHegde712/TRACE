"""Execute a planned Track B corpus: CARLA renders first, detectors second.

The two phases never share a process step. CARLA and the detectors compete for
the same GPU memory (SD-003), so Phase 1 finishes and releases the simulator
before Phase 2 loads a model, and Phase 2 loads one detector at a time.

    python -m scenario_gen.runner --corpus artifacts/corpus --device cuda:0
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scenario_gen.corpus import CorpusLayout, read_plan
from scenario_gen.detection_adapter import detections_to_report
from scenario_gen.planning import ScenarioPlan
from scenario_gen.render import (
    SOURCE_ID_BY_VIEW,
    RenderedScene,
    RenderSettings,
    render_entry,
)
from scenario_gen.reports import write_report
from spike_dependence.artifacts_io import camera_poses_from_json
from spike_dependence.detect import _predict_frame
from spike_dependence.render_scenes import _synchronous
from spike_dependence.scoring import Detection as SpikeDetection
from trace_contracts.observations import CameraPose

# A fixed instant keeps reports byte-identical across reruns. Delivery delay is
# a sweep concern (A3), so Phase 2 records every report as arriving when observed.
OBSERVED_AT = datetime(2026, 1, 1, tzinfo=UTC)
DEFAULT_WEIGHTS: dict[str, str] = {"yolo11m": "yolo11m.pt", "rtdetr-l": "rtdetr-l.pt"}
CARLA_TIMEOUT_S = 120.0

Predictor = Callable[[Path, float], list[SpikeDetection]]
PredictorFactory = Callable[[str, str, str], Predictor]

_VIEW_BY_SOURCE_ID = {source: view for view, source in SOURCE_ID_BY_VIEW.items()}


def _log(message: str) -> None:
    """Print one progress line and flush, so a tailed log stays current."""
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def render_corpus(
    client: Any,
    plan: ScenarioPlan,
    layout: CorpusLayout,
    settings: RenderSettings,
) -> list[RenderedScene]:
    """Phase 1: render every manifest entry, in manifest order."""
    rendered: list[RenderedScene] = []
    with _synchronous(client.get_world()):
        for index, entry in enumerate(plan.entries, start=1):
            rendered.append(render_entry(client, entry, layout, settings))
            _log(f"{entry.scene_id} rendered [{index}/{len(plan.entries)}]")
    return rendered


def load_predictor(detector: str, weights: str, device: str) -> Predictor:
    """Load one detector with ultralytics and return a per-frame predictor."""
    # Imported here so the module stays importable without the spike extra.
    from ultralytics import RTDETR, YOLO

    # RT-DETR is a separate lineage with its own loader; the weights name says which.
    loader = RTDETR if Path(weights).name.lower().startswith("rtdetr") else YOLO
    model = loader(weights)
    model.to(device)

    def predict(image_path: Path, min_confidence: float) -> list[SpikeDetection]:
        return _predict_frame(model, image_path, min_confidence)

    return predict


def detect_corpus(
    layout: CorpusLayout,
    weights_by_detector: Mapping[str, str],
    device: str,
    min_confidence: float,
    *,
    predictor_factory: PredictorFactory = load_predictor,
) -> list[Path]:
    """Phase 2: run each detector over every frame and write one report per frame.

    Reports land at `reports/<detector>/<scene>--<frame>--<source>.json`. Frames
    and poses are validated before any model loads, so a bad corpus fails fast
    instead of after minutes of model loading.
    """
    frames = _frame_records(layout)
    poses = {
        (scene_id, frame_id): camera_poses_from_json(
            layout.camera_pose_path(scene_id, frame_id)
        )
        for scene_id, frame_id, _, _ in frames
    }

    written: list[Path] = []
    for detector, weights in weights_by_detector.items():
        _log(f"loading {detector} ({weights}) on {device}")
        predictor = predictor_factory(detector, weights, device)
        for scene_id, frame_id, source_id, image_path in frames:
            spike_pose = poses[(scene_id, frame_id)][_view_of(source_id)]
            report = detections_to_report(
                scene_id=scene_id,
                frame_id=frame_id,
                source_id=source_id,
                detector=detector,
                observed_at=OBSERVED_AT,
                arrived_at=OBSERVED_AT,
                camera_pose=CameraPose(
                    spike_pose.x,
                    spike_pose.y,
                    spike_pose.z,
                    spike_pose.yaw,
                    spike_pose.pitch,
                ),
                detections=predictor(image_path, min_confidence),
            )
            path = layout.detector_report_path(detector, scene_id, frame_id, source_id)
            written.append(write_report(layout, report, path))
        _log(f"{detector}: {len(frames)} reports written")
        # Drop the model before the next detector loads so only one holds the GPU.
        del predictor
        gc.collect()
    return written


def _view_of(source_id: str) -> str:
    try:
        return _VIEW_BY_SOURCE_ID[source_id]
    except KeyError:
        raise ValueError(f"source {source_id!r} has no recorded camera view") from None


def _frame_records(layout: CorpusLayout) -> list[tuple[str, str, str, Path]]:
    """Return (scene, frame, source, image path) for every rendered frame."""
    paths = sorted(layout.frames_root.glob("*.png")) if layout.frames_root.is_dir() else []
    if not paths:
        raise ValueError(f"no frames found under {layout.frames_root}")

    records: list[tuple[str, str, str, Path]] = []
    for path in paths:
        parts = path.stem.split("--")
        if len(parts) != 3 or layout.frame_path(*parts) != path:
            raise ValueError(f"unrecognised frame file name: {path.name}")
        records.append((parts[0], parts[1], parts[2], path))
    return records


def main(argv: list[str] | None = None) -> int:
    """Render the planned corpus, then detect over its frames."""
    parser = argparse.ArgumentParser(description="Execute a planned Track B corpus.")
    parser.add_argument("--corpus", type=Path, required=True, help="Planned corpus folder")
    parser.add_argument("--carla-host", default="127.0.0.1")
    parser.add_argument("--carla-port", type=int, default=2000)
    parser.add_argument("--skip-render", action="store_true", help="Reuse existing frames")
    parser.add_argument("--skip-detect", action="store_true", help="Stop after rendering")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--min-confidence", type=float, default=0.25)
    args = parser.parse_args(argv)

    layout = CorpusLayout(args.corpus)
    try:
        if not args.skip_render:
            plan = read_plan(layout)
            import carla  # Imported here so --skip-render needs no simulator.

            client = carla.Client(args.carla_host, args.carla_port)
            client.set_timeout(CARLA_TIMEOUT_S)
            render_corpus(client, plan, layout, RenderSettings())
        if not args.skip_detect:
            detect_corpus(layout, DEFAULT_WEIGHTS, args.device, args.min_confidence)
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as error:
        parser.exit(2, f"scenario_gen.runner: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
