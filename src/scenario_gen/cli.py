"""Command-line entry point for creating a Track B corpus plan."""

from __future__ import annotations

import argparse
from pathlib import Path

from scenario_gen.corpus import CorpusLayout, write_detection_jobs, write_plan
from scenario_gen.planning import (
    ScenarioGenerationConfig,
    build_detection_jobs,
    build_plan,
)


def main(argv: list[str] | None = None) -> int:
    """Write the physical render manifest and post-render detector jobs."""
    parser = argparse.ArgumentParser(description="Create a deterministic Track B corpus plan.")
    parser.add_argument("--out", type=Path, required=True, help="Corpus output directory")
    parser.add_argument("--town", default="Town10HD", help="CARLA town used for every scene")
    parser.add_argument(
        "--scenes-per-render-cell",
        type=int,
        default=1,
        help="Number of physical scenes allocated to every frozen render cell",
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic generator seed")
    args = parser.parse_args(argv)

    config = ScenarioGenerationConfig(
        town=args.town,
        scenes_per_render_cell=args.scenes_per_render_cell,
        seed=args.seed,
    )
    plan = build_plan(config)
    layout = CorpusLayout(args.out)
    write_plan(layout, plan)
    jobs = build_detection_jobs(plan)
    write_detection_jobs(layout, jobs)
    print(
        f"planned {len(plan.entries)} renders and {len(jobs)} detector jobs "
        f"at {layout.root} ({plan.manifest_sha256})"
    )
    return 0
