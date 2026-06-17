from pydantic import BaseModel


class TransactionRequest(BaseModel):
    sender_id: str = "anonymous_sender"
    receiver_id: str = "anonymous_receiver"
    amount: float
    transaction_type: str
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    sender_txn_count: int = 1
    receiver_txn_count: int = 1

class ContextFeatures(BaseModel):
    sender_txn_count_10m: int
    receiver_txn_count_10m: int
    sender_volume_10m: float
    receiver_volume_10m: float
    unique_receivers_10m: int
    unique_senders_10m: int

class ReasonCodes(BaseModel):
    high_risk_transaction_type: bool
    sender_emptied_account: bool
    large_amount: bool
    origin_balance_error: float
    dest_balance_error: float

class VelocitySignals(BaseModel):
    sender_velocity_alert: bool
    receiver_velocity_alert: bool
    sender_volume_alert: bool
    receiver_volume_alert: bool
    repeated_small_transfer: bool
    funnel_pattern: bool
    fan_out_pattern: bool
    velocity_score: int

class FraudPredictionResponse(BaseModel):
    fraud_prediction: int
    fraud_probability: float
    risk_level: str
    risk_score_v1: int
    model_used: str
    reason_codes: ReasonCodes
    context_features: ContextFeatures
    velocity_signals: VelocitySignals
 
