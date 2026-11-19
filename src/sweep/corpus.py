"""Validate complete Track B corpus inputs before evaluation."""

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from scenario_gen.corpus import CorpusLayout, read_plan
from scenario_gen.reports import read_report
from scenario_gen.truth_export import read_truth
from trace_contracts import CONTRACT_VERSION
from trace_contracts.observations import AgentFrameReport
from trace_contracts.scenario import DetectorPairing, ScenarioManifestEntry
from trace_contracts.truth import TruthObject


@dataclass(frozen=True)
class CorpusTask:
    entry: ScenarioManifestEntry
    pairing: DetectorPairing
    reports: tuple[AgentFrameReport, ...]
    truth: dict[str, tuple[TruthObject, ...]]


def load_tasks(
    root: Path, pairings: tuple[DetectorPairing, ...]
) -> tuple[CorpusTask, ...]:
    layout = CorpusLayout(root)
    plan = read_plan(layout)
    entries = {entry.scene_id: entry for entry in plan.entries}
    if not entries or len(entries) != len(plan.entries):
        raise ValueError("manifest must contain unique scenes")
    grouped: dict[str, dict[tuple[str, str], AgentFrameReport]] = defaultdict(dict)
    for path in sorted(layout.reports_root.rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("report", {}).get("contract_version") != CONTRACT_VERSION:
            raise ValueError(f"unsupported report contract version: {path}")
        report = read_report(path)
        if report.scene_id not in entries:
            raise ValueError(f"report refers to unknown scene: {path}")
        if report.observed_at.tzinfo is None or report.arrived_at.tzinfo is None:
            raise ValueError(f"report timestamps must include timezone: {path}")
        if report.detector not in {
            model for pair in DetectorPairing for model in pair.models
        }:
            raise ValueError(f"unknown detector: {report.detector}")
        key = report.source_id, report.detector
        if key in grouped[report.scene_id]:
            raise ValueError(
                f"duplicate or multi-frame report for {report.scene_id}: {key}"
            )
        if len({d.detection_id for d in report.detections}) != len(report.detections):
            raise ValueError(f"duplicate detection ids: {path}")
        grouped[report.scene_id][key] = report
    tasks = []
    for scene_id, entry in sorted(entries.items()):
        records = grouped[scene_id]
        sources = sorted({source for source, _ in records})
        if len(sources) != 2:
            raise ValueError(f"scene {scene_id} needs reports from exactly two sources")
        for pairing in pairings:
            try:
                reports = tuple(
                    records[(source, model)]
                    for source, model in zip(sources, pairing.models)
                )
            except KeyError as error:
                raise ValueError(
                    f"missing report for {scene_id}/{pairing.value}: {error}"
                ) from error
            if len({r.report_id for r in reports}) != 2:
                raise ValueError(f"duplicate report ids in {scene_id}/{pairing.value}")
            if len({r.frame_id for r in reports}) != 1:
                raise ValueError(f"scene {scene_id} has mismatched frame ids")
            truth = {}
            for report in reports:
                path = layout.truth_path(scene_id, report.frame_id, report.source_id)
                payload = json.loads(path.read_text(encoding="utf-8"))
                if (
                    payload.get("scene_id"),
                    payload.get("frame_id"),
                    payload.get("source_id"),
                ) != (scene_id, report.frame_id, report.source_id):
                    raise ValueError(f"truth context mismatch: {path}")
                objects = read_truth(path)
                if any(
                    obj.scene_id != scene_id or obj.source_id != report.source_id
                    for obj in objects
                ):
                    raise ValueError(f"truth object context mismatch: {path}")
                if len({obj.object_id for obj in objects}) != len(objects):
                    raise ValueError(f"duplicate truth object: {path}")
                truth[report.report_id] = objects
            tasks.append(CorpusTask(entry, pairing, reports, truth))
    return tuple(tasks)
