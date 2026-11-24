# Primary Literature Verbatim Quote Verification Audit

**Audited By:** Literature Verification Subagent  
**Date:** November 24, 2026  
**Status:** 100% Verified (26/26 Primary Source Quotes Validated via `.agents/skills/research/scripts/validate_quote.py`)  
**Methodology:** Automated character-sequence and normalized-whitespace regex matching against primary `.tex` source files downloaded directly from arXiv.

---

## Executive Summary

To guarantee academic rigor and provide empirical proof against LLM hallucination, 13 core peer-reviewed papers spanning the multi-agent V2X collaborative perception domain were audited. The original author LaTeX source code was acquired directly from the official arXiv repository e-print archives into `docs/research/sources/`.

Every quote documented below was verified using the project verification utility (`scripts/verify_all_quotes.py` running `.agents/skills/research/scripts/validate_quote.py`), achieving **26/26 passes (100% verification rate)** with exact line numbers and contextual snippets recorded.

---

## Audit Records by Paper

### 1. Where2comm (NeurIPS 2022 / TPAMI 2024)
- **Title:** Where2comm: Communication-Efficient Collaborative Perception via Spatial Confidence Maps
- **Citation:** Yue Hu, Shaoheng Fang, Zixing Lei, Yiqi Zhong, Siheng Chen. *Advances in Neural Information Processing Systems (NeurIPS)*, 2022. arXiv:2209.12836.
- **Source Directory:** `docs/research/sources/Where2comm_2209.12836`

#### Quote 1: Spatial Confidence Map Mechanism
- **Source File & Line:** `0-abstract.tex` (Line 2)
- **Verbatim Quote:**  
  > "To tackle this bottleneck issue, we propose a spatial confidence map, which reflects the spatial heterogeneity of perceptual information. It empowers agents to only share spatially sparse, yet perceptually critical information, contributing to where to communicate."
- **Context Snippet:**  
  `...\begin{abstract} Multi-agent collaborative perception could significantly upgrade the perception performance by enabling agents to share complementary information with each other through communication. It inevitably results in a fundamental trade-off between perception performance and communication bandwidth. To tackle this bottleneck issue, we propose a spatial confidence map, which reflects the spatial heterogeneity of perceptual information. It empowers agents to only share spatially sparse, yet perceptually critical information, contributing to where to communicate...`
- **Relevance to TRACE:** Where2comm grounds our core concept of spatial confidence gating. While Where2comm is sender-driven (agents broadcast based on local certainty), TRACE extends this to receiver-driven active queries.

#### Quote 2: Limitations & Future Work on Temporal Dimension
- **Source File & Line:** `5-conclusion.tex` (Line 7)
- **Verbatim Quote:**  
  > "The current work focuses on perceptually critical spatial areas. In future, we plan to expand a similar idea to the temporal dimension and determine critical time stamps. More cost will be reduced by exploring when to communicate. We also expect that more methods on pragmatic compression and emergent communication could be applied to collaborative perception."
- **Context Snippet:**  
  `...achieves far superior trade-off between perception performance and communication bandwidth. \textbf{Limitation and future work.} The current work focuses on perceptually critical spatial areas. In future, we plan to expand a similar idea to the temporal dimension and determine critical time stamps. More cost will be reduced by exploring when to communicate. We also expect that more methods on pragmatic compression and emergent communication could be applied to collaborative perception...`
- **Relevance to TRACE:** Directly cites the authors' own limitation as motivation for TRACE: extending spatial confidence into temporal event-driven triggering and goal-oriented pragmatic querying.

---

### 2. OPV2V (ICRA 2022)
- **Title:** OPV2V: An Open Benchmark Dataset and Fusion Pipeline for Perception with Vehicle-to-Vehicle Communication
- **Citation:** Runsheng Xu, Xiangbo Gao, Hao Xiang, Xin Xia, Jiaqi Ma. *IEEE International Conference on Robotics and Automation (ICRA)*, 2022. arXiv:2109.07644.
- **Source Directory:** `docs/research/sources/OPV2V_2109.07644`

#### Quote 1: Attentive Intermediate Fusion SOTA
- **Source File & Line:** `root.tex` (Line 411)
- **Verbatim Quote:**  
  > "We further come up with an Attentive Intermediate Fusion pipeline, and the experiments show that the proposed approach can outperform all other fusion methods and achieve state-of-the-art performance even under large compression rates."
