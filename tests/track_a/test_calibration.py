"""Calibrated estimator: fit on practice scenes, freeze, check on exam scenes."""

from __future__ import annotations

import pytest

from evidence_resolution.calibration import (
    CalibratedEstimator,
    exam_check,
    fit_calibration,
    split_by_value,
    split_scenes,
)
from spike_dependence.double_fault import PairedErrorRecord
from trace_contracts.estimation import DependenceEstimator, DependenceQuery

YOLO = ("yolo11m", "yolo11m")
MIXED = ("yolo11m", "rtdetr-l")


def records(
    both: int, only_a: int, only_b: int, neither: int, scene: str = "scene-000"
) -> list[PairedErrorRecord]:
    """Build records with an exact contingency table."""
    cells = (
        [(True, True)] * both
        + [(True, False)] * only_a
        + [(False, True)] * only_b
        + [(False, False)] * neither
    )
    return [
        PairedErrorRecord(f"obj-{i}", scene, a, b) for i, (a, b) in enumerate(cells)
    ]


def test_split_is_deterministic_disjoint_and_complete() -> None:
    scenes = [f"scene-{i:03d}" for i in range(54)]
    practice, exam = split_scenes(scenes, seed=7)
    assert (practice, exam) == split_scenes(list(reversed(scenes)), seed=7)
    assert set(practice).isdisjoint(exam)
    assert set(practice) | set(exam) == set(scenes)
    assert len(practice) == 27


def test_split_by_value_holds_out_one_setting() -> None:
    weather = {
        "s1": "ClearNoon",
        "s2": "WetNoon",
        "s3": "CloudySunset",
        "s4": "WetNoon",
    }
    practice, exam = split_by_value(list(weather), weather, held_out="WetNoon")
    assert (practice, exam) == (("s1", "s3"), ("s2", "s4"))


def test_fit_recovers_miss_rates_and_ratio() -> None:
    # 100 objects: A wrong 40, B wrong 30, both 20 -> ratio 0.20 / (0.4 x 0.3) = 1.667.
    estimator = fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=200, seed=0)
    estimate = estimator.estimate(DependenceQuery(("a", "b"), YOLO))
    assert estimate.miss_rates == (pytest.approx(0.4), pytest.approx(0.3))
    assert estimate.inflation_ratio == pytest.approx(0.2 / 0.12)
    assert estimate.lower <= estimate.inflation_ratio <= estimate.upper
    assert estimate.joint_miss_probability() == pytest.approx(0.2)


def test_satisfies_the_frozen_estimator_port() -> None:
    assert isinstance(
        fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=50, seed=0),
        DependenceEstimator,
    )


def test_reversed_detector_order_swaps_the_miss_rates() -> None:
    estimator = fit_calibration({MIXED: records(20, 20, 10, 50)}, resamples=50, seed=0)
    forward = estimator.estimate(DependenceQuery(("a", "b"), MIXED))
    reverse = estimator.estimate(DependenceQuery(("a", "b"), (MIXED[1], MIXED[0])))
    assert reverse.miss_rates == (forward.miss_rates[1], forward.miss_rates[0])
    assert reverse.inflation_ratio == forward.inflation_ratio


def test_unknown_detector_pair_is_refused_not_guessed() -> None:
    estimator = fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=50, seed=0)
    with pytest.raises(KeyError):
        estimator.estimate(DependenceQuery(("a", "b"), ("rtdetr-l", "rtdetr-l")))


def test_version_is_a_fingerprint_of_the_frozen_numbers() -> None:
    first = fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=50, seed=0)
    same = fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=50, seed=0)
    other = fit_calibration({YOLO: records(25, 15, 10, 50)}, resamples=50, seed=0)
    assert first.version == same.version
    assert first.version != other.version
    assert first.version.startswith("calibrated-")
    assert isinstance(first, CalibratedEstimator)


def test_exam_check_compares_predicted_and_observed_shared_misses() -> None:
    estimator = fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=50, seed=0)
    check = exam_check(estimator, YOLO, records(10, 10, 10, 70))
    assert check.objects == 100
    assert check.predicted_joint_miss == pytest.approx(0.2)
    assert check.observed_joint_miss == pytest.approx(0.1)
    assert check.naive_joint_miss == pytest.approx(0.4 * 0.3)


def test_calibrated_estimator_drives_the_policy_end_to_end() -> None:
    from test_association import SETUP
    from test_miss_risk_policy import agreeing_reports

    from evidence_resolution.association import PoseProjectionAssociation
    from evidence_resolution.miss_risk_policy import MissRiskPolicy
    from trace_contracts.policy import Action

    # Practice numbers give a 0.20 shared-miss risk for two YOLO agents.
    estimator = fit_calibration({YOLO: records(20, 20, 10, 50)}, resamples=50, seed=0)
    policy = MissRiskPolicy(PoseProjectionAssociation(SETUP), miss_risk_tolerance=0.1)
    decision = policy.decide("scene-000", agreeing_reports(), estimator)
    assert decision.action is Action.VERIFY
    assert decision.estimator_version == estimator.version
