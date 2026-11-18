"""Translate detector outputs into the frozen agent-visible report contract."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from spike_dependence.scoring import Detection as SpikeDetection
from trace_contracts.observations import (
    AgentFrameReport,
    BoundingBox,
    CameraPose,
    Detection,
)


def detections_to_report(
    *,
    scene_id: str,
    frame_id: str,
    source_id: str,
    detector: str,
    observed_at: datetime,
    arrived_at: datetime,
    camera_pose: CameraPose,
    detections: Sequence[SpikeDetection],
) -> AgentFrameReport:
    """Return one observation-only report for a detector's frame output.

    Stable identifiers make independent detector reruns comparable without
    adding simulator truth to the agent-visible artifact.
    """
    report_id = f"{scene_id}--{frame_id}--{source_id}"
    contract_detections = tuple(
        Detection(
            detection_id=f"{report_id}--{index:04d}",
            label=detection.label,
            confidence=detection.confidence,
            box=BoundingBox(
                x1=detection.box.x1,
                y1=detection.box.y1,
                x2=detection.box.x2,
                y2=detection.box.y2,
            ),
        )
        for index, detection in enumerate(detections)
    )
    return AgentFrameReport(
        report_id=report_id,
        source_id=source_id,
        scene_id=scene_id,
        frame_id=frame_id,
        observed_at=observed_at,
        arrived_at=arrived_at,
        camera_pose=camera_pose,
        detector=detector,
        detections=contract_detections,
    )
