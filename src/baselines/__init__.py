"""Simple policies consuming only agent-visible M1 reports."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from trace_contracts.association import Association, ObjectTrack
from trace_contracts.estimation import DependenceEstimator
from trace_contracts.observations import AgentFrameReport
from trace_contracts.policy import Action, TaskDecision


def arrival_key(report: AgentFrameReport) -> tuple[datetime, datetime, str, str]:
    return report.arrived_at, report.observed_at, report.source_id, report.report_id


@dataclass(frozen=True)
class _Baseline:
    association: Association
    version: str = "baseline-v0"

    def decide(
        self,
        task_id: str,
        reports: Sequence[AgentFrameReport],
        estimator: DependenceEstimator,
    ) -> TaskDecision:
        ordered = sorted(reports, key=arrival_key)
        tracks = self.association.associate(ordered) if ordered else ()
        if not ordered:
            action, reason, causal, confirmed = Action.WAIT, "no_reports", (), ()
        else:
            action, reason, causal, confirmed = self._select(ordered, tracks)
        return TaskDecision(
            task_id,
            action,
            reason,
            tuple(sorted(r.report_id for r in causal)),
            confirmed,
            self.version,
            estimator.version,
        )

    def _select(
        self,
        reports: Sequence[AgentFrameReport],
        tracks: Sequence[ObjectTrack],
    ) -> tuple[Action, str, Sequence[AgentFrameReport], tuple[str, ...]]:
        return (
            Action.CLOSE,
            "accept_all_reports",
            reports,
            tuple(t.track_id for t in tracks),
        )


def _selected_tracks(
    report: AgentFrameReport, tracks: Sequence[ObjectTrack]
) -> tuple[str, ...]:
    return tuple(
        t.track_id for t in tracks if any(r == report.report_id for r, _ in t.members)
    )


@dataclass(frozen=True)
class LatestReportPolicy(_Baseline):
    version: str = "latest-report-v0"

    def _select(
        self, reports: Sequence[AgentFrameReport], tracks: Sequence[ObjectTrack]
    ) -> tuple[Action, str, Sequence[AgentFrameReport], tuple[str, ...]]:
        return (
            Action.CLOSE,
            "latest_report",
            reports[-1:],
            _selected_tracks(reports[-1], tracks),
        )


@dataclass(frozen=True)
class FirstReportPolicy(_Baseline):
    version: str = "first-report-wins-v0"

    def _select(
        self, reports: Sequence[AgentFrameReport], tracks: Sequence[ObjectTrack]
    ) -> tuple[Action, str, Sequence[AgentFrameReport], tuple[str, ...]]:
        return (
            Action.CLOSE,
            "first_report",
            reports[:1],
            _selected_tracks(reports[0], tracks),
        )


@dataclass(frozen=True)
class MajorityVotePolicy(_Baseline):
    version: str = "majority-vote-v0"

    def _select(
        self, reports: Sequence[AgentFrameReport], tracks: Sequence[ObjectTrack]
    ) -> tuple[Action, str, Sequence[AgentFrameReport], tuple[str, ...]]:
        voters = set({r.source_id: r.report_id for r in reports}.values())
        votes = {t.track_id: len({r for r, _ in t.members} & voters) for t in tracks}
        confirmed = tuple(
            t.track_id for t in tracks if votes[t.track_id] * 2 > len(voters)
        )
        tied = any(count * 2 == len(voters) for count in votes.values())
        action = Action.VERIFY if tied else Action.CLOSE
        return action, "majority_tie" if tied else "majority_vote", reports, confirmed


@dataclass(frozen=True)
class AlwaysVerifyPolicy(_Baseline):
    version: str = "always-verify-v0"

    def _select(
        self, reports: Sequence[AgentFrameReport], tracks: Sequence[ObjectTrack]
    ) -> tuple[Action, str, Sequence[AgentFrameReport], tuple[str, ...]]:
        return Action.VERIFY, "always_verify", reports, ()


@dataclass(frozen=True)
class NeverVerifyPolicy(_Baseline):
    version: str = "never-verify-v0"
