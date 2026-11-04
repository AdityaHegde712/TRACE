# Dependence-Aware Trust in Multi-Agent Visual Perception: Quantifying Correlated Failure and Restoring Decision Calibration

**Author:** Aditya Hegde  
**Advisor:** Dr. Kaikai Liu  
**Date:** 2026-11-03  
**Status:** Proposal for Advisor Review (Supercedes prior preliminary framings)  

---

## 1. Executive Summary & Research Questions

Multi-agent visual perception networks enable autonomous teams (e.g., unmanned aerial or ground vehicles) to achieve collective situational awareness beyond the field of view of any individual platform. When aggregating distributed detections to verify critical environmental states—such as roadway blockages or navigational obstacles—decision frameworks rely on multi-agent trust models to weigh and verify claims. Current state-of-the-art trust estimation methods, exemplified by the Multi-Agent Trust Estimator (MATE; Hallyburton & Pajic, 2025), fundamentally assume that observation errors between distinct agents are conditionally independent given the true environment. Under this assumption, agreement between multiple sources is interpreted as cumulative confirmation, accelerating task closures.

This proposal investigates the validity of this independence assumption in physical multi-agent perception, quantifies its breakdown across controlled physical channels, and develops a dependence-aware evidence-resolution policy to restore decision calibration. Through an empirical spike across 54 CARLA 0.9.16 simulation scenes encompassing 448 co-visible physical objects, we demonstrated that the conditional independence assumption fails substantially: agent pairs double-fault on the same physical object at an inflation ratio of **1.671** (95% bootstrap CI [1.500, 1.870]) relative to the rate predicted under independence. Confound controls and permutation null tests establish that this failure is causal (permutation null = 0.999), persists across apparent object size terciles, and decomposes into a 29% scene-wide effect and a 71% object-instance effect. Crucially, deploying heterogeneous detector architectures (YOLO11m paired with RT-DETR-L) reduces association only marginally (+0.0915 phi difference), leaving heterogeneous agents strongly correlated (phi = 0.2852, odds ratio ~ 4.0).

Based on these empirical findings, this research addresses three primary research questions:

1. **RQ1 (Empirical Characterization):** Across which physical, geometric, and architectural channels (object instance features, local occlusions, viewpoint disparity, ambient illumination, and model architectures) does perceptual error dependence concentrate, and how do these factors modulate joint failure rates?
2. **RQ2 (Online Dependence Estimation):** Can inter-agent perceptual error dependence be estimated online from streaming, categorical claim streams without ground truth access, and at what structural granularity (per-agent-pair versus per-object-pair) must the estimator operate?
3. **RQ3 (Downstream Task Decision Impact):** At what dependence thresholds does naive belief fusion induce unacceptable decision error (e.g., premature task closure on false positives), and can a dependence-aware evidence-discounting policy eliminate catastrophic agreement blindness while minimizing verification cost?

---

## 2. Problem Statement: The Unverified Independence Assumption

When an autonomous agent reports a detection (e.g., "road blockage present at coordinates $(x, y)$"), a distributed perception system must determine whether the claim warrants operational action. In safety-critical autonomy, a confirming report from a second platform is routinely treated as independent verification.

This inference is mathematically sound only if error processes across sensing platforms are statistically independent. In the reference architecture under study, as well as in the project's initial baseline prototype, this assumption is instantiated directly: differing source identifiers (`source_id_A != source_id_B`) are treated as evidence of statistical independence. A confirming report increments belief according to naive Bayesian updates or unweighted thresholding, triggering task closure:

```python
# Baseline evidence resolution logic (illustrative)
has_independent_positive = any(
    item.source_id != claim.source_id for item in snapshot.positive_claims
)
if claim.assertion == "present" and has_independent_positive:
    return PolicyDecision(belief_status="verified", action="close")
```

If both agents operate within the same physical environment, observe identical geometry, view through shared occluding obstacles, or employ models pretrained on overlapping feature distributions, their error distributions correlate. Under correlated failure, two agents agree and fail together. Consensus becomes a failure amplifier rather than a safeguard: confirmation bias is encoded into the fusion pipeline, producing high-confidence erroneous actions ("correlated agreement blindness") with negligible true informational gain. While accepted engineering constraints (e.g., AD-004 in this project) prescribe that repeated or correlated evidence must not be treated as independent, operational systems currently lack validated estimators to detect or mitigate this correlation.

