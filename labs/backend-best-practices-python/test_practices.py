import io
import json
import unittest

from practices import TokenBucket, make_logger, request_id


class PracticeTests(unittest.TestCase):
    def test_token_bucket(self):
        now = [1000.0]
        bucket = TokenBucket(capacity=3, per_second=0.5, clock=lambda: now[0])
        self.assertEqual([bucket.take("u1")[0] for _ in range(4)], [True, True, True, False])
        self.assertEqual(bucket.take("u1"), (False, 2))
        self.assertTrue(bucket.take("u2")[0])  # limits are per key
        now[0] += 2
        self.assertTrue(bucket.take("u1")[0])

    def test_logs_are_json_with_request_id_and_redacted(self):
        out = io.StringIO()
        log = make_logger(out)
        token = request_id.set("req_1")  # middleware does this once per request
        try:
            log.info("payment.charged", extra={"fields": {"cardToken": "tok_visa_4242", "amountKobo": 500000}})
        finally:
            request_id.reset(token)
        self.assertEqual(json.loads(out.getvalue()), {
            "level": "INFO", "msg": "payment.charged", "requestId": "req_1",
            "cardToken": "[redacted]", "amountKobo": 500000,
        })


if __name__ == "__main__":
    unittest.main()
