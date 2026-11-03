"""Name the spike outcome and render it as a report.

HANDOFF.md lists three acceptable outcomes and states that outcome 2 must not
be buried or softened. The wording here is therefore fixed in the tests: a
negligible result is reported as a finding, not as a disappointment.

The statistic is Kuncheva & Whitaker (2003) double-fault, adopted unchanged
and expressed as a ratio. It is never presented as a new measure.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from spike_dependence.double_fault import (
    InflationEstimate,
    PairedErrorRecord,
    inflation_ratio_with_interval,
)

_ATTRIBUTION = (
    "Statistic: the double-fault measure of Kuncheva & Whitaker (2003), "
    "adopted unchanged and expressed as a ratio against the independence "
    "prediction. It is not a new statistic."
)


class Outcome(Enum):
    """The three data-determined readings of the inflation ratio."""

    CORRELATED = "Outcome 1 - correlated errors"
    NEGLIGIBLE = "Outcome 2 - independence assumption survives"
    ANTICORRELATED = "Outcome 3 (variant) - errors anti-correlated"


@dataclass(frozen=True)
class SpikeReport:
    """Everything the spike reports, with the evidence behind it."""

    estimate: InflationEstimate
    outcome: Outcome
    objects_scored: int
    frames_scored: int


def classify_outcome(estimate: InflationEstimate) -> Outcome:
    """Return the outcome named by where the interval sits relative to 1.0.

    The interval decides, not the point estimate. A ratio of 1.4 whose
    interval spans 1.0 is not evidence of correlation.
    """
    if estimate.lower > 1.0:
        return Outcome.CORRELATED
    if estimate.upper < 1.0:
        return Outcome.ANTICORRELATED
    return Outcome.NEGLIGIBLE


def build_report(
    records: Sequence[PairedErrorRecord],
    *,
    resamples: int = 2000,
    seed: int = 0,
    confidence: float = 0.95,
) -> SpikeReport:
    """Compute the estimate and name the outcome for the scored objects."""
    if not records:
        raise ValueError("cannot report on no scored objects")

    estimate = inflation_ratio_with_interval(
        records, resamples=resamples, seed=seed, confidence=confidence
    )
    return SpikeReport(
        estimate=estimate,
        outcome=classify_outcome(estimate),
        objects_scored=len(records),
        frames_scored=len({record.frame_id for record in records}),
    )


def _verdict_sentence(report: SpikeReport) -> str:
    """Return the one plain sentence that answers the spike question."""
    if report.outcome is Outcome.CORRELATED:
        return (
            "The two agents were wrong together more often than independence "
            "predicts. The method framing holds; proceed to design."
        )
    if report.outcome is Outcome.ANTICORRELATED:
        return (
            "The two agents were wrong together LESS often than independence "
            "predicts. This is a real finding and it does not support the "
            "method framing."
        )
    return (
        "The two agents' errors co-occurred at about the rate independence "
        "predicts. MATE's independence assumption survives in this setting. "
        "This is a real finding, not a failed experiment; the project pivots."
    )


def render_markdown(report: SpikeReport) -> str:
    """Return the full spike report as Markdown."""
    estimate = report.estimate
    table = estimate.table
    lines = [
        "# Dependence spike result",
        "",
        f"**{report.outcome.value}**",
        "",
        _verdict_sentence(report),
        "",
        "## The number",
        "",
        f"- Dependence inflation ratio: **{estimate.ratio:.3f}**",
        f"- 95% bootstrap interval: **[{estimate.lower:.3f}, {estimate.upper:.3f}]**",
        f"- Observed joint error rate (double-fault): {table.double_fault:.4f}",
        f"- Rate independence predicts: {table.independent_prediction:.4f}",
        "",
        "A ratio of 1.0 means independent. The interval decides the outcome,",
        "not the point estimate.",
        "",
        "## Evidence",
        "",
        f"- Objects scored: {report.objects_scored}",
        f"- Frames scored: {report.frames_scored}",
        f"- Bootstrap resamples used: {estimate.resamples_used}",
        f"- Marginal error rate, agent A: {table.marginal_a:.4f}",
        f"- Marginal error rate, agent B: {table.marginal_b:.4f}",
        "",
        "| Cell | Count |",
        "| --- | --- |",
        f"| Both wrong | {table.both_wrong} |",
        f"| Only A wrong | {table.only_a_wrong} |",
        f"| Only B wrong | {table.only_b_wrong} |",
        f"| Neither wrong | {table.neither_wrong} |",
        "",
        "## Provenance",
        "",
        _ATTRIBUTION,
        "",
        "Only objects visible to BOTH agents are scored. Simulator truth was",
        "used for scoring alone and never entered the detection path (AD-001).",
    ]
    return "\n".join(lines) + "\n"
