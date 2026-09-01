# AGENTS.md

<authority>
## Scope & Precedence
Applies to **all work in this project** unless a higher-priority instruction explicitly conflicts. Explicit user instructions override project defaults (except higher-priority instructions/mandatory safeguards). Do not silently skip required skills, validation stages, approval gates, or workflows.
</authority>

<universal_directives>
## Universal Directives

### 1. Environment & Secret Safety
Never inspect, edit, read, or search `.env` files. Always reference `.env.example`.

### 2. Background Process Discipline
Never run long-running processes (>60s) synchronously. Launch detached with process redirection and continuous logging:
- **Bash**: `> task.log 2>&1 & echo $! > task.pid`
- **PowerShell**: `Start-Process -FilePath 'cmd.exe' -ArgumentList '/c ... > task.log 2>&1' -WindowStyle Hidden -PassThru`
Inspect progress via incremental log tailing. Ensure scripts flush output (`flush=True`) continuously.

### 3. File Encoding & Integrity
Enforce UTF-8 encoding across all written files, scripts, and logs with LF line endings.

### 4. Stateless Session Continuity (.agent-tasks)
Treat every turn as potentially the last turn of the session. Continuously update state files after every completed step to enable zero-context subagent handoff:
- `PLAN.md`: System architecture, active execution phase, dependency chains, affected file paths, strict exit criteria.
- `DECISIONS.md`: Immutable technical decisions, architectural tradeoffs, rejected alternatives, operational constraints.
- `TASKS.md`: Atomic numbered checklist (`[ ]`, `[/]`, `[x]`), blockers, explicit acceptance criteria, immediate next action.
</universal_directives>

<development>
## Test-Driven Development — Mandatory
All implementation MUST use **TDD** via project-level `tdd-dev` skill:
1. **RED**: Write/update test demonstrating required behavior; verify failure for expected reason.
2. **GREEN**: Implement smallest correct change to pass.
3. **REFACTOR**: Improve structure without changing behavior; rerun relevant tests.

**Rules**: No production implementation before tests; bug fixes require reproducing regression test first; preserve existing passing behavior; run narrowest tests during iteration, then broader validation. If TDD cannot reasonably apply, state **what, why, and how correctness will be validated** before proceeding.

### Clean Coding
For any coding tasks, learn the code craftsmanship, PEP 8, guard clauses, typing, and refactoring standards, by invoking the project-level `clean-code` skill.
</development>

<execution_visibility>
## Verbose, Traceable Execution
Development work must be understandable by a junior developer. Communicate observable actions, decisions, evidence, and results (no private chain-of-thought).
- **Explain**: What is changing/tested, Where (file/component/path), Why (connection to behavior), How (architectural fit), What validation is performed, and What happened (failures/assumptions).
- **Progression**: (1) State immediate goal -> (2) Identify files -> (3) Explain test & proven behavior -> (4) Report expected RED -> (5) Explain change -> (6) Report GREEN -> (7) Explain refactoring -> (8) Report broader validation. Avoid trivial command flood.
- **Completion Summary**: Added (new files/tests/APIs/deps), Modified (changed files/behavior & why), Deleted (removed files/behavior & why), Validation (checks run & results), Remaining (limitations/follow-ups). Never claim unverified success.
</execution_visibility>

<git>
## Git Workflow
For Git operations or repo/branch state work, invoke project-level `git-workflow` skill (sprint/feature startup, branch creation, rebasing, committing, resuming interrupted work, continuing after remote merges, or changing Git state).
</git>

<writing>
## Reports & Humanization Gate
When a **report** is requested, check if user specified whether output should be humanized/stripped of LLM patterns:
- If requested: Invoke project-level `humanize-doc` skill.
- If explicitly unnecessary: Proceed without `humanize-doc`.
- If unspecified: **Ask before starting** whether they want it humanized/stripped of LLM patterns (blocking prerequisite before research/outline/drafting).
</writing>

<research>
## Research & Implementation References
For research, external reference gathering, literature/tech investigation, or implementation research, invoke project-level `research` skill.
> **Retrieved information takes precedence over pretrained knowledge.** Do not use model memory to override retrieved/validated evidence.
</research>

<ui_ux>
## UI/UX
For any UI/UX decisions (app type, framework, platform, scope, new design or modification), invoke project-level `ui-ux` skill. Subject to required user interview, rendered prototype, screenshot, iteration, and approval workflow.
</ui_ux>

<slides>
## Slide Decks
For presentation/slide-deck creation, redesign, or material visual modification, invoke project-level `slide-deck` skill (HTML-first visual prototyping, rendering, screenshot, iteration, and approval workflow before finalization).
</slides>

<decision_style>
## Prior Decision Style Inheritance
If available, read `PROJECT_DECISION_STYLE.md` from project root before substantive decisions. Applies across implementation, architecture, tradeoffs, and tooling; overrides conflicting global/default preferences by intent. Do not override higher-priority instructions, safety rules, or explicit user commands.
</decision_style>