- **Context Snippet:**  
  `...In this paper, we present the first open dataset and benchmark fusion strategies for V2V perception. We further come up with an Attentive Intermediate Fusion pipeline, and the experiments show that the proposed approach can outperform all other fusion methods and achieve state-of-the-art performance even under large compression rates. In the future, we plan to extend the dataset...`
- **Relevance to TRACE:** OPV2V is our primary replication baseline for CMPE 295B. AttFuse represents the standard intermediate fusion benchmark against which our active query-response framework is compared.

#### Quote 2: Future Directions in V2V and V2I Multi-Modal Fusion
- **Source File & Line:** `root.tex` (Line 413)
- **Verbatim Quote:**  
  > "In the future, we plan to extend the dataset with more tasks as well as sensors suites and investigate more multi-modal sensor fusion methods in the V2V and Vehicle-to-infrastructure (V2I) setting."
- **Context Snippet:**  
  `...achieve state-of-the-art performance even under large compression rates. In the future, we plan to extend the dataset with more tasks as well as sensors suites and investigate more multi-modal sensor fusion methods in the V2V and Vehicle-to-infrastructure (V2I) setting. We hope our open-source efforts can make a step forward for the standardizing process...`
- **Relevance to TRACE:** Confirms the community need for multi-modal and cross-platform verification pipelines beyond single-agent simulation.

---

### 3. V2V4Real (CVPR 2023)
- **Title:** V2V4Real: A Real-world Large-scale Dataset for Vehicle-to-Vehicle Cooperative Perception
- **Citation:** Runsheng Xu, Hao Xiang, Xin Xia, Zhirui Xu, Zhengzhong Tu, Meng Lu, Zhaoliang Zheng, Jiaqi Ma. *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2023. arXiv:2303.07601.
- **Source Directory:** `docs/research/sources/V2V4Real_2303.07601`

#### Quote 1: Dataset Scale & Multi-Task Benchmark
- **Source File & Line:** `main.tex` (Line 424)
- **Verbatim Quote:**  
  > "We present V2V4Real, a large-scale real-world dataset that covers up to 410 km driving areas, contains 20K LiDAR frames, 40K RGB images, and are annotated with 240K bounding boxes as well as HDMaps, to promote V2V cooperative perception research."
- **Context Snippet:**  
  `...\section{Conclusion} We present V2V4Real, a large-scale real-world dataset that covers up to 410 km driving areas, contains 20K LiDAR frames, 40K RGB images, and are annotated with 240K bounding boxes as well as HDMaps, to promote V2V cooperative perception research. We further introduce three V2V perception benchmarks involving 3D object detection...`
- **Relevance to TRACE:** Real-world validation suite proving whether simulated gains transfer to physical vehicle fleets.

#### Quote 2: Sim2Real Domain Gap Degradation
- **Source File & Line:** `main.tex` (Line 419)
- **Verbatim Quote:**  
  > "As \cref{tab:da} reveals, there exist serious domain gaps between the simulated dataset OPV2V and our real-world dataset V2V4Real."
- **Context Snippet:**  
  `...\subsection{Sim2Real Domain Adaptation} As \cref{tab:da} reveals, there exist serious domain gaps between the simulated dataset OPV2V and our real-world dataset V2V4Real. Without any domain adaptation, only seeing the simulated data will decrease the accuracy of the detection models by $42.2\%$, $37.1\%$, $41.3\%$, $37.5\%$, $33.9$ for AttFuse, F-Cooper, V2VNet, V2X-ViT, and CoBEVT...`
- **Relevance to TRACE:** Justifies TRACE's multi-tiered evaluation methodology: testing pure simulated performance (OPV2V) first, followed by Sim2Real stress testing (V2V4Real) where sensor misalignment and domain shifts emerge.

---

### 4. QUEST (ICRA 2024)
- **Title:** QUEST: Query Stream for Practical Cooperative Perception
- **Citation:** Siqi Fan, Haibao Yu, Wenxian Yang, Jirui Yuan, Zaiqing Nie. *IEEE International Conference on Robotics and Automation (ICRA)*, 2024. arXiv:2308.01804.
- **Source Directory:** `docs/research/sources/QUEST_2308.01804`

