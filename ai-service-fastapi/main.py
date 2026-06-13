from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from feature_engineering import build_model_features
from model_loader import MODEL_NAME, is_model_available, load_fraud_model
from risk_explainer import assign_risk_level, build_reason_codes
from schemas import FraudPredictionResponse, TransactionRequest


model = load_fraud_model()

app = FastAPI(
    title="FRIX Fraud Detection API",
    description="Financial Risk Intelligence API for fraud-risk scoring",
    version="1.0.0",
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

@app.get("/")
def home():
    return {
        "message": "FRIX Fraud Detection API is running",
        "status": "healthy",
        "model": MODEL_NAME,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "frix-ai-service",
        "model_loaded": is_model_available(),
        "model_name": MODEL_NAME,
    }


@app.post("/predict-fraud", response_model=FraudPredictionResponse)
def predict_fraud(transaction: TransactionRequest):
    input_data, engineered_values = build_model_features(transaction)

    fraud_probability = float(model.predict_proba(input_data)[0][1])
    fraud_prediction = int(model.predict(input_data)[0])

    risk_level = assign_risk_level(fraud_probability)
    reason_codes = build_reason_codes(engineered_values)

    return {
        "fraud_prediction": fraud_prediction,
        "fraud_probability": round(fraud_probability, 4),
        "risk_level": risk_level,
        "risk_score_v1": engineered_values["risk_score_v1"],
        "model_used": MODEL_NAME,
        "reason_codes": reason_codes,
    }