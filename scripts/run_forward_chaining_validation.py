from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "frix_enriched_dataset_v3.csv"
CORE_FEATURE_FILE = (
    ROOT / "models" / "milestone24_core_pretransaction_features.json"
)

RESULTS_FILE = (
    ROOT / "models" / "milestone24_forward_chaining_results.csv"
)
SUMMARY_FILE = (
    ROOT / "docs" / "milestone24_forward_chaining_summary.md"
)

TARGET = "isFraud"
RANDOM_STATE = 42

BASE_FEATURES = {
    "amount",
    "oldbalanceOrg",
    "oldbalanceDest",
    "is_high_risk_type",
}

GRAPH_FEATURES = {
    "possible_mule_receiver_v2",
    "sender_out_degree_prior",
    "receiver_in_degree_prior",
    "receiver_total_amount_prior",
    "receiver_avg_amount_prior",
    "receiver_high_risk_txn_count_prior",
    "funnel_alert_v2",
}

FOLDS = [
    (1, 0.50, 0.60),
    (2, 0.60, 0.70),
    (3, 0.70, 0.80),
]


def load_inputs() -> tuple[pd.DataFrame, list[str]]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(DATA_FILE)

    if not CORE_FEATURE_FILE.exists():
        raise FileNotFoundError(CORE_FEATURE_FILE)

    print("Loading dataset...")
    dataframe = pd.read_csv(DATA_FILE)

    print("Loading approved core feature list...")
    core_features = json.loads(
        CORE_FEATURE_FILE.read_text(encoding="utf-8")
    )

    print(f"Rows: {len(dataframe):,}")
    print(f"Approved core features: {len(core_features):,}")
    print("Latest 20% remains excluded from all folds.")

    return dataframe, core_features