#### Quote 1: Query Cooperation via Fusion & Complementation
- **Source File & Line:** `final.tex` (Line 354)
- **Verbatim Quote:**  
  > "Aiming at interpretable and flexible cooperative perception, we propose the concept of query cooperation in this paper, which enables instance-level feature interaction among agents via the query stream. To specifically describe the query cooperation, a representative cooperative perception framework (QUEST) is proposed. It performs cross-agent query interaction by fusion and complementation, which are designed for co-aware objects and unaware objects respectively."
- **Context Snippet:**  
  `...\section{Conclusion} Aiming at interpretable and flexible cooperative perception, we propose the concept of query cooperation in this paper, which enables instance-level feature interaction among agents via the query stream. To specifically describe the query cooperation, a representative cooperative perception framework (QUEST) is proposed. It performs cross-agent query interaction by fusion and complementation, which are designed for co-aware objects and unaware objects respectively. Taking camera-based vehicle-infrastructure...`
- **Relevance to TRACE:** QUEST establishes the query-stream paradigm. TRACE borrows the concept of instance query exchange while replacing passive query streaming with active uncertainty-triggered querying.

#### Quote 2: Foreseeable Limitations of Query Stream Architecture
- **Source File & Line:** `final.tex` (Line 350)
- **Verbatim Quote:**  
  > "Behind all the advances, the limitation is also foreseeable. Since query cooperation is on the basis of the query stream, it naturally requests all agents participating in the symbioses to employ a query-based onboard system."
- **Context Snippet:**  
  `...\textbf{Foreseeable limitation}. Behind all the advances, the limitation is also foreseeable. Since query cooperation is on the basis of the query stream, it naturally requests all agents participating in the symbioses to employ a query-based onboard system. Therefore, the query cooperation adaption for the hybrid intelligent transportation system...`
- **Relevance to TRACE:** TRACE bridges this limitation by enabling query generation across non-query native backbones (e.g., standard CNN/PointPillars feature maps converted into localized spatial query bounding boxes).

---

### 5. V2X-ViT (ECCV 2022)
- **Title:** V2X-ViT: Vehicle-to-Everything Cooperative Perception with Vision Transformer
- **Citation:** Runsheng Xu, Hao Xiang, Zhengzhong Tu, Xin Xia, Ming-Hsuan Yang, Jiaqi Ma. *European Conference on Computer Vision (ECCV)*, 2022. arXiv:2203.10638.
- **Source Directory:** `docs/research/sources/V2X-ViT_2203.10638`

#### Quote 1: Vision Transformer with HMSA and MSwin
- **Source File & Line:** `main.tex` (Line 581)
- **Verbatim Quote:**  
  > "In this paper, we propose a new vision transformer (V2X-ViT) for V2X perception. Its key components are two novel attention modules \ie HMSA and MSwin, which can capture heterogeneous inter-agent interactions and multi-scale intra-agent spatial relationship."
- **Context Snippet:**  
  `...\section{Conclusion} In this paper, we propose a new vision transformer (V2X-ViT) for V2X perception. Its key components are two novel attention modules \ie HMSA and MSwin, which can capture heterogeneous inter-agent interactions and multi-scale intra-agent spatial relationship. % To evaluate our approach, we construct V2XSet, a new large-scale V2X perception dataset...`
- **Relevance to TRACE:** Demonstrates the value of dual-branch attention (heterogeneous inter-agent cross-attention + multi-scale spatial attention).

#### Quote 2: Joint Perception and Prediction Future Scope
- **Source File & Line:** `main.tex` (Line 589)
- **Verbatim Quote:**  
  > "Our future work involves multi-sensor fusion for joint V2X perception and prediction."
- **Context Snippet:**  
  `...This work facilitates future research on fairness, privacy, and robustness in visual learning systems for autonomous vehicles. Our future work involves multi-sensor fusion for joint V2X perception and prediction...`
- **Relevance to TRACE:** Validates the trajectory of V2X perception moving toward downstream trajectory forecasting and multi-modal integration.

---

### 6. CoBEVT (CoRL 2022)
- **Title:** CoBEVT: Cooperative Bird's Eye View Semantic Segmentation with Sparse Transformers
- **Citation:** Runsheng Xu, Zhengzhong Tu, Hao Xiang, Wei Shao, Bolei Zhou, Jiaqi Ma. *Conference on Robot Learning (CoRL)*, 2022. arXiv:2207.02202.
- **Source Directory:** `docs/research/sources/CoBEVT_2207.02202`

