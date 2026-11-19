"""Regression cases requested during Track C PR review."""

from dataclasses import replace
from pathlib import Path

import pytest
from test_baselines import ASSOCIATION, ESTIMATOR, report
from test_sweep import BOX, make_corpus, run_cli

from baselines import FirstReportPolicy, LatestReportPolicy
from sweep.scoring import score_decision
from trace_contracts.observations import BoundingBox
from trace_contracts.truth import TruthObject


@pytest.mark.parametrize("policy_type", [FirstReportPolicy, LatestReportPolicy])
@pytest.mark.parametrize("selected_correct", [False, True])
def test_only_causal_detections_can_match_truth(
    policy_type: type[FirstReportPolicy] | type[LatestReportPolicy],
    selected_correct: bool,
) -> None:
    selected = report("a", arrival=0 if policy_type is FirstReportPolicy else 2)
    unselected = report("b", arrival=1)
    wrong_box = BoundingBox(412, 300, 432, 400)
    selected = replace(
        selected,
        detections=(
            replace(
                selected.detections[0],
                box=BOX if selected_correct else wrong_box,
            ),
        ),
    )
    unselected = replace(
        unselected,
        detections=(
            replace(
                unselected.detections[0],
                box=wrong_box if selected_correct else BOX,
            ),
        ),
    )
    reports = [selected, unselected]
    tracks = ASSOCIATION.associate(reports)
    assert len(tracks) == 1
    assert len(tracks[0].members) == 2
    decision = policy_type(ASSOCIATION).decide("scene", reports, ESTIMATOR)
    assert decision.causal_report_ids == (selected.report_id,)
    truth = {
        r.report_id: (TruthObject("real", "scene", r.source_id, "car", BOX),)
        for r in reports
    }
    result = score_decision(
        decision,
        reports,
        tracks,
        truth,
        run_id="regression",
        cell_id="cell",
    )
    assert result.co_visible_objects == 1
    assert result.objects_confirmed == int(selected_correct)
    assert result.objects_missed_at_close == int(not selected_correct)
    assert result.false_confirmations == int(not selected_correct)
    assert result.false_clearance is (not selected_correct)


@pytest.mark.parametrize("slack", ["0", "-1"])
def test_cli_rejects_nonpositive_slack_before_evaluation(
    tmp_path: Path, slack: str
) -> None:
    layout = make_corpus(tmp_path / "corpus")
    output = tmp_path / "out"
    result = run_cli(layout.root, output, "--slack-seconds", slack)
    assert result.returncode == 2
    assert "slack must be strictly positive" in result.stderr
    assert "late reports" not in result.stderr
    assert not output.exists()


def test_positive_slack_accepts_simultaneous_reports(tmp_path: Path) -> None:
    layout = make_corpus(tmp_path / "corpus")
    output = tmp_path / "out"
    result = run_cli(layout.root, output, "--slack-seconds", "0.001")
    assert result.returncode == 0, result.stderr
    assert (output / "results.csv").is_file()
