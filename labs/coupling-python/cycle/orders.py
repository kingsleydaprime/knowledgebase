# cycle/orders.py — orders imports a name from payments...
from payments import charge


def mark_paid(order_id):
    return f"order {order_id} paid"


def checkout(order_id):
    return charge(order_id)
