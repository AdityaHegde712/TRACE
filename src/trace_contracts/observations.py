"""What an agent emits: one report per camera frame (agent-visible, AD-001).

A report with no detections is meaningful: the agent looked at the scene and
saw nothing. That is the evidence behind a false "all clear", the hazard the
spike measured (both agents missing the same object).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from trace_contracts import CONTRACT_VERSION
from trace_contracts._schema import require_schema

REPORT_SCHEMA: str = "trace.report.m1-v0"


@dataclass(frozen=True)
class BoundingBox:
    """Axis-aligned image box in pixels, (x1, y1) top-left."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            raise ValueError("bounding box needs x2 > x1 and y2 > y1")


@dataclass(frozen=True)
class CameraPose:
    """Camera position (metres, simulator world frame) and orientation (degrees).

    Carried on every report so cross-agent association can project detections
    into a shared frame without ground truth.
    """

    x: float
    y: float
    z: float
    yaw: float
    pitch: float


@dataclass(frozen=True)
class Detection:
    """One detector output inside a report."""

    detection_id: str
    label: str
    confidence: float
    box: BoundingBox


@dataclass(frozen=True)
class AgentFrameReport:
    """Everything one agent says about one frame.

    `arrived_at` is when the resolver receives the report, separate from
    `observed_at`, so late and out-of-order delivery (A3) can be expressed.
    """

    report_id: str
    source_id: str
    scene_id: str
    frame_id: str
    observed_at: datetime
    arrived_at: datetime
    camera_pose: CameraPose
    detector: str
    detections: tuple[Detection, ...]

    def __post_init__(self) -> None:
        if self.arrived_at < self.observed_at:
            raise ValueError("a report cannot arrive before it was observed")


def report_to_dict(report: AgentFrameReport) -> dict[str, Any]:
    pose = report.camera_pose
    return {
        "schema": REPORT_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "report_id": report.report_id,
        "source_id": report.source_id,
        "scene_id": report.scene_id,
        "frame_id": report.frame_id,
        "observed_at": report.observed_at.isoformat(),
        "arrived_at": report.arrived_at.isoformat(),
        "camera_pose": {
            "x": pose.x,
            "y": pose.y,
            "z": pose.z,
            "yaw": pose.yaw,
            "pitch": pose.pitch,
        },
        "detector": report.detector,
        "detections": [
            {
                "detection_id": d.detection_id,
                "label": d.label,
                "confidence": d.confidence,
                "box": {"x1": d.box.x1, "y1": d.box.y1, "x2": d.box.x2, "y2": d.box.y2},
            }
            for d in report.detections
        ],
    }


def report_from_dict(payload: dict[str, Any]) -> AgentFrameReport:
    require_schema(payload, REPORT_SCHEMA, "report")
    return AgentFrameReport(
        report_id=payload["report_id"],
        source_id=payload["source_id"],
        scene_id=payload["scene_id"],
        frame_id=payload["frame_id"],
        observed_at=datetime.fromisoformat(payload["observed_at"]),
        arrived_at=datetime.fromisoformat(payload["arrived_at"]),
        camera_pose=CameraPose(**payload["camera_pose"]),
        detector=payload["detector"],
        detections=tuple(
            Detection(
                detection_id=raw["detection_id"],
                label=raw["label"],
                confidence=raw["confidence"],
                box=BoundingBox(**raw["box"]),
            )
            for raw in payload["detections"]
        ),
    )
