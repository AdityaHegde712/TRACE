# Appendix: Existing Prototype Verification and Implementation Status

**Companion to:** `PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md`  
**Purpose:** Technical record of working codebases, test verification, and reproducibility guarantees to support proposal feasibility.  
**Date:** 2026-11-03  

This appendix documents the two software artifacts currently functioning within the repository: the deterministic evidence-resolution core (Sprint 1 prototype) and the empirical dependence measurement harness (`src/spike_dependence/`).

---

## 1. Evidence Resolution Prototype

The repository includes a working, deterministic evidence-resolution prototype developed during Sprint 1. It resolves streaming categorical road-blockage claims into discrete belief states and task actions while generating an append-only cryptographic causal trace. It does not introduce external robotics simulators or task planners; it validates the software contracts governing evidence aggregation.

| Architecture Component | Implementation State | Verification Method |
| :--- | :--- | :--- |
| **Typed Contracts** | Fully implemented (`ClaimRecord`, `PolicyDecision`, `TraceEvent`) | Enforced via Pydantic / dataclasses |
| **Policy Interface** | Fully implemented (`ResolutionPolicy` abstraction) | Pluggable baseline implementations |
| **Deterministic Replay** | Fully implemented (JSONL event streaming and trace hashing) | Bit-exact replay verified across runs |
| **CLI Runner** | Fully implemented (`evidence_resolution` module) | Automated scenario execution |
| **Oracle Fixtures** | 4 scenarios (supported, conflicting, false, stale) | Separately authored from policy logic |
| **Test Suite** | 22 tests passing | `python -m pytest tests/spec tests/integration` |

### Verification Evidence (Reproduced 2026-10-28)

The following verification suite was directly reproduced:

| Verification Target | Command Executed | Observed Result |
| :--- | :--- | :--- |
| **Test Suite** | `python -m pytest -q` | **22 passed** in 31.9s |
| **Static Analysis** | `python -m ruff check src tests` | All checks passed (zero violations) |
| **Code Formatting** | `python -m ruff format --check src tests` | 9 files cleanly formatted |
| **Oracle Verification** | CLI execution on `conflicting` scenario | `"oracle_passed": true` |
| **Cryptographic Determinism** | Two independent runs, SHA-256 trace hash | Bit-identical: `FCF942A0...2227D441` |

Replay stability is verified: two independent invocations produce byte-identical traces matching the recorded repository hash at commit `e2fe036`.

---

## 2. Empirical Dependence Measurement Harness

To execute the dependence spike reported in Section 4 of the proposal, an end-to-end sensor and evaluation harness was implemented under `src/spike_dependence/` supported by 131 tests:

| Module | Operational Capability | Verification Status |
| :--- | :--- | :--- |
| **`render_scenes.py`** | Headless CARLA 0.9.16 scene generation and multi-view rendering | Verified: 54 scenes, 108 RGB frames, 0 failures |
| **`artifacts_io.py`** | Strict JSON schema serialization for ground truth and detections | Verified: schema-enforced I/O |
| **`detect.py`** | Multi-detector inference runner (YOLO11m and RT-DETR-L) | Verified: 108 frames detected in 19s total |
| **`scoring.py`** | 2D bounding-box ground-truth association and visibility tracking | Verified: evaluated on 448 co-visible objects |
| **`double_fault.py`** | Double-fault calculation and 5,000-iteration bootstrap CI estimator | Verified: bootstrap bounds validated |
| **`stratify.py`** | Scenario knob and apparent-size tercile stratification | Verified: size terciles evaluated |
| **`contrast.py`** | Heterogeneous detector evaluation and paired difference bootstrapping | Verified: paired bootstrap interval validated |
| **`causation_cli.py`** | Within-scene and cross-scene permutation null testing | Verified: permutation null returns 0.999 |

---

## 3. Reproduction Commands

To reproduce the prototype and test suites from a clean development environment:

```powershell
# Core development dependencies
uv sync --dev

# Execute complete test suite (153 tests passing)
uv run pytest

# Execute static analysis and format checks
uv run ruff check src tests
uv run ruff format --check src tests

# Execute oracle scenario evaluation
uv run python -m evidence_resolution `
  --scenario tests/fixtures/oracle/conflicting.json `
  --output-dir artifacts/manual/conflicting
```

---

## 4. Architectural Relationship to Proposed Work

The Sprint 1 prototype carries no frozen status (architectural constraint AD-005 was withdrawn on 2026-10-27). Its purpose is to demonstrate that the policy seam, causal trace recording, and deterministic replay operate correctly.

In the proposed research program, the evidence-resolution engine will be expanded:
1. **Temporal Watermarking:** Extending the claim record to carry arrival timestamps alongside observation timestamps, enabling the out-of-order watermark reconciliation required for Track A.
2. **Dependence-Aware Resolution:** Replacing the heuristic baseline with the formal dependence-discounted policy while maintaining the identical `ResolutionPolicy` seam.
