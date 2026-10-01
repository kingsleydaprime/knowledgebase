"""orders.py — State as a transition table, Observer as a list of callables,
Iterator as a generator."""
from enum import Enum
from typing import Callable, Iterator


class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


TRANSITIONS: dict[Status, dict[str, Status]] = {
    Status.PENDING: {"pay": Status.PAID, "cancel": Status.CANCELLED},
    Status.PAID: {"ship": Status.SHIPPED, "cancel": Status.CANCELLED},
    Status.SHIPPED: {"deliver": Status.DELIVERED},
    Status.DELIVERED: {},
    Status.CANCELLED: {},
}


class IllegalTransition(Exception):
    pass


class Order:
    def __init__(self, order_id: str):
        self.id = order_id
        self.status = Status.PENDING
        self._listeners: list[Callable[[str, Status, Status], None]] = []
        self._history: list[Status] = [Status.PENDING]

    def on_change(self, listener: Callable[[str, Status, Status], None]) -> None:
        self._listeners.append(listener)

    def apply(self, action: str) -> None:
        nxt = TRANSITIONS[self.status].get(action)
        if nxt is None:
            raise IllegalTransition(f"cannot {action} an order that is {self.status.value}")
        before, self.status = self.status, nxt
        self._history.append(nxt)
        for listener in self._listeners:
            listener(self.id, before, nxt)

    def history(self) -> Iterator[str]:
        """Iterator: a generator yields one item at a time, without building a list."""
        for status in self._history:
            yield status.value
