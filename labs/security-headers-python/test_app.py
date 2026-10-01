import unittest
from wsgiref.util import setup_testing_defaults

from app import application


def call(origin=None):
    environ = {}
    setup_testing_defaults(environ)
    if origin:
        environ["HTTP_ORIGIN"] = origin
    captured = {}
    body = b"".join(application(environ, lambda status, headers, exc=None: captured.update(headers=dict(headers))))
    return captured["headers"], body


class HeaderTests(unittest.TestCase):
    def test_security_headers_on_every_response(self):
        headers, _ = call()
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_cors_allowlist(self):
        ours, _ = call("https://app.example.com")
        self.assertEqual(ours["Access-Control-Allow-Origin"], "https://app.example.com")
        evil, body = call("https://evil.example")
        self.assertNotIn("Access-Control-Allow-Origin", evil)
        self.assertIn(b"ada@x.com", body)  # CORS is not access control: the data still comes back


if __name__ == "__main__":
    unittest.main()
