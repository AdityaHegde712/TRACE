# Research Direction Status

**Date:** 2026-10-27 **Purpose:** Short status note. Where the research framing stands and why. Not a handoff document and not an approval record.

## Where we are

Sprint 1 remains complete and frozen. No Sprint 2 implementation is authorized. The open question is still which research framing sits on top of the existing deterministic core — not what to build.

Eight rounds of retrieval and adversarial review were run on a candidate framing (see the accompanying document `DEPENDENCE_NOVELTY_SURVEY.md`). The result narrowed the candidate significantly and surfaced three alternatives.

## Candidate framings

| ID  | Framing                                                                                        | Status                                                                                                                                                                                                                                                                                                    |
| --- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B   | Estimate inter-source dependence from claim streams; measure effect on task-lifecycle outcomes | **Withdrawn.** Retrieval found the estimation half occupied (IEEE TKDE 38(1), January 2026), and the claim that correlated errors degrade collective decisions is already established in the multi-agent language-model literature. The study would confirm a known result rather than produce a new one. |
| A   | Port the known between-agent error-correlation statistic into collaborative visual perception and regress it against task-lifecycle outcomes          | **Selected.** Survives the novelty check in weakened form. The statistic is not new and no source asserts the gap; the combination of domain, physical correlation channels, and lifecycle-outcome regression is what is unoccupied. See below.                                                                                                                                                                                 |
| C   | Deadline-aware evidence: stale-but-fast versus fresh-but-slow                                  | **Rejected.** The crossover point is expected to depend on domain and mission urgency, so a result obtained in one simulated setting would not generalize. Low transferable value for the cost.                                                                                                           |
| D   | Score adversarial robustness on task outcomes rather than detection accuracy                   | **Deferred, retained as fallback.** A sound framing, but it duplicates methodology already committed elsewhere in the author's workload and would widen the project into threat modelling. Reconsider if A fails review.                                                                                  |

## Why A is the current candidate

The _General Collaborative Intelligence_ survey (arXiv:2609.22967, 2026) names correlated failure among homogeneous agents as a recognized failure mode and does not evaluate it. **The observation that it is unevaluated is this project's inference, not that survey's assertion** — an earlier version of this document claimed otherwise on the strength of a spliced quotation, and the second adversarial review corrected it.

The measurement itself is not new either: the double-fault statistic (Kuncheva & Whitaker, 2003) is the same quantity. What is absent is its application to a domain where sources observe *different views of a shared scene*, so that correlation is driven by controllable physical channels — occlusion, weather, shared model version, viewpoint overlap — and its regression against task-lifecycle outcomes. The contribution is that port plus the characterization, not a new estimator, fusion rule, or statistic.

## What has not changed

- AD-001 through AD-004 hold. AD-005 was withdrawn on 2026-10-27.
- Sprint 1 carries no frozen status; its implementation, fixtures, and tests may
  be discarded and rebuilt.
- The engineering plan is framing-independent. The deterministic core, the out-of-order replay work (PH-01), the scenario generator, the sweep harness, and the release and demo items (PH-02, PH-03) are required by every candidate framing above and are unaffected by this decision.

## Novelty check result for A (2026-10-27, completed 2026-10-28)

**Survives.** Bounded retrieval, not proof of absence. The check was completed
on 2026-10-28 by removing the two-year recency gate and expanding coverage to
50 works across eight literatures (36 retrieved in full), after eight adversarial review rounds. The seventh literature, classifier-ensemble diversity, contains the statistic this framing uses and was missed by the first two passes. The eighth, dependability and common-cause failure analysis, was searched after round 5 flagged it as the likely counterexample location; it produced no counterexample but did produce the closest prior work in perception (Gottschalk et al., arXiv:2112.04758), which measures error correlation between perception networks and regresses it against voter accuracy. That narrowed the claim a third time. See `DEPENDENCE_NOVELTY_SURVEY.md`.

Supporting:

- A retrieved source in the target domain (GCI survey) names correlated failure
  as a recognized failure mode and does not evaluate it. **That it goes
  unevaluated is this project's inference, not that survey's assertion** — an
  earlier version claimed otherwise on a spliced quotation and was corrected by
  the second adversarial review.
- The statistic is not new: the double-fault measure (Kuncheva & Whitaker, 2003)
  is the same quantity. What is absent is its use in a domain where agents
  observe different views of a shared scene, and its regression against
  task-lifecycle outcomes.
- Existing collaborative-perception benchmarks measure something else. RCP-Bench (CVPR 2025) benchmarks robustness under _corruptions_, not correlated misses.
- STAMP (2025) observes a weaker agent degrading collective performance, but as a case observation rather than a defined metric.
- Inter-agent agreement statistics are **routine** in this domain (GLST, CoDS, LUCIA, MADE), but all are computed over features for adversary detection and scored on detection metrics. None measures correlation of detection *errors*, and none regresses it on task outcomes.
- The statistic itself is occupied (double-fault, Kuncheva & Whitaker 2003) and so is the statistic-to-outcome regression in non-perception multi-agent teams (*Smart Alone, Blind Together* 2026). The perception-domain instantiation is what remains.

Threats found and assessed:

- "Harnessing Disagreement: Detecting Correlated Agreement Blindness in Multi-Agent Triage" (arXiv:2607.19899) studies exactly this phenomenon, and reports a joint error rate inflated 3.53x over independence. **Different domain** - network intrusion detection and clinical readmission, with Random Forest and k-NN, not visual or robotic perception - and it defines indicators rather than releasing a benchmark.
- The LLM multi-agent literature has quantified collaboration deficits (CooperBench, MoltBook, diversity-collapse work). Perception has not.

**Honest limitation:** the concept of correlated failure among agents is established elsewhere, and the completed survey shows how thoroughly. Source dependence has been estimated from categorical claim streams since Dong et al. (VLDB 2009), using a hidden Markov model over time and without ground truth; inter-annotator correlation is modelled in crowdsourcing (EBCC, ICML 2019); and fusion under unknown correlation dates to Julier and Uhlmann (1997). Porting the idea to collaborative visual perception and defining a reusable metric is a legitimate contribution at master's level, but it is a domain-transfer and instrument contribution, not a new phenomenon. It must be presented that way.

**Why framing B did not survive the same test.** The ungated phase found that B's estimator was occupied by that 2009 lineage rather than by a single 2026 paper, which is the difference between a crowded corner and a seventeen-year subfield. A's gap survived the same widening, which is the substantive reason to prefer it.
