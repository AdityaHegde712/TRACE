"""Phase 3: join the saved artifacts and report the inflation ratio.

Pure CPU. It reads what Phase 1 and Phase 2 wrote, pairs the two viewpoints of
each scene, scores them against simulator truth, and renders the report.

    python -m spike_dependence.spike_cli --raw artifacts/spike/raw
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spike_dependence.artifacts_io import (
    detection_filename,
    detections_from_json,
    ground_truth_from_json,
)
from spike_dependence.double_fault import PairedErrorRecord
from spike_dependence.report import build_report, render_markdown
from spike_dependence.scoring import AgentView, paired_error_records

_TRUTH_FILES = ("gt_a.json", "gt_b.json")


def load_paired_records(
    raw_dir: Path | str,
    *,
    iou_threshold: float,
    det_a_name: str = "det_a.json",
    det_b_name: str = "det_b.json",
) -> list[PairedErrorRecord]:
    """Return one paired error record per object both agents could see.

    `det_a_name` and `det_b_name` let the two agents read DIFFERENT detectors'
    output, which is the heterogeneous contrast condition. A scene missing any
    required artifact is skipped rather than part-scored, because a half-read
    scene would silently shift the marginals.
    """
    raw_path = Path(raw_dir)
    scene_dirs = (
        sorted(path for path in raw_path.iterdir() if path.is_dir())
        if raw_path.is_dir()
        else []
    )
    if not scene_dirs:
        raise ValueError(f"no scene folders found under {raw_path}")

    records: list[PairedErrorRecord] = []
    for scene_dir in scene_dirs:
        required = (*_TRUTH_FILES, det_a_name, det_b_name)
        if not all((scene_dir / name).exists() for name in required):
            continue
        view_a = AgentView(
            agent_id="a",
            visible_truth=ground_truth_from_json(scene_dir / "gt_a.json"),
            detections=detections_from_json(scene_dir / det_a_name),
        )
        view_b = AgentView(
            agent_id="b",
            visible_truth=ground_truth_from_json(scene_dir / "gt_b.json"),
            detections=detections_from_json(scene_dir / det_b_name),
        )
        records.extend(
            paired_error_records(
                scene_dir.name, view_a, view_b, iou_threshold=iou_threshold
            )
        )
    return records


def run(args: argparse.Namespace) -> int:
    """Score every scene, render the report, and print it."""
    records = load_paired_records(
        args.raw,
        iou_threshold=args.iou,
        det_a_name=detection_filename("a", args.tag_a),
        det_b_name=detection_filename("b", args.tag_b),
    )
    if not records:
        print("no shared objects were scored; nothing to report", file=sys.stderr)
        return 1

    report = build_report(records, resamples=args.resamples, seed=args.seed)
    text = render_markdown(report)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print(f"written to {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and produce the spike report."""
    parser = argparse.ArgumentParser(description="Report the dependence spike result.")
    parser.add_argument("--raw", default="artifacts/spike/raw")
    parser.add_argument("--out", default="artifacts/spike/REPORT.md")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--tag-a", default=None, help="detector tag for agent A")
    parser.add_argument("--tag-b", default=None, help="detector tag for agent B")
    parser.add_argument("--resamples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
