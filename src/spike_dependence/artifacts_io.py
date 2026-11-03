"""The on-disk contract between the render, detect, and score phases.

Phase 1 (CARLA) and Phase 2 (detector) never share a process, so these files
are the interface between them. Each payload carries a schema marker and every
reader rejects an unknown one, because a silent schema drift would not raise:
it would produce a wrong inflation ratio that still looked reasonable.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from spike_dependence.scene_matrix import Overlap, SceneSpec, Weather
from spike_dependence.scoring import BoundingBox, Detection, GroundTruthObject

GROUND_TRUTH_SCHEMA = "spike.ground_truth.v1"
DETECTION_SCHEMA = "spike.detections.v1"
MANIFEST_SCHEMA = "spike.manifest.v1"


def detection_filename(view: str, tag: str | None) -> str:
    """Return the detections filename for one viewpoint and detector.

    An untagged run keeps the default name. A tag lets a second detector's
    output sit beside the first instead of overwriting it, which is what the
    heterogeneous-agent contrast condition needs.
    """
    if not tag:
        return f"det_{view}.json"
    if not tag.isalnum():
        raise ValueError("detector tag must be alphanumeric to stay filename-safe")
    return f"det_{view}_{tag}.json"


def _write_json(payload: dict[str, Any], path: Path) -> None:
    """Write UTF-8 JSON with LF endings, creating parent folders as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def _read_json(path: Path, expected_schema: str, kind: str) -> dict[str, Any]:
    """Read JSON and refuse anything not written under the expected schema."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != expected_schema:
        raise ValueError(
            f"unsupported {kind} schema {payload.get('schema')!r}; "
            f"expected {expected_schema!r}"
        )
    return payload


def _box_to_dict(box: BoundingBox) -> dict[str, float]:
    return {"x1": box.x1, "y1": box.y1, "x2": box.x2, "y2": box.y2}


def _box_from_dict(raw: dict[str, float]) -> BoundingBox:
    return BoundingBox(x1=raw["x1"], y1=raw["y1"], x2=raw["x2"], y2=raw["y2"])


def ground_truth_to_json(
    objects: Sequence[GroundTruthObject], path: Path | str
) -> None:
    """Write one viewpoint's visible ground-truth objects."""
    _write_json(
        {
            "schema": GROUND_TRUTH_SCHEMA,
            "objects": [
                {
                    "object_id": obj.object_id,
                    "label": obj.label,
                    "box": _box_to_dict(obj.box),
                }
                for obj in objects
            ],
        },
        Path(path),
    )


def ground_truth_from_json(path: Path | str) -> list[GroundTruthObject]:
    """Read one viewpoint's visible ground-truth objects."""
    payload = _read_json(Path(path), GROUND_TRUTH_SCHEMA, "ground-truth")
    return [
        GroundTruthObject(
            object_id=raw["object_id"],
            label=raw["label"],
            box=_box_from_dict(raw["box"]),
        )
        for raw in payload["objects"]
    ]


def detections_to_json(detections: Sequence[Detection], path: Path | str) -> None:
    """Write one viewpoint's detector output."""
    _write_json(
        {
            "schema": DETECTION_SCHEMA,
            "detections": [
                {
                    "label": det.label,
                    "confidence": det.confidence,
                    "box": _box_to_dict(det.box),
                }
                for det in detections
            ],
        },
        Path(path),
    )


def detections_from_json(path: Path | str) -> list[Detection]:
    """Read one viewpoint's detector output."""
    payload = _read_json(Path(path), DETECTION_SCHEMA, "detection")
    return [
        Detection(
            label=raw["label"],
            confidence=raw["confidence"],
            box=_box_from_dict(raw["box"]),
        )
        for raw in payload["detections"]
    ]


def write_manifest(
    scenes: Sequence[SceneSpec],
    path: Path | str,
    *,
    extra: dict[str, Any] | None = None,
) -> None:
    """Write the scene matrix plus any run settings worth reproducing."""
    payload: dict[str, Any] = dict(extra or {})
    payload["schema"] = MANIFEST_SCHEMA
    payload["scenes"] = [
        {
            "scene_id": scene.scene_id,
            "town": scene.town,
            "weather": scene.weather.value,
            "overlap": scene.overlap.value,
            "occluder": scene.occluder,
            "seed": scene.seed,
        }
        for scene in scenes
    ]
    _write_json(payload, Path(path))


def read_manifest(path: Path | str) -> list[SceneSpec]:
    """Read the scene matrix back exactly as it was generated."""
    payload = _read_json(Path(path), MANIFEST_SCHEMA, "manifest")
    return [
        SceneSpec(
            scene_id=raw["scene_id"],
            town=raw["town"],
            weather=Weather(raw["weather"]),
            overlap=Overlap(raw["overlap"]),
            occluder=raw["occluder"],
            seed=raw["seed"],
        )
        for raw in payload["scenes"]
    ]
