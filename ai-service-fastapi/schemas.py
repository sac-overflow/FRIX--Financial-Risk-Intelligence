from pydantic import BaseModel


class TransactionRequest(BaseModel):
    amount: float
    transaction_type: str
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    sender_txn_count: int = 1
    receiver_txn_count: int = 1


class ReasonCodes(BaseModel):
    high_risk_transaction_type: bool
    sender_emptied_account: bool
    large_amount: bool
    origin_balance_error: float
    dest_balance_error: float


class FraudPredictionResponse(BaseModel):
    fraud_prediction: int
    fraud_probability: float
    risk_level: str
    risk_score_v1: int
    model_used: str
    reason_codes: ReasonCodes