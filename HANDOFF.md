# Project Handoff

> Schema version: 1

**Read this file first.** It is written for a fresh session with zero prior
context. Everything needed to start work with the owner today is below. Other
files are linked for when you need them.

## Handoff metadata

- **Project:** `C:\Users\hifia\Projects\Capstone`
- **Last updated:** `2026-11-03 (America/Los_Angeles)`
- **Status:** `In progress` — the one-week dependence spike is `Complete`; the
  M1 design gate (2026-11-10) is `Not started`.
- **Evidence boundary:** Every material claim below is labeled
  `Workspace-confirmed` (a read-only command was run in this repo today and its
  result is in the Verification evidence table), `Owner-confirmed` (stated by
  the owner or recorded in a project document), `Proposed`, `Reconstructed`, or
  `Unresolved`.
- **Owner:** Aditya Hegde (`aditya.hegde@sjsu.edu`), Track A. Advisor: Dr. Kaikai Liu.
- **Session start convention:** `Workspace-confirmed` — `AGENTS.md` asks every
  session to invoke the `team-onboarding` skill, then `track-guide`. Do that
  first, then return here.
- **Reporting style:** `Owner-confirmed` — the owner has ADHD and requires
  verdict-first reporting: one plain verdict sentence, then what it means for
  the decision, then numbers, then caveats last and only when a caveat changes
  an action. The rule is encoded in the `<result_reporting>` section of
  `AGENTS.md`. Follow it in every reply.

## Where the project stands — the verdict

`Workspace-confirmed` **The spike worked, and the answer is yes.** Two simulated
agents observing the same scene with the same detector fail together far more
often than independence predicts.

- **Dependence inflation ratio 1.671, 95% bootstrap CI [1.500, 1.870]**, over
  54 CARLA 0.9.16 scenes and 448 objects visible to both agents. The interval
  sits clear of 1.0.
- **What it means for the decision:** the method framing holds. This is
  "Outcome 1" of the three outcomes the previous handoff set out. The project
  continues into the M1 design gate; no pivot is needed.
- The statistic is the **Kuncheva & Whitaker (2003) double-fault measure,
  adopted unchanged**. Never present it as a new statistic.

`Owner-confirmed` **Do not overstate this.** The spike did **not** show that
MATE's published results are wrong. It showed that the independence assumption
MATE declares untested is false in our setting. State only that.

## Mission and scope

- **Goal:** Quantify when "different source_id" fails to mean "independent" in
  a distributed perception team, and measure what that costs in decision
  quality. This is a benchmark and measurement harness, not a new fusion
  algorithm.
- **Research question as now settled** (`Owner-confirmed`): distributed agents
  observing a shared scene have non-independent perception errors; how much
  does that degrade decisions built on their agreement, and can measuring
  dependence at the right granularity recover the lost decision quality?
- **In scope now:** the M1 design-gate drafts — see "In-flight work".
- **Out of scope (do not do these, even if asked indirectly):**
  1. Do **not** send, email, or submit the advisor proposal at
     `docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md`. It has been
     revised to carry the measured result and is deliberately **unsent**.
     Sending is owner-only.
  2. Do **not** resume, extend, or re-review the literature survey at
     `docs/research/DEPENDENCE_NOVELTY_SURVEY.md`. It is paused.
  3. Do **not** begin full implementation — no sweep harness, no
     dependence-corrected policy, no evaluation pipeline — until M1 freezes the
     definitions.

## Current state

- `Workspace-confirmed` Branch `dev` at `159c6d1`; `main` at `5615902`; working
  tree **clean**; no stray feature branches (local: `dev`, `main` only).
- `Workspace-confirmed` Test suite green: **153 passed in 32.60s**. Lint clean
  (`All checks passed!`). Interpreter `.venv/Scripts/python.exe`, Python 3.12.13.
- `Workspace-confirmed` The spike harness lives in `src/spike_dependence/`
  (14 modules). `src/evidence_resolution/` is the **older Sprint 1 prototype**
  and is unrelated to the spike pipeline.
- `Workspace-confirmed` Four spike reports are committed under `docs/spike/`:
  `SPIKE_RESULT.md`, `SPIKE_STRATIFIED_ANALYSIS.md`, `SPIKE_CONTRAST_CONDITION.md`,
  `SPIKE_CAUSATION_CONTROL.md`.
