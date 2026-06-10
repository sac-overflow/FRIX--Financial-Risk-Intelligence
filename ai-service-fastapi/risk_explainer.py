def assign_risk_level(fraud_probability: float) -> str:
    """
    Converts model fraud probability into a business-friendly risk level.
    """
    if fraud_probability >= 0.75:
        return "HIGH"
    if fraud_probability >= 0.40:
        return "MEDIUM"
    return "LOW"


def build_reason_codes(engineered_values: dict) -> dict:
    """
    Builds explainable reason codes from engineered transaction signals.
    """
    return {
        "high_risk_transaction_type": bool(engineered_values["is_high_risk_type"]),
        "sender_emptied_account": bool(engineered_values["sender_emptied_account"]),
        "large_amount": bool(engineered_values["is_large_amount"]),
        "origin_balance_error": round(engineered_values["origin_balance_error"], 2),
        "dest_balance_error": round(engineered_values["dest_balance_error"], 2),
    }