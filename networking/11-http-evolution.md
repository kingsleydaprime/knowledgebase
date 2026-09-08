# HTTP and Its Evolution

**[Intermediate]** — the application protocol that ate the internet. The interesting story isn't the syntax (which you already know) — it's that **three decades of HTTP versions are all fighting the same enemy: round trips and head-of-line blocking.** Understand that, and every version's design choices are obvious.

## The kid version first

You're ordering from a shop by post.

- **HTTP/0.9–1.0:** send one letter, get one reply, and the shop closes the mail channel. Next order? Set up the whole channel again. Exhausting.
- **HTTP/1.1:** the channel stays open between orders. Better — but you must wait for order 1's reply before sending order 2. One slow item blocks everything behind it.
- **HTTP/2:** you may send all orders at once down the same channel, and replies come back interleaved. Except the *postal service* still insists on delivering everything in strict order, so one lost envelope still stalls the lot.
- **HTTP/3:** change the postal service too. Now a lost envelope only delays its own order.

The whole history in four lines. Everything below is detail.

## HTTP/1.1 — the version whose flaws defined the web

Text-based, request-response, and stateless by design. Its two defining problems:

**1. Head-of-line blocking at the application layer.** One connection carries one request at a time. Request 2 waits for response 1 to complete. **Pipelining** (sending multiple requests without waiting) was specified but is effectively dead — responses still had to come back *in order*, so a slow first response blocked the rest anyway, and buggy proxies mishandled it. It's disabled by default in every major browser.

**2. Verbose, repetitive headers.** Every request re-sends the same cookies, `User-Agent`, and `Accept` headers — often hundreds of bytes of identical text per request, uncompressed, on a page making 80 requests.

The workarounds the industry built around these limits are worth naming, because **HTTP/2 made all of them obsolete and many codebases still carry them**:

- **6 parallel connections per origin** — browsers' brute-force fix, and the reason a page's requests come in waves of six.
- **Domain sharding** — serving assets from `img1.example.com`, `img2.example.com` to get 6 connections *each*. Now actively harmful: it defeats HTTP/2 multiplexing and multiplies DNS lookups, TCP handshakes, and TLS handshakes.
- **Concatenation and spriting** — bundling all JS into one file, all icons into one image, to turn many requests into one. Under HTTP/2 this hurts caching granularity (change one line, re-download everything).
- **Inlining** — base64-ing images into CSS. Same problem, plus it defeats caching entirely.

If you're doing performance work on an existing codebase, checking whether these 1.1-era workarounds are still in place is often the highest-value single audit.

## The pieces of HTTP/1.1 worth knowing precisely

**Statelessness and how it's worked around.** The server keeps no memory between requests. Cookies, tokens, and sessions all exist to reintroduce state on top — which is what makes horizontal scaling easy (any server can handle any request) and is the foundation of the [[backend/05-auth/01-authentication-flows|auth flows]] notes.

**Persistent connections.** `Connection: keep-alive` is the default in 1.1. This is the single biggest 1.1 performance feature, because it amortises the [[foundations/networking/06-tcp-connection-lifecycle|TCP handshake]] and [[foundations/networking/12-tls-and-transport-security|TLS handshake]] — and lets [[foundations/networking/08-congestion-control|congestion control]] escape slow start, which matters more than most people realise.

**Content-Length vs chunked encoding.** The receiver needs to know where a response ends. Either declare the length upfront, or use `Transfer-Encoding: chunked` and send length-prefixed chunks with a zero-length terminator (necessary for streamed/generated content). Getting the interaction between these two wrong — where a front-end proxy and back-end server disagree about which one governs — is exactly the **request smuggling** vulnerability class. → [[cybersecurity/04-web-security/README|web security]]

**Caching**, which is the most under-used performance tool in the protocol:
- `Cache-Control: max-age=N` — freshness, no revalidation needed
- `ETag` + `If-None-Match` — revalidate cheaply; a `304 Not Modified` sends headers only
- `immutable` for content-hashed assets; `stale-while-revalidate` to serve stale instantly while refreshing in the background
- The pattern that wins: **hash your asset filenames and cache them forever; keep HTML short-lived.**

**Idempotency and safety.** `GET`/`HEAD` are safe (no side effects); `GET`/`PUT`/`DELETE` are idempotent (repeating is harmless); `POST` is neither. This isn't pedantry — it determines what intermediaries and clients may **retry automatically**, which is precisely why a retried payment `POST` can double-charge and why you need idempotency keys. → [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]

## HTTP/2 — binary, multiplexed, and one big remaining flaw

Derived from Google's SPDY, standardised 2015. Same semantics (methods, headers, status codes — nothing you write changes), completely different wire format.

- **Binary framing.** Messages become frames on **streams**, each with an ID. Parsing is unambiguous and cheap; no more text-parsing edge cases (which also kills a whole class of smuggling attacks).
- **Multiplexing.** Many concurrent streams over **one** TCP connection, interleaved. Application-layer head-of-line blocking: solved. This is the headline feature.
- **HPACK header compression.** A shared dynamic table of previously-seen headers, so repeated headers cost a couple of bytes as an index reference. Enormous saving on cookie-heavy sites. (It's *stateful*, which is why HPACK needs ordered delivery — a detail that comes back in HTTP/3.)
- **Stream prioritisation** — clients express dependency/weight so CSS can outrank an image. In practice server implementations varied so much it was largely a disappointment; replaced by a simpler scheme in RFC 9218.
- **Server push** — send resources unrequested. **Removed from Chrome in 2022.** It usually wasted bandwidth pushing things the client already had cached. A good cautionary tale: a feature that's obviously good in theory and measurably bad in deployment. `103 Early Hints` is the surviving, better idea.

**The flaw it can't fix:** HTTP/2 multiplexes on **one TCP connection**, and TCP guarantees ordered delivery of the whole byte stream. One lost packet stalls *every* stream, because TCP won't hand the receiver anything past the gap — even for streams whose data arrived perfectly. → [[foundations/networking/07-tcp-reliability-and-flow-control|TCP head-of-line blocking]]

So HTTP/2 moved head-of-line blocking from the application layer down to the transport layer. On a clean network it's a large win. **On a lossy network, HTTP/2 can be slower than HTTP/1.1 with six connections**, because those six connections fail independently while HTTP/2's single connection has one shared fate.

That single fact is the entire justification for [[foundations/networking/13-quic-and-modern-transport|HTTP/3]].

## Key insight

Every version of HTTP after 1.0 is an attack on the same two costs: **the number of round trips, and one slow thing blocking everything behind it.** 1.1 attacked round trips with keep-alive. 2 attacked blocking with multiplexing — and hit the transport layer's floor. 3 gave up on fixing HTTP and replaced the transport instead. Note the trajectory: the protocol kept pushing the problem *down* the stack until it ran out of stack and had to rebuild the layer below.

## Related
- [[foundations/networking/13-quic-and-modern-transport|QUIC & HTTP/3]] — where this story ends
- [[foundations/networking/12-tls-and-transport-security|TLS]] — h2 requires it in practice; ALPN is how it's negotiated
- [[foundations/networking/15-network-performance|Network Performance]] — measuring which of these actually matters
- [[backend/02-api-design/01-apis-and-rest|APIs]] — HTTP semantics as an API design surface
- [[cybersecurity/04-web-security/README|Web Security]] — smuggling, caching attacks, header handling
