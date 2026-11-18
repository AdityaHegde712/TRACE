"""Fit the calibrated estimator on practice scenes and check it on exam scenes.

Usage: uv run python scripts/fit_estimator.py artifacts/spike/raw [--seed 0]
Runs a random scene split and a weather shift test for every detector pair.
Prints only; writes nothing to artifacts/.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence_resolution.calibration import (
    exam_check,
    fit_calibration,
    split_by_value,
    split_scenes,
)
from spike_dependence.spike_cli import load_paired_records

DETECTOR_FILES: dict[tuple[str, str], tuple[str, str]] = {
    ("yolo11m", "yolo11m"): ("det_a.json", "det_b.json"),
    ("rtdetr-l", "rtdetr-l"): ("det_a_rtdetr.json", "det_b_rtdetr.json"),
    ("yolo11m", "rtdetr-l"): ("det_a.json", "det_b_rtdetr.json"),
}


def run_split(label: str, records_by_pair: dict, practice: tuple, exam: tuple) -> None:
    practice_set, exam_set = set(practice), set(exam)
    estimator = fit_calibration(
        {
            pair: [r for r in recs if r.frame_id in practice_set]
            for pair, recs in records_by_pair.items()
        },
        resamples=1000,
    )
    print(f"\n== {label}: {len(practice)} practice scenes, {len(exam)} exam scenes")
    print(f"   estimator version {estimator.version}")
    for pair, recs in records_by_pair.items():
        entry = next(e for e in estimator.entries if e.detectors == pair)
        check = exam_check(estimator, pair, [r for r in recs if r.frame_id in exam_set])
        print(
            f"   {pair[0]}/{pair[1]}: practice ratio {entry.ratio:.2f} [{entry.lower:.2f}, {entry.upper:.2f}] "
            f"| exam both-miss: observed {check.observed_joint_miss:.3f}, "
            f"calibrated {check.predicted_joint_miss:.3f}, naive {check.naive_joint_miss:.3f} "
            f"({check.objects} objects)",
            flush=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("raw", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    records_by_pair = {
        pair: load_paired_records(
            args.raw, iou_threshold=0.5, det_a_name=a, det_b_name=b
        )
        for pair, (a, b) in DETECTOR_FILES.items()
    }
    manifest = json.loads((args.raw / "manifest.json").read_text(encoding="utf-8"))
    weather = {scene["scene_id"]: scene["weather"] for scene in manifest["scenes"]}
    scenes = sorted(weather)

    run_split(
        f"random split (seed {args.seed})",
        records_by_pair,
        *split_scenes(scenes, seed=args.seed),
    )
    for held_out in sorted(set(weather.values())):
        practice, exam = split_by_value(scenes, weather, held_out=held_out)
        run_split(f"shift test, exam = {held_out}", records_by_pair, practice, exam)


if __name__ == "__main__":
    main()
