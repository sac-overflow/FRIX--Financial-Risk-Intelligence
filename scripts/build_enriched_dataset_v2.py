from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DAY1_FILE = DATA_DIR / "frix_features_day1.csv"
GRAPH_FILE = DATA_DIR / "frix_graph_features_day3.csv"
OUTPUT_FILE = DATA_DIR / "frix_enriched_dataset_v2.csv"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DAY1_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {DAY1_FILE}")

    if not GRAPH_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {GRAPH_FILE}")

    print("Loading datasets...")
    day1_df = pd.read_csv(DAY1_FILE)
    graph_df = pd.read_csv(GRAPH_FILE)

    print(f"Day 1 rows: {len(day1_df):,}")
    print(f"Graph rows: {len(graph_df):,}")

    return day1_df, graph_df


def validate_data(
    day1_df: pd.DataFrame,
    graph_df: pd.DataFrame,
) -> None:
    keys = ["nameOrig", "nameDest"]

    if len(day1_df) != len(graph_df):
        raise ValueError("Input datasets have different row counts.")

    if day1_df.duplicated(keys).any():
        raise ValueError("Day 1 dataset contains duplicate account pairs.")

    if graph_df.duplicated(keys).any():
        raise ValueError("Graph dataset contains duplicate account pairs.")

    print("Dataset validation passed.")


def merge_graph_features(
    day1_df: pd.DataFrame,
    graph_df: pd.DataFrame,
) -> pd.DataFrame:
    keys = ["nameOrig", "nameDest"]

    graph_columns = [
        "nameOrig",
        "nameDest",
        "receiver_in_degree",
        "sender_out_degree",
        "receiver_total_amount",
        "receiver_avg_amount",
        "receiver_high_risk_txn_count",
        "possible_mule_receiver",
        "mule_risk_score_v1",
        "mule_alert_v1",
    ]

    print("Merging graph features...")

    enriched_df = day1_df.merge(
        graph_df[graph_columns],
        on=keys,
        how="left",
        validate="one_to_one",
    )

    if len(enriched_df) != len(day1_df):
        raise ValueError("Row count changed during merge.")

    if enriched_df[graph_columns[2:]].isna().any().any():
        raise ValueError("Graph merge produced missing values.")

    return enriched_df


def add_temporal_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    print("Creating temporal features...")

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

    return dataframe


def add_risk_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    print("Creating velocity and graph-risk features...")

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

    fan_out = dataframe["sender_out_degree"] >= 5
    funnel = dataframe["receiver_in_degree"] >= 5
    mule = dataframe["possible_mule_receiver"] == 1

    dataframe["fan_out_alert_v2"] = fan_out.astype(int)
    dataframe["funnel_alert_v2"] = funnel.astype(int)

    dataframe["graph_risk_score_v2"] = (
        fan_out.astype(int) * 20
        + funnel.astype(int) * 20
        + mule.astype(int) * 30
        + dataframe["mule_risk_score_v1"].clip(0, 30)
    ).clip(upper=100)

    return dataframe


def finalize_dataset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    return (
        dataframe.sort_values("_row_order", kind="stable")
        .drop(columns=["_row_order"])
        .reset_index(drop=True)
    )


def main() -> None:
    day1_df, graph_df = load_data()
    validate_data(day1_df, graph_df)

    enriched_df = merge_graph_features(day1_df, graph_df)
    enriched_df = add_temporal_features(enriched_df)
    enriched_df = add_risk_features(enriched_df)
    enriched_df = finalize_dataset(enriched_df)

    print(f"Saving: {OUTPUT_FILE}")
    enriched_df.to_csv(OUTPUT_FILE, index=False)

    print("Dataset v2 created successfully.")
    print(f"Rows: {len(enriched_df):,}")
    print(f"Columns: {len(enriched_df.columns):,}")
    print(f"Fraud rows: {int(enriched_df['isFraud'].sum()):,}")
    print(
        f"Fraud rate: "
        f"{enriched_df['isFraud'].mean() * 100:.6f}%"
    )


if __name__ == "__main__":
    main()