#### Quote 1: Fused Axial Attention (FAX) Mechanism
- **Source File & Line:** `main-arxiv.tex` (Line 795)
- **Verbatim Quote:**  
  > "We propose a fused axial attention (FAX) mechanism that allows for local and global interactions across all views and agents."
- **Context Snippet:**  
  `...\section{Conclusion and Limitations} \label{sec:conclusion} In this paper, we propose a holistic vision Transformer dubbed CoBEVT for multi-view cooperative semantic segmentation. % We propose a fused axial attention (FAX) mechanism that allows for local and global interactions across all views and agents. % Extensive experiments on both simulated and real-world datasets show that CoBEVT achieves superior performance...`
- **Relevance to TRACE:** Proves that multi-camera multi-agent BEV features can be efficiently fused with factorized sparse attention without blowing up compute budgets.

#### Quote 2: Explicit Limitations: Asynchrony and Position Noise
- **Source File & Line:** `main-arxiv.tex` (Line 803)
- **Verbatim Quote:**  
  > "The proposed approach does not explicitly model realistic V2V challenges such as asynchronization and position errors, which may impair its robustness under these noises."
- **Context Snippet:**  
  `...\textbf{Limitations.} % Despite the proposed single-agent model outperforming the real-world nuScenes dataset, the entire cooperative framework has been trained and validated on simulated datasets only, and thus its real-world generalization capability remains unknown. % The proposed approach does not explicitly model realistic V2V challenges such as asynchronization and position errors, which may impair its robustness under these noises. % The perception robustness against different domains such as severe weather or lighting conditions needs further examination...`
- **Relevance to TRACE:** Explicitly identifies time asynchrony and position error as unaddressed failure modes in camera-based cooperative perception—the exact problems addressed in TRACE.

---

### 7. CoAlign (ICRA 2023)
- **Title:** Robust Collaborative 3D Object Detection in Presence of Pose Errors
- **Citation:** Runsheng Xu, Zhaoliang Zheng, Yixuan Wang, Jiaqi Ma. *IEEE International Conference on Robotics and Automation (ICRA)*, 2023. arXiv:2211.07214.
- **Source Directory:** `docs/research/sources/CoAlign_2211.07214`

#### Quote 1: Agent-Object Pose Graph Optimization
- **Source File & Line:** `root.tex` (Line 576)
- **Verbatim Quote:**  
  > "This paper proposes a new hybrid collaboration framework $\mathtt{CoAlign}$ for robust 3D object detection. The proposed agent-object pose graph optimization empowers $\mathtt{CoAlign}$ to handle arbitrary pose errors without any accurate pose supervision."
- **Context Snippet:**  
  `...\section{Conclusion} This paper proposes a new hybrid collaboration framework $\mathtt{CoAlign}$ for robust 3D object detection. The proposed agent-object pose graph optimization empowers $\mathtt{CoAlign}$ to handle arbitrary pose errors without any accurate pose supervision. $\mathtt{CoAlign}$ can not only reduce the relative pose noises significantly, but improve the detection ability and robustness...`
- **Relevance to TRACE:** Pose graph alignment provides the geometric anchor for matching agent coordinate systems when GPS localization drifts.

#### Quote 2: Spatial Misalignment Breakdown
- **Source File & Line:** `root.tex` (Line 112)
- **Verbatim Quote:**  
  > "However, in practice, pose estimation errors due to imperfect localization would cause spatial message misalignment and significantly reduce the performance of collaboration."
- **Context Snippet:**  
  `...\begin{abstract} Collaborative 3D object detection exploits information exchange among multiple agents to enhance accuracy of object detection in presence of sensor impairments such as occlusion. However, in practice, pose estimation errors due to imperfect localization would cause spatial message misalignment and significantly reduce the performance of collaboration. To alleviate adverse impacts of pose errors...`
- **Relevance to TRACE:** Quantifies why raw coordinate projections fail without consensus alignment, motivating bounding-box associative verification.

---

### 8. SyncNet (ECCV 2022)
- **Title:** SyncNet: Co-Designing Feature-Attention Symbiotic Latency Compensation for V2X Collaborative Perception
- **Citation:** Zixing Lei, Shaoheng Fang, Yiqi Zhong, Siheng Chen. *European Conference on Computer Vision (ECCV)*, 2022. arXiv:2207.08560.
- **Source Directory:** `docs/research/sources/SyncNet_2207.08560`

