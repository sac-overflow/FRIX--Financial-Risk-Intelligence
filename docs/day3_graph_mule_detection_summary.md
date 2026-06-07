\# Day 3 - Graph-Based Mule Detection Summary



\## Goal



Day 3 focused on building graph-based account and receiver-level features for fraud and mule detection.



\## Graph Representation



Transactions were modeled as a directed graph:



\- Sender account: nameOrig

\- Receiver account: nameDest

\- Transaction: directed edge from sender to receiver



\## Graph Features Created



\- receiver\_in\_degree

\- sender\_out\_degree

\- receiver\_total\_amount

\- receiver\_avg\_amount

\- receiver\_high\_risk\_txn\_count

\- possible\_mule\_receiver

\- mule\_risk\_score\_v1

\- mule\_alert\_v1



\## Key Findings



\- Sender out-degree was not very useful because most senders appear only once.

\- Receiver-side features were more useful for graph analysis.

\- Simple high-activity receiver rules were not strong enough because normal high-volume receivers can look suspicious too.

\- Receiver fraud exposure was very strong, but it uses the fraud label and can cause data leakage, so it should be used only for offline investigation, not real-time prediction.

\- Mule risk score v1 was built without using fraud labels to avoid leakage.

\- Mule risk score provided account-level context but was not strong enough as a standalone fraud classifier.



\## Mule Alert v1 Result



Mule Alert Precision: 0.12%  

Mule Alert Recall: 12.35%



\## Conclusion



The graph layer is useful for account-level and mule-risk intelligence, but it should support the transaction-level ML model rather than replace it. FRIX now has both transaction-level fraud detection and graph-based receiver risk profiling.

