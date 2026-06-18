from risk_fusion import calculate_fused_risk


def test_high_fused_risk():
    result = calculate_fused_risk(
        fraud_probability=0.9833,
        rule_risk_score=70,
        velocity_score=0,
    )

    assert result["ml_score"] == 98
    assert result["fused_risk_score"] == 70
    assert result["fused_risk_level"] == "HIGH"


def test_medium_fused_risk():
    result = calculate_fused_risk(
        fraud_probability=0.40,
        rule_risk_score=40,
        velocity_score=50,
    )

    assert result["fused_risk_score"] == 42
    assert result["fused_risk_level"] == "MEDIUM"


def test_low_fused_risk():
    result = calculate_fused_risk(
        fraud_probability=0.0,
        rule_risk_score=20,
        velocity_score=0,
    )

    assert result["fused_risk_score"] == 6
    assert result["fused_risk_level"] == "LOW"


def test_fused_risk_score_is_capped_at_100():
    result = calculate_fused_risk(
        fraud_probability=1.5,
        rule_risk_score=150,
        velocity_score=150,
    )

    assert result["fused_risk_score"] == 100
    assert result["fused_risk_level"] == "HIGH"
