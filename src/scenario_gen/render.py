"""CARLA adapter that renders M1 scenario entries without exposing truth to agents."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scenario_gen.corpus import CorpusLayout
from scenario_gen.truth_export import write_truth
from spike_dependence.artifacts_io import ground_truth_from_json
from spike_dependence.render_scenes import render_scene
from spike_dependence.scene_matrix import Overlap, SceneSpec, Weather
from trace_contracts.scenario import (
    Occluder,
    ScenarioManifestEntry,
    ViewpointDisparity,
)
from trace_contracts.truth import TruthObject

_OVERLAP_BY_VIEWPOINT: dict[ViewpointDisparity, Overlap] = {
    ViewpointDisparity.NARROW: Overlap.HIGH,
    ViewpointDisparity.MEDIUM: Overlap.MEDIUM,
    ViewpointDisparity.WIDE: Overlap.LOW,
}


@dataclass(frozen=True)
class RenderSettings:
    """CARLA settings retained beside the M1 manifest for reconstruction."""

    width: int = 800
    height: int = 600
    radius_m: float = 22.0
    camera_height_m: float = 14.0
    vehicle_count: int = 12
    min_pixels: int = 50


@dataclass(frozen=True)
class RenderedScene:
    """Paths written for one shared scene and its two camera views."""

    scene_id: str
    frame_id: str
    frame_paths: tuple[Path, Path]
    truth_paths: tuple[Path, Path]


def to_spike_scene_spec(entry: ScenarioManifestEntry) -> SceneSpec:
    """Adapt a frozen M1 physical cell to the tested CARLA spike renderer."""
    return SceneSpec(
        scene_id=entry.scene_id,
        town=entry.town,
        weather=Weather(entry.render.illumination.value),
        overlap=_OVERLAP_BY_VIEWPOINT[entry.render.viewpoint],
        occluder=entry.render.occluder is Occluder.STATIC,
        seed=entry.seed,
    )


def assert_loaded_town(loaded_map: str, planned_town: str) -> None:
    """Reject a CARLA server that does not match the manifest's planned map."""
    loaded_town = loaded_map.rsplit("/", maxsplit=1)[-1]
    if loaded_town != planned_town:
        raise ValueError(
            f"CARLA server loaded {loaded_town!r}, but manifest requires {planned_town!r}"
        )


def render_entry(
    carla_client: Any,
    entry: ScenarioManifestEntry,
    layout: CorpusLayout,
    settings: RenderSettings | None = None,
) -> RenderedScene:
    """Render one M1 entry and copy agent frames away from evaluator truth.

    CARLA is imported only when this function runs, keeping unit tests and
    manifest planning usable on machines without the simulator extra.
    """
    import carla

    loaded_map = carla_client.get_world().get_map().name
    assert_loaded_town(loaded_map, entry.town)
    layout.root.mkdir(parents=True, exist_ok=True)
    if settings is None:
        settings = RenderSettings()

    with tempfile.TemporaryDirectory(prefix=f"{entry.scene_id}-", dir=layout.root) as temp:
        staging_root = Path(temp)
        counts = render_scene(
            carla,
            carla_client,
            to_spike_scene_spec(entry),
            staging_root,
            width=settings.width,
            height=settings.height,
            radius_m=settings.radius_m,
            camera_height_m=settings.camera_height_m,
            vehicle_count=settings.vehicle_count,
            min_pixels=settings.min_pixels,
        )
        if counts is None:
            raise RuntimeError(f"could not find a clear camera pair for {entry.scene_id}")

        scene_dir = staging_root / entry.scene_id
        frame_id = "frame-000"
        frame_paths = tuple(
            _copy_frame(
                scene_dir / f"rgb_{view}.png",
                layout.frame_path(entry.scene_id, frame_id, f"agent-{view}"),
            )
            for view in ("a", "b")
        )
        truth_paths = tuple(
            _export_truth(
                scene_dir / f"gt_{view}.json",
                layout,
                entry.scene_id,
                frame_id,
                f"agent-{view}",
            )
            for view in ("a", "b")
        )
    return RenderedScene(entry.scene_id, frame_id, frame_paths, truth_paths)


def _copy_frame(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def _export_truth(
    source: Path,
    layout: CorpusLayout,
    scene_id: str,
    frame_id: str,
    source_id: str,
) -> Path:
    objects = tuple(
        TruthObject(
            object_id=object_.object_id,
            scene_id=scene_id,
            source_id=source_id,
            label=object_.label,
            box=object_.box,
        )
        for object_ in ground_truth_from_json(source)
    )
    return write_truth(
        layout,
        scene_id=scene_id,
        frame_id=frame_id,
        source_id=source_id,
        objects=objects,
    )
