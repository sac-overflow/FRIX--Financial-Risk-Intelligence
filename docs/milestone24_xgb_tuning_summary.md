# Milestone 24H — XGBoost Hyperparameter Tuning

Tuning used only three forward-chaining development folds. The latest 20% was excluded.

Selection score: `mean PR-AUC - 0.25 × PR-AUC standard deviation`

| Feature set | Mean PR-AUC | Std PR-AUC | Stability | Depth | Learning rate | Lambda |
|---|---:|---:|---:|---:|---:|---:|
| base_only | 0.387833 | 0.014741 | 0.384148 | 8 | 0.05 | 5.0 |
| base_plus_graph | 0.398258 | 0.017933 | 0.393775 | 6 | 0.05 | 1.0 |

No final-holdout rows or classification thresholds were used during tuning.
