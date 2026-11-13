"""Grouping detections from different agents into candidate real objects.

Only the interface is frozen. The rule itself (for example projecting boxes
into the world frame using camera poses) is Track A research and may change
without changing this contract.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from trace_contracts.observations import AgentFrameReport


@dataclass(frozen=True)
class ObjectTrack:
    """Detections believed to be the same object, as (report_id, detection_id) pairs."""

    track_id: str
    members: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.members:
            raise ValueError("an object track needs at least one detection")


@runtime_checkable
class Association(Protocol):
    """Groups one task's detections into object tracks without ground truth."""

    version: str

    def associate(self, reports: Sequence[AgentFrameReport]) -> tuple[ObjectTrack, ...]:
        """Return the tracks for one task's reports."""
        ...
