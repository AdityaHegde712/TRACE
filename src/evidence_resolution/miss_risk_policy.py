"""Miss-risk policy v0: close a task only when a shared miss is unlikely enough.

The same policy is the naive baseline or the dependence-aware treatment depending
on the estimator it is given. With `IndependenceEstimator` the shared-miss risk is
taken as zero, so two agreeing agents always close the task (the assumption under
test). With a calibrated estimator the risk is ratio x miss_A x miss_B, and the
policy pays for a verification when that risk exceeds the tolerance.

v0 handles two agents per task; with more, it uses the first two source ids.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from evidence_resolution.association import PoseProjectionAssociation
from trace_contracts.estimation import DependenceEstimator, DependenceQuery
from trace_contracts.observations import AgentFrameReport
from trace_contracts.policy import Action, TaskDecision


@dataclass(frozen=True)
class MissRiskPolicy:
    association: PoseProjectionAssociation
    miss_risk_tolerance: float = 0.05
    version: str = "miss-risk-v0"

    def decide(
        self,
        task_id: str,
        reports: Sequence[AgentFrameReport],
        estimator: DependenceEstimator,
    ) -> TaskDecision:
        report_ids = tuple(sorted(r.report_id for r in reports))
        detector_of = {r.source_id: r.detector for r in reports}
        sources = sorted(detector_of)

        def decision(
            action: Action, reason: str, confirmed: tuple[str, ...] = ()
        ) -> TaskDecision:
            return TaskDecision(
                task_id=task_id,
                action=action,
                reason_code=reason,
                causal_report_ids=report_ids,
                confirmed_track_ids=confirmed,
                policy_version=self.version,
                estimator_version=estimator.version,
            )

        if len(sources) < 2:
            return decision(Action.WAIT, "awaiting_second_agent")

        source_of_report = {r.report_id: r.source_id for r in reports}
        tracks = self.association.associate(reports)
        confirmed = tuple(
            track.track_id
            for track in tracks
            if len({source_of_report[report_id] for report_id, _ in track.members}) >= 2
        )
        if len(confirmed) < len(tracks):
            return decision(Action.VERIFY, "single_source_track", confirmed)

        pair = (sources[0], sources[1])
        estimate = estimator.estimate(
            DependenceQuery(
                source_ids=pair, detectors=(detector_of[pair[0]], detector_of[pair[1]])
            )
        )
        if estimate.joint_miss_probability() > self.miss_risk_tolerance:
            return decision(
                Action.VERIFY, "shared_miss_risk_above_tolerance", confirmed
            )
        return decision(Action.CLOSE, "shared_miss_risk_within_tolerance", confirmed)