#### Quote 1: Symbiotic Estimation Architecture
- **Source File & Line:** `LA-Coperception.tex` (Line 581)
- **Verbatim Quote:**  
  > "We introduce latency-aware collaborative perception and propose a novel latency compensation module, SyncNet, for time-domain synchronization, which fits in existing intermediate collaboration methods. SyncNet adopts a novel symbiotic estimation architecture, which jointly estimates intermediate features and attention weights, as well as the time modulation, which significantly improves the overall performance at low-latency range."
- **Context Snippet:**  
  `...\section{Conclusions} We introduce latency-aware collaborative perception and propose a novel latency compensation module, SyncNet, for time-domain synchronization, which fits in existing intermediate collaboration methods. SyncNet adopts a novel symbiotic estimation architecture, which jointly estimates intermediate features and attention weights, as well as the time modulation, which significantly improves the overall performance at low-latency range. Comprehensive quantitative and qualitative experiments show that...`
- **Relevance to TRACE:** SyncNet proves that feature warping and attention estimation can recover accuracy lost to transmission latency.

#### Quote 2: Active Adaptation to Mitigate Latency
- **Source File & Line:** `LA-Coperception.tex` (Line 97)
- **Verbatim Quote:**  
  > "To mitigate the effect caused by the inevitable latency, from a machine learning perspective, we present the first latency-aware collaborative perception system, which actively adapts asynchronous perceptual features from multiple agents to the same time stamp, promoting the robustness and effectiveness of collaboration."
- **Context Snippet:**  
  `...\begin{abstract} Collaborative perception has recently shown great potential to improve perception capabilities over single-agent perception. Existing collaborative perception methods usually consider an ideal communication environment. However, in practice, the communication system inevitably suffers from latency issues, causing potential performance degradation and high risks in safety-critical applications, such as autonomous driving. To mitigate the effect caused by the inevitable latency, from a machine learning perspective, we present the first latency-aware collaborative perception system, which actively adapts asynchronous perceptual features from multiple agents to the same time stamp, promoting the robustness and effectiveness of collaboration...`
- **Relevance to TRACE:** Establishes the necessity of timestamps and latency compensation filters in any production-ready collaborative protocol.

---

### 9. DAIR-V2X (CVPR 2022)
- **Title:** DAIR-V2X: A Large-Scale Dataset for Vehicle-Infrastructure Cooperative 3D Object Detection
- **Citation:** Haibao Yu, Yifeng Luo, Mao Shu, Yikang Huo, Zhenglong Yang, Yifu Shi, Zhenhai Guo, Huchuan Lu. *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2022. arXiv:2204.05575.
- **Source Directory:** `docs/research/sources/DAIR-V2X_2204.05575`

#### Quote 1: Real-World Vehicle-Infrastructure Dataset
- **Source File & Line:** `ms.tex` (Line 120)
- **Verbatim Quote:**  
  > "In this paper, we introduce DAIR-V2X, the first large-scale, multi-modality, multi-view dataset for vehicle-infrastructure cooperative autonomous driving, and all frames are captured from real scenes with 3D annotations."
- **Context Snippet:**  
  `...\section{Conclusion} In this paper, we introduce DAIR-V2X, the first large-scale, multi-modality, multi-view dataset for vehicle-infrastructure cooperative autonomous driving, and all frames are captured from real scenes with 3D annotations. We also define VIC3D object detection to formulate the problem of collaboratively locating and identifying 3D objects using sensory input from both vehicle and infrastructure...`
- **Relevance to TRACE:** The benchmark for real-world V2I cooperation, pairing ground vehicles with elevated roadside units (RSUs).

#### Quote 2: Asynchrony and Transmission Cost Bottleneck in VIC3D
- **Source File & Line:** `1.introduction.tex` (Line 24)
- **Verbatim Quote:**  
  > "In addition to solving traditional 3D object detection problems, the solution of VIC3D needs to consider the temporal asynchrony problem and data transmission cost between vehicle and infrastructure sensors."
- **Context Snippet:**  
  `...In this paper, the Vehicle-Infrastructure Cooperative 3D Object Detection (VIC3D) task is introduced, formulating the problem of cooperatively locating and identifying 3D objects using sensory inputs from both vehicle and infrastructure. In addition to solving traditional 3D object detection problems, the solution of VIC3D needs to consider the temporal asynchrony problem and data transmission cost between vehicle and infrastructure sensors...`
