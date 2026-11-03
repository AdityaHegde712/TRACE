"""The double-fault dependence statistic for a pair of perceiving agents.

The measure is Kuncheva & Whitaker (2003) double-fault, adopted unchanged and
expressed as a ratio against the independence prediction. It is not a new
statistic and must never be presented as one.

Truth is used only to label a detection right or wrong before it reaches this
module (project decision AD-001); nothing here reads simulator state.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import quantiles

_MIN_VALID_RESAMPLES = 2


@dataclass(frozen=True)
class PairedErrorRecord:
    """Whether each of two agents was wrong about one shared object."""

    object_id: str
    frame_id: str
    agent_a_wrong: bool
    agent_b_wrong: bool


@dataclass(frozen=True)
class ContingencyTable:
    """The 2x2 table of joint correctness over every shared object."""

    both_wrong: int
    only_a_wrong: int
    only_b_wrong: int
    neither_wrong: int

    @property
    def total(self) -> int:
        """Return the number of scored objects behind this table."""
        return (
            self.both_wrong
            + self.only_a_wrong
            + self.only_b_wrong
            + self.neither_wrong
        )

    @property
    def marginal_a(self) -> float:
        """Return agent A's own error rate, ignoring agent B."""
        return (self.both_wrong + self.only_a_wrong) / self.total

    @property
    def marginal_b(self) -> float:
        """Return agent B's own error rate, ignoring agent A."""
        return (self.both_wrong + self.only_b_wrong) / self.total

    @property
    def double_fault(self) -> float:
        """Return the observed rate of both agents being wrong together."""
        return self.both_wrong / self.total

    @property
    def independent_prediction(self) -> float:
        """Return the joint error rate independence would predict."""
        return self.marginal_a * self.marginal_b


@dataclass(frozen=True)
class InflationEstimate:
    """A point estimate of the inflation ratio with a bootstrap interval."""

    ratio: float
    lower: float
    upper: float
    resamples_used: int
    table: ContingencyTable


def odds_ratio(table: ContingencyTable) -> float:
    """Return the odds ratio of joint error; 1.0 means independent.

    Unlike the inflation ratio, this does not divide by the marginals, so it
    compares fairly across detectors with different accuracy. A Haldane-
    Anscombe half-count keeps it finite when a cell is empty.
    """
    both = table.both_wrong + 0.5
    only_a = table.only_a_wrong + 0.5
    only_b = table.only_b_wrong + 0.5
    neither = table.neither_wrong + 0.5
    return (both * neither) / (only_a * only_b)


def phi_coefficient(table: ContingencyTable) -> float:
    """Return the phi correlation between the two agents' error indicators.

    0.0 means independent, 1.0 means they always fail together and succeed
    together, -1.0 means exactly one of them is always wrong.
    """
    denominator = math.sqrt(
        (table.both_wrong + table.only_a_wrong)
        * (table.only_b_wrong + table.neither_wrong)
        * (table.both_wrong + table.only_b_wrong)
        * (table.only_a_wrong + table.neither_wrong)
    )
    if denominator == 0.0:
        raise ValueError("phi is undefined when an agent makes no errors")

    numerator = (table.both_wrong * table.neither_wrong) - (
        table.only_a_wrong * table.only_b_wrong
    )
    return numerator / denominator


def contingency(records: Sequence[PairedErrorRecord]) -> ContingencyTable:
    """Return the 2x2 joint-error table for the given paired records."""
    if not records:
        raise ValueError("contingency requires at least one paired record")

    both = sum(1 for r in records if r.agent_a_wrong and r.agent_b_wrong)
    only_a = sum(1 for r in records if r.agent_a_wrong and not r.agent_b_wrong)
    only_b = sum(1 for r in records if not r.agent_a_wrong and r.agent_b_wrong)
    neither = len(records) - both - only_a - only_b
    return ContingencyTable(both, only_a, only_b, neither)


def _ratio_from_table(table: ContingencyTable) -> float:
    """Return double-fault divided by the independence prediction."""
    predicted = table.independent_prediction
    if predicted == 0.0:
        raise ValueError(
            "inflation ratio is undefined when an agent makes no errors"
        )
    return table.double_fault / predicted


def dependence_inflation_ratio(records: Sequence[PairedErrorRecord]) -> float:
    """Return the dependence inflation ratio; 1.0 means independent."""
    return _ratio_from_table(contingency(records))


def inflation_ratio_with_interval(
    records: Sequence[PairedErrorRecord],
    *,
    resamples: int = 2000,
    seed: int = 0,
    confidence: float = 0.95,
) -> InflationEstimate:
    """Return the inflation ratio with a percentile bootstrap interval.

    Resamples in which either agent happens to make no error leave the ratio
    undefined; they are dropped rather than silently coerced to a number.
    """
    if resamples < 1:
        raise ValueError("resamples must be at least 1")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie strictly between 0 and 1")

    table = contingency(records)
    point = _ratio_from_table(table)

    rng = random.Random(seed)
    population = list(records)
    size = len(population)
    ratios: list[float] = []
    for _ in range(resamples):
        draw = [population[rng.randrange(size)] for _ in range(size)]
        try:
            ratios.append(_ratio_from_table(contingency(draw)))
        except ValueError:
            continue

    if len(ratios) < _MIN_VALID_RESAMPLES:
        raise ValueError(
            "too few resamples yielded a defined ratio to form an interval"
        )

    ratios.sort()
    tail = (1.0 - confidence) / 2.0
    cuts = quantiles(ratios, n=1000, method="inclusive")
    lower = cuts[max(0, round(tail * 1000) - 1)]
    upper = cuts[min(len(cuts) - 1, round((1.0 - tail) * 1000) - 1)]
    return InflationEstimate(point, lower, upper, len(ratios), table)
