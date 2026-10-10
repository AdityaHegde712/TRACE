# Sprint 1 Plan: Deterministic Evidence Resolution

## Objective

Deliver a runnable, simulation-data-based prototype that resolves evidence claims
about one road-blockage region into a revisable belief, a requested task action,
and a replayable causal trace. The prototype is correct when it conforms to a
separately authored oracle for four fixed scenarios.

## Boundaries

- In scope: synthetic JSONL-like event streams, fixed policy rules, belief
  transitions, requested actions, JSONL traces, deterministic replay, CLI, and
  contract/integration tests.
- Out of scope: Gazebo/PX4, ROS 2, camera models, learned perception, task
  allocation, navigation, UI, external datasets, and performance claims.
- Simulator truth is evaluator-only metadata. The resolver must never receive it.

## Architecture

`scenario events -> claim validation -> belief snapshot -> ResolutionPolicy ->
action request + TraceEvent -> JSONL trace -> replay/oracle evaluation`

The core is a Python 3.12 package under `src/evidence_resolution`. A policy is
replaceable through a typed interface; Sprint 1 supplies the fixed-rule policy.

## Execution Order

1. Install Python 3.12 with `uv`; create `.venv`, `pyproject.toml`, and pytest
   development configuration.
2. Write frozen `tests/spec` fixtures and assertions; run RED before source code.
3. Implement the smallest typed contracts, resolver, fixed policy, trace writer,
   replay function, and CLI to pass the tests.
4. Add integration coverage for CLI artifacts and replay determinism.
5. Run formatting, the full test suite, and a reduced end-to-end smoke for every
   scenario.

## Exit Criteria

- Four oracle fixtures pass exactly: supported, false, stale, and conflicting.
- Every action has causal links to its incoming event, belief transition, and
  policy version.
- Replaying a fixed scenario produces byte-identical JSONL output.
- The CLI writes a trace and oracle report without using simulator truth as input.

## Validation Evidence

- RED: `uv run --no-sync pytest` failed with `ModuleNotFoundError` before the
  package existed.
- GREEN/REFACTOR: `uv run --no-sync pytest` passed 7 tests on Python 3.12.13.
- Quality: Ruff lint and format checks passed for `src` and `tests`.
- Smoke: all four CLI scenarios wrote passing oracle reports. A repeated
  conflicting trace had SHA-256
  `FCF942A0F0F475EABCE8C6BBD7DB561B5A7AC3472D3C61F4387174D32227D441`.