- `Workspace-confirmed` `artifacts/spike/raw/` holds **54 scene folders** plus
  `manifest.json`. `artifacts/` is gitignored, so these frames exist **only on
  this machine**. Losing them means a full CARLA re-render.
- `Workspace-confirmed` CARLA 0.9.16 **is installed** at
  `D:\Software\CARLA_0.9.16\CarlaUE4.exe`, and the spike extra is currently
  present in the venv (`carla`, `torch`, `ultralytics` all import-resolvable).
  The previous handoff's claim that CARLA is absent is obsolete.
- `Owner-confirmed` **M0 advisor approval is OVERDUE** — it was due 2026-11-03.
  The proposal is revised and still unsent, by choice.
- `Owner-confirmed` M1 design gate is **2026-11-10**.

## Completed work

- `Workspace-confirmed` **Complete** — The dependence spike, all four phases.
  Headline, strata, contrast condition and permutation controls are recorded in
  [`docs/spike/`](docs/spike/) and in `.agent-tasks/DECISIONS.md` entries
  SD-001 through SD-026.
  - **Headline** (SD-020): ratio 1.671 [1.500, 1.870]; double-fault 0.2143
    against an independence prediction of 0.1282; marginals 0.3683 / 0.3482;
    contingency both-wrong 96, only-A 69, only-B 60, neither 223.
  - **Difficulty confound survived** (SD-021): conditioning on apparent object
    size, inflation holds in all three terciles — small 1.324 [1.183, 1.492],
    medium 1.725 [1.164, 2.390], large 1.782 [1.379, 2.251].
  - **Contrast condition** (SD-022 to SD-024): a second detector, RT-DETR-L.
    Sharing a detector raises association by **+0.0915 phi, paired CI
    [+0.0466, +0.1401]**, 0 of 5000 paired resamples at or below zero — but
    heterogeneous agents stay strongly correlated (phi 0.285). The failure of
    independence is therefore **broader** than "identical models fail together".
  - **Permutation controls and the correction** (SD-026): same scene /
    different object returns **1.197 [1.062, 1.340]**; different scene /
    different object returns **0.999 [0.835, 1.166]**. The null at 0.999 proves
    the statistic is unbiased and validates the whole pipeline. Breaking the
    shared context removes the effect, so shared context is **causal**.
    Decomposition of the 0.671 excess: **~29% scene-wide, ~71% attaching to the
    two agents observing the SAME individual object**.
- `Workspace-confirmed` **Complete** — An earlier claim that "the scene
  dominates" (SD-024) was **wrong**, reached by elimination rather than by a
  counterfactual. It is corrected in `README.md`, the `team-onboarding` primer,
  and the proposal. Do not reintroduce the old wording.
- `Owner-confirmed` **Complete** — Literature survey, eight literatures,
  `docs/research/DEPENDENCE_NOVELTY_SURVEY.md`. **Paused. Do not extend.**
- `Workspace-confirmed` **Complete** — Sprint 1 deterministic prototype,
  `src/evidence_resolution/`, still passing within the 153-test suite.
- `Owner-confirmed` **In progress** — Course deliverables under `Submissions/`.
  Owner-side; not an agent's job.

## In-flight work

- **M1 design gate — `Not started`.** It freezes five things: the dependence
  measure and its estimator, the agreement-reliability measure, the four
  correlation channels, the scenario matrix, and the acceptance thresholds.
  Drafts are tasks 1-5 in [`.agent-tasks/TASKS.md`](.agent-tasks/TASKS.md);
  gate context is in [`.agent-tasks/PLAN.md`](.agent-tasks/PLAN.md).
- **The first M1 question, and the reason the spike matters**
  (`Workspace-confirmed`, SD-026): **is the dependence estimate keyed per
  object pair or per agent pair?** About 71% of the dependence is object-level,
  which a per-agent or per-scene trust scalar may be unable to represent. The
  four-channel framing implicitly assumes that scalar. This is now an empirical
  question, not a stylistic one, and M1 must answer it explicitly.
