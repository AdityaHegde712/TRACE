"""Spec for turning two agents' detections into paired error indicators.

Scoring is the only place simulator truth is read (project decision AD-001).
Truth labels a detection right or wrong and then stops; it never travels
onward into the detection or decision path.
"""

from __future__ import annotations

import pytest

from spike_dependence.scoring import (
    AgentView,
    BoundingBox,
    Detection,
    GroundTruthObject,
    collect_paired_records,
    intersection_over_union,
    object_error_flags,
    paired_error_records,
)


def _box(x1: float, y1: float, x2: float, y2: float) -> BoundingBox:
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


def _truth(object_id: str, box: BoundingBox, label: str = "car") -> GroundTruthObject:
    return GroundTruthObject(object_id=object_id, label=label, box=box)


def _detection(box: BoundingBox, label: str = "car", conf: float = 0.9) -> Detection:
    return Detection(label=label, confidence=conf, box=box)


class TestIntersectionOverUnion:
    def test_identical_boxes_score_one(self) -> None:
        box = _box(0, 0, 10, 10)

        assert intersection_over_union(box, box) == pytest.approx(1.0)

    def test_disjoint_boxes_score_zero(self) -> None:
        assert intersection_over_union(_box(0, 0, 10, 10), _box(20, 20, 30, 30)) == 0.0

    def test_touching_edges_score_zero(self) -> None:
        assert intersection_over_union(_box(0, 0, 10, 10), _box(10, 0, 20, 10)) == 0.0

    def test_half_overlap_scores_one_third(self) -> None:
        # Intersection 50, union 150.
        value = intersection_over_union(_box(0, 0, 10, 10), _box(5, 0, 15, 10))

        assert value == pytest.approx(1 / 3)

    def test_rejects_degenerate_box(self) -> None:
        with pytest.raises(ValueError, match="positive area"):
            BoundingBox(x1=5, y1=0, x2=5, y2=10)


class TestObjectErrorFlags:
    def test_matched_detection_marks_object_correct(self) -> None:
        truth = [_truth("obj-1", _box(0, 0, 10, 10))]
        detections = [_detection(_box(1, 1, 11, 11))]

        flags = object_error_flags(truth, detections, iou_threshold=0.5)

        assert flags == {"obj-1": False}

    def test_missing_detection_marks_object_wrong(self) -> None:
        flags = object_error_flags(
            [_truth("obj-1", _box(0, 0, 10, 10))], [], iou_threshold=0.5
        )

        assert flags == {"obj-1": True}

    def test_overlap_below_threshold_marks_object_wrong(self) -> None:
        truth = [_truth("obj-1", _box(0, 0, 10, 10))]
        detections = [_detection(_box(5, 0, 15, 10))]  # IoU 1/3

        flags = object_error_flags(truth, detections, iou_threshold=0.5)

        assert flags == {"obj-1": True}

    def test_class_mismatch_marks_object_wrong(self) -> None:
        truth = [_truth("obj-1", _box(0, 0, 10, 10), label="car")]
        detections = [_detection(_box(0, 0, 10, 10), label="truck")]

        flags = object_error_flags(truth, detections, iou_threshold=0.5)

        assert flags == {"obj-1": True}

    def test_one_detection_cannot_satisfy_two_objects(self) -> None:
        truth = [
            _truth("obj-1", _box(0, 0, 10, 10)),
            _truth("obj-2", _box(1, 1, 11, 11)),
        ]
        detections = [_detection(_box(0, 0, 10, 10))]

        flags = object_error_flags(truth, detections, iou_threshold=0.5)

        assert sum(flags.values()) == 1, "exactly one object should be left unmatched"

    def test_greedy_match_prefers_the_better_overlap(self) -> None:
        truth = [
            _truth("obj-1", _box(0, 0, 10, 10)),
            _truth("obj-2", _box(100, 100, 110, 110)),
        ]
        detections = [
            _detection(_box(100, 100, 110, 110)),
            _detection(_box(0, 0, 10, 10)),
        ]

        flags = object_error_flags(truth, detections, iou_threshold=0.5)

        assert flags == {"obj-1": False, "obj-2": False}

    def test_extra_false_positive_does_not_change_object_flags(self) -> None:
        truth = [_truth("obj-1", _box(0, 0, 10, 10))]
        detections = [
            _detection(_box(0, 0, 10, 10)),
            _detection(_box(500, 500, 510, 510)),
        ]

        flags = object_error_flags(truth, detections, iou_threshold=0.5)

        assert flags == {"obj-1": False}

    def test_rejects_threshold_outside_unit_interval(self) -> None:
        with pytest.raises(ValueError, match="iou_threshold"):
            object_error_flags([], [], iou_threshold=1.5)


