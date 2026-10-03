# HTTP and Its Evolution

**[Intermediate]** — The application protocol that ate the internet. The interesting story isn't the syntax, which you already know. It's that **three decades of HTTP versions are all fighting the same enemy: round trips, and one slow thing blocking everything behind it.** Understand that, and every version's design choices are obvious. The lab makes each one visible on your own machine: connections saved by keep-alive, a fast reply stuck behind a slow one on HTTP/1.1 and overtaking it on HTTP/2, a `304 Not Modified`, and chunked encoding as raw bytes.

## Before you start

You can already:

- Explain a TCP connection and its handshake, and that TCP delivers bytes in order → [[networking/06-tcp-connection-lifecycle|TCP connection lifecycle]] (a skim is enough).
- Make HTTP requests from code and read status codes and headers.
- Explain `Cache-Control` and why caches serve stale data → [[architecture/02-building-blocks/02-caching/index|caching]].
- Run a TypeScript test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Explain what each HTTP version changed, in terms of round trips and head-of-line blocking.
2. Predict how many connections and round trips a page costs on HTTP/1.1 with and without keep-alive, and on HTTP/2.
3. Use caching headers so repeat visits cost nothing or a `304`, and say which methods may safely be retried.
4. Read an HTTP/1.1 response on the wire, including chunked encoding, and explain why disagreements about message length cause request smuggling.

**Study route:** sections 1–3 cover HTTP/1.1. Stop at the predictions in sections 3 and 5 and try them before reading on. Section 7 is the lab. Then read [[networking/12-tls-and-transport-security/index|TLS]], which this connection runs inside.

## The kid version first

You're ordering from a shop by post.

- **HTTP/0.9–1.0:** send one letter, get one reply, and the shop closes the mail channel. Next order? Set up the whole channel again. Exhausting.
- **HTTP/1.1:** the channel stays open between orders. Better, but you must wait for order 1's reply before sending order 2. One slow item blocks everything behind it.
- **HTTP/2:** you may send all your orders at once down the same channel, and replies come back interleaved. Except the *postal service* still delivers everything in strict order, so one lost envelope still stalls the lot.
- **HTTP/3:** change the postal service too. Now a lost envelope only delays its own order.

**Where the analogy stops working.** Letters don't share a channel the way a TCP connection does: the "strict order" in HTTP/2 is TCP refusing to hand over any bytes after a missing packet, for every stream at once. That's a property of the transport underneath HTTP, which is why fixing it meant replacing TCP with [[networking/13-quic-and-modern-transport|QUIC]] rather than changing HTTP again.

## 1. Why this exists

The shop's product page makes 60 requests: the HTML, scripts, style sheets, images and API calls. On a phone with 100 ms of round-trip time, each new connection costs a TCP handshake and a TLS handshake before any data moves. Each request on HTTP/1.1 then waits for the one before it on the same connection. The browser opens six connections per origin to compensate, the old performance advice says to shard assets across domains and bundle everything into one file, and much of that advice now makes things slower. Knowing what each HTTP version actually changed tells you which of the shop's performance habits to keep.

## Terms used in this lesson

1. **HTTP (Hypertext Transfer Protocol)**: The letters stand for those words. It's the request-and-response protocol of the web: a method and path go out, a status, headers and body come back.
2. **Round trip**: This is a message going to the server and its reply coming back. On a phone network, one can take 50–150 ms.
3. **Persistent connection**: This is also called **keep-alive**. It's reusing one TCP connection for many requests, instead of opening a new one each time.
4. **Head-of-line blocking**: This is one slow or lost item at the front of a queue holding up everything behind it.
5. **Multiplexing**: This is sending several independent requests and responses over one connection at the same time, interleaved.
6. **Stream**: In HTTP/2, this is one request and its response, carried as numbered frames on a shared connection.
7. **Chunked transfer encoding**: This is sending an HTTP/1.1 body in pieces, each preceded by its length, when the total length isn't known at the start.
8. **ETag**: This is a response header holding a fingerprint of the content, which a client sends back in `If-None-Match` to ask "has it changed?".
9. **Idempotent**: A method is idempotent when sending it twice has the same effect as sending it once, so it can be retried safely.
10. **Request smuggling**: This is an attack that exploits two servers disagreeing about where one request ends and the next begins.

