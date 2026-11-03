# When Agreement Is Not Evidence

## Measuring correlated failure in multi-agent visual evidence resolution

**Author:** Aditya Hegde **Advisor:** Dr. Kaikai Liu **Date:** 2026-10-27 **Status:** Proposal for advisor review. Not an implementation commitment.

---

## The problem

A team of drones inspects a road for a blockage. Drone A reports a blockage. Drone B independently confirms it. The system closes the inspection task, because two sources agreed.

That inference is only valid if the two reports are independent. If both drones run the same detector, view the same scene through the same occluder, or operate under the same lighting, their errors are not independent. They can agree and be wrong together. Agreement then looks like evidence while carrying almost none.

This is not a hypothetical concern for this project. The existing prototype encodes the assumption directly, in code written without anyone noticing the problem:

```python
# src/evidence_resolution/policy.py
has_independent_positive = any(
    item.source_id != claim.source_id for item in snapshot.positive_claims
)

if claim.assertion == "present" and has_independent_positive: return PolicyDecision( belief_status="verified", action="close", reason_code="independent_confirmation_verifies_blockage", ... )
```

Different source identity is taken to mean statistical independence, and a task is closed on that basis. The reason code says `independent_confirmation`, but nothing establishes independence. This is what a competent engineer writes by default, which is precisely why it is worth measuring. The project's own accepted constraint AD-004 states that correlated or repeated evidence must not be treated as independent, but nothing in the system currently tests when that assumption breaks or what it costs when it does.

## The gap

Stating this precisely matters, because an earlier draft overstated it and a
second adversarial review caught the overstatement.

A 2026 survey of collaborative multi-agent perception, *General Collaborative
Intelligence* (arXiv:2609.22967), names the failure mode directly:

> "homogeneous agents with identical perception models and similar viewpoints
> are susceptible to correlated failures, where all agents miss the same
> occluded entity; collaboration does not help when the collective shares a
> common blind spot."

That survey also states that "Systematic study of these failure modes, and of the conditions under which they dominate, remains an open research need" - a sentence covering four failure modes jointly, not correlated failure alone. It defines no measure, and GCI-Bench has no pillar for inter-agent failure correlation. **It does not assert that correlated failure specifically is unmeasured**, and this proposal does not claim that it does. (An earlier draft spliced a nearby
clause — "rarely evaluated as a benchmark metric" — onto this sentence. In the
source, that clause describes a different failure mode, error propagation from a
compromised agent. The correction is recorded in the accompanying survey.)

**What the statistic is, and who already has it.** The measurement is not new.
Kuncheva and Whitaker (*Machine Learning* 51(2), 2003) define the **double-fault
measure**: "the proportion of the cases that have been misclassified by both
classifiers", one of ten ensemble-diversity measures they study against ensemble
accuracy. Giacinto and Roli used it to build pairwise diversity matrices in 2001.
A 2026 paper on correlated agreement blindness applies the same idea to agent
pipelines, reporting joint error inflated 3.53 times over independence
(BCa 95% CI [3.50, 3.59]) — on network intrusion detection and clinical tabular
data, with no benchmark released.

**What is missing is the domain, not the statistic.** An earlier draft justified
this by claiming that every literature measuring between-source error
correlation assumes sources observe *identical input*. That was wrong, and
independent review refuted it from this project's own sources: Kuncheva and
Whitaker sweep "different subsets of features for each of L = 3 classifiers",
Pochampally et al. note that "extractors may focus on different types of
information", and the N-version literature attributes coincident failure to inputs differing in difficulty. (That last characterization is routed through *Smart Alone, Blind Together*, which cites Eckhardt & Lee; Eckhardt & Lee itself was not retrieved.)

The distinction that survives is the **conjunction** - embodiment alone is not unoccupied, and it is narrower than three earlier versions of this paragraph claimed. Those versions said, in turn, that the other literatures use identical input, that their correlation is observed rather than set, and that it is never reached through a shared world. Independent review refuted each in turn from this project's own sources — most recently Gottschalk et al., who rotate a shared 3D object and give each of five networks a different view with the networks held identical.

