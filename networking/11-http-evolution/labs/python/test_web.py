import http.client
import socket
import unittest

from web import CountingServer, start


class Http(unittest.TestCase):
    def setUp(self):
        self.server, self.port = start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_keep_alive_ten_requests_one_connection(self):
        for reuse, expected in [(False, 10), (True, 1)]:
            CountingServer.connections = 0
            conn = http.client.HTTPConnection("127.0.0.1", self.port)
            for _ in range(10):
                if not reuse:
                    conn.close()  # a fresh TCP connection for every request
                conn.request("GET", "/fast")
                self.assertEqual(conn.getresponse().read(), b"fast")
            conn.close()
            self.assertEqual(CountingServer.connections, expected)

    def test_head_of_line_blocking_on_one_connection(self):
        # http.client allows one request at a time per connection; pipelining by hand shows the server's order.
        with socket.create_connection(("127.0.0.1", self.port)) as sock:
            sock.sendall(b"GET /slow HTTP/1.1\r\nHost: shop\r\n\r\nGET /fast HTTP/1.1\r\nHost: shop\r\n\r\n")
            data = b""
            while data.count(b"\r\n\r\n") < 2 or not data.endswith(b"fast"):
                data += sock.recv(4096)
        self.assertLess(data.index(b"slow"), data.index(b"fast"))  # the fast reply came second, behind the slow one

    def test_an_etag_turns_a_second_download_into_a_304(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("GET", "/style.css")
        first = conn.getresponse()
        first.read()
        self.assertEqual((first.status, first.getheader("Cache-Control")), (200, "max-age=60"))
        conn.request("GET", "/style.css", headers={"If-None-Match": first.getheader("ETag")})
        again = conn.getresponse()
        self.assertEqual((again.status, again.read()), (304, b""))
        conn.close()

    def test_chunked_encoding_on_the_wire(self):
        with socket.create_connection(("127.0.0.1", self.port)) as sock:
            sock.sendall(b"GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n")
            raw = b""
            while chunk := sock.recv(4096):
                raw += chunk
        head, body = raw.split(b"\r\n\r\n", 1)
        self.assertIn(b"Transfer-Encoding: chunked", head)
        self.assertEqual(body, b"5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n")


if __name__ == "__main__":
    unittest.main()