## 2. HTTP/1.1: the version whose flaws defined the web

Text-based, request-response, and stateless by design. It has two defining problems:

1. **Head-of-line blocking at the application layer.** One connection carries one request at a time: request 2 waits for response 1 to finish. **Pipelining**, sending several requests without waiting, was specified but is effectively dead, because responses still had to come back *in order*, so a slow first response blocked the rest anyway, and buggy proxies mishandled it. Every major browser has it switched off.
2. **Verbose, repetitive headers.** Every request re-sends the same cookies, `User-Agent` and `Accept` headers, often hundreds of bytes of identical, uncompressed text per request, on a page making 80 requests.

The workarounds the industry built around these limits are worth naming, because **HTTP/2 made all of them obsolete, and many codebases still carry them**:

- **Six parallel connections per origin**: the browsers' brute-force fix, and why a page's requests arrive in waves of six.
- **Domain sharding**: serving assets from `img1.example.com`, `img2.example.com` to get six connections *each*. Now actively harmful: it defeats HTTP/2 multiplexing and multiplies DNS lookups and TCP and TLS handshakes.
- **Concatenation and spriting**: bundling all scripts into one file and all icons into one image. Under HTTP/2 it hurts caching: change one line, and everyone downloads everything again.
- **Inlining**: base64-encoding images into style sheets. The same problem, and it defeats caching entirely.

If you're doing performance work on an existing codebase, checking whether these HTTP/1.1-era workarounds are still in place is often the highest-value single audit.

## 3. The parts of HTTP/1.1 worth knowing precisely

**Statelessness, and how it's worked around.** The server keeps no memory between requests. Cookies, tokens and sessions exist to reintroduce state on top, which is what makes horizontal scaling easy (any server can handle any request) and is the basis of the [[backend/05-auth/01-authentication-flows|authentication flows]].

**Persistent connections.** `Connection: keep-alive` is the default in HTTP/1.1, and its single biggest performance feature, because it amortises the [[networking/06-tcp-connection-lifecycle|TCP handshake]] and the [[networking/12-tls-and-transport-security/index|TLS handshake]], and lets [[networking/08-congestion-control|congestion control]] get past slow start.

**Predict before reading on.** A client makes ten requests in a row to the same server, one at a time. How many TCP connections does the server see with keep-alive off, and with it on?

<details>
<summary>After your prediction</summary>

**Ten** without keep-alive, and **one** with it. Over the internet, each of those nine extra connections is a TCP handshake, plus a TLS handshake for HTTPS: one or two more round trips each, before the request is even sent. The lab counts the server's `connection` events for both.

</details>

**Content-Length or chunked encoding.** The receiver needs to know where a response ends. Either the sender declares the length up front, or it uses `Transfer-Encoding: chunked` and sends length-prefixed chunks ending with a zero-length one, which is necessary for generated or streamed content. On the wire, in the lab:

```
HTTP/1.1 200 OK
Transfer-Encoding: chunked

5
hello
6
 world
0

```

Each chunk is its length in hexadecimal, a line break, the bytes, and a line break; `0` ends the body. Where the chunks start and end is the sender's choice: in the lab, two writes in the same tick of the event loop went out as one chunk of 11 bytes (`b`), until the second write was delayed. Getting the interaction between `Content-Length` and chunked encoding wrong, where a front-end proxy and a back-end server disagree about which one governs, is exactly the **request smuggling** vulnerability class → [[cybersecurity/04-web-security/index|web security]].

**Caching**, the most under-used performance tool in the protocol:

- `Cache-Control: max-age=N`: fresh for N seconds, with no request at all.
- `ETag` with `If-None-Match`: revalidate cheaply. A `304 Not Modified` sends headers only. In the lab, the style sheet's second request, carrying its `ETag`, gets a `304` with an empty body.
- `immutable` for assets whose names contain a hash of their content, and `stale-while-revalidate` to serve a stale copy at once while refreshing in the background.
- The pattern that wins: **hash your asset filenames and cache them forever; keep HTML short-lived.**

