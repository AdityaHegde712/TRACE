"""Pre-commit guard: block staged edits that remove or weaken existing test assertions.

Adding tests, assertions, parametrize cases, or fixture data is allowed. Deleting or
changing existing ones needs a human to confirm, then `ALLOW_TEST_CHANGE="<reason>"`.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from collections import Counter
from typing import Any

TEST_ROOT: str = "tests/"
ASSERT_CALL_NAMES: set[str] = {"raises", "warns"}

ESCALATION_MESSAGE: str = """
COMMIT BLOCKED: existing test assertions or fixtures would change.

AGENT: do not retry, rewrite, or bypass this. Follow "Test change escalation" in
.agents/skills/git-workflow/SKILL.md. If you changed the test this session, tell the
user what changed and why, and ask them to confirm. If you did not make the change,
flag it as an issue and ask the user to confirm anyway.

HUMAN: if the change is intended, commit again with the reason, then record it in the
pull request "Test changes" section:
    ALLOW_TEST_CHANGE="<why this test changed>" git commit ...
"""


def run_git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def staged_changes() -> list[tuple[str, str]]:
    """Return (status, path) pairs for staged files under tests/; renames count as delete + add."""
    raw: str = run_git("diff", "--cached", "--name-status", "--no-renames", "-z")
    fields: list[str] = [field for field in raw.split("\0") if field]
    pairs: list[tuple[str, str]] = list(zip(fields[0::2], fields[1::2]))
    return [(status, path) for status, path in pairs if path.startswith(TEST_ROOT)]


def dotted_name(node: ast.expr) -> str:
    if isinstance(node, ast.Attribute):
        return f"{dotted_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Name):
        return node.id
    return ""


def is_assertion_call(node: ast.Call) -> bool:
    name: str = dotted_name(node.func)
    last_part: str = name.rsplit(".", 1)[-1]
    return last_part in ASSERT_CALL_NAMES or last_part.startswith("assert")


def parametrize_cases(function: ast.FunctionDef | ast.AsyncFunctionDef) -> Counter[str]:
    cases: Counter[str] = Counter()
    for decorator in function.decorator_list:
        is_parametrize = (
            isinstance(decorator, ast.Call)
            and dotted_name(decorator.func).endswith("parametrize")
            and len(decorator.args) >= 2
            and isinstance(decorator.args[1], (ast.List, ast.Tuple))
        )
        if not is_parametrize:
            continue
        names: str = ast.dump(decorator.args[0])
        for element in decorator.args[1].elts:
            cases[f"parametrize {names} -> {ast.dump(element)}"] += 1
    return cases


def collect_contract_items(source: str) -> dict[str, Counter[str]]:
    """Map each function (or the module) to the assertions and cases it contains."""
    tree: ast.Module = ast.parse(source)
    items: dict[str, Counter[str]] = {"<module>": Counter()}

    def visit(node: ast.AST, scope: str, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified: str = f"{prefix}{child.name}"
                items[qualified] = parametrize_cases(child)
                visit(child, qualified, f"{qualified}.")
                continue
            if isinstance(child, ast.ClassDef):
                visit(child, scope, f"{prefix}{child.name}.")
                continue
            is_assertion = isinstance(child, ast.Assert) or (
                isinstance(child, ast.Call) and is_assertion_call(child)
            )
            if is_assertion:
                items[scope][ast.dump(child)] += 1
            visit(child, scope, prefix)

    visit(tree, "<module>", "")
    return items


def python_violations(path: str, old: str, new: str) -> list[str]:
    try:
        new_items = collect_contract_items(new)
    except SyntaxError as error:
        return [f"{path}: staged file does not parse ({error.msg})"]
    old_items = collect_contract_items(old)
    problems: list[str] = []
    for scope, old_counter in old_items.items():
        if not old_counter:
            continue
        if scope not in new_items:
            problems.append(f"{path}: {scope} was removed or renamed")
            continue
        missing: Counter[str] = old_counter - new_items[scope]
        if missing:
            problems.append(
                f"{path}: {scope} lost or changed {sum(missing.values())} assertion(s) or case(s)"
            )
    return problems


def json_preserves(old: Any, new: Any) -> bool:
    if isinstance(old, dict):
        return isinstance(new, dict) and all(
            key in new and json_preserves(value, new[key]) for key, value in old.items()
        )
    if isinstance(old, list):
        return (
            isinstance(new, list)
            and len(new) >= len(old)
            and all(json_preserves(a, b) for a, b in zip(old, new))
        )
    return old == new


def text_violations(path: str, old: str, new: str) -> list[str]:
    if path.endswith(".json"):
        try:
            return (
                []
                if json_preserves(json.loads(old), json.loads(new))
                else [f"{path}: existing fixture data changed"]
            )
        except json.JSONDecodeError:
            return [f"{path}: fixture is not valid JSON before or after the change"]
    new_lines: Counter[str] = Counter(new.splitlines())
    removed: Counter[str] = Counter(old.splitlines()) - new_lines
    return (
        [f"{path}: {sum(removed.values())} existing line(s) removed or changed"]
        if removed
        else []
    )


def find_violations() -> list[str]:
    problems: list[str] = []
    for status, path in staged_changes():
        if status == "D":
            problems.append(f"{path}: test file deleted")
            continue
        if status != "M":
            continue
        old: str = run_git("show", f"HEAD:{path}")
        new: str = run_git("show", f":{path}")
        if path.endswith(".py"):
            problems.extend(python_violations(path, old, new))
        else:
            problems.extend(text_violations(path, old, new))
    return problems


def main() -> int:
    problems: list[str] = find_violations()
    if not problems:
        return 0

    reason: str = os.environ.get("ALLOW_TEST_CHANGE", "").strip()
    if reason and reason != "0":
        print(f"Test change approved. Reason: {reason}")
        print("Add this to the pull request 'Test changes' section:")
        print("\n".join(f"  - {problem}" for problem in problems))
        return 0

    print("\n".join(f"  - {problem}" for problem in problems))
    print(ESCALATION_MESSAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
