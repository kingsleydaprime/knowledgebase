---
id: 15ea85bb-ff10-495e-8354-e99e47a254fa
---

# Chi

Chi is a small router for Go. A router is the part of a backend that looks at a request's address, like /users/42, and sends it to the right piece of code. Go's own standard library can now do most of this by itself, so this lesson starts with what is still missing, then shows how Chi fills the gap without taking over your code.

## What changed in Go 1.22
<!-- bite: f3d4d1db-a11b-4073-867e-1dfba9d9696c -->

Before it, `http.ServeMux` had no method matching and no path parameters. Every real project used a router, and the choice mattered.

Now the stdlib does `GET /users/{id}` natively, and the honest answer is that **most services don't need a router at all**. What's left is:

| Still missing from the stdlib | Effort to write yourself |
|---|---|
| Route groups with shared middleware | ~20 lines |
| A middleware chaining helper | ~8 lines |
| `ResponseWriter` wrapping done correctly | ~40 lines (the interface matrix) |
| Regex/typed path constraints | more |
| Route listing and introspection | more |

Route grouping is the one that actually bites at scale. Twenty routes each needing `Chain(handler, Auth, RequireAdmin)` is noise a router removes.

## Chi
<!-- bite: 3757af7e-3e4b-44b8-8128-36db17776c74 -->

```go
import "github.com/go-chi/chi/v5"

r := chi.NewRouter()

r.Use(middleware.RequestID)
r.Use(middleware.RealIP)
r.Use(middleware.Logger)
r.Use(middleware.Recoverer)
r.Use(middleware.Timeout(30 * time.Second))

r.Get("/health", healthHandler)

r.Route("/api/v1", func(r chi.Router) {
    r.Use(Auth)                                   // applies to this GROUP only

    r.Route("/users", func(r chi.Router) {
        r.Get("/", listUsers)
        r.Post("/", createUser)

        r.Route("/{id}", func(r chi.Router) {
            r.Use(UserCtx)                        // load the user once for all sub-routes
            r.Get("/", getUser)
            r.Put("/", updateUser)
            r.Delete("/", deleteUser)
        })
    })

    r.Group(func(r chi.Router) {                  // inline group, no path prefix
        r.Use(RequireAdmin)
        r.Get("/admin/stats", stats)
    })
})

http.ListenAndServe(":8080", r)
```

**Chi's defining property: it's 100% `net/http` compatible.**

```go
func getUser(w http.ResponseWriter, r *http.Request) {    // a plain http.HandlerFunc
    id := chi.URLParam(r, "id")
}
```

Handlers are `http.HandlerFunc`. Middleware is `func(http.Handler) http.Handler` — the exact signature from [[backend/frameworks/net-http/03-middleware|Middleware as Composition]]. A `chi.Router` *is* an `http.Handler`.

So there's no lock-in: you can mount a Chi router inside a stdlib mux, use stdlib middleware in Chi, and swap Chi out later without touching handler code. It's a thin layer that adds grouping and stops.

Chi's `middleware` package is worth knowing even if you don't use the router — `middleware.WrapResponseWriter` solves the `Flusher`/`Hijacker` problem from [[backend/frameworks/net-http/03-middleware|Middleware as Composition]] properly.

## Chi next to the stdlib and Gin
<!-- bite: 0888c30b-e474-4a3e-b9c6-116f442bce6d -->

| | stdlib | Chi | Gin |
|---|---|---|---|
| Handler type | `http.HandlerFunc` | `http.HandlerFunc` | `gin.HandlerFunc` |
| Middleware | `func(Handler) Handler` | same | `gin.HandlerFunc` |
| Route groups | no | **yes** | **yes** |
| Binding + validation | no | no | **yes** |
| Lock-in | none | **none** | real |
| Router speed | good | good | fastest (radix tree, zero-alloc) |
| Dependencies | 0 | 1 | several |

**Gin's performance advantage is real and almost never the bottleneck.** Routing is nanoseconds; your database call is milliseconds. Choose on ergonomics and lock-in, not benchmarks.

Others you'll see: **Echo** (similar to Gin, own context), **Fiber** (Express-like API, built on fasthttp — **not `net/http` compatible**, which rules out the whole middleware ecosystem), **gorilla/mux** (was the default for years; archived, then revived, largely superseded by Go 1.22).

Fiber deserves a warning: fasthttp is faster in benchmarks and incompatible with `net/http`, so you lose every library that expects a `Handler` — including most tracing, metrics, and auth middleware. That's a big trade for throughput you probably don't need.

## Which to pick
<!-- bite: 4387b97f-bcf3-4d96-9edf-fa03d8beac1f -->

**Start with the stdlib.** Go 1.22 made it viable, dependencies are a real cost, and you can add Chi later without changing a single handler.

**Add Chi when route grouping starts hurting** — roughly when you have nested resources with layered middleware. The migration is mechanical because the types are identical.

**Choose Gin when you want the batteries** — binding, validation, and a fuller helper set — and you're comfortable committing the codebase to it. It's a reasonable choice for a team that wants fewer decisions, and it's the most popular Go web framework by a wide margin.

**Don't choose on benchmarks.**

> The Go-specific point: because everything speaks `http.Handler`, the cost of starting minimal is unusually low. In most ecosystems the framework decision is load-bearing and early; in Go you can defer it.

---

## Related
<!-- bite: a5173377-e9db-438f-bfd6-a0e578c6d553 -->
- [[backend/frameworks/gin/01-gin|Gin]] — the batteries-included alternative
- [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|net/http in Depth]] — what Chi wraps
- [[backend/frameworks/net-http/03-middleware|Middleware as Composition]] — the interface Chi preserves
- [[backend/frameworks/net-http/04-structuring-a-go-service|Structuring a Go Service]] — where routes get wired
- [[backend/frameworks/index|frameworks/]] — the cross-stack translation table
- [[backend/frameworks/chi/index|Chi]]

## About this lesson
<!-- bite: 3b907a96-4c2e-46c6-b945-589c0b5822bd -->

**Level:** Intermediate. **Covers:** What a router still adds now that the stdlib has method matching, how Chi adds it while staying `net/http` compatible, and how it compares with Gin.
