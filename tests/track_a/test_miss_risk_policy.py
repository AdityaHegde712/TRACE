"""Miss-risk policy: one policy, naive or dependence-aware depending on the estimator."""

from __future__ import annotations

from dataclasses import dataclass

from test_association import POSE_A, POSE_B, SETUP, box_standing_at, report

from evidence_resolution.association import PoseProjectionAssociation
from evidence_resolution.miss_risk_policy import MissRiskPolicy
from trace_contracts.estimation import (
    DependenceEstimate,
    DependenceQuery,
    IndependenceEstimator,
)
from trace_contracts.policy import Action, ResolutionPolicy


@dataclass(frozen=True)
class FixedEstimator:
    """Spike-like dependence: ratio 1.67, miss rates 0.37 and 0.35."""

    version: str = "fixed-spike-v0"

    def estimate(self, query: DependenceQuery) -> DependenceEstimate:
        return DependenceEstimate(
            1.671, 1.5, 1.87, self.version, miss_rates=(0.37, 0.35)
        )


def agreeing_reports() -> list:
    target = (2.0, 1.0)
    return [
        report("agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, target))]),
        report("agent-b", POSE_B, [("b1", "car", box_standing_at(POSE_B, target))]),
    ]


def policy(tolerance: float = 0.1) -> MissRiskPolicy:
    return MissRiskPolicy(
        PoseProjectionAssociation(SETUP), miss_risk_tolerance=tolerance
    )


def test_satisfies_the_frozen_policy_port() -> None:
    assert isinstance(policy(), ResolutionPolicy)


def test_naive_estimator_closes_when_both_agents_agree() -> None:
    decision = policy().decide("scene-000", agreeing_reports(), IndependenceEstimator())
    assert decision.action is Action.CLOSE
    assert decision.confirmed_track_ids == ("track-000",)
    assert decision.estimator_version == "independence-v0"
    assert set(decision.causal_report_ids) == {"rep-agent-a", "rep-agent-b"}


def test_dependence_aware_estimator_verifies_the_same_reports() -> None:
    # 1.671 x 0.37 x 0.35 = 0.216 chance a present object was missed by both: too high.
    decision = policy(tolerance=0.1).decide(
        "scene-000", agreeing_reports(), FixedEstimator()
    )
    assert decision.action is Action.VERIFY
    assert decision.reason_code == "shared_miss_risk_above_tolerance"


def test_closes_under_dependence_when_tolerance_allows() -> None:
    decision = policy(tolerance=0.3).decide(
        "scene-000", agreeing_reports(), FixedEstimator()
    )
    assert decision.action is Action.CLOSE


def test_waits_until_two_agents_have_reported() -> None:
    decision = policy().decide(
        "scene-000", agreeing_reports()[:1], IndependenceEstimator()
    )
    assert decision.action is Action.WAIT


def test_object_seen_by_only_one_agent_needs_verification() -> None:
    reports = [
        report("agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, (2.0, 1.0)))]),
        report("agent-b", POSE_B, []),
    ]
    decision = policy().decide("scene-000", reports, IndependenceEstimator())
    assert decision.action is Action.VERIFY
    assert decision.reason_code == "single_source_track"
