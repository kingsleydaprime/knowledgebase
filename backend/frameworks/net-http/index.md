# net/http (Go Backends)

## What net/http is

**net/http is the package built into Go for writing web servers, and in Go it is often all you need.** Go was made for exactly this, so a small amount of code goes a long way.

**Concurrency model: goroutines** — green threads, since Go 1.0. You write blocking code; the runtime multiplexes onto OS threads. No `async`/`await`, so no "coloured function" split in the ecosystem. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~11,000 words across 6 notes.** `[reference]` — no Go service in this vault yet. Assumes [[languages/02-go/index|the Go course]] and the [[backend/index|backend course]]; these notes cover only what those don't.

> **The thing that makes Go's HTTP ecosystem different:** everything is `http.Handler`, one interface with one method. A Chi router, a Gin engine, your own function, and every middleware in the ecosystem all satisfy it — so they interoperate without adapters. Most ecosystems have framework-specific middleware that can't be reused; Go got composability by agreeing on the narrowest possible interface early.

## Lessons so far

1. [[backend/frameworks/net-http/01-net-http-in-depth|`net/http` in Depth]] — **[Intermediate]** — the `Handler` interface, Go 1.22 routing, and the server configuration that separates a toy from production. **`http.ListenAndServe` has no timeouts**
2. [[backend/frameworks/net-http/02-middleware-as-composition|Middleware as Composition]] — **[Intermediate]** — `func(Handler) Handler`, the essential middleware, and why wrapping `ResponseWriter` breaks `Flusher` and `Hijacker`
3. [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]] — **[Intermediate]** — DI without a container, handlers as methods, and error→status mapping in one place
4. [[backend/frameworks/net-http/04-database-access|Database Access]] — **[Intermediate]** — `database/sql`, the pool settings that decide whether you survive load, and why Go is sceptical of ORMs
5. [[backend/frameworks/net-http/05-testing-and-production|Testing and Production]] — **[Intermediate]** — `httptest`, fakes without a mocking framework, observability, and the container gotchas

## The stdlib-is-enough argument, honestly

Go 1.22 gave `http.ServeMux` method matching and path wildcards, which removed most of the reason to take a router dependency. `net/http` is a production HTTP server — not a toy you replace.

What the stdlib still doesn't give you: route groups with shared middleware, a chaining helper, correct `ResponseWriter` wrapping, and request validation. Each is 10–50 lines you write once.

**So: start with the stdlib, add [[backend/frameworks/chi/index|Chi]] when route grouping starts hurting.** The migration is mechanical because Chi uses the identical types. That deferrable framework decision is unusual — in most ecosystems it's load-bearing and early.

## The framework table

| | stdlib | [[backend/frameworks/chi/index\|Chi]] | [[backend/frameworks/gin/index\|Gin]] | Echo | Fiber |
|---|---|---|---|---|---|
| `net/http` compatible | ✅ | ✅ | partial | partial | ❌ |
| Route groups | ❌ | ✅ | ✅ | ✅ | ✅ |
| Binding + validation | ❌ | ❌ | ✅ | ✅ | ✅ |
| Lock-in | none | none | real | real | **total** |

Fiber is built on fasthttp and is **not** `net/http` compatible — you lose the entire middleware, tracing and metrics ecosystem for throughput you almost certainly don't need.

## What Go does badly here

- **No request validation in the stdlib.** You write it, or take `go-playground/validator`, or use Gin's binding
- **No dependency injection.** Deliberate, and it means wiring is explicit and verbose
- **`ResponseWriter` has no status getter** — a genuine design wart, and the reason every logging middleware wraps it
- **ORMs are weak by comparison.** `sqlc` is the good answer; GORM works and generates SQL you didn't write
- **Error handling is manual.** No `@ControllerAdvice`; you write the error→status switch. More code, and no framework knowledge needed to read it

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the net/http way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What net/http is and a first server**: `http.Handler`, and why `ListenAndServe` has no timeouts — written in part: [[backend/frameworks/net-http/01-net-http-in-depth|`net/http` in Depth]]
2. **Routing**: Go 1.22 `ServeMux` patterns: methods and path wildcards — written in part: [[backend/frameworks/net-http/01-net-http-in-depth|`net/http` in Depth]]
3. **Middleware**: `func(Handler) Handler`, and wrapping `ResponseWriter` correctly — written in part: [[backend/frameworks/net-http/02-middleware-as-composition|Middleware as Composition]]
4. **Structure**: package layout, handlers as methods — written in part: [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]]
5. **Wiring**: DI in `main`, interfaces declared by the consumer — written in part: [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]]
6. **Validation**: strict JSON decoding, `go-playground/validator`
7. **Errors**: mapping errors to status codes in one place — written in part: [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]]
8. **Data**: `database/sql`, pool settings, sqlc, migrations — written in part: [[backend/frameworks/net-http/04-database-access|Database Access]]
9. **Auth**: JWT and session middleware, the user in `context`
10. **Security and cross-cutting**: CORS, rate limiting with `x/time/rate`, `MaxBytesReader` for uploads, idempotency
11. **Testing**: `httptest`, fakes, table-driven tests — written in part: [[backend/frameworks/net-http/05-testing-and-production|Testing and Production]]
12. **Production**: graceful shutdown, observability, containers — written in part: [[backend/frameworks/net-http/05-testing-and-production|Testing and Production]]

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[languages/02-go/index|The Go course]] — the language
- [[backend/frameworks/axum/index|Axum]] — the other no-runtime option
- [[networking/09-sockets-and-the-network-api|Sockets]] — what `net/http` sits on
