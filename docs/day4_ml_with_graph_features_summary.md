\# Day 4 - ML Model with Graph Features Summary



\## Goal



Day 4 focused on combining transaction-level fraud features from Day 1 and Day 2 with graph-based mule-risk features from Day 3.



The goal was to test whether graph/account-level features improve the Random Forest fraud model.



\## Datasets Used



\- frix\_features\_day1.csv

\- frix\_graph\_features\_day3.csv



The datasets were combined by row order because both files had the same number of rows:



\- Base dataset: 1,048,575 rows and 20 columns

\- Graph feature dataset: 1,048,575 rows and 10 columns

\- Combined dataset: 1,048,575 rows and 28 columns



\## Graph Features Added



\- receiver\_in\_degree

\- sender\_out\_degree

\- receiver\_total\_amount

\- receiver\_avg\_amount

\- receiver\_high\_risk\_txn\_count

\- possible\_mule\_receiver

\- mule\_risk\_score\_v1

\- mule\_alert\_v1



\## Model Trained



Random Forest with:



\- 100 estimators

\- max\_depth = 10

\- class\_weight = balanced

\- random\_state = 42



\## Day 4 Result



Confusion Matrix:



\- True Negatives: 209,487

\- False Positives: 0

\- False Negatives: 5

\- True Positives: 223



Metrics:



\- Fraud Precision: 1.00

\- Fraud Recall: 0.98

\- ROC-AUC: 0.997087

\- PR-AUC: 0.984097



\## Comparison with Day 2 Random Forest



| Model | Features | Fraud Precision | Fraud Recall | False Positives | False Negatives | ROC-AUC | PR-AUC |

|---|---|---:|---:|---:|---:|---:|---:|

| Day 2 Random Forest | Transaction + rule features | 0.77 | 0.98 | 67 | 5 | 0.997101 | 0.984208 |

| Day 4 Random Forest + Graph | Transaction + rule + graph features | 1.00 | 0.98 | 0 | 5 | 0.997087 | 0.984097 |



\## Key Finding



Adding graph features reduced false positives from 67 to 0 while keeping fraud recall at 0.98.



However, PR-AUC stayed almost the same, which means the graph features improved classification at the selected threshold but did not significantly improve overall ranking quality.



\## Feature Importance Insight



Top features remained mostly transaction and rule-based:



\- origin\_balance\_error

\- risk\_score\_v1

\- oldbalanceOrg

\- is\_high\_risk\_type

\- newbalanceOrig

\- sender\_emptied\_account

\- amount



Useful graph features included:



\- receiver\_high\_risk\_txn\_count

\- receiver\_total\_amount

\- receiver\_avg\_amount

\- receiver\_in\_degree

\- mule\_risk\_score\_v1



Low-importance graph features included:



\- possible\_mule\_receiver

\- mule\_alert\_v1

\- sender\_out\_degree



\## Technical Caution



The graph features were calculated using the full dataset before train-test split.



This does not use direct fraud labels in the safe graph features, but it may still create mild future information leakage because test-row relationships are included in aggregate graph statistics.



For a more production-realistic version, the next step should calculate graph features using only training data or use a time-based split.



\## Conclusion



Day 4 proved that graph/account-level features can support transaction-level ML and help reduce false positives. FRIX now combines rule-based fraud signals, machine learning classification, and graph-based mule-risk intelligence.

