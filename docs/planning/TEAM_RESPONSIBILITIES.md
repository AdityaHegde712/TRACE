# Team Responsibilities and Milestones

**Project:** Measuring correlated failure in multi-agent visual evidence resolution
**Status:** Proposed allocation for team and advisor review. Supersedes the work
split in the superseded `PROJECT_EXECUTION_PLAN.md` (archived) if the framing in
the accompanying `PROPOSAL_CORRELATED_FAILURE.md` is approved.
**Date:** 2026-10-27
**Window:** 2026-10-27 to 2027-01-22

---

## Roles

| Member | Role | Owns |
| --- | --- | --- |
| **Aditya Hegde** | Project lead | The measurement definitions, the deterministic core under concurrency, the evaluation, and every frozen contract. The research claim stands or falls on this track. |
| **Rishi Sheth** | Simulation and scenario generation | The controlled-correlation scenario corpus and the optional simulator spike. |
| **Pranav Senghal** | Harness, baselines, and release | The sweep infrastructure, comparison policies, and the artifacts that make the work usable and presentable. |

Each member owns their track's correctness. The lead owns cross-track contracts
and is the only person who changes a frozen definition.

---

## Three parallel tracks

The tracks are designed to run concurrently after milestone M1. Only M1 is a
hard serialization point, because every track consumes the contracts frozen
there.

### Track A - Measurement and core (Aditya)

The hardest and least delegable work. Every item here is either a definition the
rest of the project depends on, or a concurrency problem with no obvious
correct answer.

- **A1. Freeze the dependence measure.** Define the dependence inflation factor
  (observed joint error rate over independence-predicted joint error rate),
  its estimator, its sample-size requirements, and its failure cases. This is
  the project's central definition.
- **A2. Freeze the agreement-reliability measure.** Define P(correct | k sources
  agree) as a function of estimated dependence, including how it is computed
  without simulator truth at resolution time.
- **A3. Deterministic replay under out-of-order and late-arriving evidence.**
  Define and version the arrival policy: watermark, late-arrival window, and the
  behavior when a claim arrives after a trace event it would have changed.
  Prove it with property-based tests asserting that any arrival permutation
  within the watermark window yields an identical final belief and trace.
- **A4. Resolver and baseline set.** Implement an explicit, versioned
  dependence treatment, and reimplement the naive-independence rule (a
  differing `source_id` taken as statistical independence) as one of the
  comparison baselines. Sprint 1 is not frozen; the commitment is to the
  baseline's behaviour, not to the prototype's code.
- **A5. Evaluation and analysis.** Produce the correlation-versus-task-error
  characterization, the operating boundary, and the final written evidence.

### Track B - Scenario generation and simulation (Rishi)

- **B1. Latent-variable scenario generator.** Generate claim sequences from a
  scene model where the degree and source of inter-agent correlation are set
  deliberately. Must support the four correlation channels: shared occluder,
  shared detector model version, shared viewpoint geometry, shared illumination.
- **B2. Corpus and seed management.** Fixed-seed, versioned scenario corpus with
  retained generation parameters, so every reported run is reproducible.
- **B3. Ground-truth separation.** Simulator truth is emitted alongside, never
  inside, the agent-visible claim stream, per AD-001. Rishi owns the mechanism
  that keeps them separate.
- **B4. PX4 and Gazebo two-X500 spike.** Off the critical path. Run it only
  after B1 to B3 are delivered. A failed spike must leave the core evaluation
  fully runnable.

### Track C - Harness, baselines, and release (Pranav)

- **C1. Sweep harness.** Run the full scenario matrix across policies, retain
  every run, and emit comparable result tables. Must be re-runnable end to end
  by one command.
- **C2. Baseline policies.** Implement the comparison set: latest-report,
  first-report-wins, unweighted majority vote, and always-verify, each behind
  the existing `ResolutionPolicy` interface.
- **C3. Release engineering.** Root `README.md`, an Apache-2.0 `LICENSE`, an
  installable package, and a single quickstart command that works on a clean
  clone. Note that MultiUAV-Plat is GPL-3.0; no GPL components enter this core.
- **C4. Visual demonstration.** A rendered walkthrough of one correlated-failure
  scenario, showing two agents agreeing, being wrong together, and the trace
  explaining the resulting task decision.
- **C5. Integration documentation.** The camera-to-claim adapter contract,
  documented but implemented only if B4 passes.

---

## Milestones

| ID | Date | Deliverable | Owner | Gate |
| --- | --- | --- | --- | --- |
| **M0** | Nov 3 | Advisor approves the research framing | Aditya | Blocking. No downstream work starts without it. |
| **M1** | Nov 10 | Contracts frozen: dependence measure, agreement-reliability measure, four correlation channels, scenario matrix, acceptance thresholds | Aditya | Blocking for B1 and C1. Tracks run in parallel after this. |
| **M2** | Nov 24 | Generator produces controlled-correlation corpus (B1-B3); out-of-order determinism proven by property tests (A3); baselines implemented (C2) | All three, parallel | Determinism tests pass; corpus reproduces from seed. |
| **M3** | Dec 12 | First end-to-end sweep. Initial correlation-versus-task-error curves | Aditya and Pranav | A real curve exists, even if ugly. |
| **M4** | Dec 18 | Release artifacts complete (C3); PX4 spike go or no-go decision (B4) | Pranav, Rishi | Clean clone runs the demo. Spike result recorded either way. |
| **M5** | Jan 15 | Final runs, analysis, operating boundary, visual demo (A5, C4) | All three | Every reported number traces to a retained run. |
| **M6** | Jan 22 | Workbook and demo evidence submitted | All three | Stage 3 deadline. |

---

## Dependencies and handoffs

- **M1 is the only hard serialization.** Rishi cannot build the generator until
  the correlation channels are defined; Pranav cannot build the sweep harness
  until the metrics are defined. Aditya must not let M1 slip.
- **A3 and B1 are independent** and must run in parallel. Determinism work does
  not need the corpus, and the generator does not need the watermark policy.
- **C2 is independent of everything** after M1 and should start immediately, so
  Pranav is never blocked waiting on the lead.
- **Rishi hands Aditya** a corpus plus its generation parameters. Aditya never
  edits the corpus; defects go back to Rishi.
- **Pranav hands Aditya** result tables, never conclusions. Interpretation sits
  in Track A.
- **Nobody but Aditya changes a definition frozen at M1.** Those are the
  project's immutable contracts. Note that the Sprint 1 prototype is **not**
  among them: AD-005 was withdrawn on 2026-10-27 and that code, its fixtures,
  and its test assertions carry no protected status.

---

## Risks and fallbacks

1. **M1 slips.** Highest-impact risk, because two tracks idle. Fallback: Aditya
   freezes a deliberately simple first version of the dependence measure and
   versions it, rather than waiting for the right one.
2. **The generator cannot produce clean correlation control.** Fallback: reduce
   from four correlation channels to two (shared occluder and shared model
   version), which still supports the central claim.
3. **The PX4 spike fails.** Already handled by design. It is off the critical
   path and the evaluation remains fully runnable without it.
4. **Correlation shows no measurable effect on task outcomes.** This is a
   publishable negative result, not a project failure, provided the sweep is
   reproducible and the measurement is sound. It must be reported, not buried.
5. **Uneven load late in the schedule.** Track A is heaviest from M3 onward.
   Pranav's C4 and C5 are the intended buffer and can absorb reallocation.

---

## Weekly cadence

One team-only meeting per week and one advisor meeting every two weeks, per the
course requirement. Each meeting record states ownership and action items and is
kept separate from milestone updates.
