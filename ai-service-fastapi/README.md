\# FRIX FastAPI Fraud Detection Service



This folder contains the ML-backed FastAPI service for FRIX - Financial Risk Intelligence.



The service loads the trained Random Forest fraud detection model and exposes an API endpoint that accepts transaction details, performs feature engineering, predicts fraud risk, and returns explainable reason codes.



\## Service Structure



ai-service-fastapi/

\- main.py

\- schemas.py

\- model\_loader.py

\- feature\_engineering.py

\- risk\_explainer.py

\- README.md



\## Files



main.py - FastAPI app and API endpoints

schemas.py - Request and response models

model\_loader.py - Model loading and model availability checks

feature\_engineering.py - Converts API input into model-ready features

risk\_explainer.py - Risk level and reason-code logic

README.md - Service documentation



\## Model Used



random\_forest\_fraud\_model\_day2.joblib



Expected local model path:



../models/random\_forest\_fraud\_model\_day2.joblib



The model file is not committed to GitHub because trained model artifacts are ignored by .gitignore.



\## Run the API



From the project root:



venv\\Scripts\\activate

cd ai-service-fastapi

uvicorn main:app --reload



The API will run at:



http://127.0.0.1:8000



Swagger documentation:



http://127.0.0.1:8000/docs



\## Endpoints



GET /

Returns basic service status.



GET /health

Returns API health and model availability.



POST /predict-fraud

Accepts transaction information and returns fraud prediction, fraud probability, risk level, rule score, and reason codes.



\## Sample High-Risk Request



{

&#x20; "amount": 900000,

&#x20; "transaction\_type": "TRANSFER",

&#x20; "oldbalanceOrg": 900000,

&#x20; "newbalanceOrig": 0,

&#x20; "oldbalanceDest": 10000,

&#x20; "newbalanceDest": 910000,

&#x20; "sender\_txn\_count": 1,

&#x20; "receiver\_txn\_count": 27

}



Sample response:



{

&#x20; "fraud\_prediction": 1,

&#x20; "fraud\_probability": 0.9833,

&#x20; "risk\_level": "HIGH",

&#x20; "risk\_score\_v1": 70,

&#x20; "model\_used": "random\_forest\_fraud\_model\_day2"

}



\## Sample Low-Risk Request



{

&#x20; "amount": 2500,

&#x20; "transaction\_type": "PAYMENT",

&#x20; "oldbalanceOrg": 10000,

&#x20; "newbalanceOrig": 7500,

&#x20; "oldbalanceDest": 0,

&#x20; "newbalanceDest": 0,

&#x20; "sender\_txn\_count": 1,

&#x20; "receiver\_txn\_count": 1

}



Sample response:



{

&#x20; "fraud\_prediction": 0,

&#x20; "fraud\_probability": 0,

&#x20; "risk\_level": "LOW",

&#x20; "risk\_score\_v1": 20,

&#x20; "model\_used": "random\_forest\_fraud\_model\_day2"

}



\## Production Note



This service currently performs local ML inference using a trained model artifact.



In production, the model artifact should be stored and versioned using an artifact store such as S3, MLflow, or a model registry.

