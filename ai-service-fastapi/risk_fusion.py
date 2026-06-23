from __future__ import annotations


def calculate_fused_risk(
    fraud_probability: float,
    rule_risk_score: int,
    velocity_score: int,
    graph_score: int = 0,
    ml_risk_score: int | None = None,
) -> dict:
    """
    Combines ML, rule, velocity, and graph signals into one 0-100 score.

    `fraud_probability` should be the calibrated probability returned to
    the API client.

    `ml_risk_score` is an optional operational 0-100 score derived from the
    frozen model's raw decision output and thresholds. It should be used for
    fusion because calibrated fraud probabilities are extremely small in a
    highly imbalanced fraud dataset.

    When `ml_risk_score` is omitted, the function falls back to converting
    `fraud_probability` to a percentage for backward compatibility.
    """
    if ml_risk_score is None:
        ml_score = round(float(fraud_probability) * 100)
    else:
        ml_score = int(ml_risk_score)

    ml_score = min(100, max(0, ml_score))
    rule_risk_score = min(100, max(0, int(rule_risk_score)))
    velocity_score = min(100, max(0, int(velocity_score)))
    graph_score = min(100, max(0, int(graph_score)))

    # Weights intentionally sum to exactly 1.00.
    fused_score = round(
        (ml_score * 0.55)
        + (rule_risk_score * 0.20)
        + (velocity_score * 0.15)
        + (graph_score * 0.10)
    )

    fused_score = min(100, max(0, fused_score))

    if fused_score >= 70:
        fused_risk_level = "HIGH"
    elif fused_score >= 40:
        fused_risk_level = "MEDIUM"
    else:
        fused_risk_level = "LOW"

    return {
        "ml_score": ml_score,
        "rule_risk_score": rule_risk_score,
        "velocity_score": velocity_score,
        "graph_score": graph_score,
        "fused_risk_score": fused_score,
        "fused_risk_level": fused_risk_level,
    }
