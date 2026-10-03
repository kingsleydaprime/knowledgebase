import unittest

from dns import A, CNAME, CachingResolver, ask, build_query, encode_name, parse_message, search_candidates, serve

ZONE = {
    "example.com": [(A, 300, "93.184.216.34")],
    "www.example.com": [(CNAME, 3600, "example.com")],
    "big.example.com": [(A, 60, f"10.0.0.{i + 1}") for i in range(40)],
}


class Dns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sock, _ = serve(ZONE)
        cls.port = cls.sock.getsockname()[1]

    @classmethod
    def tearDownClass(cls):
        cls.sock.close()

    def test_names_and_queries_on_the_wire(self):
        self.assertEqual(encode_name("www.example.com").hex(), "03777777076578616d706c6503636f6d00")
        query = build_query(0xBEEF, "example.com", A)
        self.assertEqual(len(query), 29)
        self.assertEqual(parse_message(query).question, ("example.com", A))

    def test_the_server_follows_the_cname_and_says_nxdomain(self):
        reply = ask(self.port, build_query(42, "www.example.com", A))
        self.assertEqual((reply.id, reply.authoritative), (42, True))
        self.assertEqual(reply.answers, [("www.example.com", CNAME, 3600, "example.com"), ("example.com", A, 300, "93.184.216.34")])
        self.assertEqual(ask(self.port, build_query(43, "nope.example.com", A)).rcode, 3)

    def test_too_big_for_udp_comes_back_truncated(self):
        reply = ask(self.port, build_query(7, "big.example.com", A))
        self.assertEqual((reply.truncated, reply.answers), (True, []))

    def test_a_migration_lower_the_ttl_a_day_ahead(self):
        for old_ttl, stale_seconds in [(86_400, 86_340), (60, 0)]:
            state = {"now": 0, "address": "198.51.100.1", "ttl": old_ttl}
            resolver = CachingResolver(lambda: state["now"], lambda name: (state["address"], state["ttl"]))
            resolver.lookup("shop.example")
            state.update(now=60_000, address="203.0.113.9", ttl=60)
            stale = 0
            for t in range(60, 86_400 + 60, 60):
                state["now"] = t * 1000
                if resolver.lookup("shop.example") == "198.51.100.1":
                    stale += 60
            self.assertEqual(stale, stale_seconds)

    def test_ndots_turns_one_lookup_into_four_queries(self):
        search = ["default.svc.cluster.local", "svc.cluster.local", "cluster.local"]
        self.assertEqual(len(search_candidates("api.example.com", 5, search)), 4)
        self.assertEqual(search_candidates("api.example.com", 5, search)[-1], "api.example.com")
        self.assertEqual(search_candidates("api.example.com.", 5, search), ["api.example.com"])


if __name__ == "__main__":
    unittest.main()
