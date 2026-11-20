"""Show one real double fault: both agents miss the same co-visible object.

Usage: uv run python scripts/visualize_double_fault.py [--pairing homogeneous_yolo]
                                                       [--scene scene-0007] [--rank 0]
Reads artifacts/corpus_900 and writes paper/figures/double_fault_demo.{pdf,png}.

A double fault is an object that both agents could see (it is in both agents'
ground truth) and that neither detected. An object that an agent boxed but gave
the wrong class is a classification error, not a miss, so it is excluded.
Candidates are ranked by the smaller of
the two box areas, largest first, so rank 0 is the most clearly visible object
that both detectors still missed. Ground truth is used here only to draw the
figure; it never reaches the agents (AD-001).
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import figure_style
import run_production

from evidence_resolution.association import CameraSetup, PoseProjectionAssociation
from scenario_gen.corpus import CorpusLayout
from scenario_gen.render import SOURCE_ID_BY_VIEW
from spike_dependence.artifacts_io import camera_poses_from_json
from spike_dependence.scoring import BoundingBox as SpikeBox
from spike_dependence.scoring import intersection_over_union
from sweep.corpus import CorpusTask, load_tasks
from trace_contracts.observations import BoundingBox
from trace_contracts.scenario import DetectorPairing

DETECTED_COLOR = figure_style.GREEN
MISSED_COLOR = "#D62728"
CAMERA_COLORS = (figure_style.BLUE, figure_style.VERMILLION)
FRUSTUM_LENGTH_M = 45.0
# A box of any class overlapping the truth box this much means the agent saw the object.
BOXED_IOU = 0.3
_VIEW_BY_SOURCE = {source: view for view, source in SOURCE_ID_BY_VIEW.items()}


@dataclass(frozen=True)
class DoubleFault:
    """One object that both agents could see and neither detected."""

    scene_id: str
    cell_id: str
    object_id: str
    label: str
    box_a: BoundingBox
    box_b: BoundingBox

    @property
    def visible_area(self) -> float:
        """The smaller box area, so the rank favours objects clear in both views."""
        return min(_area(self.box_a), _area(self.box_b))


def _area(box: BoundingBox) -> float:
    return (box.x2 - box.x1) * (box.y2 - box.y1)


def _overlap(left: BoundingBox, right: BoundingBox) -> float:
    """Return the IoU of two corpus boxes using the spike scorer's definition."""
    return intersection_over_union(
        SpikeBox(left.x1, left.y1, left.x2, left.y2),
        SpikeBox(right.x1, right.y1, right.x2, right.y2),
    )


def find_double_faults(
    tasks: Sequence[CorpusTask], pairing: DetectorPairing
) -> list[DoubleFault]:
    """Return every object both agents missed, largest visible area first."""
    selected = [task for task in tasks if task.pairing is pairing]
    by_scene = {task.entry.scene_id: task for task in selected}
    records = run_production.paired_records_by_pair(
        selected, iou_threshold=run_production.IOU_THRESHOLD
    ).get(pairing.models, [])

    faults = []
    for record in records:
        if not (record.agent_a_wrong and record.agent_b_wrong):
            continue
        task = by_scene[record.frame_id]
        report_a, report_b = sorted(task.reports, key=lambda r: r.source_id)
        truth_a = {t.object_id: t for t in task.truth[report_a.report_id]}
        truth_b = {t.object_id: t for t in task.truth[report_b.report_id]}
        boxed = any(
            _overlap(truth[record.object_id].box, detection.box) >= BOXED_IOU
            for truth, report in ((truth_a, report_a), (truth_b, report_b))
            for detection in report.detections
        )
        if boxed:
            continue
        faults.append(
            DoubleFault(
                scene_id=record.frame_id,
                cell_id=_cell_label(task),
                object_id=record.object_id,
                label=truth_a[record.object_id].label,
                box_a=truth_a[record.object_id].box,
                box_b=truth_b[record.object_id].box,
            )
        )
    return sorted(faults, key=lambda f: (-f.visible_area, f.scene_id, f.object_id))


def _cell_label(task: CorpusTask) -> str:
    """Name a task's render cell as viewpoint-occluder-illumination, for the summary."""
    render = task.entry.render
    return f"{render.viewpoint.value}-{render.occluder.value}-{render.illumination.value}"


def _ground_point(
    association: PoseProjectionAssociation, pose: Any, box: BoundingBox
) -> tuple[float, float] | None:
    """Return where the box's bottom-centre meets the ground, or None above the horizon."""
    try:
        return association.ground_point(pose, (box.x1 + box.x2) / 2, box.y2)
    except ValueError:
        return None


def _draw_box(axis, box: BoundingBox, *, color: str, dashed: bool, width: float) -> None:
    from matplotlib.patches import Rectangle

    axis.add_patch(
        Rectangle(
            (box.x1, box.y1),
            box.x2 - box.x1,
            box.y2 - box.y1,
            fill=False,
            edgecolor=color,
            linewidth=width,
            linestyle=(0, (4, 2)) if dashed else "solid",
        )
    )


def _draw_frame(axis, image, report, missed: BoundingBox, title: str) -> None:
    axis.imshow(image)
    for detection in report.detections:
        _draw_box(axis, detection.box, color=DETECTED_COLOR, dashed=False, width=1.1)
    _draw_box(axis, missed, color=MISSED_COLOR, dashed=True, width=2.2)
    axis.set_title(f"{title}: {len(report.detections)} detected", loc="left")
    axis.axis("off")


