"""Scenario parsing, deterministic resolution, and replay serialization."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .contracts import ClaimEvent, EvidenceClaim, TickEvent, TraceEvent
from .policy import BeliefSnapshot, FixedRulePolicy, ResolutionPolicy

ScenarioEvent = ClaimEvent | TickEvent


@dataclass(frozen=True)
class Scenario:
    """Validated synthetic input and its independently authored oracle."""

    scenario_id: str
    policy_version: str
    events: tuple[ScenarioEvent, ...]
    expected_trace: list[dict[str, object]]


@dataclass(frozen=True)
class ResolutionResult:
    """Replayable execution output for one scenario."""

    trace: tuple[TraceEvent, ...]

    def contract_trace(self) -> list[dict[str, object]]:
        """Return records compared directly with the independent oracle."""
        return [item.to_contract_record() for item in self.trace]

    def to_jsonl(self) -> str:
        """Serialize a canonical, newline-terminated causal trace."""
        records = (
            json.dumps(item.to_contract_record(), sort_keys=True) for item in self.trace
        )
        return "".join(f"{record}\n" for record in records)


def load_scenario(source: Path | Mapping[str, Any]) -> Scenario:
    """Load and validate a scenario without exposing its truth metadata."""
    payload = _load_payload(source)
    scenario_id = _required_string(payload, "scenario_id")
    policy_version = _required_string(payload, "policy_version")
    raw_events = _required_list(payload, "events")
    expected_trace = _required_list(payload, "expected_trace")
    events = tuple(_parse_event(raw_event) for raw_event in raw_events)
    _validate_sequences(events)
    return Scenario(
        scenario_id=scenario_id,
        policy_version=policy_version,
        events=events,
        expected_trace=expected_trace,
    )


def run_scenario(
    scenario: Scenario,
    policy: ResolutionPolicy | None = None,
) -> ResolutionResult:
    """Resolve one synthetic event stream with no access to simulator truth."""
    active_policy = policy or FixedRulePolicy(version=scenario.policy_version)
    if active_policy.version != scenario.policy_version:
        message = f"policy version {active_policy.version!r} does not match scenario"
        raise ValueError(message)

    status: str | None = None
    positive_claims: list[EvidenceClaim] = []
    negative_claims: list[EvidenceClaim] = []
    trace: list[TraceEvent] = []

    for event in scenario.events:
        snapshot = BeliefSnapshot(
            status=status,
            positive_claims=tuple(positive_claims),
            negative_claims=tuple(negative_claims),
        )
        if isinstance(event, TickEvent):
            decision = active_policy.resolve_tick(snapshot, event.at)
            if decision is None:
                continue
        else:
            decision = active_policy.resolve_claim(snapshot, event.claim)
            if event.claim.assertion == "present":
                positive_claims.append(event.claim)
            else:
                negative_claims.append(event.claim)

        status = decision.belief_status
        trace.append(
            TraceEvent(
                event_id=event.event_id,
                belief_status=decision.belief_status,
                action=decision.action,
                reason_code=decision.reason_code,
                policy_version=active_policy.version,
                causal_claim_ids=decision.causal_claim_ids,
            )
        )

    return ResolutionResult(trace=tuple(trace))


def _load_payload(source: Path | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(source, Path):
        return json.loads(source.read_text(encoding="utf-8"))
    return source


def _parse_event(raw_event: object) -> ScenarioEvent:
    if not isinstance(raw_event, Mapping):
        raise TypeError("scenario event must be an object")

    event_id = _required_string(raw_event, "event_id")
    sequence = _required_integer(raw_event, "sequence")
    event_type = _required_string(raw_event, "event_type")
    if event_type == "tick":
        return TickEvent(
            event_id=event_id, sequence=sequence, at=_parse_timestamp(raw_event, "at")
        )
    if event_type != "claim":
        raise ValueError(f"unsupported event_type: {event_type}")

    raw_claim = raw_event.get("claim")
    if not isinstance(raw_claim, Mapping):
        raise TypeError("claim event must include a claim object")
    return ClaimEvent(
        event_id=event_id,
        sequence=sequence,
        claim=EvidenceClaim(
            claim_id=_required_string(raw_claim, "claim_id"),
            source_id=_required_string(raw_claim, "source_id"),
            observed_at=_parse_timestamp(raw_claim, "observed_at"),
            assertion=_one_of(raw_claim, "assertion", {"present", "absent"}),
            role=_one_of(raw_claim, "role", {"report", "verification"}),
            confidence=_required_confidence(raw_claim),
            entity_id=_required_string(raw_claim, "entity_id"),
            frame_id=_required_string(raw_claim, "frame_id"),
            pose_ref=_required_string(raw_claim, "pose_ref"),
            model_version=_required_string(raw_claim, "model_version"),
            artifact_ref=_required_string(raw_claim, "artifact_ref"),
        ),
    )


def _validate_sequences(events: tuple[ScenarioEvent, ...]) -> None:
    sequences = [event.sequence for event in events]
    if sequences != list(range(1, len(events) + 1)):
        raise ValueError("event sequences must start at 1 and increase without gaps")


def _required_string(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _required_list(
    payload: Mapping[str, Any], field_name: str
) -> list[dict[str, object]]:
    value = payload.get(field_name)
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list")
    return value


def _required_integer(payload: Mapping[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _required_confidence(payload: Mapping[str, Any]) -> float:
    value = payload.get("confidence")
    if not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError("confidence must be between 0 and 1")
    return float(value)


def _one_of(payload: Mapping[str, Any], field_name: str, choices: set[str]) -> str:
    value = _required_string(payload, field_name)
    if value not in choices:
        raise ValueError(f"{field_name} must be one of {sorted(choices)}")
    return value


def _parse_timestamp(payload: Mapping[str, Any], field_name: str) -> datetime:
    value = _required_string(payload, field_name)
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be ISO-8601") from error
