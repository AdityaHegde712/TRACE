# Project Execution Plan: Road-Blockage Verification MVP

**Status:** Owner-approved plan on 2026-10-01. This assigns planned work; it does not report completed implementation, procurement, or experiments.

## Planned responsibility split

| Member | Planned ownership |
| --- | --- |
| Aditya Hegde | Evidence lifecycle, policy rules, replay, and the independent evaluation oracle. |
| Rishi Sheth | PX4/Gazebo startup spike and synthetic scenario generation. |
| Pranav Senghal | Camera-to-claim adapter, M3OT intake check, and integration documentation. |

The team shares responsibility for the initial development effort and for resolving dataset-procurement gates. Each member’s actual Workbook contribution must be updated from completed work records before submission.

## Approved schedule

| Dates | Planned work | Acceptance gate |
| --- | --- | --- |
| Oct 1-16, 2026 | Freeze the scenario and independent-oracle design; create the code scaffold; run initial scenario tests. | The scenario contract and initial test results are recorded. |
| Oct 19-Nov 6, 2026 | Build the evidence, belief, policy, and replay core; test every transition against the oracle. | Transition tests exercise the frozen oracle. |
| Nov 9-27, 2026 | Run synthetic scenarios and the two baselines continuously; resolve reproducibility defects. | Fixed-seed runs reproduce their expected trace. |
| Nov 30-Dec 18, 2026 | Continue core experiments and run the PX4/Gazebo spike; add the adapter only if the spike passes. | The spike meets its documented two-X500, topic, sensor-stream, and startup-log criteria. |
| Jan 4-22, 2027 | Repeat final experiments, analyze results, and prepare Workbook/demo evidence. | Final reported results are traceable to retained runs and scenario definitions. |

## Meeting cadence

The meeting-log assignment requires at least one team-only meeting each week and at least one advisor meeting every two weeks. A meeting note is separate from a milestone update and must record ownership and action items.

## Evidence boundary

The primary corpus, M3OT intake, PX4/Gazebo spike, code scaffold, tests, experiments, and results remain planned until locally verified. The supporting methodology boundary is in `docs/DATASET_AND_METHOD_REVIEW.md`.
