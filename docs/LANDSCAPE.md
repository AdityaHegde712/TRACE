# Stage 1 Landscape: Existing Systems and Feasibility

## Direct Prior-Art Boundary

| System | What it already establishes | Source-backed consequence |
|---|---|---|
| [MultiUAV-Plat / Agent4Drone (2026)](https://arxiv.org/abs/2606.31073) | Multi-UAV simulator/benchmark, partial local perception, role access, viewer, and plan-act-observe-verify workflow; [repository](https://github.com/zhangsheng93/MultiUAV-Plat) is GPL-3.0. | Do not build a generic LLM-UAV simulator or copy GPL components into a permissively licensed core. |
| [COHERENT (2024)](https://arxiv.org/abs/2409.15146) | Central task decomposition/allocation, heterogeneous execution, and self-reflection feedback; [repository](https://github.com/MrKeee/COHERENT). | LLM task allocation plus feedback is not a novelty claim. |
| [DEXTER-LLM (2025)](https://arxiv.org/abs/2508.14387) | LLM subtask generation, optimized assignment/scheduling, event-based adaptation, and human verification for discoveries in unknown environments. | Dynamic task generation/replanning alone is occupied. |
| [MRBTP (2025)](https://arxiv.org/abs/2502.18072) | Decentralized multi-robot behavior-tree planning; [MIT repository](https://github.com/DIDS-EI/MRBTP). | A reusable multi-robot planner alone is occupied. |
| [MR-COGraphs (2025)](https://arxiv.org/html/2412.18381v2) | Incremental, compressed open-vocabulary multi-robot scene graph exchange/merge; [repository](https://github.com/efc-robot/MR-COGraphs). | Compact shared visual state is occupied. |
| [SlideSLAM (2024)](https://arxiv.org/abs/2406.17249) | Heterogeneous decentralized metric-semantic SLAM and observation tracking; [repository](https://github.com/MIT-SPARK/SlideSLAM). | Heterogeneous shared visual mapping/observation synchronization is occupied. |
| [Khronos (RSS 2024)](https://arxiv.org/html/2402.13817) | Temporal metric-semantic belief revision via object fragments; [repository](https://github.com/MIT-SPARK/Khronos). | Measurement-to-belief lifecycle is established in perception; it is not multi-robot orchestration. |
| [AgentComm-Bench (2026)](https://arxiv.org/html/2603.20285v1) | Latency/loss/staleness/conflict stress protocol and age-weighted fallback. | Communication fault tolerance is an evaluation axis, not this framework’s headline contribution. |

## Provisional Differentiation

The candidate runtime must not claim new mapping, task allocation, generic LLM coordination, or communication robustness. The only potentially defensible implementation space is the integration contract between:

`visual evidence claim -> temporal entity belief -> task-gating decision -> verification/replanning action -> replayable causal trace`.

This is a **provisional design inference**. Task 6 requires direct source inspection and a closest-counterexample pass before it can become a contribution recommendation.

## Feasibility Evidence

- Official Gazebo documentation recommends the Ubuntu 24.04 / ROS 2 Jazzy / Gazebo Harmonic pairing and documents `ros_gz` integration ([installation](https://gazebosim.org/docs/latest/ros_installation/), [ROS 2 integration](https://gazebosim.org/docs/harmonic/ros2_integration/)).
- [ReMRoC](https://github.com/boschresearch/remroc) is an Apache-2.0 ROS 2/Gazebo coordination benchmark with coordinator-node extension points; it also warns multi-robot navigation stacks are resource-intensive.
- PX4 is a later, not MVP, adapter: its [official simulator documentation](https://docs.px4.io/main/en/simulation/) distinguishes fast/headless SITL from Gazebo’s richer visual simulation.
- Isaac Sim is an optional backend, not the baseline: its [official requirements](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html) list RTX 4080/16GB VRAM, 32GB RAM, and 50GB storage as minimums.
- A `VisionReasoner` provider port can use hosted or open-weight multimodal models; Hugging Face documents image-text chat pipelines and Qwen2.5-VL examples ([documentation](https://huggingface.co/docs/transformers/en/chat_templating_multimodal)).

## Feasibility Inference

Use a project-owned Python event/state-machine core with a thin ROS 2/Gazebo adapter. Build deterministic/synthetic perception and scripted baselines before optional VLM calls, PX4, or a physical drone bridge. This is a five-month risk-control recommendation, not a measured performance claim.
