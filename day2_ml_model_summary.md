# Day 2 - ML Model Training Summary

## Goal

Day 2 focused on training machine learning models to improve fraud detection beyond the Day 1 rule-based risk score.

## Dataset

Used the Day 1 feature-enhanced dataset:

- frix_features_day1.csv
- 1,048,575 transactions
- 13 selected numeric and engineered features
- Target label: isFraud

## Features Used

- amount
- oldbalanceOrg
- newbalanceOrig
- oldbalanceDest
- newbalanceDest
- origin_balance_error
- dest_balance_error
- is_high_risk_type
- sender_txn_count
- receiver_txn_count
- sender_emptied_account
- is_large_amount
- risk_score_v1

## Models Trained

### Logistic Regression

Used as a baseline model with class_weight="balanced".

Results:

- Fraud Precision: 0.01
- Fraud Recall: 0.97
- False Positives: 14,873
- False Negatives: 6
- ROC-AUC: 0.988367
- PR-AUC: 0.429859

### Random Forest

Used as the stronger tree-based model with class_weight="balanced".

Results:

- Fraud Precision: 0.77
- Fraud Recall: 0.98
- False Positives: 67
- False Negatives: 5
- ROC-AUC: 0.997101
- PR-AUC: 0.984208

## Key Finding

Random Forest significantly reduced false positives while maintaining very high fraud recall.

Compared to Logistic Regression:

- False positives reduced from 14,873 to 67
- Fraud recall improved from 0.97 to 0.98
- PR-AUC improved from 0.429859 to 0.984208

## Feature Importance

Top Random Forest features:

1. origin_balance_error
2. risk_score_v1
3. is_high_risk_type
4. oldbalanceOrg
5. sender_emptied_account

## Conclusion

The Random Forest model is currently the best Day 2 model. It shows that FRIX can move beyond rule-based fraud detection by learning stronger fraud patterns from engineered transaction features.