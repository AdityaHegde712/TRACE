# Research Direction Status

**Date:** 2026-10-27
**Purpose:** Short status note. Where the research framing stands and why.
Not a handoff document and not an approval record.

## Where we are

Sprint 1 remains complete and frozen. No Sprint 2 implementation is authorized.
The open question is still which research framing sits on top of the existing
deterministic core — not what to build.

Two rounds of retrieval and adversarial review were run on a candidate framing
(see the accompanying document `DEPENDENCE_NOVELTY_SURVEY.md`). The result
narrowed the candidate significantly and surfaced three alternatives.

## Candidate framings

| ID | Framing | Status |
| --- | --- | --- |
| B | Estimate inter-source dependence from claim streams; measure effect on task-lifecycle outcomes | **Withdrawn.** Retrieval found the estimation half occupied (IEEE TKDE 38(1), January 2026), and the claim that correlated errors degrade collective decisions is already established in the multi-agent language-model literature. The study would confirm a known result rather than produce a new one. |
| A | Build the missing benchmark metric for correlated failure in collaborative perception | **Selected.** Survives the novelty check. The gap is asserted by a retrieved source rather than inferred here. See below. |
| C | Deadline-aware evidence: stale-but-fast versus fresh-but-slow | **Rejected.** The crossover point is expected to depend on domain and mission urgency, so a result obtained in one simulated setting would not generalize. Low transferable value for the cost. |
| D | Score adversarial robustness on task outcomes rather than detection accuracy | **Deferred, retained as fallback.** A sound framing, but it duplicates methodology already committed elsewhere in the author's workload and would widen the project into threat modelling. Reconsider if A fails review. |

## Why A is the current candidate

The *General Collaborative Intelligence* survey (arXiv:2609.22967, 2026) states
that a fused collective world model becoming worse than independent single-agent
performance "is rarely evaluated as a benchmark metric." The gap is asserted by a
retrieved source rather than inferred by this project. The contribution becomes
the measuring instrument and the characterization, not a new estimator or fusion
rule.

## What has not changed

- AD-001 through AD-005 hold.
- Sprint 1 fixtures and oracle assertions remain frozen.
- The engineering plan is framing-independent. The deterministic core, the
  out-of-order replay work (PH-01), the scenario generator, the sweep harness,
  and the release and demo items (PH-02, PH-03) are required by every candidate
  framing above and are unaffected by this decision.

## Novelty check result for A (2026-10-27)

**Survives.** Bounded retrieval, not proof of absence.

Supporting:
- The gap is asserted by a retrieved source, not inferred here (GCI survey).
- Existing collaborative-perception benchmarks measure something else. RCP-Bench
  (CVPR 2025) benchmarks robustness under *corruptions*, not correlated misses.
- STAMP (2025) observes a weaker agent degrading collective performance, but as
  a case observation rather than a defined metric.
- ARCV measures complementarity between agents; no retrieved metric measures
  redundancy or failure correlation.

Threats found and assessed:
- "Harnessing Disagreement: Detecting Correlated Agreement Blindness in
  Multi-Agent Triage" (arXiv:2607.19899) studies exactly this phenomenon, and
  reports a joint error rate inflated 3.53x over independence. **Different
  domain** - network intrusion detection and clinical readmission, with Random
  Forest and k-NN, not visual or robotic perception - and it defines indicators
  rather than releasing a benchmark.
- The LLM multi-agent literature has quantified collaboration deficits
  (CooperBench, MoltBook, diversity-collapse work). Perception has not.

**Honest limitation:** the concept of correlated failure among agents is
established elsewhere. Porting it to collaborative perception and defining a
reusable metric is a legitimate contribution at master's level, but it is a
domain-transfer and instrument contribution, not a new phenomenon. It must be
presented that way.

## Next action

Draft the advisor-facing proposal for framing A.
