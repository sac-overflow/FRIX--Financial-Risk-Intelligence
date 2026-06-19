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
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "frix_enriched_dataset_v3.csv"
MODELS_DIR = PROJECT_ROOT / "models"

RESULTS_FILE = MODELS_DIR / "milestone23_enriched_model_comparison.csv"
FEATURES_FILE = MODELS_DIR / "milestone23_feature_list.json"

TARGET = "isFraud"
TIME_COLUMN = "step"

DROP_COLUMNS = {
    TARGET,
    "nameOrig",
    "nameDest",
    "rule_alert_v1",
    "mule_alert_v1",
}

RANDOM_STATE = 42
TRAIN_FRACTION = 0.80


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
    print("Preparing features...")

    feature_columns = [
        column
        for column in dataframe.columns
        if column not in DROP_COLUMNS
    ]

    features = dataframe[feature_columns].copy()
    target = dataframe[TARGET].astype(int)

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

    print(f"Final feature count: {len(features.columns):,}")

    return features, target


def time_based_split(
    features: pd.DataFrame,
    target: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    split_index = int(len(features) * TRAIN_FRACTION)

    x_train = features.iloc[:split_index].copy()
    x_test = features.iloc[split_index:].copy()
    y_train = target.iloc[:split_index].copy()
    y_test = target.iloc[split_index:].copy()

    print("Time-based split created.")
    print(f"Train rows: {len(x_train):,}")
    print(f"Test rows: {len(x_test):,}")
    print(f"Train fraud rows: {int(y_train.sum()):,}")
    print(f"Test fraud rows: {int(y_test.sum()):,}")

    if y_train.sum() == 0 or y_test.sum() == 0:
        raise ValueError(
            "Fraud class missing from train or test split."
        )

    return x_train, x_test, y_train, y_test


def build_models(
    y_train: pd.Series,
) -> dict[str, object]:
    negative_count = int((y_train == 0).sum())
    positive_count = int((y_train == 1).sum())
    scale_pos_weight = negative_count / positive_count

    print(
        "Class imbalance ratio "
        f"(negative/positive): {scale_pos_weight:.2f}"
    )

    return {
        "random_forest_v2": RandomForestClassifier(
            n_estimators=250,
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "xgboost_v2": XGBClassifier(
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
        "lightgbm_v2": LGBMClassifier(
            n_estimators=350,
            max_depth=-1,
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


def evaluate_model(
    model_name: str,
    model: object,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    training_seconds: float,
) -> dict[str, object]:
    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    ).ravel()

    result = {
        "model": model_name,
        "roc_auc": roc_auc_score(y_test, probabilities),
        "pr_auc": average_precision_score(
            y_test,
            probabilities,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1_score": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "training_seconds": round(training_seconds, 2),
    }

    print(
        f"{model_name}: "
        f"PR-AUC={result['pr_auc']:.6f}, "
        f"ROC-AUC={result['roc_auc']:.6f}, "
        f"Precision={result['precision']:.6f}, "
        f"Recall={result['recall']:.6f}, "
        f"F1={result['f1_score']:.6f}"
    )

    return result


def save_feature_list(feature_columns: list[str]) -> None:
    FEATURES_FILE.write_text(
        json.dumps(feature_columns, indent=2),
        encoding="utf-8",
    )
    print(f"Saved feature list: {FEATURES_FILE}")


def train_and_save_models(
    models: dict[str, object],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    results: list[dict[str, object]] = []

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        start_time = time.perf_counter()

        model.fit(x_train, y_train)

        training_seconds = time.perf_counter() - start_time

        model_file = MODELS_DIR / f"{model_name}.joblib"
        joblib.dump(model, model_file)

        print(
            f"Saved model: {model_file} "
            f"({training_seconds:.2f} seconds)"
        )

        result = evaluate_model(
            model_name=model_name,
            model=model,
            x_test=x_test,
            y_test=y_test,
            training_seconds=training_seconds,
        )
        results.append(result)

    comparison = pd.DataFrame(results)
    comparison = comparison.sort_values(
        by=["pr_auc", "recall", "precision"],
        ascending=False,
    ).reset_index(drop=True)

    comparison.to_csv(RESULTS_FILE, index=False)

    print(f"\nSaved comparison: {RESULTS_FILE}")
    print("\nModel ranking by PR-AUC:")
    print(
        comparison[
            [
                "model",
                "pr_auc",
                "roc_auc",
                "precision",
                "recall",
                "f1_score",
                "training_seconds",
            ]
        ].to_string(index=False)
    )

    return comparison


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    dataframe = load_dataset()
    features, target = prepare_features(dataframe)

    save_feature_list(features.columns.tolist())

    x_train, x_test, y_train, y_test = time_based_split(
        features,
        target,
    )

    models = build_models(y_train)

    comparison = train_and_save_models(
        models=models,
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )

    champion = comparison.iloc[0]

    print(
        "\nMilestone 23 training completed."
        f"\nCurrent champion: {champion['model']}"
        f"\nChampion PR-AUC: {champion['pr_auc']:.6f}"
    )


if __name__ == "__main__":
    main()
