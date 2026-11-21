"""Calibrated tolerance sweep: fit on practice scenes, then sweep the tolerance."""

import csv
import json
import subprocess
import sys
from datetime import UTC, datetime

import pytest

from evidence_resolution.calibration import split_scenes
from scenario_gen.corpus import CorpusLayout, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, ScenarioPlan
from scenario_gen.reports import write_report
from scenario_gen.truth_export import write_truth
from sweep.calibrated import fit_practice_estimator, tolerance_policy_version
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

T0 = datetime(2026, 11, 18, tzinfo=UTC)
BOX = BoundingBox(390, 300, 410, 400)
SCENES = [f"scene-{i}" for i in range(6)]
DETECTED = {"scene-0", "scene-1", "scene-2"}  # both agents find the object here


def make_corpus(root):
    """Six scenes, one object each. Both agents either find it or both miss it."""
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
                found = scene in DETECTED
                report = AgentFrameReport(
                    f"{scene}-{source}-{detector}",
                    source,
                    scene,
                    "frame",
                    T0,
                    T0,
                    CameraPose(0, 0, 14, 0, -30),
                    detector,
                    (Detection("d", "car", 0.9, BOX),) if found else (),
                )
                write_report(CorpusLayout(root / "models" / detector), report)
                target = root / "reports" / detector
                target.mkdir(parents=True, exist_ok=True)
                (
                    root
                    / "models"
                    / detector
                    / "reports"
                    / f"{scene}--frame--{source}.json"
                ).replace(target / f"{scene}-{source}.json")
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


def test_policy_version_names_the_tolerance():
    assert tolerance_policy_version(0.05) == "miss-risk-calibrated-v0-tau0.05"
    assert tolerance_policy_version(0.5) == "miss-risk-calibrated-v0-tau0.5"


def test_estimator_is_fitted_on_practice_scenes_only(tmp_path):
    make_corpus(tmp_path / "corpus")
    tasks = load_tasks(tmp_path / "corpus", tuple(DetectorPairing))
    practice, _ = split_scenes(SCENES, seed=0)

    estimator = fit_practice_estimator(tasks, seed=0)

    by_pair = {entry.detectors: entry for entry in estimator.entries}
    assert by_pair[("yolo11m", "yolo11m")].objects == len(practice)


def test_the_practice_split_follows_the_seed(tmp_path):
    make_corpus(tmp_path / "corpus")
    tasks = load_tasks(tmp_path / "corpus", tuple(DetectorPairing))
    same_a = fit_practice_estimator(tasks, seed=1)
    same_b = fit_practice_estimator(tasks, seed=1)
    assert same_a.version == same_b.version


def test_calibrated_sweep_writes_one_policy_row_per_tolerance(tmp_path):
    make_corpus(tmp_path / "corpus")
    out = tmp_path / "out"
    result = run_cli(
        tmp_path / "corpus",
        out,
        "--policies",
        "miss-risk",
        "--estimator",
        "calibrated",
        "--miss-risk-tolerances",
        "0.05",
        "0.9",
    )
    assert result.returncode == 0, result.stderr
    with (out / "results.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    versions = {row["policy_version"] for row in rows}
    assert versions == {
        "miss-risk-calibrated-v0-tau0.05",
        "miss-risk-calibrated-v0-tau0.9",
    }
    assert len(rows) == len(SCENES) * 3 * 2  # scenes x pairings x tolerances
    assert all(row["estimator_version"].startswith("calibrated-") for row in rows)
    meta = json.loads((out / "run.json").read_text())
    assert meta["estimator"] == "calibrated"
    assert meta["miss_risk_tolerances"] == [0.05, 0.9]
    assert meta["calibration_seed"] == 0


def test_a_looser_tolerance_never_verifies_more_often(tmp_path):
    make_corpus(tmp_path / "corpus")
    out = tmp_path / "out"
    result = run_cli(
        tmp_path / "corpus",
        out,
        "--policies",
        "miss-risk",
        "--estimator",
        "calibrated",
        "--miss-risk-tolerances",
        "0.01",
        "1.0",
    )
    assert result.returncode == 0, result.stderr
    with (out / "results.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))

    def verifies(version):
        return sum(
            r["action"] == "verify" for r in rows if r["policy_version"] == version
        )

    assert verifies("miss-risk-calibrated-v0-tau1") <= verifies(
        "miss-risk-calibrated-v0-tau0.01"
    )


@pytest.mark.parametrize(
    "extra",
    [
        ("--miss-risk-tolerances", "0.1"),  # tolerance sweep needs the calibrated estimator
        ("--estimator", "calibrated", "--miss-risk-tolerances", "1.5"),
        ("--estimator", "calibrated", "--miss-risk-tolerances", "0.1", "0.1"),
    ],
)
def test_invalid_tolerance_sweeps_are_rejected(tmp_path, extra):
    make_corpus(tmp_path / "corpus")
    out = tmp_path / "out"
    result = run_cli(tmp_path / "corpus", out, "--policies", "miss-risk", *extra)
    assert result.returncode == 2
    assert not out.exists()
