"""Turn corpus tasks into per-object paired error records for calibration."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from spike_dependence.double_fault import PairedErrorRecord
from spike_dependence.scoring import (
    AgentView,
    Detection,
    GroundTruthObject,
    paired_error_records,
)
from spike_dependence.scoring import BoundingBox as SpikeBox
from sweep.corpus import CorpusTask
from trace_contracts.observations import AgentFrameReport
from trace_contracts.truth import TruthObject


def agent_view(report: AgentFrameReport, truth: Sequence[TruthObject]) -> AgentView:
    """Convert one corpus report and its truth into the spike scorer's types."""

    def box(raw: Any) -> SpikeBox:
        return SpikeBox(raw.x1, raw.y1, raw.x2, raw.y2)

    return AgentView(
        agent_id=report.source_id,
        visible_truth=[
            GroundTruthObject(t.object_id, t.label, box(t.box)) for t in truth
        ],
        detections=[
            Detection(d.label, d.confidence, box(d.box)) for d in report.detections
        ],
    )


def paired_records_by_pair(
    tasks: Sequence[CorpusTask], *, iou_threshold: float
) -> dict[tuple[str, str], list[PairedErrorRecord]]:
    """Group per-object error records by detector pair, keyed by scene id."""
    by_pair: dict[tuple[str, str], list[PairedErrorRecord]] = defaultdict(list)
    for task in tasks:
        view_a, view_b = (
            agent_view(report, task.truth[report.report_id])
            for report in sorted(task.reports, key=lambda r: r.source_id)
        )
        by_pair[task.pairing.models].extend(
            paired_error_records(
                task.entry.scene_id, view_a, view_b, iou_threshold=iou_threshold
            )
        )
    return dict(by_pair)
