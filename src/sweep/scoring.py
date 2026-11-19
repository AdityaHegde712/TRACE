"""Evaluator-only matching; truth never enters a policy or association rule."""

from collections.abc import Mapping, Sequence

from evidence_resolution.reconciliation import canonical_trace_hash
from trace_contracts.association import ObjectTrack
from trace_contracts.observations import AgentFrameReport, BoundingBox
from trace_contracts.policy import Action, TaskDecision
from trace_contracts.results import RunResult
from trace_contracts.truth import TruthObject


def _iou(left: BoundingBox, right: BoundingBox) -> float:
    width = max(0.0, min(left.x2, right.x2) - max(left.x1, right.x1))
    height = max(0.0, min(left.y2, right.y2) - max(left.y1, right.y1))
    intersection = width * height
    area = (left.x2 - left.x1) * (left.y2 - left.y1)
    area += (right.x2 - right.x1) * (right.y2 - right.y1)
    return intersection / (area - intersection)


def score_decision(
    decision: TaskDecision,
    reports: Sequence[AgentFrameReport],
    tracks: Sequence[ObjectTrack],
    truth: Mapping[str, Sequence[TruthObject]],
    *,
    run_id: str,
    cell_id: str,
    iou_threshold: float = 0.5,
) -> RunResult:
    """Match confirmed tracks one-to-one to real objects in their own views."""
    if not 0 < iou_threshold <= 1:
        raise ValueError("IoU threshold must be in (0, 1]")
    visible = [{obj.object_id for obj in truth[r.report_id]} for r in reports]
    co_visible = set.intersection(*visible) if visible else set()
    detections = {
        (r.report_id, d.detection_id): d for r in reports for d in r.detections
    }
    by_track = {t.track_id: t for t in tracks}
    if not set(decision.confirmed_track_ids) <= by_track.keys():
        raise ValueError("policy confirmed an unknown track")
    if len(set(decision.confirmed_track_ids)) != len(decision.confirmed_track_ids):
        raise ValueError("policy confirmed a track more than once")
    candidates: dict[str, list[str]] = {}
    for track_id in sorted(decision.confirmed_track_ids):
        overlaps: dict[str, float] = {}
        for report_id, detection_id in by_track[track_id].members:
            detection = detections[(report_id, detection_id)]
            for obj in truth[report_id]:
                overlap = _iou(detection.box, obj.box)
                if detection.label == obj.label and overlap >= iou_threshold:
                    overlaps[obj.object_id] = max(
                        overlap, overlaps.get(obj.object_id, 0.0)
                    )
        candidates[track_id] = sorted(overlaps, key=lambda obj: (-overlaps[obj], obj))

    # Augmenting paths prevent two tracks from confirming the same physical object.
    matched: dict[str, str] = {}

    def assign(track_id: str, seen: set[str]) -> bool:
        for object_id in candidates[track_id]:
            if object_id in seen:
                continue
            seen.add(object_id)
            if object_id not in matched or assign(matched[object_id], seen):
                matched[object_id] = track_id
                return True
        return False

    for track_id in candidates:
        assign(track_id, set())
    confirmed = co_visible & matched.keys()
    missed = len(co_visible - confirmed) if decision.action is Action.CLOSE else 0
    return RunResult(
        run_id,
        decision.policy_version,
        decision.estimator_version,
        decision.task_id,
        cell_id,
        decision.action.value,
        len(co_visible),
        len(confirmed),
        missed,
        len(candidates) - len(matched),
        int(decision.action is Action.VERIFY),
        canonical_trace_hash([decision]),
    )
