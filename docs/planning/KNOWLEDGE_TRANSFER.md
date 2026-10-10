# Knowledge Transfer: Evidence-Gated Visual Task Orchestration

**Purpose:** This is a project-specific adaptation of the IAS class knowledge-transfer guide. It supplies the minimum conceptual foundation to evaluate, discuss, and eventually implement the proposed capstone direction: **Evidence-Gated Visual Task Orchestration** for simulator-first cooperative search-and-inspect.

**Scope boundary:** This is a study guide, not literature-survey evidence and not a design specification. The research-backed proposal remains [DIRECTION_PROPOSAL.md](DIRECTION_PROPOSAL.md). Treat the linked resources as prerequisites and references, not as support for novelty claims.

**Estimated first pass:** about 4–6 hours. The goal is shared vocabulary and sound engineering judgment—not mastery before the team/faculty approval decision.

---

## The dependency chain

```text
1. Distributed autonomous systems
        ->
2. ROS 2 messages, frames, and recorded data
        ->
3. Simulator and visual-sensor integration
        ->
4. Visual observations versus durable world beliefs
        ->
5. Evidence-gated task orchestration and causal replay
        ->
6. Cooperative search-and-inspect evaluation
        ->
   CAPSTONE DIRECTION
```

Each layer depends on the preceding one. Do not begin with an LLM or a drone: first establish what an agent can observe, how that observation is represented, and what makes it credible enough to change mission state.

---

## 1. Distributed autonomous systems — why a swarm needs a shared operational picture

**Core idea:** A multi-agent system is not simply several robots running the same model. Each agent has a limited viewpoint, acts concurrently, and can make a locally reasonable choice that conflicts with the team mission. Coordination therefore needs a shared *operational picture*—but sending every raw camera frame to every agent is costly, hard to audit, and often unnecessary.

**Project connection:** In this capstone, the shared operational picture is deliberately not a learned MARL latent or omniscient simulator state. It is a queryable record of evidence-backed entity beliefs that agents receive in task-scoped form.

**Start here:**

