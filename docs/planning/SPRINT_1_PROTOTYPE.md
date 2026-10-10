# Sprint 1 Prototype: Evidence Resolution

## Purpose

This local prototype resolves synthetic road-blockage claims into a belief status,
a requested task action, and an append-only causal trace. It demonstrates a
contract only: no drone simulator, routing, task allocator, perception model, or
external dataset is involved.

## Run a Scenario

```powershell
uv sync --dev
uv run python -m evidence_resolution `
  --scenario tests/fixtures/oracle/conflicting.json `
  --output-dir artifacts/manual/conflicting
```

The command writes `conflicting.trace.jsonl` and `conflicting.oracle.json`. A
passing report proves only that the fixed resolver matches the separately
authored fixture; simulator truth remains evaluator-only metadata.

## Validate

```powershell
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
```

The frozen oracle fixtures cover supported, false, stale, and conflicting
reports. A later policy can replace `FixedRulePolicy` through `ResolutionPolicy`
without changing the event, trace, or CLI contracts.
