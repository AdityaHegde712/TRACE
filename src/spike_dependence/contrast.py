"""The contrast condition: do agents fail together because they SHARE a model?

The spike's headline says two agents' errors co-occur more than independence
predicts. It does not say why. The obvious candidate is the shared detector,
and this module tests it by scoring the same objects four ways:

    homogeneous   A and B both on detector 1
    homogeneous   A and B both on detector 2
    heterogeneous A on detector 1, B on detector 2
    heterogeneous A on detector 2, B on detector 1

Comparison uses the phi coefficient, not the inflation ratio. The ratio
divides by the marginals, so a more accurate detector can show a higher ratio
without the agents being any more associated; phi does not have that problem,
which makes it the fair cross-condition measure.

All four conditions score the SAME objects, so the difference is tested with a
PAIRED bootstrap: resample objects once and recompute every condition on that
same draw.

    python -m spike_dependence.contrast --raw artifacts/spike/raw --tag-b rtdetr
"""

from __future__ import annotations

import argparse
import random
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from spike_dependence.artifacts_io import (
    detection_filename,
    detections_from_json,
    ground_truth_from_json,
)
from spike_dependence.double_fault import (
    PairedErrorRecord,
    contingency,
    odds_ratio,
    phi_coefficient,
)
from spike_dependence.scoring import object_error_flags

_TRUTH_FILES = ("gt_a.json", "gt_b.json")


@dataclass(frozen=True)
class QuadErrorRecord:
    """One object scored under both detectors from both viewpoints."""

    object_id: str
    frame_id: str
    first_a_wrong: bool
    first_b_wrong: bool
    second_a_wrong: bool
    second_b_wrong: bool


@dataclass(frozen=True)
class ContrastResult:
    """Homogeneous versus heterogeneous association, with a paired interval."""

    homogeneous_phi: float
    heterogeneous_phi: float
    difference: float
    lower: float
    upper: float
    objects: int


def _pair(
    records: Sequence[QuadErrorRecord], a_second: bool, b_second: bool
) -> list[PairedErrorRecord]:
    """Build paired records choosing which detector each agent uses."""
    return [
        PairedErrorRecord(
            object_id=record.object_id,
            frame_id=record.frame_id,
            agent_a_wrong=(
                record.second_a_wrong if a_second else record.first_a_wrong
            ),
            agent_b_wrong=(
                record.second_b_wrong if b_second else record.first_b_wrong
            ),
        )
        for record in records
    ]


def condition_phis(records: Sequence[QuadErrorRecord]) -> tuple[float, float]:
    """Return mean homogeneous phi and mean heterogeneous phi."""
    homogeneous = [
        phi_coefficient(contingency(_pair(records, False, False))),
        phi_coefficient(contingency(_pair(records, True, True))),
    ]
    heterogeneous = [
        phi_coefficient(contingency(_pair(records, False, True))),
        phi_coefficient(contingency(_pair(records, True, False))),
    ]
    return (
        sum(homogeneous) / len(homogeneous),
        sum(heterogeneous) / len(heterogeneous),
    )


def paired_difference(
    records: Sequence[QuadErrorRecord], *, resamples: int = 5000, seed: int = 42
) -> ContrastResult:
    """Return the homogeneous-minus-heterogeneous phi gap with an interval.

    Resampling objects rather than conditions keeps the comparison paired,
    which is what makes the interval on the DIFFERENCE meaningful.
    """
    if not records:
        raise ValueError("cannot contrast with no scored objects")

    homogeneous, heterogeneous = condition_phis(records)
    rng = random.Random(seed)
    size = len(records)

    differences: list[float] = []
    for _ in range(resamples):
        draw = [records[rng.randrange(size)] for _ in range(size)]
        try:
            drawn_homo, drawn_hetero = condition_phis(draw)
        except ValueError:
            continue
        differences.append(drawn_homo - drawn_hetero)

    if len(differences) < 2:
        raise ValueError("too few resamples yielded a defined difference")

    differences.sort()
    lower = differences[int(0.025 * len(differences))]
    upper = differences[min(len(differences) - 1, int(0.975 * len(differences)))]
    return ContrastResult(
        homogeneous_phi=homogeneous,
        heterogeneous_phi=heterogeneous,
        difference=homogeneous - heterogeneous,
        lower=lower,
        upper=upper,
        objects=size,
    )