- **Open spike follow-up** — task S12 in `TASKS.md`: deepen the confound
  control by conditioning on object class and distance as well as apparent
  size, and consider several frames per scene. Optional; not blocking M1.

## Decisions to preserve

Full session record: [`.agent-tasks/DECISIONS.md`](.agent-tasks/DECISIONS.md)
(SD-001 to SD-026). Authoritative project record: `docs/planning/DECISIONS.md`.
Carried forward here because they are load-bearing:

- `Owner-confirmed` **AD-001** — Simulator truth never enters the claim stream
  or the policy; it scores detections only.
- `Owner-confirmed` **AD-004** — Correlated or repeated evidence is never
  treated as independent without a measurement. The spike is that measurement.
- `Owner-confirmed` **AD-005 withdrawn** — the Sprint 1 prototype is not
  frozen; its code, fixtures and tests may change.
- `Owner-confirmed` The statistic is **not new** (Kuncheva & Whitaker 2003).
  Never claim a new metric.
- `Owner-confirmed` State scope over the retrieved set, never over a whole
  field. Universal claims are banned; they failed three review rounds.
- `Owner-confirmed` A real detector is non-negotiable. Synthetic claims with an
  experimenter-chosen correlation parameter would assume the conclusion.
- `Workspace-confirmed` **SD-021** — the **mechanism is not established, only
  the effect**. Pose, colour, class, and occlusion by vegetation remain
  uncontrolled. One town, one IoU threshold, one frame per scene.
- `Workspace-confirmed` **SD-022** — cross-condition comparisons use **phi**,
  not the inflation ratio; the ratio's denominator makes a more accurate
  detector look more dependent. The headline number stays the inflation ratio.

### Operational knowledge you will otherwise rediscover painfully

All `Workspace-confirmed` from `.agent-tasks/DECISIONS.md`:

- **`client.load_world()` CRASHES the CARLA server on this machine** (SD-016).
  Launch with the town as the FIRST argument instead:
  `D:\Software\CARLA_0.9.16\CarlaUE4.exe Town10HD -quality-level=Low -RenderOffScreen -carla-rpc-port=2000`
- **Drain CARLA sensor queues to the LATEST frame** (SD-014). `queue.get()`
  returns the oldest item and silently yields pre-spawn ground truth.
- **Camera placement is ray-cast validated** (SD-017), because orbit geometry
  once put a camera inside a building and wrote valid-looking EMPTY ground truth.
- **Python is pinned to 3.12** — `requires-python = ">=3.12,<3.13"` plus
  `.python-version` — because `carla` 0.9.16 ships cp312 wheels at the latest
  (SD-025).
- **`uv sync` installs lint and test only. `uv sync --extra spike` is REQUIRED
  to run the pipeline** (adds carla, torch cu128, ultralytics). torch must come
  from the pinned **explicit** cu128 index in `pyproject.toml`; the RTX 5060 is
  Blackwell, `sm_120`, and PyPI's Windows torch is CPU-only (SD-019, SD-025).
- **Full re-run order:** launch CARLA (above) →
  `python -m spike_dependence.render_scenes --scenes 54` → **STOP CARLA** →
  `detect` → `detect --weights rtdetr-l.pt --tag rtdetr` → `spike_cli` →
  `stratify` → `causation_cli`. CARLA and the detector must never be
  co-resident in VRAM (SD-003).

## Verification evidence

All commands were run in `C:\Users\hifia\Projects\Capstone` on 2026-11-03.

