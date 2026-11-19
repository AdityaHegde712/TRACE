# Track C sweep and baselines

Run this from a checkout containing the C1/C2 packages:

```powershell
uv sync --frozen
uv run python -m harness.sweep --corpus artifacts/corpus --out artifacts/evaluation-001 --width-px 800 --height-px 600 --fov-degrees 90 --camera-height-m 14
```

Use the camera settings that produced the corpus. The values above are the
Track A v0 example, not inferred metadata. `python -m sweep` is an equivalent
entry point. No simulator or detector installation is needed to score saved reports.

## Inputs and policy behavior

The reader consumes Track B's canonical `manifest.json`, report envelopes under
`reports/**/*.json`, and truth files under `evaluator_truth/`. Keep detector outputs
in separate report subdirectories: Track B filenames do not include detector names.
Records are selected by their contents, not the subdirectory name. Reports may reuse
an ID across detector alternatives, but IDs must be unique within each evaluated pair.

The v0 evaluation unit is one scene, one frame, two sources. Each source must have
one report for every selected detector. Multiple frames for one source/detector are
rejected because the frozen truth records do not define a temporal scoring unit.
The heterogeneous pairing assigns YOLO to the lexically first source and RT-DETR to
the second, matching the ordered model pair in the contract.

The default sweep crosses every manifest scene with three detector pairings and five
policies. `--pairings homogeneous_yolo` or `--policies first-report-wins always-verify`
select a subset explicitly. Missing reports never reduce the sweep silently.

| Policy | Confirmed tracks and task action |
| --- | --- |
| latest-report | Close with tracks detected in the newest arrival. |
| first-report-wins | Close with tracks detected in the first arrival. |
| majority-vote | Confirm tracks with a strict majority of distinct sources; verify on a tied vote, otherwise close. |
| always-verify | Request verification; confirm no tracks. |
| never-verify | Close with all observed tracks, even when every report is empty. |

All policies wait on empty input. Empty detections in an existing report count as
a completed observation. Arrival ties use observed time, source ID, then report ID.
Majority voting uses only the latest report from each source as a vote. Policies
consume the shared association port; the CLI uses Track A's pose projection rule.
`--match-distance-m` defaults to 4.0.

Reports pass through `WatermarkedReconciler` before the policy is called. The default
slack is one second (`--slack-seconds`) and must be strictly positive. Zero and
negative slack are rejected before reading the corpus. Late reports cause an
explicit failure.
Each policy is called once after the scene's stream is flushed, consistent with the
M1 task-decision unit. Verification cost is one requested re-observation per VERIFY
decision, not the number of detections. The runner does not simulate that follow-up.

## Scores and retained evidence

The evaluator matches only detections from the decision's causal report IDs to truth,
so unselected reports cannot supply matches for first/latest-report policies.
Co-visible object counts still use truth from both views. Matching uses same-label,
same-view boxes
at IoU >= 0.5 (`--iou-threshold`). A deterministic one-to-one matching prevents
duplicate confirmations. `objects_confirmed` counts matched co-visible objects;
objects visible to only one source do not enter that denominator. Tracks matching
no available real object, including excess duplicate tracks, count as false
confirmations. Missing objects count as missed-at-close only for CLOSE decisions.

Outputs use a new directory for every invocation:

- `results.csv`: `RunResult` records in frozen `RESULT_COLUMNS` order.
- `traces/<cell>/<scene>/<policy>.json`: exact bytes hashed by `canonical_trace_hash`.
- `inputs/`: retained manifest, reports and evaluator truth for replay.
- `run.json`: input SHA-256 values, camera and scoring configuration, and run ID.

The run ID fingerprints inputs and configuration. The baseline estimator is
`IndependenceEstimator`; these heuristics record its version but do not query it.
Identical inputs and settings produce identical CSV and trace bytes. Changing truth
can change scores and the run ID, but cannot change decisions or trace hashes.
An existing output directory is rejected to preserve previous runs. Validation
finishes before publishing the table; filesystem failures can leave partial artifacts.

## Checks and handoff

```powershell
uv run pytest tests/track_c -q
uv run pytest
uv run ruff check .
```

The tests use synthetic geometry and Track B writers, including all three detector
pairings, shared misses, correct detections, false confirmations, late arrivals,
invalid records, truth isolation, and exact-byte reruns. A real CARLA corpus still
needs an evaluation run before reporting experimental results. Track A owns the
accuracy of cross-view association and interpretation of the resulting tables.
