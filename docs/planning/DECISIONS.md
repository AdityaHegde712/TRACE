# Active Decisions

## Accepted constraints

AD-001 through AD-004 remain in force and are unchanged by the 2026-10-27
framing change. AD-005 is withdrawn.

- AD-001: Simulator truth remains evaluator-only and never enters resolution.
- AD-002: Belief estimation and task-action selection are separate layers.
- AD-003: Every decision retains source claim IDs and policy version for replay.
- AD-004: Correlated or repeated evidence must not be treated as independent.
  **Now the subject of the research question rather than an untested assertion.**
- AD-005: **WITHDRAWN 2026-10-27 by owner decision.** It previously held that
  the Sprint 1 fixed rule was an explicit baseline whose frozen tests could not
  be changed without permission. Sprint 1 now carries no frozen status. No file,
  fixture, or test assertion in it is an immutable contract, and the
  implementation may be discarded and rebuilt.

  What replaces it: a naive-independence policy - one that treats a differing
  `source_id` as statistical independence - will be reimplemented as a
  comparison baseline, because that rule is the assumption this study measures.
  The commitment is to the baseline's *behaviour*, not to the existing code that
  happens to implement it. The design decisions worth carrying forward (the
  policy seam, truth separation, causal claim IDs, deterministic replay) are
  recorded in AD-001 through AD-003 and in the proposal, not here.

## Proposed, not yet accepted

- PD-006: Adopt correlated-failure measurement as the research contribution.
  The deliverable is an instrument and a characterization, not a new estimator
  or fusion rule. Gate: advisor approval.
- PD-007: Define dependence as an inflation factor over the
  independence-predicted joint error rate, computed from claim streams alone.
- PD-008: Report agreement reliability, P(correct | k sources agree), as a
  function of estimated dependence. This is the measure the policy layer needs.
- PD-009: Define explicit out-of-order and late-arrival semantics with a
  watermark, proven by property-based tests, before any sweep is run.
- PD-010: Replace the `source_id`-based independence proxy at `policy.py:65`
  with an explicit versioned dependence treatment, preserving the Sprint 1
  policy unchanged as a baseline.

## Superseded

- PD-001 (two-state dynamic Bayesian/HMM as the primary method): retained as an
  implementation option, withdrawn as a contribution. HMM-based estimation of
  dynamic source dependence is occupied (IEEE TKDE 38(1), January 2026).
- PD-002 (Subjective Logic challenger): deferred. Not required by the current
  framing.
- PD-003 (value of information plus hysteresis): retained as an implementation
  option, withdrawn as a contribution. A 2026 multi-robot maritime system
  already allocates by expected uncertainty reduction.
- PD-004 (VLM as claim generator, not authority): unchanged in substance, but
  off the critical path for the current framing.
- PD-005 (no reinforcement learning in the bounded MVP): unchanged.

## Rejected framings

- Online inter-source dependence estimation as the contribution. Withdrawn
  after retrieval. The estimation half is occupied, and "correlated errors degrade
  collective decisions" is already established in the multi-agent language-model
  literature, so the result would be predictable.
- Deadline-aware evidence, stale-but-fast versus fresh-but-slow. Discarded by
  the owner: the answer is expected to be domain- and urgency-dependent.
- Adversarial robustness scored on task outcomes. Deprioritized by the owner,
  who has a separate active cybersecurity research project. **Retained as the
  fallback framing if the correlated-failure framing fails review.**
- Latest observation, first report, and unweighted majority vote as final
  methods. They remain baselines, not candidates.

## Operational constraints

- Planning and implementation remain separate approval phases.
- No claim of superiority or novelty without matched-seed evidence and a
  recorded novelty pass.
- Novelty assessments are bounded search evidence, never proof of absence, and
  must state what was read in part.
- Every quoted source claim is verified verbatim against a retained copy before
  it is used in an argument.
