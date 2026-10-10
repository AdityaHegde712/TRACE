# Problem Ledger

Each item is problem-first. A `RETAIN` disposition means suitable for further novelty review, not proven unoccupied.

| ID | Affected workflow and documented limitation | Candidate measurable outcome | Closest counterexample | Disposition |
|---|---|---|---|---|
| P01 | **Multi-view evidence adjudication before task closure.** A scout and verifier can disagree because of sensing/state-estimation error, motion, or real scene change; [Khronos](https://arxiv.org/html/2402.13817) explicitly separates measurements from revisable beliefs, while [AgentComm-Bench](https://arxiv.org/html/2603.20285v1) reports severe degradation from stale/conflicting content in its grid-world setup. | Entity-state precision/recall, false closure/reopening rate, time-to-verified state, unnecessary verification trips, and trace completeness. | Khronos is single-robot temporal perception; AgentComm has age-aware fusion/fallback but lacks visual-evidence lineage and task lifecycle. | **RETAIN, 4/5 candidate problem.** It is specific, visual, agentic, and demoable. Do not claim a new robust-fusion algorithm. |
| P02 | **Role-appropriate shared-state access without raw-feed broadcasting.** Open-vocabulary map data volume is a stated multi-robot bottleneck in [MR-COGraphs](https://arxiv.org/html/2412.18381v2); it exchanges incremental graph records. [Mobile Communication Network-Guided VLN](https://www.tkn.tu-berlin.de/bib/khan2025mobile/khan2025mobile.pdf) motivates querying objects outside an individual robot’s view. | Bytes per completed inspection, role-view size, raw-evidence retrievals, query latency/accuracy, target recall, mission time. | MR-COGraphs and Khan et al. are close counterexamples to compressed shared maps and central queryable maps. | **RETAIN AS RUNTIME CONTRACT, 3/5 standalone.** Do not headline compact mapping; use it to support P01. |
| P03 | **World-state-triggered repair after contradiction, expiry, agent loss, or urgent discovery.** [DEXTER-LLM](https://arxiv.org/abs/2508.14387) and [Ghezzi et al. (2025)](https://arxiv.org/abs/2411.02062) already support online adaptation/repair. | Validated findings, makespan, repair latency, unnecessary reassignments, model calls. | DEXTER-LLM and dynamic MRTA repair are direct counterexamples. | **REJECT AS PRIMARY CONTRIBUTION.** Keep as behavior/evaluation required by P01. |
| P04 | **Communication faults and stale beliefs.** [AgentComm-Bench](https://arxiv.org/html/2603.20285v1) already defines latency, loss, bandwidth collapse, async updates, stale memory, and conflict stressors. | Robustness curves, stale-entity errors, re-verification time. | AgentComm-Bench is the direct counterexample. | **REJECT AS PRIMARY CONTRIBUTION.** Use as adversarial evaluation only. |
| P05 | **Replayable causal explanation of why a visual observation changed a mission task.** ROS 2 [rosbag2](https://github.com/ros2/rosbag2) already records/replays timestamped transport, but it does not by itself encode semantic causal links from visual evidence to entity belief to assignment/outcome. | Percentage of assignments/closures linked to source evidence and policy version; deterministic replay agreement; failure-attribution time. | rosbag2 for transport replay; MultiUAV-Plat includes a viewer/mission validation workflow. | **RETAIN AS A PORTFOLIO DIFFERENTIATOR, 3/5.** It strengthens P01 but must not be presented as a new logging format. |

## Current Problem Thesis (Hypothesis)

**In a heterogeneous autonomous search-and-inspect team, distributed visual reports are not enough to safely and efficiently decide what the team currently believes, when a finding is sufficiently verified to close or create a task, and why a later replanning decision occurred.**

The proposed system response is an **Evidence-Gated Visual Task Orchestration** control plane: it preserves evidence claims and belief status, creates explicit verification gates, publishes role-specific projections, and emits a replayable causal trace. This is a project hypothesis to test against first-report-wins, majority-vote, always-verify, static-plan, and periodic-replan baselines.

## Explicit Non-Claims

- Not a new scene-graph mapping method.
- Not a new generic multi-robot planner or task allocator.
- Not a formal safety, calibration, fault-tolerance, or human-factors claim.
- Not a claim of universal portability beyond the reference mission; extensibility is established only at the documented adapter-contract level.
