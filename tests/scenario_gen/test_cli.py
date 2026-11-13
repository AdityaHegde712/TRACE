"""End-to-end contract for the Track B corpus planning command."""

from __future__ import annotations

import json
from pathlib import Path

from scenario_gen.cli import main


def test_cli_writes_a_manifest_and_detector_job_index(tmp_path: Path) -> None:
    output = tmp_path / "corpus"

    exit_code = main(
        [
            "--out",
            str(output),
            "--town",
            "Town10HD",
            "--scenes-per-render-cell",
            "1",
            "--seed",
            "9",
        ]
    )

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    jobs = json.loads((output / "detector_jobs.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert manifest["schema"] == "scenario_gen.manifest.m1-v0"
    assert len(manifest["scenes"]) == 18
    assert jobs["schema"] == "scenario_gen.detector_jobs.m1-v0"
    assert len(jobs["jobs"]) == 54
    assert {job["pairing"] for job in jobs["jobs"]} == {
        "homogeneous_yolo",
        "homogeneous_rtdetr",
        "heterogeneous",
    }
