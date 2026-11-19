from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from baselines import (
    AlwaysVerifyPolicy,
    FirstReportPolicy,
    LatestReportPolicy,
    MajorityVotePolicy,
    NeverVerifyPolicy,
)
from evidence_resolution.association import CameraSetup, PoseProjectionAssociation
from trace_contracts.estimation import IndependenceEstimator
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)
from trace_contracts.policy import Action, ResolutionPolicy

ASSOCIATION = PoseProjectionAssociation(CameraSetup(800, 600, 90, 14))
ESTIMATOR = IndependenceEstimator()
T0 = datetime(2026, 11, 18, tzinfo=UTC)


def report(source="a", detected=True, arrival=0):
    return AgentFrameReport(
        f"rep-{source}",
        source,
        "scene",
        "frame",
        T0,
        T0 + timedelta(seconds=arrival),
        CameraPose(0, 0, 14, 0, -30),
        "yolo11m",
        (Detection("d", "car", 0.9, BoundingBox(390, 300, 410, 400)),)
        if detected
        else (),
    )


@pytest.mark.parametrize(
    "policy_type",
    [
        LatestReportPolicy,
        FirstReportPolicy,
        MajorityVotePolicy,
        AlwaysVerifyPolicy,
        NeverVerifyPolicy,
    ],
)
def test_empty_input_waits_and_contract_is_supported(policy_type):
    policy = policy_type(ASSOCIATION)
    assert isinstance(policy, ResolutionPolicy)
    result = policy.decide("scene", [], ESTIMATOR)
    assert result.action == Action.WAIT
    assert result.confirmed_track_ids == ()
    assert result.policy_version == policy.version
    assert result.estimator_version == ESTIMATOR.version


def test_first_latest_use_arrival_and_canonical_track_ids():
    reports = [report("a", True, 2), report("b", False, 1)]
    latest = LatestReportPolicy(ASSOCIATION).decide("scene", reports, ESTIMATOR)
    first = FirstReportPolicy(ASSOCIATION).decide("scene", reports, ESTIMATOR)
    assert latest.action == first.action == Action.CLOSE
    assert latest.confirmed_track_ids == ("track-000",)
    assert first.confirmed_track_ids == ()
    assert latest.causal_report_ids == ("rep-a",)
    assert first.causal_report_ids == ("rep-b",)


def test_majority_tie_verifies_and_agreement_closes():
    policy = MajorityVotePolicy(ASSOCIATION)
    tie = policy.decide("scene", [report(), report("b", False)], ESTIMATOR)
    assert tie.action == Action.VERIFY
    assert tie.confirmed_track_ids == ()
    agreement = policy.decide("scene", [report(), report("b")], ESTIMATOR)
    assert agreement.action == Action.CLOSE
    assert agreement.confirmed_track_ids == ("track-000",)
    empty = policy.decide(
        "scene", [report(detected=False), report("b", False)], ESTIMATOR
    )
    assert empty.action == Action.CLOSE
    assert empty.confirmed_track_ids == ()


def test_repeated_source_does_not_add_majority_votes():
    repeated = replace(
        report(), report_id="rep-a2", arrived_at=T0 + timedelta(seconds=1)
    )
    result = MajorityVotePolicy(ASSOCIATION).decide(
        "scene", [report(), repeated, report("b", False)], ESTIMATOR
    )
    assert result.action == Action.VERIFY
    assert result.confirmed_track_ids == ()


def test_verification_extremes_and_permutation_stability():
    reports = [report(), report("b", False)]
    for cls, action in [
        (AlwaysVerifyPolicy, Action.VERIFY),
        (NeverVerifyPolicy, Action.CLOSE),
    ]:
        policy = cls(ASSOCIATION)
        result = policy.decide("scene", reports, ESTIMATOR)
        assert result.action == action
        assert result == policy.decide("scene", list(reversed(reports)), ESTIMATOR)
    assert NeverVerifyPolicy(ASSOCIATION).decide(
        "scene", reports, ESTIMATOR
    ).confirmed_track_ids == ("track-000",)
