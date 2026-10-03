import json
import pathlib
import unittest

from communication import Db, RestApi, chain, compact, encode_order_summary, execute, order_screen_rest, resolvers, varint

SHOP = json.loads((pathlib.Path(__file__).parent.parent / "shared" / "shop.json").read_text())
ORDER_SCREEN = {"id": True, "totalPence": True, "customer": {"name": True}, "items": {"quantity": True, "product": {"name": True}}}


class Communication(unittest.TestCase):
    def test_rest_five_requests_two_round_trips(self):
        api = RestApi(Db(SHOP))
        screen, round_trips = order_screen_rest(api, "o1")
        self.assertEqual(screen["customer"]["name"], "Gbenga Ali")
        self.assertEqual([f"{i['quantity']} × {i['product']['name']}" for i in screen["items"]], ["1 × Kettle", "1 × Toaster", "2 × Mug set"])
        self.assertEqual((api.requests, round_trips, api.bytes), (5, 2, 912))
        self.assertEqual(len(compact(screen)), 203)
        self.assertEqual(len(json.dumps(screen)), 225)  # the default separators add 22 spaces

    def test_a_graphql_style_query_one_request_only_the_fields_asked_for(self):
        for batched in [False, True]:
            db = Db(SHOP)
            order = db.find("orders", ["o1"])[0]
            [screen] = execute([order], ORDER_SCREEN, resolvers(db, batched), "Order")
            self.assertEqual(screen, order_screen_rest(RestApi(Db(SHOP)), "o1")[0])
            self.assertEqual(len(compact(screen)), 203)
            self.assertEqual(db.queries, 3 if batched else 5)

    def test_n_plus_one_41_queries_or_3(self):
        for batched in [False, True]:
            db = Db(SHOP)
            orders = db.find("orders", [o["id"] for o in SHOP["orders"]])
            page = execute(orders, {"id": True, "customer": {"name": True}, "items": {"product": {"name": True}}}, resolvers(db, batched), "Order")
            self.assertEqual((len(page), page[0]["customer"]["name"]), (10, "Gbenga Ali"))
            self.assertEqual(db.queries, 3 if batched else 41)

    def test_varints_and_tags_as_in_the_protobuf_documentation(self):
        self.assertEqual(varint(1), b"\x01")
        self.assertEqual(varint(150), b"\x96\x01")
        self.assertEqual(varint(300), b"\xac\x02")
        self.assertEqual(varint(2**35), b"\x80\x80\x80\x80\x80\x01")
        with self.assertRaises(ValueError):
            varint(-1)
        self.assertEqual(encode_order_summary(150, "testing", 1).hex(" "), "08 96 01 12 07 74 65 73 74 69 6e 67 18 01")

    def test_the_same_summary_17_bytes_as_protobuf_50_as_json(self):
        self.assertEqual(len(encode_order_summary(1, "Gbenga Ali", 8996)), 17)
        self.assertEqual(len(compact({"id": 1, "customer": "Gbenga Ali", "totalPence": 8996})), 50)

    def test_a_synchronous_chain(self):
        c = chain([(0.999, 20)] * 5)
        self.assertEqual(f"{c['availability'] * 100:.2f}", "99.50")
        self.assertEqual(c["sequential_ms"], 100)
        self.assertEqual(chain([(1, 30), (1, 50), (1, 20)])["parallel_ms"], 50)


if __name__ == "__main__":
    unittest.main()
