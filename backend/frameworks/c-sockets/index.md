# Sockets and epoll (C Backend)

## What a C backend is

**A C backend is a web server written in C. This subject is the version with no framework at all, where you build almost everything yourself: accepting connections, reading requests and sending responses.** It is rarely the right choice for a normal app, but building one shows you what every other framework is doing for you.

**Concurrency model: whatever you build.** C has no runtime, so the model is a design decision rather than a language feature — a process per connection (the old CGI/Apache model), a thread per connection, a thread pool, or a single-threaded event loop over `epoll`/`kqueue`. Nearly every modern C server is the last. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~8,000 words across 4 notes.** `[reference]`. Assumes [[languages/04-c/index|the C course]].

> **The interesting thing about C here: it's the layer the *other* models are implemented in.** Node's event loop, Go's netpoller and tokio's reactor are all `epoll` loops. Writing one makes every runtime you use afterwards unmysterious — and explains exactly why blocking inside an async handler is catastrophic.

## Lessons so far

1. [[backend/frameworks/c-sockets/01-the-accept-loop-and-event-loops|01 — The Accept Loop and Event Loops]] — **[Advanced]** — `socket`/`bind`/`listen`/`accept`, the four concurrency strategies, `epoll`, edge vs level triggering, and why partial writes force a per-connection state machine
2. [[backend/frameworks/c-sockets/02-parsing-http-safely|02 — Parsing HTTP Safely]] — **[Advanced]** — every byte is attacker-controlled and C has no bounds checking. **The note that matters most**
3. [[backend/frameworks/c-sockets/03-choosing-a-c-framework|03 — Choosing a C Framework]] — **[Intermediate]** — the options side by side and what none of them give you. Each framework now has its own subject
4. [[backend/frameworks/c-sockets/04-when-not-to-use-c|04 — When Not to Use C]] — **[Intermediate]** — the decision framework, and the migration paths

## The honest question: should you?

**Usually no.** For a new network service C is the wrong choice, for a specific measurable reason: an HTTP parser is the most attacker-exposed code you will ever write, and C offers no mechanism to make it safe — only discipline, which doesn't survive deadlines.

Microsoft and Google both report **~70% of their CVEs are memory-safety bugs**, and Android's fell from 76% to 24% as new code moved to memory-safe languages. That's not careless programmers; it's the measured output of excellent ones over decades.

The cases where it's a real answer:
- **Embedding HTTP in an existing C codebase** — firmware, a device's config UI, a game engine's debug server. The strongest case, and it's about avoiding a second runtime rather than about HTTP
- **Extremely constrained targets** where no other toolchain exists
- **Learning** — writing one from `socket()` up teaches you more than any framework will → [[BUILD-PLAN|build-your-own-shit]]

If the reason is an existing native codebase, look at [[backend/frameworks/drogon/index|C++]] first — RAII, `std::string` and a real JSON layer remove most of note 02's difficulty.

## The options

| Option | Character |
|---|---|
| **[[backend/frameworks/libmicrohttpd/index\|libmicrohttpd]]** | GNU, small, embeddable; the usual choice for adding HTTP to an existing C program |
| **[[backend/frameworks/kore/index\|Kore]]** | a full framework — TLS, routing, WebSockets, **privilege separation**. Opinionated and security-focused |
| **[[backend/frameworks/ulfius/index\|Ulfius]]** | REST-oriented, with JSON and WebSocket support |
| **[[backend/frameworks/civetweb/index\|civetweb]] / mongoose** | tiny, embeddable, popular in firmware and desktop apps |
| **raw `socket()` + `epoll`** | writing one yourself — note 01 |

## The things to know

- **You are writing the accept loop.** `socket` → `bind` → `listen` → `accept`, then `epoll` (Linux) or `kqueue` (BSD) for readiness → note 01
- **Parsing is where the bugs are.** Use `llhttp` or `picohttpparser` rather than writing one for production, and [[languages/04-c/13-debugging-and-tooling|fuzz it]] if you do → note 02
- **No string type** means every buffer needs an explicit length and bound → [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]]
- **Lifetimes across an event loop are the hard part** — a connection's buffers must outlive the callback that queued them, and there's no ownership system to help
- **`SIGPIPE` will kill your process** when a client disconnects mid-write, unless you ignore it

## If you ship it

1. **Use llhttp or picohttpparser** — don't ship your own parser
2. **Bound every buffer**, cap every limit
3. **Compile hardened**: `-D_FORTIFY_SOURCE=2 -fstack-protector-strong -fPIE -pie -Wl,-z,relro,-z,now`
4. **Fuzz the parser**; run tests under ASan and UBSan in CI
5. **Drop privileges after `bind()`**; `chroot` and `seccomp` if you can
6. **Put a reverse proxy in front** — the highest-value single mitigation available

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the plain-C way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — The accept loop and event loops**: `socket` to `accept`, the four concurrency strategies, `epoll` — written in part: [[backend/frameworks/c-sockets/01-the-accept-loop-and-event-loops|The Accept Loop and Event Loops]]
2. **02 — Parsing HTTP safely**: every byte is attacker-controlled, and C has no bounds checking — written in part: [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]]
3. **03 — Choosing a C framework**: the options side by side, and what none of them give you — written in part: [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]]
4. **04 — When not to use C**: the decision, and the migration paths — written in part: [[backend/frameworks/c-sockets/04-when-not-to-use-c|When Not to Use C]]
5. **05 — Routing by hand**: a method and path table
6. **06 — Input validation**: partial writes, `Content-Length`, chunked encoding
7. **07 — Errors and structured responses**: cJSON or Jansson, and who owns each allocation, and one response shape for success and failure
8. **08 — Data**: libpq's async API inside the event loop

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with parsing the query string by hand, safely, keyset pagination
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with routing on the path prefix or a header
11. **11 — API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **12 — Authentication**: constant-time comparison, TLS with OpenSSL
13. **13 — Authorization**: roles and owning your own orders, with a permission check in every handler, and why that's fragile
14. **14 — Security**: slowloris, per-connection deadlines
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: Unity, a fuzzing harness, ASan

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with a worker thread or a forked process
19. **19 — Caching**: caching hot reads with hiredis, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with WebSockets on your own event loop

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with why GraphQL in C is rarely worth it, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with protobuf-c and the gRPC core
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with JSON-RPC 2.0 over Streamable HTTP by hand, and what that teaches about the protocol
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over NATS's C client, the outbox pattern
26. **26 — Calling other services safely**: libcurl with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with syslog and simple counters
28. **28 — Production config and Docker**: dropping privileges, a reverse proxy, signals and `SIGPIPE`; a hardened Docker image behind nginx, Docker Compose for the whole system
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|frameworks/]] · [[languages/04-c/index|the C course]]
- [[networking/09-sockets-and-the-network-api|Sockets and the Network API]]
- [[backend/frameworks/axum/index|Axum]] — the direct replacement
- [[cybersecurity/04-web-security/index|Web Security]]
