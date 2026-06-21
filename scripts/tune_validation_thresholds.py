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
)
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "frix_enriched_dataset_v3.csv"
CORE_FEATURE_FILE = ROOT / "models" / "milestone24_core_pretransaction_features.json"
BEST_CONFIG_FILE = ROOT / "models" / "milestone24_xgb_best_configs.json"

THRESHOLD_RESULTS_FILE = ROOT / "models" / "milestone24_threshold_tuning_results.csv"
OOF_PREDICTIONS_FILE = ROOT / "models" / "milestone24_threshold_oof_predictions.csv"
SUMMARY_FILE = ROOT / "docs" / "milestone24_threshold_tuning_summary.md"

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

RECALL_TARGETS = [0.50, 0.70]


def load_inputs():
    for path in [DATA_FILE, CORE_FEATURE_FILE, BEST_CONFIG_FILE]:
        if not path.exists():
            raise FileNotFoundError(path)

    print("Loading dataset...")
    dataframe = pd.read_csv(DATA_FILE)

    core_features = json.loads(
        CORE_FEATURE_FILE.read_text(encoding="utf-8")
    )
    best_configs = json.loads(
        BEST_CONFIG_FILE.read_text(encoding="utf-8")
    )

    print(f"Rows: {len(dataframe):,}")
    print(f"Approved core features: {len(core_features):,}")
    print("Latest 20% remains excluded from threshold tuning.")

    return dataframe, core_features, best_configs


def prepare_matrix(dataframe, core_features):
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


def build_feature_sets(core_features):
    type_features = {
        feature
        for feature in core_features
        if feature.startswith("type_")
    }

    return {
        "base_only": sorted(BASE_FEATURES | type_features),
        "base_plus_graph": sorted(
            BASE_FEATURES | type_features | GRAPH_FEATURES
        ),
    }


def build_model(y_train, config):
    negatives = int((y_train == 0).sum())
    positives = int((y_train == 1).sum())

    if positives == 0:
        raise ValueError("Training fold contains no fraud examples.")

    return XGBClassifier(
        n_estimators=int(config.get("n_estimators", 350)),
        max_depth=int(config["max_depth"]),
        learning_rate=float(config["learning_rate"]),
        min_child_weight=float(config.get("min_child_weight", 2.0)),
        subsample=float(config.get("subsample", 0.85)),
        colsample_bytree=float(config.get("colsample_bytree", 0.85)),
        reg_lambda=float(config["reg_lambda"]),
        objective="binary:logistic",
        eval_metric="aucpr",
        scale_pos_weight=negatives / positives,
        tree_method="hist",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )


def generate_oof_predictions(
    feature_set_name,
    selected_features,
    config,
    features,
    target,
):
    total_rows = len(features)
    frames = []

    for fold_number, train_fraction, validation_fraction in FOLDS:
        train_end = int(total_rows * train_fraction)
        validation_end = int(total_rows * validation_fraction)

        x_train = features.iloc[:train_end][selected_features]
        y_train = target.iloc[:train_end]

        x_validation = features.iloc[
            train_end:validation_end
        ][selected_features]
        y_validation = target.iloc[
            train_end:validation_end
        ]

        print(f"\n{feature_set_name} — fold {fold_number}")
        print(
            f"Train fraud: {int(y_train.sum()):,} | "
            f"Validation fraud: {int(y_validation.sum()):,}"
        )

        model = build_model(y_train, config)

        started = time.perf_counter()
        model.fit(x_train, y_train)
        elapsed = time.perf_counter() - started

        probabilities = model.predict_proba(x_validation)[:, 1]

        print(
            f"PR-AUC="
            f"{average_precision_score(y_validation, probabilities):.6f} "
            f"| Training seconds={elapsed:.2f}"
        )

        frames.append(
            pd.DataFrame(
                {
                    "feature_set": feature_set_name,
                    "fold": fold_number,
                    "row_index": np.arange(
                        train_end,
                        validation_end,
                    ),
                    "actual": y_validation.to_numpy(),
                    "probability": probabilities,
                }
            )
        )

    return pd.concat(frames, ignore_index=True)


