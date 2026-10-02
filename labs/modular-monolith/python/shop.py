"""shop.py — two modules talking through events; a bus that delivers at least once."""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PaymentSucceeded:
    event_id: str
    order_id: str
    amount_kobo: int


Handler = Callable[[PaymentSucceeded], None]


class InProcessBus:
    def __init__(self):
        self.handlers: list[Handler] = []

    def subscribe(self, handler: Handler) -> None:
        self.handlers.append(handler)

    def publish(self, event: PaymentSucceeded) -> None:
        for handler in self.handlers:
            handler(event)


class AtLeastOnceBus(InProcessBus):
    """What a real broker promises. This one delivers every event twice."""

    def publish(self, event: PaymentSucceeded) -> None:
        super().publish(event)
        super().publish(event)


class Payments:
    def __init__(self, bus: InProcessBus):
        self.bus, self.n = bus, 0

    def record_success(self, order_id: str, amount_kobo: int) -> None:
        self.n += 1
        self.bus.publish(PaymentSucceeded(f"evt_{self.n}", order_id, amount_kobo))


class Orders:
    """Never imports Payments — it only knows the event's shape."""

    def __init__(self, bus: InProcessBus, idempotent: bool):
        self.paid: dict[str, int] = {}
        self.seen: set[str] = set()
        self.idempotent = idempotent
        bus.subscribe(self.on_payment)

    def on_payment(self, event: PaymentSucceeded) -> None:
        if self.idempotent:
            if event.event_id in self.seen:
                return
            self.seen.add(event.event_id)
        self.paid[event.order_id] = self.paid.get(event.order_id, 0) + event.amount_kobo
