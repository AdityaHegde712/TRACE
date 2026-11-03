"""Phase 2: run one detector over the saved frames, offline.

CARLA is not running during this phase (SD-003), so the simulator and the
detector never compete for the 8 GB of VRAM. Input is the RGB frames written
by Phase 1; output is one detections file per frame, beside them.

The same weights run on both viewpoints. That is the whole point of the spike:
if two agents share a detector, do their errors co-occur?

    python -m spike_dependence.detect --raw artifacts/spike/raw
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from spike_dependence.artifacts_io import detections_to_json
from spike_dependence.instance_mask import VEHICLE_LABELS
from spike_dependence.scoring import BoundingBox, Detection

# Ground truth only ever contains these classes, so anything else the detector
# reports (person, traffic light, ...) cannot be matched and is dropped.
VEHICLE_CLASS_NAMES = frozenset(VEHICLE_LABELS.values())


def _log(message: str) -> None:
    """Print one progress line and flush, so a tailed log stays current."""
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def detections_from_prediction(
    *,
    boxes: Sequence[tuple[float, float, float, float]],
    labels: Sequence[str],
    confidences: Sequence[float],
    min_confidence: float,
) -> list[Detection]:
    """Convert one frame's raw detector output into scored-ready detections.

    Non-vehicle classes and low-confidence boxes are dropped. A degenerate box
    is skipped rather than raised on: a detector occasionally emits a zero-width
    box, and losing one detection is correct behaviour where aborting the whole
    run is not.
    """
    if not len(boxes) == len(labels) == len(confidences):
        raise ValueError("boxes, labels and confidences must be the same length")

    detections: list[Detection] = []
    for (x1, y1, x2, y2), label, confidence in zip(
        boxes, labels, confidences, strict=True
    ):
        if label not in VEHICLE_CLASS_NAMES or confidence < min_confidence:
            continue
        try:
            box = BoundingBox(x1=float(x1), y1=float(y1), x2=float(x2), y2=float(y2))
        except ValueError:
            continue
        detections.append(
            Detection(label=label, confidence=float(confidence), box=box)
        )
    return detections


def _predict_frame(model: Any, image_path: Path, min_confidence: float) -> list[Detection]:
    """Run the detector on one frame and convert the result."""
    result = model.predict(
        source=str(image_path), conf=min_confidence, verbose=False
    )[0]
    names = result.names
    boxes = [
        (float(row[0]), float(row[1]), float(row[2]), float(row[3]))
        for row in result.boxes.xyxy.tolist()
    ]
    labels = [names[int(index)] for index in result.boxes.cls.tolist()]
    confidences = [float(value) for value in result.boxes.conf.tolist()]
    return detections_from_prediction(
        boxes=boxes,
        labels=labels,
        confidences=confidences,
        min_confidence=min_confidence,
    )


def run(args: argparse.Namespace) -> int:
    """Detect over every saved frame and write detections beside them."""
    from ultralytics import YOLO  # Imported here so the module imports without it.

    raw_dir = Path(args.raw)
    scene_dirs = sorted(path for path in raw_dir.iterdir() if path.is_dir())
    if not scene_dirs:
        _log(f"no scene folders under {raw_dir}")
        return 1

    _log(f"loading {args.weights} on {args.device}")
    model = YOLO(args.weights)
    model.to(args.device)

    started = time.time()
    frames = 0
    totals: dict[str, int] = {"a": 0, "b": 0}
    for scene_dir in scene_dirs:
        counts: dict[str, int] = {}
        for view in ("a", "b"):
            image_path = scene_dir / f"rgb_{view}.png"
            if not image_path.exists():
                _log(f"{scene_dir.name}: missing {image_path.name}, skipped")
                continue
            detections = _predict_frame(model, image_path, args.min_confidence)
            detections_to_json(detections, scene_dir / f"det_{view}.json")
            counts[view] = len(detections)
            totals[view] += len(detections)
            frames += 1
        _log(
            f"{scene_dir.name} -> detections A={counts.get('a', 0)} "
            f"B={counts.get('b', 0)}"
        )

    _log(
        f"DONE: {frames} frames in {time.time() - started:.0f}s; "
        f"total detections A={totals['a']} B={totals['b']}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run detection over the saved frames."""
    parser = argparse.ArgumentParser(description="Run the spike detector offline.")
    parser.add_argument("--raw", default="artifacts/spike/raw")
    parser.add_argument("--weights", default="yolo11m.pt")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--min-confidence", type=float, default=0.25)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
