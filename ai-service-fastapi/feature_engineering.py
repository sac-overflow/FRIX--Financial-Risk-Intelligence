import pandas as pd

from schemas import TransactionRequest


LARGE_AMOUNT_THRESHOLD = 519460.35099999997

FEATURE_COLUMNS = [
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "origin_balance_error",
    "dest_balance_error",
    "is_high_risk_type",
    "sender_txn_count",
    "receiver_txn_count",
    "sender_emptied_account",
    "is_large_amount",
    "risk_score_v1",
]


def build_model_features(transaction: TransactionRequest) -> tuple[pd.DataFrame, dict]:
    """
    Converts an API transaction request into the exact feature format
    expected by the trained Random Forest model.
    """
    txn_type = transaction.transaction_type.upper()

    origin_balance_error = (
        transaction.oldbalanceOrg - transaction.amount - transaction.newbalanceOrig
    )

    dest_balance_error = (
        transaction.oldbalanceDest + transaction.amount - transaction.newbalanceDest
    )

    is_high_risk_type = int(txn_type in ["TRANSFER", "CASH_OUT"])

    sender_emptied_account = int(
        transaction.oldbalanceOrg > 0 and transaction.newbalanceOrig == 0
    )

    is_large_amount = int(transaction.amount > LARGE_AMOUNT_THRESHOLD)

    risk_score_v1 = (
        is_high_risk_type * 20
        + is_large_amount * 25
        + sender_emptied_account * 25
        + int(abs(dest_balance_error) > 0) * 20
        + int(transaction.receiver_txn_count > 30) * 10
    )

    engineered_values = {
        "origin_balance_error": origin_balance_error,
        "dest_balance_error": dest_balance_error,
        "is_high_risk_type": is_high_risk_type,
        "sender_emptied_account": sender_emptied_account,
        "is_large_amount": is_large_amount,
        "risk_score_v1": risk_score_v1,
    }

    input_data = pd.DataFrame(
        [
            {
                "amount": transaction.amount,
                "oldbalanceOrg": transaction.oldbalanceOrg,
                "newbalanceOrig": transaction.newbalanceOrig,
                "oldbalanceDest": transaction.oldbalanceDest,
                "newbalanceDest": transaction.newbalanceDest,
                "origin_balance_error": origin_balance_error,
                "dest_balance_error": dest_balance_error,
                "is_high_risk_type": is_high_risk_type,
                "sender_txn_count": transaction.sender_txn_count,
                "receiver_txn_count": transaction.receiver_txn_count,
                "sender_emptied_account": sender_emptied_account,
                "is_large_amount": is_large_amount,
                "risk_score_v1": risk_score_v1,
            }
        ]
    )[FEATURE_COLUMNS]

    return input_data, engineered_values