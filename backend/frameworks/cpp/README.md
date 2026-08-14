# C++ Backends — scaffold

No course written yet. The shape, for when there is one:

**Concurrency model: usually an async event loop, sometimes a thread pool.** C++ has no runtime, so the framework brings one — nearly always [asio](https://think-async.com/Asio/) underneath, which is the de facto standard async I/O library and the basis of the long-proposed `std::net`. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

| Option | Character |
|---|---|
| **Drogon** | the most complete: HTTP/1+2, WebSockets, ORM, templates, coroutine support. The usual first choice |
| **Crow** | header-only, Flask-like routing. Small and pleasant for embedding |
| **oat++** | zero-dependency, API-documentation-first, aimed at microservices |
| **Pistache** | modern C++ REST framework, Linux-focused |
| **Boost.Beast** | not a framework — HTTP/WebSocket *primitives* on asio. What you build on when you want control |
| **cpp-httplib** | single header, blocking, genuinely tiny. Great for a test server or a tool |

## When it's a real answer

Unlike [[backend/frameworks/c/README|C]], C++ on the server is defensible more often — RAII and containers remove the easy memory bugs, and the performance ceiling is the same.

The honest cases:
- **An existing C++ system needs an HTTP surface** — a game server, a trading system, a simulation engine. Crossing a process boundary to a Go service is often the wrong trade
- **Latency requirements a GC can't meet** — the same argument as [[languages/03-rust/README|Rust]]
- **The domain libraries are C++** — computer vision, numerics, physics

And where it isn't: an ordinary CRUD service. The [[languages/05-cpp/15-build-tooling-and-ecosystem|package-management and build story]] alone costs more than the performance is worth, and [[languages/02-go/README|Go]] or [[backend/frameworks/java/README|Spring Boot]] will ship sooner.

## The things to know
- **Lifetimes across async boundaries are the hard part.** A handler that captures by reference and outlives its scope is a use-after-free — the [[languages/05-cpp/07-operator-overloading|lambda capture]] rules matter enormously here. `shared_from_this` is the standard pattern for keeping a connection alive for the duration of a callback chain
- **Coroutines (C++20) change the shape** — Drogon and asio both support them, and they turn callback chains into linear code. Still low-level; the standard provides no `Task` type → [[languages/05-cpp/13-concurrency|Concurrency]]
- **Parsing untrusted input is where the CVEs are.** Use a hardened parser, and [[languages/04-c/13-debugging-and-tooling|fuzz it]]
- **`std::string_view` and `std::span` are ideal for zero-copy request parsing** — and dangle just as easily as any other view
- **Exceptions across an event loop** need care: an escaping exception usually kills the loop thread → [[languages/05-cpp/11-exceptions-and-error-handling|Exceptions]]

## Related
- [[backend/frameworks/README|frameworks/]] · [[languages/05-cpp/README|the C++ course]]
- [[backend/frameworks/c/README|C backends]] — the layer below
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]]
