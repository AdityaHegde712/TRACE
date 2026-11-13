# M1 Contracts (m1-v0)

**Status:** Interfaces frozen at `m1-v0` on 2026-11-12. M0 (advisor approval) is complete.
**Owner:** Aditya. Only he changes these; every change bumps `CONTRACT_VERSION` in `src/trace_contracts/__init__.py`.
**Code:** `src/trace_contracts/`. **Tests:** `tests/contracts/test_contracts.py`.

M1 is split in two so Tracks B and C can start now:

| Part | What | Status |
| --- | --- | --- |
| M1 interfaces | The records and ports below | Frozen (`m1-v0`) |
| M1 research answer | Which dependence estimator, sample-size floors, acceptance thresholds | Track A, in progress; plugs in behind the frozen ports |

## The hazard we measure

A **false "all clear"**: both agents miss the same real object, so the task closes as if nothing is there. This is what the spike measured (shared misses, ratio 1.671). Metrics count it as `false_clearance`.

## Who writes and reads what

| Record | File | Written by | Read by |
| --- | --- | --- | --- |
| Scenario manifest entry | `scenario.py` | Rishi (Track B) | Pranav, Aditya |
| Agent frame report | `observations.py` | Rishi (Track B detection adapter) | Policies, Pranav's harness |
| Ground truth | `truth.py` | Rishi (Track B), beside the reports, never inside | Pranav's scorer only |
| Policy decision | `policy.py` | Every policy | Pranav's harness |
| Result row | `results.py` | Pranav (Track C) | Aditya (interpretation) |

Every on-disk record carries a `schema` field. Readers reject an unknown one.

## 1. Correlation channels and scenario matrix (Track B builds to this)

Three physical channels are set at render time:

| Channel | Levels |
| --- | --- |
| Viewpoint disparity | narrow 15°, medium 60°, wide 120° |
| Occluder | none, static |
| Illumination (CARLA preset) | ClearNoon, CloudySunset, WetNoon |

That is 18 render cells (`render_cells()`). The fourth channel, **detector pairing**, is applied after rendering over the same frames: YOLO11m/YOLO11m, RT-DETR-L/RT-DETR-L, YOLO11m/RT-DETR-L. That gives 54 sweep cells (`sweep_cells()`). Cell ids are stable strings, for example `narrow-none-ClearNoon-homogeneous_yolo`.

Scenes per cell is a generator parameter. Its minimum is part of the Track A research answer; build the generator so it is configurable.

## 2. Agent frame report (what an agent emits)

One report per agent per camera frame: ids, `observed_at`, `arrived_at` (so late and out-of-order delivery can be tested), camera pose, detector name, and the detections (label, confidence, pixel box). **A report with zero detections is valid and important:** the agent looked and saw nothing.

## 3. Ground truth (evaluator-only, AD-001)

`TruthObject`: object id, scene, which agent's view it is visible in, label, box. A test fails if any agent-side module imports `truth.py`.

## 4. Association port

`Association.associate(reports) -> ObjectTrack[]` groups detections from different agents that are the same object. The rule (e.g. projecting boxes with camera poses) is Track A research; the port is frozen.

## 5. Dependence estimator port

`DependenceEstimator.estimate(DependenceQuery) -> DependenceEstimate`.
- The query has the two agents, their detectors, observable covariates, and optional object features. Object features are optional because a missed object has none.
- The estimate has the inflation ratio with its interval and each agent's miss rate. `joint_miss_probability()` = ratio × miss_A × miss_B.
- `IndependenceEstimator` is the naive baseline: ratio always 1.0.

## 6. Resolution policy port (Track C baselines implement this)

`ResolutionPolicy.decide(task_id, reports, estimator) -> TaskDecision`. A task is one scene's inspection. Actions: `close` (accept the confirmed objects as complete), `verify` (pay a re-observation), `wait`. Decisions carry causal report ids and policy and estimator versions (AD-003).

Track C baselines: latest-report, first-report-wins, unweighted majority vote, always-verify, all behind this port.

## 7. Result row (Track C emits, Track A interprets)

One row per run × policy × scene, fixed column order in `RESULT_COLUMNS`. Counts are stored and rates derived: co-visible objects, confirmed, missed at close, false confirmations, verification actions, `false_clearance`, and the trace SHA-256.

## Code locations

| Track | New code goes in |
| --- | --- |
| B (Rishi) | `src/scenario_gen/` (generalizes `src/spike_dependence/scene_matrix.py` and the render/detect adapters) |
| C (Pranav) | `src/sweep/` (harness, scorer) and `src/baselines/` (policies) |
| A (Aditya) | `src/trace_contracts/` (contracts), `src/evidence_resolution/` (resolver, estimators) |

## Not frozen yet (Track A research answer)

1. Which estimator is used: the per-agent-pair estimator with observable covariates is the current lead. Claim streams alone cannot reveal a shared miss, so some labelled signal is required.
2. Whether ground truth may fit frozen estimator parameters on a disjoint training split (needs an AD-001 ruling).
3. The cross-agent association rule.
4. Sample-size floors and acceptance thresholds.