**Idempotency and safety.** `GET` and `HEAD` are safe (no side effects); `GET`, `PUT` and `DELETE` are idempotent (repeating is harmless); `POST` is neither. This isn't pedantry: it decides what clients and intermediaries may **retry automatically**, which is precisely why a retried payment `POST` can charge twice, and why you need idempotency keys → [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]].

## 4. HTTP/2: binary, multiplexed, and one big remaining flaw

Derived from Google's SPDY and standardised in 2015. The meaning is the same (methods, headers, status codes; nothing you write changes), and the wire format is completely different:

- **Binary framing.** Messages become frames on **streams**, each with an ID. Parsing is unambiguous and cheap, with no text-parsing edge cases, which also removes a whole class of smuggling attacks.
- **Multiplexing.** Many concurrent streams over **one** TCP connection, interleaved. Application-layer head-of-line blocking: solved. This is the headline feature.
- **HPACK header compression.** A shared table of headers already seen, so a repeated header costs a couple of bytes as an index. It's an enormous saving on cookie-heavy sites. HPACK is *stateful*, so it needs ordered delivery, a detail that comes back in HTTP/3.
- **Stream prioritisation**, so style sheets can outrank images. Servers implemented it so differently that it was largely a disappointment, and RFC 9218 replaced it with a simpler scheme.
- **Server push**, sending resources nobody asked for. **Chrome removed it in 2022**: it usually wasted bandwidth pushing things the client already had cached. A good cautionary tale: obviously good in theory, measurably bad in deployment. `103 Early Hints` is the better idea that survived.

## 5. The flaw HTTP/2 can't fix

**Predict before reading on.** A client sends two requests on the *same* connection at the same moment: one the server takes 200 ms to answer, then one it answers at once. In what order do the replies finish on HTTP/1.1, and on HTTP/2?

<details>
<summary>After your prediction</summary>

On HTTP/1.1, **slow, then fast**: the fast reply can't start until the slow one has finished, because one connection carries one exchange at a time. On HTTP/2, **fast, then slow**: they're two streams, and the fast one's frames go out as soon as they're ready. The lab checks both orders, and that the HTTP/2 run used a single connection.

</details>

**But** HTTP/2 multiplexes on **one TCP connection**, and TCP guarantees ordered delivery of the whole byte stream. One lost packet stalls *every* stream, because TCP won't hand the receiver anything past the gap, even for streams whose data arrived perfectly → [[networking/07-tcp-reliability-and-flow-control|TCP head-of-line blocking]]. So HTTP/2 moved head-of-line blocking from the application layer down to the transport. On a clean network it's a large win. **On a lossy network, HTTP/2 can be slower than HTTP/1.1 with six connections**, because those six connections fail independently while HTTP/2's one connection has a single shared fate. That fact is the whole justification for [[networking/13-quic-and-modern-transport|HTTP/3]].

## 6. Which version, and how it's chosen

Browsers only speak HTTP/2 over TLS. The version is chosen *inside* the TLS handshake by ALPN, so no extra round trip is spent negotiating, and HTTP/3 is advertised by an `Alt-Svc` header or a DNS record, then tried over QUIC. Servers and clients inside a data centre, like gRPC, often use HTTP/2 without TLS ("h2c"), which is what the lab does, by telling Node's client to assume it.

## 7. The lab: one site, two protocol versions

`web.ts` serves the same small site over HTTP/1.1 and HTTP/2 on 127.0.0.1, with a fast route, a slow route, a style sheet with an `ETag`, and a streamed response. `web.test.ts` counts connections, records the order replies finish in, revalidates with `If-None-Match`, and reads a chunked response off a raw socket.

