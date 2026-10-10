# Dataset and Method Review: Road-Blockage Verification MVP

**Status:** Proposed evidence-backed input for Workbook 1. It records an owner-approved mission, not an approved implementation plan.

## Confirmed scope

The owner approved this initial reference mission on 2026-10-01: two simulated drones verify a reported road blockage near critical infrastructure. The core study asks whether a provenance-linked evidence claim, a revisable belief state, and a policy-gated task transition prevent incorrect closure or support justified reopening when reports conflict or become stale.

The study is not a detector-training project, a flight-control project, or a claim of real-world safety. Those boundaries matter because the planned outcome is a decision trace, not an autonomous flight demonstration.

## Data decision

### Primary evaluation data: project-generated synthetic scenario corpus

**Proposed use.** Create a small, versioned corpus of fixed-seed simulator scenarios. Each scenario will retain simulator truth separately from the agent-visible evidence stream. Its labels must include the report source, target region, evidence time, injected condition, expected policy decision, and ground-truth blockage status.

**Reasoning.** The required outcome labels are belief and task-lifecycle outcomes: verify, close, reopen, or reassign. Neither reviewed dataset description supplies those labels. A project-generated, policy-labeled corpus is therefore the proposed primary evaluation data. This is an inference from the reviewed descriptions, not a claim that either dataset is deficient for its own task.

The corpus will cover only the minimum cases needed for the MVP: a supported blockage report, a false report, a stale report, and conflicting reports. Before implementation, the team must freeze an independently authored event-sequence truth table that defines the correct task result for each case. It must be separate from the policy code and use held-out seeds. The evaluation will report false closure, incorrect reopening, and reopen latency against that oracle, alongside matched baselines that state their rule and state-representation differences. The exact corpus size, obstruction assets, simulator, and scoring thresholds are not yet selected.

### Auxiliary perception data: M3OT is a narrow input-adapter candidate

[M3OT](https://doi.org/10.1038/s41597-025-06204-0), published online in 2025, describes vehicle detection and tracking data acquired by two UAVs, including paired RGB-IR images. It is a candidate only for checking that the project can convert public aerial observations into its evidence-claim schema.

That is not a road-blockage recognition test. The reviewed description concerns high-altitude vehicle detection and tracking, not obstruction semantics, belief-state transitions, or task-policy outcomes. If used, M3OT can test input plumbing and tracking-oriented claim handling only. It cannot establish perception accuracy for road blockages or policy correctness.

M3OT has not been downloaded, license-verified locally, or profiled in this repository. Do not describe it as procured, integrated, or usable until those gates pass.

## Method decision

### Proposed core method

1. A simulator emits a road-blockage truth state and a deterministic visible-evidence stream for two drone viewpoints.
2. A claim adapter turns each visible event into a structured evidence claim; the first milestone may use a deterministic claim generator rather than a learned detector.
3. A single belief lifecycle reconciles claims into a task-scoped status.
4. One versioned policy maps that status to a task action: create or verify, close, reopen, or reassign.
5. An append-only causal trace links the evidence, belief change, policy version, and resulting task action. Fixed-seed replay must reproduce the same trace.

This keeps the evaluation aligned with the approved problem. It also avoids treating simulator truth as agent input; truth is scoring-only.

### Simulator options and recommendation

PX4 documents a multi-vehicle Gazebo workflow and gives an example that spawns two X500 quadrotors plus one fixed-wing vehicle. That establishes a relevant multi-UAV path, not a completed two-drone configuration. The same documentation states that multi-vehicle simulation is Linux-only, so the first technical milestone must be an environment and two-vehicle startup spike before the team commits to it.

CARLA 0.9.16 has native ROS 2 connectivity and is useful evidence that a current road-world simulator can connect sensor streams and ego control. It is not selected for this mission because the reviewed release material does not establish a two-UAV workflow. CARLA remains a rejected first-path option, not an unavailable tool.

The practical sequence is therefore: implement and test the deterministic, simulator-agnostic core against a local synthetic trace test setup; run the PX4/Gazebo two-vehicle startup spike; then add one camera-to-claim adapter. The spike passes only with a supported Linux environment, exactly two active X500 instances, unique IDs and topics, two visible sensor streams, and a saved startup log. A failed spike must leave the core evaluation runnable rather than forcing a rewrite.

## Evidence and limits

The claims above are supported by the exact source excerpts in [SOURCE_EXCERPTS.md](../.agent-tasks/dataset-method-review/SOURCE_EXCERPTS.md). They are deliberately narrow.

- Source claim: PX4 documents multi-UAV Gazebo SITL and a two-X500 example.
- Source claim: M3OT describes two-UAV aerial vehicle detection and tracking with paired RGB-IR images.
- Inference: neither reviewed dataset description supplies task-lifecycle labels; a project-generated, policy-labeled corpus is the proposed primary evaluation data.

## Workbook-ready position

For Workbook 1, describe the synthetic scenario corpus as the proposed primary evaluation data and M3OT as a candidate auxiliary input-adapter dataset. State plainly that procurement, license verification, profiling, and adapter integration are still pending. Results will establish reproducible decision-policy behavior only in synthetic scenarios; they will not establish perception accuracy, flight safety, or real-world operational safety.

## Sources

1. CARLA Simulator. "CARLA 0.9.16 Release." 2025-09-16. https://carla.org/2025/09/16/release-0.9.16/
2. PX4 Autopilot. "Multi-Vehicle Simulation with Gazebo." Current documentation retrieved 2026-10-01. https://github.com/PX4/PX4-user_guide/blob/main/en/sim_gazebo_gz/multi_vehicle_simulation.md
3. Nie, Z. et al. "M3OT: A Multi-Drone Multi-Modality dataset for Multi-Object Tracking." *Scientific Data*, 2025. https://doi.org/10.1038/s41597-025-06204-0
