# Collaborative Perception & V2X Autonomous Driving: Modern Literature Survey & Replication Roadmap

**Date:** 2026-11-24  
**Scope:** Literature foundation, taxonomy, datasets, baseline models, and replication target for CMPE 295A / 295B (*Agentic Visual Perception in Distributed Autonomous Systems*).  
**Supercedes:** Quarantined and archived 2D heuristic surveys (`docs/research/archived/trace_v1_survey/`).  

---

## 1. Executive Problem Formulation

In autonomous driving and multi-robot fleets, single-agent perception suffers from fundamental physical limits:
1. **Dynamic and Static Occlusions:** Trucks, buildings, and vegetation create severe sensory blind spots.
2. **Long-Range Attenuation:** Point-cloud sparsity and camera pixel resolution drop with distance squared ($1/d^2$).
3. **Adverse Environmental Noise:** Glare, precipitation, and low-light conditions degrade single-sensor fidelity.

Collaborative Perception (also termed Cooperative Perception or Vehicle-to-Everything [V2X] Perception) overcomes these limits by enabling connected autonomous vehicles (CAVs) and roadside infrastructure units (RSUs) to share sensory information over wireless networks (DSRC, C-V2X).

The core challenge of collaborative perception is the **Rate-Perception Tradeoff**:
$$\max \text{Performance} \quad (\text{AP}_{3D}) \quad \text{s.t.} \quad \text{Bandwidth} \le B, \quad \text{Latency} \le \Delta t$$

---

## 2. Fusion Paradigm Taxonomy

Collaborative perception architectures are categorized by the operational stage at which inter-agent information is fused:

```
[Raw Sensors] ────────► Early Fusion ────────► [Massive Bandwidth, Upper Bound AP]
       │
[Local Backbone] ─────► Intermediate Fusion ──► [SOTA: Feature Maps via Attention/GNN/Transformers]
       │
[Local 3D Bounding Boxes] ► Late Fusion ─────► [Low Bandwidth, Fails on Occlusions]
```

### A. Early Fusion (Data-Level)
- **Mechanism:** CAVs transmit raw, uncompressed 3D LiDAR point clouds or raw camera frames to an ego vehicle before running perception.
- **Strengths:** Retains complete sensory information; serves as the empirical theoretical upper bound for detection accuracy.
- **Fatal Flaws:** Transmission volumes exceed hundreds of megabits per frame ($>100\text{ MB/s}$), creating severe network congestion, packet drops, and unacceptable latency.

### B. Late Fusion (Decision-Level)
- **Mechanism:** Each agent runs its own local 3D detector (e.g., PointPillars, SECOND) and broadcasts its final 3D bounding boxes, classes, and confidence scores. The ego vehicle aggregates boxes using spatial matching and Non-Maximum Suppression (NMS).
- **Strengths:** Minimal communication bandwidth ($<1\text{ KB/frame}$).
- **Fatal Flaws:** Fails to resolve occlusions. If a vehicle is heavily occluded, no single agent detects it locally with sufficient confidence, meaning nothing is broadcast. Consensus cannot recover objects that all individual detectors missed.

