from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


WINDOW_MINUTES = 10


@dataclass
class TransactionEvent:
    timestamp: datetime
    sender_id: str
    receiver_id: str
    amount: float
    transaction_type: str


class TransactionMemory:
    """
    In-memory rolling transaction store.

    This is the first version of FRIX temporal memory.
    It tracks recent sender/receiver behavior over a rolling time window.
    Later, this can be replaced by Redis without changing the API contract.
    """

    def __init__(self, window_minutes: int = WINDOW_MINUTES):
        self.window = timedelta(minutes=window_minutes)
        self.sender_events: dict[str, deque[TransactionEvent]] = defaultdict(deque)
        self.receiver_events: dict[str, deque[TransactionEvent]] = defaultdict(deque)

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _prune(self, events: deque[TransactionEvent], now: datetime) -> None:
        cutoff = now - self.window

        while events and events[0].timestamp < cutoff:
            events.popleft()

    def record_transaction(
        self,
        sender_id: str,
        receiver_id: str,
        amount: float,
        transaction_type: str,
    ) -> None:
        now = self._now()

        event = TransactionEvent(
            timestamp=now,
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            transaction_type=transaction_type.upper(),
        )

        self.sender_events[sender_id].append(event)
        self.receiver_events[receiver_id].append(event)

        self._prune(self.sender_events[sender_id], now)
        self._prune(self.receiver_events[receiver_id], now)

    def get_context_features(self, sender_id: str, receiver_id: str) -> dict:
        now = self._now()

        sender_history = self.sender_events[sender_id]
        receiver_history = self.receiver_events[receiver_id]

        self._prune(sender_history, now)
        self._prune(receiver_history, now)

        sender_txn_count_10m = len(sender_history)
        receiver_txn_count_10m = len(receiver_history)

        sender_volume_10m = sum(event.amount for event in sender_history)
        receiver_volume_10m = sum(event.amount for event in receiver_history)

        unique_receivers_10m = len({event.receiver_id for event in sender_history})
        unique_senders_10m = len({event.sender_id for event in receiver_history})

        return {
            "sender_txn_count_10m": sender_txn_count_10m,
            "receiver_txn_count_10m": receiver_txn_count_10m,
            "sender_volume_10m": round(sender_volume_10m, 2),
            "receiver_volume_10m": round(receiver_volume_10m, 2),
            "unique_receivers_10m": unique_receivers_10m,
            "unique_senders_10m": unique_senders_10m,
        }


transaction_memory = TransactionMemory()