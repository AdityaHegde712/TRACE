# Framework Survey Decisions

## Accepted Context

- FSD-001: This is a separate survey from the prior fault-calibration direction.
- FSD-002: The submitted umbrella title remains **Agentic Visual Perception in Distributed Autonomous Systems**.
- FSD-003: The intended deliverable balances mid-to-upper-mid-tier implementation novelty, a strong demo, and an open-source or licensable career artifact; it is not required to make a major algorithmic claim.
- FSD-004: The first validation application is cooperative search-and-inspect, but the framework should expose domain-neutral extension contracts for other heterogeneous autonomous teams.
- FSD-005: The software path is simulator-first. A later physical demo is illustrative and must not be used to overclaim generality or safety.
- FSD-006: The candidate shared-state pattern is **centralized-logical, replica-aware**: a simulator-world service holds the canonical evidence/merge view while agents use task-scoped local projections. This is a proposed MVP design awaiting feasibility and prior-art analysis.
- FSD-007: The team has three members, SJSU HPC, approximately 300 Colab Pro compute units, initial AWS credits, and a desired five-month software completion window.
- FSD-008: For each future design decision, research primary sources first; distinguish direct evidence from design inference; ask the owner when a material preference remains unresolved.
- FSD-009: Do not use the `research-adversary` skill. Adversarial checking is performed directly through source entailment, closest-counterexample search, failure modes, and a disposition.
- FSD-010: A framework-only contribution is insufficient. The selected direction must address a source-supported operational problem and define a measurable success condition before architecture commitment.
- FSD-011: Market validation is recorded separately in `docs/MARKET_VALIDATION_SUMMER_2027.md`; market evidence does not convert a proposed application framing into an accepted architecture decision.
- FSD-012: Active handoff state remains only in `.agent-tasks/PLAN.md`, `.agent-tasks/DECISIONS.md`, and `.agent-tasks/TASKS.md`; current survey, evidence, proposal, and study documents are versioned in `docs/`. Superseded material is retained locally under ignored `.agent-tasks/archived/`.
- FSD-013: `dev` is the integration branch. Changes are pushed to `dev` first and may reach `main` only after the required checks pass and the owner merges the reviewed change. `main` is the primary deliverable branch.

## Pending

- FSD-P01: Select the initial simulator and adapter surface after feasibility review.
- FSD-P02: Select the world-model representation and query/projection contracts after prior-art comparison.
- FSD-P03: Determine whether a second lightweight reference adapter is needed to substantiate extensibility.
- FSD-P04: Select the exact open-source release boundary and license after implementation landscape review.
- FSD-P05: Establish whether evidence-to-belief lifecycle, task-scoped state projection, and traceable verification/replanning solve a distinct operator/mission problem rather than merely assembling known components.
- FSD-P06: **Working direction, pending team and faculty approval:** Evidence-Gated Visual Task Orchestration, rated 4/5 as implementation novelty. Authority: `docs/DIRECTION_PROPOSAL.md`, `docs/PROBLEM_LEDGER.md`, and `docs/ADVERSARIAL_NOVELTY_PASS.md`. It addresses the specific task-closure/reopening problem, not generic mapping/planning.
- FSD-P07: **Proposed evaluation anchor, pending owner/team/faculty approval:** multi-drone incident response and critical-infrastructure inspection. Retain the evidence-gated task-lifecycle research question and title; the optional plain-language description does not control the project name.
