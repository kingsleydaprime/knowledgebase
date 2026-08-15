# Go Backends

**Concurrency model: goroutines** — green threads, since Go 1.0. You write blocking code; the runtime multiplexes onto OS threads. No `async`/`await`, so no "coloured function" split in the ecosystem. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

**~11,000 words across 6 notes.** `[reference]` — no Go service in this vault yet. Assumes [[languages/02-go/README|the Go course]] and the [[backend/README|backend course]]; these notes cover only what those don't.

> **The thing that makes Go's HTTP ecosystem different:** everything is `http.Handler`, one interface with one method. A Chi router, a Gin engine, your own function, and every middleware in the ecosystem all satisfy it — so they interoperate without adapters. Most ecosystems have framework-specific middleware that can't be reused; Go got composability by agreeing on the narrowest possible interface early.

## Reading order

1. [[backend/frameworks/go/01-net-http-in-depth|`net/http` in Depth]] — **[Intermediate]** — the `Handler` interface, Go 1.22 routing, and the server configuration that separates a toy from production. **`http.ListenAndServe` has no timeouts**
2. [[backend/frameworks/go/02-middleware-as-composition|Middleware as Composition]] — **[Intermediate]** — `func(Handler) Handler`, the essential middleware, and why wrapping `ResponseWriter` breaks `Flusher` and `Hijacker`
3. [[backend/frameworks/go/03-routers-chi-and-gin|Routers: Chi and Gin]] — **[Intermediate]** — what a router still adds after Go 1.22, and the lock-in question
4. [[backend/frameworks/go/04-structuring-a-go-service|Structuring a Go Service]] — **[Intermediate]** — DI without a container, handlers as methods, and error→status mapping in one place
5. [[backend/frameworks/go/05-database-access|Database Access]] — **[Intermediate]** — `database/sql`, the pool settings that decide whether you survive load, and why Go is sceptical of ORMs
6. [[backend/frameworks/go/06-testing-and-production|Testing and Production]] — **[Intermediate]** — `httptest`, fakes without a mocking framework, observability, and the container gotchas

## The stdlib-is-enough argument, honestly

Go 1.22 gave `http.ServeMux` method matching and path wildcards, which removed most of the reason to take a router dependency. `net/http` is a production HTTP server — not a toy you replace.

What the stdlib still doesn't give you: route groups with shared middleware, a chaining helper, correct `ResponseWriter` wrapping, and request validation. Each is 10–50 lines you write once.

**So: start with the stdlib, add Chi when route grouping starts hurting.** The migration is mechanical because Chi uses the identical types. That deferrable framework decision is unusual — in most ecosystems it's load-bearing and early.

## The framework table

| | stdlib | Chi | Gin | Echo | Fiber |
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

## Related
- [[backend/frameworks/README|frameworks/]] — the same concepts across every stack
- [[languages/02-go/README|The Go course]] — the language
- [[backend/frameworks/rust/README|Rust backends]] — the other no-runtime option
- [[foundations/networking/09-sockets-and-the-network-api|Sockets]] — what `net/http` sits on
