from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "frix_enriched_dataset_v3.csv"
FEATURE_FILE = (
    PROJECT_ROOT
    / "models"
    / "milestone24_core_pretransaction_features.json"
)
MODELS_DIR = PROJECT_ROOT / "models"

RESULTS_FILE = MODELS_DIR / "milestone24_statistical_baselines.csv"
PREDICTIONS_FILE = (
    MODELS_DIR / "milestone24_statistical_baseline_test_predictions.csv"
)

TARGET = "isFraud"
TRAIN_FRACTION = 0.60
VALIDATION_FRACTION = 0.20
RANDOM_STATE = 42


def load_inputs() -> tuple[pd.DataFrame, list[str]]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(DATA_FILE)

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(FEATURE_FILE)

    print("Loading dataset...")
    dataframe = pd.read_csv(DATA_FILE)

    print("Loading approved core features...")
    feature_list = json.loads(
        FEATURE_FILE.read_text(encoding="utf-8")
    )

    print(f"Rows: {len(dataframe):,}")
    print(f"Approved features: {len(feature_list):,}")

    return dataframe, feature_list


def prepare_features(
    dataframe: pd.DataFrame,
    feature_list: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    missing = [
        feature
        for feature in feature_list
        if not feature.startswith("type_")
        and feature not in dataframe.columns
    ]

    if missing:
        raise ValueError(f"Missing features: {missing}")

    base_features = [
        feature
        for feature in feature_list
        if not feature.startswith("type_")
    ]

    features = dataframe[base_features].copy()

    if "type" in features.columns:
        features = pd.get_dummies(
            features,
            columns=["type"],
            prefix="type",
            dtype=np.int8,
        )

    expected_columns = feature_list
    for column in expected_columns:
        if column not in features.columns:
            features[column] = 0

    features = features[expected_columns]

    non_numeric = features.select_dtypes(
        exclude=[np.number, "bool"]
    ).columns.tolist()

    if non_numeric:
        raise ValueError(
            f"Unexpected non-numeric columns: {non_numeric}"
        )

    if features.isna().any().any():
        raise ValueError("Feature matrix contains missing values.")

    target = dataframe[TARGET].astype(np.int8)

    print(f"Final feature count: {len(features.columns):,}")

    return features, target


def split_by_time(
    features: pd.DataFrame,
    target: pd.Series,
):
    train_end = int(len(features) * TRAIN_FRACTION)
    validation_end = int(
        len(features)
        * (TRAIN_FRACTION + VALIDATION_FRACTION)
    )

    x_train = features.iloc[:train_end].copy()
    x_validation = features.iloc[train_end:validation_end].copy()
    x_test = features.iloc[validation_end:].copy()

    y_train = target.iloc[:train_end].copy()
    y_validation = target.iloc[train_end:validation_end].copy()
    y_test = target.iloc[validation_end:].copy()

    print(
        f"Train: {len(x_train):,} rows, "
        f"{int(y_train.sum()):,} fraud"
    )
    print(
        f"Validation: {len(x_validation):,} rows, "
        f"{int(y_validation.sum()):,} fraud"
    )
    print(
        f"Test: {len(x_test):,} rows, "
        f"{int(y_test.sum()):,} fraud"
    )

    return (
        x_train,
        x_validation,
        x_test,
        y_train,
        y_validation,
        y_test,
    )


def choose_threshold(
    y_true: pd.Series,
    probabilities: np.ndarray,
) -> float:
    precision, recall, thresholds = precision_recall_curve(
        y_true,
        probabilities,
    )

    if len(thresholds) == 0:
        return 0.50

    precision = precision[:-1]
    recall = recall[:-1]

    denominator = precision + recall
    f1_values = np.divide(
        2 * precision * recall,
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0,
    )

    return float(thresholds[int(np.argmax(f1_values))])


def evaluate(
    name: str,
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
    seconds: float,
) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(np.int8)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "model": name,
        "threshold": threshold,
        "pr_auc": average_precision_score(
            y_true,
            probabilities,
        ),
        "roc_auc": roc_auc_score(
            y_true,
            probabilities,
        ),
        "brier_score": brier_score_loss(
            y_true,
            probabilities,
        ),
        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "f1_score": f1_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "training_seconds": round(seconds, 2),
    }


def build_models() -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1000,
                        solver="liblinear",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "gaussian_naive_bayes": GaussianNB(),
        "linear_discriminant_analysis": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LinearDiscriminantAnalysis(
                        solver="lsqr",
                        shrinkage="auto",
                    ),
                ),
            ]
        ),
    }


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    dataframe, feature_list = load_inputs()
    features, target = prepare_features(
        dataframe,
        feature_list,
    )

    (
        x_train,
        x_validation,
        x_test,
        y_train,
        y_validation,
        y_test,
    ) = split_by_time(features, target)

    results = []
    prediction_frame = pd.DataFrame(
        {"actual": y_test.reset_index(drop=True)}
    )

    for name, model in build_models().items():
        print(f"\nTraining {name}...")
        started = time.perf_counter()

        model.fit(x_train, y_train)

        seconds = time.perf_counter() - started

        validation_probabilities = model.predict_proba(
            x_validation
        )[:, 1]

        threshold = choose_threshold(
            y_validation,
            validation_probabilities,
        )

        test_probabilities = model.predict_proba(
            x_test
        )[:, 1]

        result = evaluate(
            name=name,
            y_true=y_test,
            probabilities=test_probabilities,
            threshold=threshold,
            seconds=seconds,
        )

        results.append(result)

        joblib.dump(
            model,
            MODELS_DIR / f"{name}_baseline.joblib",
        )

        prediction_frame[
            f"{name}_probability"
        ] = test_probabilities

        print(
            f"PR-AUC={result['pr_auc']:.6f}, "
            f"ROC-AUC={result['roc_auc']:.6f}, "
            f"Precision={result['precision']:.6f}, "
            f"Recall={result['recall']:.6f}, "
            f"F1={result['f1_score']:.6f}"
        )

    comparison = pd.DataFrame(results).sort_values(
        by=["pr_auc", "f1_score"],
        ascending=False,
    )

    comparison.to_csv(RESULTS_FILE, index=False)
    prediction_frame.to_csv(PREDICTIONS_FILE, index=False)

    print(f"\nSaved results: {RESULTS_FILE}")
    print(f"Saved predictions: {PREDICTIONS_FILE}")
    print("\nStatistical baseline ranking:")
    print(
        comparison[
            [
                "model",
                "threshold",
                "pr_auc",
                "roc_auc",
                "precision",
                "recall",
                "f1_score",
                "false_positive",
                "false_negative",
                "training_seconds",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
