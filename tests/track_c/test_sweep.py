import csv
import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from scenario_gen.corpus import CorpusLayout, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, ScenarioPlan
from scenario_gen.reports import write_report
from scenario_gen.truth_export import write_truth
from sweep.scoring import score_decision
from trace_contracts.association import ObjectTrack
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)
from trace_contracts.policy import Action, TaskDecision
from trace_contracts.results import RESULT_COLUMNS
from trace_contracts.scenario import ScenarioManifestEntry, render_cells
from trace_contracts.truth import TruthObject

T0 = datetime(2026, 11, 18, tzinfo=UTC)
BOX = BoundingBox(390, 300, 410, 400)


def make_corpus(root, *, detected=False):
    layout = CorpusLayout(root)
    entry = ScenarioManifestEntry("scene", render_cells()[0], "Town10HD", 42)
    write_plan(layout, ScenarioPlan(ScenarioGenerationConfig(), (entry,)))
    for source in ("a", "b"):
        truth = TruthObject("real", "scene", source, "car", BOX)
        write_truth(
            layout,
            scene_id="scene",
            frame_id="frame",
            source_id=source,
            objects=[truth],
        )
        for detector in ("yolo11m", "rtdetr-l"):
            report = AgentFrameReport(
                f"{source}-{detector}",
                source,
                "scene",
                "frame",
                T0,
                T0,
                CameraPose(0, 0, 14, 0, -30),
                detector,
                (Detection("d", "car", 0.9, BOX),) if detected else (),
            )
            write_report(CorpusLayout(root / "models" / detector), report)
            target = root / "reports" / detector
            target.mkdir(parents=True, exist_ok=True)
            (
                root / "models" / detector / "reports" / f"scene--frame--{source}.json"
            ).replace(target / f"{source}.json")
    return layout


def run_cli(corpus, output, *extra):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "harness.sweep",
            "--corpus",
            str(corpus),
            "--out",
            str(output),
            "--width-px",
            "800",
            "--height-px",
            "600",
            "--fov-degrees",
            "90",
            "--camera-height-m",
            "14",
            *extra,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_all_pairings_and_policies_retains_reproducible_traces(tmp_path):
    corpus = tmp_path / "corpus"
    make_corpus(corpus)
    first, second = tmp_path / "first", tmp_path / "second"
    for output in (first, second):
        result = run_cli(corpus, output)
        assert result.returncode == 0, result.stderr
    assert (first / "results.csv").read_bytes() == (second / "results.csv").read_bytes()
    with (first / "results.csv").open(newline="") as stream:
        reader = csv.DictReader(stream)
        assert tuple(reader.fieldnames) == RESULT_COLUMNS
        rows = list(reader)
    assert len(rows) == 15
    assert len({r["cell_id"] for r in rows}) == 3
    for row in rows:
        assert row["co_visible_objects"] == "1"
        assert row["objects_confirmed"] == "0"
        verify = row["policy_version"] == "always-verify-v0"
        assert row["verification_actions"] == ("1" if verify else "0")
        assert row["objects_missed_at_close"] == ("0" if verify else "1")
        assert row["false_clearance"] == ("False" if verify else "True")
        trace = (
            first
            / "traces"
            / row["cell_id"]
            / row["scene_id"]
            / (row["policy_version"] + ".json")
        )
        assert hashlib.sha256(trace.read_bytes()).hexdigest() == row["trace_sha256"]
    assert (first / "inputs" / "manifest.json").read_bytes() == (
        corpus / "manifest.json"
    ).read_bytes()
    assert (first / "run.json").is_file()
    again = run_cli(corpus, first)
    assert again.returncode != 0


def test_detected_object_is_confirmed_once(tmp_path):
    make_corpus(tmp_path / "corpus", detected=True)
    result = run_cli(
        tmp_path / "corpus", tmp_path / "out", "--policies", "never-verify"
    )
    assert result.returncode == 0, result.stderr
    with (tmp_path / "out" / "results.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 3
    assert all(
        r["objects_confirmed"] == "1" and r["false_clearance"] == "False" for r in rows
    )


@pytest.mark.parametrize("fault", ["missing_report", "missing_truth", "schema", "late"])
def test_invalid_corpus_fails_without_results(tmp_path, fault):
    layout = make_corpus(tmp_path / "corpus")
    path = layout.root / "reports" / "yolo11m" / "a.json"
    if fault == "missing_report":
        path.unlink()
    elif fault == "missing_truth":
        layout.truth_path("scene", "frame", "a").unlink()
    else:
        payload = json.loads(path.read_text())
        if fault == "schema":
            payload["schema"] = "unknown"
        else:
            payload["report"]["arrived_at"] = (T0 + timedelta(seconds=10)).isoformat()
            other = layout.root / "reports" / "yolo11m" / "b.json"
            raw = json.loads(other.read_text())
            raw["report"]["observed_at"] = (T0 + timedelta(seconds=5)).isoformat()
            raw["report"]["arrived_at"] = (T0 + timedelta(seconds=5)).isoformat()
            other.write_text(json.dumps(raw))
        path.write_text(json.dumps(payload))
    result = run_cli(layout.root, tmp_path / "out")
    assert result.returncode != 0
    assert not (tmp_path / "out" / "results.csv").exists()


def test_scorer_counts_false_tracks_and_single_view_truth():
    reports = [
        AgentFrameReport(
            "a",
            "a",
            "scene",
            "frame",
            T0,
            T0,
            CameraPose(0, 0, 14, 0, -30),
            "yolo11m",
            (Detection("d", "car", 0.9, BOX), Detection("ghost", "truck", 0.9, BOX)),
        )
    ]
    reports.append(replace(reports[0], report_id="b", source_id="b", detections=()))
    tracks = (
        ObjectTrack("real-track", (("a", "d"),)),
        ObjectTrack("ghost-track", (("a", "ghost"),)),
    )
    truth = {
        r.report_id: (TruthObject("real", "scene", r.source_id, "car", BOX),)
        for r in reports
    }
    decision = TaskDecision(
        "scene",
        Action.CLOSE,
        "test",
        ("a", "b"),
        ("real-track", "ghost-track"),
        "test-v0",
        "independence-v0",
    )
    result = score_decision(
        decision, reports, tracks, truth, run_id="run", cell_id="cell"
    )
    assert result.co_visible_objects == 1
    assert result.objects_confirmed == 1
    assert result.false_confirmations == 1
    assert result.objects_missed_at_close == 0
    assert not result.false_clearance
