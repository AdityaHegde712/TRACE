"""Association v0: match detections across agents by projecting them onto the ground.

Each detection's bottom-centre pixel is cast as a ray from the agent's camera and
intersected with the ground plane. Detections from different agents with the same
label whose ground points lie close together are taken to be one object. Uses only
agent-visible data (AD-001).

Known limitation: the bottom edge of a vehicle seen from opposite sides touches the
ground at different points, so ground points of one object can sit a few metres
apart; `max_match_distance_m` absorbs that and must stay below typical vehicle
spacing. Accuracy against ground truth is unmeasured until scenes record poses.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from trace_contracts.association import ObjectTrack
from trace_contracts.observations import AgentFrameReport, CameraPose


@dataclass(frozen=True)
class CameraSetup:
    """Camera settings shared by every agent in a sweep (recorded in the manifest)."""

    width_px: int
    height_px: int
    fov_degrees: float
    height_above_ground_m: float


@dataclass(frozen=True)
class _GroundDetection:
    report_id: str
    detection_id: str
    source_id: str
    label: str
    x: float
    y: float


@dataclass(frozen=True)
class PoseProjectionAssociation:
    """Greedy nearest-pair matching of ground-projected detections."""

    setup: CameraSetup
    max_match_distance_m: float = 4.0
    version: str = "pose-projection-v0"

    def ground_point(self, pose: CameraPose, u: float, v: float) -> tuple[float, float]:
        """Return where the ray through pixel (u, v) meets the ground plane."""
        focal = (self.setup.width_px / 2) / math.tan(
            math.radians(self.setup.fov_degrees) / 2
        )
        right_offset = (u - self.setup.width_px / 2) / focal
        up_offset = (self.setup.height_px / 2 - v) / focal

        yaw, pitch = math.radians(pose.yaw), math.radians(pose.pitch)
        cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
        cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)
        # Camera basis in the simulator world frame (x forward, y right, z up at yaw 0).
        forward = (cos_pitch * cos_yaw, cos_pitch * sin_yaw, sin_pitch)
        right = (-sin_yaw, cos_yaw, 0.0)
        up = (-sin_pitch * cos_yaw, -sin_pitch * sin_yaw, cos_pitch)
        direction = tuple(
            forward[i] + right_offset * right[i] + up_offset * up[i] for i in range(3)
        )

        if direction[2] >= 0.0:
            raise ValueError("pixel ray does not reach the ground")
        ground_z = pose.z - self.setup.height_above_ground_m
        distance = (ground_z - pose.z) / direction[2]
        return pose.x + distance * direction[0], pose.y + distance * direction[1]

    def associate(self, reports: Sequence[AgentFrameReport]) -> tuple[ObjectTrack, ...]:
        detections = sorted(
            self._project(reports), key=lambda d: (d.report_id, d.detection_id)
        )
        cluster_of = list(range(len(detections)))
        sources_in = [{d.source_id} for d in detections]

        for distance, i, j in self._candidate_pairs(detections):
            if distance > self.max_match_distance_m:
                break
            left, right = cluster_of[i], cluster_of[j]
            is_mergeable = left != right and sources_in[left].isdisjoint(
                sources_in[right]
            )
            if not is_mergeable:
                continue
            sources_in[left] |= sources_in[right]
            cluster_of = [left if c == right else c for c in cluster_of]

        members: dict[int, list[tuple[str, str]]] = {}
        for index, detection in enumerate(detections):
            members.setdefault(cluster_of[index], []).append(
                (detection.report_id, detection.detection_id)
            )
        ordered = sorted(tuple(sorted(group)) for group in members.values())
        return tuple(
            ObjectTrack(track_id=f"track-{n:03d}", members=group)
            for n, group in enumerate(ordered)
        )

    def _project(self, reports: Sequence[AgentFrameReport]) -> list[_GroundDetection]:
        projected = []
        for report in reports:
            for detection in report.detections:
                box = detection.box
                x, y = self.ground_point(
                    report.camera_pose, (box.x1 + box.x2) / 2, box.y2
                )
                projected.append(
                    _GroundDetection(
                        report.report_id,
                        detection.detection_id,
                        report.source_id,
                        detection.label,
                        x,
                        y,
                    )
                )
        return projected

    @staticmethod
    def _candidate_pairs(
        detections: list[_GroundDetection],
    ) -> list[tuple[float, int, int]]:
        pairs = [
            (math.dist((a.x, a.y), (b.x, b.y)), i, j)
            for i, a in enumerate(detections)
            for j, b in enumerate(detections)
            if i < j and a.source_id != b.source_id and a.label == b.label
        ]
        return sorted(pairs)