---

## 3. Literature Context and the Empirical Gap

The assumption of conditional independence is pervasive across distributed sensor fusion and multi-agent systems, yet its validity in visual perception remains unverified.

### 3.1 The Baseline: MATE (Multi-Agent Trust Estimator)

The primary state-of-the-art baseline addressed in this work is MATE (Hallyburton & Pajic, arXiv:2503.04954, 2025). MATE formulates trust estimation across multi-agent perception networks via hidden Markov models, estimating online trust scalars per agent and per track to filter malicious or degraded sources. MATE explicitly anchors its theoretical optimality on conditional independence:

> "Optimal data fusion at AGG occurs when data fused from agents are uncorrelated. Agents observing the same environment from their own independent platform-level sensors will see similar state estimates but, **given the environment, their tracks will importantly not contain any correlations.**"

This premise exhibits three defining properties:
1. **Unverified Premise:** The claim is stated as an axiomatic modeling convenience rather than an empirically demonstrated finding.
2. **Acknowledged Open Question:** The authors explicitly identify this empirical gap, stating that future work must experimentally evaluate the independence assumption.
3. **Known Downstream Hazard:** The authors acknowledge the operational danger, noting that neglecting correlations causes network nodes to double-count evidence.

This assumption is not idiosyncratic to MATE. It appears as an uncalibrated scalar beta-factor in safety standard IEC 61508, as an explicit simplifying assumption in multi-sensor autonomous vehicle voter architectures, and as the default operational rule across distributed robotic teams.

### 3.2 Prior Art in Adjacent Literatures

A comprehensive investigation across eight adjacent research literatures (spanning 50 works, documented in `docs/research/DEPENDENCE_NOVELTY_SURVEY.md`) reveals that inter-source dependence has been studied extensively in non-perceptual domains:
- **Classifier Ensemble Diversity:** Kuncheva and Whitaker (2003) established statistical measures of ensemble diversity, formalizing the pairwise **double-fault measure** to capture the proportion of cases misclassified by two classifiers simultaneously.
- **Database Truth Discovery:** Dong, Berti-Équille, and Srivastava (PVLDB 2009) developed hidden Markov models to infer time-varying source copying and dependence from categorical claim streams without ground truth.
- **Crowdsourcing & Label Aggregation:** Models such as EBCC (Li et al., ICML 2019) model inter-annotator correlations to prevent consensus distortion.
- **LLM Multi-Agent Coordination:** Recent studies outside perception (*Smart Alone, Blind Together*, 2026; *Agent Behavioral Contracts II*, 2026) report that redundant LLM agents co-fail on up to 90% of tasks where either fails, proving that shared pretraining induces severe consensus failures.
- **Perception Redundancy on Single Platforms:** Gottschalk, Rottmann, and Saltagic (arXiv:2112.04758, 2021) evaluated redundant neural networks on synthetic 3D-MNIST rotations on a single compute platform, concluding that independence cannot be assumed even when different data sources are used.
- **Collaborative Perception Benchmarks:** A 2026 survey (*General Collaborative Intelligence*, arXiv:2609.22967) notes qualitatively that homogeneous agents with identical models and similar viewpoints are vulnerable to correlated failures. However, existing benchmarks (e.g., GCI-Bench, RCP-Bench, GLST, LUCIA) evaluate feature distances for adversary detection or average precision (AP) under corruptions; none measures inter-agent detection error correlation or connects it to task-lifecycle decisions.

### 3.3 The Core Research Gap

No prior work has experimentally measured inter-agent perceptual error correlation among distributed embodied agents situated in a shared 3D physical environment, decomposed that correlation into physical and architectural channels, or measured its direct operational cost on task decision policies. This project directly addresses that gap.

---

## 4. Preliminary Empirical Evidence: The Dependence Spike

To establish whether the conditional independence assumption fails in realistic visual perception settings, an end-to-end empirical spike was conducted using the CARLA 0.9.16 autonomous driving simulator and modern object detection architectures.

### 4.1 Experimental Protocol and Headline Result

