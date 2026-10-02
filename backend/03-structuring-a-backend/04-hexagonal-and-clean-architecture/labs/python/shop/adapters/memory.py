"""shop/adapters/memory — driven adapters. They import the domain, never the reverse."""
from shop.domain import Order


class InMemoryOrders:
    def __init__(self):
        self.saved: list[Order] = []

    def save(self, order: Order) -> None:
        self.saved.append(order)


class FakePayments:
    def __init__(self, decline_above: int):
        self.decline_above = decline_above

    def charge(self, customer_id: str, kobo: int) -> bool:
        return kobo <= self.decline_above
