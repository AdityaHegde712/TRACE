# M1 Research Answer (Track A, draft v0)

**Status:** Draft for owner review, 2026-11-12. Plugs in behind the frozen `m1-v0` interfaces (`M1_CONTRACTS.md`); nothing here changes them.

| Item | State | Where |
| --- | --- | --- |
| 1. Dependence estimator | v0 built and checked on spike data; weather covariate is the next step | Sections 1, 6 |
| 2. Cross-agent association | v0 implemented and tested on synthetic geometry | `src/evidence_resolution/association.py` |
| 3. Sample-size floor | Measured from spike data | Section 3 |
| 4. Acceptance thresholds | Approved 2026-11-12 (curve-based) | Section 4 |
| 5. Policy skeleton | v0 runs end to end through the ports | `src/evidence_resolution/miss_risk_policy.py` |

## 1. Dependence estimator

**Finding:** shared misses cannot be estimated from claim streams alone. When both agents miss an object, neither emits a claim, so the both-missed cell is never observed. This is the two-list capture-recapture problem: every dependence value fits the observed counts equally well. Supporting source: Albert & Dodd (JASA 2008) state that these quantities "are identifiable with multiple tests and an assumed model for the dependence between these tests", and that "gold standard evaluation on even a small percentage of cases greatly lowers the bias".

Consequences:
- Per-object-pair estimation online is ruled out. The spike's 71% object-instance share can only be reached through observable object features (label, apparent size), never object identity.
- Audits must sample **random regions**. Verification triggered by claims inspects only claimed objects and never sees a double miss.

**Decided design (owner-approved 2026-11-12):** per agent pair × observable covariates (detector pair, illumination, viewpoint angle from poses, apparent size). The model is fitted offline on a labelled training split disjoint from evaluation scenes, then recalibrated online from random-region audits, with the offline fit as the prior.

**AD-001 clarification (owner-approved 2026-11-12):** ground truth about the scene being decided never reaches the policy. Statistics fitted on separate, labelled training scenes may, the same way the detector itself is trained on labels. Three guardrails:

1. Split by scene, fixed by seed and recorded in the manifest. No scene is in both the training and the evaluation set.
2. The fitted estimator is frozen and versioned before any evaluation run (AD-003).
3. A shift test is reported: fit on two illumination presets, evaluate on the third, to show the calibration generalizes.

Random-region audits from an uninformed prior are kept as a secondary ablation (the "no labels at all" setting), not as the main method.

## 2. Association v0

Each detection's bottom-centre pixel is projected onto the ground plane using the camera pose. Same-label detections from different agents within 4 m are merged greedily by nearest pair, with at most one detection per agent per track. The camera setup (800×600, 90° FOV, 14 m above ground) is configuration, not contract.

**Unmeasured against ground truth.** The spike did not save camera poses, so accuracy can only be measured once Track B records poses in the agent frame reports (already required by `m1-v0`). Known error source: a vehicle's bottom edge seen from opposite sides projects to ground points a few metres apart.

## 3. Sample-size floor (measured)

Method: resample the spike's own 448 co-visible objects at n = 100, 200, and 448 (2,000 draws each). Measure the standard error of log(ratio), which scales as 1/√n. Then compute n for 80% power at a two-sided 5% test. Reproduce with `uv run python scripts/sample_size_floor.py artifacts/spike/raw`.

| Detector pair | Spike ratio | SE at n=448 | n for ratio 1.3 | n for ratio 1.5 |
| --- | --- | --- | --- | --- |
| YOLO11m / YOLO11m | 1.671 | 0.056 | 167 | 70 |
| YOLO11m / RT-DETR-L | 1.697 | 0.076 | 309 | 130 |
| RT-DETR-L / RT-DETR-L | 2.311 | 0.086 | 400 | 168 |

**Floor:** 400 co-visible objects per sweep cell, driven by the worst pair. At about 8.3 co-visible objects per scene, that is **50 scenes per render cell, 900 scenes total**. The spike rendered 54 scenes in 36 s and ran detection over 108 frames in 12 s, so this is minutes, not hours.

Note: the RT-DETR/RT-DETR inflation ratio (2.31) is higher than YOLO's and is not reported in the proposal, which compared pairs by φ. This needs checking before it is cited.

## 4. Acceptance thresholds (proposed)

1. **Dependence present in a cell:** the 95% bootstrap interval's lower bound is above 1.0 (existing rule SD-006).
2. **Minimum detectable dependence:** ratio 1.3 at 80% power. Cells below the 400-object floor are reported as underpowered, never as "no dependence".
3. **RQ3 success, at equal verification cost:** sweep each policy's risk tolerance across its full range and plot false-clearance rate against verification rate. The dependence-aware curve must lie below the naive curve. At matched verification rates, the paired bootstrap 95% interval on the false-clearance difference must exclude 0.
4. **No fixed verification budget.** Verifying everything trivially removes false clearances, so policies are only compared at equal verification cost (item 3). Always-verify and never-verify mark the two ends of the curve.

## 5. Policy skeleton v0

`MissRiskPolicy` is one policy that is naive or dependence-aware depending on the estimator it is given:
- `WAIT` until two agents have reported.
- `VERIFY` if any object track is seen by one agent only.
- Otherwise it computes the shared-miss risk = ratio × miss_A × miss_B, then picks `VERIFY` above the tolerance and `CLOSE` below it.

With `IndependenceEstimator` the risk is zero, so it always closes. That is exactly the assumption under test.

v0 limitation: the risk is per task, not per unseen location, and the case of more than two agents uses the first two.

## 6. Estimator v0: first check on spike data

`src/evidence_resolution/calibration.py` (9 tests). It splits scenes into practice and exam sets by seed, counts each detector pair's misses on practice scenes, freezes those numbers under a fingerprint version, and checks them on exam scenes. v0 is keyed by detector pair only. Reproduce with `uv run python scripts/fit_estimator.py artifacts/spike/raw`.

**Random split (27 practice / 27 exam scenes): it works.** The predicted rate of both agents missing the same object is close to what happened, and far closer than the naive prediction.

| Detector pair | Observed both-miss | Calibrated prediction | Naive prediction |
| --- | --- | --- | --- |
| YOLO / YOLO | 0.223 | 0.205 | 0.131 |
| RT-DETR / RT-DETR | 0.118 | 0.114 | 0.048 |
| YOLO / RT-DETR | 0.126 | 0.143 | 0.082 |

**Shift test (one weather held out entirely): it fails.** For example, with ClearNoon held out, YOLO/YOLO predicts 0.273 against an observed 0.103. The cause is measured: each detector's own miss rate roughly doubles between weathers (YOLO 0.21 in ClearNoon, 0.46 in CloudySunset), while the fail-together ratio is steadier (YOLO 1.55 to 1.76).

What this means:
1. **Next depth step:** make miss rates depend on weather, which agents can observe. Every weather appears in the practice scenes of the real sweep, so this is fittable.
2. **A weather the estimator never saw is a known limit.** The estimator should refuse it (it already refuses unknown detector pairs) rather than guess.
3. These are 54-scene dry-run numbers. The real check uses Track B's 900-scene corpus.
