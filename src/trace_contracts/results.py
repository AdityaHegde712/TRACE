"""One result row per (run, policy, scene): what the sweep harness emits.

Track C writes these rows and never interprets them; Track A does. Counts are
stored, rates are derived, so tables re-aggregate without rounding loss.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from trace_contracts import CONTRACT_VERSION
from trace_contracts._schema import require_schema

RESULT_SCHEMA: str = "trace.result.m1-v0"

RESULT_COLUMNS: tuple[str, ...] = (
    "schema",
    "contract_version",
    "run_id",
    "policy_version",
    "estimator_version",
    "scene_id",
    "cell_id",
    "action",
    "co_visible_objects",
    "objects_confirmed",
    "objects_missed_at_close",
    "false_confirmations",
    "verification_actions",
    "false_clearance",
    "trace_sha256",
)


@dataclass(frozen=True)
class RunResult:
    """Scored outcome of one policy on one scene.

    - co_visible_objects: real objects both agents could see (SD-008).
    - objects_missed_at_close: of those, ones not confirmed when the task closed.
    - false_confirmations: confirmed tracks matching no real object.
    - verification_actions: re-observations requested (verification cost).
    """

    run_id: str
    policy_version: str
    estimator_version: str
    scene_id: str
    cell_id: str
    action: str
    co_visible_objects: int
    objects_confirmed: int
    objects_missed_at_close: int
    false_confirmations: int
    verification_actions: int
    trace_sha256: str

    @property
    def false_clearance(self) -> bool:
        """The hazard: the task closed while a real object went unconfirmed."""
        return self.action == "close" and self.objects_missed_at_close > 0

    def to_record(self) -> dict[str, Any]:
        values = {
            "schema": RESULT_SCHEMA,
            "contract_version": CONTRACT_VERSION,
            **{name: getattr(self, name) for name in RESULT_COLUMNS[2:-2]},
            "false_clearance": self.false_clearance,
            "trace_sha256": self.trace_sha256,
        }
        return {name: values[name] for name in RESULT_COLUMNS}


def result_from_dict(payload: dict[str, Any]) -> RunResult:
    require_schema(payload, RESULT_SCHEMA, "result")
    stored = {
        name: payload[name]
        for name in RESULT_COLUMNS
        if name not in ("schema", "contract_version", "false_clearance")
    }
    return RunResult(**stored)
