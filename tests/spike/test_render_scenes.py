"""Spec for viewpoint search in the CARLA scene renderer.

CARLA is not importable in the test environment, so the simulator, the
ray-cast check, and everything after viewpoint selection are replaced by fakes.
What is pinned: which spawn points are tried, in what order, and how many
camera angles each one gets.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from spike_dependence import render_scenes
from spike_dependence.scene_matrix import build_scene_matrix

SCENE = build_scene_matrix(1, seed=42)[0]


class ChosenCentre(Exception):
    """Raised by the fake traffic spawner to stop rendering once a centre is chosen."""

    def __init__(self, centre: object) -> None:
        super().__init__(centre)
        self.centre = centre


def make_world(point_count: int) -> MagicMock:
    world = MagicMock()
    points = [SimpleNamespace(location=f"point-{i}") for i in range(point_count)]
    world.get_map().get_spawn_points.return_value = points
    return world


def render(world: MagicMock) -> object:
    return render_scenes.render_scene(
        MagicMock(),
        SimpleNamespace(get_world=lambda: world),
        SCENE,
        out_dir=None,
        width=8,
        height=8,
        radius_m=22.0,
        camera_height_m=14.0,
        vehicle_count=1,
        min_pixels=1,
    )


def test_a_blocked_primary_spawn_point_falls_back_to_the_next_candidate(monkeypatch) -> None:
    world = make_world(50)
    tried: list[object] = []

    def fake_pair(carla, world_, scene, centre, **kwargs):
        tried.append(centre)
        return None if len(tried) < 3 else ("pose-a", "pose-b")

    def fake_spawn_traffic(world_, centre, count, seed):
        raise ChosenCentre(centre)

    monkeypatch.setattr(render_scenes, "_clear_viewpoint_pair", fake_pair)
    monkeypatch.setattr(render_scenes, "_spawn_traffic", fake_spawn_traffic)

    with pytest.raises(ChosenCentre) as chosen:
        render(world)

    expected = [f"point-{(SCENE.seed + offset) % 50}" for offset in range(3)]
    assert tried == expected
    assert chosen.value.centre == expected[2]


def test_the_primary_spawn_point_is_still_tried_first(monkeypatch) -> None:
    world = make_world(50)

    def fake_spawn_traffic(world_, centre, count, seed):
        raise ChosenCentre(centre)

    monkeypatch.setattr(
        render_scenes, "_clear_viewpoint_pair", lambda *a, **k: ("pose-a", "pose-b")
    )
    monkeypatch.setattr(render_scenes, "_spawn_traffic", fake_spawn_traffic)

    with pytest.raises(ChosenCentre) as chosen:
        render(world)

    assert chosen.value.centre == f"point-{SCENE.seed % 50}"


def test_the_search_gives_up_after_twenty_candidates(monkeypatch) -> None:
    world = make_world(50)
    tried: list[object] = []

    def fake_pair(carla, world_, scene, centre, **kwargs):
        tried.append(centre)

    monkeypatch.setattr(render_scenes, "_clear_viewpoint_pair", fake_pair)

    assert render(world) is None
    assert len(tried) == 20
    assert len(set(tried)) == 20


def test_the_search_never_exceeds_the_available_spawn_points(monkeypatch) -> None:
    world = make_world(5)
    tried: list[object] = []

    def fake_pair(carla, world_, scene, centre, **kwargs):
        tried.append(centre)

    monkeypatch.setattr(render_scenes, "_clear_viewpoint_pair", fake_pair)

    assert render(world) is None
    assert len(tried) == 5


def test_each_candidate_gets_twenty_four_camera_angles(monkeypatch) -> None:
    checked: list[object] = []

    def blocked(carla, world, pose):
        checked.append(pose)
        return False

    monkeypatch.setattr(render_scenes, "_has_clear_view", blocked)

    result = render_scenes._clear_viewpoint_pair(
        MagicMock(),
        MagicMock(),
        SCENE,
        SimpleNamespace(x=0.0, y=0.0, z=0.0),
        radius_m=22.0,
        height_m=14.0,
    )

    assert result is None
    assert len(checked) == 24
