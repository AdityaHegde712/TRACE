"""Spec for joining saved artifacts into the paired records the report needs."""

from __future__ import annotations

import pytest

from spike_dependence.artifacts_io import detections_to_json, ground_truth_to_json
from spike_dependence.scoring import BoundingBox, Detection, GroundTruthObject
from spike_dependence.spike_cli import load_paired_records


def _write_scene(root, scene_id, truth_a, truth_b, det_a, det_b):
    scene_dir = root / scene_id
    scene_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_to_json(truth_a, scene_dir / "gt_a.json")
    ground_truth_to_json(truth_b, scene_dir / "gt_b.json")
    detections_to_json(det_a, scene_dir / "det_a.json")
    detections_to_json(det_b, scene_dir / "det_b.json")
    return scene_dir


def _truth(object_id, x=0.0):
    return GroundTruthObject(object_id, "car", BoundingBox(x, 0.0, x + 10.0, 10.0))


def _hit(x=0.0):
    return Detection("car", 0.9, BoundingBox(x, 0.0, x + 10.0, 10.0))


class TestLoadPairedRecords:
    def test_reads_one_record_per_shared_object(self, tmp_path) -> None:
        shared = [_truth("actor-1", 0.0), _truth("actor-2", 20.0)]
        _write_scene(tmp_path, "scene-000", shared, shared, [_hit(0.0)], [])

        records = load_paired_records(tmp_path, iou_threshold=0.5)

        assert sorted(r.object_id for r in records) == ["actor-1", "actor-2"]

    def test_marks_the_agent_that_detected_as_correct(self, tmp_path) -> None:
        shared = [_truth("actor-1", 0.0)]
        _write_scene(tmp_path, "scene-000", shared, shared, [_hit(0.0)], [])

        (record,) = load_paired_records(tmp_path, iou_threshold=0.5)

        assert (record.agent_a_wrong, record.agent_b_wrong) == (False, True)

    def test_frame_id_identifies_the_scene(self, tmp_path) -> None:
        shared = [_truth("actor-1")]
        _write_scene(tmp_path, "scene-007", shared, shared, [], [])

        (record,) = load_paired_records(tmp_path, iou_threshold=0.5)

        assert record.frame_id == "scene-007"

    def test_spans_multiple_scenes(self, tmp_path) -> None:
        shared = [_truth("actor-1")]
        for scene_id in ("scene-000", "scene-001", "scene-002"):
            _write_scene(tmp_path, scene_id, shared, shared, [], [])

        records = load_paired_records(tmp_path, iou_threshold=0.5)

        assert len(records) == 3

    def test_skips_a_scene_missing_its_detections(self, tmp_path) -> None:
        shared = [_truth("actor-1")]
        _write_scene(tmp_path, "scene-000", shared, shared, [], [])
        incomplete = tmp_path / "scene-001"
        incomplete.mkdir()
        ground_truth_to_json(shared, incomplete / "gt_a.json")

        records = load_paired_records(tmp_path, iou_threshold=0.5)

        assert [r.frame_id for r in records] == ["scene-000"]

    def test_object_ids_from_different_scenes_do_not_collide(self, tmp_path) -> None:
        shared = [_truth("actor-1")]
        _write_scene(tmp_path, "scene-000", shared, shared, [_hit()], [])
        _write_scene(tmp_path, "scene-001", shared, shared, [], [_hit()])

        records = load_paired_records(tmp_path, iou_threshold=0.5)

        by_scene = {r.frame_id: (r.agent_a_wrong, r.agent_b_wrong) for r in records}
        assert by_scene["scene-000"] == (False, True)
        assert by_scene["scene-001"] == (True, False)

    def test_rejects_a_missing_directory(self, tmp_path) -> None:
        with pytest.raises(ValueError, match="no scene folders"):
            load_paired_records(tmp_path / "nope", iou_threshold=0.5)


class TestHeterogeneousDetectors:
    def test_reads_a_different_detection_file_per_agent(self, tmp_path) -> None:
        shared = [_truth("actor-1", 0.0)]
        scene_dir = _write_scene(tmp_path, "scene-000", shared, shared, [], [])
        # Agent A keeps the default file; agent B gets a second detector's.
        detections_to_json([_hit(0.0)], scene_dir / "det_b_rtdetr.json")

        (record,) = load_paired_records(
            tmp_path, iou_threshold=0.5, det_b_name="det_b_rtdetr.json"
        )

        assert (record.agent_a_wrong, record.agent_b_wrong) == (True, False)

    def test_skips_a_scene_missing_the_named_file(self, tmp_path) -> None:
        shared = [_truth("actor-1", 0.0)]
        _write_scene(tmp_path, "scene-000", shared, shared, [], [])

        records = load_paired_records(
            tmp_path, iou_threshold=0.5, det_b_name="det_b_absent.json"
        )

        assert records == []
