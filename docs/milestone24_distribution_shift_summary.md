# Milestone 24D — Distribution Shift Summary

## Fraud prevalence

- Train: 0.060876%
- Validation: 0.042439%
- Test: 0.319481%

## Shift counts

- High-shift rows: 0
- Moderate-shift rows: 0

## Highest-shift features

- `amount` (train_vs_test) — level=low, PSI=0.0258, KS=0.0527, SMD=-0.0887
- `receiver_avg_amount_prior` (train_vs_test) — level=low, PSI=0.0211, KS=0.0420, SMD=-0.0996
- `receiver_avg_amount_prior` (train_vs_validation) — level=low, PSI=0.0176, KS=0.0343, SMD=-0.0252
- `receiver_prior_txn_count` (train_vs_validation) — level=low, PSI=0.0143, KS=0.0440, SMD=0.1154
- `receiver_in_degree_prior` (train_vs_validation) — level=low, PSI=0.0143, KS=0.0440, SMD=0.1154
- `receiver_high_risk_txn_count_prior` (train_vs_validation) — level=low, PSI=0.0133, KS=0.0419, SMD=0.1141
- `oldbalanceOrg` (train_vs_test) — level=low, PSI=0.0129, KS=0.0403, SMD=-0.0271
- `receiver_prior_txn_count` (train_vs_test) — level=low, PSI=0.0121, KS=0.0320, SMD=0.0833
- `receiver_in_degree_prior` (train_vs_test) — level=low, PSI=0.0121, KS=0.0320, SMD=0.0833
- `receiver_high_risk_txn_count_prior` (train_vs_test) — level=low, PSI=0.0101, KS=0.0300, SMD=0.0830
- `amount` (train_vs_validation) — level=low, PSI=0.0087, KS=0.0423, SMD=0.0281
- `funnel_alert_v2` (train_vs_validation) — level=low, PSI=0.0076, KS=0.0414, SMD=0.0874
- `possible_mule_receiver_v2` (train_vs_validation) — level=low, PSI=0.0076, KS=0.0414, SMD=0.0874
- `receiver_prior_volume` (train_vs_validation) — level=low, PSI=0.0050, KS=0.0348, SMD=0.0401
- `receiver_total_amount_prior` (train_vs_validation) — level=low, PSI=0.0050, KS=0.0348, SMD=0.0401

## Interpretation rules

- PSI below 0.10: low shift
- PSI from 0.10 to below 0.25: moderate shift
- PSI at or above 0.25: high shift
- KS and standardized mean difference are used as supporting diagnostics

Statistical significance alone is not enough on a dataset this large; effect size and operational relevance must drive decisions.
