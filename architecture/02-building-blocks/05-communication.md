# Communication

**[reference]** — from the roadmap.sh system-design roadmap. How the pieces of a system talk to each other and to clients — the API-style choice that shapes coupling, performance, and developer experience.

## The API styles

### REST

Resources addressed by URLs, manipulated with HTTP verbs (GET/POST/PUT/DELETE), usually JSON. The default for public and web APIs.

- **Pros** — simple, universal, cacheable (HTTP caching), stateless, human-readable, works everywhere.
- **Cons** — **over-fetching** (an endpoint returns more than you need) and **under-fetching** (you need several round-trips to assemble a screen), and no strict contract by default. See the real [[backend/frameworks/java/03-api-design-and-documentation|REST/OpenAPI design]].

### GraphQL

A query language where the *client* specifies exactly what data it wants, in one request.

- **Pros** — no over/under-fetching (fetch precisely the fields needed, across resources, in one round-trip), a strong typed schema, great for complex/nested data and mobile (bandwidth-sensitive) clients — the [[architecture/03-architectural-patterns/04-microservices-patterns|backends-for-frontends]] problem it addresses.
- **Cons** — more server complexity, caching is harder (not simple HTTP GETs), and naive resolvers cause the **N+1 query** problem. Powerful when clients have varied data needs; overkill for a simple CRUD API.

### gRPC

A high-performance RPC framework using **Protocol Buffers** (binary, schema-defined) over HTTP/2.

- **Pros** — fast and compact (binary, not JSON text), strongly-typed contracts with generated client/server code, streaming, low latency. Ideal for **internal service-to-service** communication ([[architecture/03-architectural-patterns/04-microservices-patterns|microservices]]).
- **Cons** — not human-readable, limited browser support (needs a proxy), more setup. Rarely the choice for a public/browser-facing API.

### The quick chooser

| Use case | Reach for |
|---|---|
| Public API, web, simplicity, caching | **REST** |
| Rich/nested data, varied client needs, mobile | **GraphQL** |
| Internal service-to-service, performance-critical | **gRPC** |

## Synchronous vs asynchronous communication

Orthogonal to the API style: does the caller *wait*?

- **Synchronous** (REST/gRPC request-response) — simple, immediate, but couples services (the caller blocks on the callee, and a slow/down dependency propagates).
- **Asynchronous** (via [[architecture/02-building-blocks/04-messaging-and-async|message queues / events]]) — decoupled and resilient, but eventually consistent and harder to trace.

A common mistake is making everything synchronous request-response, which creates a fragile chain where any one slow service degrades all callers ([[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability multiplies down]]). Mix deliberately: sync for "I need the answer now," async for "react to this eventually."

## The protocols underneath

Worth knowing what these sit on ([[devops/08-networking-and-web/01-networking-and-protocols|networking & protocols]]): **HTTP/1.1 → HTTP/2** (multiplexing, what gRPC uses) **→ HTTP/3** (over QUIC/UDP, lower latency); **TCP** (reliable, ordered — most APIs) vs **UDP** (fire-and-forget, low overhead — video, DNS, some real-time); **WebSockets** for full-duplex real-time (chat, live updates); and **TLS** securing all of it ([[cybersecurity/04-web-security/03-https-and-tls|HTTPS/TLS]]).

## Related
- [[backend/frameworks/java/03-api-design-and-documentation|API Design & Documentation (Java)]] — REST/OpenAPI in real code
- [[architecture/02-building-blocks/04-messaging-and-async|Messaging & Async]] — the async alternative to request-response
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking & Protocols (devops)]] — the transport layer
