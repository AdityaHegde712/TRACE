"""End-to-end contract for the inspectable CLI artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURE_PATH = Path(__file__).parents[1] / "fixtures" / "oracle" / "supported.json"


def test_cli_writes_trace_and_passing_oracle_report(tmp_path: Path) -> None:
    """A reviewer can run one scenario without a simulator or UI."""
    command = [
        sys.executable,
        "-m",
        "evidence_resolution",
        "--scenario",
        str(FIXTURE_PATH),
        "--output-dir",
        str(tmp_path),
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode == 0, completed.stderr
    trace_path = tmp_path / "supported.trace.jsonl"
    report_path = tmp_path / "supported.oracle.json"
    assert trace_path.is_file()
    assert report_path.is_file()
    assert len(trace_path.read_text(encoding="utf-8").splitlines()) == 2
    assert json.loads(report_path.read_text(encoding="utf-8")) == {
        "scenario_id": "supported",
        "oracle_passed": True,
        "trace_event_count": 2,
    }
