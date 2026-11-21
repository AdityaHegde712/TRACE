"""Plot the verification-versus-risk trade-off of every resolution policy.

Usage: uv run python scripts/plot_tradeoffs.py
Reads artifacts/corpus_900_baselines/results.csv and artifacts/corpus_900_eval/results.csv
for the discrete policies and artifacts/corpus_900_calibrated_sweep/results.csv for
the TRACE tolerance sweep (miss-risk with the calibrated estimator). Writes
paper/figures/tradeoffs_pareto.{pdf,png}.

The eval file re-runs two policies that the baselines file already holds. Rows
are keyed by (policy, scene, cell) and counted once; two rows with the same key
must carry the same trace hash, otherwise the files disagree and the run stops.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import figure_style

POLICY_ORDER = (
    "never-verify",
    "first-report-wins",
    "latest-report",
    "majority-vote",
    "always-verify",
    "miss-risk",
)
# One marker shape per policy, so identity never rests on color alone.
STYLE = {
    "never-verify": (figure_style.BLUE, "o"),
    "first-report-wins": (figure_style.VERMILLION, "s"),
    "latest-report": (figure_style.ORANGE, "^"),
    "majority-vote": (figure_style.GREEN, "D"),
    "always-verify": (figure_style.PINK, "v"),
    "miss-risk": (figure_style.SKY, "P"),
}


@dataclass(frozen=True)
class PolicySummary:
    policy: str
    tasks: int
    verify_rate: float
    false_clearance_rate: float
    missed_objects: int

    @property
    def missed_per_task(self) -> float:
        return self.missed_objects / self.tasks


def load_policy_rows(paths: Iterable[Path]) -> dict[tuple[str, str, str], dict[str, str]]:
    """Read result files into one dict keyed by (policy, scene, cell)."""
    rows: dict[tuple[str, str, str], dict[str, str]] = {}
    for path in paths:
        with Path(path).open(newline="", encoding="utf-8") as stream:
            for record in csv.DictReader(stream):
                key = (record["policy_version"], record["scene_id"], record["cell_id"])
                known = rows.get(key)
                if known is not None and known["trace_sha256"] != record["trace_sha256"]:
                    raise ValueError(f"row {key} differs between result files")
                rows[key] = record
    return rows


TAU = chr(0x3C4)
EN_DASH = chr(0x2013)
_TOLERANCE = re.compile(r"-tau([0-9.]+)$")


def tolerance_of(policy_version: str) -> float | None:
    """The miss-risk tolerance a sweep policy version names, or None for any other."""
    match = _TOLERANCE.search(policy_version)
    return float(match.group(1)) if match else None


def split_sweep(
    summaries: Iterable[PolicySummary],
) -> tuple[list[PolicySummary], list[PolicySummary]]:
    """Separate the tolerance-sweep points (sorted by tolerance) from the baselines."""
    baselines, sweep = [], []
    for summary in summaries:
        (baselines if tolerance_of(summary.policy) is None else sweep).append(summary)
    sweep.sort(key=lambda s: tolerance_of(s.policy))
    return baselines, sweep


def _tolerance_groups(sweep: Sequence[PolicySummary]) -> list[tuple[str, PolicySummary]]:
    """Merge neighbouring tolerances that land on one point, e.g. 'tau 0.25-0.5'."""
    groups: list[list[PolicySummary]] = []
    for summary in sweep:
        point = (summary.verify_rate, summary.false_clearance_rate)
        last = groups[-1][0] if groups else None
        if last and (last.verify_rate, last.false_clearance_rate) == point:
            groups[-1].append(summary)
        else:
            groups.append([summary])
    labels = []
    for group in groups:
        low, high = tolerance_of(group[0].policy), tolerance_of(group[-1].policy)
        span = f"{low:g}" if low == high else f"{low:g}{EN_DASH}{high:g}"
        labels.append((f"{TAU} = {span}", group[0]))
    return labels


def _short_name(policy_version: str) -> str:
    return policy_version.rsplit("-v", maxsplit=1)[0]


def _order(policy_version: str) -> tuple[int, str]:
    name = _short_name(policy_version)
    return (POLICY_ORDER.index(name) if name in POLICY_ORDER else len(POLICY_ORDER), name)


def summarize(rows: dict[tuple[str, str, str], dict[str, str]]) -> list[PolicySummary]:
    """Return one summary per policy, in the fixed plotting order.

    False clearance rate counts every task: a task closed with a co-visible
    object missed, divided by all tasks, matching Table 3 of the paper.
    """
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for (policy, _, _), record in rows.items():
        tally = counts[policy]
        tally["tasks"] += 1
        tally["verify"] += record["action"] == "verify"
        tally["false_clearance"] += record["false_clearance"] == "True"
        tally["missed"] += int(record["objects_missed_at_close"])
    return [
        PolicySummary(
            policy=policy,
            tasks=tally["tasks"],
            verify_rate=tally["verify"] / tally["tasks"],
            false_clearance_rate=tally["false_clearance"] / tally["tasks"],
            missed_objects=tally["missed"],
        )
        for policy, tally in sorted(counts.items(), key=lambda item: _order(item[0]))
    ]


def non_dominated(
    summaries: Sequence[PolicySummary], risk: Callable[[PolicySummary], float]
) -> list[PolicySummary]:
    """Keep the policies that no other policy beats on verification and risk.

    Ties are kept: two policies with the same verification rate and risk do not
    dominate each other.
    """

    def dominates(a: PolicySummary, b: PolicySummary) -> bool:
        no_worse = a.verify_rate <= b.verify_rate and risk(a) <= risk(b)
        better = a.verify_rate < b.verify_rate or risk(a) < risk(b)
        return no_worse and better

    return [s for s in summaries if not any(dominates(o, s) for o in summaries)]


# Label positions as offsets in points; the two policies that coincide get leader lines.
# never-verify sits under its point so the dashed frontier does not cross the text.
_LABEL_OFFSET = {
    "never-verify": (9, -6, "top"),
    "first-report-wins": (9, 0, "center"),
    "latest-report": (9, 0, "center"),
}
_CLUSTER_LABELS = {
    "majority-vote": ("majority-vote =\nmiss-risk (identical)", (0.40, 0.26)),
    "always-verify": ("always-verify", (0.52, 0.10)),
}


def _label_points(axis, summaries, value) -> None:
    for summary in summaries:
        name = _short_name(summary.policy)
        point = (100 * summary.verify_rate, value(summary))
        if name in _LABEL_OFFSET:
            dx, dy, va = _LABEL_OFFSET[name]
            axis.annotate(
                name, point, xytext=(dx, dy), textcoords="offset points",
                va=va, fontsize=7.5, color=figure_style.INK,
            )  # fmt: skip
        elif name in _CLUSTER_LABELS:
            text, position = _CLUSTER_LABELS[name]
            axis.annotate(
                text, point, xytext=position, textcoords="axes fraction",
                ha="left", va="center", fontsize=7.5, color=figure_style.INK,
                arrowprops={"arrowstyle": "-", "color": figure_style.MUTED, "linewidth": 0.7},
            )  # fmt: skip


def plot_tradeoffs(
    summaries: Sequence[PolicySummary],
    stem: Path | str,
    sweep: Sequence[PolicySummary] = (),
) -> list[Path]:
    """Draw false clearance and missed objects against verification rate.

    `sweep` holds the TRACE tolerance sweep. When given, the curve is drawn in both
    panels and a third panel zooms in on it, because it spans only a few percent of
    the verification axis.
    """
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    figure_style.apply_style()
    columns = 3 if sweep else 2
    fig, axes = plt.subplots(
        1, columns, figsize=(figure_style.PAGE_WIDTH_IN, 2.9), constrained_layout=True
    )
    left, right = axes[0], axes[1]
    panels = (
        (left, lambda s: 100 * s.false_clearance_rate, "False clearance rate (% of tasks)"),
        (right, lambda s: s.missed_per_task, "Missed objects per task"),
    )
    for axis, value, label in panels:
        frontier = sorted(
            non_dominated([*summaries, *sweep], value_to_risk(value)),
            key=lambda s: (s.verify_rate, value(s)),
        )
        axis.step(
            [100 * s.verify_rate for s in frontier],
            [value(s) for s in frontier],
            where="post", color=figure_style.MUTED, linewidth=0.9,
            linestyle=(0, (4, 3)), zorder=2,
        )  # fmt: skip
        for summary in summaries:
            name = _short_name(summary.policy)
            color, marker = STYLE.get(name, (figure_style.MUTED, "o"))
            # miss-risk and majority-vote land on the same point; draw miss-risk as a ring.
            ring = name == "miss-risk"
            axis.scatter(
                100 * summary.verify_rate,
                value(summary),
                s=120 if ring else 46,
                marker=marker,
                facecolor="none" if ring else color,
                edgecolor=color if ring else "white",
                linewidth=1.4 if ring else 0.8,
                zorder=3,
            )
        if sweep:
            axis.plot(
                [100 * s.verify_rate for s in sweep], [value(s) for s in sweep],
                color=figure_style.INK, linewidth=1.3, marker="o", markersize=3.2,
                zorder=4,
            )  # fmt: skip
        axis.set_xlabel("Verification rate (% of tasks sent to verify)")
        axis.set_ylabel(label)
        axis.set_xlim(-6, 106)
        axis.set_ylim(bottom=-0.04 * axis.get_ylim()[1])
        _label_points(axis, summaries, value)
    left.set_title("(a) False clearance", loc="left")
    right.set_title("(b) Missed objects", loc="left")
    if sweep:
        _plot_zoom(axes[2], summaries, sweep)
    left.text(
        0.04, 0.40, "dashed: non-dominated frontier", transform=left.transAxes,
        fontsize=7, color=figure_style.MUTED, va="center",
    )  # fmt: skip

    handles = [
        Line2D(
            [], [], linestyle="none", marker=STYLE[name][1], markersize=6,
            markerfacecolor="none" if name == "miss-risk" else STYLE[name][0],
            markeredgecolor=STYLE[name][0], label=name,
        )
        for name in POLICY_ORDER
    ]  # fmt: skip
    if sweep:
        handles.append(
            Line2D(
                [], [], color=figure_style.INK, linewidth=1.3, marker="o", markersize=3.2,
                label=f"TRACE, calibrated ({TAU} swept)",
            )
        )  # fmt: skip
    fig.legend(
        handles=handles, loc="outside lower center", ncol=4 if sweep else len(handles),
        columnspacing=1.2,
    )  # fmt: skip
    paths = figure_style.save_figure(fig, stem)
    plt.close(fig)
    return paths


def _plot_zoom(axis, summaries, sweep) -> None:
    """Zoom on the sweep: false clearance against verification, high-verify corner."""
    xs = [100 * s.verify_rate for s in sweep]
    ys = [100 * s.false_clearance_rate for s in sweep]
    axis.plot(
        xs, ys, color=figure_style.INK, linewidth=1.3, marker="o", markersize=4,
        zorder=4,
    )  # fmt: skip
    low, high = min(xs) - 0.5, 100.4
    top = max(ys) * 1.35
    for summary in summaries:
        x, y = 100 * summary.verify_rate, 100 * summary.false_clearance_rate
        if not (low <= x <= high and y <= top):
            continue
        name = _short_name(summary.policy)
        color, marker = STYLE.get(name, (figure_style.MUTED, "o"))
        ring = name == "miss-risk"
        axis.scatter(
            x, y, s=120 if ring else 46, marker=marker,
            facecolor="none" if ring else color,
            edgecolor=color if ring else "white", linewidth=1.4 if ring else 0.8,
            zorder=3,
        )  # fmt: skip
    for text, point in _tolerance_groups(sweep):
        axis.annotate(
            text, (100 * point.verify_rate, 100 * point.false_clearance_rate),
            xytext=(7, 5), textcoords="offset points", fontsize=7,
            color=figure_style.INK,
        )  # fmt: skip
    axis.set_xlim(low, high)
    axis.set_ylim(-0.06 * top, top)
    axis.set_xlabel("Verification rate (%)")
    axis.set_ylabel("False clearance rate (% of tasks)")
    axis.set_title("(c) TRACE tolerance sweep, zoomed", loc="left")


def value_to_risk(value: Callable[[PolicySummary], float]) -> Callable[[PolicySummary], float]:
    """Risk is the plotted y value; kept as a named step so the intent reads clearly."""
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--baselines", type=Path, default=Path("artifacts/corpus_900_baselines/results.csv")
    )
    parser.add_argument(
        "--eval", type=Path, default=Path("artifacts/corpus_900_eval/results.csv")
    )
    parser.add_argument(
        "--sweep",
        type=Path,
        default=Path("artifacts/corpus_900_calibrated_sweep/results.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=figure_style.FIGURES_DIR)
    args = parser.parse_args(argv)

    all_rows = load_policy_rows([args.baselines, args.eval, args.sweep])
    summaries, sweep = split_sweep(summarize(all_rows))
    for s in [*summaries, *sweep]:
        print(
            f"{s.policy:22s} tasks={s.tasks} verify={100 * s.verify_rate:.1f}% "
            f"false_clearance={100 * s.false_clearance_rate:.1f}% "
            f"missed={s.missed_objects} ({s.missed_per_task:.3f}/task)",
            flush=True,
        )
    for path in plot_tradeoffs(summaries, args.out_dir / "tradeoffs_pareto", sweep):
        print(f"wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