The measurement protocol evaluated two autonomous agents observing shared physical road scenes from distinct spatial viewpoints. Fifty-four photorealistic scenes were rendered in CARLA Town10HD across diverse spawn coordinates, environmental conditions, and camera geometries. Two-dimensional ground-truth bounding boxes were extracted directly from the simulator. Visual detections were obtained using Ultralytics YOLO11m (IoU threshold 0.50, confidence threshold 0.25). Only objects visible to both agents were evaluated ($N = 448$ co-visible objects across 108 rendered frames). Ground truth was isolated strictly for offline evaluation and withheld from the perception pipeline (preserving project directive AD-001).

To quantify error dependence, we adopted the double-fault measure (Kuncheva & Whitaker, 2003), expressed as a **dependence inflation ratio**: the observed joint error rate (both agents failing on the same object) divided by the joint error rate predicted under conditional independence ($P(\text{Error}_A \cap \text{Error}_B) / [P(\text{Error}_A) \cdot P(\text{Error}_B)]$). A ratio of 1.0 denotes perfect independence; values above 1.0 indicate positive error correlation.

| Metric | Measured Value | Analysis / Significance |
| :--- | :--- | :--- |
| **Dependence Inflation Ratio** | **1.671** | Statistically significant inflation above independence |
| **95% Bootstrap Confidence Interval** | **[1.500, 1.870]** | 5,000 resamples; lower bound sits clear of 1.0 |
| **Observed Joint-Error Rate ($p_{11}$)** | **0.2143** | Empirical probability of simultaneous double-fault |
| **Independence Predicted Rate ($p_A \cdot p_B$)** | **0.1282** | Theoretical product of marginal error probabilities |
| **Agent A Marginal Error Rate ($p_A$)** | 0.3683 | 165 detection misses out of 448 visible objects |
| **Agent B Marginal Error Rate ($p_B$)** | 0.3482 | 156 detection misses out of 448 visible objects |
| **Sample Scope** | 54 scenes, 448 objects | Town10HD, 2 viewpoints per scene, 108 total frames |

The contingency table demonstrates that agent pairs double-faulted on 96 objects, compared to the 57.4 expected under statistical independence:

| Contingency Cell | Observed Count |
| :--- | :--- |
| **Both agents wrong ($e_A = 1, e_B = 1$)** | **96** |
| Only Agent A wrong ($e_A = 1, e_B = 0$) | 69 |
| Only Agent B wrong ($e_A = 0, e_B = 1$) | 60 |
| Neither agent wrong ($e_A = 0, e_B = 0$) | 223 |

### 4.2 Confound Analysis: Stratification by Apparent Object Size

A critical hypothesis is that the measured inflation could represent an artifact of shared object difficulty: an object that is small or distant in 3D space is inherently challenging for any detector. If shared difficulty fully accounted for the effect, conditioning on apparent object area would drive the stratum inflation ratios to 1.0.

Data were stratified into apparent-size terciles based on bounding-box pixel area. The dependence inflation ratio remained bounded above 1.0 across all three terciles:

| Apparent Size Stratum | Pixel Area Range ($px^2$) | Object Count ($n$) | Inflation Ratio | 95% Bootstrap CI |
| :--- | :--- | :--- | :--- | :--- |
| **Small** | 102 – 1,736 | 149 | **1.324** | [1.183, 1.492] |
| **Medium** | 1,782 – 3,888 | 149 | **1.725** | [1.164, 2.390] |
| **Large** | 3,889 – 38,346 | 150 | **1.782** | [1.379, 2.251] |

Because inflation survives in all terciles—and is notably highest on medium and large targets—the effect cannot be dismissed as a small-object detection artifact.

### 4.3 Model Architecture Contrast: Homogeneous vs. Heterogeneous Pairs

A common design recommendation in multi-agent systems is to deploy diverse detector models to achieve redundancy. To test whether architectural diversity eliminates correlated errors, a second detector of a fundamentally different architecture—a vision transformer-based real-time detector (RT-DETR-L)—was evaluated over the exact same 108 rendered frames.

Because detection accuracy differs between YOLO11m and RT-DETR-L, comparison across model configurations used Pearson's correlation coefficient ($\phi$) and odds ratios rather than raw inflation ratios:

