from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import joblib


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
MODELS_DIR = PROJECT_ROOT / "models"

REGISTRY_PATH = MODELS_DIR / "milestone24_champion_registry.json"

BASE_MODEL_PATH = MODELS_DIR / "frix_xgboost_base_v1.joblib"
GRAPH_MODEL_PATH = MODELS_DIR / "frix_xgboost_graph_v1.joblib"

BASE_CALIBRATOR_PATH = (
    MODELS_DIR / "base_only_isotonic_calibrator.joblib"
)
GRAPH_CALIBRATOR_PATH = (
    MODELS_DIR / "base_plus_graph_isotonic_calibrator.joblib"
)

MODEL_NAME = "frix_xgboost_base_v1"
GRAPH_MODEL_NAME = "frix_xgboost_graph_v1"


class MockFraudModel:
    """
    Lightweight mock model for CI tests when local model artifacts
    are intentionally unavailable.
    """

    def __init__(self, graph_aware: bool = False) -> None:
        self.graph_aware = graph_aware

    def predict_proba(self, input_data):
        probabilities = []

        for _, row in input_data.iterrows():
            amount = float(row.get("amount", 0.0))
            high_risk_type = int(
                row.get("is_high_risk_type", 0)
            )

            score = 0.01

            if high_risk_type:
                score += 0.70

            if amount >= 100_000:
                score += 0.285

            if self.graph_aware:
                receiver_degree = float(
                    row.get("receiver_in_degree_prior", 0)
                )
                possible_mule = int(
                    row.get("possible_mule_receiver_v2", 0)
                )

                if receiver_degree >= 5:
                    score += 0.10

                if possible_mule:
                    score += 0.10

            score = min(score, 0.999)
            probabilities.append([1.0 - score, score])

        return probabilities

    def predict(self, input_data):
        return [
            int(probability[1] >= 0.50)
            for probability in self.predict_proba(input_data)
        ]


class IdentityCalibrator:
    """
    Test-mode calibrator that leaves probabilities unchanged.
    """

    def predict(self, probabilities):
        return probabilities


def is_test_mode() -> bool:
    return (
        os.getenv("FRIX_TEST_MODE", "false").lower()
        == "true"
    )


def load_registry() -> dict[str, Any]:
    if REGISTRY_PATH.exists():
        return json.loads(
            REGISTRY_PATH.read_text(encoding="utf-8")
        )

    return {
        "champion": {
            "name": MODEL_NAME,
            "threshold": 0.987806,
            "calibrator": "isotonic",
        },
        "challenger": {
            "name": GRAPH_MODEL_NAME,
            "balanced_profile": {
                "threshold": 0.991908,
                "calibrator": "isotonic",
            },
            "investigation_profile": {
                "threshold": 0.862182,
            },
        },
    }


def load_model_bundle() -> dict[str, Any]:
    """
    Loads champion, graph challenger, calibrators, and registry.

    In CI/test mode, lightweight mocks are returned so the API tests
    do not require binary model artifacts.
    """
    registry = load_registry()

    if is_test_mode():
        return {
            "champion_model": MockFraudModel(
                graph_aware=False
            ),
            "challenger_model": MockFraudModel(
                graph_aware=True
            ),
            "champion_calibrator": IdentityCalibrator(),
            "challenger_calibrator": IdentityCalibrator(),
            "registry": registry,
            "champion_name": MODEL_NAME,
            "challenger_name": GRAPH_MODEL_NAME,
        }

    required_paths = [
        BASE_MODEL_PATH,
        GRAPH_MODEL_PATH,
        BASE_CALIBRATOR_PATH,
        GRAPH_CALIBRATOR_PATH,
    ]

    missing = [
        str(path)
        for path in required_paths
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing FRIX deployment artifacts:\n"
            + "\n".join(missing)
        )

    return {
        "champion_model": joblib.load(BASE_MODEL_PATH),
        "challenger_model": joblib.load(
            GRAPH_MODEL_PATH
        ),
        "champion_calibrator": joblib.load(
            BASE_CALIBRATOR_PATH
        ),
        "challenger_calibrator": joblib.load(
            GRAPH_CALIBRATOR_PATH
        ),
        "registry": registry,
        "champion_name": MODEL_NAME,
        "challenger_name": GRAPH_MODEL_NAME,
    }


def load_fraud_model():
    """
    Backward-compatible loader used by older imports.
    Returns the frozen champion model.
    """
    return load_model_bundle()["champion_model"]


def is_model_available() -> bool:
    if is_test_mode():
        return True

    return all(
        path.exists()
        for path in [
            BASE_MODEL_PATH,
            GRAPH_MODEL_PATH,
            BASE_CALIBRATOR_PATH,
            GRAPH_CALIBRATOR_PATH,
        ]
    )
