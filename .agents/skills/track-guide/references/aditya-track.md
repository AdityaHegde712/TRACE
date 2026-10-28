# Track A: Aditya (project lead)

## Read first
In `docs/planning/TEAM_RESPONSIBILITIES.md`: "Roles", "Track A", "Milestones", "Dependencies and handoffs", "Risks and fallbacks".
Also `docs/planning/DECISIONS.md` and `docs/planning/PROPOSAL_CORRELATED_FAILURE.md`.

## Scope
Owns measurement definitions (A1, A2), deterministic replay under out-of-order evidence (A3), resolver and naive-independence baseline (A4), evaluation (A5), and every frozen contract.

Only person who may change a frozen definition. Reviews every pull request, including the "Test changes" section.

Owned code today: `src/evidence_resolution/contracts.py`, `policy.py`, `scenario.py`, and `tests/spec/`.

## Duties to the team
- Do not let M1 (Nov 10) slip: two tracks idle without it.
- Never edit Rishi's corpus; send defects back to him.
- Take result tables from Pranav and do the interpreting.
- Update the "Current gate" line in `track-guide/SKILL.md` when M0 or M1 passes.

## Starter prompts
1. `Read .agent-tasks/TASKS.md and tell me the next unblocked task in Track A, with a time estimate.`
2. `Draft the dependence inflation factor definition for A1: estimator, minimum sample size, and failure cases. Do not write code yet.`
3. `Review the open pull requests' "Test changes" sections and summarize anything that touches tests/spec/.`
