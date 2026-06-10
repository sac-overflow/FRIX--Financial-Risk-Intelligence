import sys
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app  # noqa: E402


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "frix-ai-service"
    assert data["model_loaded"] is True
    assert data["model_name"] == "random_forest_fraud_model_day2"


def test_high_risk_fraud_prediction():
    payload = {
        "amount": 900000,
        "transaction_type": "TRANSFER",
        "oldbalanceOrg": 900000,
        "newbalanceOrig": 0,
        "oldbalanceDest": 10000,
        "newbalanceDest": 910000,
        "sender_txn_count": 1,
        "receiver_txn_count": 27,
    }

    response = client.post("/predict-fraud", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["fraud_prediction"] == 1
    assert data["risk_level"] == "HIGH"
    assert data["model_used"] == "random_forest_fraud_model_day2"
    assert data["reason_codes"]["high_risk_transaction_type"] is True
    assert data["reason_codes"]["sender_emptied_account"] is True
    assert data["reason_codes"]["large_amount"] is True


def test_low_risk_fraud_prediction():
    payload = {
        "amount": 2500,
        "transaction_type": "PAYMENT",
        "oldbalanceOrg": 10000,
        "newbalanceOrig": 7500,
        "oldbalanceDest": 0,
        "newbalanceDest": 0,
        "sender_txn_count": 1,
        "receiver_txn_count": 1,
    }

    response = client.post("/predict-fraud", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["fraud_prediction"] == 0
    assert data["risk_level"] == "LOW"
    assert data["model_used"] == "random_forest_fraud_model_day2"
    assert data["reason_codes"]["high_risk_transaction_type"] is False
    assert data["reason_codes"]["sender_emptied_account"] is False
    assert data["reason_codes"]["large_amount"] is False