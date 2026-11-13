# Track B: Rishi (simulation and scenario generation)

## Read first
In `docs/planning/TEAM_RESPONSIBILITIES.md`: "Roles", "Track B", "Milestones" (M1, M2, M4), "Dependencies and handoffs", "Risks and fallbacks" (items 2 and 3).
In `docs/planning/PROPOSAL_CORRELATED_FAILURE.md`: "The problem" and "What we propose to build".

## Scope
Owns B1 (latent-variable scenario generator with four correlation channels: shared occluder, shared detector model version, shared viewpoint, shared illumination), B2 (fixed-seed versioned corpus, generation parameters kept), B3 (truth kept out of the claim stream), and B4 (PX4/Gazebo spike, optional).

M1 interfaces are frozen (`m1-v0`): build against `src/trace_contracts/` and read `docs/planning/M1_CONTRACTS.md` first. New code goes in `src/scenario_gen/`, generalizing `src/spike_dependence/scene_matrix.py` and the render and detect adapters.

## Off limits (read only)
`src/trace_contracts/`, `tests/contracts/`, `src/evidence_resolution/contracts.py`, `policy.py`, `scenario.py`, `tests/spec/`, and anything defining the dependence measure, channels, scenario matrix, or thresholds. Those are Aditya's. Send requests through `.agent-tasks/TASKS.md` "Handoffs".

## Rules that matter most
- **Truth separation (AD-001):** simulator truth is written beside the claim stream, never inside it. Done-check: no field naming the true state appears in any claim record.
- **Reproducibility:** the same seed and parameters must regenerate the identical corpus. Done-check: generate twice, compare hashes.
- You hand Aditya a corpus plus its generation parameters. He never edits the corpus.
- B4 starts only after B1 to B3 are delivered. A failed spike must leave everything else runnable.

## Starter prompts
1. `Read the Track B section and tell me, in plain English, what B1 asks me to build and what I need from Aditya before I can start.`
2. `Explain the four correlation channels with one concrete drone example each. Do not write code.`
3. `Help me set up the project (uv sync, uv run pytest) and run the existing oracle scenario so I can see what a claim and a trace look like.`
