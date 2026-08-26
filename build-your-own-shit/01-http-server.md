# Build Your Own HTTP Server

**[Intermediate]** — The most tractable build on this list, and the one that teaches you the most per hour. A weekend gets you something that serves a real browser.

## What you're building

An HTTP/1.1 server that accepts TCP connections, parses requests, routes them, and writes responses. By the end it will serve a static site to a real browser, handle keep-alive, and survive concurrent clients.

**What you're deliberately not building:** TLS (put a reverse proxy in front), HTTP/2 or HTTP/3 (a different protocol with binary framing and multiplexing — a separate project), a full framework (no templating, no ORM, no middleware ecosystem), or anything production-facing.

**Why this one first:** HTTP/1.1 is text-based and readable, you can test with `curl` and `telnet`, feedback is immediate, and every milestone produces something that visibly works.

## What you need first

| You should know | Where |
|---|---|
| **Sockets** — `socket`/`bind`/`listen`/`accept`, and what a file descriptor is | [[foundations/networking/09-sockets-and-the-network-api\|networking/09]] |
| **TCP basics** — the connection lifecycle, why `TIME_WAIT` exists | [[foundations/networking/06-tcp-connection-lifecycle\|networking/06]] |
| **HTTP semantics** — methods, status codes, headers | [[foundations/networking/11-http-evolution\|networking/11]] |
| **Blocking vs non-blocking I/O** | [[foundations/os/08-io-models\|os/08]] |
| **Processes and threads** (for the concurrency milestone) | [[foundations/os/02-processes-and-threads\|os/02]] |

You **don't** need: parsing theory (the grammar is trivial), TLS knowledge, or any framework experience.

**If you're doing this in C**, read [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]] before milestone 2 — every byte you parse is attacker-controlled and the language gives you no bounds checking.

## The build order

Each milestone runs and is testable on its own. **Do not skip ahead** — the ordering is chosen so you always have something working.

### 1. Accept a connection and say hello

Ignore the request entirely. Accept, write a fixed response, close.

```
socket() → bind() → listen() → accept() → write() → close()
```

```http
HTTP/1.1 200 OK
Content-Length: 13
Content-Type: text/plain

Hello, world!
```

**Test:** `curl -v localhost:8080` shows the response. Open it in a browser.

**Watch for:** `SO_REUSEADDR`, or restarting fails with "address already in use" for up to two minutes. And **the blank line before the body is mandatory** — `\r\n\r\n` terminates the headers. Getting this wrong makes `curl` hang, and it's the single most common first-hour bug.

### 2. Parse the request line

**Build the parser before the router.** Everything downstream depends on knowing what was actually requested.

```
GET /path?query=1 HTTP/1.1
```

Split into method, target, version. Reject anything malformed with `400`.

**Test:** print what you parsed for various `curl` calls. `curl -X POST`, `curl 'localhost:8080/a?b=c'`.

**Watch for:** the line ends with `\r\n`, not `\n` — but be lenient on read and strict on write. **Bound the length** (8KB is the conventional cap) or a client sending an infinite line exhausts your memory. Return `414` when it's exceeded.

### 3. Parse headers

```
Host: localhost:8080
User-Agent: curl/8.0
Content-Length: 42
```

`Name: value` per line until a blank line. Store them case-insensitively — `Content-Length` and `content-length` are the same header.

**Test:** echo the headers back in the response body.

**Watch for:** cap the header count (~100) and total size. Values can have leading whitespace. **Duplicate `Content-Length` headers must be rejected** — that's a request-smuggling vector, not a curiosity.

### 4. Write proper responses

A response builder: status line, headers, blank line, body — with `Content-Length` computed automatically.

```
HTTP/1.1 404 Not Found
Content-Type: text/plain
Content-Length: 9
Connection: close

Not Found
```

**Test:** trigger 200, 404, and 400. Check `curl -v` reports the right statuses.

**Watch for:** `Content-Length` must be the **byte** count, not the character count — an accented character is two bytes in UTF-8. A wrong length makes the client hang waiting for bytes that never come, or truncate.

### 5. Routing

Map (method, path) to a handler. Start with exact matches, then add parameters (`/users/{id}`).

```
GET  /           → index
GET  /users/{id} → get_user
POST /users      → create_user
*                → 404
```

