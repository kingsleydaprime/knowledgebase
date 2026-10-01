from .models import Customer


def get_customer(customer_id: int) -> Customer:
    return Customer.objects.get(pk=customer_id)
