"""Plot how well the calibrated estimator predicts joint misses on unseen scenes.

Usage: uv run python scripts/plot_calibration.py
Writes paper/figures/calibration_stability.{pdf,png}.

The numbers are transcribed from Tables 1 and 2 of paper/sections/results.tex.
tests/scripts/test_figures.py parses those tables and fails if this copy drifts.
Panel (a) is the random split; panel (b) is the nine shift-test folds.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import figure_style

OBSERVED_COLOR = figure_style.INK
CALIBRATED_COLOR = figure_style.BLUE
NAIVE_COLOR = figure_style.VERMILLION


@dataclass(frozen=True)
class RandomSplitRow:
    pairing: str
    ratio: float
    ratio_lower: float
    ratio_upper: float
    observed: float
    calibrated: float
    naive: float


@dataclass(frozen=True)
class ShiftFold:
    held_out: str
    pairing: str
    observed: float
    calibrated: float
    naive: float


RANDOM_SPLIT = (
    RandomSplitRow("YOLO11m / YOLO11m", 1.80, 1.73, 1.87, 0.241, 0.238, 0.133),
    RandomSplitRow("RT-DETR-L / RT-DETR-L", 2.52, 2.38, 2.67, 0.106, 0.110, 0.044),
    RandomSplitRow("YOLO11m / RT-DETR-L", 1.99, 1.90, 2.08, 0.141, 0.148, 0.074),
)

SHIFT_FOLDS = (
    ShiftFold("ClearNoon", "YOLO11m / YOLO11m", 0.237, 0.241, 0.135),
    ShiftFold("ClearNoon", "RT-DETR-L / RT-DETR-L", 0.117, 0.104, 0.043),
    ShiftFold("ClearNoon", "YOLO11m / RT-DETR-L", 0.146, 0.143, 0.075),
    ShiftFold("CloudySunset", "YOLO11m / YOLO11m", 0.255, 0.232, 0.130),
    ShiftFold("CloudySunset", "RT-DETR-L / RT-DETR-L", 0.113, 0.106, 0.043),
    ShiftFold("CloudySunset", "YOLO11m / RT-DETR-L", 0.154, 0.139, 0.072),
    ShiftFold("WetNoon", "YOLO11m / YOLO11m", 0.228, 0.246, 0.134),
    ShiftFold("WetNoon", "RT-DETR-L / RT-DETR-L", 0.095, 0.115, 0.045),
    ShiftFold("WetNoon", "YOLO11m / RT-DETR-L", 0.133, 0.150, 0.075),
)

_PAIRING_SHORT = {
    "YOLO11m / YOLO11m": "Y/Y",
    "RT-DETR-L / RT-DETR-L": "R/R",
    "YOLO11m / RT-DETR-L": "Y/R",
}


def naive_underestimate_range(rows: Sequence[RandomSplitRow | ShiftFold]) -> tuple[float, float]:
    """Return the smallest and largest share of the observed rate the naive model misses."""
    gaps = [1.0 - row.naive / row.observed for row in rows]
    return min(gaps), max(gaps)


def _calibrated_interval(row: RandomSplitRow) -> tuple[float, float]:
    """Scale the calibrated prediction by the fitted ratio's 95% interval."""
    return (
        row.calibrated * row.ratio_lower / row.ratio,
        row.calibrated * row.ratio_upper / row.ratio,
    )