**Test:** each route returns something distinct. An unknown path 404s; a known path with the wrong method 405s.

**Watch for:** decide early whether `/users` and `/users/` are the same route. Match the query string *off* before routing.

### 6. Serve static files

Map a URL path to a file under a document root. Guess `Content-Type` from the extension.

**Test:** serve an HTML page with a CSS file and an image. Load it in a browser — it should render fully.

**Watch for — this is the security milestone:**

```
GET /../../etc/passwd
GET /..%2f..%2fetc%2fpasswd        ← URL-encoded
GET /..%252f                        ← double-encoded
```

**URL-decode exactly once**, reject any remaining `..` or NUL byte, then resolve the real path and verify it's still under the document root. Rejecting `..` by substring alone is insufficient. → [[cybersecurity/04-web-security/README|Web Security]]

Also: don't read the whole file into memory. Stream it.

### 7. Keep-alive

HTTP/1.1 defaults to persistent connections. Don't close after one response — loop, reading the next request from the same socket.

**Test:** `curl -v localhost:8080/a localhost:8080/b` should show one connection reused ("Re-using existing connection").

**Watch for:** you must know exactly where one request ends and the next begins, which means reading precisely `Content-Length` bytes of body — no more. **This is where buffer management gets real**, because a read may return part of one request or several. Add an idle timeout, or connections accumulate forever.

### 8. Concurrency

Pick one:

- **Thread per connection** — simplest, fine to a few thousand
- **Thread pool** — bounded, better under load
- **Event loop** — one thread, `epoll`/`kqueue`. Scales furthest, hardest
- **Process per connection** — robust and expensive

**Test:** `ab -n 1000 -c 50 http://localhost:8080/` or `wrk`. Compare against your single-threaded version.

**Watch for:** shared state now needs synchronisation. **Ignore `SIGPIPE`** (or use `MSG_NOSIGNAL`), or a client disconnecting mid-response kills your process. → [[foundations/os/10-signals-and-ipc|Signals]]

If you choose the event loop, you'll need a **per-connection state machine** — a request can arrive across several reads, so parser state can't live on the stack. → [[backend/frameworks/c/01-the-accept-loop-and-event-loops|The Accept Loop]]

### 9. Chunked transfer encoding

For responses whose length isn't known upfront.

```
HTTP/1.1 200 OK
Transfer-Encoding: chunked

7\r\nMozilla\r\n
9\r\nDeveloper\r\n
0\r\n\r\n
```

**Test:** stream a slow response and watch `curl` receive it incrementally.

**Watch for:** chunk sizes are **hexadecimal**. The terminating `0` chunk needs its own trailing `\r\n`. Reject any request with both `Content-Length` and `Transfer-Encoding` — the classic smuggling vector.

## Per-language toolkit

What each language gives you per milestone, and what a library would add.

| Milestone | C | C++ | Rust | Go | Python | JS/Node |
|---|---|---|---|---|---|---|
| **Sockets** | `<sys/socket.h>` | same, or **asio** | `std::net::TcpListener` | `net.Listen` | `socket` | `net.createServer` |
| **Parsing** | by hand; **llhttp**, **picohttpparser** | by hand; **Boost.Beast** | by hand; **httparse** | `net/http` has one; **`bufio.Scanner`** | by hand; `h11` | by hand; **llhttp** |
| **Routing** | by hand | by hand | by hand; `matchit` | by hand; `http.ServeMux` (1.22+) | by hand | by hand |
| **Static files** | `open`/`sendfile` | `std::filesystem` | `std::fs` | `http.ServeFile` | `pathlib` | `fs.createReadStream` |
| **Concurrency** | `pthread`, `fork`, `epoll` | `std::thread`, asio | `std::thread`, **tokio** | **goroutines** | `threading`, `asyncio` | the event loop (built in) |
| **Testing** | `curl`, Unity | Catch2 | `#[test]`, `reqwest` | `httptest` | `pytest`, `requests` | `supertest` |

**Language-specific advice:**

**Go** — the standard library already contains a complete server, so **use only `net.Listen` and do the rest yourself**, or you're not building anything. Goroutines make milestone 8 nearly free, which is the point of the language. → [[backend/frameworks/go/01-net-http-in-depth|net/http in Depth]]

