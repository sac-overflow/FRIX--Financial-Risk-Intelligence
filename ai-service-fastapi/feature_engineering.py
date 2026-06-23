from __future__ import annotations

import pandas as pd

from schemas import TransactionRequest


LARGE_AMOUNT_THRESHOLD = 519460.35099999997

TRANSACTION_TYPES = [
    "CASH_IN",
    "CASH_OUT",
    "DEBIT",
    "PAYMENT",
    "TRANSFER",
]

BASE_FEATURE_COLUMNS = [
    "amount",
    "is_high_risk_type",
    "oldbalanceDest",
    "oldbalanceOrg",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER",
]

GRAPH_FEATURE_COLUMNS = [
    "amount",
    "funnel_alert_v2",
    "is_high_risk_type",
    "oldbalanceDest",
    "oldbalanceOrg",
    "possible_mule_receiver_v2",
    "receiver_avg_amount_prior",
    "receiver_high_risk_txn_count_prior",
    "receiver_in_degree_prior",
    "receiver_total_amount_prior",
    "sender_out_degree_prior",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER",
]


def build_model_features(
    transaction: TransactionRequest,
    graph_signals: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    txn_type = transaction.transaction_type.upper()

    if txn_type not in TRANSACTION_TYPES:
        raise ValueError(
            f"Unsupported transaction_type: {transaction.transaction_type}"
        )

    is_high_risk_type = int(
        txn_type in {"TRANSFER", "CASH_OUT"}
    )

    type_features = {
        f"type_{name}": int(txn_type == name)
        for name in TRANSACTION_TYPES
    }

    shared_values = {
        "amount": float(transaction.amount),
        "is_high_risk_type": is_high_risk_type,
        "oldbalanceDest": float(transaction.oldbalanceDest),
        "oldbalanceOrg": float(transaction.oldbalanceOrg),
        **type_features,
    }

    base_input = pd.DataFrame(
        [shared_values],
        columns=BASE_FEATURE_COLUMNS,
    )

    graph_values = {
        **shared_values,
        "funnel_alert_v2": int(
            graph_signals.get("funnel_alert_v2", 0)
        ),
        "possible_mule_receiver_v2": int(
            graph_signals.get("possible_mule_receiver_v2", 0)
        ),
        "receiver_avg_amount_prior": float(
            graph_signals.get("receiver_avg_amount_prior", 0.0)
        ),
        "receiver_high_risk_txn_count_prior": int(
            graph_signals.get(
                "receiver_high_risk_txn_count_prior",
                0,
            )
        ),
        "receiver_in_degree_prior": int(
            graph_signals.get("receiver_in_degree_prior", 0)
        ),
        "receiver_total_amount_prior": float(
            graph_signals.get("receiver_total_amount_prior", 0.0)
        ),
        "sender_out_degree_prior": int(
            graph_signals.get("sender_out_degree_prior", 0)
        ),
    }

    graph_input = pd.DataFrame(
        [graph_values],
        columns=GRAPH_FEATURE_COLUMNS,
    )

    origin_balance_error = (
        transaction.oldbalanceOrg
        - transaction.amount
        - transaction.newbalanceOrig
    )

    dest_balance_error = (
        transaction.oldbalanceDest
        + transaction.amount
        - transaction.newbalanceDest
    )

    sender_emptied_account = int(
        transaction.oldbalanceOrg > 0
        and transaction.newbalanceOrig == 0
    )

    is_large_amount = int(
        transaction.amount > LARGE_AMOUNT_THRESHOLD
    )

    if transaction.receiver_txn_count > 1000:
        receiver_activity_score = 30
    elif transaction.receiver_txn_count > 500:
        receiver_activity_score = 25
    elif transaction.receiver_txn_count > 100:
        receiver_activity_score = 18
    elif transaction.receiver_txn_count > 30:
        receiver_activity_score = 10
    else:
        receiver_activity_score = 0

    if transaction.sender_txn_count > 500:
        sender_activity_score = 15
    elif transaction.sender_txn_count > 100:
        sender_activity_score = 10
    elif transaction.sender_txn_count > 30:
        sender_activity_score = 5
    else:
        sender_activity_score = 0

    risk_score_v1 = min(
        100,
        is_high_risk_type * 20
        + is_large_amount * 25
        + sender_emptied_account * 25
        + int(abs(dest_balance_error) > 0) * 20
        + receiver_activity_score
        + sender_activity_score,
    )

    engineered_values = {
        "origin_balance_error": float(origin_balance_error),
        "dest_balance_error": float(dest_balance_error),
        "is_high_risk_type": is_high_risk_type,
        "sender_emptied_account": sender_emptied_account,
        "is_large_amount": is_large_amount,
        "receiver_activity_score": receiver_activity_score,
        "sender_activity_score": sender_activity_score,
        "risk_score_v1": int(risk_score_v1),
    }

    return base_input, graph_input, engineered_values
