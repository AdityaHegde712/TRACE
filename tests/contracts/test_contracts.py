"""M1-v0 cross-track contracts: the interfaces Tracks A, B, and C build against."""

from __future__ import annotations

import ast
from dataclasses import fields
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from trace_contracts import CONTRACT_VERSION
from trace_contracts.estimation import (
    DependenceEstimate,
    DependenceEstimator,
    DependenceQuery,
    IndependenceEstimator,
)
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
    report_from_dict,
    report_to_dict,
)
from trace_contracts.policy import Action, ResolutionPolicy, TaskDecision
from trace_contracts.results import RESULT_COLUMNS, RunResult, result_from_dict
from trace_contracts.scenario import (
    DetectorPairing,
    Illumination,
    Occluder,
    ScenarioManifestEntry,
    ViewpointDisparity,
    manifest_from_dict,
    manifest_to_dict,
    render_cells,
    sweep_cells,
)

PACKAGE_DIR: Path = Path(__file__).resolve().parents[2] / "src" / "trace_contracts"
T0 = datetime(2026, 11, 12, tzinfo=UTC)
POSE = CameraPose(x=1.0, y=2.0, z=8.0, yaw=180.0, pitch=-20.0)


def make_report(**overrides: object) -> AgentFrameReport:
    values: dict[str, object] = {
        "report_id": "rep-001",
        "source_id": "agent-a",
        "scene_id": "scene-000",
        "frame_id": "frame-000",
        "observed_at": T0,
        "arrived_at": T0 + timedelta(milliseconds=40),
        "camera_pose": POSE,
        "detector": "yolo11m",
        "detections": (
            Detection("det-1", "car", 0.9, BoundingBox(10.0, 20.0, 50.0, 60.0)),
        ),
    }
    values.update(overrides)
    return AgentFrameReport(**values)  # type: ignore[arg-type]


def test_contract_version_is_m1_v0() -> None:
    assert CONTRACT_VERSION == "m1-v0"


def test_render_matrix_is_viewpoint_by_occluder_by_illumination() -> None:
    cells = render_cells()
    assert len(cells) == 3 * 2 * 3
    assert len(set(cells)) == len(cells)
    assert cells == render_cells()


def test_sweep_adds_detector_pairing_over_the_same_renders() -> None:
    cells = sweep_cells()
    assert len(cells) == len(render_cells()) * 3
    assert {cell.render for cell in cells} == set(render_cells())


def test_channel_levels_match_the_spike() -> None:
    assert [v.yaw_separation_degrees for v in ViewpointDisparity] == [15.0, 60.0, 120.0]
    assert {i.value for i in Illumination} == {"ClearNoon", "CloudySunset", "WetNoon"}
    assert {o.value for o in Occluder} == {"none", "static"}
    assert DetectorPairing.HETEROGENEOUS.models == ("yolo11m", "rtdetr-l")


def test_cell_ids_are_stable_and_unique() -> None:
    ids = [cell.cell_id for cell in sweep_cells()]
    assert len(set(ids)) == len(ids)
    assert sweep_cells()[0].cell_id == "narrow-none-ClearNoon-homogeneous_yolo"


def test_manifest_round_trips_and_rejects_unknown_schema() -> None:
    entry = ScenarioManifestEntry("scene-000", render_cells()[0], "Town10HD", 42)
    assert manifest_from_dict(manifest_to_dict(entry)) == entry
    with pytest.raises(ValueError):
        manifest_from_dict({**manifest_to_dict(entry), "schema": "other"})


def test_report_round_trips_and_rejects_unknown_schema() -> None:
    report = make_report()
    assert report_from_dict(report_to_dict(report)) == report
    with pytest.raises(ValueError):
        report_from_dict({**report_to_dict(report), "schema": "other"})


def test_empty_report_means_looked_and_saw_nothing() -> None:
    report = make_report(detections=())
    assert report.detections == ()
    assert report_from_dict(report_to_dict(report)) == report


def test_report_cannot_arrive_before_it_was_observed() -> None:
    with pytest.raises(ValueError):
        make_report(arrived_at=T0 - timedelta(seconds=1))