| Model Pair Condition | Architecture Relationship | $\phi$ Correlation | Odds Ratio | $p_A$ | $p_B$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **YOLO11m / YOLO11m** | Homogeneous (CNN) | 0.374 | 5.129 | 0.368 | 0.348 |
| **RT-DETR-L / RT-DETR-L** | Homogeneous (Transformer) | 0.379 | 6.605 | 0.234 | 0.214 |
| **YOLO11m / RT-DETR-L** | Heterogeneous (CNN + Transformer) | 0.278 | 3.889 | 0.368 | 0.214 |
| **RT-DETR-L / YOLO11m** | Heterogeneous (Transformer + CNN) | 0.292 | 4.003 | 0.234 | 0.348 |

A paired bootstrap analysis across the identical 448 objects revealed:
- **Mean Homogeneous Association ($\phi$):** **0.3766**
- **Mean Heterogeneous Association ($\phi$):** **0.2852**
- **Paired Difference ($\Delta \phi$):** **+0.0915** (95% CI [+0.0466, +0.1401])

Deploying identical models measurably increases joint failure, confirming that shared neural network weights contribute to correlation. However, heterogeneous pairs retain substantial correlation ($\phi = 0.2852$, odds ratio $\approx 4.0$, with confidence intervals excluding zero). Thus, shared model weights represent a secondary contributor; the primary driver of failure correlation is external to the neural network weights.

### 4.4 Causal Permutation Control and Effect Decomposition

To verify that the measured inflation reflects genuine causal coupling rather than statistical sample bias, a series of permutation controls were executed across the dataset. These permutations held both agents' marginal error rates strictly constant while selectively decoupling physical context:

| Experimental Condition | Preserved Coupling | Inflation Ratio | 95% Bootstrap Range |
| :--- | :--- | :--- | :--- |
| **Observed Pairing** | Same Scene, Same Object | **1.671** | [1.495, 1.875] |
| **Within-Scene Control** | Same Scene, Shuffled Different Object | **1.197** | [1.062, 1.340] |
| **Unrelated Null** | Different Scene, Unrelated Object | **0.999** | [0.835, 1.166] |

These controls provide two decisive findings:
1. **Unbiased Metric:** When agents observe completely unrelated scenes and objects, the inflation ratio returns **0.999** (95% range [0.835, 1.166]). This validates that the double-fault ratio is statistically unbiased and confirms that zero correlation yields a ratio of exactly 1.0.
2. **Variance Decomposition:** Total excess dependence above independence is $1.671 - 1.000 = 0.671$.
   - Retaining scene-level factors (weather, global lighting, geographic layout) while decoupling the specific object accounts for $1.197 - 1.000 = 0.197$, representing **29.4%** of the excess correlation.
   - Forcing both agents to observe the **identical physical object instance** contributes the remaining $0.474$, representing **70.6%** of the excess correlation.

This empirical finding dictates the methodological direction: correlated failures in multi-agent perception are heavily localized at the **object instance level** (e.g., specific target orientation, local shadow boundaries, vehicle color contrast, partial structural occlusion) rather than behaving as a scalar property of the overall environment or platform pairing.

---

## 5. Research Objectives & Technical Methodology

Guided by these empirical insights, the proposed research aims to formalize, estimate, and correct for perceptual error dependence in multi-agent evidence resolution pipelines.

```
+-------------------------------------------------------------------------------------------------+
|                                 CARLA Controlled Scene Generator                                |
|  Orthogonal Knobs: Viewpoint Disparity | Occlusion Geometry | Weather/Illumination | Model Pair |
+-------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+-------------------------------------------------------------------------------------------------+
|                                Multi-Agent Perception Adapters                                  |
|         Agent A: Camera Viewpoint A -> Detection Stream A (YOLO11m or RT-DETR-L)                |
|         Agent B: Camera Viewpoint B -> Detection Stream B (YOLO11m or RT-DETR-L)                |
+-------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+-------------------------------------------------------------------------------------------------+
|                       Streaming Evidence Resolution Engine (AD-001 - AD-004)                    |
|   - Deterministic replay & cryptographic trace hashing                                           |
|   - Online dependence estimator (Object-instance vs. agent-pair tracking)                       |
+-------------------------------------------------------------------------------------------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                                                   |
                       v                                                   v
+-----------------------------------------------+ +-----------------------------------------------+
|       Baseline Policy (Naive Independence)    | |      Treatment Policy (Dependence-Aware)      |
|  Different source_id treated as independent;  | |  Weights confirming evidence by estimated     |
|  Unweighted Bayesian consensus.               | |  inter-source dependence; discounts overlap.  |
+-----------------------------------------------+ +-----------------------------------------------+
                       |                                                   |
                       +-------------------------+-------------------------+
                                                 |
                                                 v
+-------------------------------------------------------------------------------------------------+
|                             Downstream Task Decision Evaluation                                 |
|  Scoring against isolated ground truth: False Task Closures | Verification Cost | Latency        |
+-------------------------------------------------------------------------------------------------+
```

