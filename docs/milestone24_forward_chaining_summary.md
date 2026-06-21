# Milestone 24G — Forward-Chaining Validation

The latest 20% of the dataset was excluded. Each fold trains on an expanding historical window and validates on the immediately following period.

## Fold results

| Fold | Feature set | Train fraud | Validation fraud | PR-AUC | ROC-AUC | Precision | Recall | F1 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | base_only | 235 | 148 | 0.397015 | 0.989016 | 0.582278 | 0.310811 | 0.405286 |
| 1 | base_plus_graph | 235 | 148 | 0.430891 | 0.988018 | 0.628205 | 0.331081 | 0.433628 |
| 2 | base_only | 383 | 47 | 0.378232 | 0.988966 | 0.933333 | 0.297872 | 0.451613 |
| 2 | base_plus_graph | 383 | 47 | 0.396130 | 0.983748 | 0.600000 | 0.382979 | 0.467532 |
| 3 | base_only | 430 | 42 | 0.374370 | 0.995504 | 0.434783 | 0.476190 | 0.454545 |
| 3 | base_plus_graph | 430 | 42 | 0.363321 | 0.992472 | 0.472222 | 0.404762 | 0.435897 |

## Stability summary

| Feature set | Mean PR-AUC | Std PR-AUC | Min PR-AUC | Mean F1 | Std F1 |
|---|---:|---:|---:|---:|---:|
| base_plus_graph | 0.396781 | 0.033789 | 0.363321 | 0.445686 | 0.018954 |
| base_only | 0.383205 | 0.012114 | 0.374370 | 0.437148 | 0.027632 |

## Decision rule

Prefer the feature set with stronger average PR-AUC, lower fold-to-fold variance, and acceptable recall. A single strong fold is not sufficient.
