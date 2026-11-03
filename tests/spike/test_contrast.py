"""Spec for the homogeneous-versus-heterogeneous contrast condition."""

from __future__ import annotations

import pytest

from spike_dependence.contrast import (
    QuadErrorRecord,
    condition_phis,
    paired_difference,
)


def _quad(pattern, index: int) -> QuadErrorRecord:
    first_a, first_b, second_a, second_b = pattern
    return QuadErrorRecord(
        object_id=f"obj-{index}",
        frame_id="scene-000",
        first_a_wrong=first_a,
        first_b_wrong=first_b,
        second_a_wrong=second_a,
        second_b_wrong=second_b,
    )


def _records(patterns) -> list[QuadErrorRecord]:
    return [_quad(pattern, index) for index, pattern in enumerate(patterns)]


class TestConditionPhis:
    def test_shared_model_agreeing_raises_homogeneous_phi(self) -> None:
        # Each detector agrees perfectly with itself, and the two detectors
        # are independent of each other. Pairing agents on the SAME detector
        # must therefore show association where crossing them shows none.
        patterns = (
            [(True, True, True, True)] * 25
            + [(True, True, False, False)] * 25
            + [(False, False, True, True)] * 25
            + [(False, False, False, False)] * 25
        )

        homogeneous, heterogeneous = condition_phis(_records(patterns))

        assert homogeneous > heterogeneous

    def test_identical_detectors_give_equal_phis(self) -> None:
        # When detector two is a copy of detector one, every pairing matches.
        patterns = (
            [(True, True, True, True)] * 30
            + [(False, False, False, False)] * 30
            + [(True, False, True, False)] * 20
            + [(False, True, False, True)] * 20
        )

        homogeneous, heterogeneous = condition_phis(_records(patterns))

        assert homogeneous == pytest.approx(heterogeneous)


class TestPairedDifference:
    def test_interval_brackets_the_point_difference(self) -> None:
        patterns = (
            [(True, True, True, True)] * 25
            + [(True, True, False, False)] * 25
            + [(False, False, True, True)] * 25
            + [(False, False, False, False)] * 25
        )

        result = paired_difference(_records(patterns), resamples=400, seed=3)

        assert result.lower <= result.difference <= result.upper

    def test_counts_the_objects_it_used(self) -> None:
        patterns = (
            [(True, True, True, True)] * 25
            + [(True, True, False, False)] * 25
            + [(False, False, True, True)] * 25
            + [(False, False, False, False)] * 25
        )

        result = paired_difference(_records(patterns), resamples=200, seed=3)

        assert result.objects == 100

    def test_is_deterministic_for_a_fixed_seed(self) -> None:
        patterns = (
            [(True, True, True, True)] * 25
            + [(True, True, False, False)] * 25
            + [(False, False, True, True)] * 25
            + [(False, False, False, False)] * 25
        )
        records = _records(patterns)

        first = paired_difference(records, resamples=300, seed=11)
        second = paired_difference(records, resamples=300, seed=11)

        assert (first.lower, first.difference, first.upper) == (
            second.lower,
            second.difference,
            second.upper,
        )

    def test_rejects_empty_input(self) -> None:
        with pytest.raises(ValueError, match="no scored objects"):
            paired_difference([], resamples=100, seed=1)
