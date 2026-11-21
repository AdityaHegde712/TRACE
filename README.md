# TRACE: When Agreement Is Not Evidence

Measuring correlated failure in multi-agent visual evidence resolution. SJSU capstone, advised by Dr. Kaikai Liu.

## The idea

A team of drones inspects a road. Drone A reports a blockage, drone B confirms it, and the system closes the task because two sources agreed. That is only safe if the two reports can be wrong independently. Looking at the same scene, the drones can agree and be wrong together.

**This is measured, not assumed.** A one-week spike in November 2026 ran one detector from two viewpoints over 54 CARLA scenes and scored both against simulator ground truth. The two agents were wrong about the same object **1.67 times more often than independence predicts** (95% CI [1.50, 1.87], 448 objects).

A permutation control establishes that the shared context *causes* this rather than merely accompanying it: give the two agents unrelated objects and the ratio returns to **0.999**. Breaking down the excess, about **71% comes from the two agents looking at the same individual object** and about **29% from scene-wide conditions** such as weather and viewpoint geometry. Giving the agents different detectors reduces the effect but does not remove it. See [`docs/spike/`](docs/spike/).

## Headline results (900 scenes)

The full study confirms the spike. It uses 900 CARLA scenes in Town10HD (18 render conditions, 50 scenes each) and two agents per scene. YOLO11m and RT-DETR-L give three detector pairings. Both agents miss the same object more often than independence predicts.

| Pairing | Inflation ratio rho [95% CI] | Observed joint miss | Calibrated prediction | Naive prediction |
| --- | --- | --- | --- | --- |
| YOLO / YOLO | 1.80 [1.73, 1.87] | 0.241 | 0.238 | 0.133 |
| RT-DETR / RT-DETR | 2.52 [2.38, 2.67] | 0.106 | 0.110 | 0.044 |
| YOLO / RT-DETR (mixed) | 1.99 [1.90, 2.08] | 0.141 | 0.148 | 0.074 |

Ratios come from 450 practice scenes. The joint-miss columns come from the 450 exam scenes (4,068 co-visible objects). The calibrated prediction stays within 0.025 of the observed rate when one illumination is held out (nine folds).

Decision cost over 2,700 tasks: closing on the latest report leaves a missed object in 80.4% of tasks. The miss-risk rule cuts that to 2.3% by sending 97.4% of tasks to verification. A sweep of its tolerance with the calibrated estimator gives only four operating points between 97.4% and 100% verification. At equal verification cost it closes no fewer unsafe tasks than random choice, so the study claims no advantage for dependence-aware closing. Detail: the Results and Limitations sections of the preprint.

This project builds a benchmark and measurement harness that answers:

1. At what level of dependence between agents does a second confirming report stop reducing false task closures?
2. Can dependence be measured from claim streams alone, without simulator truth?
3. Do the four correlation channels (viewpoint, shared occluder, illumination, detector model version) hurt decisions equally? The spike says no: the scene-level channels dominate the detector-model channel.

It is not a new fusion algorithm, and results apply to simulation only. Full argument: [`docs/planning/archived/PROPOSAL_CORRELATED_FAILURE.md`](docs/planning/archived/PROPOSAL_CORRELATED_FAILURE.md).

## Status

- [x] **M0:** the research framing is approved.
- [x] **M1:** contracts frozen ([`docs/planning/M1_CONTRACTS.md`](docs/planning/M1_CONTRACTS.md)).
- [x] **M2:** 900-scene CARLA corpus rendered and run through two detectors ([`docs/planning/TRACK_B_CORPUS.md`](docs/planning/TRACK_B_CORPUS.md)).
- [x] **M3:** baseline sweep, offline calibration, and calibrated tolerance sweep executed ([`docs/planning/TRACK_C_SWEEP.md`](docs/planning/TRACK_C_SWEEP.md)).
- [ ] **M4:** release packaging and interactive demonstration.
- **Preprint:** `paper/` holds the manuscript. Build it to get `paper/main.pdf` (see below). `paper/arxiv_submission.tar.gz` is the arXiv bundle.
- **Spike (2026-11-03):** the 54-scene study that motivated the project is under [`docs/spike/`](docs/spike/). Its code is `src/spike_dependence/`.
- **Debrief:** [`docs/milestones/M2_M3_DEBRIEF.md`](docs/milestones/M2_M3_DEBRIEF.md).
- **Schedule:** 2026-10-27 to 2027-01-22. Milestones and owners are in [`docs/planning/TEAM_RESPONSIBILITIES.md`](docs/planning/TEAM_RESPONSIBILITIES.md).

## Quickstart