```ts
// web.ts — one small site served over HTTP/1.1 and over HTTP/2, with helpers that count connections and record
// the order responses finish in. Everything runs on 127.0.0.1; HTTP/2 here is "h2c", HTTP/2 without TLS, which
// browsers don't speak but Node's client does when told to (the TLS lesson covers how h2 is chosen over TLS).
import http from "node:http";
import http2 from "node:http2";
import { createHash } from "node:crypto";

const ASSET = "body { color: rebeccapurple; }\n";
const ETAG = `"${createHash("sha256").update(ASSET).digest("hex").slice(0, 16)}"`; // a fingerprint of the content

type Request = { url?: string; headers: Record<string, string | string[] | undefined> };
type Response = { writeHead: (status: number, headers?: Record<string, string>) => unknown; write: (s: string) => unknown; end: (s?: string) => unknown };

/** The site, the same for both versions: what changes between them is how requests share the connection. */
function route(req: Request, res: Response): void {
  if (req.url === "/fast") {
    res.writeHead(200, { "content-type": "text/plain" });
    res.end("fast");
  } else if (req.url === "/slow") {
    setTimeout(() => {
      res.writeHead(200, { "content-type": "text/plain" });
      res.end("slow");
    }, 200);
  } else if (req.url === "/style.css") {
    if (req.headers["if-none-match"] === ETAG) {
      res.writeHead(304, { etag: ETAG }); // "the copy you have is still right": headers only, no body
      res.end();
    } else {
      res.writeHead(200, { "content-type": "text/css", etag: ETAG, "cache-control": "max-age=60" });
      res.end(ASSET);
    }
  } else if (req.url === "/stream") {
    res.writeHead(200, { "content-type": "text/plain" }); // no Content-Length: HTTP/1.1 must send it chunked
    res.write("hello");
    // Writes in the same tick are coalesced into one chunk; where chunks begin and end is the sender's choice.
    setTimeout(() => {
      res.write(" world");
      res.end();
    }, 20);
  } else {
    res.writeHead(404);
    res.end();
  }
}

export async function startHttp1() {
  const server = http.createServer(route);
  const stats = { connections: 0 };
  server.on("connection", () => stats.connections++);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  return { port, stats, close: () => new Promise<void>((resolve) => server.close(() => resolve())) };
}

export async function startHttp2() {
  const server = http2.createServer(route as any);
  const stats = { connections: 0 };
  server.on("connection", () => stats.connections++);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as { port: number }).port;
  return { port, stats, close: () => new Promise<void>((resolve) => server.close(() => resolve())) };
}

/** One HTTP/1.1 GET through an agent, resolving to the status, headers and body. */
export function get1(port: number, path: string, agent: http.Agent, headers: Record<string, string> = {}) {
  return new Promise<{ status: number; headers: http.IncomingHttpHeaders; body: string }>((resolve, reject) => {
    http
      .get({ host: "127.0.0.1", port, path, agent, headers }, (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => resolve({ status: res.statusCode!, headers: res.headers, body }));
      })
      .on("error", reject);
  });
}

/** One HTTP/2 GET as a stream on an existing session. */
export function get2(session: http2.ClientHttp2Session, path: string) {
  return new Promise<string>((resolve, reject) => {
    const stream = session.request({ ":path": path });
    let body = "";
    stream.on("data", (chunk) => (body += chunk));
    stream.on("end", () => resolve(body));
    stream.on("error", reject);
  });
}

/** Starts the requests at the same moment and records the order they finish in. */
export async function finishOrder(requests: (() => Promise<string>)[]): Promise<string[]> {
  const order: string[] = [];
  await Promise.all(requests.map((r) => r().then((body) => void order.push(body))));
  return order;
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import http2 from "node:http2";
import net from "node:net";
import { finishOrder, get1, get2, startHttp1, startHttp2 } from "./web.ts";

test("keep-alive: ten requests over one connection instead of ten", async () => {
  for (const [keepAlive, expected] of [[false, 10], [true, 1]] as const) {
    const server = await startHttp1();
    const agent = new http.Agent({ keepAlive, maxSockets: 1 });
    for (let i = 0; i < 10; i++) assert.equal((await get1(server.port, "/fast", agent)).body, "fast");
    assert.equal(server.stats.connections, expected, `keepAlive ${keepAlive}`); // each connection is a TCP (and TLS) handshake
    agent.destroy();
    await server.close();
  }
});

test("HTTP/1.1 head-of-line blocking: on one connection, the fast reply waits behind the slow one", async () => {
  const server = await startHttp1();
  const agent = new http.Agent({ keepAlive: true, maxSockets: 1 }); // one connection, as on a busy origin
  const order = await finishOrder([async () => (await get1(server.port, "/slow", agent)).body, async () => (await get1(server.port, "/fast", agent)).body]);
  assert.deepEqual(order, ["slow", "fast"]);
  agent.destroy();
  await server.close();
});

test("HTTP/2 multiplexing: on one connection, the fast reply overtakes the slow one", async () => {
  const server = await startHttp2();
  const session = http2.connect(`http://127.0.0.1:${server.port}`);
  const order = await finishOrder([() => get2(session, "/slow"), () => get2(session, "/fast")]);
  assert.deepEqual(order, ["fast", "slow"]); // two streams interleaved on one connection
  assert.equal(server.stats.connections, 1);
  session.close();
  await server.close();
});

