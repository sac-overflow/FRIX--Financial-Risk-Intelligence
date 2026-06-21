from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
)


ROOT = Path(__file__).resolve().parents[1]

OOF_FILE = (
    ROOT / "models" / "milestone24_threshold_oof_predictions.csv"
)
OUTPUT_FILE = (
    ROOT / "models" / "milestone24_calibration_results.csv"
)
SUMMARY_FILE = (
    ROOT / "docs" / "milestone24_calibration_summary.md"
)
CONFIG_FILE = (
    ROOT / "models" / "milestone24_selected_calibrators.json"
)

CALIBRATOR_DIR = ROOT / "models"

CALIBRATION_FOLDS = [1, 2]
EVALUATION_FOLD = 3
N_BINS = 10
EPSILON = 1e-6


def expected_calibration_error(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    n_bins: int = N_BINS,
) -> float:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.digitize(
        probabilities,
        bins[1:-1],
        right=True,
    )

    ece = 0.0
    total = len(y_true)

    for bin_id in range(n_bins):
        mask = bin_ids == bin_id

        if not np.any(mask):
            continue

        bin_probability = float(probabilities[mask].mean())
        bin_actual = float(y_true[mask].mean())
        bin_weight = float(mask.sum()) / total

        ece += bin_weight * abs(
            bin_probability - bin_actual
        )

    return float(ece)


def calibration_slope_intercept(
    y_true: np.ndarray,
    probabilities: np.ndarray,
) -> tuple[float, float]:
    clipped = np.clip(
        probabilities,
        EPSILON,
        1.0 - EPSILON,
    )

    logits = np.log(
        clipped / (1.0 - clipped)
    ).reshape(-1, 1)

    model = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
    )
    model.fit(logits, y_true)

    slope = float(model.coef_[0][0])
    intercept = float(model.intercept_[0])

    return slope, intercept


def evaluate_method(
    feature_set: str,
    method: str,
    y_true: np.ndarray,
    probabilities: np.ndarray,
) -> dict[str, object]:
    slope, intercept = calibration_slope_intercept(
        y_true,
        probabilities,
    )

    return {
        "feature_set": feature_set,
        "method": method,
        "evaluation_fold": EVALUATION_FOLD,
        "rows": len(y_true),
        "fraud_count": int(y_true.sum()),
        "brier_score": brier_score_loss(
            y_true,
            probabilities,
        ),
        "log_loss": log_loss(
            y_true,
            probabilities,
            labels=[0, 1],
        ),
        "ece_10_bins": expected_calibration_error(
            y_true,
            probabilities,
        ),
        "calibration_slope": slope,
        "calibration_intercept": intercept,
        "mean_predicted_probability": float(
            probabilities.mean()
        ),
        "actual_fraud_rate": float(
            y_true.mean()
        ),
    }


def fit_sigmoid(
    calibration_probabilities: np.ndarray,
    calibration_targets: np.ndarray,
) -> LogisticRegression:
    clipped = np.clip(
        calibration_probabilities,
        EPSILON,
        1.0 - EPSILON,
    )

    logits = np.log(
        clipped / (1.0 - clipped)
    ).reshape(-1, 1)

    model = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
    )
    model.fit(logits, calibration_targets)

    return model


def apply_sigmoid(
    model: LogisticRegression,
    probabilities: np.ndarray,
) -> np.ndarray:
    clipped = np.clip(
        probabilities,
        EPSILON,
        1.0 - EPSILON,
    )

    logits = np.log(
        clipped / (1.0 - clipped)
    ).reshape(-1, 1)

    return model.predict_proba(logits)[:, 1]


def fit_isotonic(
    calibration_probabilities: np.ndarray,
    calibration_targets: np.ndarray,
) -> IsotonicRegression:
    model = IsotonicRegression(
        y_min=0.0,
        y_max=1.0,
        out_of_bounds="clip",
    )

    model.fit(
        calibration_probabilities,
        calibration_targets,
    )

    return model


