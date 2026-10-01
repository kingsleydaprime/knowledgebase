import unittest

from app import create_app


class ShopTests(unittest.TestCase):
    def setUp(self):
        app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://", "TESTING": True})
        self.client = app.test_client()
        self.app = app

    def test_order_flow_across_two_blueprints(self):
        self.assertEqual(self.client.post("/api/users/", json={"email": "a@b.c"}).get_json(), {"email": "a@b.c", "id": 1})
        created = self.client.post("/api/orders/", json={"customer_id": 1, "total_pence": 1500})
        self.assertEqual(created.status_code, 201)
        self.assertEqual(self.client.get("/api/orders/").get_data(as_text=True).strip(), "<li>#1: 1500p</li>")

    def test_unknown_customer_is_a_404_not_a_crash(self):
        response = self.client.post("/api/orders/", json={"customer_id": 99, "total_pence": 1})
        self.assertEqual(response.status_code, 404)

    def test_prefixes_come_from_the_composition_root(self):
        rules = sorted(r.rule for r in self.app.url_map.iter_rules() if r.endpoint != "static")
        self.assertEqual(rules, ["/api/orders/", "/api/orders/", "/api/users/"])


if __name__ == "__main__":
    unittest.main()
