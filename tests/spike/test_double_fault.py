"""Spec for the double-fault dependence statistic (Kuncheva & Whitaker 2003).

The spike's single reported number is the dependence inflation ratio: the rate
at which two agents are wrong about the SAME object, divided by the rate that
independence would predict. A ratio of 1 means the MATE independence
assumption survives; well above 1 means it does not.
"""

from __future__ import annotations

import math

import pytest

from spike_dependence.double_fault import (
    PairedErrorRecord,
    contingency,
    dependence_inflation_ratio,
    inflation_ratio_with_interval,
    odds_ratio,
    phi_coefficient,
)


def _records(pattern: list[tuple[bool, bool]]) -> list[PairedErrorRecord]:
    """Build paired records from (agent_a_wrong, agent_b_wrong) tuples."""
    return [
        PairedErrorRecord(
            object_id=f"obj-{index}",
            frame_id=f"frame-{index}",
            agent_a_wrong=a_wrong,
            agent_b_wrong=b_wrong,
        )
        for index, (a_wrong, b_wrong) in enumerate(pattern)
    ]


class TestContingency:
    def test_counts_all_four_cells(self) -> None:
        table = contingency(
            _records([(True, True), (True, False), (False, True), (False, False)])
        )

        assert (table.both_wrong, table.only_a_wrong) == (1, 1)
        assert (table.only_b_wrong, table.neither_wrong) == (1, 1)
        assert table.total == 4

    def test_marginals_are_per_agent_error_rates(self) -> None:
        table = contingency(_records([(True, True), (True, False), (False, False)]))

        assert table.marginal_a == pytest.approx(2 / 3)
        assert table.marginal_b == pytest.approx(1 / 3)

    def test_double_fault_is_the_joint_error_rate(self) -> None:
        table = contingency(_records([(True, True), (True, False), (False, False)]))

        assert table.double_fault == pytest.approx(1 / 3)

    def test_rejects_empty_input(self) -> None:
        with pytest.raises(ValueError, match="at least one paired record"):
            contingency([])


class TestInflationRatio:
    def test_independent_agents_give_ratio_of_one(self) -> None:
        # p_a = p_b = 1/2, joint = 1/4 exactly: the independence product.
        records = _records(
            [(True, True), (True, False), (False, True), (False, False)]
        )

        assert dependence_inflation_ratio(records) == pytest.approx(1.0)

    def test_perfectly_correlated_agents_inflate_above_one(self) -> None:
        # Both agents wrong on the same half of objects, never wrong alone.
        records = _records([(True, True), (True, True), (False, False), (False, False)])

        # joint = 1/2, independence predicts 1/2 * 1/2 = 1/4 -> ratio 2.0
        assert dependence_inflation_ratio(records) == pytest.approx(2.0)

    def test_anticorrelated_agents_deflate_below_one(self) -> None:
        records = _records([(True, False), (False, True), (True, False), (False, True)])

        assert dependence_inflation_ratio(records) == pytest.approx(0.0)

    def test_undefined_when_an_agent_never_errs(self) -> None:
        records = _records([(False, False), (False, True)])

        with pytest.raises(ValueError, match="no errors"):
            dependence_inflation_ratio(records)


class TestBootstrapInterval:
    def test_interval_brackets_the_point_estimate(self) -> None:
        pattern = [(True, True)] * 30 + [(False, False)] * 30
        pattern += [(True, False)] * 10 + [(False, True)] * 10
        records = _records(pattern)

        result = inflation_ratio_with_interval(records, resamples=500, seed=7)

        assert result.lower <= result.ratio <= result.upper

    def test_is_deterministic_for_a_fixed_seed(self) -> None:
        pattern = [(True, True)] * 20 + [(False, False)] * 20
        pattern += [(True, False)] * 10 + [(False, True)] * 10
        records = _records(pattern)

        first = inflation_ratio_with_interval(records, resamples=300, seed=11)
        second = inflation_ratio_with_interval(records, resamples=300, seed=11)

        assert (first.lower, first.ratio, first.upper) == (
            second.lower,
            second.ratio,
            second.upper,
        )

    def test_strong_correlation_excludes_one_from_the_interval(self) -> None:
        pattern = [(True, True)] * 40 + [(False, False)] * 60
        records = _records(pattern)

        result = inflation_ratio_with_interval(records, resamples=800, seed=3)

        assert result.lower > 1.0


class TestAssociationMeasures:
    def test_independent_table_gives_unit_odds_ratio(self) -> None:
        table = contingency(
            _records([(True, True), (True, False), (False, True), (False, False)])
        )

        assert odds_ratio(table) == pytest.approx(1.0)

    def test_independent_table_gives_zero_phi(self) -> None:
        table = contingency(
            _records([(True, True), (True, False), (False, True), (False, False)])
        )

        assert phi_coefficient(table) == pytest.approx(0.0)

    def test_perfect_agreement_gives_phi_of_one(self) -> None:
        table = contingency(_records([(True, True)] * 10 + [(False, False)] * 10))

        assert phi_coefficient(table) == pytest.approx(1.0)

    def test_perfect_disagreement_gives_phi_of_minus_one(self) -> None:
        table = contingency(_records([(True, False)] * 10 + [(False, True)] * 10))

        assert phi_coefficient(table) == pytest.approx(-1.0)

    def test_positive_association_raises_the_odds_ratio_above_one(self) -> None:
        table = contingency(
            _records(
                [(True, True)] * 40
                + [(False, False)] * 40
                + [(True, False)] * 10
                + [(False, True)] * 10
            )
        )

        assert odds_ratio(table) > 1.0

    def test_odds_ratio_stays_finite_on_an_empty_cell(self) -> None:
        # No object had exactly one agent wrong, so a raw odds ratio divides
        # by zero; the correction must keep it finite.
        table = contingency(_records([(True, True)] * 10 + [(False, False)] * 10))

        assert math.isfinite(odds_ratio(table))

    def test_phi_is_undefined_when_an_agent_never_errs(self) -> None:
        table = contingency(_records([(False, False), (False, True)]))

        with pytest.raises(ValueError, match="no errors"):
            phi_coefficient(table)
