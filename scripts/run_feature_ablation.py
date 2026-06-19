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

RESULTS_FILE = ROOT / "models" / "milestone24_feature_ablation_results.csv"
SUMMARY_FILE = ROOT / "docs" / "milestone24_feature_ablation_summary.md"

TARGET = "isFraud"
TRAIN_FRACTION = 0.60
VALIDATION_FRACTION = 0.20
RANDOM_STATE = 42


BASE_FEATURES = {
    "amount",
    "oldbalanceOrg",
    "oldbalanceDest",
    "is_high_risk_type",
}

TEMPORAL_FEATURES = {
    "sender_prior_txn_count",
    "receiver_prior_txn_count",
    "sender_prior_volume",
    "receiver_prior_volume",
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

    return dataframe, core_features


def prepare_full_matrix(
    dataframe: pd.DataFrame,
    core_features: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    base_columns = [
        feature
        for feature in core_features
        if not feature.startswith("type_")
    ]

    features = dataframe[base_columns].copy()

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


def split_development_data(
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

    print(
        f"Train: {len(x_train):,} rows, "
        f"{int(y_train.sum()):,} fraud"
    )
    print(
        f"Validation: {len(x_validation):,} rows, "
        f"{int(y_validation.sum()):,} fraud"
    )
    print("Latest 20% remains excluded.")

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


def build_feature_sets(
    core_features: list[str],
) -> dict[str, list[str]]:
    type_features = {
        feature
        for feature in core_features
        if feature.startswith("type_")
    }

    base = BASE_FEATURES | type_features
    temporal = TEMPORAL_FEATURES
    graph = GRAPH_FEATURES

    feature_sets = {
        "base_only": sorted(base),
        "base_plus_temporal": sorted(base | temporal),
        "base_plus_graph": sorted(base | graph),
        "full_core": list(core_features),
    }

    for name, features in feature_sets.items():
        missing = sorted(set(features) - set(core_features))
        if missing:
            raise ValueError(
                f"{name} contains features outside core list: {missing}"
            )

    return feature_sets


def train_and_evaluate(
    name: str,
    selected_features: list[str],
    x_train: pd.DataFrame,
    x_validation: pd.DataFrame,
    y_train: pd.Series,
    y_validation: pd.Series,
) -> dict[str, object]:
    negatives = int((y_train == 0).sum())
    positives = int((y_train == 1).sum())
    scale_pos_weight = negatives / positives

    model = XGBClassifier(
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

    print(
        f"\nTraining {name} "
        f"with {len(selected_features)} features..."
    )

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
        "feature_set": name,
        "feature_count": len(selected_features),
        "features": "|".join(selected_features),
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


def build_summary(results: pd.DataFrame) -> str:
    ranked = results.sort_values(
        by="pr_auc",
        ascending=False,
    ).reset_index(drop=True)

    base_pr_auc = float(
        results.loc[
            results["feature_set"] == "base_only",
            "pr_auc",
        ].iloc[0]
    )

    lines = [
        "# Milestone 24F — Feature-Family Ablation",
        "",
        "All experiments use the same XGBoost configuration, "
        "chronological training period, and validation period.",
        "",
        "## Results",
        "",
        "| Feature set | Features | PR-AUC | ROC-AUC | Precision | Recall | F1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for row in ranked.itertuples(index=False):
        lines.append(
            f"| {row.feature_set} | {row.feature_count} | "
            f"{row.pr_auc:.6f} | {row.roc_auc:.6f} | "
            f"{row.precision:.6f} | {row.recall:.6f} | "
            f"{row.f1_score:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Incremental PR-AUC versus base",
            "",
        ]
    )

    for row in ranked.itertuples(index=False):
        lift = row.pr_auc - base_pr_auc
        lines.append(
            f"- `{row.feature_set}`: {lift:+.6f}"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A positive lift indicates that the added feature family "
            "improves ranking performance over current-transaction "
            "features alone. Final conclusions still require "
            "forward-chaining validation.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    dataframe, core_features = load_inputs()

    features, target = prepare_full_matrix(
        dataframe,
        core_features,
    )

    x_train, x_validation, y_train, y_validation = (
        split_development_data(features, target)
    )

    feature_sets = build_feature_sets(core_features)

    results = []

    for name, selected_features in feature_sets.items():
        results.append(
            train_and_evaluate(
                name=name,
                selected_features=selected_features,
                x_train=x_train,
                x_validation=x_validation,
                y_train=y_train,
                y_validation=y_validation,
            )
        )

    results_df = pd.DataFrame(results).sort_values(
        by=["pr_auc", "f1_score"],
        ascending=False,
    ).reset_index(drop=True)

    results_df.to_csv(
        RESULTS_FILE,
        index=False,
    )

    SUMMARY_FILE.write_text(
        build_summary(results_df),
        encoding="utf-8",
    )

    print(f"\nSaved results: {RESULTS_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")

    print("\nFeature-family ablation ranking:")
    print(
        results_df[
            [
                "feature_set",
                "feature_count",
                "pr_auc",
                "roc_auc",
                "precision",
                "recall",
                "f1_score",
                "training_seconds",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
