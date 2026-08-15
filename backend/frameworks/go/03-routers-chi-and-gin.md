# Routers: Chi and Gin

**[Intermediate]** — What a router actually adds now that the stdlib has method matching, and the philosophical split between the two main options.

## What changed in Go 1.22

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

Handlers are `http.HandlerFunc`. Middleware is `func(http.Handler) http.Handler` — the exact signature from [[backend/frameworks/go/02-middleware-as-composition|the previous note]]. A `chi.Router` *is* an `http.Handler`.

So there's no lock-in: you can mount a Chi router inside a stdlib mux, use stdlib middleware in Chi, and swap Chi out later without touching handler code. It's a thin layer that adds grouping and stops.

Chi's `middleware` package is worth knowing even if you don't use the router — `middleware.WrapResponseWriter` solves the `Flusher`/`Hijacker` problem from note 02 properly.

## Gin

```go
import "github.com/gin-gonic/gin"

r := gin.Default()                      // Logger + Recovery already attached

r.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")
    filter := c.Query("filter")

    var req CreateUser
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusOK, user)
})

api := r.Group("/api/v1", AuthMiddleware())
{
    api.GET("/users", listUsers)
    api.POST("/users", createUser)
}

r.Run(":8080")
```

Gin uses **its own context type**, `*gin.Context`, which carries the request, response, params, bound data, errors, and per-request key/value storage.

That's the trade. You get:

```go
c.JSON(200, obj)                        // marshal + content-type + status
c.ShouldBindJSON(&req)                  // decode + VALIDATE via struct tags
c.AbortWithStatusJSON(401, gin.H{...})  // stop the chain
c.Set("user", u); c.MustGet("user")     // request-scoped storage
c.ClientIP()                            // parses X-Forwarded-For
```

Binding with validation is the genuinely useful part:

```go
type CreateUser struct {
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age"   binding:"gte=0,lte=130"`
}
```

One call decodes and validates, and returns a structured error. In stdlib Go you write that yourself.

And you lose: **handlers are no longer `http.HandlerFunc`.** Gin middleware is `gin.HandlerFunc`. Neither is portable, so adopting Gin is a decision about the whole codebase, not one route.

Gin does provide `gin.WrapH(h http.Handler)` and `gin.WrapF` to mount stdlib handlers, so the boundary is crossable in one direction.

## The comparison

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

**Start with the stdlib.** Go 1.22 made it viable, dependencies are a real cost, and you can add Chi later without changing a single handler.

**Add Chi when route grouping starts hurting** — roughly when you have nested resources with layered middleware. The migration is mechanical because the types are identical.

**Choose Gin when you want the batteries** — binding, validation, and a fuller helper set — and you're comfortable committing the codebase to it. It's a reasonable choice for a team that wants fewer decisions, and it's the most popular Go web framework by a wide margin.

**Don't choose on benchmarks.**

> The Go-specific point: because everything speaks `http.Handler`, the cost of starting minimal is unusually low. In most ecosystems the framework decision is load-bearing and early; in Go you can defer it.

---

## Related
- [[backend/frameworks/go/01-net-http-in-depth|net/http in Depth]] — what these wrap
- [[backend/frameworks/go/02-middleware-as-composition|Middleware as Composition]] — the interface Chi preserves
- [[backend/frameworks/go/04-structuring-a-go-service|Structuring a Go Service]] — where routes get wired
- [[backend/frameworks/README|frameworks/]] — the cross-stack translation table
- [[backend/frameworks/go/README|Go backends]]
