from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
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
from xgboost import XGBClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "frix_enriched_dataset_v3.csv"
MODELS_DIR = PROJECT_ROOT / "models"

RESULTS_FILE = MODELS_DIR / "milestone24_strict_pretransaction_comparison.csv"
FEATURES_FILE = MODELS_DIR / "milestone24_strict_pretransaction_features.json"
PREDICTIONS_FILE = MODELS_DIR / "milestone24_strict_pretransaction_test_predictions.csv"

TARGET = "isFraud"
RANDOM_STATE = 42

TRAIN_FRACTION = 0.60
VALIDATION_FRACTION = 0.20

EXCLUDED_COLUMNS = {
    TARGET,
    "nameOrig",
    "nameDest",
    "isFlaggedFraud",
    "sender_txn_count",
    "receiver_txn_count",
    "risk_score_v1",
    "rule_alert_v1",
    "is_large_amount",
    "newbalanceOrig",
    "newbalanceDest",
    "origin_balance_error",
    "dest_balance_error",
    "sender_emptied_account",
}


def load_dataset() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing dataset: {DATA_FILE}")

    print(f"Loading dataset: {DATA_FILE}")
    dataframe = pd.read_csv(DATA_FILE)

    print(f"Rows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns):,}")
    print(f"Fraud rows: {int(dataframe[TARGET].sum()):,}")

    return dataframe


def prepare_features(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    missing = sorted(
        column
        for column in EXCLUDED_COLUMNS
        if column not in dataframe.columns
    )

    if missing:
        raise ValueError(f"Expected columns are missing: {missing}")

    print("Building strict pre-transaction feature matrix...")

    feature_columns = [
        column
        for column in dataframe.columns
        if column not in EXCLUDED_COLUMNS
    ]

    features = dataframe[feature_columns].copy()
    target = dataframe[TARGET].astype(np.int8)

    if "type" in features.columns:
        features = pd.get_dummies(
            features,
            columns=["type"],
            prefix="type",
            dtype=np.int8,
        )

    non_numeric = features.select_dtypes(
        exclude=[np.number, "bool"]
    ).columns.tolist()

    if non_numeric:
        raise ValueError(
            f"Unexpected non-numeric features: {non_numeric}"
        )

    if features.isna().any().any():
        raise ValueError("Feature matrix contains missing values.")

    print("Excluded columns:")
    for column in sorted(EXCLUDED_COLUMNS):
        print(f"  - {column}")

    print(f"Strict feature count: {len(features.columns):,}")

    return features, target


def time_split(
    features: pd.DataFrame,
    target: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.Series,
]:
    train_end = int(len(features) * TRAIN_FRACTION)
    validation_end = int(
        len(features) * (TRAIN_FRACTION + VALIDATION_FRACTION)
    )

    x_train = features.iloc[:train_end].copy()
    x_validation = features.iloc[train_end:validation_end].copy()
    x_test = features.iloc[validation_end:].copy()

    y_train = target.iloc[:train_end].copy()
    y_validation = target.iloc[train_end:validation_end].copy()
    y_test = target.iloc[validation_end:].copy()

    print("Time-based train/validation/test split created.")
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

    for split_name, labels in {
        "train": y_train,
        "validation": y_validation,
        "test": y_test,
    }.items():
        if labels.sum() == 0:
            raise ValueError(
                f"Fraud class missing from {split_name} split."
            )

    return (
        x_train,
        x_validation,
        x_test,
        y_train,
        y_validation,
        y_test,
    )


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
        "random_forest_strict_v1": RandomForestClassifier(
            n_estimators=250,
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "xgboost_strict_v1": XGBClassifier(
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
        "lightgbm_strict_v1": LGBMClassifier(
            n_estimators=350,
            num_leaves=63,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=1.0,
            scale_pos_weight=scale_pos_weight,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            verbosity=-1,
        ),
    }


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

    best_index = int(np.argmax(f1_values))
    return float(thresholds[best_index])


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
        "roc_auc": roc_auc_score(y_true, probabilities),
        "pr_auc": average_precision_score(
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


def train_models(
    models: dict[str, object],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_validation: pd.DataFrame,
    y_validation: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    results: list[dict[str, object]] = []
    prediction_frame = pd.DataFrame(
        {
            "actual": y_test.reset_index(drop=True),
        }
    )

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        started = time.perf_counter()

        model.fit(x_train, y_train)

        training_seconds = time.perf_counter() - started

        validation_probabilities = model.predict_proba(
            x_validation
        )[:, 1]

        threshold = choose_threshold(
            y_validation,
            validation_probabilities,
        )

        print(
            f"Validation-selected threshold: {threshold:.6f}"
        )

        test_probabilities = model.predict_proba(x_test)[:, 1]

        result = evaluate(
            model_name=model_name,
            y_true=y_test,
            probabilities=test_probabilities,
            threshold=threshold,
            training_seconds=training_seconds,
        )

        results.append(result)

        model_file = MODELS_DIR / f"{model_name}.joblib"
        joblib.dump(model, model_file)

        prediction_frame[f"{model_name}_probability"] = (
            test_probabilities
        )

        print(f"Saved model: {model_file}")
        print(
            f"PR-AUC={result['pr_auc']:.6f}, "
            f"ROC-AUC={result['roc_auc']:.6f}, "
            f"Brier={result['brier_score']:.6f}"
        )
        print(
            f"Precision={result['precision']:.6f}, "
            f"Recall={result['recall']:.6f}, "
            f"F1={result['f1_score']:.6f}"
        )
        print(
            f"Confusion matrix: "
            f"TN={result['true_negative']}, "
            f"FP={result['false_positive']}, "
            f"FN={result['false_negative']}, "
            f"TP={result['true_positive']}"
        )

    comparison = pd.DataFrame(results).sort_values(
        by=["pr_auc", "f1_score", "recall"],
        ascending=False,
    ).reset_index(drop=True)

    comparison.to_csv(RESULTS_FILE, index=False)
    prediction_frame.to_csv(PREDICTIONS_FILE, index=False)

    print(f"\nSaved comparison: {RESULTS_FILE}")
    print(f"Saved test predictions: {PREDICTIONS_FILE}")

    print("\nStrict pre-transaction ranking:")
    print(
        comparison[
            [
                "model",
                "threshold",
                "pr_auc",
                "roc_auc",
                "brier_score",
                "precision",
                "recall",
                "f1_score",
                "false_positive",
                "false_negative",
                "training_seconds",
            ]
        ].to_string(index=False)
    )

    return comparison


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    dataframe = load_dataset()
    features, target = prepare_features(dataframe)

    FEATURES_FILE.write_text(
        json.dumps(features.columns.tolist(), indent=2),
        encoding="utf-8",
    )
    print(f"Saved feature list: {FEATURES_FILE}")

    (
        x_train,
        x_validation,
        x_test,
        y_train,
        y_validation,
        y_test,
    ) = time_split(features, target)

    comparison = train_models(
        models=build_models(y_train),
        x_train=x_train,
        y_train=y_train,
        x_validation=x_validation,
        y_validation=y_validation,
        x_test=x_test,
        y_test=y_test,
    )

    champion = comparison.iloc[0]

    print("\nStrict pre-transaction training completed.")
    print(f"Provisional champion: {champion['model']}")
    print(f"Champion PR-AUC: {champion['pr_auc']:.6f}")
    print(
        "Next: bootstrap confidence intervals and "
        "feature-family ablation."
    )


if __name__ == "__main__":
    main()
