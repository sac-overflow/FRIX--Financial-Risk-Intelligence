import os
from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "random_forest_fraud_model_day2.joblib"
MODEL_NAME = "random_forest_fraud_model_day2"


class MockFraudModel:
    """
    Lightweight mock model used only for CI tests when the real model artifact
    is not available in the GitHub Actions runner.
    """

    def predict_proba(self, input_data):
        probabilities = []

        for _, row in input_data.iterrows():
            if row["risk_score_v1"] >= 70:
                probabilities.append([0.0167, 0.9833])
            else:
                probabilities.append([1.0, 0.0])

        return probabilities

    def predict(self, input_data):
        predictions = []

        for _, row in input_data.iterrows():
            if row["risk_score_v1"] >= 70:
                predictions.append(1)
            else:
                predictions.append(0)

        return predictions


def is_test_mode() -> bool:
    """
    Checks whether the service is running in CI/test mode.
    """
    return os.getenv("FRIX_TEST_MODE", "false").lower() == "true"


def load_fraud_model():
    """
    Loads the trained fraud detection model from the local models folder.

    In CI/test mode, a lightweight mock model is used because the real model
    artifact is intentionally not committed to GitHub.
    """
    if is_test_mode():
        return MockFraudModel()

    return joblib.load(MODEL_PATH)


def is_model_available() -> bool:
    """
    Checks whether the model artifact exists locally or test mode is active.
    """
    return MODEL_PATH.exists() or is_test_mode()