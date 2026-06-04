# Day 1 - Fraud EDA and Rule Risk Score Summary

## Dataset

Used PaySim transaction dataset with 1,048,575 rows and 11 original columns.

## Key Findings

- Fraud transactions are highly imbalanced.
- Total fraud cases: 1,142
- Fraud percentage: 0.10891%
- Fraud occurs only in TRANSFER and CASH_OUT transactions.
- TRANSFER has the highest fraud rate among transaction types.
- Fraud transactions usually have much higher transaction amounts than non-fraud transactions.
- 99.21% of fraud transactions emptied the sender account.
- Destination balance error is much higher for fraud transactions.

## Features Created

- origin_balance_error
- dest_balance_error
- is_high_risk_type
- sender_txn_count
- receiver_txn_count
- sender_emptied_account
- is_large_amount
- risk_score_v1
- rule_alert_v1

## Rule Risk Score v1

The first FRIX rule-based risk score used:
- high-risk transaction type
- large transaction amount
- sender account emptied
- destination balance mismatch
- receiver transaction frequency

## Result

Rule Recall: 99.91%  
Rule Precision: 0.27%

## Conclusion

The rule system catches almost all fraud cases, but it creates many false positives. This validates the need for a machine learning model in Day 2 to improve precision while preserving high recall.