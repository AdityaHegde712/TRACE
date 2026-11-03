# AGENTS.md

<authority>
## Scope & Precedence
Applies to **all work in this project** unless a higher-priority instruction explicitly conflicts. Explicit user instructions override project defaults (except higher-priority instructions/mandatory safeguards). Do not silently skip required skills, validation stages, approval gates, or workflows.
</authority>

<session_start>
## Session Start
First action of every session: invoke `team-onboarding`, then `track-guide` (asks who is working, loads their track). Teammates may be new to the domain, to coding, and to agents: explain plainly, work in small steps, ask before risky actions.
</session_start>

<skill_routing>
## Skill Routing
| Need | Skill |
| --- | --- |
| Project primer, glossary, frozen decisions | `team-onboarding` |
| Who is working, track scope, starter prompts | `track-guide` |
| Writing or changing code behavior | `test-driven-development` + `clean-code` |
| Branches, commits, hooks, pull requests, merges | `git-workflow` |
| Research, literature, quick lookups | `research` (routes to full or condensed) |
| Report or doc prose | `humanize-report` |
| UI/UX design | `ui-ux` |
| Slide decks | `slide-deck` |
| Shrinking prompts/skills | `token-compressor` |
</skill_routing>

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
All implementation MUST use **TDD** via project-level `test-driven-development` skill:
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

<result_reporting>
## Reporting an Experimental Result — Verdict First

Applies whenever reporting a measurement, experiment, benchmark, spike, or any
finding the user must act on. It governs the shape of the message, never its
honesty: nothing here permits softening, omitting, or delaying a bad result.

### The required order
1. **Verdict, one sentence, plain words.** Did it work? Is it good news? Answer
   the question that was asked before anything else.
2. **What it means for the decision.** Does the work continue, change, or stop?
3. **The numbers.** The headline figure with its uncertainty. A table beats a
   paragraph.
4. **Caveats last, and only those that change an action.** Each caveat states
   the action it changes. A caveat that changes nothing is noise: drop it.

Never open with a caveat, a limitation, or a trade-off. Never make the user
read to the end to learn whether the result was good.

### Say good or bad plainly
If asked "is this good news", answer "good news" or "bad news" in the first
three words, then explain. Do not reply with a balanced survey of both sides.
A result that is genuinely mixed is reported as: what is good, what is bad,
which one decides the next step.

### Separate the result from the write-up
A measurement that holds but contradicts a sentence in a document is still a
good result. Say so in those terms: "the finding is solid; one sentence in X
needs changing." Do not let a documentation fix read like a failed experiment.

### The scoreboard
Close a substantial result with direct question-and-answer pairs:
- Does the effect exist? Yes/No + the number.
- Is it real or an artifact? What was done to check.
- Was the work worth it? Yes/No.
- Does anything have to change? The specific thing, or "nothing".

### Banned shapes
- Interleaved trade-offs, where every point is immediately qualified.
- Burying the verdict under methodology.
- Hedging a confirmed result ("appears to suggest" for something measured).
- More than five caveats. Rank them and cut.
- Restating the same limitation in several sections.

### Still mandatory
State uncertainty honestly and quantitatively. Report a negative result as
plainly as a positive one. Never claim a result that was not produced and
checked. Verdict-first is about ORDER, not about confidence inflation.
</result_reporting>

<git>
## Git Workflow
For Git operations or repo/branch state work, invoke project-level `git-workflow` skill (sprint/feature startup, branch creation, rebasing, committing, resuming interrupted work, continuing after remote merges, opening pull requests, or changing Git state). A commit blocked by the test-change hook must be escalated to the user, never bypassed.
</git>

<writing>
## Reports & Humanization Gate
When a **report** is requested, check if user specified whether output should be humanized/stripped of LLM patterns:
- If requested: Invoke project-level `humanize-report` skill.
- If explicitly unnecessary: Proceed without `humanize-report`.
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