| Check | Command or manual procedure | Result | Evidence level |
| --- | --- | --- | --- |
| Existing handoff read before overwrite | Read `HANDOFF.md` in full | Present, dated 2026-10-29, stale (`Not started`, "CARLA not installed"); owner constraints carried forward | `Workspace-confirmed` |
| Branch | `git rev-parse --abbrev-ref HEAD` | `dev` | `Workspace-confirmed` |
| `dev` head | `git rev-parse --short dev` | `159c6d1` | `Workspace-confirmed` |
| `main` head | `git rev-parse --short main` | `5615902` | `Workspace-confirmed` |
| No stray branches | `git branch -a` | Local `dev`, `main`; remotes `origin/dev`, `origin/main`, `origin/HEAD` | `Workspace-confirmed` |
| Working tree | `git status --porcelain` | Empty — clean | `Workspace-confirmed` |
| Test suite | `.venv/Scripts/python.exe -m pytest -q` | `153 passed in 32.60s` (exit 0) | `Workspace-confirmed` |
| Lint | `.venv/Scripts/python.exe -m ruff check .` | `All checks passed!` | `Workspace-confirmed` |
| Python version | `.venv/Scripts/python.exe --version` | `Python 3.12.13` | `Workspace-confirmed` |
| Spike reports present | `ls docs/spike/` | Four files: `SPIKE_CAUSATION_CONTROL.md`, `SPIKE_CONTRAST_CONDITION.md`, `SPIKE_RESULT.md`, `SPIKE_STRATIFIED_ANALYSIS.md` | `Workspace-confirmed` |
| Spike harness present | `ls src/spike_dependence/` | 14 modules incl. `render_scenes.py`, `detect.py`, `double_fault.py`, `causation.py`, `spike_cli.py` | `Workspace-confirmed` |
| Sprint 1 prototype present | `ls src/` | `evidence_resolution/`, `spike_dependence/` | `Workspace-confirmed` |
| Rendered scenes on disk | `ls -d artifacts/spike/raw/*/ \| wc -l` | `54` scene folders, plus `manifest.json` | `Workspace-confirmed` |
| Artifacts are gitignored | `grep -n "artifacts" .gitignore` | line 48: `artifacts/` | `Workspace-confirmed` |
| CARLA installed | `ls "D:/Software/CARLA_0.9.16/CarlaUE4.exe"` | File present | `Workspace-confirmed` |
| Spike extra installed | `python -c "importlib.util.find_spec(...)"` for `carla`, `torch`, `ultralytics` | All three `True` | `Workspace-confirmed` |
| Python cap and spike extra declared | `sed -n '1,40p' pyproject.toml` | `requires-python = ">=3.12,<3.13"`; `[project.optional-dependencies] spike = [carla==0.9.16, torch, torchvision, ultralytics]` | `Workspace-confirmed` |
| SD-024 correction landed | `grep -rn "71%" README.md docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md` | Hits in `README.md:11` and proposal lines 48, 149, 190 | `Workspace-confirmed` |
| Spike numbers | `sed -n '198,360p' .agent-tasks/DECISIONS.md` | SD-018 to SD-026 as quoted above | `Workspace-confirmed` |

**Not verified in this session; safe manual checks recorded instead of claimed
validation:**

- The spike pipeline was **not re-run** here. The reported numbers are read from
  `.agent-tasks/DECISIONS.md` and `docs/spike/`, not re-measured. Manual check:
  follow the re-run order above and compare against SD-020 and SD-026.
- GPU identity and VRAM were not probed. Manual check: open a normal local
  terminal outside the agent sandbox and run `nvidia-smi`; expect an RTX 5060
  Laptop GPU. Agent-shell GPU enumeration has failed before and did not matter.
- TACC Vista's `aarch64` finding and the remaining GPU-hour balance are
  `Owner-confirmed` only. Manual check: the owner inspects the allocation page.
- M0 approval status is `Owner-confirmed`; nothing in the repo records it.

## Relevant files and durable state

