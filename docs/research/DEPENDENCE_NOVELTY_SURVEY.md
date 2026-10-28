# Dependence-Estimation Novelty Survey

**Date:** 2026-10-27
**Status:** Retrieved-evidence survey for the proposed Option B research framing.
Not owner-approved. This document tests a candidate claim; it does not authorize
implementation or alter AD-001 through AD-005.

**Method:** Primary-source retrieval with verbatim quotation. Every quotation
below was verified against a locally retained copy of its source using
`.agents/skills/research/scripts/validate_quote.py`. Source recency gate: created
or updated on or after 2024-10-27. Quotations from PDF sources had line-break
hyphenation, whitespace, and typographic ligatures normalized; no wording was
altered.

## Claim under test

> Online estimation of inter-source dependence **from claim streams alone** - no
> cross-covariance, no shared state channel, no ground truth - where the measured
> consequence is **task-lifecycle correctness**, not estimation error.

Three constraints are stacked. Each is tested separately below, because the
claim survives only if no inspected source satisfies all three together.

## Counterexample matrix

### C1. Reliable Truth Discovery for Dynamic and Dependent Sources (IEEE TKDE 38(1), January 2026)

**Establishes:** HMM-based estimation of dependence among sources reporting
conflicting values, including dependence that changes over time.

> "One of the key challenges centers on measuring the dynamic dependence among sources."

> "These models are based on the Hidden Markov Model (HMM) and are designed to handle different types of dependencies"

> "real-world scenarios are often more complex, with dynamic dependence relationships among sources over time"

**Limitation for the candidate claim:** Scored on truth-discovery accuracy
against known object values. The inspected portions describe no action layer, no
verification cost, and no task lifecycle. Not embodied and not visual.

**Disposition: DIRECT COUNTEREXAMPLE to constraints 1 and 2.** Online dependence
estimation from categorical claim streams, using an HMM, is occupied.

### C2. Revisiting Split Covariance Intersection (arXiv:2501.07915, January 2025)

**Establishes:** Conservative fusion when correlation is unknown, plus an
extension that exploits known correlated components.

> "In distributed or cooperative systems, the cross-covariance terms cannot be computed, and to avoid underestimating the estimation error, conservative fusions must be performed."

> "This paper extends SCI to also take advantage of the correlated components."

**Limitation:** Operates on estimators carrying covariance representations.
Bounds correlation rather than estimating it, and scores on covariance
tightness, not on discrete decisions.

**Disposition: NARROW.** Dependence-aware *fusion* is occupied and actively
being optimized. The candidate must not claim it.

### C3. Decentralized Multi-Robot Obstacle Detection and Tracking in a Maritime Scenario (arXiv:2602.12012v2, 2026)

**Establishes:** Multi-robot visual detection with conservative fusion and
uncertainty-driven tasking.

> "Robots exchange compact track summaries that are fused conservatively using Covariance Intersection, preserving estimator consistency under unknown cross-correlations."

> "An information-driven allocator assigns targets and selects UAV hover viewpoints by trading expected uncertainty reduction in travel effort and safety separation."

**It also has a task and entity lifecycle.** An earlier draft of this survey
claimed it did not. That was wrong on the retained text, which contains
"EKF-based track management" with explicit track pruning, an assignment state
machine where "NA indicates no assignment", and an anti-churn term: the
allocator includes a stickiness reward "to reduce assignment chattering"
(the reward's notation is omitted here because the retrieved HTML renders its
mathematics unreliably). It is evaluated on discrete lifecycle-correctness
metrics:
"our approach achieved perfect identity continuity with low fragmentation and
good accuracy." Fragmentation and identity continuity are structurally the same
family of measure as false closure and incorrect reopening.

**The one limitation that survives:** it *bounds* correlation conservatively via
Covariance Intersection rather than *estimating* it, and therefore never
regresses a dependence estimate against its lifecycle outcomes.

**Disposition: CLOSEST SYSTEM-LEVEL COUNTEREXAMPLE.** It combines visual
multi-robot evidence, unknown-correlation fusion, expected-uncertainty-reduction
tasking, an assign/reassign lifecycle, and lifecycle-correctness scoring. PD-003
cannot be claimed as new. This source constrains the candidate claim far more
tightly than the rest of the matrix.

