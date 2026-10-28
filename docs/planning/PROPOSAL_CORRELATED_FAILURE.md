# When Agreement Is Not Evidence

## Measuring correlated failure in multi-agent visual evidence resolution

**Author:** Aditya Hegde
**Advisor:** Dr. Kaikai Liu
**Date:** 2026-10-27
**Status:** Proposal for advisor review. Not an implementation commitment.

---

## The problem

A team of drones inspects a road for a blockage. Drone A reports a blockage.
Drone B independently confirms it. The system closes the inspection task,
because two sources agreed.

That inference is only valid if the two reports are independent. If both drones
run the same detector, view the same scene through the same occluder, or operate
under the same lighting, their errors are not independent. They can agree and be
wrong together. Agreement then looks like evidence while carrying almost none.

This is not a hypothetical concern for this project. The existing prototype
encodes the assumption directly, in code written without anyone noticing the
problem:

```python
# src/evidence_resolution/policy.py
has_independent_positive = any(
    item.source_id != claim.source_id for item in snapshot.positive_claims
)

if claim.assertion == "present" and has_independent_positive:
    return PolicyDecision(
        belief_status="verified",
        action="close",
        reason_code="independent_confirmation_verifies_blockage",
        ...
    )
```

Different source identity is taken to mean statistical independence, and a task
is closed on that basis. The reason code says `independent_confirmation`, but
nothing establishes independence. This is what a competent engineer writes by
default, which is precisely why it is worth measuring. The project's own accepted constraint
AD-004 states that correlated or repeated evidence must not be treated as
independent, but nothing in the system currently tests when that assumption
breaks or what it costs when it does.

## The gap

A 2026 survey of collaborative multi-agent perception states the problem and
states that it is unmeasured. The source for both quotations below is *General
Collaborative Intelligence: Architecting Cognition for Resilient Multi-Agent
Ecosystems* (arXiv:2609.22967, 2026). On correlated failure, that survey states:

> "homogeneous agents with identical perception models and similar viewpoints
> are susceptible to correlated failures, where all agents miss the same
> occluded entity; collaboration does not help when the collective shares a
> common blind spot."
>
> — *General Collaborative Intelligence*, arXiv:2609.22967

And on the state of evaluation, the same survey describes the case where a fused
collective model becomes worse than what each agent would achieve independently:

> "this phenomenon is documented in early work on Byzantine-resilient fusion"
> ... "but is rarely evaluated as a benchmark metric."
>
> — *General Collaborative Intelligence*, arXiv:2609.22967
> (the elision is a citation marker)

A bounded primary-source search supports that assessment for this domain.
RCP-Bench (CVPR 2025) benchmarks collaborative perception robustness under
sensor corruptions such as noise and weather, not under correlated failure
between agents. STAMP (2025) observes a weaker agent degrading collective
performance, but reports it as a case observation rather than defining a
measure. The existing cross-agent metric, Average Recall of Collaborative View,
scores what collaboration adds, not what redundancy conceals.

The phenomenon has been quantified outside perception. Work on correlated
agreement blindness in multi-agent triage reports a joint error rate inflated
3.53 times over what independence predicts, on network intrusion detection and
clinical data using classical models. Parallel results exist in multi-agent
language model research. Neither line addresses visual multi-agent perception,
and neither releases a reusable benchmark.

## What we propose to build

A benchmark and measurement harness for correlated failure in multi-agent visual
evidence resolution, reusing the validated design of the existing prototype (see
Feasibility below) rather than assuming its code carries over intact.

1. **A scenario generator with controlled dependence.** Scenarios are produced
   from a latent scene model so that the degree and the _source_ of correlation
   between agents are set deliberately rather than observed accidentally. The
   planned correlation channels are shared occluder, shared detector model
   version, shared viewpoint geometry, and shared illumination.
2. **A dependence measure computed from claim streams alone.** The primary
   candidate is a dependence inflation factor: the observed joint error rate
   between two sources divided by the joint error rate independence would
   predict. It requires no cross-covariance and no access to simulator truth at
   resolution time.
3. **An agreement-reliability measure.** The probability that a claim is correct
   given that two or more sources agree, reported as a function of the
   dependence inflation factor. This is the measure the project actually needs,
   because agreement is the signal every fusion policy consumes.
4. **Task-outcome scoring.** Collaboration gain relative to the best single
   agent, plus false task closure, incorrect reopening, and verification cost.
   Simulator truth is used for scoring only and never enters resolution, per
   AD-001.

## What the experiment would show

The study sweeps dependence from independent to fully correlated across the four
correlation channels and reports where the independence assumption stops paying
for itself. Concretely, it answers:

- At what dependence level does a second confirming report stop reducing the
  false-closure rate?
- Does the dependence inflation factor, computed without ground truth, predict
  that breakdown well enough to act on?
- Do the four correlation channels degrade decisions equivalently, or does
  shared model version behave differently from shared viewpoint?

The outcome is a characterization and a reusable instrument, with a stated
operating boundary for the naive-independence baseline and its successors.

## What we are not claiming

- Not a new fusion operator, and not an improvement on covariance intersection
  or any existing conservative fusion method.
- Not the discovery of correlated failure. The phenomenon is established in
  other domains; this work ports it to collaborative visual perception and
  supplies the missing measurement.
- Not a formal safety, calibration, or real-world operational claim. Results
  will establish decision-policy behavior in simulation only.
- Not a field-first claim. The novelty assessment is bounded search evidence.
  Its method, its two rounds, and the errors the adversarial pass caught are
  documented below and in
  the accompanying document `DEPENDENCE_NOVELTY_SURVEY.md`.

