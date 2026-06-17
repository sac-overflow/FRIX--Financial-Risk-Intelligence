def calculate_velocity_signals(context_features: dict, amount: float) -> dict:
    """
    Converts rolling transaction memory into velocity-risk signals.

    This detects early signs of smurfing, burst activity, and unusual
    short-window transaction concentration.
    """

    sender_count = context_features.get("sender_txn_count_10m", 0)
    receiver_count = context_features.get("receiver_txn_count_10m", 0)
    sender_volume = context_features.get("sender_volume_10m", 0.0)
    receiver_volume = context_features.get("receiver_volume_10m", 0.0)
    unique_receivers = context_features.get("unique_receivers_10m", 0)
    unique_senders = context_features.get("unique_senders_10m", 0)

    sender_velocity_alert = sender_count >= 5
    receiver_velocity_alert = receiver_count >= 5

    sender_volume_alert = sender_volume >= 50000
    receiver_volume_alert = receiver_volume >= 50000

    repeated_small_transfer = (
        sender_count >= 5
        and amount <= 10000
        and sender_volume >= 10000
    )

    funnel_pattern = (
        unique_senders >= 5
        and receiver_count >= 5
    )

    fan_out_pattern = (
        unique_receivers >= 5
        and sender_count >= 5
    )

    velocity_score = 0

    if sender_velocity_alert:
        velocity_score += 15
    if receiver_velocity_alert:
        velocity_score += 15
    if sender_volume_alert:
        velocity_score += 15
    if receiver_volume_alert:
        velocity_score += 15
    if repeated_small_transfer:
        velocity_score += 20
    if funnel_pattern:
        velocity_score += 20
    if fan_out_pattern:
        velocity_score += 15

    velocity_score = min(100, velocity_score)

    return {
        "sender_velocity_alert": sender_velocity_alert,
        "receiver_velocity_alert": receiver_velocity_alert,
        "sender_volume_alert": sender_volume_alert,
        "receiver_volume_alert": receiver_volume_alert,
        "repeated_small_transfer": repeated_small_transfer,
        "funnel_pattern": funnel_pattern,
        "fan_out_pattern": fan_out_pattern,
        "velocity_score": velocity_score,
    }