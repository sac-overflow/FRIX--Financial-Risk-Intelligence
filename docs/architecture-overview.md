\# FRIX Architecture Overview



FRIX is a modular fintech risk intelligence platform designed for real-time fraud detection, transaction risk scoring, mule-risk analysis, and future event-driven fraud monitoring.



The current implementation includes a FastAPI-based fraud detection service, a React risk dashboard, a modular frontend API service layer, Dockerized backend and frontend services, and GitHub Actions CI for backend validation.



\---



\## 1. Current High-Level Architecture



```text

React Risk Dashboard

&#x20;       ↓

Frontend API Service Layer

&#x20;       ↓

FastAPI Fraud Detection API

&#x20;       ↓

Feature Engineering Layer

&#x20;       ↓

Fraud Model / Mock Test Model

&#x20;       ↓

Risk Explainer

&#x20;       ↓

Risk Result Returned to UI

```



\---



\## 2. Implemented Components



\### Frontend



The frontend is located in:



```text

frontend-react/

```



It provides the user-facing FRIX console, including:



\* Landing page

\* Login page

\* Dashboard layout

\* Fraud Prediction console

\* API Console

\* Model Engine page

\* Model Monitoring page

\* Mule Network page

\* CI/CD Pipeline page

\* Settings page



Important frontend modules:



```text

frontend-react/src/app/pages/

frontend-react/src/app/components/

frontend-react/src/config/apiConfig.ts

frontend-react/src/services/fraudApi.ts

```



The frontend does not own fraud logic. It only collects user input, calls backend APIs, and renders returned risk results.



\---



\### Backend



The backend is located in:



```text

ai-service-fastapi/

```



It provides the fraud intelligence API.



Important backend modules:



```text

main.py

schemas.py

feature\_engineering.py

model\_loader.py

risk\_explainer.py

tests/

```



The backend owns:



\* Request validation

\* Feature engineering

\* Model loading

\* Fraud prediction

\* Risk scoring

\* Reason code generation

\* API response formatting



\---



\## 3. Backend Module Responsibilities



\### `main.py`



Defines the FastAPI app, CORS middleware, and API endpoints.



Implemented endpoints:



```text

GET  /

GET  /health

POST /predict-fraud

```



\### `schemas.py`



Defines Pydantic request and response schemas.



This keeps API contracts consistent between frontend and backend.



\### `feature\_engineering.py`



Converts incoming transaction requests into model-ready feature vectors.



It also calculates rule-assisted risk features such as:



\* origin balance error

\* destination balance error

\* high-risk transaction type

\* sender emptied account

\* large amount flag

\* sender activity score

\* receiver activity score

\* risk\_score\_v1



\### `model\_loader.py`



Loads the trained fraud model if available.



In test mode, it uses a lightweight mock model through:



```text

FRIX\_TEST\_MODE=true

```



This avoids committing large model artifacts into GitHub and keeps CI lightweight.



\### `risk\_explainer.py`



Converts prediction and engineered features into analyst-readable risk levels and reason codes.



\---



\## 4. Frontend Module Responsibilities



\### `apiConfig.ts`



Defines the backend API base URL.



```text

VITE\_FRIX\_API\_BASE\_URL=http://127.0.0.1:8000

```



\### `fraudApi.ts`



Centralizes frontend-to-backend calls.



Implemented frontend API functions:



```text

predictFraud()

getHealthStatus()

```



This prevents API logic from being duplicated across React pages.



\### `FraudPrediction.tsx`



Provides the UI form for transaction scoring and displays:



\* fraud prediction

\* fraud probability

\* risk level

\* risk score

\* model used

\* reason codes



\### `APIConsole.tsx`



Provides a live API console inside the FRIX dashboard.



Currently supports live calls to:



```text

GET  /health

POST /predict-fraud

```



\---



\## 5. Fraud Prediction Flow



```text

User enters transaction in React

&#x20;       ↓

FraudPrediction.tsx builds request payload

&#x20;       ↓

fraudApi.ts calls POST /predict-fraud

&#x20;       ↓

FastAPI validates request through Pydantic schema

&#x20;       ↓

feature\_engineering.py builds model features

&#x20;       ↓

model\_loader.py provides model

&#x20;       ↓

model predicts fraud probability

&#x20;       ↓

risk\_explainer.py assigns risk level and reason codes

&#x20;       ↓

FastAPI returns JSON response

&#x20;       ↓

React renders result card

```



\---



\## 6. Docker Compose Runtime



FRIX can run as a full local stack using Docker Compose.



```text

docker compose up --build

```



Services:



```text

frix-backend   → FastAPI service on port 8000

frix-frontend  → React dashboard on port 5173

```



This allows the platform to run as a unified frontend-backend system.



\---



\## 7. Current Architecture Strengths



\* Clear frontend/backend separation

\* Modular API service layer in frontend

\* Modular backend layers

\* API-first design

\* Dockerized backend and frontend

\* CI-backed backend testing

\* Real frontend-backend integration

\* Environment-based API configuration

\* Mock model support for CI and container mode



\---



\## 8. Known Current Limitations



The current implementation is still an MVP-style platform and does not yet include:



\* persistent transaction database

\* authentication enforcement

\* production model registry

\* Kafka transaction streaming

\* real-time alert queue

\* Prometheus/Grafana metrics

\* large-scale graph processing

\* deployed production environment

\* full black-box and edge-case test suite



These are planned as future milestones.



\---



\## 9. Future Target Architecture



```text

Transaction Sources

&#x20;       ↓

API Gateway / Transaction Ingestion API

&#x20;       ↓

Kafka Transaction Stream

&#x20;       ↓

Fraud Scoring Workers

&#x20;       ↓

Feature Store / PostgreSQL / Cache

&#x20;       ↓

Model Selector

&#x20;       ↓

Fraud Model + Rule Engine + Graph Risk Engine

&#x20;       ↓

Alert Service

&#x20;       ↓

React Analyst Dashboard

&#x20;       ↓

Monitoring with Prometheus + Grafana

```



Future components may include:



\* Kafka for high-volume transaction streaming

\* PostgreSQL for storing scored transactions and alerts

\* Redis for low-latency feature caching

\* Prometheus and Grafana for observability

\* Neo4j, NetworkX, PyTorch Geometric, or Giraph-style graph processing for mule-network intelligence

\* model selector for Random Forest, XGBoost, LightGBM, graph-risk, and rule-assisted modes



\---



\## 10. Design Principle



FRIX follows one key design rule:



```text

Frontend owns experience.

Backend owns intelligence.

Infrastructure owns scale.

Observability owns trust.

```



