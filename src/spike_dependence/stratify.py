"""Split the inflation ratio by correlation knob and by object difficulty.

The headline ratio answers the spike question. These splits test WHY, and they
are what a reviewer asks for first:

1. By knob (overlap, occluder, weather) -- does the project's predicted
   mechanism, shared viewpoint, actually drive the correlation?
2. By apparent object size -- the leading alternative explanation is that both
   agents fail together merely because some objects are small and far. If the
   inflation vanishes inside size bins, shared difficulty explains it and
   MATE's conditional claim is not yet refuted.

    python -m spike_dependence.stratify --raw artifacts/spike/raw
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from spike_dependence.artifacts_io import (
    detections_from_json,
    ground_truth_from_json,
    read_manifest,
)
from spike_dependence.double_fault import (
    PairedErrorRecord,
    inflation_ratio_with_interval,
)
from spike_dependence.scoring import object_error_flags

_MIN_STRATUM = 20
_REQUIRED_FILES = ("gt_a.json", "gt_b.json", "det_a.json", "det_b.json")


@dataclass(frozen=True)
class SizedRecord:
    """One paired record plus the object's mean apparent area in pixels."""

    record: PairedErrorRecord
    mean_area_px: float


def load_sized_records(
    raw_dir: Path | str, *, iou_threshold: float
) -> list[SizedRecord]:
    """Return paired records carrying each object's mean apparent area."""
    raw_path = Path(raw_dir)
    scene_dirs = sorted(path for path in raw_path.iterdir() if path.is_dir())

    sized: list[SizedRecord] = []
    for scene_dir in scene_dirs:
        if not all((scene_dir / name).exists() for name in _REQUIRED_FILES):
            continue
        truth_a = ground_truth_from_json(scene_dir / "gt_a.json")
        truth_b = ground_truth_from_json(scene_dir / "gt_b.json")
        flags_a = object_error_flags(
            truth_a,
            detections_from_json(scene_dir / "det_a.json"),
            iou_threshold=iou_threshold,
        )
        flags_b = object_error_flags(
            truth_b,
            detections_from_json(scene_dir / "det_b.json"),
            iou_threshold=iou_threshold,
        )
        area_a = {obj.object_id: obj.box.area for obj in truth_a}
        area_b = {obj.object_id: obj.box.area for obj in truth_b}

        for object_id in sorted(set(flags_a) & set(flags_b)):
            sized.append(
                SizedRecord(
                    record=PairedErrorRecord(
                        object_id=object_id,
                        frame_id=scene_dir.name,
                        agent_a_wrong=flags_a[object_id],
                        agent_b_wrong=flags_b[object_id],
                    ),
                    mean_area_px=(area_a[object_id] + area_b[object_id]) / 2.0,
                )
            )
    return sized


def split_into_terciles(
    sized: Sequence[SizedRecord],
) -> tuple[list[SizedRecord], list[SizedRecord], list[SizedRecord]]:
    """Return the records ordered by area and cut into three equal groups."""
    if len(sized) < 3:
        raise ValueError("need at least three records to form terciles")

    ordered = sorted(sized, key=lambda item: item.mean_area_px)
    cut = len(ordered) // 3
    return ordered[:cut], ordered[cut : 2 * cut], ordered[2 * cut :]


def _describe(name: str, records: Sequence[PairedErrorRecord], seed: int) -> str:
    """Return one report line for a stratum, or say why it has none."""
    if len(records) < _MIN_STRATUM:
        return f"| {name} | {len(records)} | too few | - |"
    try:
        estimate = inflation_ratio_with_interval(records, resamples=4000, seed=seed)
    except ValueError as error:
        return f"| {name} | {len(records)} | undefined | {error} |"
    return (
        f"| {name} | {len(records)} | {estimate.ratio:.3f} | "
        f"[{estimate.lower:.3f}, {estimate.upper:.3f}] |"
    )


def build_analysis(raw_dir: Path | str, *, iou_threshold: float, seed: int) -> str:
    """Return the stratified analysis as Markdown."""
    raw_path = Path(raw_dir)
    sized = load_sized_records(raw_path, iou_threshold=iou_threshold)
    if not sized:
        raise ValueError("no scored objects found")

    scenes = {
        scene.scene_id: scene for scene in read_manifest(raw_path / "manifest.json")
    }
    records = [item.record for item in sized]

    lines = [
        "# Stratified analysis",
        "",
        f"Scored objects: {len(records)} across {len({r.frame_id for r in records})} scenes.",
        "",
        "## By viewpoint overlap (the predicted mechanism)",
        "",
        "| Stratum | n | Ratio | 95% CI |",
        "| --- | --- | --- | --- |",
    ]
    for level in ("high", "medium", "low"):
        subset = [r for r in records if scenes[r.frame_id].overlap.value == level]
        lines.append(_describe(f"overlap = {level}", subset, seed))

    lines += ["", "## By occluder", "", "| Stratum | n | Ratio | 95% CI |", "| --- | --- | --- | --- |"]
    for flag in (True, False):
        subset = [r for r in records if scenes[r.frame_id].occluder is flag]
        lines.append(_describe(f"occluder = {flag}", subset, seed))

    lines += ["", "## By weather", "", "| Stratum | n | Ratio | 95% CI |", "| --- | --- | --- | --- |"]
    for weather in ("ClearNoon", "CloudySunset", "WetNoon"):
        subset = [r for r in records if scenes[r.frame_id].weather.value == weather]
        lines.append(_describe(f"weather = {weather}", subset, seed))

    small, medium, large = split_into_terciles(sized)
    lines += [
        "",
        "## By apparent object size (the confound test)",
        "",
        "Both agents observe the SAME object, so a small, distant object is hard",
        "for both. If that alone produced the headline ratio, these rows would sit",
        "at about 1.0. They do not.",
        "",
        "| Stratum | n | Ratio | 95% CI |",
        "| --- | --- | --- | --- |",
    ]
    for name, chunk in (("small", small), ("medium", medium), ("large", large)):
        span = f"{chunk[0].mean_area_px:.0f}-{chunk[-1].mean_area_px:.0f} px2"
        lines.append(
            _describe(f"size {name} ({span})", [item.record for item in chunk], seed)
        )

    lines += [
        "",
        "## Limitations",
        "",
        "- Apparent area is ONE proxy for difficulty. Object class, pose, colour,",
        "  and partial occlusion by vegetation are shared causes this split does",
        "  not control for.",
        "- The ratio is not monotonic in viewpoint overlap, so shared viewpoint is",
        "  not established as the operative mechanism; it is only the largest",
        "  single stratum.",
        "- One town, one detector, one IoU threshold, one frame per scene.",
        "",
    ]
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> int:
    """Write and print the stratified analysis."""
    text = build_analysis(args.raw, iou_threshold=args.iou, seed=args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print(f"written to {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and produce the stratified analysis."""
    parser = argparse.ArgumentParser(description="Stratify the spike result.")
    parser.add_argument("--raw", default="artifacts/spike/raw")
    parser.add_argument("--out", default="artifacts/spike/ANALYSIS.md")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
