from collections import defaultdict
from typing import DefaultDict, Dict, Set, Tuple


class GraphIntelligence:
    def __init__(self) -> None:
        self.outgoing_neighbors: DefaultDict[str, Set[str]] = defaultdict(set)
        self.incoming_neighbors: DefaultDict[str, Set[str]] = defaultdict(set)
        self.edge_counts: DefaultDict[Tuple[str, str], int] = defaultdict(int)
        self.edge_amounts: DefaultDict[Tuple[str, str], float] = defaultdict(float)

        self.receiver_txn_counts: DefaultDict[str, int] = defaultdict(int)
        self.receiver_total_amounts: DefaultDict[str, float] = defaultdict(float)
        self.receiver_high_risk_txn_counts: DefaultDict[str, int] = defaultdict(int)

    def get_graph_signals(
        self,
        sender_id: str,
        receiver_id: str,
    ) -> Dict[str, int | float | bool]:
        edge_key = (sender_id, receiver_id)
        reverse_edge_key = (receiver_id, sender_id)

        sender_out_degree = len(self.outgoing_neighbors[sender_id])
        receiver_in_degree = len(self.incoming_neighbors[receiver_id])

        repeated_pair_count = self.edge_counts[edge_key]
        repeated_pair_volume = self.edge_amounts[edge_key]

        receiver_txn_count = self.receiver_txn_counts[receiver_id]
        receiver_total_amount = self.receiver_total_amounts[receiver_id]

        receiver_avg_amount = (
            receiver_total_amount / receiver_txn_count
            if receiver_txn_count > 0
            else 0.0
        )

        receiver_high_risk_txn_count = (
            self.receiver_high_risk_txn_counts[receiver_id]
        )

        reciprocal_link = self.edge_counts[reverse_edge_key] > 0
        self_transfer = sender_id == receiver_id
        fan_out_alert = sender_out_degree >= 5
        funnel_alert = receiver_in_degree >= 5
        repeated_pair_alert = repeated_pair_count >= 3

        possible_mule_receiver = (
            receiver_in_degree >= 5
            and receiver_high_risk_txn_count >= 2
        )

        graph_score = 0

        if fan_out_alert:
            graph_score += 20
        if funnel_alert:
            graph_score += 20
        if repeated_pair_alert:
            graph_score += 20
        if reciprocal_link:
            graph_score += 15
        if self_transfer:
            graph_score += 25
        if possible_mule_receiver:
            graph_score += 20

        graph_score = min(100, graph_score)

        return {
            # Existing API fields
            "sender_out_degree": sender_out_degree,
            "receiver_in_degree": receiver_in_degree,
            "repeated_pair_count": repeated_pair_count,
            "repeated_pair_volume": float(repeated_pair_volume),
            "fan_out_alert": fan_out_alert,
            "funnel_alert": funnel_alert,
            "repeated_pair_alert": repeated_pair_alert,
            "reciprocal_link": reciprocal_link,
            "self_transfer": self_transfer,
            "graph_score": graph_score,

            # Frozen graph-challenger model fields
            "sender_out_degree_prior": sender_out_degree,
            "receiver_in_degree_prior": receiver_in_degree,
            "receiver_total_amount_prior": float(receiver_total_amount),
            "receiver_avg_amount_prior": float(receiver_avg_amount),
            "receiver_high_risk_txn_count_prior": (
                receiver_high_risk_txn_count
            ),
            "funnel_alert_v2": int(funnel_alert),
            "possible_mule_receiver_v2": int(possible_mule_receiver),
        }

    def record_transaction(
        self,
        sender_id: str,
        receiver_id: str,
        amount: float,
        transaction_type: str = "",
    ) -> None:
        edge_key = (sender_id, receiver_id)
        normalized_type = transaction_type.upper()

        self.outgoing_neighbors[sender_id].add(receiver_id)
        self.incoming_neighbors[receiver_id].add(sender_id)

        self.edge_counts[edge_key] += 1
        self.edge_amounts[edge_key] += float(amount)

        self.receiver_txn_counts[receiver_id] += 1
        self.receiver_total_amounts[receiver_id] += float(amount)

        if normalized_type in {"TRANSFER", "CASH_OUT"}:
            self.receiver_high_risk_txn_counts[receiver_id] += 1

    def clear(self) -> None:
        self.outgoing_neighbors.clear()
        self.incoming_neighbors.clear()
        self.edge_counts.clear()
        self.edge_amounts.clear()

        self.receiver_txn_counts.clear()
        self.receiver_total_amounts.clear()
        self.receiver_high_risk_txn_counts.clear()


graph_intelligence = GraphIntelligence()
