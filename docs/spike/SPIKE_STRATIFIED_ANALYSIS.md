> Source data: 54 CARLA 0.9.16 scenes in Town10HD, 448 co-visible objects evaluated under YOLO11m.
> Generated via `python -m spike_dependence.stratify`. Decision SD-021.

# Stratified Analysis and Confound Evaluation

To evaluate whether the observed dependence inflation ratio of 1.671 represents an artifact of shared object difficulty or specific scenario attributes, the dataset was stratified across environmental knobs and apparent object size.

## Stratification by Apparent Object Size (The Confound Test)

Because both agents observe the identical physical object, objects that are distant or small in the visual field present greater intrinsic difficulty. If shared difficulty accounted for the double-fault inflation, conditioning on apparent bounding-box pixel area would reduce stratum ratios toward 1.0. The data demonstrate that inflation persists across all size terciles:

| Stratum | Pixel Area Range ($px^2$) | Object Count ($n$) | Inflation Ratio | 95% Bootstrap CI |
| :--- | :--- | :--- | :--- | :--- |
| **Small** | 102 – 1,736 | 149 | **1.324** | [1.183, 1.492] |
| **Medium** | 1,782 – 3,888 | 149 | **1.725** | [1.164, 2.390] |
| **Large** | 3,889 – 38,346 | 150 | **1.782** | [1.379, 2.251] |

Because the lower confidence bound in every size stratum sits strictly above 1.0, the headline correlation cannot be explained as a small-object detection artifact.

## Stratification by Viewpoint Overlap

| Stratum | Object Count ($n$) | Inflation Ratio | 95% Bootstrap CI |
| :--- | :--- | :--- | :--- |
| **High Overlap** | 171 | **1.985** | [1.682, 2.370] |
| **Medium Overlap** | 146 | **1.377** | [1.038, 1.751] |
| **Low Overlap** | 131 | **1.576** | [1.311, 1.919] |

While the highest viewpoint overlap produces the largest point estimate (1.985), the inflation ratio does not exhibit strict monotonicity across medium and low overlap strata. Viewpoint overlap modulates correlation but does not act as an isolated on/off switch for dependence.

## Stratification by Static Occlusion

| Stratum | Object Count ($n$) | Inflation Ratio | 95% Bootstrap CI |
| :--- | :--- | :--- | :--- |
| **Occluder Present** | 238 | **1.453** | [1.240, 1.699] |
| **Occluder Absent** | 210 | **1.982** | [1.691, 2.353] |

Both conditions maintain statistically significant inflation. Unoccluded targets exhibit higher correlation, reflecting the fact that high-confidence visible objects share consistent salient visual features across camera viewpoints.

## Stratification by Ambient Weather and Lighting

| Stratum | Object Count ($n$) | Inflation Ratio | 95% Bootstrap CI |
| :--- | :--- | :--- | :--- |
| **ClearNoon** | 155 | **1.761** | [1.242, 2.399] |
| **CloudySunset** | 143 | **1.589** | [1.370, 1.863] |
| **WetNoon** | 150 | **1.550** | [1.306, 1.850] |

Error correlation remains robust across varied atmospheric conditions, establishing that dependence persists across diverse lighting environments rather than degrading only in edge-case weather.
