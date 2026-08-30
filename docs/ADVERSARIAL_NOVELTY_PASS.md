# Primary-Agent Adversarial Novelty Pass

**Date:** 2026-08-29
**Method:** Direct primary-source inspection plus closest-counterexample searches. No `research-adversary` skill was used.

## Candidate Under Test

**Evidence-Gated Visual Task Orchestration:** a simulator-first control plane that prevents a distributed visual report from changing an entity’s operational status or opening/closing/reassigning a mission task until the system records its provenance, freshness, conflict/corroboration status, and applicable verification policy. It supplies role-scoped belief projections and a causal replay trace.

## Direct Counterexample Matrix

| Work | Already establishes | Direct limitation for the candidate claim | Disposition |
|---|---|---|---|
| [MultiUAV-Plat / Agent4Drone (2026)](https://arxiv.org/html/2606.31073) | Restricted APIs, partial local perception, a shared compact blackboard, short-horizon planning, verification, retry/replanning, and a reproducible multi-UAV benchmark ([lines 201–237](https://arxiv.org/html/2606.31073#S3.SS3)). | Its blackboard records visible entities, assignments, action outcomes, prior verification, and retries ([lines 223–231](https://arxiv.org/html/2606.31073#S3.SS3)). In the inspected paper, searches for `conflict` and `world model` found no matching description; this is bounded evidence, not proof of absence. The document does not establish an entity-level multi-source evidence/provenance/conflict/expiry policy that gates task lifecycle transitions. | **NARROW.** The candidate cannot claim a new observe-plan-verify workflow, blackboard, simulator, or UAV benchmark. |
| [Language-Grounded Hierarchical Planning with Multi-Robot 3D Scene Graphs (2025)](https://arxiv.org/abs/2506.07454) | Multi-robot fusion of open-set maps/3D scene graphs, capability-grounded LLM-to-PDDL planning, and real-world task execution ([lines 18–27](https://arxiv.org/html/2506.07454)). | Its concept of operations uses an initial mapping stage followed by an execution stage ([lines 23–31](https://arxiv.org/html/2506.07454)); direct searches for `verify` and `update` returned no matches in the inspected paper. It is therefore not evidence for an online evidence-status task-gating lifecycle, but it is a very close system-level overlap. | **NARROW.** Reject shared multi-robot scene graph plus language planning as a contribution. |
| [DEXTER-LLM (2025)](https://arxiv.org/abs/2508.14387) | Online task generation, assignment/scheduling, event-based updates, human verification, and filtering irrelevant past global scene observations ([lines 3–5](https://arxiv.org/abs/2508.14387)). | It directly defeats dynamic discovery-to-replan as a novelty claim. It does not, from the inspected portions, establish distributed visual evidence provenance, entity conflict state, or causal trace contracts. | **NARROW.** Replanning is a required behavior, not the project identity. |
| [MR-COGraphs (2025)](https://arxiv.org/html/2412.18381v2) | Compact, incremental open-vocabulary object/relation graph sharing and merge. | It is a map representation/communication method, not an orchestration task-lifecycle runtime. | **NARROW.** Reject compact shared visual state as a novelty claim. |
| [VeriGraph (2026)](https://arxiv.org/abs/2411.10446) | Visual scene graph as an intermediate representation for single-robot plan feasibility verification ([lines 3–4](https://arxiv.org/abs/2411.10446)). | It is a single-robot plan-verification system; it does not establish multi-agent evidence conflict adjudication, role projections, or task-causal replay. | **NARROW.** The candidate must distinguish *evidence status before multi-agent task state change* from action-feasibility checking. |
| [AgentComm-Bench (2026)](https://arxiv.org/html/2603.20285v1) | Communication fault protocol and age-aware fallback. | It is a grid-world benchmark with no semantic evidence lifecycle or visual task-closure semantics. | **REJECT AS HEADLINE.** Use as adversarial stress-axis inspiration only. |

## Candidate Failure Tests

1. **Integration-only criticism:** If the demo merely stores scene-graph observations then assigns tasks, it is an assembly of known systems. The evaluation must show a causal improvement from explicit evidence status/gates over matched blackboard or first-report-wins baselines.
2. **Identity/pose error dominates:** Conflicting reports may refer to different physical entities. Limit v1 to a small entity schema and preserve frame/pose/evidence references; do not hide association errors inside LLM prompts.
3. **Always-verify trivializes the policy:** Compare against always-verify under the same budget and show reduced unnecessary verifier trips without excessive false closure.
4. **Trace is ordinary logging:** Every assignment, closure, reopening, and replan must link to evidence IDs, status transition, and policy version; raw rosbag transport replay alone is insufficient.
5. **Privileged simulator leakage:** Agents must use camera/detector/VLM-derived claims only. Simulator truth is scoring-only.

## Verdict

**RETAIN AS A 4/5 IMPLEMENTATION-NOVELTY CANDIDATE, NOT A FIELD-FIRST ALGORITHM.**

The existing problem is operational: a heterogeneous visual team needs to decide what report is sufficiently supported to change mission state, while retaining an explanation of why a task was created, closed, reopened, or reassigned. Current closest systems establish planning, blackboards, maps, verification, and dynamic replanning separately or in partial combinations. In this bounded primary-source pass, no inspected source supplied the full reusable evidence-to-task lifecycle contract.

The only defensible contribution statement is:

> An open simulator-first reference runtime and evaluation protocol for **evidence-gated visual task orchestration**: provenance-linked visual claims are reconciled into entity beliefs, and only policy-defined belief states may trigger task lifecycle transitions, verification routing, or replanning.

This must be presented as a reusable systems implementation and controlled evaluation artifact. Do not claim first-in-field, superior general planning, formal safety, generic distributed resilience, or universal swarm applicability.
