"""Deterministic plans for Track B's CARLA render and detector phases."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

from trace_contracts import CONTRACT_VERSION
from trace_contracts.scenario import (
    DetectorPairing,
    ScenarioManifestEntry,
    manifest_to_dict,
    render_cells,
)

MANIFEST_SCHEMA = "scenario_gen.manifest.m1-v0"
GENERATOR_VERSION = "scenario-gen-v0"


@dataclass(frozen=True)
class ScenarioGenerationConfig:
    """Parameters that reproduce a corpus without changing the M1 matrix."""

    town: str = "Town10HD"
    scenes_per_render_cell: int = 1
    seed: int = 42

    def __post_init__(self) -> None:
        if not self.town:
            raise ValueError("town cannot be empty")
        if self.scenes_per_render_cell < 1:
            raise ValueError("scenes_per_render_cell must be at least one")


@dataclass(frozen=True)
class ScenarioPlan:
    """The complete deterministic physical render plan for one corpus."""

    config: ScenarioGenerationConfig
    entries: tuple[ScenarioManifestEntry, ...]

    def manifest_payload(self) -> dict[str, object]:
        """Return the versioned, canonical on-disk representation."""
        return {
            "schema": MANIFEST_SCHEMA,
            "contract_version": CONTRACT_VERSION,
            "generator_version": GENERATOR_VERSION,
            "generation_parameters": {
                "town": self.config.town,
                "scenes_per_render_cell": self.config.scenes_per_render_cell,
                "seed": self.config.seed,
            },
            "scenes": [manifest_to_dict(entry) for entry in self.entries],
        }

    @property
    def manifest_sha256(self) -> str:
        """Return the hash of the exact canonical manifest bytes."""
        return hashlib.sha256(canonical_manifest_bytes(self)).hexdigest()


@dataclass(frozen=True)
class DetectionJob:
    """One detector-pair run over frames produced by one physical render."""

    scene_id: str
    frame_dir: str
    pairing: DetectorPairing
    detectors: tuple[str, str]


def build_plan(config: ScenarioGenerationConfig) -> ScenarioPlan:
    """Allocate fixed-seed scenes evenly across the frozen render matrix."""
    rng = random.Random(config.seed)
    entries: list[ScenarioManifestEntry] = []

    for cell in render_cells():
        for _ in range(config.scenes_per_render_cell):
            scene_id = f"scene-{len(entries):04d}"
            entries.append(
                ScenarioManifestEntry(
                    scene_id=scene_id,
                    render=cell,
                    town=config.town,
                    seed=rng.randrange(2**31),
                )
            )

    return ScenarioPlan(config=config, entries=tuple(entries))


def build_detection_jobs(plan: ScenarioPlan) -> tuple[DetectionJob, ...]:
    """Cross every physical render with the frozen detector pairings."""
    return tuple(
        DetectionJob(
            scene_id=entry.scene_id,
            frame_dir=entry.scene_id,
            pairing=pairing,
            detectors=pairing.models,
        )
        for entry in plan.entries
        for pairing in DetectorPairing
    )


def canonical_manifest_bytes(plan: ScenarioPlan) -> bytes:
    """Encode a plan in one stable form for persisted hashes and comparisons."""
    return (
        json.dumps(
            plan.manifest_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")
