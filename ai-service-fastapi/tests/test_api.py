import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app  # noqa: E402
from graph_engine import graph_intelligence  # noqa: E402
from transaction_memory import transaction_memory  # noqa: E402


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_risk_engine_state():
    transaction_memory.clear()
    graph_intelligence.clear()
    yield
    transaction_memory.clear()
    graph_intelligence.clear()


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
        "sender_id": "high-risk-sender",
        "receiver_id": "high-risk-receiver",
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
    assert data["context_features"]["sender_txn_count_10m"] == 0
    assert data["velocity_signals"]["velocity_score"] == 0


def test_low_risk_fraud_prediction():
    payload = {
        "sender_id": "low-risk-sender",
        "receiver_id": "low-risk-receiver",
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
    assert data["context_features"]["sender_txn_count_10m"] == 0
    assert data["velocity_signals"]["velocity_score"] == 0


def test_repeated_transactions_trigger_velocity_alerts():
    payload = {
        "sender_id": "velocity-sender",
        "receiver_id": "velocity-receiver",
        "amount": 2500,
        "transaction_type": "TRANSFER",
        "oldbalanceOrg": 50000,
        "newbalanceOrig": 47500,
        "oldbalanceDest": 10000,
        "newbalanceDest": 12500,
        "sender_txn_count": 1,
        "receiver_txn_count": 1,
    }

    response = None

    for _ in range(6):
        response = client.post("/predict-fraud", json=payload)
        assert response.status_code == 200

    assert response is not None
    data = response.json()

    assert data["context_features"]["sender_txn_count_10m"] == 5
    assert data["context_features"]["receiver_txn_count_10m"] == 5
    assert data["context_features"]["sender_volume_10m"] == 12500.0
    assert data["context_features"]["receiver_volume_10m"] == 12500.0
    assert data["velocity_signals"]["sender_velocity_alert"] is True
    assert data["velocity_signals"]["receiver_velocity_alert"] is True
    assert data["velocity_signals"]["repeated_small_transfer"] is True
    assert data["velocity_signals"]["velocity_score"] == 50