def test_bounding_box_rejects_inverted_corners() -> None:
    with pytest.raises(ValueError):
        BoundingBox(50.0, 20.0, 10.0, 60.0)


def test_agent_visible_records_carry_no_truth_fields() -> None:
    truth_like = {"object_id", "ground_truth", "is_correct", "true_label"}
    for record in (AgentFrameReport, Detection, DependenceQuery):
        assert truth_like.isdisjoint({f.name for f in fields(record)})


@pytest.mark.parametrize(
    "module", ["observations", "estimation", "policy", "scenario", "association"]
)
def test_agent_side_modules_never_import_truth(module: str) -> None:
    tree = ast.parse((PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8"))
    imported = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(name.endswith("truth") for name in imported)


def test_independence_estimator_is_the_naive_baseline() -> None:
    estimator = IndependenceEstimator()
    query = DependenceQuery(("agent-a", "agent-b"), ("yolo11m", "yolo11m"))
    estimate = estimator.estimate(query)
    assert (estimate.inflation_ratio, estimate.lower, estimate.upper) == (1.0, 1.0, 1.0)
    assert estimate.joint_miss_probability() == pytest.approx(
        estimate.miss_rates[0] * estimate.miss_rates[1]
    )
    assert estimate.estimator_version == estimator.version
    assert isinstance(estimator, DependenceEstimator)


def test_dependence_query_needs_two_distinct_sources() -> None:
    with pytest.raises(ValueError):
        DependenceQuery(("agent-a", "agent-a"), ("yolo11m", "yolo11m"))


def test_policy_protocol_accepts_a_minimal_policy() -> None:
    class AlwaysVerify:
        version = "always-verify-v0"

        def decide(self, task_id, reports, estimator):
            return TaskDecision(
                task_id=task_id,
                action=Action.VERIFY,
                reason_code="always_verify",
                causal_report_ids=tuple(r.report_id for r in reports),
                confirmed_track_ids=(),
                policy_version=self.version,
                estimator_version=estimator.version,
            )

    policy = AlwaysVerify()
    assert isinstance(policy, ResolutionPolicy)
    decision = policy.decide("scene-000", (make_report(),), IndependenceEstimator())
    assert decision.action is Action.VERIFY
    assert decision.causal_report_ids == ("rep-001",)


def make_result(**overrides: object) -> RunResult:
    values: dict[str, object] = {
        "run_id": "run-001",
        "policy_version": "naive-v0",
        "estimator_version": "independence-v0",
        "scene_id": "scene-000",
        "cell_id": sweep_cells()[0].cell_id,
        "action": "close",
        "co_visible_objects": 8,
        "objects_confirmed": 6,
        "objects_missed_at_close": 2,
        "false_confirmations": 1,
        "verification_actions": 0,
        "trace_sha256": "0" * 64,
    }
    values.update(overrides)
    return RunResult(**values)  # type: ignore[arg-type]


def test_result_columns_are_stable_and_round_trip() -> None:
    result = make_result()
    record = result.to_record()
    assert tuple(record) == RESULT_COLUMNS
    assert record["contract_version"] == CONTRACT_VERSION
    assert result_from_dict(record) == result


def test_false_clearance_is_a_close_that_missed_an_object() -> None:
    assert make_result().false_clearance is True
    assert make_result(objects_missed_at_close=0).false_clearance is False
    assert (
        make_result(action="verify", objects_missed_at_close=0).false_clearance is False
    )


def test_query_for_an_unseen_object_needs_no_box() -> None:
    # A shared miss leaves no detection, so object features must be optional.
    query = DependenceQuery(
        ("agent-a", "agent-b"),
        ("yolo11m", "rtdetr-l"),
        covariates=(("illumination", "WetNoon"), ("viewpoint_deg", "15")),
    )
    assert query.label is None
    assert query.box_areas == (None, None)


def test_joint_miss_probability_scales_with_dependence() -> None:
    estimate = DependenceEstimate(1.5, 1.2, 1.8, "test-v0", miss_rates=(0.4, 0.3))
    assert estimate.joint_miss_probability() == pytest.approx(1.5 * 0.4 * 0.3)
