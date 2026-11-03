"""Spec for the scene matrix and the two-viewpoint camera geometry.

The spike needs ~50 scenes that vary viewpoint overlap and at least one
occluder or weather condition. The matrix is a balanced factorial design, not
a random draw: an unbalanced sweep would confound the correlation knobs with
each other and make the inflation ratio uninterpretable.

Nothing here imports carla. Geometry is plain arithmetic so it can be checked
before the simulator is ever launched.
"""

from __future__ import annotations

import pytest

from spike_dependence.scene_matrix import (
    INSTALLED_TOWNS,
    Overlap,
    SceneSpec,
    Weather,
    build_scene_matrix,
    viewpoint_pair,
    yaw_separation_degrees,
)


class TestBuildSceneMatrix:
    def test_generates_the_requested_number_of_scenes(self) -> None:
        assert len(build_scene_matrix(50, seed=1)) == 50

    def test_scene_ids_are_unique_and_zero_padded(self) -> None:
        scenes = build_scene_matrix(50, seed=1)

        ids = [scene.scene_id for scene in scenes]
        assert len(set(ids)) == 50
        assert ids[0] == "scene-000"
        assert ids[49] == "scene-049"

    def test_overlap_levels_are_balanced(self) -> None:
        scenes = build_scene_matrix(54, seed=1)

        counts = {level: 0 for level in Overlap}
        for scene in scenes:
            counts[scene.overlap] += 1

        assert max(counts.values()) - min(counts.values()) <= 1

    def test_occluder_condition_is_balanced(self) -> None:
        scenes = build_scene_matrix(54, seed=1)

        with_occluder = sum(1 for scene in scenes if scene.occluder)
        assert abs(with_occluder - (len(scenes) - with_occluder)) <= 1

    def test_every_weather_condition_appears(self) -> None:
        scenes = build_scene_matrix(54, seed=1)

        assert {scene.weather for scene in scenes} == set(Weather)

    def test_only_uses_installed_towns(self) -> None:
        scenes = build_scene_matrix(50, seed=1)

        assert {scene.town for scene in scenes} <= set(INSTALLED_TOWNS)

    def test_is_deterministic_for_a_fixed_seed(self) -> None:
        assert build_scene_matrix(50, seed=7) == build_scene_matrix(50, seed=7)

    def test_different_seeds_change_the_matrix(self) -> None:
        assert build_scene_matrix(50, seed=7) != build_scene_matrix(50, seed=8)

    def test_rejects_a_non_positive_count(self) -> None:
        with pytest.raises(ValueError, match="at least one scene"):
            build_scene_matrix(0, seed=1)


