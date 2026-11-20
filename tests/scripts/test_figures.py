"""Spec for the preprint figure scripts.

The numbers in a figure must not drift from the numbers in the paper, so the
calibration data is checked against results.tex itself. The plotting calls run
only where matplotlib is installed.
"""

from __future__ import annotations

import csv
import importlib
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scenario_gen.corpus import CorpusLayout, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, ScenarioPlan
from scenario_gen.reports import write_report
from scenario_gen.truth_export import write_truth
from spike_dependence.artifacts_io import camera_poses_to_json
from spike_dependence.scene_matrix import CameraPose as SpikePose
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
SCRIPTS = ROOT / "scripts"
RESULTS_TEX = ROOT / "paper" / "sections" / "results.tex"
T0 = datetime(2026, 1, 1, tzinfo=UTC)
COLUMNS = [
    "schema", "contract_version", "run_id", "policy_version", "estimator_version",
    "scene_id", "cell_id", "action", "co_visible_objects", "objects_confirmed",
    "objects_missed_at_close", "false_confirmations", "verification_actions",
    "false_clearance", "trace_sha256",
]  # fmt: skip


def load(monkeypatch, name):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    return importlib.import_module(name)


def row(policy, scene, action, missed, *, false_clearance, sha="h"):
    return {
        "schema": "trace.result.m1-v0", "contract_version": "m1-v0", "run_id": "r",
        "policy_version": policy, "estimator_version": "independence-v0",
        "scene_id": scene, "cell_id": "cell", "action": action,
        "co_visible_objects": 3, "objects_confirmed": 0,
        "objects_missed_at_close": missed, "false_confirmations": 0,
        "verification_actions": int(action == "verify"),
        "false_clearance": str(false_clearance), "trace_sha256": sha,
    }  # fmt: skip


