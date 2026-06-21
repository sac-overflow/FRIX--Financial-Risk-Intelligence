# Milestone 24I — Validation-Only Threshold Tuning

Thresholds were selected using pooled out-of-fold predictions from the three forward-chaining development folds.

The latest 20% of the dataset was not used.

## Selected operating profiles

| Feature set | Profile | Threshold | Precision | Recall | F1 | Alerts | TP | FP | FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base_only | max_f1 | 0.987806 | 0.463687 | 0.350211 | 0.399038 | 179 | 83 | 96 | 154 |
| base_only | recall_at_least_0.50 | 0.543219 | 0.123732 | 0.514768 | 0.199509 | 986 | 122 | 864 | 115 |
| base_only | recall_at_least_0.70 | 0.120824 | 0.056968 | 0.708861 | 0.105461 | 2949 | 168 | 2781 | 69 |
| base_plus_graph | max_f1 | 0.991908 | 0.693069 | 0.295359 | 0.414201 | 101 | 70 | 31 | 167 |
| base_plus_graph | recall_at_least_0.50 | 0.862182 | 0.185647 | 0.502110 | 0.271071 | 641 | 119 | 522 | 118 |
| base_plus_graph | recall_at_least_0.70 | 0.304288 | 0.057539 | 0.700422 | 0.106342 | 2885 | 166 | 2719 | 71 |

## Governance

- `max_f1` is the balanced development operating point.
- Recall-target profiles trade more alerts for fewer missed frauds.
- Thresholds remain provisional until calibration and final evaluation.
- No threshold was selected using the excluded latest 20%.
