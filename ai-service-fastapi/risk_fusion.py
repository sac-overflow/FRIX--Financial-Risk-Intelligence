def calculate_fused_risk(
    fraud_probability: float,
    rule_risk_score: int,
    velocity_score: int,
    graph_score: int = 0,
) -> dict:
    ml_score = round(fraud_probability * 100)

    fused_score = round(
        (ml_score * 0.50)
        + (rule_risk_score * 0.30)
        + (velocity_score * 0.20)
        + (graph_score * 0.15)
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