- [Hugging Face Deep RL Course: multi-agent reinforcement learning introduction](https://huggingface.co/learn/deep-rl-course/en/unit7/introduction-to-marl) — intuition for local observations, joint outcomes, and coordination.
- [MultiUAV-Plat / Agent4Drone](https://arxiv.org/html/2606.31073) — read the system overview for a recent example of multi-UAV partial perception, compact shared memory, verification, and replanning. It is prior art, not the proposed contribution.

**Check that you understand:** Why is a global simulator truth value useful for scoring an experiment but inappropriate as an agent’s normal input?

---

## 2. ROS 2 messages, frames, and recordings — how robotic information is exchanged and inspected

**Core idea:** ROS 2 is a robotics middleware ecosystem. Nodes exchange typed messages on topics, request bounded work through services/actions, and use coordinate-frame transforms to say *where* a sensor observation was made. The information flow matters as much as a model’s prediction: a detection without an agent ID, timestamp, frame, or pose cannot be reliably reconciled later.

**Project connection:** A future ROS 2 adapter should translate robot/simulator data into project-owned evidence claims. The core runtime should not depend on a specific flight stack or simulator; ROS 2 is an integration boundary, not the source of truth.

**Start here:**

- [ROS 2 Jazzy documentation](https://docs.ros.org/en/jazzy/) — learn the concepts overview, publishers/subscribers, services/actions, and `tf2` coordinate frames. The documentation is the authoritative starting point even when access protections prevent automated rendering.
- [rosbag2 repository and documentation](https://github.com/ros2/rosbag2) — understand record/replay as an engineering debugging tool. Project-level causal replay is richer: it must connect a claim to a belief transition and then a task decision.

**Minimum vocabulary:** node, topic, message type, action, frame, transform, timestamp, bag/replay, QoS.

---

## 3. Simulator and visual-sensor integration — establish a safe test world before hardware

**Core idea:** The project is simulator-first because it needs repeatable occlusion, disagreement, staleness, and unavailable-agent cases. A simulator can produce truth labels for evaluation while still withholding them from normal agent decisions.

**Project connection:** The proposed initial boundary is a project-owned event/state-machine core plus a thin ROS 2/Gazebo adapter. The team should prove the evidence/task/replay loop with deterministic or synthetic observations before adding VLM latency, PX4, or physical robots.

**Start here:**

- [Gazebo Harmonic: ROS 2 integration](https://gazebosim.org/docs/harmonic/ros2_integration/) — explains `ros_gz_bridge`, sensor/actuation bridging, and simulator interactions. It explicitly documents ROS-to-Gazebo message exchange and simulator-agnostic simulation interfaces.
- [Gazebo Harmonic sensor tutorials](https://gazebosim.org/docs/harmonic/sensors/) — review camera and sensor concepts before choosing a simulated visual input.
- [Nav2 documentation](https://docs.nav2.org/) — optional background for navigation boundaries. The project consumes navigation availability/outcomes; it does not try to replace navigation.

**Check that you understand:** Which signals belong in a visual evidence claim, and which belong only in experiment scoring? Example: camera image reference and pose are claim context; simulator object identity is scoring-only unless the simulated agent independently infers it.

---

## 4. Visual observations versus durable world beliefs — the central distinction

**Core idea:** An observation says, “Agent A, at time T, using model M, observed X with confidence C from pose P.” A belief says, “Given all linked observations, the system currently treats entity E as proposed, corroborated, disputed, stale, verified, or invalid.” These are not interchangeable.

An observation can be wrong, duplicated, delayed, stale because the world changed, or associated with the wrong entity. Deleting or overwriting it makes later investigation impossible. A belief can change when newer or conflicting evidence arrives, while preserving the observation history.

**Project connection:** The candidate contribution is the reusable contract that carries an evidence claim through entity-belief state transitions, policy-gated task changes, and a causal replay trace. [Khronos](https://arxiv.org/html/2402.13817) is useful background for separating measurements from revisable world beliefs; it is not evidence that this project’s full multi-agent task-gating runtime already exists.

**Suggested exercise (no implementation required):** Take the sentence “a blue truck blocks Route 3” and list the fields needed to make it a replayable claim: source agent, observation time, coordinate frame/pose reference, entity or region assertion, confidence, model/version, and raw-artifact reference. Then explain what additional evidence would move the belief from *proposed* to *corroborated*.

---

## 5. Evidence-gated task orchestration and causal replay — when a belief may change work

**Core idea:** A task system should not necessarily create, complete, reopen, or reassign work whenever it receives a single visual report. A policy makes those transitions explicit: for example, disputed, stale, or high-impact evidence may create a verification task instead of closing an inspection.

**Project connection:** The intended lifecycle is:

```text
visual observation
  -> structured evidence claim
  -> entity belief and status transition
  -> policy-gated task action
  -> action outcome and causal replay trace
```

The explanation must be inspectable: “This verification task was assigned because claims C-12 and C-19 conflict, the belief became disputed under policy P-3, and Agent B was eligible.” It is not enough to log that an LLM happened to produce a task.

**Start here:**

- [Python `asyncio` documentation](https://docs.python.org/3/library/asyncio.html) — understand event loops, queues, tasks, synchronization, and cancellation. An event-driven prototype should make ordering and failure handling explicit.
- [Pydantic documentation](https://docs.pydantic.dev/latest/) — optional but practical for typed, versioned event schemas and validation in a Python prototype.
- [AgentComm-Bench](https://arxiv.org/html/2603.20285v1) — recent benchmark context for why stale and conflicting communicated content can degrade cooperative task performance. Read it as research evidence; do not infer untested claims beyond its evaluation.

**Check that you understand:** Why is an immutable evidence record different from a current belief state? Why is a policy version part of a replay trace?

---

## 6. Visual-agent reasoning — use models as bounded tools, not as the database

**Core idea:** A detector or VLM can propose an entity, location, attribute, or ambiguity. It cannot by itself provide the durable, team-wide decision record. Treat model output as one source of evidence with a model identifier, prompt/configuration reference, confidence or uncertainty signal when available, and artifact reference.

**Project connection:** The software plan must include deterministic and synthetic-observation baselines before an LLM/VLM. That avoids crediting a model for improvements caused by the task-gating policy or hiding a broken lifecycle behind a fluent explanation.

**Start here:**

- [Hugging Face Transformers: multimodal chat templates](https://huggingface.co/docs/transformers/en/chat_templating_multimodal) — reference for a later provider abstraction supporting multimodal input. This is optional until the core baseline works.
- [OpenCV documentation](https://docs.opencv.org/4.x/) — basic image/geometry tooling for visual pre-processing and overlays.
- [VeriGraph](https://arxiv.org/abs/2411.10446) — a useful contrast: visual scene-graph verification of task plans is not the same as multi-agent evidence-status task gating.

**Minimum vocabulary:** detection, tracking/association, pose, provenance, confidence, latency, deterministic baseline, model version.

---

## 7. Cooperative search-and-inspect — the reference application and evaluation discipline

**Core idea:** The reference mission gives the framework a concrete problem: several simulated agents search regions, inspect candidates, reconcile inconsistent visual reports, and decide when verification, closure, reopening, or reassignment is warranted.

**Project connection:** The application is an evaluation vehicle, not a claim that all swarm tasks are solved. The strongest result is a fair comparison against simple alternatives under matched scenarios and budgets.

**Required comparisons:**

| Baseline or treatment | What it tests |
|---|---|
| First-report-wins | Whether acting on a single report causes false task transitions. |
| Majority vote | Whether simple aggregation is sufficient. |
| Always-verify | Whether the proposed gate saves verification effort without losing correctness. |
| Evidence-gated policy | Whether an explicit belief lifecycle improves mission-state correctness and traceability. |

**Core measures:** entity-state precision/recall, false closure/reopening rate, time to verified state, unnecessary verification trips, mission time, task completion, model/tool calls, trace completeness, and fixed-seed replay agreement. These are proposed evaluation criteria from [DIRECTION_PROPOSAL.md](DIRECTION_PROPOSAL.md), not results.

---

## Suggested first-pass study sequence

| Order | Material | Time |
|---|---|---:|
| 1 | §1 distributed autonomy and the MultiUAV-Plat overview | 35 min |
| 2 | §2 ROS 2 concepts, frames, and rosbag2 | 45 min |
| 3 | §3 Gazebo/ROS 2 bridge and sensor concepts | 45 min |
| 4 | §4 observation-versus-belief exercise and Khronos context | 35 min |
| 5 | §5 event-driven orchestration, schemas, and replay | 45 min |
| 6 | §6 visual-model boundary and §7 baselines/metrics | 40 min |
| 7 | Re-read [DIRECTION_PROPOSAL.md](DIRECTION_PROPOSAL.md) and explain the lifecycle aloud in your own words | 20 min |

**Total:** about 4–5 hours. Optional hands-on exploration of ROS 2/Gazebo or a VLM runtime should wait until the direction receives owner, team, and faculty approval.

---

## Plain-English restatement of the proposed capstone

Several autonomous agents observe a scene, but any one image-based report may be wrong, late, incomplete, or contradicted by another agent. Instead of letting a single report silently change the mission, the proposed framework records each report as evidence, maintains a revisable belief about the relevant entity, and applies an explicit policy to decide whether work should be created, verified, closed, reopened, or reassigned. The system then preserves the chain of reasons so an operator can replay why the team acted.

If that statement makes sense, the project direction should be understandable. If it does not, revisit §§2, 4, and 5 before reading additional papers or debating implementation details.

## Relationship to the research record

For research claims, counterexamples, novelty boundary, and the approval decision, use the framework-survey artifacts rather than this guide:

- [DIRECTION_PROPOSAL.md](DIRECTION_PROPOSAL.md) — review-ready direction and functional requirements.
- [ADVERSARIAL_NOVELTY_PASS.md](ADVERSARIAL_NOVELTY_PASS.md) — direct counterexample and novelty checks.
- [PROBLEM_LEDGER.md](PROBLEM_LEDGER.md) — source-cited operational problem and comparison target.
- [LANDSCAPE.md](LANDSCAPE.md) — implementation landscape and feasibility evidence.
