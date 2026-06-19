# FRIX Feature Availability Registry

This registry classifies every feature by prediction-time availability, leakage risk, and strict pre-transaction eligibility.

## Status meanings
- **yes** — approved for strict pre-transaction use
- **no** — forbidden
- **review** — causally constructed but requires timestamp-granularity review, ablation, or policy-score review

## Governance
No feature may enter training, validation, testing, calibration, or inference unless it appears in this registry and its status is approved.
