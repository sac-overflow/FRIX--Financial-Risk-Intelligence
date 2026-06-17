from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import DefaultDict, Deque


@dataclass
class TransactionEvent:
    timestamp: datetime
    sender_id: str
    receiver_id: str
    amount: float
    transaction_type: str


class TransactionMemory:
    def __init__(self, window_minutes: int = 10) -> None:
        self.window = timedelta(minutes=window_minutes)
        self.sender_events: DefaultDict[str, Deque[TransactionEvent]] = defaultdict(deque)
        self.receiver_events: DefaultDict[str, Deque[TransactionEvent]] = defaultdict(deque)

    def _prune_events(
        self,
        events: Deque[TransactionEvent],
        current_time: datetime,
    ) -> None:
        cutoff_time = current_time - self.window

        while events and events[0].timestamp < cutoff_time:
            events.popleft()

    def record_transaction(
        self,
        sender_id: str,
        receiver_id: str,
        amount: float,
        transaction_type: str,
    ) -> None:
        current_time = datetime.now(timezone.utc)

        event = TransactionEvent(
            timestamp=current_time,
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=float(amount),
            transaction_type=transaction_type,
        )

        sender_history = self.sender_events[sender_id]
        receiver_history = self.receiver_events[receiver_id]

        self._prune_events(sender_history, current_time)
        self._prune_events(receiver_history, current_time)

        sender_history.append(event)
        receiver_history.append(event)

    def get_context_features(
        self,
        sender_id: str,
        receiver_id: str,
    ) -> dict:
        current_time = datetime.now(timezone.utc)

        sender_history = self.sender_events[sender_id]
        receiver_history = self.receiver_events[receiver_id]

        self._prune_events(sender_history, current_time)
        self._prune_events(receiver_history, current_time)

        sender_volume = sum(event.amount for event in sender_history)
        receiver_volume = sum(event.amount for event in receiver_history)

        unique_receivers = {event.receiver_id for event in sender_history}
        unique_senders = {event.sender_id for event in receiver_history}

        return {
            "sender_txn_count_10m": len(sender_history),
            "receiver_txn_count_10m": len(receiver_history),
            "sender_volume_10m": float(sender_volume),
            "receiver_volume_10m": float(receiver_volume),
            "unique_receivers_10m": len(unique_receivers),
            "unique_senders_10m": len(unique_senders),
        }

    def clear(self) -> None:
        self.sender_events.clear()
        self.receiver_events.clear()


transaction_memory = TransactionMemory()
