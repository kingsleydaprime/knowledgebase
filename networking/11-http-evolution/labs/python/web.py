"""The same small site as the TypeScript lab, on the standard library's HTTP/1.1 server. Python's standard library
has no HTTP/2 at all; hypercorn (server) and httpx[http2] (client) add it."""
import hashlib
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ASSET = b"body { color: rebeccapurple; }\n"
ETAG = '"' + hashlib.sha256(ASSET).hexdigest()[:16] + '"'


class Site(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # the default is "HTTP/1.0", which closes the connection after every response

    def do_GET(self):
        if self.path in ("/fast", "/slow"):
            if self.path == "/slow":
                time.sleep(0.2)
            body = self.path[1:].encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/style.css":
            if self.headers.get("If-None-Match") == ETAG:
                self.send_response(304)  # still the same: headers only
                self.send_header("ETag", ETAG)
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/css")
                self.send_header("ETag", ETAG)
                self.send_header("Cache-Control", "max-age=60")
                self.send_header("Content-Length", str(len(ASSET)))
                self.end_headers()
                self.wfile.write(ASSET)
        elif self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Transfer-Encoding", "chunked")  # http.server doesn't chunk for you: frame it by hand
            self.end_headers()
            for part in (b"hello", b" world"):
                self.wfile.write(f"{len(part):x}\r\n".encode() + part + b"\r\n")
            self.wfile.write(b"0\r\n\r\n")
        else:
            self.send_error(404)

    def log_message(self, *args):  # keep test output quiet
        pass


class CountingServer(ThreadingHTTPServer):
    connections = 0

    def process_request(self, request, client_address):  # called once per accepted TCP connection
        type(self).connections += 1
        super().process_request(request, client_address)


def start() -> tuple[CountingServer, int]:
    CountingServer.connections = 0
    server = CountingServer(("127.0.0.1", 0), Site)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]
