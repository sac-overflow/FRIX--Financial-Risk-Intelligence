from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "frix_enriched_dataset_v3.csv"
CORE_FEATURE_FILE = ROOT / "models" / "milestone24_core_pretransaction_features.json"
BEST_CONFIG_FILE = ROOT / "models" / "milestone24_xgb_best_configs.json"
THRESHOLD_FILE = ROOT / "models" / "milestone24_threshold_tuning_results.csv"

RESULTS_FILE = ROOT / "models" / "milestone24_holdout_bootstrap_results.csv"
PREDICTIONS_FILE = ROOT / "models" / "milestone24_holdout_predictions.csv"
SUMMARY_FILE = ROOT / "docs" / "milestone24_holdout_bootstrap_summary.md"

TARGET = "isFraud"
RANDOM_STATE = 42
BOOTSTRAP_ITERATIONS = 1000
TRAIN_END_FRACTION = 0.80

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


def load_inputs():
    for path in [
        DATA_FILE,
        CORE_FEATURE_FILE,
        BEST_CONFIG_FILE,
        THRESHOLD_FILE,
    ]:
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
    thresholds = pd.read_csv(THRESHOLD_FILE)

    print(f"Rows: {len(dataframe):,}")
    print(f"Approved core features: {len(core_features):,}")
    print("Training on first 80%; evaluating on latest 20%.")

    return dataframe, core_features, best_configs, thresholds


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
        raise ValueError("Training data contains no fraud examples.")

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


def point_metrics(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(np.int8)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "pr_auc": average_precision_score(y_true, probabilities),
        "roc_auc": roc_auc_score(y_true, probabilities),
        "brier_score": brier_score_loss(y_true, probabilities),
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
    }


def bootstrap_intervals(
    y_true,
    probabilities,
    threshold,
    iterations=BOOTSTRAP_ITERATIONS,
):
    rng = np.random.default_rng(RANDOM_STATE)
    n = len(y_true)

    metric_samples = {
        "pr_auc": [],
        "roc_auc": [],
        "precision": [],
        "recall": [],
        "f1_score": [],
        "brier_score": [],
    }

    accepted = 0
    attempts = 0
    max_attempts = iterations * 5

    while accepted < iterations and attempts < max_attempts:
        attempts += 1
        indices = rng.integers(0, n, size=n)

        sample_y = y_true[indices]
        sample_p = probabilities[indices]

        if sample_y.min() == sample_y.max():
            continue

        metrics = point_metrics(
            sample_y,
            sample_p,
            threshold,
        )

        for name in metric_samples:
            metric_samples[name].append(metrics[name])

        accepted += 1

    if accepted < iterations:
        raise RuntimeError(
            f"Only {accepted} valid bootstrap samples generated."
        )

    intervals = {}

    for name, values in metric_samples.items():
        values_array = np.asarray(values)
        intervals[name] = {
            "lower": float(np.percentile(values_array, 2.5)),
            "upper": float(np.percentile(values_array, 97.5)),
        }

    return intervals


def get_threshold(thresholds, feature_set, profile):
    matched = thresholds[
        (thresholds["feature_set"] == feature_set)
        & (thresholds["profile"] == profile)
    ]

    if len(matched) != 1:
        raise ValueError(
            f"Expected one threshold for {feature_set}/{profile}, "
            f"found {len(matched)}."
        )

    return float(matched.iloc[0]["threshold"])


def build_summary(results):
    lines = [
        "# Milestone 24J — Holdout Evaluation with Bootstrap Confidence Intervals",
        "",
        "Models were retrained on the first 80% of transactions using "
        "frozen feature sets and frozen hyperparameters. Thresholds were "
        "taken from forward-chaining development validation.",
        "",
        "The latest 20% was used only for this evaluation step.",
        "",
        "## Results",
        "",
        "| Feature set | Profile | PR-AUC | PR-AUC 95% CI | Precision | Recall | F1 | Alerts | TP | FP | FN |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in results.itertuples(index=False):
        lines.append(
            f"| {row.feature_set} | {row.profile} | "
            f"{row.pr_auc:.6f} | "
            f"[{row.pr_auc_ci_lower:.6f}, {row.pr_auc_ci_upper:.6f}] | "
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
            "## Important note",
            "",
            "This is the final internal temporal holdout for the current "
            "PaySim experiment. Because earlier exploratory experiments "
            "had already inspected this late period, external or newly "
            "collected data will still be required for a truly untouched "
            "production claim.",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    dataframe, core_features, best_configs, thresholds = load_inputs()
    features, target = prepare_matrix(dataframe, core_features)
    feature_sets = build_feature_sets(core_features)

    split_index = int(len(features) * TRAIN_END_FRACTION)

    x_train = features.iloc[:split_index]
    y_train = target.iloc[:split_index]

    x_holdout = features.iloc[split_index:]
    y_holdout = target.iloc[split_index:].to_numpy()

    print(
        f"Train rows: {len(x_train):,}, fraud: {int(y_train.sum()):,}"
    )
    print(
        f"Holdout rows: {len(x_holdout):,}, fraud: {int(y_holdout.sum()):,}"
    )

    rows = []
    prediction_frame = pd.DataFrame(
        {
            "row_index": np.arange(split_index, len(features)),
            "actual": y_holdout,
        }
    )

    for feature_set_name, selected_features in feature_sets.items():
        print(f"\nTraining frozen {feature_set_name} model...")

        model = build_model(
            y_train,
            best_configs[feature_set_name],
        )

        model.fit(
            x_train[selected_features],
            y_train,
        )

        probabilities = model.predict_proba(
            x_holdout[selected_features]
        )[:, 1]

        prediction_frame[
            f"{feature_set_name}_probability"
        ] = probabilities

        for profile in [
            "max_f1",
            "recall_at_least_0.50",
            "recall_at_least_0.70",
        ]:
            threshold = get_threshold(
                thresholds,
                feature_set_name,
                profile,
            )

            metrics = point_metrics(
                y_holdout,
                probabilities,
                threshold,
            )

            print(
                f"{feature_set_name} | {profile} | "
                f"PR-AUC={metrics['pr_auc']:.6f} | "
                f"Precision={metrics['precision']:.6f} | "
                f"Recall={metrics['recall']:.6f} | "
                f"F1={metrics['f1_score']:.6f}"
            )

            intervals = bootstrap_intervals(
                y_holdout,
                probabilities,
                threshold,
            )

            row = {
                "feature_set": feature_set_name,
                "profile": profile,
                "threshold": threshold,
                **metrics,
            }

            for metric_name, interval in intervals.items():
                row[f"{metric_name}_ci_lower"] = interval["lower"]
                row[f"{metric_name}_ci_upper"] = interval["upper"]

            rows.append(row)

    results = pd.DataFrame(rows).sort_values(
        ["feature_set", "profile"]
    )

    results.to_csv(RESULTS_FILE, index=False)
    prediction_frame.to_csv(PREDICTIONS_FILE, index=False)
    SUMMARY_FILE.write_text(
        build_summary(results),
        encoding="utf-8",
    )

    print(f"\nSaved results: {RESULTS_FILE}")
    print(f"Saved predictions: {PREDICTIONS_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")

    print("\nHoldout results:")
    print(
        results[
            [
                "feature_set",
                "profile",
                "threshold",
                "pr_auc",
                "pr_auc_ci_lower",
                "pr_auc_ci_upper",
                "precision",
                "recall",
                "f1_score",
                "alert_count",
                "false_positive",
                "false_negative",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