What no retrieved work provides is **distributed agents in a real shared scene, with occlusion, weather, viewpoint geometry and detector version as separately actuable channels varied orthogonally inside one experiment**. Gottschalk's viewpoint knob is a synthetic rotation of a toy dataset on one platform with a single channel varied; RCP-Bench switches which agents a corruption lands on but defines no correlation statistic. In collaborative visual perception
the correlation channels are **physically actuated and independently
controllable within a shared three-dimensional scene**: an occluder can be
placed, weather dialled, viewpoint geometry swept, detector version held or
varied — each independently of the others, in one experiment, with ground truth
available for scoring. Gamerdinger et al. (Springer 2024) document that "adverse
weather conditions such as rain, snow, and fog, as well as soiled sensors"
degrade detectors; that such conditions therefore correlate failures across
co-located agents is an inference, not their claim.

That makes the question experimental rather than observational: which physical
configuration drives the statistic, and does the statistic predict task-level
error? The channel taxonomy is not original either — the maritime multi-robot
system lists "shared priors, overlapping observations, common process models,
and information relaying" as its sources of unknown cross-correlation. What it
does not do is measure them.

**The nearest work in the target domain, and why it does not close the gap.**
Inter-agent agreement statistics are in fact **routine** here. GLST (2026)
computes a pairwise inter-agent distance matrix; CoDS (2026) uses inter-agent
feature variance; LUCIA (USENIX Security 2025) converts pairwise feature
distances into collaborator trust; MADE (2023) runs a double-hypothesis
consistency test per collaborator. All four compute them over *features*, to
identify adversaries, and score detection metrics — none measures correlation of
detection *errors*, and none relates it to task outcomes.

RCP-Bench (CVPR 2025) already varies which agents degrade, defining "three
interference scenarios: Global, Ego, and CA[V] Interference" and reporting that
"perception models are particularly vulnerable to Global Interference" — the
regime where ego and collaborating vehicles degrade together. But it defines no
correlation statistic and relates none to outcomes. A 2026 multi-robot maritime
system has the visual setting, a task lifecycle, and lifecycle-correctness
scoring, but *bounds* correlation conservatively via covariance intersection
rather than estimating it.

**The closest work in any domain is not in perception at all.** *Smart Alone,
Blind Together* (2026) defines an effective-redundancy statistic, measures teams
"all wrong together far more often than independence allows: 4.7 to 18.6 times for the Claude models",
and states its aim as "we ask what agreement does to a team that acts on its
beliefs" — which is this proposal's question, in Hanabi and task assignment
rather than perception. It is separated from this work **only by modality**, and
it is named first in the withdrawal condition below for that reason.

So the open question is not whether a known statistic transfers, which would be
uninteresting. It is **what physical configuration drives that statistic, and
whether it predicts task-level error.** That question can only be asked in this
domain, and on bounded retrieval across 50 works in eight literatures, nobody
has asked it.

## What we propose to build

A benchmark and measurement harness for correlated failure in multi-agent visual evidence resolution, reusing the validated design of the existing prototype (see Feasibility below) rather than assuming its code carries over intact.

1. **A scenario generator with controlled dependence.** Scenarios are produced from a latent scene model so that the degree and the _source_ of correlation between agents are set deliberately rather than observed accidentally. The planned correlation channels are shared occluder, shared detector model version, shared viewpoint geometry, and shared illumination.
2. **An adopted dependence measure, computed from claim streams alone.** The candidate is a joint-error inflation factor: the observed joint error rate between two agents divided by the rate independence would predict. This is the double-fault measure of Kuncheva and Whitaker (2003) expressed as a ratio, and it is adopted rather than invented. It requires no cross-covariance and no access to simulator truth at resolution time.
3. **An agreement-reliability measure.** The probability that a claim is correct given that two or more sources agree, reported as a function of the dependence inflation factor. This is the measure the project actually needs, because agreement is the signal every fusion policy consumes.
4. **Task-outcome scoring.** Collaboration gain relative to the best single agent, plus false task closure, incorrect reopening, and verification cost. Simulator truth is used for scoring only and never enters resolution, per AD-001.

## What the experiment would show

The study sweeps dependence from independent to fully correlated across the four correlation channels and reports where the independence assumption stops paying for itself. Concretely, it answers:

