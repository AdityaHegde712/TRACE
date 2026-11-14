"""Evaluator-only truth storage for Track B's CARLA render output."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from scenario_gen.corpus import CorpusLayout
from trace_contracts._schema import require_schema
from trace_contracts.observations import BoundingBox
from trace_contracts.truth import TruthObject

TRUTH_ARTIFACT_SCHEMA = "scenario_gen.truth.m1-v0"


def write_truth(
    layout: CorpusLayout,
    *,
    scene_id: str,
    frame_id: str,
    source_id: str,
    objects: Sequence[TruthObject],
) -> Path:
    """Write evaluator-only visible objects beside, never inside, reports."""
    _validate_truth_context(scene_id, source_id, objects)
    path = layout.truth_path(scene_id, frame_id, source_id)
    _write_json(
        {
            "schema": TRUTH_ARTIFACT_SCHEMA,
            "scene_id": scene_id,
            "frame_id": frame_id,
            "source_id": source_id,
            "objects": [_truth_to_dict(obj) for obj in objects],
        },
        path,
    )
    return path


def read_truth(path: Path) -> tuple[TruthObject, ...]:
    """Read one evaluator-only view's ground truth."""
    payload = _read_json(path)
    require_schema(payload, TRUTH_ARTIFACT_SCHEMA, "scenario truth artifact")
    raw_objects = payload["objects"]
    if not isinstance(raw_objects, list):
        raise TypeError("scenario truth artifact must contain an object list")
    return tuple(_truth_from_dict(raw) for raw in raw_objects)


def _validate_truth_context(
    scene_id: str, source_id: str, objects: Sequence[TruthObject]
) -> None:
    if any(obj.scene_id != scene_id for obj in objects):
        raise ValueError("truth objects must match the requested scene")
    if any(obj.source_id != source_id for obj in objects):
        raise ValueError("truth objects must match the requested source")


def _truth_to_dict(obj: TruthObject) -> dict[str, object]:
    return {
        "object_id": obj.object_id,
        "scene_id": obj.scene_id,
        "source_id": obj.source_id,
        "label": obj.label,
        "box": {"x1": obj.box.x1, "y1": obj.box.y1, "x2": obj.box.x2, "y2": obj.box.y2},
    }


def _truth_from_dict(raw: object) -> TruthObject:
    if not isinstance(raw, dict):
        raise TypeError("truth object must be a JSON object")
    box = raw["box"]
    if not isinstance(box, dict):
        raise TypeError("truth object must include a box object")
    return TruthObject(
        object_id=str(raw["object_id"]),
        scene_id=str(raw["scene_id"]),
        source_id=str(raw["source_id"]),
        label=str(raw["label"]),
        box=BoundingBox(
            x1=float(box["x1"]),
            y1=float(box["y1"]),
            x2=float(box["x2"]),
            y2=float(box["y2"]),
        ),
    )


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("record must contain a JSON object")
    return payload