def _draw_bev(axis, poses, points, fov_degrees: float, ranges) -> None:
    """Top-down schematic in the simulator frame: cameras, their view cones, the object."""
    from matplotlib.patches import Polygon

    for pose, color, name in zip(poses, CAMERA_COLORS, "AB", strict=True):
        yaw = math.radians(pose.yaw)
        half = math.radians(fov_degrees / 2)
        edges = [
            (pose.x + FRUSTUM_LENGTH_M * math.cos(yaw + sign * half),
             pose.y + FRUSTUM_LENGTH_M * math.sin(yaw + sign * half))
            for sign in (-1, 1)
        ]  # fmt: skip
        axis.add_patch(Polygon([(pose.x, pose.y), *edges], closed=True, color=color, alpha=0.12, lw=0))
        axis.annotate(
            "", (pose.x + 6 * math.cos(yaw), pose.y + 6 * math.sin(yaw)), (pose.x, pose.y),
            arrowprops={"arrowstyle": "-|>", "color": color, "linewidth": 1.2},
        )  # fmt: skip
        axis.scatter([pose.x], [pose.y], s=40, color=color, zorder=4)
        axis.annotate(name, (pose.x, pose.y), xytext=(5, 5), textcoords="offset points",
                      color=color, fontweight="bold")  # fmt: skip
    valid = [p for p in points if p is not None]
    if valid:
        x = sum(p[0] for p in valid) / len(valid)
        y = sum(p[1] for p in valid) / len(valid)
        axis.scatter([x], [y], s=110, marker="*", color=MISSED_COLOR, zorder=5)
    text = ", ".join(f"{name} {metres:.0f} m" for name, metres in zip("AB", ranges) if metres)
    axis.set_title(f"(c) Top view; range {text}", loc="left")
    axis.set_aspect("equal")
    axis.invert_yaxis()  # the simulator's y axis points right, so flip for a map-style view
    axis.set_xlabel("x (m)")
    axis.set_ylabel("y (m)")


def make_figure(
    layout: CorpusLayout,
    pairing: DetectorPairing,
    stem: Path | str,
    *,
    width: int,
    height: int,
    fov_degrees: float = 90.0,
    camera_height_m: float = 14.0,
    scene_id: str | None = None,
    rank: int = 0,
) -> DoubleFault:
    """Draw the three-panel figure for one double fault and return the fault shown."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    tasks = load_tasks(layout.root, (pairing,))
    faults = [
        f for f in find_double_faults(tasks, pairing) if scene_id in (None, f.scene_id)
    ]
    if rank >= len(faults):
        raise ValueError(f"only {len(faults)} double faults found; rank {rank} requested")
    fault = faults[rank]

    task = next(t for t in tasks if t.entry.scene_id == fault.scene_id)
    report_a, report_b = sorted(task.reports, key=lambda r: r.source_id)
    poses = camera_poses_from_json(layout.camera_pose_path(fault.scene_id, report_a.frame_id))
    camera_poses = [poses[_VIEW_BY_SOURCE[r.source_id]] for r in (report_a, report_b)]
    association = PoseProjectionAssociation(
        CameraSetup(width, height, fov_degrees, camera_height_m)
    )
    boxes = (fault.box_a, fault.box_b)
    points = [_ground_point(association, p, b) for p, b in zip(camera_poses, boxes, strict=True)]
    valid = [p for p in points if p is not None]
    centre = (
        (sum(p[0] for p in valid) / len(valid), sum(p[1] for p in valid) / len(valid))
        if valid
        else None
    )
    ranges = [
        math.dist((pose.x, pose.y), centre) if centre else 0.0 for pose in camera_poses
    ]

    figure_style.apply_style()
    fig, axes = plt.subplots(
        1, 3, figsize=(figure_style.PAGE_WIDTH_IN, 2.8),
        gridspec_kw={"width_ratios": [1.0, 1.0, 0.85]}, constrained_layout=True,
    )  # fmt: skip
    detector = report_a.detector
    frames = zip(axes[:2], (report_a, report_b), boxes, ("(a) Camera A", "(b) Camera B"), strict=True)
    for axis, report, box, name in frames:
        image = plt.imread(layout.frame_path(fault.scene_id, report.frame_id, report.source_id))
        _draw_frame(axis, image, report, box, f"{name}, {detector}")
    _draw_bev(axes[2], camera_poses, points, fov_degrees, ranges)

    handles = [
        Line2D([], [], color=DETECTED_COLOR, linewidth=1.4, label="detection"),
        Line2D([], [], color=MISSED_COLOR, linewidth=2.2, linestyle=(0, (4, 2)),
               label="ground-truth object missed by both agents"),
    ]  # fmt: skip
    fig.legend(handles=handles, loc="outside lower center", ncol=2)
    figure_style.save_figure(fig, stem)
    plt.close(fig)
    return fault


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--corpus", type=Path, default=Path("artifacts/corpus_900"))
    parser.add_argument(
        "--pairing", choices=[p.value for p in DetectorPairing], default="homogeneous_yolo"
    )
    parser.add_argument("--scene", default=None, help="Restrict to one scene id")
    parser.add_argument("--rank", type=int, default=0, help="0 = largest missed object")
    parser.add_argument("--width-px", type=int, default=800)
    parser.add_argument("--height-px", type=int, default=600)
    parser.add_argument("--out-dir", type=Path, default=figure_style.FIGURES_DIR)
    args = parser.parse_args(argv)

    fault = make_figure(
        CorpusLayout(args.corpus),
        DetectorPairing(args.pairing),
        args.out_dir / "double_fault_demo",
        width=args.width_px,
        height=args.height_px,
        scene_id=args.scene,
        rank=args.rank,
    )
    print(
        f"showing {fault.scene_id} ({fault.cell_id}): {fault.label} {fault.object_id}, "
        f"box area A={_area(fault.box_a):.0f}px B={_area(fault.box_b):.0f}px",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