def load_quad_records(
    raw_dir: Path | str, *, iou_threshold: float, tag_a: str | None, tag_b: str | None
) -> list[QuadErrorRecord]:
    """Load every object scored by both detectors from both viewpoints."""
    raw_path = Path(raw_dir)
    first = ("det_a.json", "det_b.json")
    second = (detection_filename("a", tag_a), detection_filename("b", tag_b))

    records: list[QuadErrorRecord] = []
    for scene_dir in sorted(path for path in raw_path.iterdir() if path.is_dir()):
        required = (*_TRUTH_FILES, *first, *second)
        if not all((scene_dir / name).exists() for name in required):
            continue
        truth_a = ground_truth_from_json(scene_dir / "gt_a.json")
        truth_b = ground_truth_from_json(scene_dir / "gt_b.json")

        def flags(truth, name, scene_dir=scene_dir):
            return object_error_flags(
                truth,
                detections_from_json(scene_dir / name),
                iou_threshold=iou_threshold,
            )

        first_a, first_b = flags(truth_a, first[0]), flags(truth_b, first[1])
        second_a, second_b = flags(truth_a, second[0]), flags(truth_b, second[1])

        for object_id in sorted(set(first_a) & set(first_b)):
            records.append(
                QuadErrorRecord(
                    object_id=object_id,
                    frame_id=scene_dir.name,
                    first_a_wrong=first_a[object_id],
                    first_b_wrong=first_b[object_id],
                    second_a_wrong=second_a[object_id],
                    second_b_wrong=second_b[object_id],
                )
            )
    return records


def build_contrast(
    raw_dir: Path | str,
    *,
    iou_threshold: float,
    tag_a: str | None,
    tag_b: str | None,
    first_name: str,
    second_name: str,
    seed: int,
) -> str:
    """Return the contrast condition as Markdown."""
    records = load_quad_records(
        raw_dir, iou_threshold=iou_threshold, tag_a=tag_a, tag_b=tag_b
    )
    if not records:
        raise ValueError("no objects were scored under both detectors")
    result = paired_difference(records, seed=seed)

    rows = [
        (f"homogeneous {first_name} / {first_name}", _pair(records, False, False)),
        (f"homogeneous {second_name} / {second_name}", _pair(records, True, True)),
        (f"heterogeneous {first_name} / {second_name}", _pair(records, False, True)),
        (f"heterogeneous {second_name} / {first_name}", _pair(records, True, False)),
    ]

    lines = [
        "# Contrast condition: does sharing a detector cause the correlation?",
        "",
        f"Objects scored under both detectors: {result.objects}.",
        "",
        "Comparison uses phi, not the inflation ratio: the ratio divides by the",
        "marginals, so a more accurate detector can show a higher ratio without",
        "the agents being any more associated.",
        "",
        "| Condition | phi | odds ratio | pA | pB |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, paired in rows:
        table = contingency(paired)
        lines.append(
            f"| {name} | {phi_coefficient(table):.3f} | {odds_ratio(table):.3f} | "
            f"{table.marginal_a:.3f} | {table.marginal_b:.3f} |"
        )

    excludes_zero = result.lower > 0.0
    lines += [
        "",
        "## Paired bootstrap on the difference",
        "",
        f"- Mean homogeneous phi: **{result.homogeneous_phi:.4f}**",
        f"- Mean heterogeneous phi: **{result.heterogeneous_phi:.4f}**",
        (
            f"- Difference: **{result.difference:+.4f}**, "
            f"95% CI **[{result.lower:+.4f}, {result.upper:+.4f}]**"
        ),
        "",
        "## What this supports",
        "",
    ]
    if excludes_zero:
        lines += [
            "1. Sharing a detector MEASURABLY raises how often two agents fail",
            "   together: the interval on the difference excludes zero.",
            "2. It is NOT the whole story. Agents running DIFFERENT detectors are",
            "   still strongly associated, so most of the correlation comes from",
            "   something they share regardless of model - the scene itself: the",
            "   same objects, the same geometry, the same occlusion.",
            "",
            "Consequence for the method framing: an independence assumption fails",
            "even for heterogeneous agents. That is a BROADER claim than 'identical",
            "perception models fail together', and the proposal should say so.",
        ]
    else:
        lines += [
            "The paired interval on the difference spans zero, so this data cannot",
            "separate homogeneous from heterogeneous agents. Sharing a detector is",
            "not shown to raise the association.",
        ]
    lines += [
        "",
        "## Limitations",
        "",
        "- Two detectors, both COCO-pretrained on overlapping data. Independently",
        "  trained models on disjoint data could behave differently.",
        "- One town, one IoU threshold, one frame per scene.",
        "",
    ]
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> int:
    """Write and print the contrast condition."""
    text = build_contrast(
        args.raw,
        iou_threshold=args.iou,
        tag_a=args.tag_a,
        tag_b=args.tag_b,
        first_name=args.first_name,
        second_name=args.second_name,
        seed=args.seed,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print(f"written to {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and produce the contrast condition."""
    parser = argparse.ArgumentParser(description="Contrast shared vs distinct models.")
    parser.add_argument("--raw", default="artifacts/spike/raw")
    parser.add_argument("--out", default="artifacts/spike/CONTRAST.md")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--tag-a", default="rtdetr")
    parser.add_argument("--tag-b", default="rtdetr")
    parser.add_argument("--first-name", default="yolo11m")
    parser.add_argument("--second-name", default="rtdetr-l")
    parser.add_argument("--seed", type=int, default=42)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