### 5.1 System Architecture and Design Invariants

The evaluation harness adheres to four immutable architectural decisions:
- **AD-001 (Ground-Truth Separation):** Ground truth from the simulator is restricted to downstream evaluation metrics; it is strictly excluded from perception streams and resolution policies.
- **AD-002 (Layer Decoupling):** Probabilistic belief estimation and discrete task action selection (e.g., verifying, closing, or dispatching inspection) are strictly isolated into modular components.
- **AD-003 (Deterministic Traceability):** Every policy decision records the contributing claim IDs and policy version, ensuring byte-identical replay verified via SHA-256 trace hashes.
- **AD-004 (Dependence Invariant):** Multi-source evidence is never treated as statistically independent without explicit quantitative validation.

### 5.2 Controlled Physical Scenario Generator

Building on the CARLA 0.9.16 pipeline, we will systematically generate an experimental corpus sweeping four orthogonal correlation channels:
1. **Viewpoint Geometry:** Angular and baseline separation between agents (sweeping from narrow stereoscopic baselines to wide orthogonal vantage points).
2. **Local Occlusion:** Insertion of static roadway infrastructure, vegetation, and adjacent vehicles partially masking target objects.
3. **Environmental Illumination:** Controlled weather and sun angle presets (ClearNoon, WetNoon, CloudySunset, Dusk).
4. **Detector Diversity:** Pairs drawn from identical architectures (YOLO/YOLO), distinct model families (YOLO/RT-DETR), and models fine-tuned on disjoint versus overlapping training partitions.

### 5.3 Online Dependence Estimation Without Ground Truth

To satisfy RQ2, we will develop an online estimator that calculates inter-source dependence directly from claim streams. Because the spike demonstrated that 71% of correlation concentrates at the object level, the estimator must move beyond coarse scalar agent-trust weights. We will formalize and evaluate two candidate estimators:
- **Agent-Pair Estimator:** Tracks pairwise rolling double-fault rates across shared spatio-temporal claim tracks.
- **Instance-Conditioned Estimator:** Conditions dependence estimates on spatial bounding-box overlap, estimated distance, and feature similarity of the target track.

### 5.4 Dependence-Corrected Policy vs. Naive Baseline

Both policies are implemented behind an identical `ResolutionPolicy` interface to guarantee rigorous comparative evaluation:
- **Naive-Independence Baseline:** Implements standard multi-agent Bayesian updating, treating any claim from an alternate `source_id` as conditionally independent evidence.
- **Dependence-Aware Treatment:** Applies a discounting operator to confirming claims. When Agent B confirms a detection reported by Agent A, Agent B's belief contribution is discounted as a function of the estimated inter-source dependence factor, preventing premature certainty escalation.

### 5.5 Quantitative Evaluation Protocol

The experimental corpus will be evaluated against three core operational metrics:
1. **False Closure Rate:** Frequency with which the system erroneously closes inspection tasks on false-positive detections due to correlated agent double-faults.
2. **Incorrect Reopening / Rejection Rate:** Frequency of erroneously discarding true obstacles due to over-conservative fusion.
3. **Verification Cost:** Total sensing operations, re-observations, or secondary UAV dispatches required to reach definitive task resolution.

**Success Criterion:** The dependence-aware policy must demonstrate a statistically significant reduction in false task closures under correlated operating regimes without incurring prohibitive re-verification overhead compared to the naive baseline.

---

## 6. Feasibility, Compute Plan, and Infrastructure Status

The proposed investigation is grounded in a verified, working codebase and validated hardware configurations.

### 6.1 Simulation and Rendering Pipeline