def build_summary(
    results: pd.DataFrame,
    selected: dict[str, dict[str, object]],
) -> str:
    lines = [
        "# Milestone 24K — Temporal Probability Calibration",
        "",
        "Calibration models were fitted on forward-validation folds 1 and 2 "
        "and evaluated on the later fold 3.",
        "",
        "The latest 20% holdout was not used to choose a calibrator.",
        "",
        "## Calibration comparison",
        "",
        "| Feature set | Method | Brier | Log loss | ECE | Slope | Intercept |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    ranked = results.sort_values(
        [
            "feature_set",
            "brier_score",
            "log_loss",
        ]
    )

    for row in ranked.itertuples(index=False):
        lines.append(
            f"| {row.feature_set} | {row.method} | "
            f"{row.brier_score:.8f} | "
            f"{row.log_loss:.8f} | "
            f"{row.ece_10_bins:.8f} | "
            f"{row.calibration_slope:.6f} | "
            f"{row.calibration_intercept:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Selected calibrators",
            "",
        ]
    )

    for feature_set, config in selected.items():
        lines.append(
            f"- `{feature_set}`: `{config['method']}` "
            f"(Brier {config['brier_score']:.8f}, "
            f"log loss {config['log_loss']:.8f})"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Lower Brier score, log loss, and ECE indicate better probability "
            "quality. PR-AUC is unchanged by monotonic calibration and remains "
            "a ranking metric rather than a probability-quality metric.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    if not OOF_FILE.exists():
        raise FileNotFoundError(OOF_FILE)

    print("Loading out-of-fold development predictions...")
    predictions = pd.read_csv(OOF_FILE)

    required_columns = {
        "feature_set",
        "fold",
        "actual",
        "probability",
    }

    missing = required_columns - set(predictions.columns)

    if missing:
        raise ValueError(
            f"Missing OOF columns: {sorted(missing)}"
        )

    print(
        f"Rows: {len(predictions):,} | "
        f"Fraud: {int(predictions['actual'].sum()):,}"
    )
    print(
        "Calibration folds: 1 and 2 | "
        "Evaluation fold: 3"
    )

    all_rows: list[dict[str, object]] = []
    selected: dict[str, dict[str, object]] = {}

    for feature_set in sorted(
        predictions["feature_set"].unique()
    ):
        print(f"\nCalibrating {feature_set}...")

        subset = predictions[
            predictions["feature_set"] == feature_set
        ].copy()

        calibration = subset[
            subset["fold"].isin(CALIBRATION_FOLDS)
        ]
        evaluation = subset[
            subset["fold"] == EVALUATION_FOLD
        ]

        if calibration.empty or evaluation.empty:
            raise ValueError(
                f"Insufficient folds for {feature_set}."
            )

        y_calibration = calibration[
            "actual"
        ].to_numpy(dtype=np.int8)

        p_calibration = calibration[
            "probability"
        ].to_numpy(dtype=float)

        y_evaluation = evaluation[
            "actual"
        ].to_numpy(dtype=np.int8)

        p_evaluation = evaluation[
            "probability"
        ].to_numpy(dtype=float)

        all_rows.append(
            evaluate_method(
                feature_set,
                "uncalibrated",
                y_evaluation,
                p_evaluation,
            )
        )

        sigmoid_model = fit_sigmoid(
            p_calibration,
            y_calibration,
        )
        sigmoid_probabilities = apply_sigmoid(
            sigmoid_model,
            p_evaluation,
        )

        all_rows.append(
            evaluate_method(
                feature_set,
                "sigmoid",
                y_evaluation,
                sigmoid_probabilities,
            )
        )

        isotonic_model = fit_isotonic(
            p_calibration,
            y_calibration,
        )
        isotonic_probabilities = isotonic_model.predict(
            p_evaluation
        )

        all_rows.append(
            evaluate_method(
                feature_set,
                "isotonic",
                y_evaluation,
                isotonic_probabilities,
            )
        )

        joblib.dump(
            sigmoid_model,
            CALIBRATOR_DIR
            / f"{feature_set}_sigmoid_calibrator.joblib",
        )

        joblib.dump(
            isotonic_model,
            CALIBRATOR_DIR
            / f"{feature_set}_isotonic_calibrator.joblib",
        )

    results = pd.DataFrame(all_rows)

    for feature_set in sorted(
        results["feature_set"].unique()
    ):
        candidates = (
            results[
                results["feature_set"] == feature_set
            ]
            .sort_values(
                ["brier_score", "log_loss", "ece_10_bins"]
            )
            .reset_index(drop=True)
        )

        best = candidates.iloc[0]

        selected[feature_set] = {
            "method": best["method"],
            "brier_score": float(best["brier_score"]),
            "log_loss": float(best["log_loss"]),
            "ece_10_bins": float(best["ece_10_bins"]),
            "evaluation_fold": int(
                best["evaluation_fold"]
            ),
        }

    results.to_csv(OUTPUT_FILE, index=False)

    CONFIG_FILE.write_text(
        json.dumps(selected, indent=2),
        encoding="utf-8",
    )

    SUMMARY_FILE.write_text(
        build_summary(results, selected),
        encoding="utf-8",
    )

    print(f"\nSaved results: {OUTPUT_FILE}")
    print(f"Saved selected calibrators: {CONFIG_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")

    print("\nCalibration ranking:")
    print(
        results.sort_values(
            ["feature_set", "brier_score", "log_loss"]
        )[
            [
                "feature_set",
                "method",
                "brier_score",
                "log_loss",
                "ece_10_bins",
                "calibration_slope",
                "calibration_intercept",
                "mean_predicted_probability",
                "actual_fraud_rate",
            ]
        ].to_string(index=False)
    )

    print("\nSelected calibrators:")

    for feature_set, config in selected.items():
        print(
            f"{feature_set}: {config['method']} | "
            f"Brier={config['brier_score']:.8f} | "
            f"Log loss={config['log_loss']:.8f}"
        )


if __name__ == "__main__":
    main()
