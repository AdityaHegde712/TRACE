"""Behavioral contract for detector output translated into M1 reports."""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path

from scenario_gen.detection_adapter import detections_to_report
from spike_dependence.scoring import BoundingBox as SpikeBoundingBox
from spike_dependence.scoring import Detection as SpikeDetection
from trace_contracts.observations import CameraPose


def test_adapter_creates_an_agent_visible_report_with_stable_detection_ids() -> None:
    report = detections_to_report(
        scene_id="scene-0000",
        frame_id="frame-000",
        source_id="agent-a",
        detector="yolo11m",
        observed_at=datetime(2026, 11, 12, tzinfo=UTC),
        arrived_at=datetime(2026, 11, 12, tzinfo=UTC),
        camera_pose=CameraPose(1.0, 2.0, 3.0, 180.0, -20.0),
        detections=(SpikeDetection("car", 0.9, SpikeBoundingBox(1.0, 2.0, 4.0, 5.0)),),
    )

    assert report.report_id == "scene-0000--frame-000--agent-a"
    assert report.detections[0].detection_id == "scene-0000--frame-000--agent-a--0000"
    assert report.detections[0].label == "car"
    assert report.detections[0].box.x2 == 4.0


def test_adapter_preserves_an_empty_detection_set_as_an_observation() -> None:
    observed_at = datetime(2026, 11, 12, tzinfo=UTC)
    report = detections_to_report(
        scene_id="scene-0000",
        frame_id="frame-000",
        source_id="agent-b",
        detector="rtdetr-l",
        observed_at=observed_at,
        arrived_at=observed_at,
        camera_pose=CameraPose(1.0, 2.0, 3.0, 180.0, -20.0),
        detections=(),
    )

    assert report.detections == ()


def test_detector_adapter_never_imports_evaluator_truth() -> None:
    source_path = Path(__file__).parents[2] / "src" / "scenario_gen" / "detection_adapter.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }

    assert not any(name.endswith("truth") for name in imported)