- At what dependence level does a second confirming report stop reducing the false-closure rate?
- Does the dependence inflation factor, computed without ground truth, predict that breakdown well enough to act on?
- Do the four correlation channels degrade decisions equivalently, or does shared model version behave differently from shared viewpoint?

The outcome is a characterization and a reusable instrument, with a stated operating boundary for the naive-independence baseline and its successors.

## What we are not claiming

- Not a new fusion operator, and not an improvement on covariance intersection or any existing conservative fusion method.
- Not the discovery of correlated failure. The phenomenon is established in other domains; this work ports it to collaborative visual perception and supplies the missing measurement.
- Not a formal safety, calibration, or real-world operational claim. Results will establish decision-policy behavior in simulation only.
- Not a field-first claim. The novelty assessment is bounded search evidence. Its method, its eight rounds, and the errors the adversarial pass caught are documented below and in the accompanying document `DEPENDENCE_NOVELTY_SURVEY.md`.

## How this framing was tested before proposing it

This proposal is the second framing considered, not the first. Both were put through adversarial novelty passes before reaching you - eight independent review rounds in total, each of which found real errors. The full record is in the accompanying documents `DEPENDENCE_NOVELTY_SURVEY.md` and `DIRECTION_STATUS.md`.

**Method.** Primary-source retrieval, with every quotation verified verbatim against a locally retained copy of its source using a regex validation script. Claims directly asserted by a source are separated from inferences derived here. Findings were then handed to an independent adversarial reviewer instructed to attack rather than approve, and every objection it raised was re-verified against the source text before being accepted.

**Round 1 — the first framing failed.** The original candidate was online estimation of inter-source dependence, scored on task-lifecycle outcomes. Retrieval found the estimation half occupied by an IEEE TKDE paper from January 2026 performing HMM-based estimation of dynamic source dependence from categorical conflicting reports, and a 2026 multi-robot maritime system already combining visual evidence, unknown-correlation fusion, and tasking by expected uncertainty reduction, which removed the novelty of the proposed value-of-information gate.

The ungated phase later showed this verdict had been understated. Source dependence has been estimated from categorical claim streams since Dong, Berti-Équille and Srivastava (VLDB 2009), whose method is "a Hidden Markov Model that decides whether a source is a copier of another source and identifies the specific moments at which it copies" — time-varying, without ground truth, seventeen years before the paper originally cited as the counterexample. Fusion under unknown correlation dates to Julier and Uhlmann (1997), and inter-annotator correlation is modelled in crowdsourcing (EBCC, ICML 2019). The first framing was not competing with one recent paper; it was competing with three mature literatures.

**The adversarial pass rejected the base survey.** The literature survey was drafted first and is referred to here as the base survey. It was submitted to an independent adversarial reviewer agent, which was instructed to attack the survey's reasoning rather than approve it, and which returned a verdict of NEEDS REVISION with five blocking issues. Four were re-verified directly against the retained source text and corrected in the survey:

1. The base survey claimed that a counterexample system had no task lifecycle. The source text contradicts this. That system implements track management, an assign and reassign state machine, an explicit anti-chattering term, and evaluation on fragmentation and identity continuity. Its exclusion was rewritten to rest on the single ground that survives: it bounds correlation conservatively rather than estimating it.
2. The base survey described a source's method as "online" and labelled that a source claim. The source claims "dynamic," not "online," and extracts dependence via the Viterbi algorithm, which decodes a complete observation sequence. "Online" was an inference presented as an assertion.
3. The base survey dispositioned a 2026 survey as supportive motivation. That survey in fact proposes its own benchmark (GCI-Bench) and assigns the correlated-failure case to one of its named synergy conditions, which makes it a threat to the claim rather than support for it. It was re-dispositioned accordingly.
4. The base survey made negative claims about a benchmark from its abstract page alone, without disclosing the partial read. The disclosure was added.

Two quotations also failed verbatim validation, caused by mangled mathematical notation and a citation bracket in the retrieved text. Both were restated in verified wording. The full record, including the corrections, is retained in the accompanying document `DEPENDENCE_NOVELTY_SURVEY.md`.

