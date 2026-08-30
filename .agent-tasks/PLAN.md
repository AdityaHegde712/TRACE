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

The direction proposal is complete at `docs/DIRECTION_PROPOSAL.md`. `docs/MARKET_VALIDATION_SUMMER_2027.md` rates the proposed technical work's market alignment 4/5; the separate 3/5 rating concerns current specialized new-grad role availability, not the project name. It proposes multi-drone incident response and critical-infrastructure inspection as the evaluation anchor. The direction and anchor remain pending owner, team, and faculty approval. No implementation or detailed system design is authorized until that review is complete.

## Prerequisite Study Guide

`docs/KNOWLEDGE_TRANSFER.md` is a project-specific study guide adapted from the owner’s IAS coursework material. It is not research evidence or a design commitment. It covers the prerequisite chain from multi-agent partial observability through ROS 2/Gazebo integration, visual evidence versus belief state, event-driven task gating, and evaluation baselines. It should be read before the approval discussion or a later implementation phase.
