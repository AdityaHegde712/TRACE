# Simulator-First Visual Swarm Framework Survey Plan

## Objective

Identify a credible, career-relevant, open-source implementation novelty for **Agentic Visual Perception in Distributed Autonomous Systems**. The target is a simulator-first framework for heterogeneous autonomous agents that maintain an evidence-backed shared world model and coordinate a cooperative search-and-inspect reference mission.

This is a new survey. The earlier uncertainty/fault-calibration survey in the parent `.agent-tasks` folder is historical context only and must not constrain this direction.

## Problem-First Acceptance Gate

The project must solve an existing, observable problem in heterogeneous visual-autonomy teams. A framework is only a means to solve that problem. Before selecting a novelty, the survey must document: the affected workflow, the failure under current approaches, a measurable outcome, the closest current solution, and why the proposed system can be fairly evaluated against it.

The current **hypothesis to test**, not an accepted finding, is that teams can detect/map and independently allocate tasks, but lack a reusable way to preserve distributed visual evidence with provenance, update/revoke beliefs, and make those updates auditable causes of verification or replanning actions.

## Candidate Product Thesis

An extensible **Evidence-Backed Visual Swarm Orchestration Runtime** in which agents contribute visual evidence; a canonical service reconciles that evidence into a shared world model; agents consume task-scoped belief projections and carry out delegated verification/search tasks. The framework is validated in one simulator-first search-and-inspect application and designed, not claimed proven, to support other grouped autonomous-system applications.

## Survey Scope

- Core date window: 2022-08-29 through 2026-08-29. Older sources are background only.
- Existing papers and open-source systems for multi-robot orchestration, shared semantic world models, VLM/LLM robotics agents, simulator-first evaluation, and observability/evidence provenance.
- Feasibility for a three-person team with five months to software completion and a later small physical demo.
- Direct adversarial comparison against the closest systems; no use of the `research-adversary` skill.

## Non-Goals

- Do not build the framework during this survey.
- Do not claim a universal swarm platform, formal safety guarantees, a novel scene-graph mapper, or decentralization/resilience without implementation and evaluation evidence.
- Do not treat a learned MARL latent as the inspectable operational world state.

## Proposed Research Phases

1. [x] Establish protocol and source matrix.
2. [x] Map existing frameworks, implementations, and their extension seams.
3. [x] Compare world-model, coordination, and evidence-lifecycle designs.
4. [x] Evaluate simulator, model, compute, and physical-demo feasibility.
5. [x] Establish a source-cited problem statement and evaluation target.
6. [x] Perform primary-agent adversarial novelty pass and choose a bounded implementation contribution.
7. [x] Validate Summer 2027 market relevance and new-grad employability against target-application companies.

## Exit Criteria

- A source-cited problem ledger identifies a workflow failure, affected user/operator, baseline, and measurable outcome.
- [x] A source-cited feature matrix distinguishes the candidate from the closest implementations.
- A scoped v1 contribution, reference application, and open-source release boundary are selected.
- A five-month feasibility plan is based on explicit dependencies and measured-risk assumptions, not assertions.
- Every retained finding has a direct source, counterexample check, and `RETAIN`, `NARROW`, or `REJECT` disposition.
- [x] A market addendum distinguishes product adoption, procurement, investment, and hiring evidence from project inference.

## Review State

The direction proposal is complete at `docs/DIRECTION_PROPOSAL.md`. `docs/MARKET_VALIDATION_SUMMER_2027.md` rates the proposed technical work's market alignment 4/5; the separate 3/5 rating concerns current specialized new-grad role availability, not the project name. On 2026-10-01, the owner approved the narrow reference mission: two simulated drones verify a reported road blockage near critical infrastructure. Team and faculty approval remains reported as tentative. No implementation or detailed system design is authorized until the methodology, initial dataset, evaluation plan, ownership, and schedule are documented and confirmed.

## Prerequisite Study Guide

`docs/KNOWLEDGE_TRANSFER.md` is a project-specific study guide adapted from the owner’s IAS coursework material. It is not research evidence or a design commitment. It covers the prerequisite chain from multi-agent partial observability through ROS 2/Gazebo integration, visual evidence versus belief state, event-driven task gating, and evaluation baselines. It should be read before the approval discussion or a later implementation phase.

## Project Abstract

`docs/PROJECT_ABSTRACT.md` is the current one-page project abstract. It contains three body paragraphs covering only the domain background, then the operational problem and adjacent company work, then the proposed evidence-gated solution and evaluation. Its company references are attributed to official sources, its claims retain the bounded novelty position from `docs/DIRECTION_PROPOSAL.md`, and the 215-word body has passed rubric-driven structure, phrasing, and humanization checks.

## Active Submission Audit

The active phase is a read-only evidence audit for the CMPE 295A Workbook 1 report and meeting-log submittables. The meeting-log Canvas export at `Submissions/Zips/canvas_assignments_2026-10-01.zip` has been extracted to `Submissions/Extracted/canvas_assignments_2026-10-01/`. The Workbook 1 Canvas export at `Submissions/Zips/canvas_assignments_2026-10-01 (1).zip` has been extracted separately to `Submissions/Extracted/canvas_assignments_2026-10-01-workbook/`. The verified archive inventory includes meeting-log instructions and a text template plus Workbook 1 instructions and separate research and development DOCX templates.

