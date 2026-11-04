> Source data: 54 CARLA 0.9.16 scenes in Town10HD, 448 co-visible objects.
> Detectors: Ultralytics YOLO11m and RT-DETR-L evaluated over identical 108 frames via `python -m spike_dependence.contrast`. Decisions SD-022 through SD-024.

# Contrast Condition: Evaluating Detector Architecture Homogeneity vs. Heterogeneity

To evaluate whether shared neural network weights explain inter-agent error correlation, a second detector of a fundamentally different architecture—the real-time vision transformer RT-DETR-L—was evaluated over the identical 108 rendered CARLA frames.

Because detection accuracy differs between YOLO11m and RT-DETR-L, comparison across homogeneous and heterogeneous configurations evaluates Pearson's $\phi$ correlation coefficient and odds ratios rather than the raw inflation ratio.

| Condition | Architecture Pairing | $\phi$ Correlation | Odds Ratio | $p_A$ | $p_B$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Homogeneous (YOLO11m / YOLO11m)** | Dual CNN | 0.374 | 5.129 | 0.368 | 0.348 |
| **Homogeneous (RT-DETR-L / RT-DETR-L)** | Dual Transformer | 0.379 | 6.605 | 0.234 | 0.214 |
| **Heterogeneous (YOLO11m / RT-DETR-L)** | CNN + Transformer | 0.278 | 3.889 | 0.368 | 0.214 |
| **Heterogeneous (RT-DETR-L / YOLO11m)** | Transformer + CNN | 0.292 | 4.003 | 0.234 | 0.348 |

## Paired Bootstrap Analysis on Architecture Contrast

- **Mean Homogeneous Association ($\phi$):** **0.3766**
- **Mean Heterogeneous Association ($\phi$):** **0.2852**
- **Paired Association Difference ($\Delta \phi$):** **+0.0915**, 95% CI **[+0.0466, +0.1401]**

## Empirical Findings

1. **Shared Model Weights Contribute to Co-Failure:** Homogeneous pairs exhibit higher error association than heterogeneous pairs. Because the confidence interval on the paired difference strictly excludes zero, deploying identical model weights measurably increases joint failure rates.
2. **Model Diversity Fails to Restore Independence:** Heterogeneous pairs running distinct architectures (CNN vs. vision transformer) remain strongly correlated ($\phi = 0.2852$, odds ratio $\approx 4.0$). Shared weights are therefore a contributing channel rather than the primary driver of failure correlation; the shared physical embodiment dominates model-induced correlation.

This empirical finding broadens the research scope: the independence assumption fails even across heterogeneous agent teams, refuting the common assumption that architectural diversity alone guarantees uncorrelated perception errors.
