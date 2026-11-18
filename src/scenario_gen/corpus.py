"""Versioned corpus manifest storage for Track B's generated scenes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scenario_gen.planning import (
    MANIFEST_SCHEMA,
    DetectionJob,
    ScenarioGenerationConfig,
    ScenarioPlan,
    canonical_manifest_bytes,
)
from trace_contracts import CONTRACT_VERSION
from trace_contracts._schema import require_schema
from trace_contracts.scenario import manifest_from_dict

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
DETECTOR_JOBS_SCHEMA = "scenario_gen.detector_jobs.m1-v0"


@dataclass(frozen=True)
class CorpusLayout:
    """Paths that keep agent reports and evaluator truth physically separate."""

    root: Path

    @property
    def manifest_path(self) -> Path:
        return self.root / "manifest.json"

    @property
    def reports_root(self) -> Path:
        return self.root / "reports"

    @property
    def truth_root(self) -> Path:
        return self.root / "evaluator_truth"

    @property
    def frames_root(self) -> Path:
        return self.root / "frames"

    @property
    def detector_jobs_path(self) -> Path:
        return self.root / "detector_jobs.json"

    def report_path(self, scene_id: str, frame_id: str, source_id: str) -> Path:
        return self.reports_root / self._record_name(scene_id, frame_id, source_id)

    def truth_path(self, scene_id: str, frame_id: str, source_id: str) -> Path:
        return self.truth_root / self._record_name(scene_id, frame_id, source_id)

    def frame_path(self, scene_id: str, frame_id: str, source_id: str) -> Path:
        filename = self._record_name(scene_id, frame_id, source_id)
        return self.frames_root / Path(filename).with_suffix(".png")

    @staticmethod
    def _record_name(scene_id: str, frame_id: str, source_id: str) -> str:
        for value in (scene_id, frame_id, source_id):
            if not _IDENTIFIER.fullmatch(value):
                raise ValueError("record identifier contains unsafe characters")
        return f"{scene_id}--{frame_id}--{source_id}.json"


def write_plan(layout: CorpusLayout, plan: ScenarioPlan) -> str:
    """Persist a canonical manifest and return its reproducibility hash."""
    layout.root.mkdir(parents=True, exist_ok=True)
    manifest_bytes = canonical_manifest_bytes(plan)
    layout.manifest_path.write_bytes(manifest_bytes)
    return plan.manifest_sha256


def read_plan(layout: CorpusLayout) -> ScenarioPlan:
    """Load a persisted M1 corpus plan and reject incompatible versions."""
    payload = _read_json(layout.manifest_path)
    require_schema(payload, MANIFEST_SCHEMA, "scenario corpus manifest")
    if payload.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unsupported trace contract version")

    parameters = payload["generation_parameters"]
    if not isinstance(parameters, dict):
        raise TypeError("manifest generation_parameters must be an object")
    config = ScenarioGenerationConfig(
        town=str(parameters["town"]),
        scenes_per_render_cell=int(parameters["scenes_per_render_cell"]),
        seed=int(parameters["seed"]),
    )
    scenes = payload["scenes"]
    if not isinstance(scenes, list):
        raise TypeError("manifest scenes must be a list")

    entries = tuple(manifest_from_dict(entry) for entry in scenes)
    plan = ScenarioPlan(config=config, entries=entries)
    expected = canonical_manifest_bytes(plan)
    actual = layout.manifest_path.read_bytes()
    if actual != expected:
        raise ValueError("manifest is not canonically encoded")
    return plan


def write_detection_jobs(layout: CorpusLayout, jobs: tuple[DetectionJob, ...]) -> Path:
    """Persist detector runs that reuse the physical renders in a corpus."""
    layout.root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": DETECTOR_JOBS_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "jobs": [
            {
                "scene_id": job.scene_id,
                "frame_dir": job.frame_dir,
                "pairing": job.pairing.value,
                "detectors": list(job.detectors),
            }
            for job in jobs
        ],
    }
    layout.detector_jobs_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return layout.detector_jobs_path


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("record must contain a JSON object")
    return payload
