from graph_engine import GraphIntelligence


def test_repeated_pair_alert():
    graph = GraphIntelligence()

    for _ in range(3):
        graph.record_transaction(
            sender_id="sender-a",
            receiver_id="receiver-a",
            amount=1000,
        )

    signals = graph.get_graph_signals(
        sender_id="sender-a",
        receiver_id="receiver-a",
    )

    assert signals["repeated_pair_count"] == 3
    assert signals["repeated_pair_volume"] == 3000.0
    assert signals["repeated_pair_alert"] is True
    assert signals["graph_score"] == 20


def test_reciprocal_link_alert():
    graph = GraphIntelligence()

    graph.record_transaction(
        sender_id="account-a",
        receiver_id="account-b",
        amount=5000,
    )

    signals = graph.get_graph_signals(
        sender_id="account-b",
        receiver_id="account-a",
    )

    assert signals["reciprocal_link"] is True
    assert signals["graph_score"] == 15


def test_self_transfer_alert():
    graph = GraphIntelligence()

    signals = graph.get_graph_signals(
        sender_id="same-account",
        receiver_id="same-account",
    )

    assert signals["self_transfer"] is True
    assert signals["graph_score"] == 25


def test_fan_out_and_funnel_alerts():
    graph = GraphIntelligence()

    for index in range(5):
        graph.record_transaction(
            sender_id="hub-sender",
            receiver_id=f"receiver-{index}",
            amount=1000,
        )

    fan_out_signals = graph.get_graph_signals(
        sender_id="hub-sender",
        receiver_id="receiver-new",
    )

    assert fan_out_signals["sender_out_degree"] == 5
    assert fan_out_signals["fan_out_alert"] is True
    assert fan_out_signals["graph_score"] == 20

    for index in range(5):
        graph.record_transaction(
            sender_id=f"sender-{index}",
            receiver_id="hub-receiver",
            amount=1000,
        )

    funnel_signals = graph.get_graph_signals(
        sender_id="sender-new",
        receiver_id="hub-receiver",
    )

    assert funnel_signals["receiver_in_degree"] == 5
    assert funnel_signals["funnel_alert"] is True
    assert funnel_signals["graph_score"] == 20
