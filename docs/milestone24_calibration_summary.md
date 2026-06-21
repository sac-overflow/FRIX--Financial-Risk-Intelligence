# Milestone 24K — Temporal Probability Calibration

Calibration models were fitted on forward-validation folds 1 and 2 and evaluated on the later fold 3.

The latest 20% holdout was not used to choose a calibrator.

## Calibration comparison

| Feature set | Method | Brier | Log loss | ECE | Slope | Intercept |
|---|---|---:|---:|---:|---:|---:|
| base_only | isotonic | 0.00032305 | 0.00187492 | 0.00075350 | 1.323924 | -0.211156 |
| base_only | sigmoid | 0.00035522 | 0.00191042 | 0.00079430 | 1.335698 | -0.330814 |
| base_only | uncalibrated | 0.00324067 | 0.01217935 | 0.00597762 | 0.671728 | -4.522478 |
| base_plus_graph | isotonic | 0.00033220 | 0.00198671 | 0.00073213 | 1.281130 | -0.227629 |
| base_plus_graph | sigmoid | 0.00036560 | 0.00207323 | 0.00081835 | 1.313088 | -0.341102 |
| base_plus_graph | uncalibrated | 0.00541130 | 0.01903985 | 0.01036315 | 0.720234 | -4.806297 |

## Selected calibrators

- `base_only`: `isotonic` (Brier 0.00032305, log loss 0.00187492)
- `base_plus_graph`: `isotonic` (Brier 0.00033220, log loss 0.00198671)

## Interpretation

Lower Brier score, log loss, and ECE indicate better probability quality. PR-AUC is unchanged by monotonic calibration and remains a ranking metric rather than a probability-quality metric.
