"""Behavioral contract for Track B corpus storage and truth separation."""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scenario_gen.corpus import CorpusLayout, read_plan, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, build_plan
from scenario_gen.reports import read_report, write_report
from scenario_gen.truth_export import read_truth, write_truth
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)
from trace_contracts.truth import TruthObject


def make_report() -> AgentFrameReport:
    observed_at = datetime(2026, 11, 12, tzinfo=UTC)
    return AgentFrameReport(
        report_id="report-a-000",
        source_id="agent-a",
        scene_id="scene-0000",
        frame_id="frame-000",
        observed_at=observed_at,
        arrived_at=observed_at,
        camera_pose=CameraPose(1.0, 2.0, 3.0, 180.0, -20.0),
        detector="yolo11m",
        detections=(Detection("det-1", "car", 0.9, BoundingBox(1.0, 2.0, 3.0, 4.0)),),
    )


def make_truth() -> TruthObject:
    return TruthObject(
        object_id="carla-actor-19",
        scene_id="scene-0000",
        source_id="agent-a",
        label="car",
        box=BoundingBox(1.0, 2.0, 3.0, 4.0),
    )


def test_plan_round_trips_with_its_parameters_and_stable_hash(tmp_path: Path) -> None:
    plan = build_plan(ScenarioGenerationConfig(scenes_per_render_cell=1, seed=41))
    layout = CorpusLayout(tmp_path / "corpus")

    first_hash = write_plan(layout, plan)
    second_hash = write_plan(layout, plan)

    assert first_hash == second_hash == plan.manifest_sha256
    assert read_plan(layout) == plan


def test_reports_and_truth_are_written_to_separate_evaluator_boundary(tmp_path: Path) -> None:
    layout = CorpusLayout(tmp_path / "corpus")
    report = make_report()
    truth = make_truth()

    report_path = write_report(layout, report)
    truth_path = write_truth(
        layout,
        scene_id=truth.scene_id,
        frame_id=report.frame_id,
        source_id=truth.source_id,
        objects=(truth,),
    )

    assert report_path.is_relative_to(layout.reports_root)
    assert truth_path.is_relative_to(layout.truth_root)
    assert truth_path not in report_path.parents
    assert read_report(report_path) == report
    assert read_truth(truth_path) == (truth,)


def test_truth_export_can_record_an_empty_visible_set(tmp_path: Path) -> None:
    layout = CorpusLayout(tmp_path / "corpus")

    path = write_truth(
        layout,
        scene_id="scene-0000",
        frame_id="frame-000",
        source_id="agent-b",
        objects=(),
    )

    assert read_truth(path) == ()


def test_report_writer_never_imports_evaluator_truth() -> None:
    source_path = Path(__file__).parents[2] / "src" / "scenario_gen" / "reports.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }

    assert not any(name.endswith("truth") for name in imported)


def test_layout_rejects_path_traversal_in_record_identifiers(tmp_path: Path) -> None:
    layout = CorpusLayout(tmp_path / "corpus")

    with pytest.raises(ValueError, match="identifier"):
        layout.report_path("../scene", "frame-000", "agent-a")