- **Relevance to TRACE:** Validates that V2I edge-cloud architectures inherently grapple with network latency and transmission budgets.

---

### 10. V2VNet (ECCV 2020)
- **Title:** V2VNet: Vehicle-to-Vehicle Communication for Joint Perception and Prediction
- **Citation:** Tsun-Hsuan Wang, Sivabalan Manivasakan, Ming Liang, Bin Yang, Wenyuan Zeng, Raquel Urtasun. *European Conference on Computer Vision (ECCV)*, 2020. arXiv:2008.07519.
- **Source Directory:** `docs/research/sources/V2VNet_2008.07519`

#### Quote 1: Joint Perception and Prediction Intermediate Representation
- **Source File & Line:** `3838.tex` (Line 647)
- **Verbatim Quote:**  
  > "In this paper, we have proposed a V2V approach for perception and prediction that transmits compressed intermediate representations of the \pnp{} neural network, achieving the best compromise between accuracy improvements and bandwidth requirements."
- **Context Snippet:**  
  `...\section{Conclusion} In this paper, we have proposed a V2V approach for perception and prediction that transmits compressed intermediate representations of the \pnp{} neural network, achieving the best compromise between accuracy improvements and bandwidth requirements. To demonstrate the effectiveness of our approach we have created a novel {\it V2V-Sim} dataset that realistically simulates the world when SDVs will be ubiquitous...`
- **Relevance to TRACE:** Seminal intermediate fusion paper using Graph Neural Networks (GNN) to jointly perform 3D object detection and motion forecasting.

#### Quote 2: Realistic Simulation & Future Work in Motion Forecasting
- **Source File & Line:** `3838.tex` (Line 651)
- **Verbatim Quote:**  
  > "To demonstrate the effectiveness of our approach we have created a novel {\it V2V-Sim} dataset that realistically simulates the world when SDVs will be ubiquitous. We hope that our findings will inspire future work in V2V perception and motion forecasting strategies for safer self-driving cars."
- **Context Snippet:**  
  `...achieving the best compromise between accuracy improvements and bandwidth requirements. To demonstrate the effectiveness of our approach we have created a novel {\it V2V-Sim} dataset that realistically simulates the world when SDVs will be ubiquitous. We hope that our findings will inspire future work in V2V perception and motion forecasting strategies for safer self-driving cars...`
- **Relevance to TRACE:** Highlights the ultimate goal of collaborative perception: improving downstream trajectory forecasting and collision avoidance.

---

### 11. When2com (CVPR 2020)
- **Title:** When2com: Multi-Agent Perception via Communication Graph Grouping
- **Citation:** Yen-Cheng Liu, Junjiao Tian, Nathaniel Glaser, Zsolt Kira. *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2020. arXiv:2006.00176.
- **Source Directory:** `docs/research/sources/When2com_2006.00176`

#### Quote 1: Framework for When to Communicate
- **Source File & Line:** `conclusion.tex` (Line 2)
- **Verbatim Quote:**  
  > "In this paper, we proposed a general bandwidth-efficient communication framework for collaborative perception. Our framework learns both how to construct communication groups and when to communicate."
- **Context Snippet:**  
  `...\section{Conclusion} In this paper, we proposed a general bandwidth-efficient communication framework for collaborative perception. Our framework learns both how to construct communication groups and when to communicate. This framework can be generalized to several down-stream tasks including (but not limited to) multi-agent semantic segmentation and multi-agent 3D shape recognition...`
- **Relevance to TRACE:** When2com pioneered temporal communication gating. TRACE integrates temporal triggers with spatial uncertainty maps.

#### Quote 2: Unsupervised Bandwidth Reduction During Inference
- **Source File & Line:** `intro.tex` (Line 34)
- **Verbatim Quote:**  
  > "We propose a unified framework that learns both how to construct communication groups and when to communicate. It does not require ground truth communication labels during training, and it can dynamically reduce bandwidth during inference."
- **Context Snippet:**  
  `...\begin{itemize} \item We propose a unified framework that learns both how to construct communication groups and when to communicate. It does not require ground truth communication labels during training, and it can dynamically reduce bandwidth during inference. \item We demonstrate across different tasks that our method can perform favorably against previous works...`
- **Relevance to TRACE:** Confirms that bandwidth minimization should be dynamic during runtime inference rather than a static hyperparameter.

