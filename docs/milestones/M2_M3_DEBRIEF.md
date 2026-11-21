# M2 and M3 Debrief for Dr. Kaikai Liu

Date: 2026-11-20. Authors: the TRACE team. Scope: milestones M2 (900-scene corpus) and M3 (calibration and policy sweep).

## 1. Verdict

**Good news on the measurement, bad news on the decision rule.**

- **Good:** independence fails across 900 physical scenes. Two agents miss the same object 1.80 to 2.52 times as often as independence predicts. A calibration fitted on 450 scenes predicts the joint miss rate on unseen scenes and unseen illuminations, to within 0.025.
- **Bad:** the decision experiment shows no benefit from dependence awareness. The calibrated policy was evaluated and sweeps only four operating points. At equal verification cost it closes no fewer unsafe tasks than random choice.
- **What decides the next step:** the measurement is publishable as it stands. The decision-rule claim stops at "unconditional trust is costly". A task-level estimator is needed before any claim of benefit.

## 2. Core numbers

### Table 1: practice ratio and exam joint-miss rate (random split, 450 practice / 450 exam scenes, 4,068 co-visible exam objects)

| Pairing | Ratio rho [95% CI] | Observed | Calibrated | Naive (independence) |
| --- | --- | --- | --- | --- |
| YOLO / YOLO | 1.80 [1.73, 1.87] | 0.241 | 0.238 | 0.133 |
| RT-DETR / RT-DETR | 2.52 [2.38, 2.67] | 0.106 | 0.110 | 0.044 |
| YOLO / RT-DETR | 1.99 [1.90, 2.08] | 0.141 | 0.148 | 0.074 |

The naive prediction sits 45 to 58% below the observed rate. The calibrated prediction is within 0.007 of it for all three pairings.

### Table 2: shift test (one illumination held out; 600 practice, 300 exam scenes)

| Held out | Pairing | Observed | Calibrated | Naive |
| --- | --- | --- | --- | --- |
| ClearNoon | YOLO / YOLO | 0.237 | 0.241 | 0.135 |
| | RT-DETR / RT-DETR | 0.117 | 0.104 | 0.043 |
| | YOLO / RT-DETR | 0.146 | 0.143 | 0.075 |
| CloudySunset | YOLO / YOLO | 0.255 | 0.232 | 0.130 |
| | RT-DETR / RT-DETR | 0.113 | 0.106 | 0.043 |
| | YOLO / RT-DETR | 0.154 | 0.139 | 0.072 |
| WetNoon | YOLO / YOLO | 0.228 | 0.246 | 0.134 |
| | RT-DETR / RT-DETR | 0.095 | 0.115 | 0.045 |
| | YOLO / RT-DETR | 0.133 | 0.150 | 0.075 |

The calibrated prediction stays within 0.025 in all nine cases and beats the naive one in all nine. The naive prediction is 41 to 63% low.

### Table 3: policy comparison over 2,700 tasks

| Rule | False clearance | Rate | Missed objects | Verified |
| --- | --- | --- | --- | --- |
| never-verify | 1,798 | 66.6% | 3,970 | 0% |
| first-report-wins | 2,362 | 87.5% | 7,702 | 0% |
| latest-report | 2,172 | 80.4% | 6,084 | 0% |
| majority-vote | 61 | 2.3% | 122 | 97.4% |
| miss-risk v0 (independence estimator) | 61 | 2.3% | 122 | 97.4% |
| always-verify | 0 | 0% | 0 | 100% |

Majority-vote and miss-risk v0 are the same rule here. Both verify exactly when a track has a single source.

### Calibrated tolerance sweep (13 tolerances, 0.01 to 0.50)

| Tolerance | Verified | False clearance | Tasks closed (unsafe) | Unsafe if closed at random |
| --- | --- | --- | --- | --- |
| 0.10 or less | 100% | 0% | 0 | 0 |
| 0.12 | 99.3% | 0.6% | 18 (15) | 15.5 |
| 0.15 to 0.20 | 98.6% | 1.2% | 38 (32) | 32.6 |
| 0.25 or more | 97.4% | 2.3% | 71 (61) | 61 |

The single-source test sends 97.4% of tasks to verification at every tolerance. Only 71 tasks reach the risk test. The estimator ranks detector pairings, not tasks, so it cannot pick safer tasks inside a pairing.

## 3. Engineering accomplishments

- 900 CARLA scenes in Town10HD: 18 render cells (3 viewpoint disparities, static and no occluder, 3 illuminations), 50 scenes each.
- 3,600 detector inferences (900 scenes, 2 cameras, 2 detectors) on one RTX 5060 (8 GB) with no VRAM crash. CARLA is stopped before detection to free the GPU.
- Frozen M1 contracts, five baseline policies, watermarked report reconciliation with permutation tests, ground-plane association, a calibrated estimator and the miss-risk policy.
- A sweep harness with replayable, hash-checked decision traces.
- 341 tests pass and ruff is clean.
- Reproduction commands are in the README. A scene inspector (`scripts/inspect_scene.py`) prints any scene's truth, detections, tracks and every policy's decision.

## 4. Preprint status

- `paper/` holds a 7-page preprint. It compiles with zero errors, zero overfull boxes and zero undefined references.
- `paper/arxiv_submission.tar.gz` holds the arXiv bundle. It compiles from a fresh extract.
- Three figures are generated from the corpus results by scripts in `scripts/`. Tests check the figure data against the paper's tables.
- The paper is ready to send for your review. One validity threat should be settled before arXiv (see below).

**Open validity threat.** In the double-fault example (scene-0515) both cameras sit inside tree canopy. The viewpoint check in the renderer casts rays against static map geometry only, so foliage is not caught. Some of the measured double-fault excess may come from this simulator effect and not from detector behavior. We have not measured how many scenes are affected.

## 5. Next steps (M4)

1. **Decide the foliage threat** (~1 day): count scenes whose cameras are under foliage and recompute the ratios without them. This changes the headline only if the ratios fall near 1.
2. **Release packaging** (~2 days): tag the repository, publish the corpus manifest and results, choose the license (Apache-2.0 is planned).
3. **Interactive demonstration** (~3 days): use the scene inspector and the double-fault figure to walk through single scenes.
4. **Decision-rule follow-up** (optional): test an estimator keyed on illumination and object size. Without it the paper claims no decision-level benefit.

Decision needed from you: submit the measurement-only claim now, or wait for the foliage check.
