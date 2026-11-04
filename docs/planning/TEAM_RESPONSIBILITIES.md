# Team Responsibilities and Milestones

**Project:** Dependence-Aware Trust in Multi-Agent Visual Perception  
**Status:** Team work allocation and milestone schedule for advisor review. Aligned with `PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md`.  
**Date:** 2026-11-03  
**Window:** 2026-10-27 to 2027-01-22  

The experimental spike established that approximately 71% of measured error dependence concentrates at the individual observed object instance. Consequently, the M1 milestone explicitly decides whether the online dependence estimator is keyed per object pair or per agent pair. That decision sits on the project lead's track (Track A).

---

## Team Roles

| Member | Role | Track Ownership |
| :--- | :--- | :--- |
| **Aditya Hegde** | Project Lead | Formal measurement definitions, deterministic evidence resolution engine, evaluation protocol, and immutable architectural contracts. |
| **Rishi Sheth** | Simulation Engineer | CARLA controlled-correlation scenario generation, ground-truth extraction, and optional robotics simulation spike. |
| **Pranav Senghal** | Systems & Harness Engineer | Parameter sweep harness, baseline policy implementations, CI/CD pipeline, and public benchmark release artifacts. |

Each member owns the technical correctness of their assigned track. The project lead governs cross-track contracts and serves as the sole authority for modifying frozen definitions.

---

## Three Concurrent Tracks

Following milestone M1, development tracks execute concurrently. Milestone M1 serves as the primary synchronization gate, freezing the shared interfaces and mathematical contracts consumed by all tracks.

### Track A: Measurement and Evidence Resolution Core (Aditya)

- **A1. Dependence Metric and Online Estimator:** Formalize the dependence inflation factor (observed joint error rate normalized by marginal independence expectation), estimator sample-size bounds, and failure modes. Resolve per-object versus per-agent estimator granularity.
- **A2. Agreement-Reliability Metric:** Define $P(\text{correct} \mid k \text{ sources agree})$ as a function of measured inter-source dependence, executable from streaming claim data without ground-truth access.
- **A3. Deterministic Replay Under Concurrency:** Formalize arrival watermarks and out-of-order reconciliation windows. Validate through property-based tests proving that any claim arrival permutation within the watermark window produces byte-identical traces.
- **A4. Evidence Resolver and Policy Suite:** Implement the dependence-aware discounting policy behind the `ResolutionPolicy` interface, and implement the naive-independence baseline rule treating distinct `source_id` attributes as statistically independent.
- **A5. Empirical Evaluation and Manuscript:** Synthesize the correlation-versus-decision-error operating curves, establish decision boundary thresholds, and lead the research manuscript.

### Track B: Scenario Generation and Sensor Simulation (Rishi)

- **B1. Controlled Physical Scenario Generator:** Construct CARLA 0.9.16 scene generation pipelines controlling four physical channels: viewpoint angular disparity, static occluder placement, ambient illumination/weather presets, and detector model pairings.
- **B2. Corpus Versioning and Determinism:** Implement fixed-seed scene manifests ensuring bit-exact procedural scene reconstruction and frame extraction.
- **B3. Ground-Truth Separation:** Isolate simulator 2D/3D bounding boxes into evaluator-only artifacts, preventing ground truth from entering the claim stream (enforcing AD-001).
- **B4. Robotics Simulation Spike (PX4 / Gazebo):** Optional secondary integration. Kept off the critical path to ensure core evaluation remains independent of robotics simulation stability.

### Track C: Parameter Sweep Harness and Release Engineering (Pranav)

- **C1. Automated Sweep Harness:** Construct CLI orchestration to sweep the scenario matrix across policy configurations, record run artifacts, and generate structured comparative performance tables.
- **C2. Baseline Resolution Policies:** Implement comparison heuristics: latest-report, first-report-wins, unweighted majority vote, and always-verify, all adhering to the `ResolutionPolicy` interface.
- **C3. Release Engineering & Open Source Packaging:** Maintain root documentation, Apache-2.0 licensing, clean virtual environments via `uv`, and reproducible single-command execution.
- **C4. Interactive Walkthrough Demonstration:** Render visual walkthroughs of representative failure scenes, illustrating simultaneous double-faults under naive consensus versus calibrated withholding under dependence-aware resolution.
- **C5. Sensor-to-Claim Adapter Interface:** Specify camera-to-claim ingestion contracts for potential physical sensor integration.

---

## Project Milestones

| Milestone | Target Date | Primary Deliverables | Owner | Decision Gate |
| :--- | :--- | :--- | :--- | :--- |
| **M0** | Nov 3 | Advisor approval of refined proposal framing, spike findings, and research questions | Aditya | Gate: Authorizes M1 design phase. |
| **M1** | Nov 10 | Immutable contracts frozen: dependence estimator, scenario matrix, policy interface | Aditya | Gate: Serializes B1 and C1. Tracks run in parallel after this. |
| **M2** | Nov 24 | Controlled CARLA scenario corpus generated; deterministic arrival tests passing; baselines implemented | All | Verification: Determinism tests pass; corpus generates reproducibly from seed. |
| **M3** | Dec 12 | Initial end-to-end parameter sweep; preliminary correlation-vs-decision-error curves | Aditya, Pranav | Verification: First empirical comparison curve generated. |
| **M4** | Dec 18 | Release benchmark packaging completed; go/no-go decision on optional PX4 spike | Pranav, Rishi | Verification: Clean clone runs end-to-end evaluation. |
| **M5** | Jan 15 | Complete experimental sweeps, final trade-off curves, and visual demonstrations | All | Verification: Every reported statistic traces to an immutable run artifact. |
| **M6** | Jan 22 | Final capstone report, code repository release, and demonstration presentation | All | Final capstone submission deadline. |

---

## Dependencies and Coordination Contracts

- **M1 Synchronization:** Track B cannot construct the full scenario sweep until the correlation channels are frozen; Track C cannot build the sweep harness until evaluation metrics are defined.
- **Decoupled Development:** Task A3 (out-of-order determinism) and Task B1 (scenario generation) operate independently in parallel.
- **Strict Data Flow:** Track B delivers scenario corpora and generation manifests to Track A; Track C provides automated execution tables. Analytical interpretation and claims sit exclusively in Track A.
- **Authority on Frozen Contracts:** Only the project lead (Aditya) modifies contracts frozen at M1. The Sprint 1 prototype carries no protected status and serves as a disposable reference.

---

## Risk Management and Fallback Protocols

1. **M1 Schedule Slip:** Lead freezes an initial versioned formulation of the dependence estimator rather than delaying downstream generation.
2. **Simulation Channel Coupling:** If orthogonal channel control proves difficult in CARLA, collapse the sweep to the two most influential channels (viewpoint disparity and model pairing).
3. **Robotics Simulation Failure:** The PX4/Gazebo spike is non-blocking. If robotics simulator integration fails, the CARLA benchmark provides 100% of required empirical evaluation.
4. **Negligible Impact on Decision Outcomes:** If empirical results reveal that decision errors do not scale with dependence, document and publish the calibrated negative result.
5. **Workload Imbalance Late in Cycle:** Track C incorporates buffer tasks (C4 visual demonstration, C5 adapters) that can be rescheduled to support Track A analysis.

---

## Operational Cadence

Weekly team technical review meetings and bi-weekly faculty advisor progress reviews. Every meeting produces a dated action ledger tracking milestone progress and blocking issues.
