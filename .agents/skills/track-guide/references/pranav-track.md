# Track C: Pranav (harness, baselines, release)

## Read first
In `docs/planning/TEAM_RESPONSIBILITIES.md`: "Roles", "Track C", "Milestones" (M1 to M5), "Dependencies and handoffs", "Risks and fallbacks" (item 5).
In `docs/planning/PROPOSAL_CORRELATED_FAILURE.md`: "The problem" and "What we propose to build".

## Scope
Owns C1 (sweep harness, re-runnable by one command), C2 (baselines: latest-report, first-report-wins, unweighted majority vote, always-verify), C3 (README, Apache-2.0 LICENSE, installable package, one-command quickstart), C4 (visual demo of two agents agreeing and being wrong together), C5 (camera-to-claim adapter docs).

C2 starts immediately after M1 and depends on nothing else. New code goes in new modules; Aditya confirms paths at M1, so ask before creating top-level folders.

## Off limits (read only)
`src/evidence_resolution/contracts.py`, `policy.py`, `scenario.py`, `tests/spec/`, and the definitions of the measures, channels, matrix, and thresholds. Baselines implement the existing `ResolutionPolicy` interface; read it, do not change it. Requests go through `.agent-tasks/TASKS.md` "Handoffs".

## Rules that matter most
- You hand Aditya **result tables, never conclusions.** Interpretation is Track A.
- Every reported number must trace to a retained run. Keep every run's output.
- No GPL code in the core (MultiUAV-Plat is GPL-3.0). Check a dependency's license before adding it.
- Done-check for C3: a fresh clone runs the quickstart with one command.
- C4 and C5 are the schedule buffer; Aditya may reassign work to them.

## Starter prompts
1. `Read the Track C section and tell me what C2 asks me to build, with the four baselines explained in plain English. Do not write code yet.`
2. `Help me set up the project (uv sync, uv run pytest), then show me the ResolutionPolicy interface and explain what a policy must return.`
3. `Write the failing test for the first-report-wins baseline using the existing scenario fixtures, run it, and show me why it fails.`
