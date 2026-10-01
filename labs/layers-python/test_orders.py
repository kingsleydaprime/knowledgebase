import unittest

from orders import Item, OutOfStockError, Repository, Service, create_order


class LayerTests(unittest.TestCase):
    def test_service_rule_without_http(self):
        service = Service(Repository({"mug": 1}))
        with self.assertRaises(OutOfStockError):
            service.place([Item("mug", 2)])

    def test_controller_maps_domain_errors_to_status_codes(self):
        stock = {"mug": 1}
        service = Service(Repository(stock))
        self.assertEqual(create_order(service, {"items": []})[0], 400)
        self.assertEqual(create_order(service, {"items": [{"sku": "mug", "quantity": 5}]}),
                         (409, {"error": "out of stock: mug", "sku": "mug"}))
        self.assertEqual(create_order(service, {"items": [{"sku": "mug", "quantity": 1}]}), (201, {"id": 1}))
        self.assertEqual(stock["mug"], 0)


if __name__ == "__main__":
    unittest.main()