class TestViewpointGeometry:
    def test_higher_overlap_means_smaller_yaw_separation(self) -> None:
        high = yaw_separation_degrees(Overlap.HIGH)
        medium = yaw_separation_degrees(Overlap.MEDIUM)
        low = yaw_separation_degrees(Overlap.LOW)

        assert high < medium < low

    def test_both_cameras_look_at_the_same_scene_centre(self) -> None:
        scene = SceneSpec(
            scene_id="scene-000",
            town="Town01",
            weather=Weather.CLEAR_NOON,
            overlap=Overlap.HIGH,
            occluder=False,
            seed=3,
        )

        pose_a, pose_b = viewpoint_pair(scene, radius_m=15.0, height_m=6.0)

        assert pose_a.target == pose_b.target

    def test_cameras_sit_on_the_requested_radius_and_height(self) -> None:
        scene = SceneSpec(
            scene_id="scene-000",
            town="Town01",
            weather=Weather.CLEAR_NOON,
            overlap=Overlap.MEDIUM,
            occluder=False,
            seed=3,
        )

        pose_a, pose_b = viewpoint_pair(scene, radius_m=20.0, height_m=5.0)

        for pose in (pose_a, pose_b):
            planar = ((pose.x - pose.target[0]) ** 2 + (pose.y - pose.target[1]) ** 2) ** 0.5
            assert planar == pytest.approx(20.0)
            assert pose.z == pytest.approx(pose.target[2] + 5.0)

    def test_separation_matches_the_overlap_level(self) -> None:
        scene = SceneSpec(
            scene_id="scene-000",
            town="Town01",
            weather=Weather.CLEAR_NOON,
            overlap=Overlap.LOW,
            occluder=False,
            seed=3,
        )

        pose_a, pose_b = viewpoint_pair(scene, radius_m=15.0, height_m=6.0)

        gap = abs(pose_a.orbit_degrees - pose_b.orbit_degrees)
        assert gap == pytest.approx(yaw_separation_degrees(Overlap.LOW))

    def test_cameras_face_the_centre(self) -> None:
        scene = SceneSpec(
            scene_id="scene-000",
            town="Town01",
            weather=Weather.CLEAR_NOON,
            overlap=Overlap.HIGH,
            occluder=True,
            seed=3,
        )

        pose_a, _ = viewpoint_pair(scene, radius_m=15.0, height_m=6.0)

        # Yaw points back toward the centre, so it is the orbit angle plus 180.
        assert pose_a.yaw == pytest.approx((pose_a.orbit_degrees + 180.0) % 360.0)

    def test_rejects_a_non_positive_radius(self) -> None:
        scene = SceneSpec(
            scene_id="scene-000",
            town="Town01",
            weather=Weather.CLEAR_NOON,
            overlap=Overlap.HIGH,
            occluder=False,
            seed=3,
        )

        with pytest.raises(ValueError, match="radius"):
            viewpoint_pair(scene, radius_m=0.0, height_m=6.0)


class TestViewpointRetryAndPitch:
    def _scene(self, overlap: Overlap = Overlap.HIGH) -> SceneSpec:
        return SceneSpec(
            scene_id="scene-000",
            town="Town10HD",
            weather=Weather.CLEAR_NOON,
            overlap=overlap,
            occluder=False,
            seed=3,
        )

    def test_explicit_base_angle_overrides_the_seed(self) -> None:
        pose_a, _ = viewpoint_pair(
            self._scene(), radius_m=20.0, height_m=10.0, base_angle_degrees=90.0
        )

        assert pose_a.orbit_degrees == pytest.approx(90.0)

    def test_explicit_base_angle_keeps_the_overlap_separation(self) -> None:
        pose_a, pose_b = viewpoint_pair(
            self._scene(Overlap.MEDIUM),
            radius_m=20.0,
            height_m=10.0,
            base_angle_degrees=90.0,
        )

        gap = pose_b.orbit_degrees - pose_a.orbit_degrees
        assert gap == pytest.approx(yaw_separation_degrees(Overlap.MEDIUM))

    def test_omitting_the_base_angle_still_uses_the_seed(self) -> None:
        first, _ = viewpoint_pair(self._scene(), radius_m=20.0, height_m=10.0)
        again, _ = viewpoint_pair(self._scene(), radius_m=20.0, height_m=10.0)

        assert first.orbit_degrees == pytest.approx(again.orbit_degrees)

    def test_pitch_points_down_at_the_target(self) -> None:
        import math

        pose_a, _ = viewpoint_pair(self._scene(), radius_m=20.0, height_m=20.0)

        # Equal height and radius means a 45 degree downward look.
        assert pose_a.pitch == pytest.approx(-45.0)
        assert math.isclose(abs(pose_a.pitch), 45.0, rel_tol=1e-6)

    def test_a_higher_camera_looks_further_down(self) -> None:
        low, _ = viewpoint_pair(self._scene(), radius_m=20.0, height_m=5.0)
        high, _ = viewpoint_pair(self._scene(), radius_m=20.0, height_m=30.0)

        assert high.pitch < low.pitch

    def test_a_ground_level_camera_looks_straight_ahead(self) -> None:
        pose_a, _ = viewpoint_pair(self._scene(), radius_m=20.0, height_m=0.0)

        assert pose_a.pitch == pytest.approx(0.0)