def _plot_random_split(axis) -> None:
    import numpy as np

    positions = np.arange(len(RANDOM_SPLIT))
    width = 0.24
    series = (
        ("Observed", OBSERVED_COLOR, [r.observed for r in RANDOM_SPLIT]),
        ("Calibrated", CALIBRATED_COLOR, [r.calibrated for r in RANDOM_SPLIT]),
        ("Naive (independence)", NAIVE_COLOR, [r.naive for r in RANDOM_SPLIT]),
    )
    for offset, (label, color, values) in zip((-1, 0, 1), series, strict=True):
        yerr = None
        if label == "Calibrated":
            intervals = [_calibrated_interval(r) for r in RANDOM_SPLIT]
            yerr = [
                [v - low for v, (low, _) in zip(values, intervals, strict=True)],
                [high - v for v, (_, high) in zip(values, intervals, strict=True)],
            ]
        axis.bar(
            positions + offset * (width + 0.02), values, width, color=color, label=label,
            yerr=yerr, error_kw={"elinewidth": 0.9, "capsize": 2, "ecolor": figure_style.INK},
            zorder=3,
        )  # fmt: skip
    low, high = naive_underestimate_range(RANDOM_SPLIT)
    for position, row in zip(positions, RANDOM_SPLIT, strict=True):
        gap = 100 * (1.0 - row.naive / row.observed)
        axis.text(
            position, max(row.observed, row.calibrated) + 0.035, f"naive {gap:.0f}% low",
            ha="center", va="bottom", fontsize=7, color=NAIVE_COLOR,
        )  # fmt: skip
    axis.set_xticks(positions, [r.pairing.replace(" / ", " /\n") for r in RANDOM_SPLIT])
    axis.set_ylabel("Exam joint-miss rate")
    axis.set_ylim(0, 0.32)
    axis.grid(axis="x", visible=False)
    axis.set_title("(a) Random split: calibrated tracks observed", loc="left")
    axis.legend(loc="upper right", ncol=1)
    print(f"naive underestimates observed by {100 * low:.0f}% to {100 * high:.0f}%", flush=True)


def _plot_shift(axis) -> None:
    folds = SHIFT_FOLDS
    groups = sorted({f.held_out for f in folds}, key=[f.held_out for f in folds].index)
    markers = (
        ("Observed", OBSERVED_COLOR, "o", lambda f: f.observed, -0.15),
        ("Calibrated", CALIBRATED_COLOR, "D", lambda f: f.calibrated, 0.0),
        ("Naive (independence)", NAIVE_COLOR, "X", lambda f: f.naive, 0.15),
    )
    for label, color, marker, value, jitter in markers:
        axis.scatter(
            [index + jitter for index in range(len(folds))],
            [value(f) for f in folds],
            s=26, marker=marker, color=color, edgecolor="white", linewidth=0.6,
            zorder=3, label=label,
        )  # fmt: skip
    axis.set_xticks(range(len(folds)), [_PAIRING_SHORT[f.pairing] for f in folds])
    for number, group in enumerate(groups):
        first = 3 * number
        axis.text(
            first + 1, -0.13, group, ha="center", va="top", fontsize=7.5,
            transform=axis.get_xaxis_transform(), color=figure_style.INK,
        )  # fmt: skip
        if number:
            axis.axvline(first - 0.5, color=figure_style.GRID, linewidth=0.8)
    axis.set_ylabel("Exam joint-miss rate")
    axis.set_ylim(0, 0.32)
    axis.set_xlim(-0.6, len(folds) - 0.4)
    axis.grid(axis="x", visible=False)
    axis.set_title("(b) Held-out illumination: nine folds", loc="left")
    axis.legend(loc="upper center", ncol=3, columnspacing=1.0, handletextpad=0.3)
    low, high = naive_underestimate_range(folds)
    print(f"shift folds: naive underestimates by {100 * low:.0f}% to {100 * high:.0f}%", flush=True)


def plot_calibration(stem: Path | str) -> list[Path]:
    """Draw the two-panel calibration figure and save it as PDF and PNG."""
    import matplotlib.pyplot as plt

    figure_style.apply_style()
    fig, (left, right) = plt.subplots(
        1,
        2,
        figsize=(figure_style.PAGE_WIDTH_IN, 3.0),
        gridspec_kw={"width_ratios": [1.0, 1.15]},
        constrained_layout=True,
    )
    _plot_random_split(left)
    _plot_shift(right)
    paths = figure_style.save_figure(fig, stem)
    plt.close(fig)
    return paths


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", type=Path, default=figure_style.FIGURES_DIR)
    args = parser.parse_args(argv)
    for path in plot_calibration(args.out_dir / "calibration_stability"):
        print(f"wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
