from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "frix_enriched_dataset_v3.csv"
FEATURE_FILE = (
    PROJECT_ROOT
    / "models"
    / "milestone24_core_pretransaction_features.json"
)
MODELS_DIR = PROJECT_ROOT / "models"

RESULTS_FILE = MODELS_DIR / "milestone24_core_model_v1_comparison.csv"
PREDICTIONS_FILE = (
    MODELS_DIR / "milestone24_core_model_v1_validation_predictions.csv"
)
METADATA_FILE = MODELS_DIR / "milestone24_core_model_v1_metadata.json"

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

    print("Loading approved 20-feature core list...")
    feature_list = json.loads(
        FEATURE_FILE.read_text(encoding="utf-8")
    )

    print(f"Rows: {len(dataframe):,}")
    print(f"Approved core features: {len(feature_list):,}")

    return dataframe, feature_list


def prepare_features(
    dataframe: pd.DataFrame,
    feature_list: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    base_features = [
        feature
        for feature in feature_list
        if not feature.startswith("type_")
    ]

    missing = [
        feature
        for feature in base_features
        if feature not in dataframe.columns
    ]

    if missing:
        raise ValueError(f"Missing core features: {missing}")

    features = dataframe[base_features].copy()

    if "type" in features.columns:
        features = pd.get_dummies(
            features,
            columns=["type"],
            prefix="type",
            dtype=np.int8,
        )

    for feature in feature_list:
        if feature not in features.columns:
            features[feature] = 0

    features = features[feature_list]

    non_numeric = features.select_dtypes(
        exclude=[np.number, "bool"]
    ).columns.tolist()

    if non_numeric:
        raise ValueError(
            f"Unexpected non-numeric features: {non_numeric}"
        )

    if features.isna().any().any():
        raise ValueError("Core feature matrix contains missing values.")

    target = dataframe[TARGET].astype(np.int8)

    print(f"Final core feature count: {len(features.columns):,}")

    return features, target


def development_split(
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

    y_train = target.iloc[:train_end].copy()
    y_validation = target.iloc[train_end:validation_end].copy()

    print("Chronological development split created.")
    print(
        f"Train: {len(x_train):,} rows, "
        f"{int(y_train.sum()):,} fraud"
    )
    print(
        f"Validation: {len(x_validation):,} rows, "
        f"{int(y_validation.sum()):,} fraud"
    )
    print(
        "Latest 20% is excluded from this core-model fit and "
        "will be handled later under final evaluation governance."
    )

    return x_train, x_validation, y_train, y_validation


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
    model_name: str,
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
    training_seconds: float,
) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(np.int8)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "model": model_name,
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
        "training_seconds": round(training_seconds, 2),
    }


def build_models(
    y_train: pd.Series,
) -> dict[str, object]:
    negatives = int((y_train == 0).sum())
    positives = int((y_train == 1).sum())
    scale_pos_weight = negatives / positives

    print(
        "Class imbalance ratio "
        f"(negative/positive): {scale_pos_weight:.2f}"
    )

    return {
        "logistic_regression_core_v1": Pipeline(
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
        "random_forest_core_v1": RandomForestClassifier(
            n_estimators=250,
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "xgboost_core_v1": XGBClassifier(
            n_estimators=350,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=2,
            reg_lambda=1.0,
            objective="binary:logistic",
            eval_metric="aucpr",
            scale_pos_weight=scale_pos_weight,
            tree_method="hist",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    dataframe, feature_list = load_inputs()
    features, target = prepare_features(
        dataframe,
        feature_list,
    )

    x_train, x_validation, y_train, y_validation = (
        development_split(features, target)
    )

    results: list[dict[str, object]] = []
    prediction_frame = pd.DataFrame(
        {"actual": y_validation.reset_index(drop=True)}
    )

    thresholds: dict[str, float] = {}

    for model_name, model in build_models(y_train).items():
        print(f"\nTraining {model_name}...")
        started = time.perf_counter()

        model.fit(x_train, y_train)

        training_seconds = time.perf_counter() - started

        probabilities = model.predict_proba(
            x_validation
        )[:, 1]

        threshold = choose_threshold(
            y_validation,
            probabilities,
        )

        thresholds[model_name] = threshold

        result = evaluate(
            model_name=model_name,
            y_true=y_validation,
            probabilities=probabilities,
            threshold=threshold,
            training_seconds=training_seconds,
        )
        results.append(result)

        model_path = MODELS_DIR / f"{model_name}.joblib"
        joblib.dump(model, model_path)

        prediction_frame[
            f"{model_name}_probability"
        ] = probabilities

        print(f"Saved model: {model_path}")
        print(
            f"PR-AUC={result['pr_auc']:.6f}, "
            f"ROC-AUC={result['roc_auc']:.6f}, "
            f"Precision={result['precision']:.6f}, "
            f"Recall={result['recall']:.6f}, "
            f"F1={result['f1_score']:.6f}"
        )

    comparison = pd.DataFrame(results).sort_values(
        by=["pr_auc", "f1_score", "recall"],
        ascending=False,
    ).reset_index(drop=True)

    comparison.to_csv(RESULTS_FILE, index=False)
    prediction_frame.to_csv(PREDICTIONS_FILE, index=False)

    metadata = {
        "dataset": str(DATA_FILE),
        "feature_file": str(FEATURE_FILE),
        "feature_count": len(feature_list),
        "features": feature_list,
        "train_fraction": TRAIN_FRACTION,
        "validation_fraction": VALIDATION_FRACTION,
        "latest_fraction_excluded": (
            1 - TRAIN_FRACTION - VALIDATION_FRACTION
        ),
        "thresholds": thresholds,
        "ranking_metric": "pr_auc",
        "status": "development_core_benchmark",
    }

    METADATA_FILE.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved comparison: {RESULTS_FILE}")
    print(f"Saved predictions: {PREDICTIONS_FILE}")
    print(f"Saved metadata: {METADATA_FILE}")

    print("\nFRIX Core Model v1 ranking:")
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

    champion = comparison.iloc[0]

    print("\nCore Model v1 training completed.")
    print(f"Development champion: {champion['model']}")
    print(f"Validation PR-AUC: {champion['pr_auc']:.6f}")


if __name__ == "__main__":
    main()