### C4. KC-Bench (arXiv:2609.03588, September 2026)

**Establishes:** A benchmark scoring whether agents reconcile conflicting
information before acting.

> "they must reconcile user instructions, parametric knowledge, and dynamic environmental observations before taking actions"

**Limitation:**

> "KC-Bench isolates this model-level behavior rather than ranking complete agent frameworks"

Text and tool domains, not multi-agent visual evidence. No dependence or
correlation axis.

**Disposition: NARROW.** Scoring conflict handling by downstream action
consequences is occupied in the LLM-agent setting.

### C5. General Collaborative Intelligence (arXiv:2609.22967, 2026)

**Establishes:** Motivating evidence that correlated failure is a real
multi-agent perception problem.

> "homogeneous agents with identical perception models and similar viewpoints are susceptible to correlated failures, where all agents miss the same occluded entity; collaboration does not help when the collective shares a common blind spot."

It also supplies the strongest available statement that the evaluation gap
this project targets is real:

> "this phenomenon is documented in early work on Byzantine-resilient fusion" ... "but is rarely evaluated as a benchmark metric."

(The elision is a citation marker. The phenomenon referred to is a fused
collective world model becoming worse than what each agent would achieve
independently.)

**It is not only a survey.** An earlier draft of this survey said it supplied no
evaluation. That was wrong: "we propose GCI-Bench, a five-pillar scoring protocol
with a maturity model that makes the trade-offs of collaborative methods
comparable across studies."

**It also describes claim-stream-only reliability estimation and
independence-conditioned gating.** Trust-aware fusion frameworks "address this by
assigning time-varying reliability scores to each node based on latency, spatial
consistency, and historical performance" — no ground truth, no cross-covariance.
And it describes ROBOSAC [96], "accepting only detections confirmed by multiple
independent viewpoints to filter out spoofed data."

**Disposition: LEAD-BEARING COUNTEREXAMPLE, not motivation.** Per-source
reliability is not inter-source dependence, and accept/reject is not a five-state
task lifecycle — but independence-conditioned discrete action gating in a visual
multi-agent setting is materially closer to constraint 3 than this survey first
conceded. ROBOSAC (2023) and refs [106]-[108] must be inspected before the
constraint-3 verdict is relied on.

## Verdict by constraint

1. **Dependence estimation from categorical claim streams** - **OCCUPIED.** C1
   does this with HMMs, including dependence that changes over time.
   **Correction:** an earlier draft called this "online" estimation and labelled
   it a source claim. The word "online" appears twice in the retained C1 text,
   neither describing C1's own method; one refers to a *different* cited work.
   C1 extracts dependence via the Viterbi algorithm, which decodes a complete
   observation sequence. Whether C1 operates in a streaming regime was **not
   established** from the inspected text. "Dynamic" is the source's claim;
   "online" was this survey's inference.
2. **Without cross-covariance or ground truth** - **OCCUPIED.** The
   covariance-intersection line (C2, C3) avoids needing cross-covariance by
   presuming partial structural knowledge of it; C1 estimates dependence without
   ground truth; C5 describes time-varying per-node reliability from the stream
   alone.
3. **Scored on task-lifecycle correctness and verification cost** - **NOT FOUND
   OCCUPIED in combination with 1 and 2, on bounded and incomplete evidence.**
   C4 scores action consequences but the inspected abstract shows no dependence
   axis. C3 has the visual setting, the lifecycle, *and* lifecycle-correctness
   scoring, and is excluded on one ground only: it bounds correlation rather
   than estimating it, so it never relates a dependence estimate to those
   outcomes. C5 describes independence-conditioned gating and is an open threat.

**Inference** (derived, not asserted by any source): on the inspected evidence,
the most defensible candidate contribution appears to be neither the estimator
nor the fusion rule, but the measured link between an *estimated* inter-source
dependence and *discrete task-lifecycle errors* - false closure, incorrect
reopening, and verification trips - in a multi-agent visual setting.

