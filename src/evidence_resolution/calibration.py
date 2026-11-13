"""Calibrated dependence estimator v0: learn on practice scenes, freeze, check on exam scenes.

AD-001 (clarified 2026-11-12): simulator truth may be used OFFLINE, on practice
scenes that never appear in evaluation, to fit the estimator's numbers. The fitted
estimator holds only those frozen numbers; it never sees truth about the scene it
is asked about.

v0 is keyed by detector pair only. Covariates such as illumination and viewpoint
are the next depth step, once the breadth-first pipeline is proven end to end.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from spike_dependence.double_fault import (
    PairedErrorRecord,
    contingency,
    inflation_ratio_with_interval,
)
from trace_contracts.estimation import DependenceEstimate, DependenceQuery


def split_scenes(
    scene_ids: Sequence[str], *, seed: int, practice_fraction: float = 0.5
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split scenes into practice and exam sets, the same way for the same seed."""
    shuffled = sorted(scene_ids)
    random.Random(seed).shuffle(shuffled)
    cut = round(len(shuffled) * practice_fraction)
    return tuple(sorted(shuffled[:cut])), tuple(sorted(shuffled[cut:]))


def split_by_value(
    scene_ids: Sequence[str], value_of: Mapping[str, str], *, held_out: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Hold out every scene with one setting (the shift test, e.g. one weather)."""
    practice = tuple(sorted(s for s in scene_ids if value_of[s] != held_out))
    exam = tuple(sorted(s for s in scene_ids if value_of[s] == held_out))
    return practice, exam


@dataclass(frozen=True)
class CalibrationEntry:
    """Frozen numbers for one detector pair, learned from practice scenes."""

    detectors: tuple[str, str]
    miss_a: float
    miss_b: float
    ratio: float
    lower: float
    upper: float
    objects: int


@dataclass(frozen=True)
class CalibratedEstimator:
    """Looks up frozen practice-scene numbers; satisfies the DependenceEstimator port."""

    entries: tuple[CalibrationEntry, ...]

    @property
    def version(self) -> str:
        """A fingerprint of the frozen numbers, so every decision names exactly them (AD-003)."""
        payload = json.dumps([entry.__dict__ for entry in self.entries], sort_keys=True)
        return "calibrated-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    def estimate(self, query: DependenceQuery) -> DependenceEstimate:
        for entry in self.entries:
            if entry.detectors == query.detectors:
                return self._to_estimate(entry, swapped=False)
            if entry.detectors == (query.detectors[1], query.detectors[0]):
                return self._to_estimate(entry, swapped=True)
        raise KeyError(f"no calibration for detector pair {query.detectors}")

    def _to_estimate(
        self, entry: CalibrationEntry, *, swapped: bool
    ) -> DependenceEstimate:
        miss_rates = (
            (entry.miss_b, entry.miss_a) if swapped else (entry.miss_a, entry.miss_b)
        )
        return DependenceEstimate(
            entry.ratio, entry.lower, entry.upper, self.version, miss_rates=miss_rates
        )


def fit_calibration(
    records_by_pair: Mapping[tuple[str, str], Sequence[PairedErrorRecord]],
    *,
    resamples: int = 2000,
    seed: int = 0,
) -> CalibratedEstimator:
    """Count practice-scene misses per detector pair and freeze the result."""
    entries = []
    for detectors in sorted(records_by_pair):
        records = records_by_pair[detectors]
        table = contingency(records)
        interval = inflation_ratio_with_interval(
            records, resamples=resamples, seed=seed
        )
        entries.append(
            CalibrationEntry(
                detectors=detectors,
                miss_a=table.marginal_a,
                miss_b=table.marginal_b,
                ratio=interval.ratio,
                lower=interval.lower,
                upper=interval.upper,
                objects=table.total,
            )
        )
    return CalibratedEstimator(tuple(entries))


@dataclass(frozen=True)
class ExamCheck:
    """How well frozen practice numbers predict shared misses on unseen exam scenes."""

    objects: int
    predicted_joint_miss: float
    naive_joint_miss: float
    observed_joint_miss: float


def exam_check(
    estimator: CalibratedEstimator,
    detectors: tuple[str, str],
    exam_records: Sequence[PairedErrorRecord],
) -> ExamCheck:
    """Compare predicted (calibrated and naive) with observed shared-miss rates."""
    estimate = estimator.estimate(DependenceQuery(("agent-a", "agent-b"), detectors))
    table = contingency(exam_records)
    return ExamCheck(
        objects=table.total,
        predicted_joint_miss=estimate.joint_miss_probability(),
        naive_joint_miss=estimate.miss_rates[0] * estimate.miss_rates[1],
        observed_joint_miss=table.double_fault,
    )