test("revalidation: an ETag turns a second download into a 304 with no body", async () => {
  const server = await startHttp1();
  const agent = new http.Agent({ keepAlive: true });
  const first = await get1(server.port, "/style.css", agent);
  assert.equal(first.status, 200);
  assert.equal(first.headers["cache-control"], "max-age=60"); // fresh for a minute: no request at all
  const again = await get1(server.port, "/style.css", agent, { "if-none-match": first.headers.etag as string });
  assert.deepEqual([again.status, again.body], [304, ""]); // after that, a cheap "is it still the same?"
  agent.destroy();
  await server.close();
});

test("chunked transfer encoding, as it looks on the wire", async () => {
  const server = await startHttp1();
  try {
    const raw = await new Promise<string>((resolve) => {
      const socket = net.connect(server.port, "127.0.0.1", () => socket.write("GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n"));
      let data = "";
      socket.on("data", (chunk) => (data += chunk));
      socket.on("end", () => resolve(data));
    });
    const split = raw.indexOf("\r\n\r\n"); // a blank line separates the head from the body
    const [head, body] = [raw.slice(0, split), raw.slice(split + 4)];
    assert.match(head, /^HTTP\/1\.1 200 OK/);
    assert.match(head, /Transfer-Encoding: chunked/i);
    assert.equal(body, "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n"); // each chunk's length in hex, then the chunk; 0 ends it
  } finally {
    await server.close();
  }
});
```

**Lab:** the code is in [`networking/11-http-evolution/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/11-http-evolution/labs/typescript). From the vault root, `python3 labs/run.py http-evolution/typescript` runs the tests and checks this page still shows the same code. Expect five passing tests in under a second; two of them wait 200 ms on purpose.

## Common pitfalls

1. **Keeping HTTP/1.1 workarounds on HTTP/2.** Sharding and giant bundles now cost connections and cache hits.
2. **Turning keep-alive off, or letting a proxy do it.** Every request pays the handshakes again.
3. **Not caching static assets.** Hash the names and cache them for a year.
4. **Retrying `POST` automatically.** It's not idempotent; use idempotency keys.
5. **Front-end and back-end servers parsing message lengths differently.** That's request smuggling.
6. **Assuming HTTP/2 is always faster.** On lossy networks, one shared TCP connection can lose to six.

## Check your understanding

1. What two costs has every HTTP version since 1.0 attacked, and how did 1.1, 2 and 3 each attack them?
2. Why is domain sharding harmful under HTTP/2?
3. A response has no `Content-Length`. How does the client know where the body ends on HTTP/1.1?
4. Which of `GET`, `PUT`, `POST` and `DELETE` may a proxy safely retry after a timeout, and why?
5. Why can HTTP/2 be slower than HTTP/1.1 on a network that loses packets?
6. What does a `304 Not Modified` save, and what does `Cache-Control: max-age=60` save that a `304` doesn't?

<details>
<summary>Answers — after your attempt</summary>

