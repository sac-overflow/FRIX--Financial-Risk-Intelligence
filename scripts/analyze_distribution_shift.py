from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = PROJECT_ROOT / "data" / "frix_enriched_dataset_v3.csv"
FEATURE_FILE = (
    PROJECT_ROOT
    / "models"
    / "milestone24_core_pretransaction_features.json"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "models"
    / "milestone24_distribution_shift_report.csv"
)

SUMMARY_FILE = (
    PROJECT_ROOT
    / "docs"
    / "milestone24_distribution_shift_summary.md"
)

TARGET = "isFraud"

TRAIN_FRACTION = 0.60
VALIDATION_FRACTION = 0.20

PSI_EPSILON = 1e-6
PSI_BINS = 10


def load_inputs() -> tuple[pd.DataFrame, list[str]]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(DATA_FILE)

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(FEATURE_FILE)

    print("Loading dataset...")
    dataframe = pd.read_csv(DATA_FILE)

    print("Loading approved core feature list...")
    feature_list = json.loads(
        FEATURE_FILE.read_text(encoding="utf-8")
    )

    print(f"Rows: {len(dataframe):,}")
    print(f"Approved features: {len(feature_list):,}")

    return dataframe, feature_list


def split_by_time(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_end = int(len(dataframe) * TRAIN_FRACTION)
    validation_end = int(
        len(dataframe)
        * (TRAIN_FRACTION + VALIDATION_FRACTION)
    )

    train = dataframe.iloc[:train_end].copy()
    validation = dataframe.iloc[train_end:validation_end].copy()
    test = dataframe.iloc[validation_end:].copy()

    print(
        f"Train rows: {len(train):,}, "
        f"fraud rows: {int(train[TARGET].sum()):,}"
    )
    print(
        f"Validation rows: {len(validation):,}, "
        f"fraud rows: {int(validation[TARGET].sum()):,}"
    )
    print(
        f"Test rows: {len(test):,}, "
        f"fraud rows: {int(test[TARGET].sum()):,}"
    )

    return train, validation, test


def calculate_psi(
    reference: pd.Series,
    comparison: pd.Series,
    bins: int = PSI_BINS,
) -> float:
    reference = reference.dropna().astype(float)
    comparison = comparison.dropna().astype(float)

    if reference.nunique() <= 1:
        return 0.0

    quantiles = np.linspace(0, 1, bins + 1)

    breakpoints = np.unique(
        reference.quantile(quantiles).to_numpy()
    )

    if len(breakpoints) < 3:
        breakpoints = np.linspace(
            reference.min(),
            reference.max(),
            bins + 1,
        )

    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    reference_bins = pd.cut(
        reference,
        bins=breakpoints,
        include_lowest=True,
    )

    comparison_bins = pd.cut(
        comparison,
        bins=breakpoints,
        include_lowest=True,
    )

    reference_distribution = (
        reference_bins.value_counts(normalize=True, sort=False)
        .to_numpy()
    )

    comparison_distribution = (
        comparison_bins.value_counts(normalize=True, sort=False)
        .reindex(
            reference_bins.cat.categories,
            fill_value=0,
        )
        .to_numpy()
    )

    reference_distribution = np.clip(
        reference_distribution,
        PSI_EPSILON,
        None,
    )

    comparison_distribution = np.clip(
        comparison_distribution,
        PSI_EPSILON,
        None,
    )

    psi = np.sum(
        (comparison_distribution - reference_distribution)
        * np.log(
            comparison_distribution / reference_distribution
        )
    )

    return float(psi)


def calculate_js_divergence(
    reference: pd.Series,
    comparison: pd.Series,
    bins: int = PSI_BINS,
) -> float:
    reference = reference.dropna().astype(float)
    comparison = comparison.dropna().astype(float)

    combined_min = min(reference.min(), comparison.min())
    combined_max = max(reference.max(), comparison.max())

    if combined_min == combined_max:
        return 0.0

    edges = np.linspace(
        combined_min,
        combined_max,
        bins + 1,
    )

    reference_hist, _ = np.histogram(
        reference,
        bins=edges,
        density=False,
    )

    comparison_hist, _ = np.histogram(
        comparison,
        bins=edges,
        density=False,
    )

    reference_prob = reference_hist / max(
        reference_hist.sum(),
        1,
    )

    comparison_prob = comparison_hist / max(
        comparison_hist.sum(),
        1,
    )

    return float(
        jensenshannon(
            reference_prob + PSI_EPSILON,
            comparison_prob + PSI_EPSILON,
            base=2,
        ) ** 2
    )


def standardized_mean_difference(
    reference: pd.Series,
    comparison: pd.Series,
) -> float:
    reference = reference.astype(float)
    comparison = comparison.astype(float)

    pooled_variance = (
        reference.var(ddof=1)
        + comparison.var(ddof=1)
    ) / 2

    if pooled_variance <= 0 or pd.isna(pooled_variance):
        return 0.0

    return float(
        (
            comparison.mean()
            - reference.mean()
        )
        / np.sqrt(pooled_variance)
    )


def classify_shift(
    psi: float,
    ks_statistic: float,
    smd: float,
) -> str:
    if (
        psi >= 0.25
        or ks_statistic >= 0.20
        or abs(smd) >= 0.50
    ):
        return "high"

    if (
        psi >= 0.10
        or ks_statistic >= 0.10
        or abs(smd) >= 0.20
    ):
        return "moderate"

    return "low"


def analyze_pair(
    reference_name: str,
    comparison_name: str,
    reference: pd.DataFrame,
    comparison: pd.DataFrame,
    feature_list: list[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for feature in feature_list:
        if feature.startswith("type_"):
            continue

        if feature not in reference.columns:
            continue

        if not pd.api.types.is_numeric_dtype(
            reference[feature]
        ):
            continue

        ref = reference[feature]
        comp = comparison[feature]

        ks_statistic, ks_pvalue = ks_2samp(
            ref,
            comp,
            alternative="two-sided",
            mode="auto",
        )

        psi = calculate_psi(ref, comp)
        js_divergence = calculate_js_divergence(ref, comp)
        smd = standardized_mean_difference(ref, comp)

        shift_level = classify_shift(
            psi=psi,
            ks_statistic=float(ks_statistic),
            smd=smd,
        )

        rows.append(
            {
                "comparison": (
                    f"{reference_name}_vs_{comparison_name}"
                ),
                "feature": feature,
                "reference_mean": ref.mean(),
                "comparison_mean": comp.mean(),
                "reference_std": ref.std(),
                "comparison_std": comp.std(),
                "psi": psi,
                "ks_statistic": float(ks_statistic),
                "ks_pvalue": float(ks_pvalue),
                "js_divergence": js_divergence,
                "standardized_mean_difference": smd,
                "shift_level": shift_level,
            }
        )

    return rows


def build_summary(
    report: pd.DataFrame,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> str:
    high = report[
        report["shift_level"] == "high"
    ]

    moderate = report[
        report["shift_level"] == "moderate"
    ]

    lines = [
        "# Milestone 24D — Distribution Shift Summary",
        "",
        "## Fraud prevalence",
        "",
        (
            f"- Train: "
            f"{train[TARGET].mean() * 100:.6f}%"
        ),
        (
            f"- Validation: "
            f"{validation[TARGET].mean() * 100:.6f}%"
        ),
        (
            f"- Test: "
            f"{test[TARGET].mean() * 100:.6f}%"
        ),
        "",
        "## Shift counts",
        "",
        f"- High-shift rows: {len(high)}",
        f"- Moderate-shift rows: {len(moderate)}",
        "",
        "## Highest-shift features",
        "",
    ]

    ranked = report.sort_values(
        by=[
            "shift_level",
            "psi",
            "ks_statistic",
        ],
        ascending=[True, False, False],
    )

    priority = {
        "high": 0,
        "moderate": 1,
        "low": 2,
    }

    ranked["_priority"] = ranked["shift_level"].map(
        priority
    )

    ranked = ranked.sort_values(
        ["_priority", "psi", "ks_statistic"],
        ascending=[True, False, False],
    )

    for row in ranked.head(15).itertuples(index=False):
        lines.append(
            f"- `{row.feature}` "
            f"({row.comparison}) — "
            f"level={row.shift_level}, "
            f"PSI={row.psi:.4f}, "
            f"KS={row.ks_statistic:.4f}, "
            f"SMD={row.standardized_mean_difference:.4f}"
        )

    lines.extend(
        [
            "",
            "## Interpretation rules",
            "",
            "- PSI below 0.10: low shift",
            "- PSI from 0.10 to below 0.25: moderate shift",
            "- PSI at or above 0.25: high shift",
            "- KS and standardized mean difference are used as supporting diagnostics",
            "",
            "Statistical significance alone is not enough on a dataset this large; effect size and operational relevance must drive decisions.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    dataframe, feature_list = load_inputs()

    train, validation, test = split_by_time(
        dataframe
    )

    rows: list[dict[str, object]] = []

    rows.extend(
        analyze_pair(
            "train",
            "validation",
            train,
            validation,
            feature_list,
        )
    )

    rows.extend(
        analyze_pair(
            "train",
            "test",
            train,
            test,
            feature_list,
        )
    )

    report = pd.DataFrame(rows)

    report.to_csv(
        REPORT_FILE,
        index=False,
    )

    summary = build_summary(
        report,
        train,
        validation,
        test,
    )

    SUMMARY_FILE.write_text(
        summary,
        encoding="utf-8",
    )

    print(f"Saved report: {REPORT_FILE}")
    print(f"Saved summary: {SUMMARY_FILE}")

    print("\nShift counts:")
    print(
        report["shift_level"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()