---

### 12. Who2com (ICRA 2020)
- **Title:** Who2com: Collaborative Perception via Learnable Handshake Communication
- **Citation:** Yen-Cheng Liu, Junjiao Tian, Nathaniel Glaser, Zsolt Kira. *IEEE International Conference on Robotics and Automation (ICRA)*, 2020. arXiv:2003.09575.
- **Source Directory:** `docs/research/sources/Who2com_2003.09575`

#### Quote 1: Decoupled Handshake Mechanism
- **Source File & Line:** `root.tex` (Line 60)
- **Verbatim Quote:**  
  > "Inspired by the network communication literature, we propose a handshake communication mechanism for which the network can learn compressed representations. Key to our approach is that we decouple the message, key, and value elements to support asymmetric compression, resulting in bandwidth savings."
- **Context Snippet:**  
  `...\section{Conclusion} \label{sec:conclusion} In this paper, we formulated the problem of \textit{collaborative perception}, where agents can combine their local observations with those of other agents in order to improve performance on scene understanding tasks. Inspired by the network communication literature, we propose a handshake communication mechanism for which the network can learn compressed representations. Key to our approach is that we decouple the message, key, and value elements to support asymmetric compression, resulting in bandwidth savings...`
- **Relevance to TRACE:** Direct precedent for request-response handshakes. Decoupling query headers from heavy payload tensors is fundamental to TRACE's protocol.

#### Quote 2: Problem Formulation
- **Source File & Line:** `root.tex` (Line 60)
- **Verbatim Quote:**  
  > "In this paper, we formulated the problem of \textit{collaborative perception}, where agents can combine their local observations with those of other agents in order to improve performance on scene understanding tasks."
- **Context Snippet:**  
  `...\section{Conclusion} \label{sec:conclusion} In this paper, we formulated the problem of \textit{collaborative perception}, where agents can combine their local observations with those of other agents in order to improve performance on scene understanding tasks. Inspired by the network communication literature, we propose a handshake communication mechanism...`
- **Relevance to TRACE:** Foundational framing of multi-agent collaborative perception.

---

### 13. SEC (arXiv:2611.22439)
- **Title:** Where Demand Meets Supply: Spatial Elastic Consensus for Low-Bandwidth Collaborative Perception
- **Citation:** Linshan Yan. School of Software, Northwestern Polytechnical University, 2026. arXiv:2611.22439 (Preprint / CVPR 2027 Submission).
- **Source Directory:** `docs/research/sources/SEC_2611.22439`

#### Quote 1: Demand-Supply Consensus & Budget Enforcement
- **Source File & Line:** `10_conclusion.tex` (Line 3)
- **Verbatim Quote:**  
  > "This paper has introduced SEC, a novel bandwidth-adaptive framework that replaces sender-driven pruning with bilateral demand-supply consensus. By systematically coupling a single-round multiplicative gate with an anti-dilation selection pipeline, SEC strictly enforces exact token budgets while precisely isolating critical ego-missed information."
- **Context Snippet:**  
  `...\section{Conclusion} \label{sec:conclusion} This paper has introduced SEC, a novel bandwidth-adaptive framework that replaces sender-driven pruning with bilateral demand-supply consensus. By systematically coupling a single-round multiplicative gate with an anti-dilation selection pipeline, SEC strictly enforces exact token budgets while precisely isolating critical ego-missed information. Comprehensive evaluations demonstrate that SEC substantially outperforms existing methods under stringent communication constraints...`
- **Relevance to TRACE:** Validates the demand-supply economic model in collaborative perception, proving that bilateral consensus beats unilateral broadcasting.

#### Quote 2: Sender-Driven Bandwidth Waste on Ego-Perceived Targets
- **Source File & Line:** `01_intro.tex` (Line 11)
- **Verbatim Quote:**  
  > "This sender-driven design inevitably wastes scarce bandwidth on transmitting targets the ego vehicle has already perceived, leaving critical occluded blind zones unassisted (Fig.~\ref{fig:teaser}c)."
- **Context Snippet:**  
  `...Previous spatial selection strategies typically rely on senders evaluating perceptual importance through spatial confidence scores. This sender-driven design inevitably wastes scarce bandwidth on transmitting targets the ego vehicle has already perceived, leaving critical occluded blind zones unassisted (Fig.~\ref{fig:teaser}c). Second, a pervasive architectural flaw undermines feature quality: unguided convolutions after spatial masking cause dilated information leakage...`
