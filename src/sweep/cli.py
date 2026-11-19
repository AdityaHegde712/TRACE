"""Evaluate frozen M1 policies over a Track B corpus."""

import argparse
import csv
import hashlib
import json
import math
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

from baselines import (
    AlwaysVerifyPolicy,
    FirstReportPolicy,
    LatestReportPolicy,
    MajorityVotePolicy,
    NeverVerifyPolicy,
    arrival_key,
)
from evidence_resolution.association import CameraSetup, PoseProjectionAssociation
from evidence_resolution.reconciliation import WatermarkedReconciler
from sweep.corpus import load_tasks
from sweep.scoring import score_decision
from trace_contracts.estimation import IndependenceEstimator
from trace_contracts.results import RESULT_COLUMNS
from trace_contracts.scenario import DetectorPairing, SweepCell

POLICIES = {
    "latest-report": LatestReportPolicy,
    "first-report-wins": FirstReportPolicy,
    "majority-vote": MajorityVotePolicy,
    "always-verify": AlwaysVerifyPolicy,
    "never-verify": NeverVerifyPolicy,
}


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _safe_segment(value: str) -> str:
    if not value or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        for c in value
    ):
        raise ValueError(f"unsafe artifact identifier: {value!r}")
    return value


def run(args: argparse.Namespace) -> int:
    root, output = args.corpus.resolve(), args.out.resolve()
    if root == output or root in output.parents or output in root.parents:
        raise ValueError("output must be separate from the corpus")
    if output.exists():
        raise ValueError(
            "output already exists; use a new directory to retain prior runs"
        )
    values = [
        args.fov_degrees,
        args.camera_height_m,
        args.slack_seconds,
        args.match_distance_m,
        args.iou_threshold,
    ]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("configuration values must be finite")
    if args.width_px <= 0 or args.height_px <= 0 or not 0 < args.fov_degrees < 180:
        raise ValueError("invalid camera dimensions or field of view")
    if args.slack_seconds <= 0:
        raise ValueError("slack must be strictly positive")
    if args.camera_height_m <= 0 or args.match_distance_m <= 0:
        raise ValueError("invalid camera height or match distance")
    pairings = tuple(DetectorPairing(p) for p in args.pairings)
    if len(set(pairings)) != len(pairings) or len(set(args.policies)) != len(
        args.policies
    ):
        raise ValueError("duplicate pairing or policy selection")
    tasks = load_tasks(root, pairings)
    setup = CameraSetup(
        args.width_px, args.height_px, args.fov_degrees, args.camera_height_m
    )
    association = PoseProjectionAssociation(setup, args.match_distance_m)
    estimator = IndependenceEstimator()
    paths = [root / "manifest.json"]
    paths += sorted((root / "reports").rglob("*.json"))
    paths += sorted((root / "evaluator_truth").rglob("*.json"))
    inputs = {path.relative_to(root).as_posix(): path.read_bytes() for path in paths}
    metadata = {
        "schema": "trace.sweep-run.v0",
        "camera": asdict(setup),
        "slack_seconds": args.slack_seconds,
        "match_distance_m": args.match_distance_m,
        "iou_threshold": args.iou_threshold,
        "association_version": association.version,
        "policies": args.policies,
        "pairings": args.pairings,
        "input_sha256": {
            name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()
        },
    }
    run_id = hashlib.sha256(_json_bytes(metadata)).hexdigest()
    rows, traces = [], {}
    for task in tasks:
        scene = _safe_segment(task.entry.scene_id)
        cell = SweepCell(task.entry.render, task.pairing).cell_id
        reconciler = WatermarkedReconciler(timedelta(seconds=args.slack_seconds))
        reports = []
        for report in sorted(task.reports, key=arrival_key):
            reports.extend(reconciler.ingest(report))
        reports.extend(reconciler.flush())
        if reconciler.late:
            raise ValueError(
                f"late reports beyond watermark in {scene}/{cell}: "
                f"{[r.report_id for r in reconciler.late]}"
            )
        tracks = association.associate(reports)
        for name in args.policies:
            policy = POLICIES[name](association)
            decision = policy.decide(scene, reports, estimator)
            result = score_decision(
                decision,
                reports,
                tracks,
                task.truth,
                run_id=run_id,
                cell_id=cell,
                iou_threshold=args.iou_threshold,
            )
            rows.append(result.to_record())
            record = asdict(decision)
            record["action"] = decision.action.value
            data = _json_bytes([record])
            if hashlib.sha256(data).hexdigest() != result.trace_sha256:
                raise ValueError("persisted trace differs from contract hash")
            traces[f"traces/{cell}/{scene}/{policy.version}.json"] = data
    # Validate all tasks before publishing a results table; preserve inputs for replay.
    output.mkdir(parents=True)
    for name, data in {
        **traces,
        **{f"inputs/{name}": data for name, data in inputs.items()},
    }.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (output / "run.json").write_bytes(
        _json_bytes({"run_id": run_id, **metadata}) + b"\n"
    )
    with (output / "results.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=RESULT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output / 'results.csv'}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--policies", nargs="+", choices=POLICIES, default=list(POLICIES)
    )
    parser.add_argument(
        "--pairings",
        nargs="+",
        choices=[p.value for p in DetectorPairing],
        default=[p.value for p in DetectorPairing],
    )
    parser.add_argument("--width-px", type=int, required=True)
    parser.add_argument("--height-px", type=int, required=True)
    parser.add_argument("--fov-degrees", type=float, required=True)
    parser.add_argument("--camera-height-m", type=float, required=True)
    parser.add_argument("--match-distance-m", type=float, default=4.0)
    parser.add_argument("--slack-seconds", type=float, default=1.0)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(2, f"sweep: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
