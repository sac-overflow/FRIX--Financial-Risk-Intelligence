from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

HOLDOUT_FILE = (
    ROOT / "models" / "milestone24_holdout_bootstrap_results.csv"
)
TUNING_FILE = (
    ROOT / "models" / "milestone24_xgb_best_configs.json"
)
THRESHOLD_FILE = (
    ROOT / "models" / "milestone24_threshold_tuning_results.csv"
)
CALIBRATION_FILE = (
    ROOT / "models" / "milestone24_selected_calibrators.json"
)

REGISTRY_FILE = (
    ROOT / "models" / "milestone24_champion_registry.json"
)
SUMMARY_FILE = (
    ROOT / "docs" / "milestone24_champion_selection.md"
)


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def get_row(
    dataframe: pd.DataFrame,
    feature_set: str,
    profile: str,
) -> pd.Series:
    matched = dataframe[
        (dataframe["feature_set"] == feature_set)
        & (dataframe["profile"] == profile)
    ]

    if len(matched) != 1:
        raise ValueError(
            f"Expected one row for {feature_set}/{profile}, "
            f"found {len(matched)}."
        )

    return matched.iloc[0]


def main() -> None:
    for path in [
        HOLDOUT_FILE,
        TUNING_FILE,
        THRESHOLD_FILE,
        CALIBRATION_FILE,
    ]:
        require(path)

    holdout = pd.read_csv(HOLDOUT_FILE)
    thresholds = pd.read_csv(THRESHOLD_FILE)

    best_configs = json.loads(
        TUNING_FILE.read_text(encoding="utf-8")
    )
    calibrators = json.loads(
        CALIBRATION_FILE.read_text(encoding="utf-8")
    )

    base_balanced = get_row(
        holdout,
        "base_only",
        "max_f1",
    )
    graph_balanced = get_row(
        holdout,
        "base_plus_graph",
        "max_f1",
    )
    graph_review = get_row(
        holdout,
        "base_plus_graph",
        "recall_at_least_0.50",
    )

    base_threshold = float(
        get_row(
            thresholds,
            "base_only",
            "max_f1",
        )["threshold"]
    )
    graph_threshold = float(
        get_row(
            thresholds,
            "base_plus_graph",
            "max_f1",
        )["threshold"]
    )
    graph_review_threshold = float(
        get_row(
            thresholds,
            "base_plus_graph",
            "recall_at_least_0.50",
        )["threshold"]
    )

    registry = {
        "milestone": "24L",
        "status": "frozen_internal_development_selection",
        "prediction_time": (
            "Immediately before authorization using the current "
            "transaction request and history strictly prior to it."
        ),
        "champion": {
            "name": "frix_xgboost_base_v1",
            "feature_set": "base_only",
            "role": "primary_fraud_ranking_and_balanced_review",
            "hyperparameters": best_configs["base_only"],
            "threshold_profile": "max_f1",
            "threshold": base_threshold,
            "calibrator": calibrators["base_only"]["method"],
            "holdout_metrics": {
                "pr_auc": float(base_balanced["pr_auc"]),
                "pr_auc_ci_lower": float(
                    base_balanced["pr_auc_ci_lower"]
                ),
                "pr_auc_ci_upper": float(
                    base_balanced["pr_auc_ci_upper"]
                ),
                "precision": float(base_balanced["precision"]),
                "recall": float(base_balanced["recall"]),
                "f1_score": float(base_balanced["f1_score"]),
                "false_positive": int(
                    base_balanced["false_positive"]
                ),
                "false_negative": int(
                    base_balanced["false_negative"]
                ),
            },
        },
        "challenger": {
            "name": "frix_xgboost_graph_v1",
            "feature_set": "base_plus_graph",
            "role": "graph_aware_specialist_and_investigation_routing",
            "hyperparameters": best_configs["base_plus_graph"],
            "balanced_profile": {
                "threshold": graph_threshold,
                "calibrator": calibrators[
                    "base_plus_graph"
                ]["method"],
                "precision": float(
                    graph_balanced["precision"]
                ),
                "recall": float(
                    graph_balanced["recall"]
                ),
                "f1_score": float(
                    graph_balanced["f1_score"]
                ),
            },
            "investigation_profile": {
                "threshold": graph_review_threshold,
                "precision": float(
                    graph_review["precision"]
                ),
                "recall": float(
                    graph_review["recall"]
                ),
                "f1_score": float(
                    graph_review["f1_score"]
                ),
            },
            "holdout_pr_auc": float(
                graph_balanced["pr_auc"]
            ),
            "holdout_pr_auc_ci_lower": float(
                graph_balanced["pr_auc_ci_lower"]
            ),
            "holdout_pr_auc_ci_upper": float(
                graph_balanced["pr_auc_ci_upper"]
            ),
        },
        "routing_policy": {
            "default_model": "frix_xgboost_base_v1",
            "graph_model_usage": (
                "Use as a specialist score when meaningful prior "
                "sender/receiver graph history exists."
            ),
            "disagreement_action": (
                "Route strong champion/challenger disagreement to "
                "manual review or additional rules."
            ),
        },
        "limitations": [
            (
                "The latest PaySim period was used in earlier exploratory "
                "work, so it is an internal temporal benchmark rather than "
                "a fully untouched external validation set."
            ),
            (
                "Production claims require external or newly collected "
                "transaction data."
            ),
            (
                "Thresholds and calibration must be monitored for drift."
            ),
        ],
    }

    REGISTRY_FILE.write_text(
        json.dumps(registry, indent=2),
        encoding="utf-8",
    )

    summary = f"""# Milestone 24L — FRIX Champion Selection

## Frozen internal development decision

### Champion

- **Model:** `frix_xgboost_base_v1`
- **Feature set:** `base_only`
- **Role:** Primary fraud ranking and balanced review
- **Holdout PR-AUC:** {base_balanced["pr_auc"]:.6f}
- **95% CI:** [{base_balanced["pr_auc_ci_lower"]:.6f}, {base_balanced["pr_auc_ci_upper"]:.6f}]
- **Precision:** {base_balanced["precision"]:.6f}
- **Recall:** {base_balanced["recall"]:.6f}
- **F1:** {base_balanced["f1_score"]:.6f}
- **Frozen raw threshold:** {base_threshold:.6f}
- **Probability calibrator:** `{calibrators["base_only"]["method"]}`

### Challenger

- **Model:** `frix_xgboost_graph_v1`
- **Feature set:** `base_plus_graph`
- **Role:** Graph-aware specialist and investigation routing
- **Holdout PR-AUC:** {graph_balanced["pr_auc"]:.6f}
- **95% CI:** [{graph_balanced["pr_auc_ci_lower"]:.6f}, {graph_balanced["pr_auc_ci_upper"]:.6f}]
- **Balanced threshold:** {graph_threshold:.6f}
- **Investigation threshold:** {graph_review_threshold:.6f}
- **Probability calibrator:** `{calibrators["base_plus_graph"]["method"]}`

## Routing policy

1. Use the base-only champion by default.
2. Use the graph challenger when meaningful prior graph history exists.
3. Treat strong disagreement as a reason for manual review or additional checks.
4. Do not describe raw XGBoost scores as literal probabilities; use calibrated outputs.

## Limitation

This is the frozen **internal development selection** for the PaySim experiment. External or newly collected data is still required before making a production-performance claim.
"""

    SUMMARY_FILE.write_text(
        summary,
        encoding="utf-8",
    )

    print(f"Saved registry: {REGISTRY_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")
    print()
    print("FRIX champion frozen:")
    print("  frix_xgboost_base_v1")
    print("FRIX challenger frozen:")
    print("  frix_xgboost_graph_v1")


if __name__ == "__main__":
    main()
