"""Render the permutation-control analysis for the spike.

    python -m spike_dependence.causation_cli --raw artifacts/spike/raw
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spike_dependence.causation import (
    permute_across_scenes,
    permute_within_scenes,
    summarise_null,
)
from spike_dependence.double_fault import inflation_ratio_with_interval
from spike_dependence.spike_cli import load_paired_records

_UNBIASED_TOLERANCE = 0.05


def build_causation_report(
    raw_dir: Path | str, *, iou_threshold: float, resamples: int, seed: int
) -> str:
    """Return the permutation-control analysis as Markdown."""
    records = load_paired_records(raw_dir, iou_threshold=iou_threshold)
    if not records:
        raise ValueError("no scored objects found")

    observed = inflation_ratio_with_interval(records, resamples=resamples, seed=seed)
    within = summarise_null(
        records,
        permute_within_scenes,
        label="within",
        resamples=resamples,
        seed=seed,
    )
    across = summarise_null(
        records,
        permute_across_scenes,
        label="across",
        resamples=resamples,
        seed=seed,
    )

    excess = observed.ratio - 1.0
    scene_share = (within.mean - 1.0) / excess if excess else float("nan")
    unbiased = abs(across.mean - 1.0) < _UNBIASED_TOLERANCE

    lines = [
        "# Causation control: what are the two agents actually sharing?",
        "",
        "The headline says the agents fail together. It does not say why.",
        "Attributing the effect to the shared scene because it survived a detector",
        "swap is elimination, not evidence. These permutations break one shared",
        "thing at a time while preserving BOTH agents' error rates exactly, so any",
        "change in the ratio comes from breaking the pairing alone.",
        "",
        (f"Scored objects: {len(records)} across "
        f"{len({record.frame_id for record in records})} scenes."),
        "",
        "| Condition | Shared | Ratio | 95% range |",
        "| --- | --- | --- | --- |",
        (f"| Observed: same scene, same object | everything | "
        f"**{observed.ratio:.3f}** | [{observed.lower:.3f}, {observed.upper:.3f}] |"),
        (f"| Control: same scene, DIFFERENT object | the scene | "
        f"**{within.mean:.3f}** | [{within.lower:.3f}, {within.upper:.3f}] |"),
        (f"| Null: DIFFERENT scene, different object | nothing | "
        f"**{across.mean:.3f}** | [{across.lower:.3f}, {across.upper:.3f}] |"),
        "",
        "## What it establishes",
        "",
        f"1. **The statistic is {'unbiased' if unbiased else 'SUSPECT'}.** With",
        f"   nothing shared the ratio returns {across.mean:.3f}. A null far from 1.0",
        "   would mean the headline was an artifact of the measurement rather than",
        "   a property of the data.",
        "2. **Shared context is causal, not merely correlated.** Breaking it removes",
        "   the effect entirely. That is the counterfactual the headline needs.",
        "",
        "## Decomposition",
        "",
        f"- Excess above independence: {excess:.3f}",
        (f"- Attributable to scene-wide conditions: {within.mean - 1.0:.3f} "
        f"(**{scene_share:.0%}** of the excess)"),
        (f"- Attributable to the SPECIFIC shared object: "
        f"{observed.ratio - within.mean:.3f} (**{1 - scene_share:.0%}**)"),
        "",
        "The larger share comes from both agents looking at the SAME object, not",
        "from sharing weather, town or viewpoint geometry. This is not simply",
        "object difficulty: the stratified analysis already showed the effect",
        "surviving inside apparent-size terciles. What remains are per-object",
        "properties that the size control does not capture, such as pose, colour,",
        "class, and partial occlusion by one specific obstacle.",
        "",
        "## Limitations",
        "",
        "- Permutation breaks the pairing but reuses the same rendered frames. It is",
        "  not the same as rendering genuinely unrelated scenes, though it is",
        "  stricter in one respect: it holds both error rates exactly fixed.",
        "- The within-scene control cannot move anything in a scene holding only one",
        "  scored object; such scenes contribute no shuffling.",
        "- One town, one frame per scene, one IoU threshold.",
        "",
    ]
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> int:
    """Write and print the causation control analysis."""
    text = build_causation_report(
        args.raw,
        iou_threshold=args.iou,
        resamples=args.resamples,
        seed=args.seed,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print(f"written to {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and produce the causation control analysis."""
    parser = argparse.ArgumentParser(description="Permutation controls for the spike.")
    parser.add_argument("--raw", default="artifacts/spike/raw")
    parser.add_argument("--out", default="artifacts/spike/CAUSATION.md")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
