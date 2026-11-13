"""Resolution policy interface v2: one decision per inspection task.

A task is one scene's inspection. CLOSE accepts the confirmed object set as
complete; when two agents' agreement is weak evidence (high dependence), a
policy should VERIFY instead, paying a re-observation to avoid a false
"all clear". Baselines (Track C) and the dependence-aware policy (Track A)
implement the same `decide`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from trace_contracts.estimation import DependenceEstimator
from trace_contracts.observations import AgentFrameReport


class Action(Enum):
    CLOSE = "close"
    VERIFY = "verify"
    WAIT = "wait"


@dataclass(frozen=True)
class TaskDecision:
    """A policy outcome with lineage for deterministic replay (AD-003)."""

    task_id: str
    action: Action
    reason_code: str
    causal_report_ids: tuple[str, ...]
    confirmed_track_ids: tuple[str, ...]
    policy_version: str
    estimator_version: str


@runtime_checkable
class ResolutionPolicy(Protocol):
    """Port for every policy, baseline or treatment."""

    version: str

    def decide(
        self,
        task_id: str,
        reports: Sequence[AgentFrameReport],
        estimator: DependenceEstimator,
    ) -> TaskDecision:
        """Decide one task from the reports received so far."""
        ...
