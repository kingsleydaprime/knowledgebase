# Go Backends — scaffold

No course written yet. The shape, for when there is one:

**Concurrency model: goroutines** — green threads, since Go 1.0. You write blocking code; the runtime multiplexes onto OS threads. No `async`/`await`, so no "coloured function" split in the ecosystem. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

| Option | Character |
|---|---|
| **`net/http`** | the standard library is genuinely enough for most services — unusual, and a real Go strength |
| **Chi** | a thin router on top of `net/http`, stdlib-compatible middleware |
| **Gin** | more batteries, own context type |

## The things to know
- **`context.Context` is the spine** — cancellation and deadline propagation are threaded through every call, which makes [[backend/interview/01-production-debugging|deadline propagation]] idiomatic rather than an afterthought.
- **Explicit error returns**, no exceptions — so [[backend/01-foundations/03-the-request-lifecycle|error→status mapping]] is done by hand, usually with typed errors and `errors.As`.
- **Goroutines are cheap enough to leak.** Unbounded spawning is the characteristic Go bug; bound it.

## Related
- [[backend/frameworks/README|frameworks/]]
