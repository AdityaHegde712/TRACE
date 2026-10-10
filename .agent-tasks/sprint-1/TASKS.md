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
7. [x] Commit the Sprint 1 prototype.
   - Evidence: `4dc33ce feat: add evidence resolution prototype`.
   - Acceptance: source, fixtures, documents, and zero-context handoff are
     preserved on `feature/evidence-resolution-sprint-1`.

## Immediate Next Action

Owner reviews `4dc33ce` and decides whether to merge the feature branch through
the project remote-review workflow.
