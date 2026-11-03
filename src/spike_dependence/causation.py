"""Permutation controls: test WHAT the two agents share, not just that they fail.

The spike measured that two agents fail together more than independence
predicts. Attributing that to "the shared scene" because the effect survived
swapping detectors is elimination, not evidence. These controls break one
shared thing at a time and re-measure:

- `permute_within_scenes` shuffles agent B's errors among the objects of the
  SAME scene. The scene, the weather, the viewpoint geometry and the occluders
  are still shared; the specific object is not.
- `permute_across_scenes` shuffles agent B's errors over every object in the
  run, so the two agents are effectively looking at different scenes. Nothing
  is shared. This is the NULL control: if it does not come back near 1.0, the
  statistic is biased and the headline cannot be trusted.

Permutation preserves each agent's marginal error rate exactly, so any change
in the ratio comes from breaking the pairing rather than from changing how
accurate either agent is. That is what makes this a control rather than a
different experiment.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from spike_dependence.double_fault import PairedErrorRecord, contingency

Permutation = Callable[[Sequence[PairedErrorRecord], int], list[PairedErrorRecord]]


@dataclass(frozen=True)
class NullSummary:
    """A permutation null: where the ratio sits once a shared thing is broken."""

    label: str
    mean: float
    lower: float
    upper: float
    resamples: int


def _rebuilt(
    records: Sequence[PairedErrorRecord], b_flags: Sequence[bool]
) -> list[PairedErrorRecord]:
    """Return the records with agent B's error flags replaced in order."""
    return [
        PairedErrorRecord(
            object_id=record.object_id,
            frame_id=record.frame_id,
            agent_a_wrong=record.agent_a_wrong,
            agent_b_wrong=flag,
        )
        for record, flag in zip(records, b_flags, strict=True)
    ]


def permute_across_scenes(
    records: Sequence[PairedErrorRecord], seed: int
) -> list[PairedErrorRecord]:
    """Shuffle agent B's errors over every object, ignoring scene boundaries.

    The two agents are then effectively observing different scenes. Nothing is
    shared, so this is the null control.
    """
    flags = [record.agent_b_wrong for record in records]
    random.Random(seed).shuffle(flags)
    return _rebuilt(records, flags)


def permute_within_scenes(
    records: Sequence[PairedErrorRecord], seed: int
) -> list[PairedErrorRecord]:
    """Shuffle agent B's errors only among objects of the same scene.

    The scene stays shared; the specific object does not. A ratio above 1.0
    here is scene-level dependence. A ratio near 1.0 says the association is
    attached to the individual object rather than to the scene as a whole.
    """
    rng = random.Random(seed)
    by_scene: dict[str, list[int]] = {}
    for index, record in enumerate(records):
        by_scene.setdefault(record.frame_id, []).append(index)

    flags = [record.agent_b_wrong for record in records]
    for positions in by_scene.values():
        scene_flags = [flags[position] for position in positions]
        rng.shuffle(scene_flags)
        for position, flag in zip(positions, scene_flags, strict=True):
            flags[position] = flag
    return _rebuilt(records, flags)


def null_ratios(
    records: Sequence[PairedErrorRecord],
    permutation: Permutation,
    *,
    resamples: int,
    seed: int,
) -> list[float]:
    """Return the inflation ratio under repeated permutation.

    A permutation that leaves an agent with no errors makes the ratio
    undefined; those draws are dropped rather than coerced.
    """
    if not records:
        raise ValueError("permutation needs at least one record")
    if resamples < 1:
        raise ValueError("resamples must be at least 1")

    ratios: list[float] = []
    for offset in range(resamples):
        table = contingency(permutation(records, seed + offset))
        predicted = table.independent_prediction
        if predicted == 0.0:
            continue
        ratios.append(table.double_fault / predicted)
    return ratios


def summarise_null(
    records: Sequence[PairedErrorRecord],
    permutation: Permutation,
    *,
    label: str,
    resamples: int = 2000,
    seed: int = 42,
) -> NullSummary:
    """Return the mean and central 95% range of a permutation null."""
    ratios = sorted(null_ratios(records, permutation, resamples=resamples, seed=seed))
    if len(ratios) < 2:
        raise ValueError("too few permutations yielded a defined ratio")
    return NullSummary(
        label=label,
        mean=sum(ratios) / len(ratios),
        lower=ratios[int(0.025 * len(ratios))],
        upper=ratios[min(len(ratios) - 1, int(0.975 * len(ratios)))],
        resamples=len(ratios),
    )