**Falsifier.** A single retrieved source that regresses an estimated
inter-source dependence against discrete task or track lifecycle outcomes in a
multi-agent perception setting would close this gap. ROBOSAC (2023) and the
closed-loop collaborative-perception evaluation line are the most likely
candidates and have **not** been inspected.

## Consequences for the project

- PD-001 (HMM resolver) must not be presented as novel. C1 uses HMMs for exactly
  this family of problem.
- PD-003 (value-of-information gate) must not be presented as novel. C3 already
  allocates by expected uncertainty reduction.
- AD-004 remains the right constraint, but dependence-aware fusion is an
  occupied solution space. The project should adopt an existing dependence
  treatment and measure its task-level consequence, rather than propose a new
  fusion rule.

## Explicit non-claims

- Not a new fusion operator, and not an improvement on covariance intersection.
- Not a new dependence estimator; an existing formulation should be adopted.
- Not a claim that correlated evidence degrades task decisions; that is the
  hypothesis to be measured, not an established result.
- Not a field-first claim. This is bounded retrieval over the sources listed
  below.

## Limitations of this survey

**This survey has not completed its adversarial-review cycle.** It was reviewed
once, failed, and was corrected on the points above. The constraint-3 verdict
has not yet been re-tested against the leads the review surfaced.

- **Three of five sources were read partially.** C1: first six pages of
  thirteen; its scoring on truth-discovery accuracy is supported by its
  abstract, not by its experiments section. **C4: the arXiv abstract page only
  (~6 KB)** — the claim that it has no dependence axis is made from ~200 words,
  and its abstract does list "multi-source temporal conflicts", a category that
  could involve correlated sources. C5: mined selectively from ~1 MB.
- **The recency gate is a search budget, not a novelty boundary.** It distorts in
  both directions. It excludes the foundational covariance-intersection and
  data-incest literature. It also hides that constraint 1 is not a 2026 result:
  C1's own abstract notes that "Existing studies primarily focus on dependent
  sources with conflicting information, where sources may copy information from
  each other" — a lineage running back to the VLDB 2009 copy-detection work.
  Most damagingly, ROBOSAC (2023) sits inside C5, is pre-gate, and bears
  directly on constraint 3.
- Searches were English-language against general web indexes, not a systematic
  database protocol. This is bounded search evidence, not proof of absence.

## Open actions before this survey is citable

1. Inspect ROBOSAC (ICCV 2023) and C5 refs [106]-[108].
2. Run an ungated search on constraint 3 specifically: closed-loop
   collaborative-perception evaluation (V2X-Sim and successors), and V2X
   misbehaviour detection, checking whether any models *inter-source* dependence
   rather than per-source reliability.
3. Retrieve the KC-Bench full paper before any claim about its dependence axis.
4. Resolve C1's reference [20], described there as "A novel online truth
   discovery framework", which bears directly on the online-versus-dynamic
   correction above.

## Sources

1. Zhang, H., Wang, S., Chen, L., Li, X., Gao, Q., Sheng, Q. Z. "Reliable Truth Discovery for Dynamic and Dependent Sources." *IEEE Transactions on Knowledge and Data Engineering* 38(1), January 2026. http://web.science.mq.edu.au/~qsheng/papers/TKDE-2026-truth-discovery.pdf
2. "Revisiting Split Covariance Intersection: Correlated Components and Optimality." arXiv:2501.07915, January 2025. https://arxiv.org/abs/2501.07915
3. "Decentralized Multi-Robot Obstacle Detection and Tracking in a Maritime Scenario." arXiv:2602.12012v2, 2026. https://arxiv.org/html/2602.12012v2
4. Lyu, Y., Zhou, S., Toh, B., Zhu, P., Li, L. "KC-Bench: A Dynamic Interactive Benchmark for Evaluating Knowledge Conflicts in LLM Agents." arXiv:2609.03588, September 2026. https://arxiv.org/abs/2609.03588
5. "General Collaborative Intelligence: Architecting Cognition for Resilient Multi-Agent Ecosystems." arXiv:2609.22967, 2026. https://arxiv.org/abs/2609.22967

**Consulted but not quoted:** DIFNet (arXiv:2508.18854, August 2025); Overlapping
Covariance Intersection (arXiv:2603.16768v2, 2026).
