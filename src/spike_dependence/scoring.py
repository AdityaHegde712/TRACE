"""Turn two agents' detections into paired per-object error indicators.

This module is the single place simulator truth is read (project decision
AD-001). Truth labels each detection right or wrong, then stops. It never
travels onward into the detection or decision path.

An object is scored only when BOTH agents could see it. An object visible to
one agent alone carries no information about joint failure, so counting it
would bias the double-fault rate.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from spike_dependence.double_fault import PairedErrorRecord


@dataclass(frozen=True)
class BoundingBox:
    """An axis-aligned image-space box in pixels, top-left origin."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        """Reject boxes that cannot take part in an overlap calculation."""
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            raise ValueError("a bounding box must have positive area")

    @property
    def area(self) -> float:
        """Return the box area in square pixels."""
        return (self.x2 - self.x1) * (self.y2 - self.y1)


@dataclass(frozen=True)
class GroundTruthObject:
    """One simulator object that a given viewpoint can actually see."""

    object_id: str
    label: str
    box: BoundingBox


@dataclass(frozen=True)
class Detection:
    """One detector output from a single viewpoint."""

    label: str
    confidence: float
    box: BoundingBox


@dataclass(frozen=True)
class AgentView:
    """What one agent saw, and what it reported, for one frame."""

    agent_id: str
    visible_truth: Sequence[GroundTruthObject]
    detections: Sequence[Detection]


def intersection_over_union(left: BoundingBox, right: BoundingBox) -> float:
    """Return the IoU of two boxes; 0.0 when they do not overlap."""
    overlap_width = min(left.x2, right.x2) - max(left.x1, right.x1)
    overlap_height = min(left.y2, right.y2) - max(left.y1, right.y1)
    if overlap_width <= 0 or overlap_height <= 0:
        return 0.0

    intersection = overlap_width * overlap_height
    return intersection / (left.area + right.area - intersection)


def object_error_flags(
    visible_truth: Sequence[GroundTruthObject],
    detections: Sequence[Detection],
    *,
    iou_threshold: float,
) -> dict[str, bool]:
    """Return `{object_id: was_this_agent_wrong}` for one agent and frame.

    Matching is greedy on descending IoU, with a same-label requirement, and
    each detection can satisfy at most one truth object. An unmatched truth
    object is an error. Unmatched detections (false positives) do not appear:
    the double-fault measure is defined per shared object, so there is no
    object to attribute them to.
    """
    if not 0.0 <= iou_threshold <= 1.0:
        raise ValueError("iou_threshold must lie between 0.0 and 1.0")

    candidates = [
        (
            intersection_over_union(truth.box, detection.box),
            truth.object_id,
            detection_index,
        )
        for truth in visible_truth
        for detection_index, detection in enumerate(detections)
        if detection.label == truth.label
    ]
    # Descending IoU, then object id and detection index so ties are stable.
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))

    matched_objects: set[str] = set()
    claimed_detections: set[int] = set()
    for iou, object_id, detection_index in candidates:
        if iou < iou_threshold or iou == 0.0:
            break
        if object_id in matched_objects or detection_index in claimed_detections:
            continue
        matched_objects.add(object_id)
        claimed_detections.add(detection_index)

    return {
        truth.object_id: truth.object_id not in matched_objects
        for truth in visible_truth
    }


def _require_unique_object_ids(view: AgentView) -> None:
    """Raise when one view lists the same object id twice."""
    seen: set[str] = set()
    for truth in view.visible_truth:
        if truth.object_id in seen:
            raise ValueError(
                f"view {view.agent_id!r} lists duplicate object id "
                f"{truth.object_id!r}"
            )
        seen.add(truth.object_id)


def _shared_object_ids(flags_a: Mapping[str, bool], flags_b: Mapping[str, bool]) -> list[str]:
    """Return the sorted object ids that both agents could see."""
    return sorted(set(flags_a) & set(flags_b))


def paired_error_records(
    frame_id: str,
    view_a: AgentView,
    view_b: AgentView,
    *,
    iou_threshold: float,
) -> list[PairedErrorRecord]:
    """Return one paired record per object both agents could see."""
    _require_unique_object_ids(view_a)
    _require_unique_object_ids(view_b)

    flags_a = object_error_flags(
        view_a.visible_truth, view_a.detections, iou_threshold=iou_threshold
    )
    flags_b = object_error_flags(
        view_b.visible_truth, view_b.detections, iou_threshold=iou_threshold
    )

    return [
        PairedErrorRecord(
            object_id=object_id,
            frame_id=frame_id,
            agent_a_wrong=flags_a[object_id],
            agent_b_wrong=flags_b[object_id],
        )
        for object_id in _shared_object_ids(flags_a, flags_b)
    ]


def collect_paired_records(
    frames: Iterable[tuple[str, AgentView, AgentView]],
    *,
    iou_threshold: float,
) -> list[PairedErrorRecord]:
    """Flatten paired records across many frames, preserving frame order."""
    records: list[PairedErrorRecord] = []
    for frame_id, view_a, view_b in frames:
        records.extend(
            paired_error_records(frame_id, view_a, view_b, iou_threshold=iou_threshold)
        )
    return records
