# FRIX — Financial Risk Intelligence Platform

FRIX is an AI-powered fintech risk intelligence platform for real-time fraud detection, transaction risk scoring, mule-risk analysis, and model-driven financial decision support.

The platform currently includes a machine-learning-backed FastAPI service and a premium React dashboard that are integrated through a modular API layer.

---

## Current Project Status

FRIX currently supports:

* ML-backed fraud prediction using a trained Random Forest model
* Real-time transaction scoring through FastAPI
* React dashboard with a premium fintech UI
* Frontend-to-backend integration for fraud prediction
* Risk level, fraud probability, risk score, model name, and reason-code display
* FastAPI test suite with pytest
* GitHub Actions CI for backend tests
* Dockerized FastAPI service
* Environment-based frontend API configuration

---

## Architecture Overview

```text
React Dashboard
        ↓
Frontend API Service Layer
        ↓
FastAPI Fraud Detection API
        ↓
Feature Engineering Layer
        ↓
Fraud Model / Mock Test Model
        ↓
Reason Code Generator
        ↓
Risk Result Displayed in UI
```

---

## Repository Structure

```text
frix-financial-risk-intelligence/
│
├── ai-service-fastapi/
│   ├── main.py
│   ├── schemas.py
│   ├── model_loader.py
│   ├── feature_engineering.py
│   ├── risk_explainer.py
│   ├── requirements-api.txt
│   ├── Dockerfile
│   └── tests/
│
├── frontend-react/
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── context/
│   │   │   └── routes.tsx
│   │   ├── config/
│   │   │   └── apiConfig.ts
│   │   └── services/
│   │       └── fraudApi.ts
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
│
├── .github/workflows/
│   └── fastapi-ci.yml
│
├── docs/
├── ml-notebooks/
├── models/
├── data/
└── README.md
```

---

## Backend — FastAPI Fraud Detection Service

The backend exposes fraud-risk APIs and owns the fraud intelligence logic.

### Main endpoints

```text
GET  /
GET  /health
POST /predict-fraud
```

### Run backend locally

From the project root:

```cmd
cd ai-service-fastapi
..\venv\Scripts\activate
set FRIX_TEST_MODE=true
uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Frontend — React Risk Dashboard

The frontend is a React + Vite dashboard that provides the user-facing FRIX console.

### Run frontend locally

From the project root:

```cmd
cd frontend-react
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

## Frontend Environment Setup

Create a local `.env` file inside `frontend-react/`:

```env
VITE_FRIX_API_BASE_URL=http://127.0.0.1:8000
```

An example file is provided:

```text
frontend-react/.env.example
```

The local `.env` file is ignored by Git.

---

## Fraud Prediction Flow

The Fraud Prediction page calls the FastAPI backend through the frontend service layer.

```text
frontend-react/src/services/fraudApi.ts
```

Example request:

```json
{
  "amount": 900000,
  "transaction_type": "TRANSFER",
  "oldbalanceOrg": 900000,
  "newbalanceOrig": 0,
  "oldbalanceDest": 10000,
  "newbalanceDest": 910000,
  "sender_txn_count": 1,
  "receiver_txn_count": 27
}
```

Example response:

```json
{
  "fraud_prediction": 1,
  "fraud_probability": 0.9833,
  "risk_level": "HIGH",
  "risk_score_v1": 90,
  "model_used": "random_forest_fraud_model_day2",
  "reason_codes": {
    "high_risk_transaction_type": true,
    "sender_emptied_account": true,
    "large_amount": true,
    "origin_balance_error": 0,
    "dest_balance_error": 0
  }
}
```

---

## Testing

### Backend tests

```cmd
cd ai-service-fastapi
..\venv\Scripts\activate
set FRIX_TEST_MODE=true
python -m pytest
```

Expected result:

```text
3 passed
```

### Frontend production build

```cmd
cd frontend-react
npm run build
```

Expected result:

```text
built successfully
```

---

## Docker

The FastAPI backend is dockerized.

### Build backend image

```cmd
cd ai-service-fastapi
docker build -t frix-fastapi .
```

### Run backend container

```cmd
docker run -d -p 8000:8000 --name frix-fastapi-container frix-fastapi
```

### Stop and remove container

```cmd
docker stop frix-fastapi-container
docker rm frix-fastapi-container
```

---

## Current ML Model

Current model used by the backend:

```text
random_forest_fraud_model_day2
```

Current production-style API supports:

* Fraud prediction
* Fraud probability
* Risk level assignment
* Rule-assisted risk score
* Reason-code explanation

In CI and Docker test mode, FRIX can use a lightweight mock model through:

```text
FRIX_TEST_MODE=true
```

This avoids committing large local model artifacts to GitHub.

---

## Planned Enhancements

Future FRIX enhancements include:

* Docker Compose for unified frontend + backend startup
* API Console page connected to live backend endpoints
* Model Monitoring page connected to real metrics
* Expanded black-box, white-box, and edge-case tests
* Sandbox transaction simulator
* Kafka-based transaction streaming
* Prometheus and Grafana monitoring
* Graph-risk pipeline for mule-network detection
* Model selector for Random Forest, XGBoost, LightGBM, graph-risk, and rule-assisted modes

---

## Project Goal

FRIX is being built as a production-style fintech AI platform demonstrating:

* Applied machine learning for fraud detection
* Full-stack frontend-backend integration
* API-first product architecture
* Risk explainability
* Modular system design
* CI/CD and Dockerized deployment foundations
* Future-ready streaming and graph intelligence architecture