The audit will map each explicit requirement and rubric item to repository evidence, classify it as present, partial, missing, or unverifiable, and identify the smallest work needed to maximize the score. Every `docs/Capstone-TRACE*.md` file is excluded until the owner explicitly authorizes reading it. Drafting will follow the supplied template and receive a factual-preservation humanization pass.

## Meeting Log Repository Reconciliation

On 2026-10-01, `origin/main` was fetched and verified to contain `meetings/folder_purpose.md`, but no dated meeting-entry path. At verification time, `origin/main` was three commits ahead of local `dev`; local `dev` had one commit not in `origin/main`. The local working tree also contained pre-existing uncommitted changes. Do not rebase dirty `dev` onto `main`, and do not merge branches locally. When meeting facts are confirmed, create the note on a dedicated feature branch based on `dev`; the owner can later decide how the main-only folder commit is integrated through the project’s remote-review workflow.

The dedicated local branch `codex/meeting-log-sept-15` was created from current `dev` on 2026-10-01 without a commit or push. It contains an intentionally incomplete draft at `meetings/2026-09-15-advisor.md`. The meeting date, time, mode, student attendee, problem-refinement discussion, unresolved planning topics, team-wide initial-development/dataset-procurement action, and next-meeting code-scaffold goal came directly from the owner. The professor/advisor name, attendance, due date, and all formal technical decisions remain unconfirmed and are visibly labeled as such.

## Provisional Advisor Gate

The owner reports tentative team and advisor approval of the Evidence-Gated Visual Task Orchestration direction and multi-drone search-and-inspect evaluation anchor. The advisor's stated prerequisites are: (1) a novelty-proof document, (2) an initial dataset, (3) an initial solution direction, and (4) an initial evidence-resolution direction. Existing `docs/ADVERSARIAL_NOVELTY_PASS.md` addresses the novelty gate only as a bounded candidate, not a final field-first proof. Dataset, solution, and evidence-resolution work remains provisional until the experiment’s data modality and reference workflow are confirmed.

## TRACE Reference Boundary

The owner authorized `docs/Capstone-TRACE*.md` as loose directional material only. Use the following concepts as candidates for formal review: provenance-linked evidence claims; a revisable entity-belief lifecycle; explicit policy-gated task create, verify, close, reopen, and reassign actions; task-scoped projections; and causal replay. Do not reuse its claimed implementation, completed architecture, technology stack, fixed thresholds, named algorithms, dataset procurement, benchmark configuration, metrics, results, performance comparisons, security guarantees, or deployment statements as project facts. Every retained concept must be re-evaluated against current sources, project feasibility, and advisor/team confirmation.

## Pre-Approval Adversarial Review

Before the owner chooses a reference mission, an adversarial review is in progress for the tentative project direction. It must assess: feasibility for three members in a 3-4 month development-and-experiment window; the distinct narrow problem and novelty boundary; adherence to active plan/directory authority and the TRACE reference boundary; and fitness of simulator-native observations with M3OT only as an auxiliary real-world perception source. The review cannot approve a mission, create an implementation commitment, or validate fabricated TRACE claims.

The completed adversarial review is retained in `docs/ADVERSARIAL_PREAPPROVAL_REVIEW.md`. It accepts only a narrow deterministic simulator-first MVP: two simulated agents, one entity/region schema, a deterministic claim generator, six-state belief lifecycle, one policy, causal links, fixed-seed replay, and two baselines. It excludes VLMs, training, Re-ID, 3D association, distributed recovery, physical demo, and TRACE performance claims from the first milestone. The owner approved its reference-mission boundary on 2026-10-01; no other technical decision is implied by that approval.

`docs/DATASET_AND_METHOD_REVIEW.md` is the approved-for-proposal Workbook 1 input after research validation and independent adversarial review. It proposes a project-generated, policy-labeled synthetic scenario corpus as primary evaluation data; M3OT is a candidate only for a later input-adapter check. The recommended technical sequence is a simulator-agnostic deterministic core, a falsifiable PX4/Gazebo two-X500 startup spike, then one camera-to-claim adapter. Dataset procurement, local license verification, profiling, simulator selection, the evaluation oracle, and implementation remain pending.

The current copy-ready Workbook 1 development-track draft is `Submissions/WORKBOOK_1_DEVELOPMENT_DRAFT.md`. It covers every chapter in the supplied development template, labels planned work as planned, includes the owner-confirmed role split and schedule, and passed structural, LF/UTF-8, and humanization lexical checks. The owner requested Markdown rather than DOCX authoring; template rendering is additionally unavailable because the bundled document renderer cannot locate `soffice.exe`.

### Submission Audit Exit Criteria

- Extracted files are readable and their requirements, due dates, formatting rules, and rubric criteria are recorded exactly.
- Repository evidence is inventoried without opening or searching excluded `docs/Capstone-TRACE*.md` files or any `.env` file.
- A requirement-to-evidence matrix distinguishes present, partial, missing, and unverifiable items with exact paths.
- Missing inputs that require owner or teammate facts are called out rather than invented.
- Every factual statement in the audit and later drafts must be supported by an exact workspace artifact or confirmed directly by the owner; unsupported inferences remain unresolved.
