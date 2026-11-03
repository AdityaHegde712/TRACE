"""Spec for naming the spike outcome and rendering the report.

HANDOFF.md names three acceptable outcomes and forbids burying or softening
outcome 2 (the MATE independence assumption survives). These tests pin that
behaviour: the renderer must state a negligible result as plainly as a
positive one, and must never describe the statistic as new.
"""

from __future__ import annotations

import pytest

from spike_dependence.double_fault import (
    PairedErrorRecord,
    inflation_ratio_with_interval,
)
from spike_dependence.report import (
    Outcome,
    build_report,
    classify_outcome,
    render_markdown,
)


def _records(pattern: list[tuple[bool, bool]]) -> list[PairedErrorRecord]:
    return [
        PairedErrorRecord(
            object_id=f"obj-{index}",
            frame_id=f"frame-{index // 4}",
            agent_a_wrong=a,
            agent_b_wrong=b,
        )
        for index, (a, b) in enumerate(pattern)
    ]


_CORRELATED = _records([(True, True)] * 40 + [(False, False)] * 60)
_INDEPENDENT = _records(
    [(True, True)] * 25 + [(True, False)] * 25 + [(False, True)] * 25 + [(False, False)] * 25
)


class TestClassifyOutcome:
    def test_interval_above_one_is_correlated(self) -> None:
        estimate = inflation_ratio_with_interval(_CORRELATED, resamples=800, seed=3)

        assert classify_outcome(estimate) is Outcome.CORRELATED

    def test_interval_spanning_one_is_negligible(self) -> None:
        estimate = inflation_ratio_with_interval(_INDEPENDENT, resamples=800, seed=3)

        assert classify_outcome(estimate) is Outcome.NEGLIGIBLE

    def test_interval_below_one_is_anticorrelated(self) -> None:
        pattern = [(True, False)] * 40 + [(False, True)] * 40 + [(False, False)] * 20
        estimate = inflation_ratio_with_interval(_records(pattern), resamples=800, seed=5)

        assert classify_outcome(estimate) is Outcome.ANTICORRELATED


class TestBuildReport:
    def test_counts_objects_and_frames(self) -> None:
        report = build_report(_CORRELATED, resamples=400, seed=1)

        assert report.objects_scored == 100
        assert report.frames_scored == 25

    def test_rejects_empty_records(self) -> None:
        with pytest.raises(ValueError, match="no scored objects"):
            build_report([], resamples=400, seed=1)


class TestRenderMarkdown:
    def test_reports_a_negligible_result_without_softening(self) -> None:
        text = render_markdown(build_report(_INDEPENDENT, resamples=400, seed=1))

        assert "Outcome 2" in text
        assert "independence assumption survives" in text
        assert "inconclusive" not in text.lower()
        assert "promising" not in text.lower()

    def test_reports_a_correlated_result(self) -> None:
        text = render_markdown(build_report(_CORRELATED, resamples=400, seed=1))

        assert "Outcome 1" in text

    def test_always_attributes_the_statistic(self) -> None:
        text = render_markdown(build_report(_CORRELATED, resamples=400, seed=1))

        assert "Kuncheva" in text
        assert "adopted" in text.lower()

    def test_includes_the_contingency_table_and_marginals(self) -> None:
        text = render_markdown(build_report(_CORRELATED, resamples=400, seed=1))

        for heading in ("Both wrong", "Only A wrong", "Only B wrong", "Neither wrong"):
            assert heading in text
        assert "Marginal error rate" in text

    def test_is_deterministic_for_a_fixed_seed(self) -> None:
        first = render_markdown(build_report(_CORRELATED, resamples=400, seed=9))
        second = render_markdown(build_report(_CORRELATED, resamples=400, seed=9))

        assert first == second
