# HTTP and Its Evolution in Other Languages

**[Intermediate]** — A companion to [[networking/11-http-evolution/index|HTTP and its evolution]], which serves one small site over HTTP/1.1 and HTTP/2 and shows keep-alive, head-of-line blocking, multiplexing, a `304` and chunked encoding. This page does the same in Python, Go, Java, Rust and C#. The protocol is the same everywhere; the standard libraries are not. Go's serves and speaks HTTP/2 out of the box, and C#'s does through Kestrel. Java's client speaks it but its built-in server doesn't. Python's standard library is HTTP/1.1 only, and Rust's has no HTTP at all, so the Rust lab writes an HTTP/1.1 server by hand, which turns out to be the best way to see what a framework does.

## Before you start

You can already:

- Explain keep-alive, head-of-line blocking, multiplexing, `ETag` revalidation and chunked encoding → [[networking/11-http-evolution/index|the main lesson]].
- Make an HTTP request from at least one of the languages here.

After this lesson you will be able to:

1. Say which HTTP versions your language's standard library can serve and request, and which library adds the rest.
2. Find where your HTTP client pools connections, and the common mistake that defeats it.
3. Read and write HTTP/1.1 messages by hand: request line, headers, the blank line, and a body framed by length or by chunks.

## The kid version

Five post offices all deliver the same letters, by the same rules. One also offers a fast lane where many letters travel together in one van (HTTP/2). One offers the fast lane for sending but not for receiving. Two have only the ordinary counter. And one has no counter at all, so you have to build it yourself from a table, a stamp and a bag, after which you really understand what a counter does.

**Where the analogy stops working.** A post office's counter is the same for every customer. An HTTP client's connection pool belongs to the client *object*: create a new client for every request, and each one opens its own connection, as if every letter came with a brand-new van.

## 1. The tools, by ecosystem

| Language | Server in the standard library | Client in the standard library | HTTP/2 | Usual frameworks |
|---|---|---|---|---|
| TypeScript | `node:http`, `node:http2` | `fetch`, `node:http`, `node:http2` | **both**, including h2c | Express, Fastify |
| Python | `http.server` (HTTP/1.1) | `http.client`, `urllib` | **none** (hypercorn serves it, httpx requests it) | FastAPI, Django |
| Go | `net/http` | `net/http` | **both**, h2c since Go 1.24 (`http.Protocols`) | the standard library, chi |
| Java | `com.sun.net.httpserver` (HTTP/1.1) | `java.net.http.HttpClient` | **client only** (Jetty, Netty serve it) | Spring Boot |
| Rust | none: `TcpListener` and your own parsing | none | none (hyper adds both) | axum, actix-web |
| C# | **Kestrel** (ASP.NET Core) | `HttpClient` | **both**; h2c on an HTTP/2-only endpoint | ASP.NET Core |

C would use a library such as libcurl (client) or nghttp2 (HTTP/2); no lab here.

## 2. What changes between languages

### HTTP/2 needs a version decision, and without TLS nothing decides it

Over TLS, client and server choose HTTP/1.1 or HTTP/2 inside the handshake with ALPN. Without TLS ("h2c"), there's no handshake to choose in. So the client must start speaking HTTP/2 immediately ("prior knowledge"), and the server must expect it:

- **Go** turns h2c on with `Protocols.SetUnencryptedHTTP2(true)` on both the server and the client's `Transport`.
- **C#'s** Kestrel needs an endpoint whose protocols are HTTP/2 *only*, since it can't tell an HTTP/2 client from an HTTP/1.1 one without TLS. `HttpClient` must be told `HttpVersionPolicy.RequestVersionExact`.
- **Node's** `http2.connect("http://…")` assumes it.

In Go and C#, the lab's slow-then-fast pair finishes fast-then-slow on one HTTP/2 connection, just as in TypeScript.

### Connection pools belong to the client object

Keep-alive is HTTP/1.1's default, but reuse only happens if requests share a pool:

- **Go**'s pool is in the `http.Transport`, shared by every `http.Client` that uses it.
- **Java**'s is inside each `HttpClient`. The lab's "no keep-alive" case creates a new `HttpClient` per request, ten connections, which is the real-world mistake that defeats it.
- **C#**'s `HttpClient` pools inside its handler: create one and share it (or use `IHttpClientFactory`), never one per request. The lab turns reuse off per request with `ConnectionClose`.
- **Python's** `http.client.HTTPConnection` *is* one connection; closing it between requests makes a new one.

The labs count connections differently because each server exposes them differently: Python overrides `process_request`, Go uses `ConnState`, Java counts distinct client ports, Rust counts accepted streams, and C# collects Kestrel's connection IDs.

