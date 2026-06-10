from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "random_forest_fraud_model_day2.joblib"
MODEL_NAME = "random_forest_fraud_model_day2"


def load_fraud_model():
    """
    Loads the trained fraud detection model from the local models folder.
    """
    return joblib.load(MODEL_PATH)


def is_model_available() -> bool:
    """
    Checks whether the model artifact exists locally.
    """
    return MODEL_PATH.exists()