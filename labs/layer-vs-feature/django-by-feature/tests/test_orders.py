from django.test import TestCase

from apps.orders.models import Order
from apps.orders.services import place_order
from apps.users.models import Customer


class PlaceOrderTests(TestCase):
    def test_order_is_linked_to_customer_through_users_service(self):
        customer = Customer.objects.create(email="a@b.c")
        order = place_order(customer.id, 1500)
        self.assertEqual(order.customer.email, "a@b.c")

    def test_cross_app_foreign_key_uses_the_app_label(self):
        field = Order._meta.get_field("customer")
        self.assertEqual(field.related_model._meta.label, "users.Customer")

    def test_orders_route_is_mounted(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
