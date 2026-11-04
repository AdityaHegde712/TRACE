> Source data: 54 CARLA 0.9.16 scenes in Town10HD, two viewpoints each, rendered via `python -m spike_dependence.render_scenes --scenes 54`.
> Detector: Ultralytics YOLO11m, IoU 0.50, confidence 0.25, homogeneous weights on both agents. Decisions SD-020 and SD-021.

# Dependence Spike Result: Baseline Empirical Evidence

**Outcome 1: Statistically Significant Correlated Failure**

Empirical evaluation demonstrates that co-located perceptual agents double-fault simultaneously on identical objects substantially more often than statistical independence allows. The empirical independence assumption is rejected; proceed to M1 design phase.

## Primary Metric: Dependence Inflation Ratio

- **Dependence Inflation Ratio:** **1.671**
- **95% Bootstrap Confidence Interval:** **[1.500, 1.870]** (5,000 resamples)
- **Observed Joint Error Rate (Double-Fault $p_{11}$):** 0.2143
- **Rate Predicted Under Independence ($p_A \cdot p_B$):** 0.1282

A dependence inflation ratio of 1.0 represents statistical independence. Because the entire 95% bootstrap confidence interval sits strictly above 1.0, the observed joint error cannot be explained by independent random sensor or detector noise.

## Sample Scope & Contingency Distribution

- Total Co-Visible Objects Evaluated: 448
- Total Rendered Frames: 108 (54 scenes $\times$ 2 viewpoints)
- Marginal Error Rate, Agent A ($p_A$): 0.3683 (165 misses)
- Marginal Error Rate, Agent B ($p_B$): 0.3482 (156 misses)

| Contingency Cell | Observed Count | Expected Count Under Independence |
| :--- | :--- | :--- |
| **Both agents wrong ($e_A = 1, e_B = 1$)** | **96** | 57.4 |
| Only Agent A wrong ($e_A = 1, e_B = 0$) | 69 | 107.6 |
| Only Agent B wrong ($e_A = 0, e_B = 1$) | 60 | 98.6 |
| Neither agent wrong ($e_A = 0, e_B = 0$) | 223 | 184.4 |

## Provenance and Methodological Guarantees

The evaluation adopts the pairwise double-fault measure formulated by Kuncheva and Whitaker (2003), normalized against the joint expectation under marginal independence.

Only objects verified as co-visible to both viewpoints in simulator ground truth are evaluated. Simulator ground truth was strictly isolated for offline scoring and never provided to the detection or inference pipeline, enforcing architectural directive AD-001.
