# Project Handoff

> Schema version: 1

**Read this file only.** It is written for a fresh Claude session with zero prior
context. Everything needed to start work with the owner today is below. Other
files are linked for when you need them; do not read them before starting.

## Handoff metadata

- **Project:** `C:\Users\hifia\Projects\Capstone`
- **Last updated:** `2026-10-29 (America/Los_Angeles)`
- **Status:** `Not started` (the spike below has not begun)
- **Evidence boundary:** Claims are labeled `Workspace-confirmed` (a read-only
  command was run in this repo and its result is in the Verification evidence
  table), `Owner-confirmed` (stated by the project owner or recorded in a
  project document), `Proposed`, `Reconstructed`, or `Unresolved`.
- **Owner:** Aditya Hegde (`aditya.hegde@sjsu.edu`), Track A. Advisor: Dr. Kaikai Liu.
- **Session start convention:** `Workspace-confirmed` — `AGENTS.md` asks every
  session to invoke the `team-onboarding` skill, then `track-guide`. Do that
  first, then come straight back to the single job below.

## Mission and scope

- **Goal:** Run a one-week spike that answers exactly one question — **when two
  simulated agents observe the same scene with the same detector, do their
  perception errors co-occur more often than independence predicts?**
- **In scope:** Only the spike described in "The spike" below: render scenes,
  run one detector from two viewpoints, score against simulator ground truth,
  compute a joint-error inflation ratio, and report it.
- **Out of scope (do not do these, even if asked indirectly):**
  1. Do **not** send, email, submit, or edit the advisor proposal at
     `docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md`. It is written and
     deliberately unsent, pending this spike's result. Sending it is an owner-only
     action.
  2. Do **not** resume, extend, re-verify, or re-review the literature survey at
     `docs/research/DEPENDENCE_NOVELTY_SURVEY.md`. It is paused and complete enough.
  3. Do **not** begin full implementation: no sweep harness, no dependence-corrected
     policy, no evaluation pipeline, no detector-pair training. Those wait on the
     spike result and on the M1 design gate.

## Why this spike exists

`Owner-confirmed` (recorded in `docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md`,
where every quotation was verified verbatim against a retained source copy):

The project studies whether agents in a distributed perception team fail
*together*, and whether that breaks the decisions built on their agreement.

The baseline it attacks is **MATE: the Multi-Agent Trust Estimator**
(Hallyburton & Pajic, arXiv:2503.04954, 2025), which assumes the opposite:
"given the environment, their tracks will importantly not contain any
correlations." MATE states no experiment for that assumption and writes
"Future works will experimentally evaluate the independence assumption."
**This spike is that experiment, at small scale**, run to decide whether the
project's method framing is worth the remaining ten weeks.

Evidence that the assumption is probably false (all `Owner-confirmed`, sourced
in the survey and the proposal):

1. Gottschalk et al. (arXiv:2112.04758) measured correlated errors between
   redundant perception networks.
2. A 2026 collaborative-perception survey names homogeneous agents with identical
   perception models and similar viewpoints as susceptible to correlated failures.
3. Agent Behavioral Contracts II found two instances of one model co-failing on
   90.0% of missions on which either failed.

## The spike

`Owner-confirmed` design. Five steps, in order:

1. **Render ~50 scenes** in CARLA 0.9.15, locally. Two agent viewpoints per scene,
   both observing one shared scene. Vary viewpoint overlap and at least one
   occluder or weather condition.
2. **Run ONE detector** (same weights) from both viewpoints. Produce per-agent
   detections.
3. **Score** each agent's detections against CARLA ground truth to get a per-agent
   error indicator per object.
4. **Compute the pairwise joint-error rate** (both agents wrong on the same object)
   and compare it to the rate independence predicts (the product of the marginals).
   **Report the inflation ratio.** This is the double-fault measure of Kuncheva &
   Whitaker (2003) expressed as a ratio — **adopted, not invented**. Never present
   it as a new statistic.
5. **Optional contrast condition:** repeat with two *different* detectors.

### Three outcomes, all acceptable, none a failure

