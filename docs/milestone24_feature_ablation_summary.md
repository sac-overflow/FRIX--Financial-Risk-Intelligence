# Milestone 24F — Feature-Family Ablation

All experiments use the same XGBoost configuration, chronological training period, and validation period.

## Results

| Feature set | Features | PR-AUC | ROC-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| base_only | 9 | 0.380977 | 0.992260 | 0.630435 | 0.325843 | 0.429630 |
| base_plus_temporal | 13 | 0.380598 | 0.989058 | 0.533333 | 0.359551 | 0.429530 |
| base_plus_graph | 16 | 0.375685 | 0.987958 | 0.521739 | 0.404494 | 0.455696 |
| full_core | 20 | 0.371645 | 0.983042 | 0.568966 | 0.370787 | 0.448980 |

## Incremental PR-AUC versus base

- `base_only`: +0.000000
- `base_plus_temporal`: -0.000379
- `base_plus_graph`: -0.005292
- `full_core`: -0.009332

## Interpretation

A positive lift indicates that the added feature family improves ranking performance over current-transaction features alone. Final conclusions still require forward-chaining validation.