## How this framing was tested before proposing it

This proposal is the second framing considered, not the first. Both were put
through an adversarial novelty pass before reaching you. The full record is in
the accompanying documents `DEPENDENCE_NOVELTY_SURVEY.md` and
`DIRECTION_STATUS.md`.

**Method.** Primary-source retrieval, with every quotation verified verbatim
against a locally retained copy of its source using a regex validation script.
Claims directly asserted by a source are separated from inferences derived here.
Findings were then handed to an independent adversarial reviewer instructed to
attack rather than approve, and every objection it raised was re-verified against
the source text before being accepted.

**Round 1 — the first framing failed.** The original candidate was online
estimation of inter-source dependence, scored on task-lifecycle outcomes.
Retrieval found the estimation half occupied: an IEEE TKDE paper from January
2026 performs HMM-based estimation of dynamic source dependence from categorical
conflicting reports. A 2026 multi-robot maritime system was found to already
combine visual evidence, unknown-correlation fusion, and tasking by expected
uncertainty reduction, which removed the novelty of the proposed
value-of-information gate.

**The adversarial pass rejected the base survey.** The literature survey was
drafted first and is referred to here as the base survey. It was submitted to an
independent adversarial reviewer agent, which was instructed to attack the
survey's reasoning rather than approve it, and which returned a verdict of NEEDS
REVISION with five blocking issues. Four were re-verified directly against the
retained source text and corrected in the survey:

1. The base survey claimed that a counterexample system had no task lifecycle.
   The source text contradicts this. That system implements track management, an
   assign and reassign state machine, an explicit anti-chattering term, and
   evaluation on fragmentation and identity continuity. Its exclusion was
   rewritten to rest on the single ground that survives: it bounds correlation
   conservatively rather than estimating it.
2. The base survey described a source's method as "online" and labelled that a
   source claim. The source claims "dynamic," not "online," and extracts
   dependence via the Viterbi algorithm, which decodes a complete observation
   sequence. "Online" was an inference presented as an assertion.
3. The base survey dispositioned a 2026 survey as supportive motivation. That
   survey in fact proposes its own benchmark and describes
   independence-conditioned acceptance gating, which makes it a threat to the
   claim rather than support for it. It was re-dispositioned accordingly.
4. The base survey made negative claims about a benchmark from its abstract page
   alone, without disclosing the partial read. The disclosure was added.

Two quotations also failed verbatim validation, caused by mangled mathematical
notation and a citation bracket in the retrieved text. Both were restated in
verified wording. The full record, including the corrections, is retained in
the accompanying document `DEPENDENCE_NOVELTY_SURVEY.md`.

**Round 2 — the present framing survived.** The same process was applied to this
proposal's framing. The gap is asserted by a retrieved source rather than
inferred. The nearest threat, a 2026 paper on correlated agreement blindness
reporting joint error inflated 3.53 times over independence, was checked and
operates on network intrusion detection and clinical tabular data with classical
models, not visual perception, and defines indicators rather than releasing a
benchmark.

The stated limitations of that assessment are recorded with it: a two-year
source recency gate that functions as a search budget rather than a novelty
boundary, three sources read only in part, and general web indexes rather than a
systematic database protocol. It is bounded search evidence, not proof of
absence.

## Honest limitation

The contribution is a domain transfer plus an instrument, not a new phenomenon.
Correlated failure among agents is understood elsewhere. The defensible claims
are that it is unmeasured in collaborative visual perception, that the
measurement is constructible, and that the resulting numbers change how an
evidence-gating policy should be designed. If a reviewer finds a published
benchmark that measures failure correlation against task outcomes in multi-agent
perception, this framing should be withdrawn or narrowed.

## Feasibility

A working prototype exists: typed claim and trace contracts, a replaceable
policy interface, four oracle scenarios, deterministic replay verified by
matching SHA-256 trace hashes, and a command-line harness. It was built in a
single session. It is treated as disposable, and carries no frozen status.

What it establishes is that the design is sound, and three design decisions
carry forward independently of the code that currently implements them:

1. **A single policy seam.** Comparison policies plug in behind one interface,
   which is what makes a baseline sweep cheap to run.
2. **A naive-independence baseline.** A policy that treats a differing source
   identifier as statistical independence is exactly the assumption this study
   measures, so one will exist in the comparison set. The prototype shows that
   rule is what a reasonable engineer writes by default, which is the point.
3. **Separation of simulator truth from the agent-visible claim stream**, on
   which the whole evaluation depends (AD-001).

The implementation itself is expected to be rebuilt rather than extended, for
concrete reasons. The current claim record carries a single observation
timestamp and no arrival time, so it cannot express late or out-of-order
delivery, which this study must control for in order to avoid confounding
ordering effects with dependence effects. The four existing scenarios exercise
support, contradiction, and staleness; none exercises correlation between
agents, so a new corpus is required regardless.

This is a deliberate position rather than a concession. The project's risk was
never implementation volume; it is whether the measurement is well defined. A
prototype this small is cheaper to rebuild against a clear specification than to
bend toward a purpose it was not designed for, and rebuilding removes any
pressure to preserve decisions that were convenient rather than correct.

The work requires no new simulator dependency, no flight hardware, and no
perception training. The PX4 and Gazebo spike remains optional and off the
critical path.

## Requested decision

Approval to proceed to a design phase for this framing: freeze the dependence
measure, the correlation channels, the scenario matrix, and the acceptance
thresholds. Implementation remains a separate approval gate.
