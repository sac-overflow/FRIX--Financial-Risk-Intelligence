from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DAY1_FILE = DATA_DIR / "frix_features_day1.csv"
GRAPH_FILE = DATA_DIR / "frix_time_aware_graph_features_v2.csv"
OUTPUT_FILE = DATA_DIR / "frix_enriched_dataset_v3.csv"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DAY1_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {DAY1_FILE}")

    if not GRAPH_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {GRAPH_FILE}")

    print("Loading Day 1 feature dataset...")
    day1_df = pd.read_csv(DAY1_FILE)

    print("Loading time-aware graph feature dataset...")
    graph_df = pd.read_csv(GRAPH_FILE)

    print(f"Day 1 rows: {len(day1_df):,}")
    print(f"Graph rows: {len(graph_df):,}")

    return day1_df, graph_df


def validate_alignment(
    day1_df: pd.DataFrame,
    graph_df: pd.DataFrame,
) -> None:
    if len(day1_df) != len(graph_df):
        raise ValueError("Input datasets have different row counts.")

    sender_match = day1_df["nameOrig"].equals(graph_df["nameOrig"])
    receiver_match = day1_df["nameDest"].equals(graph_df["nameDest"])

    if not sender_match or not receiver_match:
        raise ValueError(
            "Time-aware graph rows are not aligned with Day 1 transactions."
        )

    if graph_df.isna().any().any():
        raise ValueError("Time-aware graph dataset contains missing values.")

    print("Row alignment validation passed.")


def add_temporal_and_velocity_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    print("Creating causal temporal and velocity features...")

    dataframe = dataframe.copy()
    dataframe["_row_order"] = range(len(dataframe))

    dataframe = dataframe.sort_values(
        ["step", "_row_order"],
        kind="stable",
    ).reset_index(drop=True)

    dataframe["sender_prior_txn_count"] = (
        dataframe.groupby("nameOrig").cumcount()
    )

    dataframe["receiver_prior_txn_count"] = (
        dataframe.groupby("nameDest").cumcount()
    )

    dataframe["sender_prior_volume"] = (
        dataframe.groupby("nameOrig")["amount"].cumsum()
        - dataframe["amount"]
    )

    dataframe["receiver_prior_volume"] = (
        dataframe.groupby("nameDest")["amount"].cumsum()
        - dataframe["amount"]
    )

    dataframe["sender_same_step_txn_count"] = (
        dataframe.groupby(["step", "nameOrig"]).cumcount()
    )

    dataframe["receiver_same_step_txn_count"] = (
        dataframe.groupby(["step", "nameDest"]).cumcount()
    )

    dataframe["sender_same_step_volume"] = (
        dataframe.groupby(["step", "nameOrig"])["amount"].cumsum()
        - dataframe["amount"]
    )

    dataframe["receiver_same_step_volume"] = (
        dataframe.groupby(["step", "nameDest"])["amount"].cumsum()
        - dataframe["amount"]
    )

    sender_velocity = (
        dataframe["sender_same_step_txn_count"] >= 5
    )

    receiver_velocity = (
        dataframe["receiver_same_step_txn_count"] >= 5
    )

    sender_volume = (
        dataframe["sender_same_step_volume"] >= 50000
    )

    receiver_volume = (
        dataframe["receiver_same_step_volume"] >= 50000
    )

    repeated_small = (
        (dataframe["sender_same_step_txn_count"] >= 5)
        & (dataframe["amount"] <= 10000)
        & (dataframe["sender_same_step_volume"] >= 10000)
    )

    dataframe["sender_velocity_alert_v2"] = sender_velocity.astype(int)
    dataframe["receiver_velocity_alert_v2"] = receiver_velocity.astype(int)
    dataframe["sender_volume_alert_v2"] = sender_volume.astype(int)
    dataframe["receiver_volume_alert_v2"] = receiver_volume.astype(int)
    dataframe["repeated_small_transfer_v2"] = repeated_small.astype(int)

    dataframe["velocity_score_v2"] = (
        sender_velocity.astype(int) * 15
        + receiver_velocity.astype(int) * 15
        + sender_volume.astype(int) * 15
        + receiver_volume.astype(int) * 15
        + repeated_small.astype(int) * 20
    ).clip(upper=100)

    dataframe = (
        dataframe.sort_values("_row_order", kind="stable")
        .drop(columns=["_row_order"])
        .reset_index(drop=True)
    )

    return dataframe


def combine_features(
    day1_df: pd.DataFrame,
    graph_df: pd.DataFrame,
) -> pd.DataFrame:
    graph_feature_columns = [
        column
        for column in graph_df.columns
        if column not in {"nameOrig", "nameDest"}
    ]

    print("Combining causal graph features with transaction features...")

    enriched_df = pd.concat(
        [
            day1_df.reset_index(drop=True),
            graph_df[graph_feature_columns].reset_index(drop=True),
        ],
        axis=1,
    )

    if enriched_df.columns.duplicated().any():
        duplicates = enriched_df.columns[
            enriched_df.columns.duplicated()
        ].tolist()
        raise ValueError(f"Duplicate columns found: {duplicates}")

    return enriched_df


def validate_output(
    dataframe: pd.DataFrame,
    expected_rows: int,
) -> None:
    if len(dataframe) != expected_rows:
        raise ValueError(
            f"Unexpected row count: {len(dataframe):,}; "
            f"expected {expected_rows:,}."
        )

    if dataframe.isna().any().any():
        raise ValueError("Final dataset contains missing values.")

    expected_fraud_rows = 1142
    fraud_rows = int(dataframe["isFraud"].sum())

    if fraud_rows != expected_fraud_rows:
        raise ValueError(
            f"Unexpected fraud row count: {fraud_rows:,}; "
            f"expected {expected_fraud_rows:,}."
        )

    print("Final dataset validation passed.")
    print(f"Rows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns):,}")
    print(f"Fraud rows: {fraud_rows:,}")
    print(
        f"Fraud rate: "
        f"{dataframe['isFraud'].mean() * 100:.6f}%"
    )
    print(
        "Maximum velocity score: "
        f"{int(dataframe['velocity_score_v2'].max())}"
    )
    print(
        "Maximum graph risk score: "
        f"{int(dataframe['graph_risk_score_v2'].max())}"
    )


def main() -> None:
    day1_df, graph_df = load_inputs()
    validate_alignment(day1_df, graph_df)

    day1_df = add_temporal_and_velocity_features(day1_df)
    enriched_df = combine_features(day1_df, graph_df)

    validate_output(
        enriched_df,
        expected_rows=len(day1_df),
    )

    print(f"Saving: {OUTPUT_FILE}")
    enriched_df.to_csv(OUTPUT_FILE, index=False)

    print("Leakage-safe enriched dataset v3 created successfully.")


if __name__ == "__main__":
    main()
