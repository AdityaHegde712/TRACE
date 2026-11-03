# Appendix: Prototype Status

**Companion to** `PROPOSAL_CORRELATED_FAILURE.md`. One page. This records what currently runs, so the proposal's feasibility claim can be checked rather than taken on trust.

## What exists

A deterministic evidence-resolution prototype, built in a single working session. It resolves synthetic road-blockage claims into a belief status, a requested task action, and an append-only causal trace. No drone simulator, routing, task allocator, perception model, or external dataset is involved. It demonstrates a contract, not a capability.

| Component | State |
| --- | --- |
| Typed claim, event, and trace records | Implemented |
| `ResolutionPolicy` interface with a fixed-rule implementation | Implemented |
| Scenario loading, resolution, and JSONL replay | Implemented |
| Command-line entry point | Implemented |
| Oracle scenarios (supported, false, stale, conflicting) | Four, separately authored from the policy |
| Test suite | 22 tests, all passing |

## What has been verified

All of the following was **reproduced on 2026-10-28**, not quoted from an earlier
record:

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest -q` | **22 passed** in 31.9s |
| Lint | `python -m ruff check src tests` | All checks passed |
| Format | `python -m ruff format --check src tests` | 9 files already formatted |
| Oracle | CLI run of the `conflicting` scenario | `"oracle_passed": true` |
| Determinism | Two independent CLI runs, SHA-256 of each trace | Identical: `FCF942A0...2227D441` |

The determinism result is the meaningful one: two separate invocations produced
byte-identical traces, and the hash matches the value recorded at commit
`e2fe036`, so replay stability holds across both runs and time.

**Two corrections to earlier records.** The project handoff described a
permission error blocking test reruns and a suite of 7 tests. Neither still
holds: the environment runs cleanly, and the suite has since grown to 22 tests
across `tests/spec/` and `tests/integration/`. Earlier documents describing this
evidence as retained rather than reproduced are superseded by this appendix.

## Running it

```powershell
uv sync --dev
uv run python -m evidence_resolution `
  --scenario tests/fixtures/oracle/conflicting.json `
  --output-dir artifacts/manual/conflicting
```

Writes `conflicting.trace.jsonl` and `conflicting.oracle.json`. A passing report proves only that the fixed resolver matches a separately authored fixture; simulator truth remains evaluator-only metadata throughout.

```powershell
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
```

## Status under the proposed framing

This prototype is **not** treated as a frozen foundation. The constraint that previously protected it (AD-005) was withdrawn on 2026-10-27. Its code, fixtures, and test assertions may be discarded and rebuilt.

What it establishes is that the design works end to end: claims resolve to actions, decisions retain their causal claim identifiers, replay is deterministic, and the policy seam allows a different resolver to be substituted without touching the event, trace, or CLI contracts.

What it cannot support, and why a rebuild is expected:

- Its claim record carries one observation timestamp and no arrival time, so it cannot represent late or out-of-order delivery. The proposed study must control for arrival order to avoid confounding it with dependence effects.
- Its four scenarios exercise support, contradiction, and staleness. None exercises correlation between agents, which is the phenomenon under study.

Both gaps are properties of the original scope rather than defects. The prototype answered the question it was built to answer.
