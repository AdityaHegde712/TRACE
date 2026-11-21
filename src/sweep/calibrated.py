"""Fit the calibrated estimator on practice scenes for the tolerance sweep.

AD-001: the estimator learns from practice scenes only. The sweep still scores
every scene, so rows for the practice half are in-sample. Callers that need an
unbiased figure keep the exam half (`exam_scene_ids`).
"""

from __future__ import annotations

from collections.abc import Sequence

from evidence_resolution.calibration import (
    CalibratedEstimator,
    fit_calibration,
    split_scenes,
)
from sweep.corpus import CorpusTask
from sweep.paired import paired_records_by_pair

DEFAULT_IOU_THRESHOLD = 0.5


def tolerance_policy_version(tolerance: float) -> str:
    """Name one point of the sweep, so every row says which tolerance made it."""
    return f"miss-risk-calibrated-v0-tau{tolerance:g}"


def _scene_ids(tasks: Sequence[CorpusTask]) -> list[str]:
    return sorted({task.entry.scene_id for task in tasks})


def exam_scene_ids(tasks: Sequence[CorpusTask], *, seed: int) -> tuple[str, ...]:
    """The scenes the estimator never saw."""
    return split_scenes(_scene_ids(tasks), seed=seed)[1]


def fit_practice_estimator(
    tasks: Sequence[CorpusTask],
    *,
    seed: int,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> CalibratedEstimator:
    """Fit on the practice half of a seeded random split of the scenes."""
    practice = set(split_scenes(_scene_ids(tasks), seed=seed)[0])
    records = paired_records_by_pair(
        [task for task in tasks if task.entry.scene_id in practice],
        iou_threshold=iou_threshold,
    )
    return fit_calibration(records, seed=seed)