**A fifth finding changed the survey's basis.** The reviewer identified that a two-year source recency gate, adopted as a search budget, was concealing the foundational literature. The gate was removed and the survey re-run without it. Coverage went from five sources to **50 works across eight literatures**: distributed estimation and track fusion, database truth discovery, crowdsourcing label aggregation, collaborative perception, multi-agent language models, closed-loop evaluation, **classifier-ensemble diversity** (which supplies the statistic this proposal adopts), and **dependability / common-cause failure analysis** (which supplies the closest prior work in perception). 26 were retrieved and searched directly at that stage, 36 after further review rounds; the rest are marked in the bibliography as dispositioned from abstracts or cited from within retrieved papers.

**A second independent review rejected the expanded survey.** It found a
spliced quotation on the single most load-bearing citation — two fragments of
*General Collaborative Intelligence* joined across an ellipsis so that "rarely
evaluated as a benchmark metric" appeared to describe correlated failure, when
in the source it describes a different failure mode and terminates before the
correlated-failure sentence begins. Each fragment passed string validation
individually; the splice did not, which is why string validation alone is now
treated as insufficient for any quotation spanning an ellipsis. The review also
found a mislabeled retrieval, a factually wrong exclusion ground for one
counterexample, and an entire literature the survey had missed — classifier-
ensemble diversity, which contains the statistic this proposal uses. All are
corrected, and coverage expanded again to 50 works across eight literatures, 36 retrieved in full.

**Rounds 3 through 8 followed**, each independent, each finding real errors: a misattributed quotation, a self-refuting replacement argument, an incomplete bibliography, and two over-strong universals. One round-4 finding was rejected with evidence. The full record, including the rejected finding, is in the accompanying survey's *What the adversarial reviews caught* section.

**The framing survived all eight rounds, in progressively weakened form.** The gap is **this project's inference** from the retrieved set, not a claim borrowed from any source. The nearest threat in any domain is *Smart Alone, Blind Together* (see the withdrawal condition below). Next nearest, a 2026 paper on correlated agreement blindness reporting joint error inflated 3.53 times over independence, operates on network intrusion detection and clinical tabular data with classical models, not visual perception, and defines indicators rather than releasing a benchmark. The nearest pre-gate threat, ROBOSAC (ICCV 2023), was retrieved in full and contains no treatment of correlation at all — correcting a description the survey had inherited from a third source rather than read directly. The nearest system-level counterexample bounds correlation via covariance intersection and never estimates it, so it never relates a dependence estimate to the task outcomes it does measure.

**The eighth literature was searched, and it narrowed this claim.** Dependability and common-cause failure analysis - IEC 61508 beta-factor models, shock models, SOTIF redundancy - was initially flagged as unsearched and as the most likely place a counterexample would sit. It was then searched. It produced no counterexample, but it produced **the closest prior work in perception**:

> Gottschalk, Rottmann & Saltagic, *Does Redundancy in AI Perception Systems Help to Test for Super-Human Automated Driving Performance?* (arXiv:2112.04758, 2021)

That paper measures error correlation between redundant perception networks, gives each network a **different rotation of a shared 3D object** so that viewpoint is an actuated knob with the networks held identical, and regresses the measured correlation against **k-out-of-5 voter accuracy**. It concludes that independence "cannot be taken simply for granted, even if different sources of data are employed".

Three things still separate it from this proposal, and they are now the whole of the separation: it runs **redundant networks on one platform**, not distributed agents; it uses **synthetic rotations of a toy dataset** (3D-MNIST), not a real shared scene with occlusion and weather as independent channels; and it scores **voter accuracy**, a perception metric, not task-lifecycle outcomes. That is a thinner separation than this proposal previously claimed, and it is stated plainly rather than defended.

**What remains limited**, and is stated with the survey: bounded English-language retrieval against general web indexes and arXiv rather than a systematic database protocol with recorded query strings; varying depth per source, marked in place; and three works cited from within other papers rather than independently retrieved. It is bounded search evidence, not proof of absence, and the survey states the single finding that would close the gap.

## Honest limitation

The contribution is a **domain transfer plus a regression**, and it is narrower
than two earlier drafts of this document claimed. Stated at the strength the
evidence supports:

