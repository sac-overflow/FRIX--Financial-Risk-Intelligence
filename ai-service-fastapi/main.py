from __future__ import annotations

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from feature_engineering import build_model_features
from graph_engine import graph_intelligence
from model_loader import (
    MODEL_NAME,
    is_model_available,
    load_model_bundle,
)
from risk_explainer import assign_risk_level, build_reason_codes
from risk_fusion import calculate_fused_risk
from schemas import FraudPredictionResponse, TransactionRequest
from transaction_memory import transaction_memory
from velocity_engine import calculate_velocity_signals


model_bundle = load_model_bundle()

champion_model = model_bundle["champion_model"]
challenger_model = model_bundle["challenger_model"]
champion_calibrator = model_bundle["champion_calibrator"]
challenger_calibrator = model_bundle["challenger_calibrator"]
model_registry = model_bundle["registry"]


app = FastAPI(
    title="FRIX Fraud Detection API",
    description="Financial Risk Intelligence API for fraud-risk scoring",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calibrate_probability(calibrator, raw_probability: float) -> float:
    calibrated = calibrator.predict(
        np.asarray([raw_probability], dtype=float)
    )

    return float(
        np.clip(
            np.asarray(calibrated).reshape(-1)[0],
            0.0,
            1.0,
        )
    )


def graph_history_available(graph_signals: dict) -> bool:
    """
    Uses the graph challenger only when meaningful prior graph history exists.
    The current transaction is not included in these signals.
    """
    return any(
        [
            int(graph_signals["sender_out_degree_prior"]) > 0,
            int(graph_signals["receiver_in_degree_prior"]) > 0,
            float(graph_signals["receiver_total_amount_prior"]) > 0.0,
            int(
                graph_signals[
                    "receiver_high_risk_txn_count_prior"
                ]
            )
            > 0,
        ]
    )


def operational_ml_score(
    raw_probability: float,
    high_threshold: float,
) -> int:
    """
    Converts a raw model score into a 0-100 operational score.

    A score of 70 corresponds to the frozen high-risk threshold.
    This is separate from the calibrated fraud probability.
    """
    raw_probability = float(
        np.clip(raw_probability, 0.0, 1.0)
    )
    high_threshold = float(
        np.clip(high_threshold, 1e-6, 1.0 - 1e-6)
    )

    if raw_probability < high_threshold:
        return int(
            round(
                min(
                    69.0,
                    (raw_probability / high_threshold) * 70.0,
                )
            )
        )

    score_above_threshold = (
        (raw_probability - high_threshold)
        / (1.0 - high_threshold)
    )

    return int(
        round(
            min(
                100.0,
                70.0 + score_above_threshold * 30.0,
            )
        )
    )


def champion_threshold() -> float:
    return float(
        model_registry["champion"]["threshold"]
    )


def challenger_threshold() -> float:
    return float(
        model_registry["challenger"][
            "balanced_profile"
        ]["threshold"]
    )


@app.get("/")
def home():
    return {
        "message": "FRIX Fraud Detection API is running",
        "status": "healthy",
        "model": MODEL_NAME,
        "architecture": "champion-challenger",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "frix-ai-service",
        "model_loaded": is_model_available(),
        "model_name": MODEL_NAME,
    }


@app.post(
    "/predict-fraud",
    response_model=FraudPredictionResponse,
)
def predict_fraud(transaction: TransactionRequest):
    context_features = transaction_memory.get_context_features(
        sender_id=transaction.sender_id,
        receiver_id=transaction.receiver_id,
    )

    velocity_signals = calculate_velocity_signals(
        context_features=context_features,
        amount=transaction.amount,
    )

    graph_signals = graph_intelligence.get_graph_signals(
        sender_id=transaction.sender_id,
        receiver_id=transaction.receiver_id,
    )

    (
        base_input,
        graph_input,
        engineered_values,
    ) = build_model_features(
        transaction=transaction,
        graph_signals=graph_signals,
    )

    base_raw_probability = float(
        champion_model.predict_proba(base_input)[0][1]
    )

    graph_raw_probability = float(
        challenger_model.predict_proba(graph_input)[0][1]
    )

    use_graph_model = graph_history_available(
        graph_signals
    )

    if use_graph_model:
        raw_probability = graph_raw_probability
        calibrated_probability = calibrate_probability(
            challenger_calibrator,
            graph_raw_probability,
        )
        selected_threshold = challenger_threshold()
        selected_model_name = model_bundle[
            "challenger_name"
        ]
    else:
        raw_probability = base_raw_probability
        calibrated_probability = calibrate_probability(
            champion_calibrator,
            base_raw_probability,
        )
        selected_threshold = champion_threshold()
        selected_model_name = model_bundle[
            "champion_name"
        ]

    fraud_prediction = int(
        raw_probability >= selected_threshold
    )

    ml_risk_score = operational_ml_score(
        raw_probability=raw_probability,
        high_threshold=selected_threshold,
    )

    fused_risk = calculate_fused_risk(
        fraud_probability=calibrated_probability,
        ml_risk_score=ml_risk_score,
        rule_risk_score=engineered_values[
            "risk_score_v1"
        ],
        velocity_score=velocity_signals[
            "velocity_score"
        ],
        graph_score=graph_signals["graph_score"],
    )

    risk_level = assign_risk_level(
        fraud_probability=calibrated_probability,
        operational_score=ml_risk_score,
    )

    reason_codes = build_reason_codes(
        engineered_values
    )

    transaction_memory.record_transaction(
        sender_id=transaction.sender_id,
        receiver_id=transaction.receiver_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
    )

    graph_intelligence.record_transaction(
        sender_id=transaction.sender_id,
        receiver_id=transaction.receiver_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
    )

    return {
        "fraud_prediction": fraud_prediction,
        "fraud_probability": round(
            calibrated_probability,
            6,
        ),
        "risk_level": risk_level,
        "risk_score_v1": engineered_values[
            "risk_score_v1"
        ],
        "model_used": selected_model_name,
        "reason_codes": reason_codes,
        "context_features": context_features,
        "velocity_signals": velocity_signals,
        "fused_risk": fused_risk,
        "graph_signals": graph_signals,
    }
