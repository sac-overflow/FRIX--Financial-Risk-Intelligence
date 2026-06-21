# Milestone 24L — FRIX Champion Selection

## Frozen internal development decision

### Champion

- **Model:** `frix_xgboost_base_v1`
- **Feature set:** `base_only`
- **Role:** Primary fraud ranking and balanced review
- **Holdout PR-AUC:** 0.781108
- **95% CI:** [0.751493, 0.808840]
- **Precision:** 0.880383
- **Recall:** 0.549254
- **F1:** 0.676471
- **Frozen raw threshold:** 0.987806
- **Probability calibrator:** `isotonic`

### Challenger

- **Model:** `frix_xgboost_graph_v1`
- **Feature set:** `base_plus_graph`
- **Role:** Graph-aware specialist and investigation routing
- **Holdout PR-AUC:** 0.733011
- **95% CI:** [0.699087, 0.764160]
- **Balanced threshold:** 0.991908
- **Investigation threshold:** 0.862182
- **Probability calibrator:** `isotonic`

## Routing policy

1. Use the base-only champion by default.
2. Use the graph challenger when meaningful prior graph history exists.
3. Treat strong disagreement as a reason for manual review or additional checks.
4. Do not describe raw XGBoost scores as literal probabilities; use calibrated outputs.

## Limitation

This is the frozen **internal development selection** for the PaySim experiment. External or newly collected data is still required before making a production-performance claim.
