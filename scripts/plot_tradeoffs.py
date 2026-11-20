"""Plot the verification-versus-risk trade-off of every resolution policy.

Usage: uv run python scripts/plot_tradeoffs.py
Reads artifacts/corpus_900_baselines/results.csv and artifacts/corpus_900_eval/results.csv
and writes paper/figures/tradeoffs_pareto.{pdf,png}.

The eval file re-runs two policies that the baselines file already holds. Rows
are keyed by (policy, scene, cell) and counted once; two rows with the same key
must carry the same trace hash, otherwise the files disagree and the run stops.
"""

from __future__ import annotations

import argparse
import csv
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


def plot_tradeoffs(summaries: Sequence[PolicySummary], stem: Path | str) -> list[Path]:
    """Draw false clearance and missed objects against verification rate."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    figure_style.apply_style()
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(figure_style.PAGE_WIDTH_IN, 2.9), constrained_layout=True
    )
    panels = (
        (left, lambda s: 100 * s.false_clearance_rate, "False clearance rate (% of tasks)"),
        (right, lambda s: s.missed_per_task, "Missed objects per task"),
    )
    for axis, value, label in panels:
        frontier = non_dominated(summaries, value_to_risk(value))
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
        axis.set_xlabel("Verification rate (% of tasks sent to verify)")
        axis.set_ylabel(label)
        axis.set_xlim(-6, 106)
        axis.set_ylim(bottom=-0.04 * axis.get_ylim()[1])
        _label_points(axis, summaries, value)
    left.set_title("(a) Unsafe closures fall as verification rises", loc="left")
    right.set_title("(b) Same trade-off in missed objects", loc="left")
    left.text(
        0.40, 0.58, "dashed: non-dominated frontier", transform=left.transAxes,
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
    fig.legend(
        handles=handles, loc="outside lower center", ncol=len(handles), columnspacing=1.2
    )
    paths = figure_style.save_figure(fig, stem)
    plt.close(fig)
    return paths


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
    parser.add_argument("--out-dir", type=Path, default=figure_style.FIGURES_DIR)
    args = parser.parse_args(argv)

    summaries = summarize(load_policy_rows([args.baselines, args.eval]))
    for s in summaries:
        print(
            f"{s.policy:22s} tasks={s.tasks} verify={100 * s.verify_rate:.1f}% "
            f"false_clearance={100 * s.false_clearance_rate:.1f}% "
            f"missed={s.missed_objects} ({s.missed_per_task:.3f}/task)",
            flush=True,
        )
    for path in plot_tradeoffs(summaries, args.out_dir / "tradeoffs_pareto"):
        print(f"wrote {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
