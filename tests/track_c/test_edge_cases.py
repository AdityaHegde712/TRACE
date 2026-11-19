import ast
import csv
import json
from dataclasses import replace
from pathlib import Path

import pytest
from test_baselines import ASSOCIATION, ESTIMATOR, report
from test_sweep import BOX, make_corpus, run_cli

from baselines import FirstReportPolicy, LatestReportPolicy, MajorityVotePolicy
from sweep.scoring import score_decision
from trace_contracts.association import ObjectTrack
from trace_contracts.policy import Action, TaskDecision
from trace_contracts.truth import TruthObject


def test_baseline_modules_have_no_truth_dependency():
    root = Path(__file__).parents[2] / "src" / "baselines"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text())
        imports = [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        assert not any("truth" in name or name.startswith("sweep") for name in imports)


@pytest.mark.parametrize(
    "cls", [FirstReportPolicy, LatestReportPolicy, MajorityVotePolicy]
)
def test_equal_arrival_has_deterministic_tiebreak(cls):
    reports = [report(), report("b", False)]
    policy = cls(ASSOCIATION)
    assert policy.decide("scene", reports, ESTIMATOR) == policy.decide(
        "scene", reports[::-1], ESTIMATOR
    )


def test_single_view_detection_is_real_but_not_co_visible():
    reports = [report(), report("b", False)]
    truth = {"rep-a": (TruthObject("real", "scene", "a", "car", BOX),), "rep-b": ()}
    decision = TaskDecision(
        "scene", Action.CLOSE, "test", ("rep-a",), ("one",), "v", "e"
    )
    result = score_decision(
        decision,
        reports,
        [ObjectTrack("one", (("rep-a", "d"),))],
        truth,
        run_id="r",
        cell_id="c",
    )
    assert result.co_visible_objects == result.objects_confirmed == 0
    assert result.false_confirmations == result.objects_missed_at_close == 0


def test_duplicate_tracks_cannot_double_count_real_objects():
    a = report()
    a = replace(
        a, detections=a.detections + (replace(a.detections[0], detection_id="d2"),)
    )
    reports = [a, report("b", False)]
    truth = {
        r.report_id: (TruthObject("real", "scene", r.source_id, "car", BOX),)
        for r in reports
    }
    tracks = [
        ObjectTrack("one", (("rep-a", "d"),)),
        ObjectTrack("two", (("rep-a", "d2"),)),
    ]
    decision = TaskDecision(
        "scene", Action.CLOSE, "test", ("rep-a",), ("one", "two"), "v", "e"
    )
    result = score_decision(decision, reports, tracks, truth, run_id="r", cell_id="c")
    assert result.objects_confirmed == 1
    assert result.false_confirmations == 1


@pytest.mark.parametrize(
    "fault", ["duplicate", "unknown_scene", "truth_context", "version"]
)
def test_corpus_validation_rejects_ambiguous_records(tmp_path, fault):
    layout = make_corpus(tmp_path / "corpus")
    path = layout.root / "reports" / "yolo11m" / "a.json"
    payload = json.loads(path.read_text())
    if fault == "duplicate":
        (path.parent / "duplicate.json").write_text(json.dumps(payload))
    elif fault == "unknown_scene":
        payload["report"]["scene_id"] = "unknown"
        path.write_text(json.dumps(payload))
    elif fault == "version":
        payload["report"]["contract_version"] = "wrong"
        path.write_text(json.dumps(payload))
    else:
        path = layout.truth_path("scene", "frame", "a")
        payload = json.loads(path.read_text())
        payload["source_id"] = "wrong"
        path.write_text(json.dumps(payload))
    result = run_cli(layout.root, tmp_path / "out")
    assert result.returncode != 0
    assert not (tmp_path / "out" / "results.csv").exists()


def test_truth_changes_scores_not_decisions_or_hashes(tmp_path):
    layout = make_corpus(tmp_path / "corpus")
    assert run_cli(layout.root, tmp_path / "before").returncode == 0
    for path in layout.truth_root.glob("*.json"):
        payload = json.loads(path.read_text())
        payload["objects"] = []
        path.write_text(json.dumps(payload))
    assert run_cli(layout.root, tmp_path / "after").returncode == 0
    with (tmp_path / "before" / "results.csv").open() as stream:
        before = list(csv.DictReader(stream))
    with (tmp_path / "after" / "results.csv").open() as stream:
        after = list(csv.DictReader(stream))
    assert [r["trace_sha256"] for r in before] == [r["trace_sha256"] for r in after]
    assert before[0]["co_visible_objects"] == "1"
    assert after[0]["co_visible_objects"] == "0"