### Head-of-line blocking without HTTP/2

Python, Java and Rust can't show multiplexing with their standard libraries, so they show the HTTP/1.1 side directly: two requests **pipelined** on one raw socket, slow first, come back in that order, with the fast reply waiting behind the slow one. Python's `BaseHTTPRequestHandler` also needs `protocol_version = "HTTP/1.1"`, or it closes the connection after every response, HTTP/1.0 style.

### What a framework does for you: the Rust server

Rust's lab writes the whole server over `TcpListener`. It reads the request line, reads headers until a blank line, and decides where each response's body ends: with `Content-Length`, or with chunks, each its length in hex. It keeps reading requests on the same connection until the client sends `Connection: close` or hangs up. That loop is keep-alive. It's about a hundred lines, and every one of them is something hyper, axum or any framework does, plus the things this one skips: request bodies, timeouts, header limits, and refusing ambiguous `Content-Length` and `Transfer-Encoding` combinations, the root of request smuggling.

### Chunks: who decides the boundaries

The servers that frame chunks for you (Go, Java, Kestrel, Node) decide where chunks start by when you *flush*: Go's `Flusher.Flush`, Java's `flush` on the response stream, C#'s `FlushAsync`. Each lab flushes after `"hello"` and waits a moment, so the wire shows two chunks, `5` and `6`. Python's `http.server` and the Rust server frame chunks by hand.

## 3. The same results, in every language

