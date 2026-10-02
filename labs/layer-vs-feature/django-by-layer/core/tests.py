from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Customer, Order


class ModelsPackageTests(TestCase):
    def test_models_in_a_package_are_registered_because_init_imports_them(self):
        out = StringIO()
        call_command("makemigrations", "core", dry_run=True, stdout=out)
        self.assertIn("Create model Customer", out.getvalue())
        self.assertIn("Create model Order", out.getvalue())

    def test_every_table_is_named_after_the_single_app(self):
        self.assertEqual(Order._meta.db_table, "core_order")
        self.assertEqual(Customer._meta.db_table, "core_customer")

    def test_layer_folders_are_routed_through_one_urls_file(self):
        Customer.objects.create(email="a@b.c")
        self.assertEqual(self.client.get("/api/users/").json(), {"users": [{"id": 1, "email": "a@b.c"}]})
        self.assertEqual(self.client.get("/api/orders/").json(), {"orders": []})
