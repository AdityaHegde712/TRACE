"""Schema markers shared by every on-disk contract record."""

from __future__ import annotations

from typing import Any


def require_schema(payload: dict[str, Any], expected: str, kind: str) -> None:
    """Refuse a payload written under another schema; silent drift corrupts results."""
    if payload.get("schema") != expected:
        raise ValueError(
            f"unsupported {kind} schema {payload.get('schema')!r}; expected {expected!r}"
        )
