# Track C Done Checklist

Updated: 2026-11-18. Owner: Pranav Senghal.
M0 and M1 are complete per Aditya's confirmation. Frozen interface: m1-v0.
C1/C2 implementation commit: 6cb9925. Publication branch: feature/track-c.

## Setup and contracts

1. [x] Load onboarding and confirm Track C ownership.
2. [x] Install uv 0.13.7 and verify it; use CPython 3.12.16.
3. [x] Synchronize dependencies with the frozen lockfile.
4. [x] Install the Git test-change guard using .githooks.
5. [x] Fetch dev and base C1/C2 work on dc2fd6f.
6. [x] Consume trace_contracts ResolutionPolicy, TaskDecision, RunResult and RESULT_COLUMNS without modifying them.
7. [x] Read M1 contracts, matrix, channel definitions, research-answer status and approved code locations.
8. [x] Consume Track A association, IndependenceEstimator and WatermarkedReconciler.
9. [x] Record M1 confirmation and implementation decisions in local session state.

## C2 - Five baseline policies

10. [x] Add tests before implementation; observe RED for the missing baseline package.
11. [x] Implement LatestReportPolicy using newest arrival.
12. [x] Implement FirstReportPolicy using first arrival.
13. [x] Implement MajorityVotePolicy with distinct-source voting and verification on ties.
14. [x] Implement AlwaysVerifyPolicy.
15. [x] Implement NeverVerifyPolicy per Aditya's expanded handoff.
16. [x] Return frozen TaskDecision records with causal report IDs, policy version and estimator version.
17. [x] Wait on empty input; preserve valid zero-detection reports.
18. [x] Verify deterministic arrival tie-breaking and input-order stability.
19. [x] Verify repeated reports from one source cannot add votes.
20. [x] Refactor shared behavior and rerun focused tests.
21. [x] Keep evaluator truth out of baseline imports and decisions.

## C1 - Corpus sweep and scoring

22. [x] Add tests before implementation; observe RED for the missing sweep package.
23. [x] Provide python -m harness.sweep and python -m sweep entry points.
24. [x] Read Track B manifest, nested report files and evaluator_truth records.
25. [x] Cross selected scenes, detector pairings and all five policies.
26. [x] Reconcile reports with WatermarkedReconciler before policy decisions.
27. [x] Reject late, missing, duplicate, unknown-version and ambiguous records explicitly.
28. [x] Keep truth in evaluator-only scoring.
29. [x] Score co-visible objects, confirmed objects, misses at close, false confirmations and verification actions.
30. [x] Match confirmed tracks one-to-one to real objects; prevent duplicate counting.
31. [x] Emit results.csv in exact RESULT_COLUMNS order with false_clearance and trace_sha256.
32. [x] Retain exact trace bytes, inputs, configuration and input hashes.
33. [x] Fingerprint inputs/configuration and refuse existing output directories.
34. [x] Prove identical reruns produce byte-identical CSV files and matching trace hashes.
35. [x] Prove changes to evaluator truth affect scores but not decisions or trace hashes.
36. [x] Run synthetic end-to-end sweeps across all three pairings and five policies.
37. [ ] Run the full physical scenario corpus when Rishi supplies reports and truth.
38. [ ] Deliver real-corpus result tables and retained artifacts to Aditya.

Current scope: one frame from two sources per scene/pairing, one decision after
reconciliation, one verification action per VERIFY decision. Camera configuration
is explicit. Follow-up observations are not simulated. Baseline runs use
IndependenceEstimator; treatment/calibration experiments remain coordinated with Track A.
The frozen result schema does not include the old checklist's latency/rejection metrics.

## Validation and packaging completed

39. [x] Pass 27 new focused Track C tests.
40. [x] Pass the complete suite: 258 tests.
41. [x] Pass uv run ruff check . across the feature worktree.
42. [x] Pass formatting checks for all 11 new Python files.
43. [x] Build the wheel and verify all new packages are included.
44. [x] Validate CLI help and subprocess execution from the installed worktree.
45. [x] Document inputs, outputs, scoring rules and commands in docs/planning/TRACK_C_SWEEP.md.
46. [x] Commit implementation on a feature branch without changing existing tests, Track A/B code or frozen contracts.
47. [x] Publish feature/track-c and verify the remote commit (initial publication bd7d8d3).
48. [ ] Open a PR into dev and obtain Aditya and Rishi reviews.

Full-suite invocation used a fresh workspace-local --basetemp after the Windows
default temporary directory denied access. The successful run had one pytest
cache-write warning. The old 16-file formatting finding was from an earlier
checkout; repository-wide formatting has not been revalidated on this branch.

## C3 - Release work still to complete

49. [ ] Update the root README and repair outdated planning links.
50. [ ] Add or verify the approved Apache-2.0 license.
51. [ ] Audit dependency licenses for the release.
52. [ ] Verify the complete quickstart from a fresh clone.
53. [ ] Document the legacy demo artifacts where still relevant.
54. [ ] Resolve release-wide formatting/documentation gaps with the relevant owners.
55. [ ] Run final release tests, lint and clean-clone checks after integration.

## C4 - Visual demonstration

56. [ ] Select a retained representative real-corpus double-miss run.
57. [ ] Show the naive false clearance and dependence-aware verification decision.
58. [ ] Link displayed results to retained traces and truth.
59. [ ] Validate the demonstration against final artifacts; coordinate interpretation with Aditya.

## C5 - Camera-to-claim documentation

60. [ ] Document camera inputs and the frozen report fields.
61. [ ] Explain source IDs, timestamps, spatial references, provenance and replay metadata.
62. [ ] Document malformed-input handling and evaluator-only truth separation.
63. [ ] Provide example input payloads and output reports without changing frozen definitions.

## Handoffs and completion

64. [x] Resolve the prior setup and M0/M1 approval blockers.
65. [ ] Rishi: supply the generated corpus, matching camera settings and separate detector outputs.
66. [ ] Aditya: review policy/scoring choices and interpret result tables.
67. [ ] Retain every experimental run and confirm reported statistics trace to its artifacts.
68. [ ] Deliver the integrated benchmark, demo, adapter documentation and release instructions.

Next action: open the feature/track-c PR into dev and evaluate Rishi's corpus.
