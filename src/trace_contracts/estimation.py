"""The dependence estimator interface, decoupled from the research answer.

A shared miss leaves no claim, so the double-miss rate cannot be estimated
from claim streams alone (two-list capture-recapture: the both-missed cell is
never observed). Estimators therefore answer from agent-pair identity plus
covariates both agents can observe; object features are optional because an
unseen object has none. Which estimator wins (RQ2) is Track A work after M1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class DependenceQuery:
    """What a policy asks about two agents, optionally about one candidate object.

    `covariates` holds observable context only, such as illumination or the
    viewpoint angle derived from camera poses; never ground truth (AD-001).
    `label` and `box_areas` are set only when at least one agent detected the
    object; spike stratum analysis shows inflation varies with size (SD-021).
    """

    source_ids: tuple[str, str]
    detectors: tuple[str, str]
    covariates: tuple[tuple[str, str], ...] = ()
    label: str | None = None
    box_areas: tuple[float | None, float | None] = (None, None)

    def __post_init__(self) -> None:
        if self.source_ids[0] == self.source_ids[1]:
            raise ValueError("dependence needs two distinct sources")


@dataclass(frozen=True)
class DependenceEstimate:
    """Double-fault inflation ratio with its interval; 1.0 means independent.

    `miss_rates` are each agent's estimated marginal miss probability, so a
    policy can ask how likely "nothing reported here" hides a real object.
    """

    inflation_ratio: float
    lower: float
    upper: float
    estimator_version: str
    miss_rates: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self) -> None:
        if not 0.0 < self.lower <= self.inflation_ratio <= self.upper:
            raise ValueError("need 0 < lower <= inflation_ratio <= upper")
        if not all(0.0 <= rate <= 1.0 for rate in self.miss_rates):
            raise ValueError("miss rates must lie in [0, 1]")

    def joint_miss_probability(self) -> float:
        """P(both agents miss a present object) = ratio x miss_A x miss_B."""
        return self.inflation_ratio * self.miss_rates[0] * self.miss_rates[1]


@runtime_checkable
class DependenceEstimator(Protocol):
    """Port for every dependence estimator. Never reads ground truth online (AD-001)."""

    version: str

    def estimate(self, query: DependenceQuery) -> DependenceEstimate:
        """Return the estimated dependence for this query."""
        ...


@dataclass(frozen=True)
class IndependenceEstimator:
    """Naive baseline: different source_id means independent. Always 1.0.

    The miss rates are placeholders until Track A calibrates them; the naive
    policy reads only the ratio.
    """

    version: str = "independence-v0"

    def estimate(self, query: DependenceQuery) -> DependenceEstimate:
        return DependenceEstimate(1.0, 1.0, 1.0, self.version)
