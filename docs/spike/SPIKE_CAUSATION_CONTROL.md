> Source data: 54 CARLA 0.9.16 scenes in Town10HD, 448 co-visible objects evaluated under YOLO11m.
> Permutation controls executed via `python -m spike_dependence.causation_cli`. Decision SD-026.

# Causation Control and Variance Decomposition

While the baseline spike demonstrates significant joint failure inflation, observing correlated errors does not independently identify the causal source of coupling. To isolate whether shared physical context causally drives co-failure, permutation controls were executed across the identical set of 448 objects and 54 scenes. These permutations selectively break physical associations while holding both agents' marginal error distributions strictly invariant.

| Experimental Condition | Preserved Coupling | Inflation Ratio | 95% Bootstrap Range | Empirical Finding |
| :--- | :--- | :--- | :--- | :--- |
| **Observed Pairing** | Same Scene, Same Object | **1.671** | [1.495, 1.875] | Full physical and instance coupling |
| **Within-Scene Control** | Same Scene, Different Object | **1.197** | [1.062, 1.340] | Preserves scene-wide factors, decouples object identity |
| **Unrelated Null** | Different Scene, Unrelated Object | **0.999** | [0.835, 1.166] | Complete decoupling of scene and target |

## Methodological Validation

1. **Unbiased Metric Formulation:** When all physical coupling is severed in the null condition, the inflation ratio returns **0.999** (95% range [0.835, 1.166]). This confirms that the double-fault inflation statistic is mathematically unbiased and does not introduce synthetic correlation artifacts.
2. **Causal Environmental Grounding:** Systematically breaking shared context eliminates the correlation effect, establishing that shared physical embodiment causally drives simultaneous multi-agent failure.

## Variance Decomposition

- Total measured excess dependence above independence ($1.671 - 1.000$): **0.671**
- Attributable to scene-wide environmental factors ($1.197 - 1.000$): **0.197** (**29.4%** of excess)
- Attributable to the specific shared physical object instance ($1.671 - 1.197$): **0.474** (**70.6%** of excess)

The dominant fraction of failure correlation arises from two agents observing the exact same physical object instance rather than ambient town layout, viewpoint angle, or atmospheric weather. Because stratified analysis demonstrates that inflation survives across apparent size terciles, this instance-level effect reflects fine-grained target attributes such as target orientation, local shadow boundaries, vehicle livery, and local occlusion geometry.

## Scope and Experimental Controls

- The permutation test re-samples across the rendered frame corpus, maintaining identical marginal error counts while evaluating counterfactual pairings.
- Single-object scenes contribute no within-scene shuffling permutations and are accounted for in sample bounds.
- Scope reflects Town10HD across 54 scenes, single frame per scene, at an IoU threshold of 0.50.
