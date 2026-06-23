from __future__ import annotations


def assign_risk_level(
    fraud_probability: float,
    operational_score: int | None = None,
) -> str:
    """
    Converts the model output into a business-friendly risk level.

    `fraud_probability` is the calibrated fraud probability returned to
    API clients.

    `operational_score` is an optional 0-100 score derived from the frozen
    raw-model thresholds. It should drive the risk label because calibrated
    probabilities are naturally very small in an extremely imbalanced
    fraud dataset.

    The probability thresholds remain only as a backward-compatible
    fallback for older callers.
    """
    if operational_score is not None:
        score = min(100, max(0, int(operational_score)))

        if score >= 70:
            return "HIGH"
        if score >= 40:
            return "MEDIUM"
        return "LOW"

    if fraud_probability >= 0.75:
        return "HIGH"
    if fraud_probability >= 0.40:
        return "MEDIUM"
    return "LOW"


def build_reason_codes(engineered_values: dict) -> dict:
    """
    Builds explainable reason codes from transaction-level signals.

    These reason codes support investigator interpretation only. The legacy
    post-transaction values are not supplied to the frozen champion or
    challenger machine-learning models.
    """
    return {
        "high_risk_transaction_type": bool(
            engineered_values["is_high_risk_type"]
        ),
        "sender_emptied_account": bool(
            engineered_values["sender_emptied_account"]
        ),
        "large_amount": bool(
            engineered_values["is_large_amount"]
        ),
        "origin_balance_error": round(
            engineered_values["origin_balance_error"],
            2,
        ),
        "dest_balance_error": round(
            engineered_values["dest_balance_error"],
            2,
        ),
    }