1. Round trips, and one slow thing blocking everything behind it. HTTP/1.1 attacked round trips with keep-alive. HTTP/2 attacked blocking by multiplexing streams on one connection, and hit TCP's ordered delivery. HTTP/3 replaced TCP with QUIC, so a lost packet only stalls its own stream.
2. HTTP/2 can carry all of a page's requests on one connection to one origin. Spreading them over several hostnames forces several connections, each with its own DNS lookup, TCP handshake and TLS handshake, and splits the header compression and prioritisation that work per connection.
3. Chunked transfer encoding: each chunk is preceded by its length in hexadecimal, and a zero-length chunk ends the body. (Or, in HTTP/1.0 style, the server closes the connection at the end.)
4. `GET`, `PUT` and `DELETE`: they're idempotent, so doing them twice leaves the same result as once. `POST` isn't: a retry might create a second order or charge twice.
5. All its streams share one TCP connection, and TCP won't deliver bytes after a lost packet until it's resent, so one loss stalls every stream. Six HTTP/1.1 connections lose packets independently, so one loss stalls one connection.
6. A `304` saves sending the body again, but still costs a round trip to ask. `max-age=60` saves the request entirely for 60 seconds: the browser uses its copy without asking.

</details>

## Practice — independent task

**Measure a real page's HTTP.**

1. Run `curl -sv --http1.1 https://example.com -o /dev/null` and `curl -sv --http2 https://example.com -o /dev/null`, and find in the output: the version negotiated, the ALPN result, and the response headers.
2. Fetch the same URL twice with `curl -I`, the second time with `-H 'If-None-Match: <the ETag>'`, and confirm a `304` (pick a site that sends an `ETag`).
3. Open your flagship in a browser's network panel and record: the protocol column, how many connections are opened, and which responses are served from cache on a reload.

**A smaller step first:** in the lab, make the slow route take 1 second and add a third request. Predict the finish order on both versions before running it.

**Done when:** you have the negotiated versions and ALPN results, a `304` you produced yourself, and your flagship's numbers with one change you'd make to its caching headers.

## Tradeoffs, limits and extensions

- **h2c isn't what browsers use.** The lab runs HTTP/2 without TLS to keep it local; real browsers negotiate h2 inside TLS with ALPN.
- **The lab doesn't show packet loss.** Head-of-line blocking at the TCP level needs a lossy link, simulated on Linux with `tc qdisc add dev lo root netem loss 2%` (as root). Worth trying, then undoing.
- **HTTP/3** is in [[networking/13-quic-and-modern-transport|QUIC and modern transport]].

## Before moving on

You can explain what each HTTP version changed in terms of round trips and blocking, count connections with and without keep-alive, use caching headers and `304`s, read chunked encoding on the wire, and say which methods are safe to retry.

**Recap.** Every HTTP version since 1.0 fights round trips and head-of-line blocking. HTTP/1.1's keep-alive reuses connections (ten requests: one connection instead of ten), but one connection carries one exchange at a time, so a fast reply waits behind a slow one. HTTP/2 multiplexes streams on one connection, so the fast reply overtakes, but TCP's ordered delivery means one lost packet stalls them all, which HTTP/3 fixes with QUIC. Cache with `max-age` and `ETag`s; a `304` is headers only. Chunked encoding frames bodies of unknown length, and disagreement about lengths is request smuggling. Retry only idempotent methods.

**Next.** [[networking/12-tls-and-transport-security/index|TLS and transport security]]: the encrypted, authenticated channel this all runs inside, and the maths that makes it work.

## Related

- [[networking/13-quic-and-modern-transport|QUIC and HTTP/3]]: where this story ends
- [[networking/12-tls-and-transport-security/index|TLS]]: HTTP/2 requires it in browsers; ALPN negotiates the version
- [[networking/15-network-performance|Network performance]]: measuring which of these actually matters
- [[backend/02-api-design/01-apis-and-rest|APIs]]: HTTP semantics as an API design surface
- [[cybersecurity/04-web-security/index|Web security]]: smuggling, caching attacks, header handling