def metric_row(
    feature_set,
    profile,
    threshold,
    y_true,
    probabilities,
):
    predictions = (
        probabilities >= threshold
    ).astype(np.int8)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "feature_set": feature_set,
        "profile": profile,
        "threshold": float(threshold),
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
        "alert_count": int(predictions.sum()),
        "fraud_count": int(y_true.sum()),
    }


def select_thresholds(feature_set, prediction_frame):
    y_true = prediction_frame["actual"].to_numpy()
    probabilities = prediction_frame["probability"].to_numpy()

    precision, recall, thresholds = precision_recall_curve(
        y_true,
        probabilities,
    )

    precision = precision[:-1]
    recall = recall[:-1]

    denominator = precision + recall
    f1_values = np.divide(
        2 * precision * recall,
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0,
    )

    rows = []

    best_f1_index = int(np.argmax(f1_values))
    rows.append(
        metric_row(
            feature_set,
            "max_f1",
            float(thresholds[best_f1_index]),
            y_true,
            probabilities,
        )
    )

    for target_recall in RECALL_TARGETS:
        eligible = np.where(recall >= target_recall)[0]

        if len(eligible) == 0:
            continue

        best_index = eligible[
            int(np.argmax(precision[eligible]))
        ]

        rows.append(
            metric_row(
                feature_set,
                f"recall_at_least_{target_recall:.2f}",
                float(thresholds[best_index]),
                y_true,
                probabilities,
            )
        )

    return rows


def build_summary(results):
    lines = [
        "# Milestone 24I — Validation-Only Threshold Tuning",
        "",
        "Thresholds were selected using pooled out-of-fold predictions "
        "from the three forward-chaining development folds.",
        "",
        "The latest 20% of the dataset was not used.",
        "",
        "## Selected operating profiles",
        "",
        "| Feature set | Profile | Threshold | Precision | Recall | F1 | Alerts | TP | FP | FN |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in results.itertuples(index=False):
        lines.append(
            f"| {row.feature_set} | {row.profile} | "
            f"{row.threshold:.6f} | "
            f"{row.precision:.6f} | "
            f"{row.recall:.6f} | "
            f"{row.f1_score:.6f} | "
            f"{row.alert_count} | "
            f"{row.true_positive} | "
            f"{row.false_positive} | "
            f"{row.false_negative} |"
        )

    lines.extend(
        [
            "",
            "## Governance",
            "",
            "- `max_f1` is the balanced development operating point.",
            "- Recall-target profiles trade more alerts for fewer missed frauds.",
            "- Thresholds remain provisional until calibration and final evaluation.",
            "- No threshold was selected using the excluded latest 20%.",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    dataframe, core_features, best_configs = load_inputs()

    features, target = prepare_matrix(
        dataframe,
        core_features,
    )

    feature_sets = build_feature_sets(core_features)

    all_predictions = []
    threshold_rows = []

    for feature_set_name, selected_features in feature_sets.items():
        prediction_frame = generate_oof_predictions(
            feature_set_name,
            selected_features,
            best_configs[feature_set_name],
            features,
            target,
        )

        all_predictions.append(prediction_frame)
        threshold_rows.extend(
            select_thresholds(
                feature_set_name,
                prediction_frame,
            )
        )

    predictions = pd.concat(
        all_predictions,
        ignore_index=True,
    )

    results = pd.DataFrame(threshold_rows).sort_values(
        ["feature_set", "profile"]
    )

    predictions.to_csv(
        OOF_PREDICTIONS_FILE,
        index=False,
    )
    results.to_csv(
        THRESHOLD_RESULTS_FILE,
        index=False,
    )
    SUMMARY_FILE.write_text(
        build_summary(results),
        encoding="utf-8",
    )

    print(f"\nSaved thresholds: {THRESHOLD_RESULTS_FILE}")
    print(f"Saved OOF predictions: {OOF_PREDICTIONS_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")

    print("\nSelected validation-only thresholds:")
    print(
        results[
            [
                "feature_set",
                "profile",
                "threshold",
                "precision",
                "recall",
                "f1_score",
                "alert_count",
                "true_positive",
                "false_positive",
                "false_negative",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
