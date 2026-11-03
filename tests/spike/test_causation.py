"""Spec for the permutation controls that test WHAT is shared.

The spike measured that two agents fail together. It did not establish why.
Attributing the effect to "the shared scene" by elimination is correlation
read as causation. These controls break one shared thing at a time:

- permute agent B's errors WITHIN each scene: the scene is still shared, the
  specific object is not.
- permute agent B's errors ACROSS scenes: nothing is shared. This is the null
  control. If it does not return a ratio near 1.0, the statistic itself is
  biased and the headline cannot be trusted.

Permutation preserves each agent's marginal error rate exactly, so any drop in
the ratio comes from breaking the pairing and not from changing accuracy.
"""

from __future__ import annotations

import pytest

from spike_dependence.causation import (
    null_ratios,
    permute_across_scenes,
    permute_within_scenes,
)
from spike_dependence.double_fault import PairedErrorRecord, contingency


def _records(scene_count: int, per_scene: int) -> list[PairedErrorRecord]:
    """Build perfectly correlated records: both agents wrong on the same half."""
    records = []
    for scene in range(scene_count):
        for index in range(per_scene):
            wrong = index % 2 == 0
            records.append(
                PairedErrorRecord(
                    object_id=f"obj-{scene}-{index}",
                    frame_id=f"scene-{scene}",
                    agent_a_wrong=wrong,
                    agent_b_wrong=wrong,
                )
            )
    return records


class TestPermutationPreservesMarginals:
    def test_across_scene_permutation_keeps_both_marginals(self) -> None:
        records = _records(6, 8)
        before = contingency(records)

        after = contingency(permute_across_scenes(records, seed=1))

        assert after.marginal_a == pytest.approx(before.marginal_a)
        assert after.marginal_b == pytest.approx(before.marginal_b)

    def test_within_scene_permutation_keeps_both_marginals(self) -> None:
        records = _records(6, 8)
        before = contingency(records)

        after = contingency(permute_within_scenes(records, seed=1))

        assert after.marginal_a == pytest.approx(before.marginal_a)
        assert after.marginal_b == pytest.approx(before.marginal_b)

    def test_permutation_keeps_the_record_count(self) -> None:
        records = _records(6, 8)

        assert len(permute_across_scenes(records, seed=1)) == len(records)
        assert len(permute_within_scenes(records, seed=1)) == len(records)


class TestWithinSceneStaysInScene:
    def test_each_record_keeps_its_own_frame(self) -> None:
        records = _records(5, 6)

        permuted = permute_within_scenes(records, seed=2)

        assert [r.frame_id for r in permuted] == [r.frame_id for r in records]

    def test_per_scene_error_counts_are_unchanged(self) -> None:
        records = _records(5, 6)

        permuted = permute_within_scenes(records, seed=2)

        for scene in {r.frame_id for r in records}:
            before = sum(
                1 for r in records if r.frame_id == scene and r.agent_b_wrong
            )
            after = sum(
                1 for r in permuted if r.frame_id == scene and r.agent_b_wrong
            )
            assert before == after


class TestNullRatios:
    def test_breaking_the_pairing_destroys_a_perfect_correlation(self) -> None:
        # Observed data is perfectly correlated, so the ratio is well above 1.
        records = _records(10, 10)
        observed = contingency(records)
        observed_ratio = observed.double_fault / observed.independent_prediction

        ratios = null_ratios(records, permute_across_scenes, resamples=200, seed=5)
        mean_null = sum(ratios) / len(ratios)

        assert observed_ratio > 1.8
        assert mean_null == pytest.approx(1.0, abs=0.15)

    def test_returns_one_ratio_per_resample(self) -> None:
        ratios = null_ratios(_records(8, 8), permute_across_scenes, resamples=50, seed=5)

        assert len(ratios) == 50

    def test_is_deterministic_for_a_fixed_seed(self) -> None:
        records = _records(8, 8)

        first = null_ratios(records, permute_within_scenes, resamples=40, seed=9)
        second = null_ratios(records, permute_within_scenes, resamples=40, seed=9)

        assert first == second

    def test_rejects_empty_input(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            null_ratios([], permute_across_scenes, resamples=10, seed=1)
