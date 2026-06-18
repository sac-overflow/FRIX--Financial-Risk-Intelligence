from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

INPUT_FILE = DATA_DIR / "frix_features_day1.csv"
OUTPUT_FILE = DATA_DIR / "frix_time_aware_graph_features_v2.csv"


def build_time_aware_graph_features() -> pd.DataFrame:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    usecols = [
        "step",
        "nameOrig",
        "nameDest",
        "amount",
        "is_high_risk_type",
    ]

    print("Loading Day 1 feature dataset...")
    df = pd.read_csv(INPUT_FILE, usecols=usecols)

    print(f"Rows loaded: {len(df):,}")
    print("Sorting transactions by time...")

    df["_row_order"] = range(len(df))
    df = df.sort_values(
        ["step", "_row_order"],
        kind="stable",
    ).reset_index(drop=True)

    sender_neighbors: dict[str, set[str]] = defaultdict(set)
    receiver_neighbors: dict[str, set[str]] = defaultdict(set)

    receiver_total_amount: dict[str, float] = defaultdict(float)
    receiver_txn_count: dict[str, int] = defaultdict(int)
    receiver_high_risk_count: dict[str, int] = defaultdict(int)

    pair_count: dict[tuple[str, str], int] = defaultdict(int)
    pair_volume: dict[tuple[str, str], float] = defaultdict(float)

    sender_out_degree_values: list[int] = []
    receiver_in_degree_values: list[int] = []
    receiver_total_amount_values: list[float] = []
    receiver_avg_amount_values: list[float] = []
    receiver_high_risk_values: list[int] = []
    repeated_pair_count_values: list[int] = []
    repeated_pair_volume_values: list[float] = []
    reciprocal_link_values: list[int] = []
    self_transfer_values: list[int] = []
    fan_out_alert_values: list[int] = []
    funnel_alert_values: list[int] = []
    repeated_pair_alert_values: list[int] = []
    possible_mule_receiver_values: list[int] = []
    graph_risk_score_values: list[int] = []

    print("Building causal graph features...")

    for index, row in enumerate(df.itertuples(index=False), start=1):
        sender = row.nameOrig
        receiver = row.nameDest
        amount = float(row.amount)
        high_risk = int(row.is_high_risk_type)
        pair = (sender, receiver)

        sender_out_degree = len(sender_neighbors[sender])
        receiver_in_degree = len(receiver_neighbors[receiver])

        prior_receiver_total = receiver_total_amount[receiver]
        prior_receiver_count = receiver_txn_count[receiver]
        prior_receiver_avg = (
            prior_receiver_total / prior_receiver_count
            if prior_receiver_count > 0
            else 0.0
        )
        prior_receiver_high_risk = receiver_high_risk_count[receiver]

        prior_pair_count = pair_count[pair]
        prior_pair_volume = pair_volume[pair]

        reciprocal_link = int(sender in sender_neighbors[receiver])
        self_transfer = int(sender == receiver)

        fan_out_alert = int(sender_out_degree >= 5)
        funnel_alert = int(receiver_in_degree >= 5)
        repeated_pair_alert = int(prior_pair_count >= 3)

        possible_mule_receiver = int(
            receiver_in_degree >= 5
            and prior_receiver_total >= 50000
            and prior_receiver_high_risk >= 2
        )

        graph_risk_score = min(
            100,
            fan_out_alert * 20
            + funnel_alert * 20
            + repeated_pair_alert * 20
            + reciprocal_link * 15
            + self_transfer * 25
            + possible_mule_receiver * 30,
        )

        sender_out_degree_values.append(sender_out_degree)
        receiver_in_degree_values.append(receiver_in_degree)
        receiver_total_amount_values.append(prior_receiver_total)
        receiver_avg_amount_values.append(prior_receiver_avg)
        receiver_high_risk_values.append(prior_receiver_high_risk)
        repeated_pair_count_values.append(prior_pair_count)
        repeated_pair_volume_values.append(prior_pair_volume)
        reciprocal_link_values.append(reciprocal_link)
        self_transfer_values.append(self_transfer)
        fan_out_alert_values.append(fan_out_alert)
        funnel_alert_values.append(funnel_alert)
        repeated_pair_alert_values.append(repeated_pair_alert)
        possible_mule_receiver_values.append(possible_mule_receiver)
        graph_risk_score_values.append(graph_risk_score)

        sender_neighbors[sender].add(receiver)
        receiver_neighbors[receiver].add(sender)

        receiver_total_amount[receiver] += amount
        receiver_txn_count[receiver] += 1
        receiver_high_risk_count[receiver] += high_risk

        pair_count[pair] += 1
        pair_volume[pair] += amount

        if index % 100000 == 0:
            print(f"Processed {index:,} rows...")

    output = pd.DataFrame(
        {
            "_row_order": df["_row_order"],
            "nameOrig": df["nameOrig"],
            "nameDest": df["nameDest"],
            "sender_out_degree_prior": sender_out_degree_values,
            "receiver_in_degree_prior": receiver_in_degree_values,
            "receiver_total_amount_prior": receiver_total_amount_values,
            "receiver_avg_amount_prior": receiver_avg_amount_values,
            "receiver_high_risk_txn_count_prior": receiver_high_risk_values,
            "repeated_pair_count_prior": repeated_pair_count_values,
            "repeated_pair_volume_prior": repeated_pair_volume_values,
            "reciprocal_link_prior": reciprocal_link_values,
            "self_transfer": self_transfer_values,
            "fan_out_alert_v2": fan_out_alert_values,
            "funnel_alert_v2": funnel_alert_values,
            "repeated_pair_alert_v2": repeated_pair_alert_values,
            "possible_mule_receiver_v2": possible_mule_receiver_values,
            "graph_risk_score_v2": graph_risk_score_values,
        }
    )

    output = (
        output.sort_values("_row_order", kind="stable")
        .drop(columns=["_row_order"])
        .reset_index(drop=True)
    )

    return output


def validate_output(output: pd.DataFrame) -> None:
    expected_rows = 1_048_575

    if len(output) != expected_rows:
        raise ValueError(
            f"Unexpected row count: {len(output):,}. "
            f"Expected {expected_rows:,}."
        )

    if output.isna().any().any():
        raise ValueError("Output contains missing values.")

    print("Validation passed.")
    print(f"Rows: {len(output):,}")
    print(f"Columns: {len(output.columns):,}")
    print(
        "Maximum graph risk score: "
        f"{int(output['graph_risk_score_v2'].max())}"
    )


def main() -> None:
    output = build_time_aware_graph_features()
    validate_output(output)

    print(f"Saving: {OUTPUT_FILE}")
    output.to_csv(OUTPUT_FILE, index=False)

    print("Time-aware graph feature dataset created successfully.")


if __name__ == "__main__":
    main()
