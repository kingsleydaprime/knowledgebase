# fixed/payments.py — payments announces an event instead of calling orders.
import events


def charge(order_id):
    return events.publish({"type": "PaymentSucceeded", "order_id": order_id})
