"""Simulator ground truth. EVALUATOR-ONLY (AD-001).

Nothing an agent, estimator, association rule, or policy runs may import this
module; a test enforces it. Track B writes these records beside the reports,
never inside them, and Track C's scorer reads them.
"""

from __future__ import annotations

from dataclasses import dataclass

from trace_contracts.observations import BoundingBox


@dataclass(frozen=True)
class TruthObject:
    """One real object as one viewpoint sees it.

    Visibility is per viewpoint, because only objects both agents could see
    are scored (SD-008).
    """

    object_id: str
    scene_id: str
    source_id: str
    label: str
    box: BoundingBox