class TestPairedErrorRecords:
    def test_scores_only_objects_both_agents_could_see(self) -> None:
        shared = _truth("shared", _box(0, 0, 10, 10))
        a_only = _truth("a-only", _box(50, 50, 60, 60))
        b_only = _truth("b-only", _box(80, 80, 90, 90))

        view_a = AgentView(agent_id="a", visible_truth=[shared, a_only], detections=[])
        view_b = AgentView(agent_id="b", visible_truth=[shared, b_only], detections=[])

        records = paired_error_records("frame-0", view_a, view_b, iou_threshold=0.5)

        assert [r.object_id for r in records] == ["shared"]

    def test_records_each_agent_flag_independently(self) -> None:
        truth = [_truth("obj-1", _box(0, 0, 10, 10))]
        view_a = AgentView(
            agent_id="a", visible_truth=truth, detections=[_detection(_box(0, 0, 10, 10))]
        )
        view_b = AgentView(agent_id="b", visible_truth=truth, detections=[])

        (record,) = paired_error_records("frame-0", view_a, view_b, iou_threshold=0.5)

        assert (record.agent_a_wrong, record.agent_b_wrong) == (False, True)
        assert record.frame_id == "frame-0"

    def test_no_shared_objects_yields_no_records(self) -> None:
        view_a = AgentView(
            agent_id="a", visible_truth=[_truth("x", _box(0, 0, 5, 5))], detections=[]
        )
        view_b = AgentView(
            agent_id="b", visible_truth=[_truth("y", _box(0, 0, 5, 5))], detections=[]
        )

        assert paired_error_records("frame-0", view_a, view_b, iou_threshold=0.5) == []

    def test_records_are_ordered_deterministically(self) -> None:
        truth = [
            _truth("obj-b", _box(0, 0, 10, 10)),
            _truth("obj-a", _box(50, 50, 60, 60)),
        ]
        view_a = AgentView(agent_id="a", visible_truth=truth, detections=[])
        view_b = AgentView(agent_id="b", visible_truth=list(reversed(truth)), detections=[])

        records = paired_error_records("frame-0", view_a, view_b, iou_threshold=0.5)

        assert [r.object_id for r in records] == ["obj-a", "obj-b"]

    def test_rejects_duplicate_object_ids_in_one_view(self) -> None:
        duplicated = [
            _truth("obj-1", _box(0, 0, 10, 10)),
            _truth("obj-1", _box(20, 20, 30, 30)),
        ]
        view_a = AgentView(agent_id="a", visible_truth=duplicated, detections=[])
        view_b = AgentView(agent_id="b", visible_truth=duplicated, detections=[])

        with pytest.raises(ValueError, match="duplicate object id"):
            paired_error_records("frame-0", view_a, view_b, iou_threshold=0.5)


class TestCollectPairedRecords:
    def test_flattens_frames_in_order(self) -> None:
        truth = [_truth("obj-1", _box(0, 0, 10, 10))]
        frames = [
            (
                f"frame-{index}",
                AgentView(agent_id="a", visible_truth=truth, detections=[]),
                AgentView(agent_id="b", visible_truth=truth, detections=[]),
            )
            for index in range(3)
        ]

        records = collect_paired_records(frames, iou_threshold=0.5)

        assert [r.frame_id for r in records] == ["frame-0", "frame-1", "frame-2"]

    def test_empty_input_yields_no_records(self) -> None:
        assert collect_paired_records([], iou_threshold=0.5) == []
