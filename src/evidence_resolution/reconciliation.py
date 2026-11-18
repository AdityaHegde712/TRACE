"""A3 reconciliation: make decisions independent of report arrival order.

Agents deliver reports late and out of order. The reconciler buffers them and
releases a report only once the watermark (newest observed_at seen, minus a
fixed slack) has passed it. Released reports come out in one canonical order,
(observed_at, source_id, report_id), so any arrival permutation whose skew stays
within the slack produces the same sequence, the same decisions, and the same
trace hash.

A report that arrives behind the watermark cannot be placed in order without
rewriting what was already released, so it is held in `late`, never dropped
silently and never mixed into the canonical stream.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta

from trace_contracts.observations import AgentFrameReport
from trace_contracts.policy import TaskDecision


def _order_key(report: AgentFrameReport) -> tuple[datetime, str, str]:
    return (report.observed_at, report.source_id, report.report_id)


class WatermarkedReconciler:
    """Buffer reports and release them in canonical order behind a watermark."""

    def __init__(self, slack: timedelta) -> None:
        if slack < timedelta(0):
            raise ValueError("slack must be zero or positive")
        self._slack = slack
        self._pending: list[AgentFrameReport] = []
        self._late: list[AgentFrameReport] = []
        self._newest_observed: datetime | None = None

    @property
    def watermark(self) -> datetime | None:
        """Reports observed at or before this instant are complete."""
        if self._newest_observed is None:
            return None
        return self._newest_observed - self._slack

    @property
    def late(self) -> tuple[AgentFrameReport, ...]:
        """Reports that arrived after the watermark had already passed them."""
        return tuple(self._late)

    def ingest(self, report: AgentFrameReport) -> list[AgentFrameReport]:
        """Accept one report and return any reports the watermark now releases."""
        watermark = self.watermark
        if watermark is not None and report.observed_at <= watermark:
            self._late.append(report)
            return []

        self._pending.append(report)
        if self._newest_observed is None or report.observed_at > self._newest_observed:
            self._newest_observed = report.observed_at
        return self._release(lambda r: r.observed_at <= self.watermark)

    def flush(self) -> list[AgentFrameReport]:
        """Release every pending report in canonical order, e.g. at end of stream."""
        return self._release(lambda _: True)

    def _release(
        self, ready: Callable[[AgentFrameReport], bool]
    ) -> list[AgentFrameReport]:
        released = sorted((r for r in self._pending if ready(r)), key=_order_key)
        released_ids = {id(r) for r in released}
        self._pending = [r for r in self._pending if id(r) not in released_ids]
        return released


def canonical_trace_hash(decisions: Sequence[TaskDecision]) -> str:
    """Return the SHA-256 of the decisions as canonical JSON (sorted keys, no spaces)."""
    payload = [
        {
            "task_id": d.task_id,
            "action": d.action.value,
            "reason_code": d.reason_code,
            "causal_report_ids": list(d.causal_report_ids),
            "confirmed_track_ids": list(d.confirmed_track_ids),
            "policy_version": d.policy_version,
            "estimator_version": d.estimator_version,
        }
        for d in decisions
    ]
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