def write_results(path: Path, rows: list[dict]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


# --- plot_tradeoffs -------------------------------------------------------


def test_policy_rows_shared_by_both_files_are_counted_once(tmp_path, monkeypatch) -> None:
    tradeoffs = load(monkeypatch, "plot_tradeoffs")
    shared = row("miss-risk-v0", "s0", "verify", 0, false_clearance=False)
    first = write_results(tmp_path / "a.csv", [shared, row("never-verify-v0", "s0", "close", 2, false_clearance=True)])
    second = write_results(tmp_path / "b.csv", [shared])

    rows = tradeoffs.load_policy_rows([first, second])

    assert len(rows) == 2


def test_conflicting_duplicate_rows_are_rejected(tmp_path, monkeypatch) -> None:
    tradeoffs = load(monkeypatch, "plot_tradeoffs")
    first = write_results(tmp_path / "a.csv", [row("p-v0", "s0", "close", 1, false_clearance=True, sha="x")])
    second = write_results(tmp_path / "b.csv", [row("p-v0", "s0", "close", 1, false_clearance=True, sha="y")])

    with pytest.raises(ValueError, match="differs"):
        tradeoffs.load_policy_rows([first, second])


def test_summary_reports_verify_rate_false_clearance_rate_and_missed_objects(
    tmp_path, monkeypatch
) -> None:
    tradeoffs = load(monkeypatch, "plot_tradeoffs")
    path = write_results(
        tmp_path / "a.csv",
        [
            row("p-v0", "s0", "verify", 0, false_clearance=False),
            row("p-v0", "s1", "close", 2, false_clearance=True),
            row("p-v0", "s2", "close", 0, false_clearance=False),
            row("p-v0", "s3", "close", 4, false_clearance=True),
        ],
    )

    (summary,) = tradeoffs.summarize(tradeoffs.load_policy_rows([path]))

    assert summary.policy == "p-v0"
    assert summary.tasks == 4
    assert summary.verify_rate == 0.25
    assert summary.false_clearance_rate == 0.5
    assert summary.missed_objects == 6
    assert summary.missed_per_task == 1.5


def test_frontier_keeps_only_policies_no_other_policy_beats_on_both_axes(
    monkeypatch,
) -> None:
    tradeoffs = load(monkeypatch, "plot_tradeoffs")

    def make(name, verify, risk):
        return tradeoffs.PolicySummary(name, 100, verify, risk, 0)

    summaries = [
        make("never-verify-v0", 0.0, 0.67),
        make("latest-report-v0", 0.0, 0.80),  # same verify rate, more risk: dominated
        make("majority-vote-v0", 0.97, 0.02),
        make("miss-risk-v0", 0.97, 0.02),  # ties with majority-vote: both stay
        make("always-verify-v0", 1.0, 0.0),
    ]

    frontier = tradeoffs.non_dominated(summaries, lambda s: s.false_clearance_rate)

    assert [s.policy for s in frontier] == [
        "never-verify-v0",
        "majority-vote-v0",
        "miss-risk-v0",
        "always-verify-v0",
    ]


def test_tradeoff_figure_is_written_as_pdf_and_png(tmp_path, monkeypatch) -> None:
    pytest.importorskip("matplotlib")
    tradeoffs = load(monkeypatch, "plot_tradeoffs")
    rows = [
        row(f"{name}-v0", f"s{i}", action, missed, false_clearance=missed > 0)
        for name in tradeoffs.POLICY_ORDER
        for i, (action, missed) in enumerate([("verify", 0), ("close", 3)])
    ]
    path = write_results(tmp_path / "a.csv", rows)

    tradeoffs.plot_tradeoffs(tradeoffs.summarize(tradeoffs.load_policy_rows([path])), tmp_path / "fig")

    assert (tmp_path / "fig.pdf").stat().st_size > 0
    assert (tmp_path / "fig.png").stat().st_size > 0


# --- plot_calibration -----------------------------------------------------


def _table_numbers(tex: str, label: str) -> list[list[float]]:
    """Return every numeric cell of one LaTeX table, row by row."""
    block = tex.split(f"\\label{{{label}}}")[1].split("\\end{tabular}")[0]
    rows = []
    for line in block.splitlines():
        if "&" not in line:
            continue
        numbers = [float(n) for n in re.findall(r"(?<![\w.])\d\.\d+", line)]
        if numbers:  # skip the header row
            rows.append(numbers)
    return rows


def test_calibration_data_matches_table_one_of_the_paper(monkeypatch) -> None:
    calibration = load(monkeypatch, "plot_calibration")
    expected = _table_numbers(RESULTS_TEX.read_text(encoding="utf-8"), "tab:calib")

    actual = [
        [r.ratio, r.ratio_lower, r.ratio_upper, r.observed, r.calibrated, r.naive]
        for r in calibration.RANDOM_SPLIT
    ]

    assert actual == expected


def test_calibration_data_matches_table_two_of_the_paper(monkeypatch) -> None:
    calibration = load(monkeypatch, "plot_calibration")
    expected = _table_numbers(RESULTS_TEX.read_text(encoding="utf-8"), "tab:shift")

    actual = [[f.observed, f.calibrated, f.naive] for f in calibration.SHIFT_FOLDS]

    assert actual == expected
    assert len(actual) == 9


def test_naive_underestimate_is_measured_against_the_observed_rate(monkeypatch) -> None:
    calibration = load(monkeypatch, "plot_calibration")

    low, high = calibration.naive_underestimate_range(calibration.RANDOM_SPLIT)

    assert round(low, 2) == 0.45  # 1 - 0.133 / 0.241
    assert round(high, 2) == 0.58  # 1 - 0.044 / 0.106


def test_calibration_figure_is_written_as_pdf_and_png(tmp_path, monkeypatch) -> None:
    pytest.importorskip("matplotlib")
    calibration = load(monkeypatch, "plot_calibration")

    calibration.plot_calibration(tmp_path / "fig")

    assert (tmp_path / "fig.pdf").stat().st_size > 0
    assert (tmp_path / "fig.png").stat().st_size > 0


# --- visualize_double_fault -----------------------------------------------

POSE_A = SpikePose(22.0, 0.0, 14.0, 180.0, -32.5, 0.0, (0.0, 0.0, 0.5))
POSE_B = SpikePose(11.0, 19.05, 14.0, 240.0, -32.5, 60.0, (0.0, 0.0, 0.5))
SMALL = BoundingBox(380, 420, 400, 450)
LARGE = BoundingBox(300, 300, 420, 450)


def make_double_fault_corpus(root: Path) -> CorpusLayout:
    """scene-0000: object seen by both agents. scene-0001: missed by both."""
    layout = CorpusLayout(root)
    entries = tuple(
        ScenarioManifestEntry(f"scene-{i:04d}", render_cells()[i], "Town10HD", i)
        for i in range(2)
    )
    write_plan(layout, ScenarioPlan(ScenarioGenerationConfig(), entries))
    for entry in entries:
        scene = entry.scene_id
        camera_poses_to_json(
            {"a": POSE_A, "b": POSE_B}, layout.camera_pose_path(scene, "frame-000")
        )
        for source in ("agent-a", "agent-b"):
            objects = [TruthObject("big", scene, source, "car", LARGE)]
            if scene == "scene-0001":
                objects.append(TruthObject("small", scene, source, "car", SMALL))
            write_truth(layout, scene_id=scene, frame_id="frame-000", source_id=source, objects=objects)
            seen = scene == "scene-0000"
            report = AgentFrameReport(
                f"{scene}--frame-000--{source}", source, scene, "frame-000", T0, T0,
                CameraPose(0, 0, 14, 0, -30), "yolo11m",
                (Detection("d", "car", 0.9, LARGE),) if seen else (),
            )  # fmt: skip
            write_report(layout, report, layout.detector_report_path("yolo11m", scene, "frame-000", source))
    return layout


def test_double_faults_are_objects_both_agents_missed_largest_first(
    tmp_path, monkeypatch
) -> None:
    double_fault = load(monkeypatch, "visualize_double_fault")
    layout = make_double_fault_corpus(tmp_path)
    tasks = load_tasks(layout.root, (DetectorPairing.HOMOGENEOUS_YOLO,))

    found = double_fault.find_double_faults(tasks, DetectorPairing.HOMOGENEOUS_YOLO)

    assert [(f.scene_id, f.object_id) for f in found] == [
        ("scene-0001", "big"),
        ("scene-0001", "small"),
    ]
    assert found[0].box_a == LARGE and found[1].box_a == SMALL


def test_objects_detected_by_either_agent_are_not_double_faults(
    tmp_path, monkeypatch
) -> None:
    double_fault = load(monkeypatch, "visualize_double_fault")
    layout = make_double_fault_corpus(tmp_path)
    tasks = load_tasks(layout.root, (DetectorPairing.HOMOGENEOUS_YOLO,))

    found = double_fault.find_double_faults(tasks, DetectorPairing.HOMOGENEOUS_YOLO)

    assert all(f.scene_id != "scene-0000" for f in found)


def test_an_object_boxed_with_the_wrong_class_is_not_a_double_fault(
    tmp_path, monkeypatch
) -> None:
    double_fault = load(monkeypatch, "visualize_double_fault")
    layout = make_double_fault_corpus(tmp_path)
    # Agent B boxes the big object but calls it a truck: a classification error, not a miss.
    mislabelled = AgentFrameReport(
        "scene-0001--frame-000--agent-b", "agent-b", "scene-0001", "frame-000", T0, T0,
        CameraPose(0, 0, 14, 0, -30), "yolo11m", (Detection("d", "truck", 0.9, LARGE),),
    )  # fmt: skip
    path = layout.detector_report_path("yolo11m", "scene-0001", "frame-000", "agent-b")
    write_report(layout, mislabelled, path)
    tasks = load_tasks(layout.root, (DetectorPairing.HOMOGENEOUS_YOLO,))

    found = double_fault.find_double_faults(tasks, DetectorPairing.HOMOGENEOUS_YOLO)

    assert [(f.scene_id, f.object_id) for f in found] == [("scene-0001", "small")]


def test_double_fault_figure_is_written_as_pdf_and_png(tmp_path, monkeypatch) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    double_fault = load(monkeypatch, "visualize_double_fault")
    layout = make_double_fault_corpus(tmp_path / "corpus")
    for scene in ("scene-0000", "scene-0001"):
        for source in ("agent-a", "agent-b"):
            path = layout.frame_path(scene, "frame-000", source)
            path.parent.mkdir(parents=True, exist_ok=True)
            matplotlib.pyplot.imsave(path, [[[0.5, 0.5, 0.5]] * 800] * 600)

    double_fault.make_figure(
        layout, DetectorPairing.HOMOGENEOUS_YOLO, tmp_path / "fig", width=800, height=600
    )

    assert (tmp_path / "fig.pdf").stat().st_size > 0
    assert (tmp_path / "fig.png").stat().st_size > 0
