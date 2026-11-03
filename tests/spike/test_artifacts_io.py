"""Spec for the on-disk contract between render, detect, and score.

Phase 1 (CARLA) and Phase 2 (detector) never share a process, so these files
ARE the interface. A schema drift here would not raise; it would quietly
produce a wrong inflation ratio. Round-trip tests pin the shape.
"""

from __future__ import annotations

import json

import pytest

from spike_dependence.artifacts_io import (
    detections_from_json,
    detections_to_json,
    ground_truth_from_json,
    ground_truth_to_json,
    read_manifest,
    write_manifest,
)
from spike_dependence.scene_matrix import build_scene_matrix
from spike_dependence.scoring import BoundingBox, Detection, GroundTruthObject


def _objects() -> list[GroundTruthObject]:
    return [
        GroundTruthObject("actor-49", "car", BoundingBox(357.0, 524.0, 443.0, 600.0)),
        GroundTruthObject("actor-50", "truck", BoundingBox(377.0, 373.0, 423.0, 433.0)),
    ]


def _detections() -> list[Detection]:
    return [
        Detection("car", 0.91, BoundingBox(355.0, 520.0, 445.0, 599.0)),
        Detection("car", 0.42, BoundingBox(10.0, 10.0, 20.0, 20.0)),
    ]


class TestGroundTruthRoundTrip:
    def test_survives_a_write_and_read(self, tmp_path) -> None:
        path = tmp_path / "gt_a.json"
        ground_truth_to_json(_objects(), path)

        assert ground_truth_from_json(path) == _objects()

    def test_writes_readable_json_with_a_schema_marker(self, tmp_path) -> None:
        path = tmp_path / "gt_a.json"
        ground_truth_to_json(_objects(), path)

        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema"] == "spike.ground_truth.v1"
        assert len(payload["objects"]) == 2

    def test_rejects_an_unknown_schema(self, tmp_path) -> None:
        path = tmp_path / "gt_a.json"
        path.write_text(json.dumps({"schema": "nope", "objects": []}), encoding="utf-8")

        with pytest.raises(ValueError, match="unsupported ground-truth schema"):
            ground_truth_from_json(path)

    def test_empty_object_list_round_trips(self, tmp_path) -> None:
        path = tmp_path / "gt_a.json"
        ground_truth_to_json([], path)

        assert ground_truth_from_json(path) == []


class TestDetectionRoundTrip:
    def test_survives_a_write_and_read(self, tmp_path) -> None:
        path = tmp_path / "det_a.json"
        detections_to_json(_detections(), path)

        assert detections_from_json(path) == _detections()

    def test_rejects_an_unknown_schema(self, tmp_path) -> None:
        path = tmp_path / "det_a.json"
        path.write_text(json.dumps({"schema": "nope", "detections": []}), encoding="utf-8")

        with pytest.raises(ValueError, match="unsupported detection schema"):
            detections_from_json(path)


class TestManifest:
    def test_round_trips_the_scene_matrix(self, tmp_path) -> None:
        scenes = build_scene_matrix(6, seed=4)
        path = tmp_path / "manifest.json"

        write_manifest(scenes, path, extra={"min_pixels": 50})

        assert read_manifest(path) == scenes

    def test_records_the_knob_settings_per_scene(self, tmp_path) -> None:
        scenes = build_scene_matrix(3, seed=4)
        path = tmp_path / "manifest.json"
        write_manifest(scenes, path, extra={"min_pixels": 50})

        payload = json.loads(path.read_text(encoding="utf-8"))
        first = payload["scenes"][0]
        assert set(first) == {"scene_id", "town", "weather", "overlap", "occluder", "seed"}
        assert payload["min_pixels"] == 50

    def test_rejects_an_unknown_schema(self, tmp_path) -> None:
        path = tmp_path / "manifest.json"
        path.write_text(json.dumps({"schema": "nope", "scenes": []}), encoding="utf-8")

        with pytest.raises(ValueError, match="unsupported manifest schema"):
            read_manifest(path)
