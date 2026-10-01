# Direction Proposal: Evidence-Gated Visual Task Orchestration

**Status:** Owner-approved reference mission; team and faculty approval is still reported as tentative. This is a direction-evaluation document, not a design specification or an implementation commitment.
**Capstone umbrella title:** _Agentic Visual Perception in Distributed Autonomous Systems_
**Reference application:** Owner-approved simulator-first road-blockage verification near critical infrastructure, using two simulated drones.

## Decision Status

The owner approved the narrow reference mission on 2026-10-01. The methodology, initial dataset, metrics, ownership, schedule, and implementation plan remain pending confirmation; this document does not authorize implementation.

> Build and evaluate an open, simulator-first runtime that converts distributed visual observations into provenance-linked evidence claims and allows only policy-defined belief states to create, close, reopen, verify, or reassign mission tasks.

The purpose is to address a concrete operational problem: teams need a traceable basis for deciding when an uncertain visual report is sufficiently supported to change mission state.

## The Problem

In cooperative search-and-inspect, one agent may report that a target, hazard, or blockage exists while another later reports contrary evidence. This can occur through sensing error, pose/identity error, object motion, or genuine scene change. A system needs to decide whether the team should treat the entity as proposed, corroborated, disputed, stale, verified, or invalid—and whether that status should trigger a verification trip, task closure, reopening, or reassignment.

