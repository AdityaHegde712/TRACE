"""Pose-projection association: grouping two agents' detections into objects."""

from __future__ import annotations

import math
from datetime import UTC, datetime

import pytest

from evidence_resolution.association import CameraSetup, PoseProjectionAssociation
from trace_contracts.association import Association
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)

SETUP = CameraSetup(
    width_px=800, height_px=600, fov_degrees=90.0, height_above_ground_m=14.0
)
T0 = datetime(2026, 11, 12, tzinfo=UTC)


def orbit_pose(orbit_degrees: float, radius_m: float = 22.0) -> CameraPose:
    """Camera on a circle around the origin looking inward, as the spike places them."""
    radians = math.radians(orbit_degrees)
    return CameraPose(
        x=radius_m * math.cos(radians),
        y=radius_m * math.sin(radians),
        z=SETUP.height_above_ground_m,
        yaw=(orbit_degrees + 180.0) % 360.0,
        pitch=-math.degrees(math.atan2(SETUP.height_above_ground_m, radius_m)),
    )


def pixel_of(
    pose: CameraPose, point: tuple[float, float, float]
) -> tuple[float, float]:
    """Independent forward projection of a world point into the image (test oracle)."""
    dx, dy, dz = point[0] - pose.x, point[1] - pose.y, point[2] - pose.z
    yaw, pitch = math.radians(pose.yaw), math.radians(pose.pitch)
    forward = (
        math.cos(pitch) * math.cos(yaw),
        math.cos(pitch) * math.sin(yaw),
        math.sin(pitch),
    )
    right = (-math.sin(yaw), math.cos(yaw), 0.0)
    up = (
        -math.sin(pitch) * math.cos(yaw),
        -math.sin(pitch) * math.sin(yaw),
        math.cos(pitch),
    )
    depth = dx * forward[0] + dy * forward[1] + dz * forward[2]
    lateral = dx * right[0] + dy * right[1] + dz * right[2]
    vertical = dx * up[0] + dy * up[1] + dz * up[2]
    focal = (SETUP.width_px / 2) / math.tan(math.radians(SETUP.fov_degrees) / 2)
    return (
        SETUP.width_px / 2 + focal * lateral / depth,
        SETUP.height_px / 2 - focal * vertical / depth,
    )


def box_standing_at(pose: CameraPose, ground_xy: tuple[float, float]) -> BoundingBox:
    """A 40x30 px box whose bottom-centre is the object's ground contact point."""
    u, v = pixel_of(pose, (ground_xy[0], ground_xy[1], 0.0))
    return BoundingBox(u - 20.0, v - 30.0, u + 20.0, v)


def report(
    source: str, pose: CameraPose, detections: list[tuple[str, str, BoundingBox]]
) -> AgentFrameReport:
    return AgentFrameReport(
        report_id=f"rep-{source}",
        source_id=source,
        scene_id="scene-000",
        frame_id=f"frame-{source}",
        observed_at=T0,
        arrived_at=T0,
        camera_pose=pose,
        detector="yolo11m",
        detections=tuple(
            Detection(det_id, label, 0.9, box) for det_id, label, box in detections
        ),
    )


POSE_A = orbit_pose(0.0)
POSE_B = orbit_pose(60.0)


def test_satisfies_the_frozen_association_port() -> None:
    assert isinstance(PoseProjectionAssociation(SETUP), Association)


def test_projects_the_image_centre_onto_the_ground() -> None:
    association = PoseProjectionAssociation(SETUP)
    x, y = association.ground_point(POSE_A, 400.0, 300.0)
    # The orbit camera looks at the origin, so the optical axis meets the ground there.
    assert (x, y) == (pytest.approx(0.0, abs=1e-6), pytest.approx(0.0, abs=1e-6))


def test_same_object_seen_from_two_viewpoints_becomes_one_track() -> None:
    target = (3.0, -2.0)
    tracks = PoseProjectionAssociation(SETUP).associate(
        [
            report("agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, target))]),
            report("agent-b", POSE_B, [("b1", "car", box_standing_at(POSE_B, target))]),
        ]
    )
    assert [set(t.members) for t in tracks] == [
        {("rep-agent-a", "a1"), ("rep-agent-b", "b1")}
    ]


def test_distant_objects_stay_separate() -> None:
    tracks = PoseProjectionAssociation(SETUP).associate(
        [
            report(
                "agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, (5.0, 5.0)))]
            ),
            report(
                "agent-b",
                POSE_B,
                [("b1", "car", box_standing_at(POSE_B, (-5.0, -5.0)))],
            ),
        ]
    )
    assert len(tracks) == 2


def test_different_labels_never_merge() -> None:
    target = (1.0, 1.0)
    tracks = PoseProjectionAssociation(SETUP).associate(
        [
            report("agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, target))]),
            report(
                "agent-b", POSE_B, [("b1", "truck", box_standing_at(POSE_B, target))]
            ),
        ]
    )
    assert len(tracks) == 2


def test_one_agent_contributes_at_most_one_detection_per_track() -> None:
    target = (0.0, 0.0)
    near = (0.5, 0.0)
    tracks = PoseProjectionAssociation(SETUP).associate(
        [
            report(
                "agent-a",
                POSE_A,
                [
                    ("a1", "car", box_standing_at(POSE_A, target)),
                    ("a2", "car", box_standing_at(POSE_A, near)),
                ],
            ),
            report("agent-b", POSE_B, [("b1", "car", box_standing_at(POSE_B, target))]),
        ]
    )
    for track in tracks:
        sources = [report_id for report_id, _ in track.members]
        assert len(sources) == len(set(sources))
    assert {("rep-agent-a", "a1"), ("rep-agent-b", "b1")} in [
        set(t.members) for t in tracks
    ]


def test_empty_reports_give_no_tracks_and_output_is_deterministic() -> None:
    association = PoseProjectionAssociation(SETUP)
    assert association.associate([report("agent-a", POSE_A, [])]) == ()
    reports = [
        report("agent-a", POSE_A, [("a1", "car", box_standing_at(POSE_A, (2.0, 0.0)))]),
        report("agent-b", POSE_B, [("b1", "car", box_standing_at(POSE_B, (2.0, 0.0)))]),
    ]
    assert association.associate(reports) == association.associate(
        list(reversed(reports))
    )