| Check | Expected in every language |
|---|---|
| ten requests, connection reused / not reused | 1 connection / 10 connections |
| `/slow` then `/fast` on one HTTP/1.1 connection | slow arrives first; fast waits |
| the same on HTTP/2 (TypeScript, Go, C#) | fast first, on one connection |
| `/style.css`, then again with `If-None-Match` | `200` with `max-age=60`, then `304` with an empty body |
| `/stream` on the wire | `Transfer-Encoding: chunked`, body `5␍␊hello␍␊6␍␊ world␍␊0␍␊␍␊` |

## Terms used in this lesson

1. **Prior knowledge**: In HTTP/2, this is a client starting a connection in HTTP/2 straight away, because it already knows the server speaks it, rather than negotiating.
2. **h2c**: This is HTTP/2 over a plain TCP connection, without TLS.
3. **Connection pool**: This is a set of open connections an HTTP client keeps and reuses for later requests to the same server.
4. **Pipelining**: In HTTP/1.1, this is sending several requests on one connection without waiting for the responses, which must still come back in order.
5. **Flush**: This is pushing buffered output onto the network now, rather than waiting for more.

## 4. Python

`ThreadingHTTPServer` gives each connection a thread; `protocol_version = "HTTP/1.1"` keeps connections open. The chunked response is framed by hand, because `http.server` doesn't do it. The tests use `http.client.HTTPConnection` and raw sockets.

```python
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
```

```python
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
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/11-http-evolution/labs/python). `python3 labs/run.py http-evolution/python`.

## 5. Go

`httptest.NewUnstartedServer` with `Protocols` set to HTTP/1.1 and unencrypted HTTP/2; `ConnState` counts new connections. `Client` builds a transport limited to one connection per host, speaking either version. The ordering test sends the slow request 20 ms before the fast one on each version.

```go
// Package web: the same small site as the TypeScript lab, served by net/http over HTTP/1.1 and HTTP/2. Since Go
// 1.24, net/http speaks HTTP/2 without TLS ("h2c") when asked, on both the server and the client.
package web

import (
	"crypto/sha256"
	"fmt"
	"net"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"time"
)

var (
	asset = []byte("body { color: rebeccapurple; }\n")
	etag  = fmt.Sprintf(`"%x"`, sha256.Sum256(asset))[:17] + `"`
)

func site(w http.ResponseWriter, r *http.Request) {
	switch r.URL.Path {
	case "/fast":
		fmt.Fprint(w, "fast")
	case "/slow":
		time.Sleep(200 * time.Millisecond)
		fmt.Fprint(w, "slow")
	case "/style.css":
		w.Header().Set("ETag", etag)
		if r.Header.Get("If-None-Match") == etag {
			w.WriteHeader(http.StatusNotModified) // headers only
			return
		}
		w.Header().Set("Cache-Control", "max-age=60")
		w.Write(asset)
	case "/stream":
		fmt.Fprint(w, "hello")
		w.(http.Flusher).Flush() // send what we have: without a Content-Length, HTTP/1.1 goes chunked
		time.Sleep(20 * time.Millisecond)
		fmt.Fprint(w, " world")
	default:
		http.NotFound(w, r)
	}
}

// Server starts the site on 127.0.0.1, speaking HTTP/1.1 and h2c, and counts TCP connections.
func Server() (*httptest.Server, *atomic.Int64) {
	var connections atomic.Int64
	server := httptest.NewUnstartedServer(http.HandlerFunc(site))
	server.Config.Protocols = new(http.Protocols)
	server.Config.Protocols.SetHTTP1(true)
	server.Config.Protocols.SetUnencryptedHTTP2(true)
	server.Config.ConnState = func(_ net.Conn, state http.ConnState) {
		if state == http.StateNew {
			connections.Add(1)
		}
	}
	server.Start()
	return server, &connections
}

// Client returns an HTTP client limited to one connection, speaking HTTP/1.1 (with or without keep-alive) or h2c.
func Client(http2, keepAlive bool) *http.Client {
	transport := &http.Transport{MaxConnsPerHost: 1, DisableKeepAlives: !keepAlive, Protocols: new(http.Protocols)}
	if http2 {
		transport.Protocols.SetUnencryptedHTTP2(true) // speak HTTP/2 straight away, with no TLS and no upgrade
	} else {
		transport.Protocols.SetHTTP1(true)
	}
	return &http.Client{Transport: transport}
}
```

```go
package web

import (
	"bufio"
	"io"
	"net"
	"net/http"
	"slices"
	"strings"
	"sync"
	"testing"
	"time"
)

func get(t *testing.T, c *http.Client, url string, header map[string]string) (*http.Response, string) {
	t.Helper()
	req, _ := http.NewRequest("GET", url, nil)
	for k, v := range header {
		req.Header.Set(k, v)
	}
	res, err := c.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	return res, string(body)
}

func TestKeepAliveTenRequestsOneConnection(t *testing.T) {
	for _, c := range []struct {
		keepAlive bool
		want      int64
	}{{false, 10}, {true, 1}} {
		server, connections := Server()
		client := Client(false, c.keepAlive)
		for range 10 {
			get(t, client, server.URL+"/fast", nil)
		}
		server.Close()
		if connections.Load() != c.want {
			t.Fatalf("keepAlive=%v: %d connections", c.keepAlive, connections.Load())
		}
	}
}

// finishOrder sends /slow, then /fast 20 ms later, and records the order the replies finish in.
func finishOrder(t *testing.T, client *http.Client, base string) []string {
	var mu sync.Mutex
	var order []string
	var wg sync.WaitGroup
	for i, path := range []string{"/slow", "/fast"} {
		wg.Go(func() {
			time.Sleep(time.Duration(i) * 20 * time.Millisecond) // the slow request is always sent first
			_, body := get(t, client, base+path, nil)
			mu.Lock()
			order = append(order, body)
			mu.Unlock()
		})
	}
	wg.Wait()
	return order
}

func TestHeadOfLineBlockingAndMultiplexing(t *testing.T) {
	server, connections := Server()
	defer server.Close()
	// HTTP/1.1 with one connection: the fast request waits until the slow one's response has finished.
	if order := finishOrder(t, Client(false, true), server.URL); !slices.Equal(order, []string{"slow", "fast"}) {
		t.Fatal("HTTP/1.1:", order)
	}
	before := connections.Load()
	// HTTP/2: two streams on one connection, so the fast reply overtakes.
	if order := finishOrder(t, Client(true, true), server.URL); !slices.Equal(order, []string{"fast", "slow"}) {
		t.Fatal("HTTP/2:", order)
	}
	if connections.Load()-before != 1 {
		t.Fatal("HTTP/2 used more than one connection")
	}
}

func TestAnETagTurnsASecondDownloadIntoA304(t *testing.T) {
	server, _ := Server()
	defer server.Close()
	client := Client(false, true)
	first, _ := get(t, client, server.URL+"/style.css", nil)
	again, body := get(t, client, server.URL+"/style.css", map[string]string{"If-None-Match": first.Header.Get("ETag")})
	if first.StatusCode != 200 || first.Header.Get("Cache-Control") != "max-age=60" || again.StatusCode != 304 || body != "" {
		t.Fatal(first.StatusCode, again.StatusCode, body)
	}
}

func TestChunkedEncodingOnTheWire(t *testing.T) {
	server, _ := Server()
	defer server.Close()
	conn, err := net.Dial("tcp", strings.TrimPrefix(server.URL, "http://"))
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()
	io.WriteString(conn, "GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n")
	raw, _ := io.ReadAll(bufio.NewReader(conn))
	head, body, _ := strings.Cut(string(raw), "\r\n\r\n")
	if !strings.Contains(head, "Transfer-Encoding: chunked") || body != "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n" {
		t.Fatalf("%q", raw)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/11-http-evolution/labs/go). `python3 labs/run.py http-evolution/go`.

## 6. Java

The JDK's `HttpServer` runs handlers on a virtual-thread executor; `sendResponseHeaders(200, 0)` means "length unknown", so it chunks. Connections are counted by the client's port. The check contrasts one shared `HttpClient` with a new one per request.

```java
package web;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;

/**
 * The same small site as the TypeScript lab, on the JDK's built-in HTTP server. That server speaks HTTP/1.1 only;
 * the JDK's HttpClient speaks HTTP/2, but an HTTP/2 server needs a library such as Jetty or Netty.
 */
public final class Site {
    private Site() {}

    static final byte[] ASSET = "body { color: rebeccapurple; }\n".getBytes(StandardCharsets.UTF_8);
    static final String ETAG;

    static {
        try {
            ETAG = "\"" + HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(ASSET)).substring(0, 16) + "\"";
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    /** The client ports seen: each TCP connection comes from its own port, so this counts connections. */
    public static final Set<Integer> CLIENT_PORTS = ConcurrentHashMap.newKeySet();

    public static HttpServer start() throws IOException {
        var server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);
        server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        server.createContext("/", Site::handle);
        server.start();
        return server;
    }

    private static void handle(HttpExchange ex) throws IOException {
        CLIENT_PORTS.add(ex.getRemoteAddress().getPort());
        try (ex) {
            switch (ex.getRequestURI().getPath()) {
                case "/fast" -> send(ex, 200, "fast");
                case "/slow" -> {
                    sleep(200);
                    send(ex, 200, "slow");
                }
                case "/style.css" -> {
                    ex.getResponseHeaders().set("ETag", ETAG);
                    if (ETAG.equals(ex.getRequestHeaders().getFirst("If-None-Match"))) {
                        ex.sendResponseHeaders(304, -1); // -1: no body at all
                    } else {
                        ex.getResponseHeaders().set("Cache-Control", "max-age=60");
                        ex.sendResponseHeaders(200, ASSET.length);
                        ex.getResponseBody().write(ASSET);
                    }
                }
                case "/stream" -> {
                    ex.sendResponseHeaders(200, 0); // 0 means "length unknown": the server sends it chunked
                    var out = ex.getResponseBody();
                    out.write("hello".getBytes(StandardCharsets.UTF_8));
                    out.flush(); // send this chunk now
                    sleep(20);
                    out.write(" world".getBytes(StandardCharsets.UTF_8));
                }
                default -> ex.sendResponseHeaders(404, -1);
            }
        }
    }

    private static void send(HttpExchange ex, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.sendResponseHeaders(status, bytes.length);
        ex.getResponseBody().write(bytes);
    }

    private static void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

```java
package web;

import java.io.ByteArrayOutputStream;
import java.net.Socket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

/** The same checks as every other language. Run with -ea. */
public final class SiteCheck {
    private SiteCheck() {}

    public static void main(String[] args) throws Exception {
        var server = Site.start();
        int port = server.getAddress().getPort();
        URI base = URI.create("http://127.0.0.1:" + port);
        try {
            // Keep-alive: one HttpClient reuses its connection; a new client per request (a common mistake) can't.
            for (boolean shared : new boolean[] {false, true}) {
                Site.CLIENT_PORTS.clear();
                var one = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
                for (int i = 0; i < 10; i++) {
                    var client = shared ? one : HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
                    var res = client.send(HttpRequest.newBuilder(base.resolve("/fast")).build(), HttpResponse.BodyHandlers.ofString());
                    assert res.body().equals("fast");
                    if (!shared) client.close(); // HttpClient is AutoCloseable since Java 21
                }
                one.close();
                assert Site.CLIENT_PORTS.size() == (shared ? 1 : 10) : shared + ": " + Site.CLIENT_PORTS.size();
            }

            // Head-of-line blocking: two requests pipelined on one connection come back in order, slow first.
            String pipelined = raw(port, "GET /slow HTTP/1.1\r\nHost: shop\r\n\r\nGET /fast HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n");
            assert pipelined.indexOf("slow") < pipelined.indexOf("fast") : pipelined;

            // Revalidation: the second request carries the ETag and gets a 304 with no body.
            try (var client = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build()) {
                var first = client.send(HttpRequest.newBuilder(base.resolve("/style.css")).build(), HttpResponse.BodyHandlers.ofString());
                assert first.statusCode() == 200 && first.headers().firstValue("Cache-Control").orElseThrow().equals("max-age=60");
                var again = client.send(HttpRequest.newBuilder(base.resolve("/style.css"))
                        .header("If-None-Match", first.headers().firstValue("ETag").orElseThrow()).build(), HttpResponse.BodyHandlers.ofString());
                assert again.statusCode() == 304 && again.body().isEmpty();
            }

            // Chunked encoding, as bytes on the wire.
            String stream = raw(port, "GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n");
            String head = stream.substring(0, stream.indexOf("\r\n\r\n"));
            String body = stream.substring(stream.indexOf("\r\n\r\n") + 4);
            assert head.toLowerCase().contains("transfer-encoding: chunked") : head;
            assert body.equals("5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n") : body;
        } finally {
            server.stop(0);
        }
        System.out.println("all http checks passed");
    }

    /** Sends raw bytes on a fresh connection and reads until the server closes it. */
    static String raw(int port, String request) throws Exception {
        try (var socket = new Socket("127.0.0.1", port)) {
            socket.getOutputStream().write(request.getBytes(StandardCharsets.US_ASCII));
            var out = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(out);
            return out.toString(StandardCharsets.US_ASCII);
        }
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/11-http-evolution/labs/java). `python3 labs/run.py http-evolution/java`.

## 7. Rust

The server is written from scratch: `serve_connection` loops over requests on one connection, parsing the request line and headers, and writes each response with a `Content-Length` or as chunks. `get` is a matching minimal client that reads exactly one response by its `Content-Length`, so it can send the next request on the same connection.

```rust
//! A minimal HTTP/1.1 server written by hand over std's TcpListener: Rust's standard library has no HTTP at all
//! (hyper and axum are the usual crates, and they add HTTP/2). Writing it shows what a framework does for you:
//! read a request line and headers, decide where the body ends, and keep the connection for the next request.
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;

const ASSET: &str = "body { color: rebeccapurple; }\n";
const ETAG: &str = "\"v1-rebeccapurple\""; // any fingerprint of the content works

/// Starts the site on 127.0.0.1 and returns its port and a count of accepted TCP connections.
pub fn start() -> (u16, Arc<AtomicUsize>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let port = listener.local_addr().expect("address").port();
    let connections = Arc::new(AtomicUsize::new(0));
    let counter = connections.clone();
    std::thread::spawn(move || {
        for stream in listener.incoming().flatten() {
            counter.fetch_add(1, Ordering::SeqCst);
            std::thread::spawn(move || serve_connection(stream));
        }
    });
    (port, connections)
}

/// Answers requests on one connection until the client closes it or asks to (keep-alive is HTTP/1.1's default).
fn serve_connection(stream: TcpStream) {
    let mut reader = BufReader::new(stream.try_clone().expect("clone"));
    let mut out = stream;
    loop {
        let mut request_line = String::new();
        if reader.read_line(&mut request_line).unwrap_or(0) == 0 {
            return; // the client closed the connection
        }
        let path = request_line
            .split_whitespace()
            .nth(1)
            .unwrap_or("/")
            .to_string();
        let (mut if_none_match, mut close) = (None, false);
        loop {
            let mut header = String::new();
            reader.read_line(&mut header).expect("a header line");
            let header = header.trim_end();
            if header.is_empty() {
                break; // a blank line ends the headers; these GETs have no body
            }
            let (name, value) = header.split_once(':').unwrap_or((header, ""));
            match name.to_ascii_lowercase().as_str() {
                "if-none-match" => if_none_match = Some(value.trim().to_string()),
                "connection" => close = value.trim().eq_ignore_ascii_case("close"),
                _ => {}
            }
        }
        let response = match path.as_str() {
            "/fast" => text("200 OK", "fast"),
            "/slow" => {
                std::thread::sleep(Duration::from_millis(200));
                text("200 OK", "slow")
            }
            "/style.css" if if_none_match.as_deref() == Some(ETAG) => {
                format!("HTTP/1.1 304 Not Modified\r\nETag: {ETAG}\r\n\r\n")
            }
            "/style.css" => format!(
                "HTTP/1.1 200 OK\r\nETag: {ETAG}\r\nCache-Control: max-age=60\r\nContent-Length: {}\r\n\r\n{ASSET}",
                ASSET.len()
            ),
            "/stream" => {
                // No Content-Length: frame the body as chunks, each its length in hex, ended by a zero-length chunk.
                let chunks = ["hello", " world"]
                    .iter()
                    .map(|c| format!("{:x}\r\n{c}\r\n", c.len()))
                    .collect::<String>();
                format!("HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n{chunks}0\r\n\r\n")
            }
            _ => text("404 Not Found", ""),
        };
        if out.write_all(response.as_bytes()).is_err() || close {
            return;
        }
    }
}

fn text(status: &str, body: &str) -> String {
    format!(
        "HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{body}",
        body.len()
    )
}

/// Sends one GET on an open connection and reads exactly one response, using its Content-Length.
pub fn get(stream: &mut TcpStream, path: &str, extra_header: &str) -> (u16, String) {
    write!(
        stream,
        "GET {path} HTTP/1.1\r\nHost: shop\r\n{extra_header}\r\n"
    )
    .expect("send");
    let mut reader = BufReader::new(stream.try_clone().expect("clone"));
    let mut status_line = String::new();
    reader.read_line(&mut status_line).expect("status line");
    let status = status_line
        .split_whitespace()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .expect("a status code");
    let mut length = 0;
    loop {
        let mut header = String::new();
        reader.read_line(&mut header).expect("header");
        if header.trim_end().is_empty() {
            break;
        }
        if let Some(value) = header.to_ascii_lowercase().strip_prefix("content-length:") {
            length = value.trim().parse().expect("a length");
        }
    }
    let mut body = vec![0; length];
    reader.read_exact(&mut body).expect("body");
    (status, String::from_utf8(body).expect("utf-8"))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn connect(port: u16) -> TcpStream {
        TcpStream::connect(("127.0.0.1", port)).expect("connect")
    }

    #[test]
    fn keep_alive_ten_requests_one_connection() {
        for (reuse, expected) in [(false, 10), (true, 1)] {
            let (port, connections) = start();
            let mut shared = reuse.then(|| connect(port));
            for _ in 0..10 {
                let mut fresh = None;
                let stream = match shared.as_mut() {
                    Some(stream) => stream,
                    None => fresh.insert(connect(port)), // a new TCP connection for each request
                };
                assert_eq!(get(stream, "/fast", "").1, "fast");
            }
            // Each response arrived after the server accepted (and counted) its connection: no waiting needed.
            assert_eq!(connections.load(Ordering::SeqCst), expected);
        }
    }

    #[test]
    fn head_of_line_blocking_on_one_connection() {
        let (port, _) = start();
        let mut stream = connect(port);
        stream.write_all(b"GET /slow HTTP/1.1\r\nHost: shop\r\n\r\nGET /fast HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n").unwrap();
        let mut all = String::new();
        stream.read_to_string(&mut all).unwrap();
        assert!(all.find("slow").unwrap() < all.find("fast").unwrap()); // answered in order: fast waited
    }

    #[test]
    fn an_etag_turns_a_second_download_into_a_304() {
        let (port, _) = start();
        let mut stream = connect(port);
        assert_eq!(get(&mut stream, "/style.css", "").0, 200);
        assert_eq!(
            get(
                &mut stream,
                "/style.css",
                &format!("If-None-Match: {ETAG}\r\n")
            ),
            (304, String::new())
        );
    }

    #[test]
    fn chunked_encoding_on_the_wire() {
        let (port, _) = start();
        let mut stream = connect(port);
        stream
            .write_all(b"GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n")
            .unwrap();
        let mut raw = String::new();
        stream.read_to_string(&mut raw).unwrap();
        let (head, body) = raw.split_once("\r\n\r\n").unwrap();
        assert!(head.contains("Transfer-Encoding: chunked"));
        assert_eq!(body, "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n");
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/11-http-evolution/labs/rust). `python3 labs/run.py http-evolution/rust`.

## 8. C#

Kestrel listens on two loopback ports, one HTTP/1.1 and one HTTP/2-only, with minimal-API routes. A middleware records connection IDs. `HttpClient` with `MaxConnectionsPerServer = 1` shows head-of-line blocking on HTTP/1.1 and multiplexing on HTTP/2. It runs in the .NET SDK container.

```csharp
// The same small site as the TypeScript lab, on Kestrel: HTTP/1.1 on one port and HTTP/2 without TLS on another.
// Without TLS there's no ALPN to choose a version, so an h2c endpoint must speak HTTP/2 only.
using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.AspNetCore.Server.Kestrel.Core;

public static class Site
{
    static readonly byte[] Asset = Encoding.UTF8.GetBytes("body { color: rebeccapurple; }\n");
    static readonly string ETag = $"\"{Convert.ToHexStringLower(SHA256.HashData(Asset))[..16]}\"";

    /// <summary>Kestrel's connection IDs seen: one per TCP connection.</summary>
    public static readonly ConcurrentDictionary<string, bool> Connections = new();

    public static async Task<(WebApplication App, int Http1Port, int Http2Port)> StartAsync()
    {
        var builder = WebApplication.CreateSlimBuilder();
        builder.Logging.ClearProviders();
        builder.WebHost.ConfigureKestrel(k =>
        {
            k.Listen(System.Net.IPAddress.Loopback, 0, o => o.Protocols = HttpProtocols.Http1);
            k.Listen(System.Net.IPAddress.Loopback, 0, o => o.Protocols = HttpProtocols.Http2); // h2c: prior knowledge only
        });
        var app = builder.Build();
        app.Use(async (context, next) =>
        {
            Connections.TryAdd(context.Connection.Id, true);
            await next();
        });
        app.MapGet("/fast", () => "fast");
        app.MapGet("/slow", async () =>
        {
            await Task.Delay(200);
            return "slow";
        });
        app.MapGet("/style.css", (HttpContext context) =>
        {
            context.Response.Headers.ETag = ETag;
            if (context.Request.Headers.IfNoneMatch == ETag) return Results.StatusCode(304); // headers only
            context.Response.Headers.CacheControl = "max-age=60";
            return Results.Bytes(Asset, "text/css");
        });
        app.MapGet("/stream", async (HttpContext context) =>
        {
            await context.Response.WriteAsync("hello"); // no Content-Length: HTTP/1.1 goes chunked
            await context.Response.Body.FlushAsync();
            await Task.Delay(20);
            await context.Response.WriteAsync(" world");
        });
        await app.StartAsync();
        var ports = app.Services.GetRequiredService<Microsoft.AspNetCore.Hosting.Server.IServer>().Features.Get<IServerAddressesFeature>()!
            .Addresses.Select(a => new Uri(a).Port).ToArray();
        return (app, ports[0], ports[1]);
    }
}
```

```csharp
// Checks: the same results as every other language, plus HTTP/2 multiplexing.
using System.Net;
using System.Net.Sockets;
using System.Text;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var (app, http1, http2) = await Site.StartAsync();

// One connection per client at most, as on a browser's busy origin.
HttpClient Client(int port, bool http2Only) => new(new SocketsHttpHandler { MaxConnectionsPerServer = 1 })
{
    BaseAddress = new Uri($"http://127.0.0.1:{port}"),
    DefaultRequestVersion = http2Only ? HttpVersion.Version20 : HttpVersion.Version11,
    DefaultVersionPolicy = HttpVersionPolicy.RequestVersionExact, // h2c: speak HTTP/2 straight away, no upgrade
};

// Keep-alive: ten requests on one connection, unless each request asks to close it.
foreach (var (keepAlive, expected) in new[] { (false, 10), (true, 1) })
{
    Site.Connections.Clear();
    using var client = Client(http1, false);
    for (var i = 0; i < 10; i++)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, "/fast");
        request.Headers.ConnectionClose = !keepAlive;
        using var response = await client.SendAsync(request);
        Check(await response.Content.ReadAsStringAsync() == "fast", "fast");
    }
    Check(Site.Connections.Count == expected, (keepAlive, Site.Connections.Count));
}

// The slow request first, the fast one 20 ms later; record the order they finish in.
async Task<string[]> FinishOrder(HttpClient client)
{
    var order = new List<string>();
    async Task Fetch(string path, int delay)
    {
        await Task.Delay(delay);
        var body = await client.GetStringAsync(path);
        lock (order) order.Add(body);
    }
    await Task.WhenAll(Fetch("/slow", 0), Fetch("/fast", 20));
    return [.. order];
}
using (var one = Client(http1, false)) Check((await FinishOrder(one)).SequenceEqual(["slow", "fast"]), "HTTP/1.1 order");
Site.Connections.Clear();
using (var multiplexed = Client(http2, true)) Check((await FinishOrder(multiplexed)).SequenceEqual(["fast", "slow"]), "HTTP/2 order");
Check(Site.Connections.Count == 1, Site.Connections.Count);

// Revalidation.
using (var client = Client(http1, false))
{
    using var first = await client.GetAsync("/style.css");
    Check(first.StatusCode == HttpStatusCode.OK && first.Headers.CacheControl?.MaxAge == TimeSpan.FromSeconds(60), first.StatusCode);
    using var request = new HttpRequestMessage(HttpMethod.Get, "/style.css");
    request.Headers.IfNoneMatch.Add(first.Headers.ETag!);
    using var again = await client.SendAsync(request);
    Check(again.StatusCode == HttpStatusCode.NotModified && (await again.Content.ReadAsStringAsync()) == "", again.StatusCode);
}

// Chunked encoding, as bytes on the wire.
using (var socket = new TcpClient())
{
    await socket.ConnectAsync(IPAddress.Loopback, http1);
    var stream = socket.GetStream();
    await stream.WriteAsync(Encoding.ASCII.GetBytes("GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n"));
    var raw = await new StreamReader(stream, Encoding.ASCII).ReadToEndAsync();
    var split = raw.IndexOf("\r\n\r\n");
    Check(raw[..split].Contains("Transfer-Encoding: chunked"), raw[..split]);
    Check(raw[(split + 4)..] == "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n", raw[(split + 4)..]);
}
await app.StopAsync();
Console.WriteLine("all http checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/11-http-evolution/labs/csharp). `python3 labs/run.py http-evolution/csharp`.

## Common pitfalls

1. **A new HTTP client per request** (Java's `HttpClient`, C#'s `HttpClient`, Python's `requests` without a `Session`). Every request pays new handshakes.
2. **Python's `BaseHTTPRequestHandler` with the default `protocol_version`.** It's HTTP/1.0: no keep-alive.
3. **Expecting h2c to negotiate.** Without TLS there's no ALPN; both sides must be configured for HTTP/2 explicitly.
4. **Forgetting to flush a streamed response.** The client sees nothing until the buffer fills or the response ends.
5. **Hand-written HTTP parsing in production.** The Rust lab's server skips limits, timeouts and smuggling defences; use hyper or a framework.

## Check your understanding

1. Why does a new Java `HttpClient` per request open a new connection every time, while one shared client reuses a single connection?
2. Why must Kestrel's h2c endpoint be HTTP/2-only, when over TLS one endpoint can serve both versions?
3. The Python server answers correctly but every request opens a new connection, even with one `HTTPConnection`. What's the likely cause?
4. In the Rust server, what tells it where one request ends and the next begins, and why doesn't it need `Content-Length` for these requests?
5. Which standard libraries can show HTTP/2 multiplexing, and what do the others show instead?

<details>
<summary>Answers — after your attempt</summary>

1. Each `HttpClient` owns its own connection pool. A new client has an empty pool, so it must connect; the shared client finds its earlier connection idle in the pool and reuses it.
2. Over TLS, the client says which version it wants in the handshake (ALPN). Without TLS there's no handshake to say it in, and an HTTP/2 connection's first bytes look nothing like an HTTP/1.1 request, so the server must know in advance which one the endpoint speaks.
3. `protocol_version` is still the default `"HTTP/1.0"`, so the server closes the connection after each response, and `http.client` has to reconnect.
4. The blank line after the headers ends each request. These are `GET`s with no body, so nothing follows the blank line; a request with a body would need its `Content-Length` or chunked framing to find where the body, and so the request, ends.
5. Node's, Go's and C#'s (with Kestrel). Python, Java (server side) and Rust show the HTTP/1.1 side instead: two requests pipelined on one connection come back in order, with the fast one stuck behind the slow one.

</details>

## Practice — independent task

**Extend the Rust server, and break it on purpose.**

1. Add `POST /echo`, which reads a request body using `Content-Length` and sends it back.
2. Add support for a chunked *request* body.
3. Send a request with both `Content-Length: 5` and `Transfer-Encoding: chunked`, and decide what your server should do. Then look up what RFC 9112 says, and make it do that.

**Done when:** both body framings work, the ambiguous request gets the response the RFC requires, and you can explain in two sentences how disagreement over that request becomes request smuggling.

## Before moving on

You can say what your language's standard library can do with HTTP/1.1 and HTTP/2, reuse connections correctly with its client, and read and write HTTP/1.1 messages by hand.

**Recap.** HTTP is the same protocol everywhere, but the standard libraries differ: Node, Go and C# (Kestrel) serve and request HTTP/2, including h2c with explicit configuration; Java's client speaks it and its built-in server doesn't; Python's standard library is HTTP/1.1 only; and Rust's has no HTTP, so writing a server by hand shows the request line, headers, blank line, body framing and keep-alive loop a framework hides. Share one client so its connection pool can reuse connections, flush to stream chunks, and leave production parsing to libraries that defend against smuggling.

## Related

- [[networking/11-http-evolution/index|HTTP and its evolution]]: the main lesson
- [[networking/10-dns-in-depth/in-other-languages|DNS in other languages]]: the lookup before the connection, in the same languages
- [[networking/12-tls-and-transport-security/index|TLS]]: where HTTP/2's version is negotiated, with ALPN
