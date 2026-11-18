"""A3: watermarked reconciliation makes decisions independent of arrival order.

Reports from different agents reach the resolver in any order. The reconciler
holds them until the watermark (newest observed_at minus slack) passes them,
then releases them in one canonical order. Every arrival permutation within
the slack must yield the same order, the same decisions, and the same trace hash.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from itertools import permutations

import pytest
from test_association import POSE_A, POSE_B, SETUP, T0, box_standing_at, report

from evidence_resolution.association import PoseProjectionAssociation
from evidence_resolution.miss_risk_policy import MissRiskPolicy
from evidence_resolution.reconciliation import (
    WatermarkedReconciler,
    canonical_trace_hash,
)
from trace_contracts.estimation import IndependenceEstimator
from trace_contracts.observations import AgentFrameReport
from trace_contracts.policy import Action, TaskDecision

SLACK = timedelta(seconds=5)


def scene_reports(scene: str, offset_s: float) -> list[AgentFrameReport]:
    target = (2.0, 1.0)
    observed = T0 + timedelta(seconds=offset_s)
    reports = [
        report("agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, target))]),
        report("agent-b", POSE_B, [("b1", "car", box_standing_at(POSE_B, target))]),
    ]
    return [
        replace(
            r,
            report_id=f"{scene}-{r.report_id}",
            scene_id=scene,
            observed_at=observed,
            arrived_at=observed + SLACK,
        )
        for r in reports
    ]


ALL_REPORTS = scene_reports("scene-000", 0.0) + scene_reports("scene-001", 2.0)


def reconcile(arrivals: list[AgentFrameReport]) -> list[AgentFrameReport]:
    reconciler = WatermarkedReconciler(SLACK)
    released: list[AgentFrameReport] = []
    for item in arrivals:
        released.extend(reconciler.ingest(item))
    released.extend(reconciler.flush())
    return released


def decide_all(ordered: list[AgentFrameReport]) -> list[TaskDecision]:
    policy = MissRiskPolicy(PoseProjectionAssociation(SETUP), miss_risk_tolerance=0.1)
    scenes = sorted({r.scene_id for r in ordered})
    return [
        policy.decide(
            scene,
            [r for r in ordered if r.scene_id == scene],
            IndependenceEstimator(),
        )
        for scene in scenes
    ]


def far_report(base: AgentFrameReport) -> AgentFrameReport:
    observed = T0 + timedelta(seconds=10)
    return replace(base, report_id="far", observed_at=observed, arrived_at=observed)


def canonical_ids() -> list[str]:
    return [r.report_id for r in reconcile(ALL_REPORTS)]


def test_releases_in_observed_source_report_order() -> None:
    assert canonical_ids() == [
        "scene-000-rep-agent-a",
        "scene-000-rep-agent-b",
        "scene-001-rep-agent-a",
        "scene-001-rep-agent-b",
    ]


def test_holds_reports_until_the_watermark_passes_them() -> None:
    reconciler = WatermarkedReconciler(SLACK)
    early, later = ALL_REPORTS[0], ALL_REPORTS[2]
    assert reconciler.ingest(early) == []
    # Newest observed is 2 s; watermark is -3 s, still before the 0 s report.
    assert reconciler.ingest(later) == []
    far = far_report(later)
    # Watermark moves to 5 s and releases both earlier reports in order.
    assert [r.report_id for r in reconciler.ingest(far)] == [
        early.report_id,
        later.report_id,
    ]
    assert [r.report_id for r in reconciler.flush()] == ["far"]


def test_every_arrival_permutation_gives_the_same_order() -> None:
    expected = canonical_ids()
    for arrivals in permutations(ALL_REPORTS):
        assert [r.report_id for r in reconcile(list(arrivals))] == expected


def test_every_arrival_permutation_gives_the_same_decisions() -> None:
    expected = decide_all(reconcile(ALL_REPORTS))
    assert [d.action for d in expected] == [Action.CLOSE, Action.CLOSE]
    for arrivals in permutations(ALL_REPORTS):
        assert decide_all(reconcile(list(arrivals))) == expected


def test_every_arrival_permutation_gives_the_same_trace_hash() -> None:
    expected = canonical_trace_hash(decide_all(reconcile(ALL_REPORTS)))
    assert len(expected) == 64
    for arrivals in permutations(ALL_REPORTS):
        assert canonical_trace_hash(decide_all(reconcile(list(arrivals)))) == expected


def test_trace_hash_changes_when_a_decision_changes() -> None:
    decisions = decide_all(reconcile(ALL_REPORTS))
    changed = [replace(decisions[0], action=Action.VERIFY), decisions[1]]
    assert canonical_trace_hash(changed) != canonical_trace_hash(decisions)


def test_a_report_behind_the_released_watermark_is_flagged_late() -> None:
    reconciler = WatermarkedReconciler(SLACK)
    far = far_report(ALL_REPORTS[0])
    reconciler.ingest(far)
    late = ALL_REPORTS[0]
    assert reconciler.ingest(late) == []
    assert reconciler.late == (late,)
    assert [r.report_id for r in reconciler.flush()] == ["far"]


def test_rejects_negative_slack() -> None:
    with pytest.raises(ValueError, match="slack"):
        WatermarkedReconciler(timedelta(seconds=-1))
