"""Spec for the tercile split used by the difficulty-confound test."""

from __future__ import annotations

import pytest

from spike_dependence.double_fault import PairedErrorRecord
from spike_dependence.stratify import SizedRecord, split_into_terciles


def _sized(area: float, index: int) -> SizedRecord:
    return SizedRecord(
        record=PairedErrorRecord(f"obj-{index}", "scene-000", False, False),
        mean_area_px=area,
    )


class TestSplitIntoTerciles:
    def test_orders_by_area_before_cutting(self) -> None:
        sized = [_sized(area, i) for i, area in enumerate([900.0, 100.0, 500.0])]

        small, medium, large = split_into_terciles(sized)

        assert small[0].mean_area_px == 100.0
        assert medium[0].mean_area_px == 500.0
        assert large[0].mean_area_px == 900.0

    def test_groups_are_balanced_to_within_two(self) -> None:
        sized = [_sized(float(i), i) for i in range(100)]

        small, medium, large = split_into_terciles(sized)

        assert len(small) == len(medium) == 33
        assert len(large) == 34
        assert len(small) + len(medium) + len(large) == 100

    def test_largest_group_absorbs_the_remainder(self) -> None:
        sized = [_sized(float(i), i) for i in range(11)]

        small, medium, large = split_into_terciles(sized)

        assert (len(small), len(medium), len(large)) == (3, 3, 5)

    def test_strata_do_not_overlap_in_area(self) -> None:
        sized = [_sized(float(i), i) for i in range(30)]

        small, medium, large = split_into_terciles(sized)

        assert small[-1].mean_area_px < medium[0].mean_area_px
        assert medium[-1].mean_area_px < large[0].mean_area_px

    def test_rejects_too_few_records(self) -> None:
        with pytest.raises(ValueError, match="at least three"):
            split_into_terciles([_sized(1.0, 0), _sized(2.0, 1)])