def prepare_matrix(
    dataframe: pd.DataFrame,
    core_features: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    source_features = [
        feature
        for feature in core_features
        if not feature.startswith("type_")
    ]

    features = dataframe[source_features].copy()

    if "type" in features.columns:
        features = pd.get_dummies(
            features,
            columns=["type"],
            prefix="type",
            dtype=np.int8,
        )

    for feature in core_features:
        if feature not in features.columns:
            features[feature] = 0

    features = features[core_features]

    if features.isna().any().any():
        raise ValueError("Feature matrix contains missing values.")

    target = dataframe[TARGET].astype(np.int8)

    return features, target


def build_feature_sets(
    core_features: list[str],
) -> dict[str, list[str]]:
    type_features = {
        feature
        for feature in core_features
        if feature.startswith("type_")
    }

    base_only = sorted(BASE_FEATURES | type_features)
    base_plus_graph = sorted(
        BASE_FEATURES | type_features | GRAPH_FEATURES
    )

    for name, selected in {
        "base_only": base_only,
        "base_plus_graph": base_plus_graph,
    }.items():
        missing = sorted(set(selected) - set(core_features))
        if missing:
            raise ValueError(
                f"{name} uses features outside core list: {missing}"
            )

    return {
        "base_only": base_only,
        "base_plus_graph": base_plus_graph,
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

    return float(thresholds[int(np.argmax(f1_values))])


def build_model(y_train: pd.Series) -> XGBClassifier:
    negatives = int((y_train == 0).sum())
    positives = int((y_train == 1).sum())

    if positives == 0:
        raise ValueError("Training fold contains no fraud examples.")

    scale_pos_weight = negatives / positives

    return XGBClassifier(
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
    )


def evaluate_fold(
    fold_number: int,
    feature_set_name: str,
    selected_features: list[str],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_validation: pd.DataFrame,
    y_validation: pd.Series,
) -> dict[str, object]:
    print(
        f"\nFold {fold_number} — {feature_set_name} "
        f"({len(selected_features)} features)"
    )
    print(
        f"Train rows: {len(x_train):,}, "
        f"fraud: {int(y_train.sum()):,}"
    )
    print(
        f"Validation rows: {len(x_validation):,}, "
        f"fraud: {int(y_validation.sum()):,}"
    )

    if y_validation.sum() == 0:
        raise ValueError(
            f"Fold {fold_number} validation contains no fraud."
        )

    model = build_model(y_train)

    started = time.perf_counter()
    model.fit(
        x_train[selected_features],
        y_train,
    )
    training_seconds = time.perf_counter() - started

    probabilities = model.predict_proba(
        x_validation[selected_features]
    )[:, 1]

    threshold = choose_threshold(
        y_validation,
        probabilities,
    )

    predictions = (
        probabilities >= threshold
    ).astype(np.int8)

    tn, fp, fn, tp = confusion_matrix(
        y_validation,
        predictions,
        labels=[0, 1],
    ).ravel()

    result = {
        "fold": fold_number,
        "feature_set": feature_set_name,
        "feature_count": len(selected_features),
        "train_rows": len(x_train),
        "validation_rows": len(x_validation),
        "train_fraud": int(y_train.sum()),
        "validation_fraud": int(y_validation.sum()),
        "threshold": threshold,
        "pr_auc": average_precision_score(
            y_validation,
            probabilities,
        ),
        "roc_auc": roc_auc_score(
            y_validation,
            probabilities,
        ),
        "precision": precision_score(
            y_validation,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_validation,
            predictions,
            zero_division=0,
        ),
        "f1_score": f1_score(
            y_validation,
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
        f"PR-AUC={result['pr_auc']:.6f}, "
        f"ROC-AUC={result['roc_auc']:.6f}, "
        f"Precision={result['precision']:.6f}, "
        f"Recall={result['recall']:.6f}, "
        f"F1={result['f1_score']:.6f}"
    )

    return result


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby("feature_set")
        .agg(
            folds=("fold", "count"),
            mean_pr_auc=("pr_auc", "mean"),
            std_pr_auc=("pr_auc", "std"),
            min_pr_auc=("pr_auc", "min"),
            max_pr_auc=("pr_auc", "max"),
            mean_roc_auc=("roc_auc", "mean"),
            mean_precision=("precision", "mean"),
            mean_recall=("recall", "mean"),
            mean_f1=("f1_score", "mean"),
            std_f1=("f1_score", "std"),
        )
        .reset_index()
        .sort_values(
            ["mean_pr_auc", "mean_f1"],
            ascending=False,
        )
    )


def build_markdown(
    results: pd.DataFrame,
    summary: pd.DataFrame,
) -> str:
    lines = [
        "# Milestone 24G — Forward-Chaining Validation",
        "",
        "The latest 20% of the dataset was excluded. "
        "Each fold trains on an expanding historical window "
        "and validates on the immediately following period.",
        "",
        "## Fold results",
        "",
        "| Fold | Feature set | Train fraud | Validation fraud | PR-AUC | ROC-AUC | Precision | Recall | F1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in results.itertuples(index=False):
        lines.append(
            f"| {row.fold} | {row.feature_set} | "
            f"{row.train_fraud} | {row.validation_fraud} | "
            f"{row.pr_auc:.6f} | {row.roc_auc:.6f} | "
            f"{row.precision:.6f} | {row.recall:.6f} | "
            f"{row.f1_score:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Stability summary",
            "",
            "| Feature set | Mean PR-AUC | Std PR-AUC | Min PR-AUC | Mean F1 | Std F1 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.feature_set} | "
            f"{row.mean_pr_auc:.6f} | "
            f"{row.std_pr_auc:.6f} | "
            f"{row.min_pr_auc:.6f} | "
            f"{row.mean_f1:.6f} | "
            f"{row.std_f1:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Decision rule",
            "",
            "Prefer the feature set with stronger average PR-AUC, "
            "lower fold-to-fold variance, and acceptable recall. "
            "A single strong fold is not sufficient.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    dataframe, core_features = load_inputs()

    features, target = prepare_matrix(
        dataframe,
        core_features,
    )

    feature_sets = build_feature_sets(core_features)

    results: list[dict[str, object]] = []
    total_rows = len(features)

    for fold, train_fraction, validation_fraction in FOLDS:
        train_end = int(total_rows * train_fraction)
        validation_end = int(
            total_rows * validation_fraction
        )

        x_train = features.iloc[:train_end]
        y_train = target.iloc[:train_end]

        x_validation = features.iloc[
            train_end:validation_end
        ]
        y_validation = target.iloc[
            train_end:validation_end
        ]

        for feature_set_name, selected_features in (
            feature_sets.items()
        ):
            results.append(
                evaluate_fold(
                    fold_number=fold,
                    feature_set_name=feature_set_name,
                    selected_features=selected_features,
                    x_train=x_train,
                    y_train=y_train,
                    x_validation=x_validation,
                    y_validation=y_validation,
                )
            )

    results_df = pd.DataFrame(results).sort_values(
        ["fold", "feature_set"]
    )

    stability_summary = summarize(results_df)

    results_df.to_csv(
        RESULTS_FILE,
        index=False,
    )

    SUMMARY_FILE.write_text(
        build_markdown(
            results_df,
            stability_summary,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved results: {RESULTS_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")

    print("\nForward-chaining stability summary:")
    print(stability_summary.to_string(index=False))


if __name__ == "__main__":
    main()
