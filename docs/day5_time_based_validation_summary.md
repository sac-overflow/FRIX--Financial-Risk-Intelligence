\# Day 5 - Time-Based Validation Summary



\## Goal



Day 5 focused on making FRIX validation more production-realistic by using a time-based split instead of a random train-test split.



The purpose was to simulate real fraud detection where the model is trained on older transactions and tested on future transactions.



\## Time-Based Split



The dataset step range was:



\- Minimum step: 1

\- Maximum step: 95

\- Unique steps: 95



The split used was:



\- Train: step 1 to 80

\- Test: step 81 to 95



\## Dataset Split



\- Train shape: 1,030,645 rows

\- Test shape: 17,930 rows

\- Train fraud count: 972

\- Test fraud count: 170



Fraud rate:



\- Train fraud rate: 0.0943%

\- Test fraud rate: 0.9481%



The test period had a much higher fraud concentration, making this validation more realistic and harder.



\## Full Feature Model



A Random Forest model was trained using the Day 1 engineered feature set.



\### Result



Confusion Matrix:



\- True Negatives: 17,760

\- False Positives: 0

\- False Negatives: 0

\- True Positives: 170



Metrics:



\- Fraud Precision: 1.00

\- Fraud Recall: 1.00

\- ROC-AUC: 1.00

\- PR-AUC: 1.00



\## Strict Feature Model



Because the full model performed perfectly, a stricter model was trained by removing the strongest rule-derived and balance-error features.



Removed features included:



\- origin\_balance\_error

\- dest\_balance\_error

\- risk\_score\_v1

\- sender\_emptied\_account

\- is\_large\_amount



The strict model used a reduced feature set:



\- amount

\- oldbalanceOrg

\- newbalanceOrig

\- oldbalanceDest

\- newbalanceDest

\- is\_high\_risk\_type

\- sender\_txn\_count

\- receiver\_txn\_count



\### Result



Confusion Matrix:



\- True Negatives: 17,577

\- False Positives: 183

\- False Negatives: 0

\- True Positives: 170



Metrics:



\- Fraud Precision: 0.48

\- Fraud Recall: 1.00

\- ROC-AUC: 0.999413

\- PR-AUC: 0.949704



\## Key Finding



The full model achieved perfect performance, but the strict test showed that the strongest engineered rule features were carrying much of the precision.



After removing those features:



\- Fraud recall stayed at 1.00

\- Fraud precision dropped from 1.00 to 0.48

\- False positives increased from 0 to 183

\- PR-AUC dropped from 1.00 to 0.949704



This confirms that the synthetic dataset contains very clean fraud patterns and that the engineered balance/rule features are extremely powerful.



\## Technical Interpretation



The perfect full-feature result should not be presented as proof of a flawless real-world fraud model.



A more honest interpretation is:



The model performs extremely well on this synthetic dataset, but stricter validation shows that some performance comes from strong engineered features and clean synthetic fraud behavior.



\## Conclusion



Day 5 made FRIX more production-realistic by introducing time-based validation and a stricter feature test.



This improved the credibility of the project by showing not only model performance, but also awareness of leakage risk, synthetic data limitations, and realistic fraud model evaluation.