- [`docs/spike/SPIKE_RESULT.md`](docs/spike/SPIKE_RESULT.md) — the headline result.
- [`docs/spike/SPIKE_STRATIFIED_ANALYSIS.md`](docs/spike/SPIKE_STRATIFIED_ANALYSIS.md) — strata and the size-tercile confound test.
- [`docs/spike/SPIKE_CONTRAST_CONDITION.md`](docs/spike/SPIKE_CONTRAST_CONDITION.md) — homogeneous vs heterogeneous detector pairs.
- [`docs/spike/SPIKE_CAUSATION_CONTROL.md`](docs/spike/SPIKE_CAUSATION_CONTROL.md) — permutation controls, the null at 0.999, and the 29/71 decomposition.
- `src/spike_dependence/` — the spike harness. Entry points are the `*_cli.py` modules and `render_scenes.py`, `detect.py`, `stratify.py`, `contrast.py`.
- `src/evidence_resolution/` — older Sprint 1 prototype; background only.
- `artifacts/spike/raw/` — 54 rendered scenes. **Gitignored, local only, irreplaceable without a CARLA re-render.**
- `docs/planning/PROPOSAL_METHOD_DEPENDENCE_AWARE_TRUST.md` — revised, carries the measured result. **Read-only. Do not send or edit.**
- `docs/planning/DECISIONS.md` — authoritative decision record (AD-001 onward).
- `docs/research/DEPENDENCE_NOVELTY_SURVEY.md` — paused survey. **Do not extend.**
- [`.agent-tasks/PLAN.md`](.agent-tasks/PLAN.md) — active gate, M1 freeze list, spike architecture, exit criteria.
- [`.agent-tasks/DECISIONS.md`](.agent-tasks/DECISIONS.md) — SD-001 to SD-026, the operational record for the spike.
- [`.agent-tasks/TASKS.md`](.agent-tasks/TASKS.md) — atomic checklist; tasks 1-5 are the M1 drafts, S12 is the open spike follow-up.
- `AGENTS.md` — project rules: session start, TDD, verdict-first reporting, background-process discipline, UTF-8/LF, `.agent-tasks` continuity.

## Blockers, conflicts, and assumptions

- **Blockers:**
  - `Owner-confirmed` **M0 advisor approval is overdue** (was due 2026-11-03)
    and gates everything downstream. Only the owner can clear it by sending the
    proposal.
- **Conflicts (retained, not silently resolved):**
  - `Workspace-confirmed` The "Blockers" section of `.agent-tasks/TASKS.md` still
    says "Nothing on this branch is committed. Commits are owner-only per
    `HANDOFF.md`." That is **stale**: the spike work is committed and merged, and
    `dev` is at `159c6d1` with a clean tree. Do not edit that file to fix this
    without the owner's instruction; just do not believe the line.
  - `Workspace-confirmed` **SD-024 vs SD-026** both remain in `DECISIONS.md`.
    SD-026 supersedes SD-024's "the scene dominates". The object dominates
    (~71%). Both entries are kept on purpose as a record of the correction.
  - `Workspace-confirmed` `.agent-tasks/TASKS.md` still names
    `spike/dependence-correlation` as an open branch; it is merged and gone.
- **Assumptions:**
  - The project continues on this Windows machine, in this repo, under the
    existing `.venv`.
  - "Two agents" means two viewpoints on one shared scene, not two simulations.
  - `Unresolved` — which per-object property drives the 71%. Apparent size is
    excluded (SD-021); class, pose, colour and specific occluders are not.

## Owner-only actions

- Sending the advisor proposal and obtaining **M0 approval (overdue since 2026-11-03)**.
  An agent must never send, email, or submit it.
- Approving any new dependency or GPU spend.
- Teammate review and Canvas submission of anything under `Submissions/`.
- Any commit, push, branch change, pull request, or merge. The repo uses
  **full-mode git**: feature branches off `dev`, PRs into `dev`, the agent never
  merges. `Owner-confirmed` one exception was granted and is **expired** — a
  one-time direct commit to `dev` on 2026-11-03. Treat it as spent.
- A commit blocked by the test-change hook must be escalated, never bypassed.

## Deferred work

- Spike task **S12** — deepen the confound control (object class, distance,
  several frames per scene). Deferred: the spike question is answered and M1 is
  the critical path.
- A3 deterministic replay under out-of-order evidence, A4 resolver plus
  naive-independence baseline, A5 evaluation — all deferred behind M1.
- Adding an arrival timestamp to the claim record in
  `src/evidence_resolution/contracts.py` — real gap, irrelevant until A3.
- Deliverables under `Submissions/` — owner-side.
- Stale 922 MB partial `CARLA_0.9.16.zip` under `D:\CARLA_0.9.16_download\` —
  useless; the real install is at `D:\Software\CARLA_0.9.16\`. Owner deletes by
  hand.

## Immediate next action

> Draft M1 task 1 — the dependence measure and its estimator — in
> [`.agent-tasks/TASKS.md`](.agent-tasks/TASKS.md), and make its first decision
> explicit: whether the dependence estimate is keyed **per object pair** or
> **per agent pair**, given that SD-026 places ~71% of the measured dependence
> at the object level.