This is distinct from merely creating a map or assigning tasks. [Khronos](https://arxiv.org/html/2402.13817) separates visual measurements from revisable world beliefs, showing why observation history matters. [AgentComm-Bench](https://arxiv.org/html/2603.20285v1) demonstrates that stale/conflicting communicated content can substantially degrade cooperative task performance in its benchmark. Neither source establishes a reusable multi-agent visual evidence-to-task-lifecycle runtime.

## Proposed System Boundary

The proposed artifact is **Evidence-Gated Visual Task Orchestration**:

```text
Visual observation
  -> evidence claim with source/time/pose/model/artifact reference
  -> entity belief and status transition
  -> policy-gated task action: create, verify, close, reopen, or reassign
  -> causal replay trace
```

The runtime would supply task-scoped state projections to agents instead of raw video or omniscient simulator state. A cooperative search-and-inspect mission is the reference validation, not a claim that every swarm application is already supported.

## What Is Already Covered by Prior Work

The proposal deliberately does **not** claim novelty in these areas:

| Existing capability                                                                                                              | Evidence                                                                                                                                                    | Consequence                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Multi-UAV partial perception, shared blackboard memory, observation-planning-execution-verification loop, and benchmark platform | [MultiUAV-Plat / Agent4Drone](https://arxiv.org/html/2606.31073) describes restricted APIs, compact blackboard memory, verification, retry, and replanning. | Do not build a generic LLM-UAV simulator or claim a new observe-plan-verify workflow. |
| Fused multi-robot 3D scene graphs, LLM-grounded PDDL planning, and real-world execution                                          | [Language-Grounded Hierarchical Planning with Multi-Robot 3D Scene Graphs](https://arxiv.org/abs/2506.07454)                                                | Do not claim a new shared scene graph or language-grounded multi-robot planner.       |
| Dynamic LLM task generation, assignment, scheduling, event-based adaptation, and human verification                              | [DEXTER-LLM](https://arxiv.org/abs/2508.14387)                                                                                                              | Do not claim discovery-triggered replanning or multi-robot allocation as new.         |
| Compact open-vocabulary graph sharing and multi-robot map merge                                                                  | [MR-COGraphs](https://arxiv.org/html/2412.18381v2)                                                                                                          | Do not claim compact shared visual state as new.                                      |
| Single-robot visual scene-graph verification of task plans                                                                       | [VeriGraph](https://arxiv.org/abs/2411.10446)                                                                                                               | Distinguish multi-agent evidence-status task gating from plan-feasibility checking.   |

## Why This Direction Still Has Value

The bounded systems contribution is the reusable contract between five already-useful capabilities: provenance-preserving evidence claims, temporal entity beliefs, task-scoped projections, policy-gated task transitions, and causal replay. The primary-source review did not find one inspected system exposing all five as a reusable simulator-first runtime for multi-agent visual search-and-inspect. This is bounded search evidence, not a field-first claim.

The project is career-relevant because it demonstrates agentic engineering beyond prompting: event-driven systems, VLM/detector integration, state reconciliation, multi-agent coordination, evaluation harnesses, reproducible traces, and a ROS 2 bridge boundary. The open-source value is an inspectable reference implementation and experiment suite, not a promise to replace ROS, a flight stack, a mapping library, or a general robotics platform.

## Proposed Outcomes

1. **Open-source runtime:** a documented, permissively licensed core with a stable evidence/task event protocol and simulator adapter.
2. **Reference mission:** two or three simulated agents execute search-and-inspect, handle conflicting or stale visual reports, request verification, and update task state.
3. **Evaluation harness:** seed-controlled scenarios for occlusion, disagreement, stale report, and agent unavailability; simulator truth is scoring-only.
4. **Replay and explanation:** an operator can answer “which observations and policy transition caused this assignment, closure, or reopening?”
5. **Physical-demo bridge:** a constrained ROS 2 adapter contract for a later small drone/rover/fixed-camera demonstration; it illustrates the interface but does not prove flight safety or generalization.

## Proposed Functional Requirements

These are proposed project requirements, not claims that literature establishes them as new.

| ID    | Requirement                                                                                                                                                                                                  | Acceptance evidence                                                                                           |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| FR-01 | Ingest visual observations from each simulated agent as structured evidence claims with source, timestamp, pose/frame reference, entity/region assertion, confidence, model/version, and artifact reference. | Schema validation plus replayable sample claims from every agent.                                             |
| FR-02 | Maintain a canonical entity belief that links supporting/conflicting claims and exposes statuses including proposed, corroborated, disputed, stale, verified, and invalid.                                   | Scenario tests that cause every status transition.                                                            |
| FR-03 | Apply explicit, versioned policies to determine whether a belief may create, close, reopen, verify, or reassign a task.                                                                                      | Same claims under different policy versions yield explainable, recorded decisions.                            |
| FR-04 | Give each role a task-scoped projection and a query path to retrieve supporting evidence; do not broadcast raw visual streams as the default state path.                                                     | Logged view/projection contents and evidence-query traces.                                                    |
| FR-05 | Route a verification task to an eligible agent when evidence is disputed, stale, insufficient, or high-impact under the chosen policy.                                                                       | Seeded disagreement/occlusion scenarios result in correctly linked verification tasks.                        |
| FR-06 | Record causal links from evidence claim to belief transition to task decision to action outcome, and support deterministic replay of the task-state trace.                                                   | Trace-completeness report and replay-equivalence test on fixed seeds.                                         |
| FR-07 | Provide a simulator-first bridge and a documented ROS 2 adapter boundary; lower-level navigation/flight control remains outside the runtime.                                                                 | One simulator adapter works end-to-end; ROS 2 bridge contract and minimal smoke demonstration are documented. |

## Evaluation Questions and Success Criteria

The project should be judged against the following questions, not simply on whether a demo runs:

| Question                                                        | Comparison                                                                                | Measures                                                                                                          |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Do evidence gates improve mission-state correctness?            | First-report-wins, majority vote, always-verify, and proposed evidence gating.            | Entity-state precision/recall, false closure/reopening rate, time-to-verified state.                              |
| Do gates use verification resources efficiently?                | Always-verify and periodic replan versus evidence-gated verification.                     | Unnecessary verifier trips, mission time, completed inspections, model/tool calls.                                |
| Is the system genuinely explainable and reproducible?           | Transport-level replay alone versus semantic causal trace.                                | Percentage of decisions linked to evidence/policy/outcome, fixed-seed replay agreement, failure-attribution time. |
| Does partial/stale information expose a useful stress boundary? | Clean inputs versus injected stale, contradictory, occluded, and unavailable-agent cases. | Task success, stale-entity errors, recovery time.                                                                 |

No formal safety, calibration, or human-factors improvement should be claimed unless separately tested.

## Feasibility Position

The proposed software scope is deliberately narrower than an end-to-end autonomy stack. The recommended baseline is a project-owned Python event/state-machine core with a thin ROS 2/Gazebo adapter. Official Gazebo documentation supports the ROS 2 Jazzy/Gazebo Harmonic pairing and ROS integration ([installation](https://gazebosim.org/docs/latest/ros_installation/), [integration](https://gazebosim.org/docs/harmonic/ros2_integration/)). PX4 and Isaac Sim remain optional later adapters; they are not MVP dependencies. A model-provider interface can support a hosted visual model and later an open-weight alternative using the documented Hugging Face multimodal chat path ([documentation](https://huggingface.co/docs/transformers/en/chat_templating_multimodal)).

The five-month target is feasible only if the team first builds deterministic/synthetic observation and policy baselines, then adds VLMs and physical bridging after the evidence/task/replay loop is working. This is a planning hypothesis, not a verified schedule guarantee.

## Reasons to Reject or Revise This Direction

Reject or significantly narrow the direction if any of the following occur:

1. A closer source or implementation already exposes a multi-agent, provenance-linked visual evidence lifecycle that gates task transitions and causal replay.
2. The team cannot build fair non-LLM baselines; then any apparent improvement may be attributable to model choice rather than the framework.
3. Entity identity/pose association errors dominate the experiment and cannot be isolated with a small initial schema.
4. Evidence-gated verification performs no better than always-verify or a simple vote under matched cost budgets.
5. The project expands into flight control, generic mapping, or a general-purpose robotics platform and loses its measurable problem boundary.

## Recommendation

**Recommend approval as a working direction, with a 4/5 suitability rating.** It is better aligned with the capstone title and a portfolio-quality open-source artifact than the earlier fault-calibration direction, while avoiding unsupported claims of algorithmic or field-first novelty. Approval should authorize a separate design phase—not implementation—where simulator choice, event contracts, baseline definitions, and release boundaries are specified.

## Evidence and Handoff

The detailed audit is in [ADVERSARIAL_NOVELTY_PASS.md](ADVERSARIAL_NOVELTY_PASS.md), the problem comparison in [PROBLEM_LEDGER.md](PROBLEM_LEDGER.md), and the implementation/feasibility landscape in [LANDSCAPE.md](LANDSCAPE.md). These are supporting research artifacts, not part of the design specification.
