# fixed/orders.py — orders depends on payments and events; nothing depends back on it.
import events
from payments import charge


def mark_paid(event):
    return f"order {event['order_id']} paid"


events.subscribe(mark_paid)


def checkout(order_id):
    return charge(order_id)
