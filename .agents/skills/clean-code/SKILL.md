---
name: clean-code
description: Enforce PEP8, Uncle Bob's Clean Code, SOLID, KISS, DRY, and YAGNI. Applies self-explanatory code standards, guard clauses, type annotations, pathlib.Path relative resolution, and comment guidelines ("code tells WHAT, comments tell WHY"). Use whenever refactoring, reviewing code quality, or implementing software modules.
---

<role_definition>
Quality and craftsmanship specialist. Refine software modules to the highest standards of readability, maintainability, efficiency, and modularity.
</role_definition>

<universal_coding_standards>
### 1. Relative & Environment-Agnostic Filepaths (`pathlib.Path`)
Never use absolute drive paths (`C:\...`), home shortcuts (`~`), or string concatenation (`os.path.join` / `"./dir/" + name`). Always use `pathlib.Path` resolved relative to `__file__` or project root.
- **Good**: `from pathlib import Path; config_path: Path = Path(__file__).parent / "config.json"; data_path: Path = Path("./data") / filename`

### 2. Structural Spacing (PEP 8)
- 2 newlines (1 blank line) between `import` statements and top-level variables/functions.
- 3 newlines (2 blank lines) between separate top-level function definitions.
- 2 newlines (1 blank line) between consecutive, independent `if` blocks.

### 3. Explaining Variables for Complex Boolean Logic
Extract compound or non-obvious boolean expressions into descriptive boolean variables before `if` statements.
- **Good**: `has_pro_access: bool = user.has_access and not user.is_banned and (user.tier == "pro" or user.is_trial); if has_pro_access: grant_access()`

### 4. Control Flow & Guard Clauses
Avoid deep indentation and nested `if/else` ladders. Validate preconditions early and return or raise immediately to keep primary logic unindented.
- **Good**: `def process(user: User | None) -> Data | None: if not user or not user.is_active: return None; return user.data`

### 5. Exception Handling & Error Propagation
Never swallow exceptions with bare `except:` or silent `pass` blocks. Catch specific expected classes (`FileNotFoundError`, `ValueError`) with actionable diagnostic messages.

### 6. Explicit Type Annotations
Annotate all parameter types and explicit return types (`-> None` for void functions).

### 7. Variable Reuse & No Redundant Aliasing
Never create temporary variables that merely alias input parameters without transformation. Reassign input parameters directly for simple in-place transformations (e.g. string stripping/regex).

### 8. Concise Single-Line Comments
"Code tells WHAT, Comments tell WHY." Never state the obvious. Do not use decorative ASCII banner boxes (`# ---...`). Use single-line comments directly above target blocks explaining trade-offs or rationale.

### 9. Windows Subprocess Execution
Never use `asyncio.create_subprocess_exec` on Windows due to ProactorEventLoop limitations. Run blocking subprocess commands via `subprocess.run` inside `asyncio.to_thread`.
</universal_coding_standards>