**Rust** — `std::net` for a blocking version first; tokio for the async one. The borrow checker will push you toward the right buffer ownership, which is genuinely instructive. → [[languages/03-rust/README|Rust]]

**C** — the most educational and the most dangerous. Read [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]] first, bound every buffer, and build with `-fsanitize=address,undefined`.

**Python** — fastest to a working server; `asyncio` for milestone 8. You'll learn the protocol without fighting the language.

**JS/Node** — the event loop is already there, so milestone 8 is free — which also means you skip learning it. Use `net`, never `http`.

## The parts that will bite you

**`\r\n` vs `\n`.** The spec says CRLF. Be lenient reading, strict writing. Mixing them causes failures that look like nothing at all.

**Reading is not message-framed.** TCP is a byte stream — one `read()` may return half a request, or two. You need a buffer that accumulates until you have a complete message, and retains the remainder. **This is the single hardest part of the whole build**, and it's why milestone 7 is where people get stuck.

**`Content-Length` in bytes, not characters.**

**Partial writes.** `write()` returning less than you asked is normal, not an error. Loop until everything is sent.

**Not draining the request body.** If you don't read the body, the next request on a keep-alive connection starts mid-garbage.

**Path traversal.** Milestone 6. Get it wrong and you serve `/etc/passwd`.

**`SIGPIPE`.** It kills your process by default.

**Header injection.** If a user-controlled value ends up in a response header, a `\r\n` in it lets them inject arbitrary headers. Strip CR and LF from every header value you write.

## How to know it works

```bash
curl -v localhost:8080/                       # the basics
curl -v --http1.1 -H "Connection: keep-alive" localhost:8080/a localhost:8080/b
printf 'GET / HTTP/1.1\r\nHost: x\r\n\r\n' | nc localhost 8080    # raw protocol
curl -v localhost:8080/../../etc/passwd       # must 400 or 404
ab -n 1000 -c 50 http://localhost:8080/       # load
wrk -t4 -c100 -d10s http://localhost:8080/
```

**A real browser is the best integration test.** Serve an HTML page with CSS, an image, and a favicon. Browsers make concurrent keep-alive requests, send conditional headers, and are unforgiving about framing — if Chrome renders your page fully, the core is right.

**Compare against a reference.** Run `python3 -m http.server` and diff the raw bytes for the same request.

**Fuzz the parser** if you're in C or C++:

```bash
clang -fsanitize=fuzzer,address,undefined fuzz.c parser.c -o fuzzer && ./fuzzer corpus/
```

**Unit-test the parser separately from the socket layer.** Feed it byte strings, including ones split at awkward boundaries (`"GET /"` then `" HTTP/1.1\r\n"`) — that split case is where framing bugs hide.

## Where to stop

**Stop at milestone 8 or 9.** You'll have learned:

- How TCP becomes HTTP, and where framing lives
- Why buffering and partial reads are the hard part
- What every framework's router is doing
- Why timeouts, body limits and path validation are non-negotiable
- What an event loop is, from the inside

**Do not ship it.** Real servers handle: TLS, HTTP/2 and /3, compression, caching semantics (ETag, `If-Modified-Since`, `Vary`), range requests, WebSocket upgrades, connection limits, slowloris defence, graceful shutdown, and a decade of CVE fixes in their parsers.

**If you want to go further**, the interesting extensions in order: an `epoll` event loop (if you didn't), WebSocket upgrade (a satisfying, self-contained protocol), then HTTP/2 — binary framing, HPACK header compression, and stream multiplexing, which is a genuinely different and much larger project.

The natural follow-on from here is **your own Redis** (guide 03, planned) — same socket handling, a simpler protocol, and it moves the focus to data structures and persistence.

---

## Related
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]] — the syscalls
- [[foundations/os/08-io-models|I/O Models]] — blocking, epoll, io_uring
- [[backend/frameworks/c/01-the-accept-loop-and-event-loops|C: The Accept Loop]] — milestone 8 in depth
- [[backend/frameworks/c/02-parsing-http-safely|C: Parsing HTTP Safely]] — read before milestone 2 if you're in C
- [[build-your-own-shit/README|build-your-own-shit]]
