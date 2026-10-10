# Adversarial Pre-Approval Review

## Disposition

Approve only a narrowed minimum viable project. The deterministic simulator-first evidence-to-task lifecycle is a **3/5 feasibility** candidate for three people over three to four months. Treating the `Capstone-TRACE*.md` narrative as a build specification is **2/5**: it combines unvalidated perception, association, robotics, networking, persistence, and benchmark work that exceeds the active plan.

This review does not approve a reference mission. It establishes the boundary that a later mission decision must respect.

## 1. Engineering Feasibility

The active project proposal specifies a project-owned event/state-machine core with a thin ROS 2/Gazebo adapter. It also requires deterministic or synthetic observations and policy baselines before optional visual-language models or physical bridging. The TRACE reference narrative instead describes a larger, completed system with spatial association, Re-ID, online visual models, multi-store persistence, scoped projections, offline recovery, and a large benchmark. Those claims are not project evidence.

The feasible MVP is:

1. Two simulated agents and one entity or region schema.
2. A deterministic claim generator that creates clean, stale, contradictory, and occluded observations under fixed seeds.
3. A six-state belief lifecycle and one versioned deterministic policy.
4. Append-only causal links and fixed-seed replay.
5. First-report-wins and always-verify baselines.
6. One camera-to-claim adapter only after core tests pass.

Exclude VLMs, detector training, Re-ID, 3D association, distributed recovery, physical hardware, bandwidth claims, and the TRACE benchmark scale from the first milestone. Gazebo integration remains a bounded risk because the official bridge documentation states that its message-type support is limited. Start with a two-agent bridge smoke test using only the specific image, pose, and task messages selected for the MVP.

## 2. Novelty Boundary

Dynamic task generation, allocation, event-driven adaptation, and human-in-the-loop verification cannot be the novelty headline. DEXTER-LLM already describes a dynamic adaptation and human-in-the-loop verification module with event-based updates to subtasks and assignments.

The defensible narrow contribution is a reusable and evaluated contract:

```text
provenance-bearing observation claim
  -> revisable belief transition
  -> versioned policy decision
  -> task lifecycle action
  -> replayable causal trace
```

The evaluation must show that this explicit contract changes false closure or reopening and verification-cost outcomes under matched scenario seeds and budgets. A demo that records observations and assigns tasks without that comparison does not establish the intended systems contribution.

## 3. Plan and Directory Adherence

The active plan still records the direction and evaluation anchor as pending owner, team, and faculty approval. It also prohibits detailed design or implementation before that approval. The authorized TRACE boundary permits its conceptual vocabulary only; it excludes all claimed implementation status, thresholds, stack choices, datasets, metrics, results, and deployment claims.

The project remains aligned only if new artifacts preserve this distinction:

- `docs/` holds review-ready proposals, decisions, and reports.
- `.agent-tasks/` holds active state, source excerpts, and continuation details.
- `docs/Capstone-TRACE*.md` remains inspiration, not evidence.
- `meetings/` holds fact-bounded meeting notes.

## 4. Methodology and Dataset Fit

Simulator-native observations are suitable as the primary evaluation input because the project needs controlled stale, conflicting, occluded, and unavailable-agent cases with simulator truth reserved for scoring. They test evidence resolution directly.

M3OT is suitable only as an auxiliary offline perception adapter. Its public description identifies it as a multi-drone, multi-modality object-tracking dataset. It can test whether a small real-world RGB/IR observation split can be converted into the project claim schema. It does not provide task lifecycle labels, belief-state truth, policy decisions, agent capabilities, or verification outcomes. It therefore cannot validate the core evidence-to-task method by itself.

Before procurement, verify license, download access, storage cost, a small fixed split, and the adapter's schema conversion. Keep the simulator mission and scoring truth independent from the external dataset.

## Mission Approval Gate

Approve a reference mission only if the team accepts the narrowed MVP and rejects all unvalidated TRACE completion claims as project facts. The chosen mission must support one entity or region type, independent contradictory observations, a verification action, and measurable false closure or reopening outcomes.

## Evidence Classification

- **Workspace-supported:** active scope, plan boundaries, prior-art boundary, evaluation intent, and TRACE-reference restrictions.
- **Source-supported:** ROS 2/Gazebo bridge limitation and DEXTER-LLM's overlapping dynamic adaptation and verification capability.
- **Design inference:** the minimal viable architecture, exact implementation sequence, and M3OT's restricted role as an auxiliary adapter.
