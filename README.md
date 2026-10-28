# TRACE: When Agreement Is Not Evidence

Measuring correlated failure in multi-agent visual evidence resolution. SJSU capstone, advised by Dr. Kaikai Liu.

## The idea

A team of drones inspects a road. Drone A reports a blockage, drone B confirms it, and the system closes the task because two sources agreed. That is only safe if the two reports can be wrong independently. If both drones use the same detector, the same viewpoint, or the same lighting, they can agree and be wrong together.

This project builds a benchmark and measurement harness that answers:

1. At what level of dependence between agents does a second confirming report stop reducing false task closures?
2. Can dependence be measured from claim streams alone, without simulator truth?
3. Do the four correlation channels (shared occluder, detector model version, viewpoint, illumination) hurt decisions equally?

It is not a new fusion algorithm, and results apply to simulation only. Full argument: [`docs/planning/PROPOSAL_CORRELATED_FAILURE.md`](docs/planning/PROPOSAL_CORRELATED_FAILURE.md).

## Status

- **Phase:** design. The research framing awaits advisor approval (milestone M0); implementation is a separate gate.
- **Code today:** a small deterministic prototype that turns synthetic road-blockage claims into a belief status, a task action, and a causal trace. It is disposable and is expected to be rebuilt. See [`docs/planning/APPENDIX_PROTOTYPE_STATUS.md`](docs/planning/APPENDIX_PROTOTYPE_STATUS.md).
- **Schedule:** 2026-10-27 to 2027-01-22. Milestones and owners are in [`docs/planning/TEAM_RESPONSIBILITIES.md`](docs/planning/TEAM_RESPONSIBILITIES.md).

## Quickstart

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/AdityaHegde712/TRACE.git
cd TRACE
git switch dev
uv sync
uv run pytest
```

Run one scenario and look at the output:

```bash
uv run python -m evidence_resolution --scenario tests/fixtures/oracle/supported.json --output-dir artifacts/demo
```

This writes `supported.trace.jsonl` (the decision log) and `supported.oracle.json` (whether the log matched the expected answer). Lint with `uv run ruff check .`.

## Repository map

| Path | What it holds |
| --- | --- |
| `src/evidence_resolution/` | Claim and trace contracts, the resolution policy, scenario runner, CLI |
| `tests/` | `spec/` contract tests, `integration/` tests, `fixtures/` oracle scenarios |
| `docs/planning/` | Proposal, decisions, team responsibilities, prototype status |
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

AD-001 to AD-004 in [`docs/planning/DECISIONS.md`](docs/planning/DECISIONS.md) apply to all work. The most important: simulator truth is used for scoring only and never enters the claim stream or the policy.

## License

No license has been chosen yet. Apache-2.0 is planned for the first release.