1. **Clear correlation** (ratio well above 1) — the method framing holds; proceed
   to design.
2. **Negligible correlation** — MATE's assumption survives in this setting. That
   is a real finding, and the project pivots with roughly nine weeks left.
3. **CARLA will not run** — then it is known in week one rather than week six.
   Fall back to a lighter renderer that keeps the same correlation knobs.

Report whichever occurs. Do not bury or soften outcome 2.

## Current state

- `Workspace-confirmed` Branch is `dev`; head commit `9bd267e docs: add project README`.
  The working tree has uncommitted modifications to seven docs files plus several
  untracked PDFs and one untracked Markdown proposal. Nothing in `src/` or `tests/`
  is modified. **Do not commit, stash, or clean any of this** unless the owner asks.
- `Workspace-confirmed` Test suite is green: **22 passed** in 24.69s. Lint clean.
- `Workspace-confirmed` Python 3.12.13 in the repo venv at `.venv/Scripts/python.exe`.
  Declared dev dependencies are only `pytest` and `ruff`; the project itself has no
  runtime dependencies. **The spike will need new ones** (a CARLA client, a detector
  stack) — propose them to the owner before installing anything.
- `Workspace-confirmed` CARLA is **not installed**: the `carla` Python package is
  absent from the venv, and no CARLA directory was found in the usual locations.
  Obtaining and launching CARLA 0.9.15 is step 0 of the spike.
- `Owner-confirmed` M0 advisor approval is **pending**, due **2026-11-03**. The
  proposal is written but deliberately unsent, pending this spike's result.
- `Owner-confirmed` M1 design gate is **2026-11-10**; it would freeze the dependence
  measure and its estimator, the agreement-reliability measure, the four correlation
  channels, the scenario matrix, and the acceptance thresholds. Those drafts are
  tasks 1-5 in `.agent-tasks/TASKS.md` and are **not** this session's job.

### Hardware constraints

`Owner-confirmed` by a direct check on 2026-10-29:

- **Rendering is LOCAL.** RTX 5060, 8 GB VRAM. Use **CARLA 0.9.15** (Unreal 4.26
  line, documented 6 GB floor). **Do NOT use CARLA 0.10** — it needs 12-16 GB.
  The 5060 is Blackwell silicon on an old engine, so first-launch trouble is
  plausible and is **not** a dead end; it is outcome 3 above.
- **TACC Vista cannot run CARLA.** A check on a GH node returned `aarch64`, no x86
  emulation is available, and CARLA ships x86_64 binaries. The graphics stack is
  otherwise present (`nvidia_icd.aarch64.json`, loadable EGL) — the blocker is the
  instruction set, not the GPU. Vista stays available for detector inference and
  training; roughly **900 GPU-hours remain until 2026-11-18**.

`Unresolved` — this session's own hardware probe **did not see** the RTX 5060. See
Blockers below; resolve that before assuming local rendering will work.

## Completed work

- `Workspace-confirmed` **Complete** — Sprint 1 deterministic evidence-resolution
  prototype exists and passes its tests: `src/evidence_resolution/` with
  `contracts.py`, `policy.py`, `scenario.py`, `__main__.py`, exercised by
  `tests/spec/` and `tests/integration/` (22 tests).
- `Owner-confirmed` **Complete** — Literature survey: eight literatures, 50 works
  screened, 36 retrieved in full, eight adversarial review rounds —
  `docs/research/DEPENDENCE_NOVELTY_SURVEY.md`. **Paused. Do not extend.**
- `Owner-confirmed` **Complete** — Advisor proposal drafted:
  `docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md`. **Unsent, by choice.**
- `Owner-confirmed` **In progress** — Course deliverables (three member logbooks and
  the Workbook 2 continuation) under `Submissions/`. Owner-side review and submission;
  not this session's job unless the owner redirects you.

## In-flight work

- **This spike: `Not started`.** No spike code, scenes, detector adapter, or scoring
  script exists in the repository yet. There is nothing half-written to pick up.

## Existing code to reuse, not rebuild