- Correlated failure among agents is **not a new phenomenon**. It is established
  in distributed estimation (1997), database truth discovery (2009),
  crowdsourcing (2012-2019), multi-version software (1986) and classifier
  ensembles (2003).
- The **statistic is not new**. The double-fault measure is 23 years old.
- No source **asserts** the gap. That correlated failure goes unevaluated in
  collaborative visual perception is this project's inference from the
  retrieved set, not a claim borrowed from a survey.

What remains defensible: no retrieved source relates a between-agent
error-correlation statistic to task-lifecycle outcomes in collaborative visual
perception, where correlation is driven by physical channels that have no
analogue in the literatures that already measure it. Building that measurement
and characterizing where it predicts decision error is the contribution.

**Withdrawal condition.** If a reviewer finds work computing an
error-correlation statistic between agents over **perceptual detections of a
shared physical scene** and relating it to task or track lifecycle outcomes,
this framing should be withdrawn or narrowed. The nearest misses, ordered by how
close they come:

1. ***Smart Alone, Blind Together*** (2026) — the closest in any domain. It has
   both halves of the conjunction and is separated from this work only by
   modality (Hanabi and task assignment; zero occurrences of "visual" or
   "perception").
2. **Agent Behavioral Contracts II** (2026) — the conjunction outside perception, and
   the strongest on the outcome side: 18,000 preregistered missions, two agents
   co-failing on 90.0% of missions where either fails. Zero perception content.
3. **Gottschalk, Rottmann & Saltagic** (2021) — the closest in perception. Measures error correlation between perception networks with viewpoint as an
   actuated knob, regressed against voter accuracy. Separated by one platform,
   toy data, and a perception metric rather than task outcomes.
4. **Harnessing Disagreement** (2026) — the statistic and a downstream link, on
   tabular intrusion-detection and clinical data; no released benchmark.
5. **GLST / CoDS / LUCIA / MADE** — inter-agent statistics in this domain, but
   over features, for adversary detection, scored on detection metrics.
6. **RCP-Bench** (2025) — joint-degradation regimes, but no statistic.
7. **Maritime multi-robot** (2026) — the setting, a lifecycle, and
   lifecycle-correctness scoring, but it bounds correlation rather than
   estimating it.

That the domain qualifier carries the claim is stated plainly rather than
hidden; a reader who disputes that the perception setting is materially
different should reject this framing.

## Feasibility

A working prototype exists: typed claim and trace contracts, a replaceable policy interface, four oracle scenarios, deterministic replay verified by matching SHA-256 trace hashes, and a command-line harness. It was built in a single session. It is treated as disposable, and carries no frozen status.

What it establishes is that the design is sound, and three design decisions carry forward independently of the code that currently implements them:

1. **A single policy seam.** Comparison policies plug in behind one interface, which is what makes a baseline sweep cheap to run.
2. **A naive-independence baseline.** A policy that treats a differing source identifier as statistical independence is exactly the assumption this study measures, so one will exist in the comparison set. The prototype shows that rule is what a reasonable engineer writes by default, which is the point.
3. **Separation of simulator truth from the agent-visible claim stream**, on which the whole evaluation depends (AD-001).

The implementation itself is expected to be rebuilt rather than extended, for concrete reasons. The current claim record carries a single observation timestamp and no arrival time, so it cannot express late or out-of-order delivery, which this study must control for in order to avoid confounding ordering effects with dependence effects. The four existing scenarios exercise support, contradiction, and staleness; none exercises correlation between agents, so a new corpus is required regardless.

This is a deliberate position rather than a concession. The project's risk was never implementation volume; it is whether the measurement is well defined. A prototype this small is cheaper to rebuild against a clear specification than to bend toward a purpose it was not designed for, and rebuilding removes any pressure to preserve decisions that were convenient rather than correct.

The work requires no new simulator dependency, no flight hardware, and no perception training. The PX4 and Gazebo spike remains optional and off the critical path.

## Requested decision

Approval to proceed to a design phase for this framing: freeze the dependence measure, the correlation channels, the scenario matrix, and the acceptance thresholds. Implementation remains a separate approval gate.