All CARLA simulation rendering runs locally on an dedicated RTX 5060 Laptop GPU (8 GB VRAM), executing CARLA 0.9.16 on Unreal Engine 4.26 under Python 3.12. The spike retired primary hardware risks:
- **Throughput:** Rendering 54 scenes required 36 seconds; inference across 108 frames required 12 seconds on YOLO11m and 7 seconds on RT-DETR-L.
- **Server Stability:** To prevent Unreal Engine server crashes identified during `client.load_world()` invocations (documented in decision SD-016), the simulator town is fixed at launch, and spatial diversity is achieved via distributed camera actor spawn coordinates.

### 6.2 Model Inference and Fine-Tuning

For large-scale sweeps and controlled detector fine-tuning, workloads will utilize the Vista HPC cluster. While Vista nodes run ARM64 (`aarch64`) architecture—precluding CARLA x86_64 binary execution—they provide high-throughput GPU capacity for detector inference across saved frame corpora and for fine-tuning detector pairs on disjoint data partitions.

### 6.3 Existing Prototype & Test Infrastructure

The software framework is fully operational and maintained under strict test-driven development:
- **Evidence Resolution Prototype:** Implements typed claim contracts, event logs, deterministic replay, and CLI harnesses (22 tests passing in `tests/spec/` and `tests/integration/`). Trace replay determinism is cryptographically verified via identical SHA-256 hashes across runs.
- **Dependence Measurement Harness:** Implements artifacts I/O, ground-truth projection, double-fault calculation, bootstrapping, stratification, and permutation shuffling (153 total tests passing across the project test suite).

---

## 7. Scope, Delimitations, and Risk Management

To maintain scientific rigor, the boundaries of this research are explicitly delimited:

- **Simulation-Grounded Behavioral Evaluation:** Findings characterize decision-policy behavior in photorealistic simulation (CARLA). No formal claim of real-world physical deployment safety is asserted.
- **Adopted Statistical Metrics:** The project does not claim the invention of the double-fault measure (Kuncheva & Whitaker, 2003) or the discovery of correlated failure as an abstract mathematical concept. The novelty lies in the empirical measurement of physical dependence channels in multi-agent visual perception and the design of dependence-calibrated resolution policies.
- **Non-Confounding Ordering Controls:** The claim stream architecture explicitly controls for message arrival latency and out-of-order delivery (Track A watermark design) to prevent temporal arrival anomalies from confounding dependence measurements.

### Risk Matrix and Mitigations

| Identified Risk | Impact | Status / Mitigation Strategy |
| :--- | :--- | :--- |
| **High local simulation overhead** | Slow sweep execution | **Retired:** Spike proved rendering takes <1 s per scene; frame generation is decoupled from offline multi-model inference. |
| **Negligible real-world correlation** | Insufficient signal to study | **Retired:** Spike measured an inflation ratio of 1.671 (CI [1.500, 1.870]), confirming substantial correlation in realistic scenes. |
| **Dependence cannot be captured by scalar trust** | Policy unable to prevent co-failures | **Active Focus:** Spike established that 71% of correlation is object-level. The M1 milestone will explicitly evaluate object-pair versus agent-pair estimator representations. |
| **Disentangling fine-grained per-object properties** | Inability to isolate exact causal feature | Controlled scenario generator will systematically hold vehicle models, colors, and poses constant while toggling ambient lighting and viewpoint angles. |

---

## 8. Research Milestones and Requested Decision

The research is organized across six structured milestones:

- **M0 (Current Gate - Nov 3):** Advisor approval of the refined research framing, empirical evidence, and qualitative research direction.
- **M1 (Nov 10):** Formal freezing of experimental contracts: dependence metric formulations, online estimator interfaces, scenario parameter matrices, and baseline policies.
- **M2 (Nov 24):** Delivery of the controlled-correlation CARLA scenario corpus and completion of deterministic out-of-order evidence replay verification.
- **M3 (Dec 12):** Execution of the full experimental matrix sweep; generation of correlation-versus-decision-error curves.
- **M4 (Dec 18):** Delivery of release-grade evaluation benchmarks, CLI harnesses, and packaging.
- **M5 (Jan 15):** Final comparative analysis, policy operating boundary identification, and demonstration visualizations.
- **M6 (Jan 22):** Final capstone research manuscript and comprehensive artifact submission.

**Requested Decision:** Approval to proceed to the M1 Design Phase under this empirical and methodological framing, formalizing the dependence estimator specifications and scenario matrix. Implementation of production policies remains governed by subsequent approval gates.