### C. Intermediate Fusion (Feature-Level — The Modern Standard)
- **Mechanism:** Each CAV extracts intermediate spatial feature maps (e.g., Bird's-Eye-View [BEV] representations) using a shared neural backbone, compresses the feature tensors, transmits them over V2V, and fuses them via spatial cross-attention, graph neural networks, or transformers.
- **Strengths:** Achieves near-early-fusion detection accuracy ($\approx 95\%\text{ of early fusion AP}$) while reducing communication volume by $10\times$ to $100\times$.
- **Core Challenge:** Avoiding transmission of redundant features over clear road surfaces and actively resolving spatial occlusions.

---

## 3. Foundational Datasets & Ecosystems

The modern V2X perception literature standardizes on two primary benchmark ecosystems:

### 1. OPV2V (Open Benchmark Dataset for V2V Communication — ICRA 2022)
- **Authors:** Zhirui Xu, Xiangbo Gao, Hao Xiang, Xin Xia, Jiaqi Ma (UCLA Mobility Lab).
- **Simulation Platform:** CARLA 0.9.10 + OpenCDA co-simulation.
- **Specs:**
  - 73 scenarios, 11,464 frames, 2 to 7 cooperating CAVs per frame.
  - Multi-modal sensing: 64-channel LiDAR ($1.3\text{M pts/s}$) + 4 multi-view RGB cameras ($1920 \times 1080$, $360^\circ$ FOV).
  - High diversity: Urban downtown (Culver City), highway interchanges, rural curves, varying traffic densities.
  - Complete 3D bounding ground truth for vehicles across all views.
- **Standard Benchmark Tasks:** Cooperative 3D object detection, BEV semantic segmentation.

### 2. V2V4Real (Real-World Large-Scale V2V Dataset — CVPR 2023)
- **Authors:** Runsheng Xu, Hao Xiang, Xin Xia, Zhirui Xu, Zhengzhong Tu, Meng Lu, Zhaoliang Zheng, Jiaqi Ma.
- **Platform:** Real-world dual-vehicle testbed driven simultaneously across 410 km in Columbus, Ohio.
- **Specs:**
  - Synchronized LiDAR (32-channel RoboSense), multi-view cameras, GNSS/IMU RTK localization.
  - 20K LiDAR frames, 40K RGB images, 240K annotated 3D bounding boxes.
- **Role:** The critical bridge proving Sim2Real transferability for cooperative models trained on OPV2V.

### 3. OpenCOOD Framework (IEEE T-IV 2022)
- Official open-source codebase supporting OPV2V, V2X-Sim, DAIR-V2X, and V2V4Real.
- Built on PyTorch and `spconv` (sparse 3D convolutions). Provides modular data loaders, coordinate transformation matrices, pose-noise injection, and standard evaluation suites.

---

## 4. Key SOTA Architectures & Baselines

| Model | Venue | Backbone / Architecture | Fusion Strategy | Bandwidth / Compression |
| :--- | :--- | :--- | :--- | :--- |
| **PointPillars (No Fusion)** | CVPR 2019 | PointPillars (Pillar feature net + 2D CNN) | Single-Agent (Baseline) | $0\text{ MB/s}$ |
| **Late Fusion** | Standard | PointPillars local detection + Spatial NMS | Decision-Level (Boxes) | $\approx 0.001\text{ MB/s}$ |
| **F-Cooper** | SEC 2019 | VoxelNet / PointPillars | Max-out feature pooling | $\approx 1.5\text{ MB/s}$ (Dense) |
| **AttFuse** | ICRA 2022 | PointPillars + Multi-head self-attention | Attentive graph aggregation | $\approx 1.5\text{ MB/s}$ (Dense) |
| **V2VNet** | ECCV 2020 | GNN + spatial-temporal recurrent state | Graph message passing | $\approx 1.5\text{ MB/s}$ (Dense) |
| **V2X-ViT** | ECCV 2022 | Vision Transformer + Spatial/Temporal Multi-Scale | Dual-branch spatial cross-attention | $\approx 1.5\text{ MB/s}$ (Dense) |
| **CoBEVT** | CoRL 2022 | SinBEVT (Facetted Sparse Transformer) | Sparse cross-agent BEV attention | $\approx 1.2\text{ MB/s}$ (Dense) |
| **Where2comm** | NeurIPS 2022 / TPAMI 2024 | PointPillars / SECOND + Spatial Confidence Estimator | Spatial Confidence Map selection | **$0.01\text{ to }0.2\text{ MB/s}$ (Dynamic)** |

### Deep Dive: Where2comm (The Crucial Reference for TRACE)
- **Core Concept:** Instead of broadcasting dense BEV feature maps across the entire road grid, Where2comm generates a spatial confidence map $M \in \mathbb{R}^{H \times W}$.
- **Mechanism:** Grid cells representing empty pavement, sky, or static buildings have low informational entropy. High-confidence cells (objects, complex intersections, high-uncertainty zones) are prioritized.
- **Communication Throttling:** Agents broadcast only the top-$p\%$ feature vectors. Where2comm achieves higher $\text{AP}_{3D}$ than dense baselines with **over $100\times$ bandwidth reduction**.

---

## 5. Replication Target for CMPE 295B

To establish a solid empirical foundation, we will replicate the standard **OpenCOOD** cooperative 3D detection pipeline on the **OPV2V** benchmark before developing our custom agentic active-verification method.

### Concrete Replication Target
- **Framework:** `OpenCOOD` ([DerrickXuNu/OpenCOOD](https://github.com/DerrickXuNu/OpenCOOD))
- **Benchmark:** `OPV2V` (Culver City / Town05 test split)
- **Sensor Modality:** 3D LiDAR point clouds (PointPillars backbone)
- **Baselines to Reproduce:**
  1. `Single-Agent (PointPillars)`: Lower bound (no collaboration).
  2. `Late Fusion`: 3D bounding box broadcast + NMS.
  3. `AttFuse (Attentive Fusion)`: Standard dense intermediate feature fusion.
  4. `Where2comm`: Sparse spatial confidence map intermediate fusion.
- **Evaluation Metrics:**
  - Detection Accuracy: 3D Bounding Box Average Precision ($\text{AP}_{3D}$ at $\text{IoU} = 0.5$ and $\text{IoU} = 0.7$).
  - Communication Volume: Bandwidth consumed per frame (Megabits / MB per time-step).
  - Operating Curve: $\text{AP}_{3D}$ vs. Bandwidth Pareto frontier.

---

## 6. Where TRACE Improves Upon SOTA (The CMPE 295B Hypothesis)

### The SOTA Limitation
`Where2comm` and existing communication-efficient frameworks rely on **unilateral broadcast**: each agent decides what to send based only on its own local confidence. When an agent experiences severe local occlusion or sensor degradation, its confidence map is blind to what it is missing.

### The TRACE Agentic Active Verification Hypothesis
Instead of unilateral broadcast, TRACE introduces **Bidirectional Agentic Active Verification**:
1. **Uncertainty & Frustum Intersection:** Ego vehicle computes its visibility frustum and flags high-uncertainty occlusion zones.
2. **Targeted Agentic Queries:** Ego vehicle sends a targeted spatial query requesting features *specifically for its occluded coordinates* from collaborating CAVs that have clear line-of-sight.
3. **Dependence-Aware Evidence Gating:** Rather than blindly fusing received features, TRACE evaluates inter-agent viewpoint disparity and sensor diversity to dynamically weight or verify incoming evidence.

**Expected Outcome:** Higher $\text{AP}_{3D}@0.7$ on occluded vehicles with lower overall communication volume than Where2comm.
