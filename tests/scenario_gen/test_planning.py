"""Behavioral contract for Track B's deterministic scenario planning."""

from __future__ import annotations

import pytest

from scenario_gen.planning import (
    ScenarioGenerationConfig,
    build_detection_jobs,
    build_plan,
)
from trace_contracts.scenario import render_cells, sweep_cells


def test_plan_covers_every_render_cell_with_configured_scene_count() -> None:
    plan = build_plan(ScenarioGenerationConfig(scenes_per_render_cell=2, seed=17))

    assert len(plan.entries) == len(render_cells()) * 2
    assert {entry.render for entry in plan.entries} == set(render_cells())
    assert all(
        sum(entry.render == cell for entry in plan.entries) == 2
        for cell in render_cells()
    )


def test_plan_is_reproducible_for_the_same_generation_parameters() -> None:
    config = ScenarioGenerationConfig(town="Town10HD", scenes_per_render_cell=1, seed=31)

    assert build_plan(config) == build_plan(config)
    assert build_plan(config).manifest_sha256 == build_plan(config).manifest_sha256


def test_plan_changes_derived_scene_seeds_without_changing_the_render_matrix() -> None:
    first = build_plan(ScenarioGenerationConfig(scenes_per_render_cell=1, seed=4))
    second = build_plan(ScenarioGenerationConfig(scenes_per_render_cell=1, seed=5))

    assert [entry.render for entry in first.entries] == [entry.render for entry in second.entries]
    assert [entry.seed for entry in first.entries] != [entry.seed for entry in second.entries]


def test_detector_jobs_reuse_every_rendered_scene_for_all_pairings() -> None:
    plan = build_plan(ScenarioGenerationConfig(scenes_per_render_cell=1, seed=23))

    jobs = build_detection_jobs(plan)

    assert len(jobs) == len(sweep_cells())
    assert {job.pairing for job in jobs} == {cell.pairing for cell in sweep_cells()}
    for entry in plan.entries:
        scene_jobs = [job for job in jobs if job.scene_id == entry.scene_id]
        assert len(scene_jobs) == 3
        assert {job.frame_dir for job in scene_jobs} == {entry.scene_id}


@pytest.mark.parametrize("scenes_per_render_cell", [0, -1])
def test_plan_rejects_non_positive_scene_count(scenes_per_render_cell: int) -> None:
    with pytest.raises(ValueError, match="scenes_per_render_cell"):
        ScenarioGenerationConfig(scenes_per_render_cell=scenes_per_render_cell)
