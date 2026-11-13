# Track B scenario corpus workflow

Track B turns the frozen M1 scenario matrix into a repeatable CARLA corpus.
It plans the physical scenes first, then schedules detector pairings over the
same rendered frames. The generator does not alter the M1 factors or use
evaluator truth in any agent-visible artifact.

## Plan a corpus

From the repository root, create a one-scene-per-cell corpus plan with:

```bash
.agent-tasks/tooling/bin/uv run python -m scenario_gen \
  --out artifacts/scenario-gen/plan \
  --town Town10HD \
  --scenes-per-render-cell 1 \
  --seed 42
```

This writes a canonical `manifest.json` and `detector_jobs.json`. With one
scene per physical render cell, the plan contains 18 renders and 54 detector
jobs: each render is reused for the three frozen detector pairings. The
manifest records the town, seed, generator version, contract version, and one
fixed seed per planned scene. Its SHA-256 digest is printed by the command and
can be used to confirm that teammates are using the same plan.

## Corpus boundaries

The corpus layout keeps observations and evaluator labels in separate paths:

```text
<corpus>/
  manifest.json
  detector_jobs.json
  frames/
  reports/
  evaluator_truth/
```

`frames/` stores RGB images and `reports/` stores only `AgentFrameReport`
objects. `evaluator_truth/` stores `TruthObject` records for scoring. The
report writer and detector adapter do not import evaluator truth, so simulator
object IDs and labels cannot enter the online observation path.

## Rendering on a CARLA host

`scenario_gen.render.render_entry` consumes one `ScenarioManifestEntry` and a
connected CARLA client. It refuses to render if the loaded map does not match
the manifest town. It stages CARLA's RGB and ground-truth output privately,
copies RGB images to `frames/`, then exports truth only to
`evaluator_truth/`. The staging directory is removed afterward.

The repository tests validate planning, schema boundaries, and the adapter
logic without CARLA. A real corpus still requires a CARLA 0.9.16 host with the
planned map loaded. On that host, render every manifest entry, retain the
printed manifest hash with the captured corpus, and inspect CARLA failures
before declaring a physical render cell complete.