`Workspace-confirmed` — `src/evidence_resolution/` is a working deterministic
prototype: typed claim and trace contracts, a replaceable `ResolutionPolicy`
interface (`policy.py` defines the `Protocol` and a `FixedRulePolicy`), scenario
replay (`scenario.py`: `load_scenario`, `run_scenario`), and a CLI
(`python -m evidence_resolution --scenario ... --output-dir ...`).

The spike needs **none of the policy logic**. What is worth matching:

- the **claim record shape** in `contracts.py` (`EvidenceClaim` carries `source_id`,
  `entity_id`, `frame_id`, `model_version`, `confidence`, `artifact_ref`), and
- the **truth-held-out discipline**: simulator truth is used for scoring only.

`Owner-confirmed` known gap, irrelevant to this spike but real later: the claim
record carries only an observation timestamp (`observed_at`) and **no arrival time**,
so it cannot represent late or out-of-order delivery.

## Decisions to preserve

- `Owner-confirmed` **AD-001** — Simulator truth never enters the claim stream or the
  policy; it is for scoring only. This binds the spike: ground truth scores detections
  and must never reach the detection or decision path.
- `Owner-confirmed` **AD-004** — Correlated or repeated evidence is never treated as
  independent without a measurement. This spike is that measurement.
- `Owner-confirmed` **AD-005 withdrawn** — the Sprint 1 prototype carries **no frozen
  status**. Its code, fixtures, and tests may be changed freely.
- `Owner-confirmed` The statistic is **not new**: double-fault, Kuncheva & Whitaker
  2003. Do not claim a new metric, and do not claim that any source asserts a gap.
- `Owner-confirmed` State scope over the retrieved set, never over a whole field.
  Universal claims ("every literature...") failed three times and are banned.
- `Owner-confirmed` A real detector is non-negotiable. Synthetic claims with an
  experimenter-chosen correlation parameter would assume the conclusion.

Full authoritative record: `docs/planning/DECISIONS.md`. Session-level additions:
[`.agent-tasks/DECISIONS.md`](.agent-tasks/DECISIONS.md).

## Verification evidence

| Check | Command or manual procedure | Result | Evidence level |
| --- | --- | --- | --- |
| Root handoff absent before writing | `test -f HANDOFF.md` in project root | Absent; this file is new, nothing was overwritten | `Workspace-confirmed` |
| Test suite state | `.venv/Scripts/python.exe -m pytest -q` | `22 passed in 24.69s` | `Workspace-confirmed` |
| Lint state | `.venv/Scripts/python.exe -m ruff check .` | `All checks passed!` | `Workspace-confirmed` |
| Python version | `.venv/Scripts/python.exe --version` | `Python 3.12.13` | `Workspace-confirmed` |
| Branch and head commit | `git rev-parse --abbrev-ref HEAD` then `git log --oneline -5` | `dev`; head `9bd267e docs: add project README` | `Workspace-confirmed` |
| Working tree | `git status --porcelain` | 7 modified docs files, 6 untracked (5 PDFs + the proposal `.md`); `src/` and `tests/` clean | `Workspace-confirmed` |
| CARLA Python client installed | `.venv/Scripts/python.exe -c "import importlib.util; print(importlib.util.find_spec('carla'))"` | Not installed | `Workspace-confirmed` |
| CARLA engine present on disk | `ls C:/` and `ls C:/Users/hifia/` | No CARLA directory found in either location | `Workspace-confirmed` |
| NVIDIA GPU visible to this shell | `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv` | Failed: "couldn't communicate with the NVIDIA driver" | `Unresolved` |
| Display adapters | PowerShell `Get-CimInstance Win32_VideoController` | Only `AMD Radeon(TM) 610M` returned; no NVIDIA adapter listed | `Unresolved` |
| Source modules present | `find src -name "*.py"` | `__init__.py`, `__main__.py`, `contracts.py`, `policy.py`, `scenario.py` | `Workspace-confirmed` |
| Spike code present | `find src tests` for any spike, CARLA, or detector module | None found; spike is `Not started` | `Workspace-confirmed` |

