from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "frix_enriched_dataset_v3.csv"
CORE_FEATURE_FILE = (
    ROOT / "models" / "milestone24_core_pretransaction_features.json"
)
BEST_CONFIG_FILE = (
    ROOT / "models" / "milestone24_xgb_best_configs.json"
)

BASE_MODEL_FILE = ROOT / "models" / "frix_xgboost_base_v1.joblib"
GRAPH_MODEL_FILE = ROOT / "models" / "frix_xgboost_graph_v1.joblib"
METADATA_FILE = ROOT / "models" / "frix_deployment_model_metadata.json"

TARGET = "isFraud"
TRAIN_END_FRACTION = 0.80
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


def load_inputs():
    for path in [
        DATA_FILE,
        CORE_FEATURE_FILE,
        BEST_CONFIG_FILE,
    ]:
        if not path.exists():
            raise FileNotFoundError(path)

    print("Loading deployment training data...")
    dataframe = pd.read_csv(DATA_FILE)

    core_features = json.loads(
        CORE_FEATURE_FILE.read_text(encoding="utf-8")
    )
    best_configs = json.loads(
        BEST_CONFIG_FILE.read_text(encoding="utf-8")
    )

    print(f"Rows: {len(dataframe):,}")
    print(f"Core features: {len(core_features):,}")

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


def main():
    dataframe, core_features, best_configs = load_inputs()
    features, target = prepare_matrix(
        dataframe,
        core_features,
    )
    feature_sets = build_feature_sets(core_features)

    split_index = int(
        len(features) * TRAIN_END_FRACTION
    )

    x_train = features.iloc[:split_index]
    y_train = target.iloc[:split_index]

    print(
        f"Training rows: {len(x_train):,} | "
        f"Fraud: {int(y_train.sum()):,}"
    )

    artifacts = {}

    for feature_set_name, selected_features in (
        feature_sets.items()
    ):
        model_name = (
            "frix_xgboost_base_v1"
            if feature_set_name == "base_only"
            else "frix_xgboost_graph_v1"
        )

        output_path = (
            BASE_MODEL_FILE
            if feature_set_name == "base_only"
            else GRAPH_MODEL_FILE
        )

        print(
            f"\nTraining {model_name} "
            f"with {len(selected_features)} features..."
        )

        model = build_model(
            y_train,
            best_configs[feature_set_name],
        )

        model.fit(
            x_train[selected_features],
            y_train,
        )

        joblib.dump(model, output_path)

        artifacts[model_name] = {
            "path": str(output_path),
            "feature_set": feature_set_name,
            "features": selected_features,
            "feature_count": len(selected_features),
            "hyperparameters": best_configs[
                feature_set_name
            ],
            "training_rows": len(x_train),
            "training_fraud": int(y_train.sum()),
        }

        print(f"Saved: {output_path}")

    METADATA_FILE.write_text(
        json.dumps(
            {
                "status": "deployment_artifacts_created",
                "training_fraction": TRAIN_END_FRACTION,
                "artifacts": artifacts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved metadata: {METADATA_FILE}")
    print("Deployment model artifacts created successfully.")


if __name__ == "__main__":
    main()
