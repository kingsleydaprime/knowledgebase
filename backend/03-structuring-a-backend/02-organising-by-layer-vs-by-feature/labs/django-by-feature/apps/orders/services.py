from apps.users.services import get_customer

from .models import Order


def place_order(customer_id: int, total_pence: int) -> Order:
    customer = get_customer(customer_id)
    return Order.objects.create(customer=customer, total_pence=total_pence)