Requires Python 3.12 exactly and [uv](https://docs.astral.sh/uv/). The CARLA
client publishes `cp312` wheels at the latest, so 3.13+ cannot resolve.

```bash
git clone https://github.com/AdityaHegde712/TRACE.git
cd TRACE
git switch dev
uv sync          # lint, tests and figures; no GPU, CARLA or detector needed
uv run pytest
```

To run the spike pipeline as well, install the optional extra:

```bash
uv sync --extra spike   # adds carla, torch (cu128) and ultralytics
```

## Reproduce the results

All commands run from the repository root. Steps 2 to 4 need the corpus under `artifacts/corpus_900` (not in git; it is rendered by `scripts/run_production.py` and needs CARLA and a GPU).

1. Run the test suite: `uv run pytest`
2. Re-run the offline calibration check on the corpus (random split plus one shift test per illumination). This re-runs the sweep into a new folder, so pick an unused `--out`:
   `uv run python scripts/run_production.py --skip-render --skip-detect --out artifacts/corpus_900_recheck`
   The same check on the 54-scene spike data: `uv run python scripts/fit_estimator.py artifacts/spike/raw`
3. Print the baseline sweep summary (Table 3 of the paper): `uv run python scripts/summarize_sweep.py`
4. Re-run the calibrated tolerance sweep (13 tolerances, about 1 minute):
   `uv run python -m harness.sweep --corpus artifacts/corpus_900 --out artifacts/corpus_900_calibrated_sweep_new --policies miss-risk --estimator calibrated --miss-risk-tolerances 0.01 0.02 0.05 0.08 0.10 0.12 0.15 0.18 0.20 0.25 0.30 0.40 0.50 --width-px 800 --height-px 600 --fov-degrees 90 --camera-height-m 14`
5. Generate the publication figures into `paper/figures/`:
   `uv run python scripts/plot_tradeoffs.py`, `uv run python scripts/plot_calibration.py`, `uv run python scripts/visualize_double_fault.py`
6. Build the paper (MiKTeX or TeX Live): `cd paper && latexmk -pdf main.tex` writes `paper/main.pdf`.
7. Inspect one scene (conditions, truth, detections, tracks, every policy's decision): `uv run python scripts/inspect_scene.py --scene scene-0515`

Run one scenario and look at the output:

```bash
uv run python -m evidence_resolution --scenario tests/fixtures/oracle/supported.json --output-dir artifacts/demo
```

This writes `supported.trace.jsonl` (the decision log) and `supported.oracle.json` (whether the log matched the expected answer). Lint with `uv run ruff check .`.

## Repository map

| Path | What it holds |
| --- | --- |
| `src/evidence_resolution/` | Association, reconciliation, calibrated estimator, miss-risk policy, scenario runner, CLI |
| `src/trace_contracts/`, `src/baselines/` | Frozen M1 contracts and the five baseline policies |
| `src/scenario_gen/`, `src/sweep/`, `src/harness/` | Corpus generation, sweep CLI, calibrated sweep |
| `scripts/` | Production runner, calibration check, plotting scripts, scene inspector |
| `paper/` | Preprint source, figures, arXiv bundle |
| `tests/` | `spec/` contract tests, `integration/` tests, `fixtures/` oracle scenarios, plus per-track tests |
| `docs/planning/` | Contracts, track plans, team responsibilities, archived proposal and decisions |
| `docs/milestones/` | Advisor debriefs |
| `docs/research/` | Novelty survey and direction status |
| `meetings/` | Advisor and team meeting records |
| `.agents/skills/` | Skills that guide AI coding agents in this repo |
| `.githooks/`, `.github/` | Test-change guard hook, PR template, lint workflow |

## Team and tracks

| Member | Track |
| --- | --- |
| Aditya Hegde (lead) | Measurement definitions, deterministic core, evaluation |
| Rishi Sheth | Controlled-correlation scenario generator and corpus |
| Pranav Senghal | Sweep harness, baseline policies, release |

## Contributing

1. Branch from `dev`; never commit to `dev` or `main` directly.
2. Test first: write a failing test, make it pass, then clean up. Never edit or weaken an existing test assertion without asking Aditya.
3. Install the commit guard once: `uv run python .agents/skills/git-workflow/scripts/install_hooks.py`.
4. Open a pull request into `dev` and request review from Aditya and the other teammate. The PR template has a required "Test changes" section.
5. Using an AI agent? Start it in this folder; it loads `AGENTS.md`, asks who you are, and routes you to your track.

Definitions frozen at milestone M1 (the dependence measure, agreement-reliability measure, correlation channels, scenario matrix, and thresholds) change only through Aditya.

## Key decisions

AD-001 to AD-004 in [`docs/planning/archived/DECISIONS.md`](docs/planning/archived/DECISIONS.md) apply to all work. The most important: simulator truth is used for scoring only and never enters the claim stream or the policy.

## License

No license has been chosen yet. Apache-2.0 is planned for the first release.
