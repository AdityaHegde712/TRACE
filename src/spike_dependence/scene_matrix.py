"""The balanced scene matrix and the two-viewpoint camera geometry.

The spike varies three correlation knobs: viewpoint overlap, presence of an
occluder, and weather (illumination). The matrix walks every cell of that
factorial design in a fixed order before repeating, so the knobs stay balanced
at any scene count. An unbalanced sweep would confound the knobs with each
other and make the inflation ratio uninterpretable.

This module does not import carla. Geometry is plain arithmetic so it can be
checked long before the simulator is launched. The CARLA adapter consumes
these poses; it does not compute them.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum

INSTALLED_TOWNS: tuple[str, ...] = (
    "Town01",
    "Town02",
    "Town03",
    "Town04",
    "Town05",
    "Town10HD",
)


class Overlap(Enum):
    """How much of the scene the two viewpoints share."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Weather(Enum):
    """Illumination conditions, named to match CARLA weather presets."""

    CLEAR_NOON = "ClearNoon"
    CLOUDY_SUNSET = "CloudySunset"
    WET_NOON = "WetNoon"


# Small separation means the two cameras see nearly the same thing, which is
# the condition the project expects to produce correlated failure.
_YAW_SEPARATION_BY_OVERLAP: dict[Overlap, float] = {
    Overlap.HIGH: 15.0,
    Overlap.MEDIUM: 60.0,
    Overlap.LOW: 120.0,
}


@dataclass(frozen=True)
class SceneSpec:
    """One scene's knob settings, fixed before anything is rendered."""

    scene_id: str
    town: str
    weather: Weather
    overlap: Overlap
    occluder: bool
    seed: int


@dataclass(frozen=True)
class CameraPose:
    """One camera placed on a circle around the scene centre."""

    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    orbit_degrees: float
    target: tuple[float, float, float]


def yaw_separation_degrees(overlap: Overlap) -> float:
    """Return the angular gap between the two cameras for this overlap level."""
    return _YAW_SEPARATION_BY_OVERLAP[overlap]


def _factorial_cells() -> list[tuple[Overlap, bool, Weather]]:
    """Return every cell of the overlap x occluder x weather design."""
    return [
        (overlap, occluder, weather)
        for overlap in Overlap
        for occluder in (False, True)
        for weather in Weather
    ]


def build_scene_matrix(scene_count: int, *, seed: int) -> list[SceneSpec]:
    """Return a balanced, deterministic list of scene specifications.

    Cells are walked in order and repeat only after every cell is used once,
    so any prefix of the list is balanced to within one scene per level. The
    seed controls town assignment and each scene's own actor-placement seed,
    not the knob balance.
    """
    if scene_count < 1:
        raise ValueError("the scene matrix needs at least one scene")

    rng = random.Random(seed)
    cells = _factorial_cells()
    towns = list(INSTALLED_TOWNS)
    rng.shuffle(towns)

    scenes: list[SceneSpec] = []
    for index in range(scene_count):
        overlap, occluder, weather = cells[index % len(cells)]
        scenes.append(
            SceneSpec(
                scene_id=f"scene-{index:03d}",
                town=towns[index % len(towns)],
                weather=weather,
                overlap=overlap,
                occluder=occluder,
                seed=rng.randrange(1_000_000),
            )
        )
    return scenes


def viewpoint_pair(
    scene: SceneSpec,
    *,
    radius_m: float,
    height_m: float,
    centre: tuple[float, float, float] = (0.0, 0.0, 0.0),
    base_angle_degrees: float | None = None,
) -> tuple[CameraPose, CameraPose]:
    """Return two camera poses orbiting one shared scene centre.

    Both cameras sit on the same circle at the same height and look inward, so
    they observe one shared scene rather than two separate ones. Only the
    angular gap between them changes with the overlap level.

    `base_angle_degrees` lets the caller rotate the whole pair. The renderer
    uses it to retry when a camera lands inside a building; the seed supplies
    the default so a scene stays reproducible.
    """
    if radius_m <= 0.0:
        raise ValueError("radius_m must be greater than zero")
    if height_m < 0.0:
        raise ValueError("height_m cannot be negative")

    separation = yaw_separation_degrees(scene.overlap)
    if base_angle_degrees is None:
        base_angle = random.Random(scene.seed).uniform(0.0, 360.0)
    else:
        base_angle = base_angle_degrees
    return (
        _pose_at(base_angle, radius_m, height_m, centre),
        _pose_at(base_angle + separation, radius_m, height_m, centre),
    )


def _pose_at(
    orbit_degrees: float,
    radius_m: float,
    height_m: float,
    centre: tuple[float, float, float],
) -> CameraPose:
    """Return the pose of a camera at one point on the orbit, facing inward."""
    radians = math.radians(orbit_degrees)
    return CameraPose(
        x=centre[0] + radius_m * math.cos(radians),
        y=centre[1] + radius_m * math.sin(radians),
        z=centre[2] + height_m,
        yaw=(orbit_degrees + 180.0) % 360.0,
        # Negative pitch looks down; the angle follows from the triangle the
        # camera, the centre and the drop between them form.
        pitch=-math.degrees(math.atan2(height_m, radius_m)),
        orbit_degrees=orbit_degrees,
        target=centre,
    )
