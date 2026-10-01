# cycle/payments.py — ...and payments imports a name from orders: a cycle.
from orders import mark_paid


def charge(order_id):
    return mark_paid(order_id)
