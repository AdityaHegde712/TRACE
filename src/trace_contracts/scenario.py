"""The four correlation channels and the scenario matrix (Track B builds to this).

Three channels are physical and fixed at render time. Detector pairing is
applied afterwards over the SAME rendered frames, so homogeneous and
heterogeneous pairs are compared paired, as in the spike (SD-023).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from trace_contracts import CONTRACT_VERSION
from trace_contracts._schema import require_schema

MANIFEST_SCHEMA: str = "trace.manifest.m1-v0"


class ViewpointDisparity(Enum):
    """Angular gap between the two agents' cameras around one scene centre."""

    NARROW = "narrow"
    MEDIUM = "medium"
    WIDE = "wide"

    @property
    def yaw_separation_degrees(self) -> float:
        return {"narrow": 15.0, "medium": 60.0, "wide": 120.0}[self.value]


class Occluder(Enum):
    """Whether a static occluder is placed between the cameras and the scene."""

    NONE = "none"
    STATIC = "static"


class Illumination(Enum):
    """CARLA weather presets verified present in CARLA 0.9.16 during the spike."""

    CLEAR_NOON = "ClearNoon"
    CLOUDY_SUNSET = "CloudySunset"
    WET_NOON = "WetNoon"


class DetectorPairing(Enum):
    """Which detector each of the two agents runs over its frames."""

    HOMOGENEOUS_YOLO = "homogeneous_yolo"
    HOMOGENEOUS_RTDETR = "homogeneous_rtdetr"
    HETEROGENEOUS = "heterogeneous"

    @property
    def models(self) -> tuple[str, str]:
        return {
            "homogeneous_yolo": ("yolo11m", "yolo11m"),
            "homogeneous_rtdetr": ("rtdetr-l", "rtdetr-l"),
            "heterogeneous": ("yolo11m", "rtdetr-l"),
        }[self.value]


@dataclass(frozen=True)
class RenderCell:
    """One combination of the three physical channels."""

    viewpoint: ViewpointDisparity
    occluder: Occluder
    illumination: Illumination

    @property
    def cell_id(self) -> str:
        return f"{self.viewpoint.value}-{self.occluder.value}-{self.illumination.value}"


@dataclass(frozen=True)
class SweepCell:
    """A render cell plus the detector pairing applied to its frames."""

    render: RenderCell
    pairing: DetectorPairing

    @property
    def cell_id(self) -> str:
        return f"{self.render.cell_id}-{self.pairing.value}"


@dataclass(frozen=True)
class ScenarioManifestEntry:
    """One rendered scene: its cell, town, and seed, so it regenerates exactly."""

    scene_id: str
    render: RenderCell
    town: str
    seed: int


def render_cells() -> list[RenderCell]:
    """Return the full physical factorial in a fixed order."""
    return [
        RenderCell(viewpoint, occluder, illumination)
        for viewpoint in ViewpointDisparity
        for occluder in Occluder
        for illumination in Illumination
    ]


def sweep_cells() -> list[SweepCell]:
    """Return every render cell crossed with every detector pairing."""
    return [
        SweepCell(render, pairing)
        for render in render_cells()
        for pairing in DetectorPairing
    ]


def manifest_to_dict(entry: ScenarioManifestEntry) -> dict[str, Any]:
    return {
        "schema": MANIFEST_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "scene_id": entry.scene_id,
        "viewpoint": entry.render.viewpoint.value,
        "occluder": entry.render.occluder.value,
        "illumination": entry.render.illumination.value,
        "town": entry.town,
        "seed": entry.seed,
    }


def manifest_from_dict(payload: dict[str, Any]) -> ScenarioManifestEntry:
    require_schema(payload, MANIFEST_SCHEMA, "manifest")
    return ScenarioManifestEntry(
        scene_id=payload["scene_id"],
        render=RenderCell(
            ViewpointDisparity(payload["viewpoint"]),
            Occluder(payload["occluder"]),
            Illumination(payload["illumination"]),
        ),
        town=payload["town"],
        seed=payload["seed"],
    )
