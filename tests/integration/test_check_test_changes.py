"""Behavior of the pre-commit guard that blocks edits to existing test assertions."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT: Path = (
    Path(__file__).resolve().parents[2]
    / ".agents"
    / "skills"
    / "git-workflow"
    / "scripts"
    / "check_test_changes.py"
)

BASE_TEST = (
    "import pytest\n\n\n"
    "@pytest.mark.parametrize('value', [1, 2])\n"
    "def test_total(value: int) -> None:\n"
    "    assert value > 0\n"
    "    assert value < 10\n"
)


def git(repo: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=repo, check=True, capture_output=True)


def write(repo: Path, relative: str, text: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_guard(repo: Path, allow: str | None = None) -> subprocess.CompletedProcess[str]:
    environment = {
        key: value for key, value in os.environ.items() if key != "ALLOW_TEST_CHANGE"
    }
    if allow is not None:
        environment["ALLOW_TEST_CHANGE"] = allow
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    write(tmp_path, "tests/test_sample.py", BASE_TEST)
    write(tmp_path, "tests/fixtures/case.json", '{\n  "a": 1\n}\n')
    write(tmp_path, "src/module.py", "VALUE = 1\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "test: baseline")
    return tmp_path


def stage(repo: Path, relative: str, text: str) -> None:
    write(repo, relative, text)
    git(repo, "add", relative)


def test_new_test_file_passes(repo: Path) -> None:
    stage(repo, "tests/test_new.py", "def test_x() -> None:\n    assert True\n")
    assert run_guard(repo).returncode == 0


def test_added_assertion_passes(repo: Path) -> None:
    stage(repo, "tests/test_sample.py", BASE_TEST + "    assert value != 5\n")
    assert run_guard(repo).returncode == 0


def test_removed_assertion_is_blocked_and_names_the_test(repo: Path) -> None:
    stage(
        repo, "tests/test_sample.py", BASE_TEST.replace("    assert value < 10\n", "")
    )
    result = run_guard(repo)
    assert result.returncode == 1
    assert "test_total" in result.stdout + result.stderr


def test_weakened_assertion_is_blocked(repo: Path) -> None:
    stage(repo, "tests/test_sample.py", BASE_TEST.replace("value < 10", "value < 1000"))
    assert run_guard(repo).returncode == 1


def test_deleted_test_file_is_blocked(repo: Path) -> None:
    git(repo, "rm", "-q", "tests/test_sample.py")
    assert run_guard(repo).returncode == 1


def test_removed_parametrize_case_is_blocked(repo: Path) -> None:
    stage(repo, "tests/test_sample.py", BASE_TEST.replace("[1, 2]", "[1]"))
    assert run_guard(repo).returncode == 1


def test_added_parametrize_case_passes(repo: Path) -> None:
    stage(repo, "tests/test_sample.py", BASE_TEST.replace("[1, 2]", "[1, 2, 3]"))
    assert run_guard(repo).returncode == 0


def test_changed_fixture_value_is_blocked(repo: Path) -> None:
    stage(repo, "tests/fixtures/case.json", '{\n  "a": 2\n}\n')
    assert run_guard(repo).returncode == 1


def test_added_fixture_key_passes(repo: Path) -> None:
    stage(repo, "tests/fixtures/case.json", '{\n  "a": 1,\n  "b": 2\n}\n')
    assert run_guard(repo).returncode == 0


def test_changes_outside_tests_are_ignored(repo: Path) -> None:
    stage(repo, "src/module.py", "VALUE = 2\n")
    assert run_guard(repo).returncode == 0


def test_override_with_reason_lets_the_commit_through(repo: Path) -> None:
    stage(
        repo, "tests/test_sample.py", BASE_TEST.replace("    assert value < 10\n", "")
    )
    result = run_guard(repo, allow="spec changed per Aditya")
    assert result.returncode == 0
    assert "spec changed per Aditya" in result.stdout + result.stderr


def test_override_of_zero_does_not_count(repo: Path) -> None:
    stage(
        repo, "tests/test_sample.py", BASE_TEST.replace("    assert value < 10\n", "")
    )
    assert run_guard(repo, allow="0").returncode == 1
