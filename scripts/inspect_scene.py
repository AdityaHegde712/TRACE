"""Print one corpus scene: conditions, truth, detections, tracks, and every policy's decision.

Usage: uv run python scripts/inspect_scene.py --scene scene-0515
           [--corpus artifacts/corpus_900] [--pairing homogeneous_yolo] [--tau 0.05]
Reads the corpus only; writes nothing. Loading validates the whole corpus, so
expect a few seconds on the 900-scene corpus.

A double fault is an object both agents got wrong at IoU 0.5 (missed, or boxed with
the wrong class). This is the paper's definition. The calibrated miss-risk row uses
an estimator fitted on the practice half of a seed-0 split.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from baselines import arrival_key
from evidence_resolution.association import CameraSetup, PoseProjectionAssociation
from evidence_resolution.miss_risk_policy import MissRiskPolicy
from evidence_resolution.reconciliation import WatermarkedReconciler
from spike_dependence.scoring import paired_error_records
from sweep.calibrated import fit_practice_estimator, tolerance_policy_version
from sweep.cli import POLICIES
from sweep.corpus import CorpusTask, load_tasks
from sweep.paired import agent_view
from sweep.scoring import score_decision
from trace_contracts.estimation import IndependenceEstimator
from trace_contracts.observations import AgentFrameReport
from trace_contracts.scenario import DetectorPairing, RenderCell

# The camera the production sweep used (scripts/run_production.py SWEEP_CAMERA).
CAMERA = CameraSetup(width_px=800, height_px=600, fov_degrees=90.0, height_above_ground_m=14.0)
MATCH_DISTANCE_M = 4.0
SLACK_SECONDS = 1.0
IOU_THRESHOLD = 0.5
CALIBRATION_SEED = 0
BASELINES = (
    "latest-report", "first-report-wins", "majority-vote", "never-verify", "always-verify",
)  # fmt: skip


@dataclass(frozen=True)
class ObjectRow:
    object_id: str
    label: str
    box: tuple[int, int, int, int]
    found_by_a: bool
    found_by_b: bool

    @property
    def double_fault(self) -> bool:
        return not self.found_by_a and not self.found_by_b


@dataclass(frozen=True)
class DecisionRow:
    policy: str
    action: str
    reason: str
    false_clearance: bool
    missed: int


@dataclass(frozen=True)
class Inspection:
    scene_id: str
    town: str
    render: RenderCell
    pairing: DetectorPairing
    reports: tuple[AgentFrameReport, ...]
    objects: tuple[ObjectRow, ...]
    tracks: tuple[str, ...]
    decisions: tuple[DecisionRow, ...]


def _reconcile(task: CorpusTask) -> list[AgentFrameReport]:
    reconciler = WatermarkedReconciler(timedelta(seconds=SLACK_SECONDS))
    reports: list[AgentFrameReport] = []
    for report in sorted(task.reports, key=arrival_key):
        reports.extend(reconciler.ingest(report))
    reports.extend(reconciler.flush())
    if reconciler.late:
        raise ValueError(f"late reports beyond watermark in {task.entry.scene_id}")
    return reports


def _box(raw) -> tuple[int, int, int, int]:
    return round(raw.x1), round(raw.y1), round(raw.x2), round(raw.y2)


def _objects(task: CorpusTask) -> tuple[ObjectRow, ...]:
    report_a, report_b = sorted(task.reports, key=lambda r: r.source_id)
    views = [agent_view(r, task.truth[r.report_id]) for r in (report_a, report_b)]
    records = paired_error_records(
        task.entry.scene_id, *views, iou_threshold=IOU_THRESHOLD
    )
    truth_a = {t.object_id: t for t in task.truth[report_a.report_id]}
    return tuple(
        ObjectRow(
            record.object_id,
            truth_a[record.object_id].label,
            _box(truth_a[record.object_id].box),
            found_by_a=not record.agent_a_wrong,
            found_by_b=not record.agent_b_wrong,
        )
        for record in records
    )


def _track_text(track, reports: Sequence[AgentFrameReport]) -> str:
    source_of = {r.report_id: r.source_id for r in reports}
    label_of = {
        (r.report_id, d.detection_id): d.label for r in reports for d in r.detections
    }
    members = " + ".join(
        f"{source_of[rid]}:{did} {label_of[(rid, did)]}" for rid, did in track.members
    )
    confirmed = len({source_of[rid] for rid, _ in track.members}) >= 2
    return f"{track.track_id}: {members} ({'confirmed' if confirmed else 'single source'})"


def _policies(association, calibrated, tau):
    policies = [(name, POLICIES[name](association), IndependenceEstimator()) for name in BASELINES]
    policies.append(
        (
            f"miss-risk (independence, tau={tau:g})",
            MissRiskPolicy(association, miss_risk_tolerance=tau),
            IndependenceEstimator(),
        )
    )
    policies.append(
        (
            f"miss-risk (calibrated, tau={tau:g})",
            MissRiskPolicy(
                association,
                miss_risk_tolerance=tau,
                version=tolerance_policy_version(tau),
            ),
            calibrated,
        )
    )
    return policies


def inspect_scene(
    tasks: Sequence[CorpusTask],
    scene_id: str,
    *,
    pairings: Sequence[DetectorPairing] = tuple(DetectorPairing),
    tau: float = 0.05,
) -> list[Inspection]:
    """Return one inspection per requested detector pairing."""
    if scene_id not in {t.entry.scene_id for t in tasks}:
        raise ValueError(f"unknown scene: {scene_id}")
    association = PoseProjectionAssociation(CAMERA, MATCH_DISTANCE_M)
    calibrated = fit_practice_estimator(tasks, seed=CALIBRATION_SEED, iou_threshold=IOU_THRESHOLD)
    inspections = []
    for pairing in pairings:
        task = next(
            t for t in tasks if t.entry.scene_id == scene_id and t.pairing is pairing
        )
        reports = _reconcile(task)
        tracks = association.associate(reports)
        decisions = []
        for name, policy, estimator in _policies(association, calibrated, tau):
            decision = policy.decide(scene_id, reports, estimator)
            result = score_decision(
                decision, reports, tracks, task.truth,
                run_id="inspect", cell_id=pairing.value, iou_threshold=IOU_THRESHOLD,
            )  # fmt: skip
            decisions.append(
                DecisionRow(
                    name,
                    decision.action.value,
                    decision.reason_code,
                    result.false_clearance,
                    result.objects_missed_at_close,
                )
            )
        inspections.append(
            Inspection(
                scene_id,
                task.entry.town,
                task.entry.render,
                pairing,
                tuple(sorted(reports, key=lambda r: r.source_id)),
                _objects(task),
                tuple(_track_text(t, reports) for t in tracks),
                tuple(decisions),
            )
        )
    return inspections


def _table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> list[str]:
    cells = [[str(c) for c in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths, strict=True))
    out = [line.rstrip(), "  ".join("-" * w for w in widths)]
    out += ["  ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)).rstrip() for r in cells]
    return out


def _render_one(i: Inspection) -> list[str]:
    cell = i.render
    detectors = i.pairing.models
    lines = [
        (
            f"=== {i.scene_id} | pairing {i.pairing.value} "
            f"(camera a: {detectors[0]}, camera b: {detectors[1]}) ==="
        ),
        f"Town: {i.town}",
        (
            f"Conditions: viewpoint {cell.viewpoint.value}, "
            f"occluder {cell.occluder.value}, illumination {cell.illumination.value}"
        ),
        "",
        "Co-visible ground truth (found = detected with the right class at IoU 0.5):",
    ]
    if i.objects:
        lines += _table(
            ["object", "label", "box (x1,y1,x2,y2)", "camera a", "camera b", ""],
            [
                (
                    o.object_id, o.label, ",".join(map(str, o.box)),
                    "found" if o.found_by_a else "WRONG",
                    "found" if o.found_by_b else "WRONG",
                    "<- DOUBLE FAULT" if o.double_fault else "",
                )
                for o in i.objects
            ],
        )  # fmt: skip
    else:
        lines.append("(none)")
    faults = [o.object_id for o in i.objects if o.double_fault]
    lines.append(
        f"DOUBLE FAULT: {len(faults)} object(s) wrong in both cameras: {', '.join(faults)}"
        if faults
        else "No double fault in this scene."
    )
    lines += ["", "Detections:"]
    rows = [
        (r.source_id, r.detector, d.detection_id, d.label, f"{d.confidence:.2f}",
         ",".join(map(str, _box(d.box))))
        for r in i.reports
        for d in r.detections
    ]  # fmt: skip
    lines += (
        _table(["camera", "detector", "id", "label", "conf", "box"], rows)
        if rows
        else ["(no detections from either camera)"]
    )
    lines += ["", "Ground-plane tracks:"]
    lines += [f"  {t}" for t in i.tracks] or ["  (none)"]
    lines += ["", "Decisions:"]
    lines += _table(
        ["policy", "action", "reason", "missed at close", "false clearance"],
        [
            (d.policy, d.action, d.reason, d.missed, "YES" if d.false_clearance else "no")
            for d in i.decisions
        ],
    )
    return lines


def render_text(inspections: Sequence[Inspection]) -> str:
    """Format the inspections as plain text for a terminal."""
    blocks = ["\n".join(_render_one(i)) for i in inspections]
    return "\n\n".join(blocks) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--corpus", type=Path, default=Path("artifacts/corpus_900"))
    parser.add_argument("--scene", required=True, help="e.g. scene-0515")
    parser.add_argument(
        "--pairing", choices=[p.value for p in DetectorPairing], default=None,
        help="Show one detector pairing (default: all three)",
    )  # fmt: skip
    parser.add_argument("--tau", type=float, default=0.05, help="Miss-risk tolerance")
    args = parser.parse_args(argv)
    if not 0 <= args.tau <= 1:
        parser.exit(2, "inspect_scene: --tau must lie in [0, 1]\n")
    pairings = (
        (DetectorPairing(args.pairing),) if args.pairing else tuple(DetectorPairing)
    )
    try:
        tasks = load_tasks(args.corpus, tuple(DetectorPairing))
        inspections = inspect_scene(tasks, args.scene, pairings=pairings, tau=args.tau)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f"inspect_scene: {error}\n")
    sys.stdout.write(render_text(inspections))
    return 0


if __name__ == "__main__":
    sys.exit(main())
