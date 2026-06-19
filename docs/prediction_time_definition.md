FRIX Prediction-Time Definition



Purpose



This document defines the exact moment at which the FRIX fraud-risk model must generate a prediction and establishes which information is allowed or forbidden at that moment.



The goal is to prevent target leakage, future-data leakage, post-transaction leakage, and unrealistic model evaluation.



\## Prediction-Time Event



FRIX will generate its primary fraud-risk score:



\*\*Immediately before a transaction is authorized or declined.\*\*



At prediction time, FRIX may use:



\* Information contained in the current transaction request

\* Account and counterparty attributes already known before the transaction

\* Historical transaction data recorded strictly before the current transaction

\* Historical graph relationships created strictly before the current transaction

\* Historical velocity and behavioural features calculated strictly before the current transaction



FRIX must not use information created by processing, completing, settling, reversing, investigating, or labelling the current transaction.



\## Primary Model Use Case



The primary FRIX model is a:



\*\*Pre-transaction fraud detection and decision-support model.\*\*



Its output may support:



\* Approve

\* Decline

\* Hold for review

\* Step-up authentication

\* Manual investigation

\* Risk-based transaction monitoring



The model does not make the final business decision by itself. It provides a probability, risk band, reason codes, and supporting behavioural signals.



\## Current Transaction Information Allowed



The following current-transaction fields are available at prediction time:



\* Transaction step or timestamp

\* Transaction type

\* Transaction amount

\* Sender identifier for historical lookup only

\* Receiver identifier for historical lookup only

\* Sender balance before the transaction

\* Receiver balance before the transaction, when available

\* Previously calculated historical sender behaviour

\* Previously calculated historical receiver behaviour

\* Previously observed sender-receiver relationships



Identifiers may be used to retrieve historical features but must not be passed directly into the model as arbitrary categorical identifiers.



\## Historical Information Allowed



Historical features must be calculated using transactions that occurred strictly before the current transaction.



Examples include:



\* Sender prior transaction count

\* Receiver prior transaction count

\* Sender prior transaction volume

\* Receiver prior transaction volume

\* Sender transaction count in earlier rolling windows

\* Receiver transaction count in earlier rolling windows

\* Number of prior unique receivers

\* Number of prior unique senders

\* Prior sender out-degree

\* Prior receiver in-degree

\* Prior sender-receiver interaction count

\* Prior sender-receiver transferred volume

\* Prior reciprocal relationship indicator

\* Historical velocity alerts

\* Historical funnel and fan-out signals



The current transaction must not be included while calculating its own historical features.



\## Information Forbidden at Prediction Time



The following information must not be used by the strict pre-transaction model:



\* Fraud label of the current transaction

\* Fraud labels created after investigation

\* Final transaction status

\* New sender balance after the transaction

\* New receiver balance after the transaction

\* Post-transaction balance errors

\* Whether the sender account became empty after the transaction

\* Chargeback or dispute outcome

\* Reversal outcome

\* Manual-review decision

\* Settlement result

\* Future transaction counts

\* Future transaction volumes

\* Future graph relationships

\* Dataset-wide account totals calculated using later transactions

\* Thresholds fitted using validation or test data

\* Features derived directly or indirectly from the target label

\* Existing fraud flags produced after the current transaction



\## Post-Transaction Model Separation



Post-transaction information may be used only in a separately defined model for purposes such as:



\* Transaction investigation

\* Fraud confirmation

\* Chargeback prediction

\* Case prioritization

\* Post-settlement monitoring



A post-transaction model must not be reported as a real-time authorization model.



Its metrics must remain separate from the strict pre-transaction model.



\## Temporal Ordering Rule



All modelling datasets must preserve chronological order.



For every transaction at time (t):



\* Training features may use information from times earlier than (t)

\* Features must not use information from time (t) after transaction execution

\* Features must not use information from any time later than (t)



Where multiple transactions share the same coarse time step, the original stable row order must be preserved unless a more precise timestamp is available.



\## Train, Validation, and Test Policy



Model development will use chronological splits.



\* Training data: earliest period

\* Validation data: subsequent period

\* Test data: latest untouched period



The test dataset must not be used for:



\* Feature selection

\* Threshold selection

\* Hyperparameter tuning

\* Calibration fitting

\* Model selection

\* Class-weight selection

\* Early stopping decisions



The test set will be opened only after the full modelling pipeline has been finalized.



\## Threshold Policy



Classification thresholds must be selected using validation data only.



Different operating thresholds may be maintained for:



\* High-precision mode

\* Balanced mode

\* High-recall mode



Final test metrics must use thresholds frozen before test evaluation.



\## Feature Engineering Policy



Every engineered feature must satisfy all of the following:



1\. It has a clear business definition.

2\. Its availability time is documented.

3\. It is reproducible in production.

4\. It uses only information available at prediction time.

5\. It does not include the current transaction in its own history.

6\. It is calculated identically during training and live inference.

7\. Its data source and owner are documented.

8\. Its leakage risk is reviewed before model training.



\## Model Output



At prediction time, FRIX should return:



\* Fraud probability

\* Risk band

\* Classification decision at the active threshold

\* Model version

\* Threshold version

\* Reason codes

\* Rule-based signals

\* Velocity signals

\* Graph signals

\* Data-quality warnings

\* Prediction timestamp



\## Governance Rule



Any change to the prediction-time definition requires:



\* Documentation update

\* Feature registry review

\* Leakage re-audit

\* Model retraining

\* Validation rerun

\* Version increment

\* Approval before production deployment



\## Frozen Definition



For the current FRIX development cycle, the official prediction point is:



\*\*Immediately before authorization, using the current transaction request and historical information available strictly before that transaction.\*\*



This definition remains frozen until formally revised.



