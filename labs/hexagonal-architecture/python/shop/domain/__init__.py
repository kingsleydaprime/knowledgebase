"""shop/domain — rules and ports. Imports nothing from shop.adapters."""
from dataclasses import dataclass
from typing import Protocol


class InvalidTotal(Exception):
    pass


class PaymentDeclined(Exception):
    pass


@dataclass
class Order:
    id: str
    total_kobo: int
    paid: bool = False


# Ports: Protocols say what the domain needs; any class with these methods fits.
class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...


class PaymentGateway(Protocol):
    def charge(self, customer_id: str, kobo: int) -> bool: ...


def place_order(orders: OrderRepository, payments: PaymentGateway, order_id: str, customer_id: str, kobo: int) -> Order:
    if kobo <= 0:
        raise InvalidTotal(kobo)
    if not payments.charge(customer_id, kobo):
        raise PaymentDeclined(order_id)
    order = Order(order_id, kobo, paid=True)
    orders.save(order)
    return order
