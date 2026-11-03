"""Spec for turning a CARLA instance-segmentation frame into ground truth.

Encoding verified empirically against CARLA 0.9.16 on 2026-11-03 (see SD-013):
raw_data is BGRA; R carries the semantic tag; the actor id is B*256 + G.

Per-viewpoint visibility comes from this frame and nothing else. An object
occluded from one camera occupies few or no pixels there, so it is correctly
absent from that agent's visible set. That is what makes SD-008's shared-object
rule trustworthy.
"""

from __future__ import annotations

import numpy as np
import pytest

from spike_dependence.instance_mask import (
    CAR_TAG,
    VEHICLE_LABELS,
    decode_actor_ids,
    ground_truth_from_instance_frame,
)


def _blank(height: int = 20, width: int = 30) -> np.ndarray:
    """Return an empty BGRA frame."""
    return np.zeros((height, width, 4), dtype=np.uint8)


def _paint(frame: np.ndarray, rows: slice, cols: slice, actor_id: int, tag: int = CAR_TAG) -> None:
    """Paint one actor's pixels using CARLA's BGRA instance encoding."""
    frame[rows, cols, 0] = actor_id // 256   # B: high byte
    frame[rows, cols, 1] = actor_id % 256    # G: low byte
    frame[rows, cols, 2] = tag               # R: semantic tag


class TestDecodeActorIds:
    def test_recovers_the_actor_id_from_blue_and_green(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 5), slice(3, 7), actor_id=43)

        ids = decode_actor_ids(frame)

        assert ids[3, 4] == 43

    def test_recovers_an_id_above_one_byte(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 5), slice(3, 7), actor_id=42840)

        assert decode_actor_ids(frame)[3, 4] == 42840

    def test_rejects_a_frame_that_is_not_bgra(self) -> None:
        with pytest.raises(ValueError, match="BGRA"):
            decode_actor_ids(np.zeros((4, 4, 3), dtype=np.uint8))


class TestGroundTruthFromInstanceFrame:
    def test_returns_one_object_per_visible_actor(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 6), slice(3, 9), actor_id=43)
        _paint(frame, slice(10, 14), slice(15, 21), actor_id=44)

        objects = ground_truth_from_instance_frame(frame, min_pixels=1)

        assert sorted(o.object_id for o in objects) == ["actor-43", "actor-44"]

    def test_box_is_the_tight_pixel_extent(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 6), slice(3, 9), actor_id=43)

        (obj,) = ground_truth_from_instance_frame(frame, min_pixels=1)

        # Rows 2..5 and cols 3..8 are painted; the box is exclusive at max.
        assert (obj.box.x1, obj.box.y1) == (3.0, 2.0)
        assert (obj.box.x2, obj.box.y2) == (9.0, 6.0)

    def test_labels_the_object_from_its_semantic_tag(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 6), slice(3, 9), actor_id=43, tag=CAR_TAG)

        (obj,) = ground_truth_from_instance_frame(frame, min_pixels=1)

        assert obj.label == VEHICLE_LABELS[CAR_TAG]

    def test_ignores_non_vehicle_tags(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 6), slice(3, 9), actor_id=43, tag=1)  # Roads

        assert ground_truth_from_instance_frame(frame, min_pixels=1) == []

    def test_drops_actors_below_the_visibility_threshold(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 10), slice(2, 10), actor_id=43)  # 64 pixels
        _paint(frame, slice(15, 16), slice(20, 22), actor_id=44)  # 2 pixels

        objects = ground_truth_from_instance_frame(frame, min_pixels=10)

        assert [o.object_id for o in objects] == ["actor-43"]

    def test_an_occluded_actor_simply_does_not_appear(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 10), slice(2, 10), actor_id=43)
        # Actor 44 is fully painted over by 43: no pixels survive for it.
        objects = ground_truth_from_instance_frame(frame, min_pixels=1)

        assert [o.object_id for o in objects] == ["actor-43"]

    def test_results_are_sorted_by_object_id(self) -> None:
        frame = _blank()
        _paint(frame, slice(2, 6), slice(3, 9), actor_id=90)
        _paint(frame, slice(10, 14), slice(15, 21), actor_id=12)

        objects = ground_truth_from_instance_frame(frame, min_pixels=1)

        assert [o.object_id for o in objects] == ["actor-12", "actor-90"]

    def test_empty_frame_yields_nothing(self) -> None:
        assert ground_truth_from_instance_frame(_blank(), min_pixels=1) == []

    def test_rejects_a_non_positive_threshold(self) -> None:
        with pytest.raises(ValueError, match="min_pixels"):
            ground_truth_from_instance_frame(_blank(), min_pixels=0)

    def test_single_pixel_actor_still_makes_a_valid_box(self) -> None:
        frame = _blank()
        _paint(frame, slice(5, 6), slice(7, 8), actor_id=43)

        (obj,) = ground_truth_from_instance_frame(frame, min_pixels=1)

        assert obj.box.area == pytest.approx(1.0)
