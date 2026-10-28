"""Behavior of the research quote validator used to verify citations."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT: Path = (
    Path(__file__).resolve().parents[2]
    / ".agents"
    / "skills"
    / "research"
    / "scripts"
    / "validate_quote.py"
)


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_quote", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quote_found_across_line_break_reports_line_number(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("first line\nthe quick brown\nfox jumps\n", encoding="utf-8")

    found, _, line = load_validator().validate_in_file(source, "quick brown fox")

    assert found is True
    assert line == 2


def test_missing_quote_is_reported_not_found(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("nothing relevant here\n", encoding="utf-8")

    found, message, line = load_validator().validate_in_file(source, "absent phrase")

    assert (found, line) == (False, None)
    assert "not found" in message.lower()


def test_unreadable_file_is_reported_as_failure(tmp_path: Path) -> None:
    found, message, line = load_validator().validate_in_file(
        tmp_path / "does_not_exist.txt", "anything"
    )

    assert (found, line) == (False, None)
    assert message.startswith("Failed to read file")