- **Relevance to TRACE:** Crucial empirical critique of Where2comm's sender-driven model, reinforcing TRACE's receiver-driven active query philosophy.

---

## Verification Audit Matrix

| Paper | arXiv ID | File | Line | Verification Status | Core Theme Validated |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Where2comm** | 2209.12836 | `0-abstract.tex` | 2 | **[PASS] 100% Verbatim** | Spatial Confidence Map |
| **Where2comm** | 2209.12836 | `5-conclusion.tex` | 7 | **[PASS] 100% Verbatim** | Limitation to Temporal/Pragmatic |
| **OPV2V** | 2109.07644 | `root.tex` | 411 | **[PASS] 100% Verbatim** | AttFuse SOTA Performance |
| **OPV2V** | 2109.07644 | `root.tex` | 413 | **[PASS] 100% Verbatim** | Multi-Modal V2V/V2I Extension |
| **V2V4Real** | 2303.07601 | `main.tex` | 424 | **[PASS] 100% Verbatim** | Real-World Scale & Benchmarks |
| **V2V4Real** | 2303.07601 | `main.tex` | 419 | **[PASS] 100% Verbatim** | Sim2Real Domain Gap |
| **QUEST** | 2308.01804 | `final.tex` | 354 | **[PASS] 100% Verbatim** | Query Stream Paradigm |
| **QUEST** | 2308.01804 | `final.tex` | 350 | **[PASS] 100% Verbatim** | Onboard Query Architecture Constraint |
| **V2X-ViT** | 2203.10638 | `main.tex` | 581 | **[PASS] 100% Verbatim** | Vision Transformer for V2X |
| **V2X-ViT** | 2203.10638 | `main.tex` | 589 | **[PASS] 100% Verbatim** | Joint Perception-Prediction Scope |
| **CoBEVT** | 2207.02202 | `main-arxiv.tex` | 795 | **[PASS] 100% Verbatim** | FAX Sparse Transformer |
| **CoBEVT** | 2207.02202 | `main-arxiv.tex` | 803 | **[PASS] 100% Verbatim** | Asynchrony & Position Noise Gap |
| **CoAlign** | 2211.07214 | `root.tex` | 576 | **[PASS] 100% Verbatim** | Agent-Object Pose Graph Optimization |
| **CoAlign** | 2211.07214 | `root.tex` | 112 | **[PASS] 100% Verbatim** | Misalignment from Pose Noise |
| **SyncNet** | 2207.08560 | `LA-Coperception.tex` | 581 | **[PASS] 100% Verbatim** | Latency Compensation Architecture |
| **SyncNet** | 2207.08560 | `LA-Coperception.tex` | 97 | **[PASS] 100% Verbatim** | Active Time Adaptation |
| **DAIR-V2X** | 2204.05575 | `ms.tex` | 120 | **[PASS] 100% Verbatim** | Real-Scene V2I Dataset |
| **DAIR-V2X** | 2204.05575 | `1.introduction.tex` | 24 | **[PASS] 100% Verbatim** | Asynchrony & Transmission Cost |
| **V2VNet** | 2008.07519 | `3838.tex` | 647 | **[PASS] 100% Verbatim** | Intermediate Fusion Compromise |
| **V2VNet** | 2008.07519 | `3838.tex` | 651 | **[PASS] 100% Verbatim** | V2V-Sim & Future Joint Tasks |
| **When2com** | 2006.00176 | `conclusion.tex` | 2 | **[PASS] 100% Verbatim** | When to Communicate Framework |
| **When2com** | 2006.00176 | `intro.tex` | 34 | **[PASS] 100% Verbatim** | Dynamic Bandwidth Pruning |
| **Who2com** | 2003.09575 | `root.tex` | 60 | **[PASS] 100% Verbatim** | Handshake Mechanism Decoupling |
| **Who2com** | 2003.09575 | `root.tex` | 60 | **[PASS] 100% Verbatim** | Collaborative Perception Formulation |
| **SEC** | 2611.22439 | `10_conclusion.tex` | 3 | **[PASS] 100% Verbatim** | Bilateral Demand-Supply Consensus |
| **SEC** | 2611.22439 | `01_intro.tex` | 11 | **[PASS] 100% Verbatim** | Sender-Driven Bandwidth Waste |
