# Milestone 24J — Holdout Evaluation with Bootstrap Confidence Intervals

Models were retrained on the first 80% of transactions using frozen feature sets and frozen hyperparameters. Thresholds were taken from forward-chaining development validation.

The latest 20% was used only for this evaluation step.

## Results

| Feature set | Profile | PR-AUC | PR-AUC 95% CI | Precision | Recall | F1 | Alerts | TP | FP | FN |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| base_only | max_f1 | 0.781108 | [0.751493, 0.808840] | 0.880383 | 0.549254 | 0.676471 | 418 | 368 | 50 | 302 |
| base_only | recall_at_least_0.50 | 0.781108 | [0.751493, 0.808840] | 0.434150 | 0.846269 | 0.573887 | 1306 | 567 | 739 | 103 |
| base_only | recall_at_least_0.70 | 0.781108 | [0.751493, 0.808840] | 0.216115 | 0.944776 | 0.351764 | 2929 | 633 | 2296 | 37 |
| base_plus_graph | max_f1 | 0.733011 | [0.699087, 0.764160] | 0.932692 | 0.434328 | 0.592668 | 312 | 291 | 21 | 379 |
| base_plus_graph | recall_at_least_0.50 | 0.733011 | [0.699087, 0.764160] | 0.549721 | 0.734328 | 0.628754 | 895 | 492 | 403 | 178 |
| base_plus_graph | recall_at_least_0.70 | 0.733011 | [0.699087, 0.764160] | 0.200067 | 0.886567 | 0.326463 | 2969 | 594 | 2375 | 76 |

## Important note

This is the final internal temporal holdout for the current PaySim experiment. Because earlier exploratory experiments had already inspected this late period, external or newly collected data will still be required for a truly untouched production claim.
