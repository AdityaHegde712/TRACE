"""Typed public records for evidence resolution and causal replay."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EvidenceClaim:
    """A normalized observation claim emitted by one simulated source."""

    claim_id: str
    source_id: str
    observed_at: datetime
    assertion: str
    role: str
    confidence: float
    entity_id: str
    frame_id: str
    pose_ref: str
    model_version: str
    artifact_ref: str


@dataclass(frozen=True)
class ClaimEvent:
    """A scenario event containing one evidence claim."""

    event_id: str
    sequence: int
    claim: EvidenceClaim


@dataclass(frozen=True)
class TickEvent:
    """A deterministic scenario clock advance used to assess staleness."""

    event_id: str
    sequence: int
    at: datetime


@dataclass(frozen=True)
class TraceEvent:
    """The observable policy decision and its direct evidence lineage."""

    event_id: str
    belief_status: str
    action: str
    reason_code: str
    policy_version: str
    causal_claim_ids: tuple[str, ...]

    def to_contract_record(self) -> dict[str, object]:
        """Return the stable, reviewer-facing trace representation."""
        return {
            "event_id": self.event_id,
            "belief_status": self.belief_status,
            "action": self.action,
            "reason_code": self.reason_code,
            "policy_version": self.policy_version,
            "causal_claim_ids": list(self.causal_claim_ids),
        }
