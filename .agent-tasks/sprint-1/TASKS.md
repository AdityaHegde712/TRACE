# Sprint 1 Task Ledger

1. [x] Freeze scope, policy defaults, and four oracle cases.
   - Acceptance: `PLAN.md` and `DECISIONS.md` state executable boundaries.
2. [x] Preserve pre-Sprint-1 materials as planning/research documents.
   - Acceptance: historical documents are categorized, links are repaired, and
     protected TRACE files remain unread and unchanged.
3. [x] Bootstrap Python 3.12 and `uv` virtual environment.
   - Acceptance: `uv run pytest` executes from the repository root.
4. [x] RED: write immutable contract tests and golden oracle fixtures.
   - Acceptance: tests fail because the package is absent or behavior is missing.
5. [x] GREEN: implement contracts, fixed policy, resolver, trace, replay, and CLI.
   - Acceptance: all spec tests pass without test changes.
6. [x] REFACTOR: isolate policy and serialization concerns; add integration smoke.
   - Acceptance: formatter and full test suite pass; each CLI scenario emits
     deterministic JSONL trace and oracle report.

## Immediate Next Action

Review the staged Sprint 1 changes, then create the milestone commit on the
feature branch.
