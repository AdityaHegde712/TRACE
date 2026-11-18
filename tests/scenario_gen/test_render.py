"""Behavioral contract for the M1-to-CARLA render adapter."""

from __future__ import annotations

import pytest

from scenario_gen.planning import ScenarioGenerationConfig, build_plan
from scenario_gen.render import assert_loaded_town, to_spike_scene_spec
from spike_dependence.scene_matrix import Overlap, Weather
from trace_contracts.scenario import (
    Illumination,
    Occluder,
    RenderCell,
    ScenarioManifestEntry,
    ViewpointDisparity,
)


@pytest.mark.parametrize(
    ("viewpoint", "expected_overlap"),
    [
        (ViewpointDisparity.NARROW, Overlap.HIGH),
        (ViewpointDisparity.MEDIUM, Overlap.MEDIUM),
        (ViewpointDisparity.WIDE, Overlap.LOW),
    ],
)
def test_adapter_maps_frozen_viewpoint_disparity_to_existing_geometry(
    viewpoint: ViewpointDisparity, expected_overlap: Overlap
) -> None:
    entry = ScenarioManifestEntry(
        scene_id="scene-0000",
        render=RenderCell(viewpoint, Occluder.STATIC, Illumination.WET_NOON),
        town="Town10HD",
        seed=91,
    )

    spike_spec = to_spike_scene_spec(entry)

    assert spike_spec.overlap is expected_overlap
    assert spike_spec.occluder is True
    assert spike_spec.weather is Weather.WET_NOON
    assert spike_spec.seed == entry.seed


def test_adapter_rejects_a_carla_server_running_the_wrong_town() -> None:
    with pytest.raises(ValueError, match="Town10HD"):
        assert_loaded_town("/Game/Carla/Maps/Town01", "Town10HD")


def test_adapter_accepts_a_carla_map_path_ending_in_the_planned_town() -> None:
    assert_loaded_town("/Game/Carla/Maps/Town10HD", "Town10HD")


def test_adapter_preserves_the_manifest_town() -> None:
    entry = build_plan(ScenarioGenerationConfig(town="Town10HD")).entries[0]

    assert to_spike_scene_spec(entry).town == entry.town
