"""Scene inspector: one scene's conditions, truth, detections, tracks and decisions."""

from __future__ import annotations

import importlib
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scenario_gen.corpus import CorpusLayout, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, ScenarioPlan
from scenario_gen.reports import write_report
from scenario_gen.truth_export import write_truth
from sweep.corpus import load_tasks
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)
from trace_contracts.scenario import (
    DetectorPairing,
    ScenarioManifestEntry,
    render_cells,
)
from trace_contracts.truth import TruthObject

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "inspect_scene.py"
T0 = datetime(2026, 11, 18, tzinfo=UTC)
BOX = BoundingBox(390, 300, 410, 400)
SCENES = [f"scene-{i:04d}" for i in range(6)]
FOUND = {"scene-0000", "scene-0001", "scene-0002"}  # both agents find the object


def make_corpus(root: Path) -> None:
    layout = CorpusLayout(root)
    entries = tuple(
        ScenarioManifestEntry(scene, render_cells()[0], "Town10HD", 42 + i)
        for i, scene in enumerate(SCENES)
    )
    write_plan(layout, ScenarioPlan(ScenarioGenerationConfig(), entries))
    for scene in SCENES:
        for source in ("a", "b"):
            write_truth(
                layout,
                scene_id=scene,
                frame_id="frame",
                source_id=source,
                objects=[TruthObject("real", scene, source, "car", BOX)],
            )
            for detector in ("yolo11m", "rtdetr-l"):
                report = AgentFrameReport(
                    f"{scene}-{source}-{detector}",
                    source,
                    scene,
                    "frame",
                    T0,
                    T0,
                    CameraPose(0, 0, 14, 0, -30),
                    detector,
                    (Detection("d1", "car", 0.9, BOX),) if scene in FOUND else (),
                )
                write_report(CorpusLayout(root / "models" / detector), report)
                target = root / "reports" / detector
                target.mkdir(parents=True, exist_ok=True)
                (
                    root / "models" / detector / "reports"
                    / f"{scene}--frame--{source}.json"
                ).replace(target / f"{scene}-{source}.json")


@pytest.fixture
def inspector(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    return importlib.import_module("inspect_scene")


@pytest.fixture
def corpus(tmp_path) -> Path:
    make_corpus(tmp_path / "corpus")
    return tmp_path / "corpus"


def report_for(inspector, corpus: Path, scene: str, pairing: str = "homogeneous_yolo"):
    tasks = load_tasks(corpus, tuple(DetectorPairing))
    return inspector.render_text(
        inspector.inspect_scene(tasks, scene, pairings=(DetectorPairing(pairing),))
    )


def test_report_lists_the_scene_conditions(inspector, corpus) -> None:
    text = report_for(inspector, corpus, "scene-0000")

    cell = render_cells()[0]
    assert "scene-0000" in text
    assert cell.viewpoint.value in text
    assert cell.occluder.value in text
    assert cell.illumination.value in text
    assert "Town10HD" in text


def test_an_object_both_agents_missed_is_flagged_as_a_double_fault(
    inspector, corpus
) -> None:
    text = report_for(inspector, corpus, "scene-0005")

    assert "DOUBLE FAULT" in text
    assert "real" in text


def test_an_object_both_agents_found_is_not_flagged(inspector, corpus) -> None:
    text = report_for(inspector, corpus, "scene-0000")

    assert "DOUBLE FAULT" not in text
    assert "no double fault" in text.lower()


def test_a_confirmed_track_names_both_agents(inspector, corpus) -> None:
    text = report_for(inspector, corpus, "scene-0000")

    assert "a:d1" in text
    assert "b:d1" in text


def test_every_policy_decision_is_listed(inspector, corpus) -> None:
    text = report_for(inspector, corpus, "scene-0005")

    for name in (
        "latest-report",
        "first-report-wins",
        "majority-vote",
        "never-verify",
        "always-verify",
        "miss-risk",
    ):
        assert name in text


def test_latest_report_closes_a_missed_object_and_always_verify_does_not(
    inspector, corpus
) -> None:
    tasks = load_tasks(corpus, tuple(DetectorPairing))
    (inspection,) = inspector.inspect_scene(
        tasks, "scene-0005", pairings=(DetectorPairing.HOMOGENEOUS_YOLO,)
    )
    by_policy = {d.policy: d for d in inspection.decisions}

    assert by_policy["latest-report"].action == "close"
    assert by_policy["latest-report"].false_clearance
    assert by_policy["always-verify"].action == "verify"
    assert not by_policy["always-verify"].false_clearance


def test_all_three_pairings_are_shown_by_default(inspector, corpus) -> None:
    tasks = load_tasks(corpus, tuple(DetectorPairing))

    inspections = inspector.inspect_scene(tasks, "scene-0005")

    assert [i.pairing for i in inspections] == list(DetectorPairing)


def test_an_unknown_scene_is_rejected(inspector, corpus) -> None:
    tasks = load_tasks(corpus, tuple(DetectorPairing))

    with pytest.raises(ValueError, match="scene-9999"):
        inspector.inspect_scene(tasks, "scene-9999")


def test_command_line_prints_the_report(corpus) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--corpus", str(corpus), "--scene", "scene-0005"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "scene-0005" in result.stdout
    assert "DOUBLE FAULT" in result.stdout


def test_command_line_rejects_an_unknown_scene(corpus) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--corpus", str(corpus), "--scene", "scene-9999"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "scene-9999" in result.stderr
