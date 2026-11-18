"""Empirical SE of log(inflation ratio) vs sample size, from the spike records.

Usage: uv run python scripts/sample_size_floor.py artifacts/spike/raw
Backs the floor table in docs/planning/M1_RESEARCH_ANSWER.md.
"""

from __future__ import annotations

import math
import random
import statistics
import sys

from spike_dependence.double_fault import dependence_inflation_ratio
from spike_dependence.spike_cli import load_paired_records

DETECTOR_PAIRS: dict[str, tuple[str, str]] = {
    "yolo/yolo": ("det_a.json", "det_b.json"),
    "rtdetr/rtdetr": ("det_a_rtdetr.json", "det_b_rtdetr.json"),
    "yolo/rtdetr": ("det_a.json", "det_b_rtdetr.json"),
}
SAMPLE_SIZES: tuple[int, ...] = (100, 200, 448)
DRAWS: int = 2000
# Two-sided 5% test with 80% power.
Z_TOTAL: float = 1.96 + 0.84


def log_ratio_se(records: list, n: int, rng: random.Random) -> float:
    logs = []
    for _ in range(DRAWS):
        draw = [records[rng.randrange(len(records))] for _ in range(n)]
        try:
            logs.append(math.log(dependence_inflation_ratio(draw)))
        except (ValueError, ZeroDivisionError):
            continue
    return statistics.stdev(logs)


def main(raw_dir: str) -> None:
    for name, (det_a, det_b) in DETECTOR_PAIRS.items():
        records = load_paired_records(
            raw_dir, iou_threshold=0.5, det_a_name=det_a, det_b_name=det_b
        )
        point = dependence_inflation_ratio(records)
        rng = random.Random(0)
        ses = {n: log_ratio_se(records, n, rng) for n in SAMPLE_SIZES}
        # SE x sqrt(n) is roughly constant; average it to extrapolate.
        scale = statistics.mean(se * math.sqrt(n) for n, se in ses.items())
        needed = {
            target: math.ceil((Z_TOTAL * scale / math.log(target)) ** 2)
            for target in (1.3, 1.5)
        }
        print(
            f"{name}: objects={len(records)} ratio={point:.3f} "
            + " ".join(f"SE@{n}={se:.3f}" for n, se in ses.items())
            + " | n needed: "
            + ", ".join(f"ratio {t} -> {v}" for t, v in needed.items()),
            flush=True,
        )


if __name__ == "__main__":
    main(sys.argv[1])
