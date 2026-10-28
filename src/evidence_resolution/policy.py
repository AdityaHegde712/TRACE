"""Replaceable policy interface and Sprint 1 fixed-rule policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from .contracts import EvidenceClaim


@dataclass(frozen=True)
class BeliefSnapshot:
    """The minimal prior state a policy needs to resolve the next event."""

    status: str | None
    positive_claims: tuple[EvidenceClaim, ...]
    negative_claims: tuple[EvidenceClaim, ...]


@dataclass(frozen=True)
class PolicyDecision:
    """A policy outcome with stable reason text for replay and evaluation."""

    belief_status: str
    action: str
    reason_code: str
    causal_claim_ids: tuple[str, ...]


class ResolutionPolicy(Protocol):
    """Port for a future weighted or learned evidence-resolution policy."""

    version: str

    def resolve_claim(
        self,
        snapshot: BeliefSnapshot,
        claim: EvidenceClaim,
    ) -> PolicyDecision:
        """Resolve one normalized claim against a prior belief snapshot."""

    def resolve_tick(
        self,
        snapshot: BeliefSnapshot,
        at: datetime,
    ) -> PolicyDecision | None:
        """Resolve staleness after a deterministic scenario clock advance."""


@dataclass(frozen=True)
class FixedRulePolicy:
    """Small, inspectable baseline policy for Sprint 1."""

    version: str = "fixed-v1"
    freshness_window: timedelta = timedelta(minutes=5)

    def resolve_claim(
        self,
        snapshot: BeliefSnapshot,
        claim: EvidenceClaim,
    ) -> PolicyDecision:
        """Map a claim to the frozen Sprint 1 decision table."""
        prior_claim_ids = tuple(item.claim_id for item in snapshot.positive_claims)
        has_independent_positive = any(
            item.source_id != claim.source_id for item in snapshot.positive_claims
        )

        if claim.role == "verification" and claim.assertion == "absent":
            return PolicyDecision(
                belief_status="invalid",
                action="close",
                reason_code="verifier_disproves_blockage",
                causal_claim_ids=prior_claim_ids + (claim.claim_id,),
            )

        if claim.assertion == "present" and has_independent_positive:
            return PolicyDecision(
                belief_status="verified",
                action="close",
                reason_code="independent_confirmation_verifies_blockage",
                causal_claim_ids=prior_claim_ids + (claim.claim_id,),
            )

        has_positive_report = bool(snapshot.positive_claims)
        if claim.assertion == "absent" and has_positive_report:
            return PolicyDecision(
                belief_status="disputed",
                action="reassign",
                reason_code="fresh_reports_conflict",
                causal_claim_ids=prior_claim_ids + (claim.claim_id,),
            )

        if claim.assertion == "present":
            return PolicyDecision(
                belief_status="proposed",
                action="create",
                reason_code="positive_report_requires_verification",
                causal_claim_ids=(claim.claim_id,),
            )

        return PolicyDecision(
            belief_status=snapshot.status or "invalid",
            action="verify",
            reason_code="negative_report_requires_context",
            causal_claim_ids=(claim.claim_id,),
        )

    def resolve_tick(
        self,
        snapshot: BeliefSnapshot,
        at: datetime,
    ) -> PolicyDecision | None:
        """Request reassignment when an unverified positive report expires."""
        if snapshot.status != "proposed" or not snapshot.positive_claims:
            return None

        newest_positive = max(item.observed_at for item in snapshot.positive_claims)
        if at - newest_positive < self.freshness_window:
            return None

        return PolicyDecision(
            belief_status="stale",
            action="reassign",
            reason_code="verification_window_expired",
            causal_claim_ids=tuple(item.claim_id for item in snapshot.positive_claims),
        )
