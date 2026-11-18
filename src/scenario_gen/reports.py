"""Agent-visible report storage with no evaluator-truth dependency."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scenario_gen.corpus import CorpusLayout
from trace_contracts._schema import require_schema
from trace_contracts.observations import (
    AgentFrameReport,
    report_from_dict,
    report_to_dict,
)

REPORT_ARTIFACT_SCHEMA = "scenario_gen.report.m1-v0"


def write_report(layout: CorpusLayout, report: AgentFrameReport) -> Path:
    """Write one agent's observation-only report under the reports boundary."""
    path = layout.report_path(report.scene_id, report.frame_id, report.source_id)
    _write_json({"schema": REPORT_ARTIFACT_SCHEMA, "report": report_to_dict(report)}, path)
    return path


def read_report(path: Path) -> AgentFrameReport:
    """Read one agent report and reject a non-Track-B storage schema."""
    payload = _read_json(path)
    require_schema(payload, REPORT_ARTIFACT_SCHEMA, "scenario report artifact")
    report = payload["report"]
    if not isinstance(report, dict):
        raise TypeError("scenario report artifact must contain a report object")
    return report_from_dict(report)


def _write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("record must contain a JSON object")
    return payload
