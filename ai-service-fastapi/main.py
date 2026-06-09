from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "random_forest_fraud_model_day2.joblib"

model = joblib.load(MODEL_PATH)

app = FastAPI(
    title="FRIX Fraud Detection API",
    description="Financial Risk Intelligence API for fraud-risk scoring",
    version="1.0.0"
)


class TransactionRequest(BaseModel):
    amount: float
    transaction_type: str
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    sender_txn_count: int = 1
    receiver_txn_count: int = 1


FEATURE_COLUMNS = [
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "origin_balance_error",
    "dest_balance_error",
    "is_high_risk_type",
    "sender_txn_count",
    "receiver_txn_count",
    "sender_emptied_account",
    "is_large_amount",
    "risk_score_v1"
]


LARGE_AMOUNT_THRESHOLD = 519460.35099999997


@app.get("/")
def home():
    return {
        "message": "FRIX Fraud Detection API is running",
        "status": "healthy",
        "model": "random_forest_fraud_model_day2"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "frix-ai-service",
        "model_loaded": MODEL_PATH.exists()
    }


@app.post("/predict-fraud")
def predict_fraud(transaction: TransactionRequest):
    txn_type = transaction.transaction_type.upper()

    origin_balance_error = (
        transaction.oldbalanceOrg - transaction.amount - transaction.newbalanceOrig
    )

    dest_balance_error = (
        transaction.oldbalanceDest + transaction.amount - transaction.newbalanceDest
    )

    is_high_risk_type = int(txn_type in ["TRANSFER", "CASH_OUT"])

    sender_emptied_account = int(
        transaction.oldbalanceOrg > 0 and transaction.newbalanceOrig == 0
    )

    is_large_amount = int(transaction.amount > LARGE_AMOUNT_THRESHOLD)

    risk_score_v1 = (
        is_high_risk_type * 20
        + is_large_amount * 25
        + sender_emptied_account * 25
        + int(abs(dest_balance_error) > 0) * 20
        + int(transaction.receiver_txn_count > 30) * 10
    )

    input_data = pd.DataFrame([{
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,
        "origin_balance_error": origin_balance_error,
        "dest_balance_error": dest_balance_error,
        "is_high_risk_type": is_high_risk_type,
        "sender_txn_count": transaction.sender_txn_count,
        "receiver_txn_count": transaction.receiver_txn_count,
        "sender_emptied_account": sender_emptied_account,
        "is_large_amount": is_large_amount,
        "risk_score_v1": risk_score_v1
    }])[FEATURE_COLUMNS]

    fraud_probability = float(model.predict_proba(input_data)[0][1])
    fraud_prediction = int(model.predict(input_data)[0])

    if fraud_probability >= 0.75:
        risk_level = "HIGH"
    elif fraud_probability >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "fraud_prediction": fraud_prediction,
        "fraud_probability": round(fraud_probability, 4),
        "risk_level": risk_level,
        "risk_score_v1": risk_score_v1,
        "model_used": "random_forest_fraud_model_day2",
        "reason_codes": {
            "high_risk_transaction_type": bool(is_high_risk_type),
            "sender_emptied_account": bool(sender_emptied_account),
            "large_amount": bool(is_large_amount),
            "origin_balance_error": round(origin_balance_error, 2),
            "dest_balance_error": round(dest_balance_error, 2)
        }
    }