Not verifiable from this session; safe manual checks recorded instead of claimed
validation: RTX 5060 presence and VRAM, the TACC Vista `aarch64` finding, and the
~900 remaining GPU-hours. Manual check for the GPU — open a normal local terminal
outside the agent sandbox and run `nvidia-smi`; it should name the RTX 5060 at ~8 GB.

## Relevant files and durable state

- `src/evidence_resolution/contracts.py` — claim record shape worth matching.
- `src/evidence_resolution/scenario.py`, `src/evidence_resolution/policy.py` — replay
  and policy interface; background only, the spike does not need the policy logic.
- `docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md` — why this spike exists,
  the baseline, the compute plan. **Read-only. Do not send or edit.**
- `docs/planning/DECISIONS.md` — authoritative decision record (AD-001 onward).
- `docs/research/DEPENDENCE_NOVELTY_SURVEY.md` — paused survey. **Do not extend.**
- `docs/research/DIRECTION_STATUS.md` — why framing A was selected and B, C, D were not.
- [`.agent-tasks/PLAN.md`](.agent-tasks/PLAN.md) — active gate (M0 pending), the M1
  freeze list, Track A paths, exit criteria.
- [`.agent-tasks/DECISIONS.md`](.agent-tasks/DECISIONS.md) — session-level decisions
  not yet promoted to `docs/planning/DECISIONS.md`.
- [`.agent-tasks/TASKS.md`](.agent-tasks/TASKS.md) — atomic checklist; tasks 1-5 are
  the M1 design drafts, deferred past this spike.
- `AGENTS.md` — project rules: TDD, background-process discipline, UTF-8/LF, and the
  `.agent-tasks` continuity contract.

## Blockers, conflicts, and assumptions

- **Blockers:**
  - `Workspace-confirmed` CARLA 0.9.15 is not installed and not on disk. Acquiring
    and launching it is step 0 and is the most likely source of week-one friction.
- **Conflicts (retained, not silently resolved):**
  - `Owner-confirmed` hardware is an **RTX 5060 with 8 GB VRAM**, but this session's
    checks saw **no NVIDIA adapter**: `nvidia-smi` could not reach a driver, and
    `Win32_VideoController` returned only an AMD Radeon 610M integrated GPU. This may
    be the sandboxed shell or hybrid-graphics enumeration, or it may mean the discrete
    GPU is unavailable on this machine. **Resolve this before spending time on CARLA**,
    and tell the owner which it is.
- **Assumptions:**
  - The spike runs on this Windows machine, in this repo, under the existing `.venv`.
    New dependencies will be required and are not yet approved.
  - "Two agents" means two viewpoints on one shared scene, not two separate simulations.

## Owner-only actions

- Sending the advisor proposal and obtaining **M0 approval (due 2026-11-03)**.
- Approving any new runtime dependency, CARLA download, or TACC Vista GPU-hour spend.
- Teammate review and Canvas submission of anything under `Submissions/`.
- Any commit, push, branch change, or pull request. `AGENTS.md` routes Git work
  through the `git-workflow` skill; a commit blocked by the test-change hook must be
  escalated to the owner, never bypassed.

## Deferred work

- M1 design drafts — dependence inflation factor definition and estimator, the
  agreement-reliability measure, the four correlation channels, the scenario matrix
  and acceptance thresholds — deferred until the spike result is in. See
  [`.agent-tasks/TASKS.md`](.agent-tasks/TASKS.md) tasks 1-5.
- Sweep harness, dependence-corrected policy, naive-independence baseline, evaluation
  pipeline, and detector-pair training on Vista — deferred; all require M0 then M1.
- Adding an arrival timestamp to the claim record — deferred; irrelevant to this spike.
- Deliverables under `Submissions/` — deferred to the owner.

## Immediate next action

> Ask the owner to confirm the discrete RTX 5060 is visible on this machine — have
> them run `nvidia-smi` in a normal local terminal and paste the output — because
> this session's checks found only an integrated AMD adapter; once confirmed, plan
> the CARLA 0.9.15 download and first launch as step 0 of the spike.
