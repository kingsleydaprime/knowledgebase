# Middleware as Composition

**[Intermediate]** — No registration, no framework, no ordering config. Middleware in Go is a function that wraps a function, and that's the whole design.

## The pattern

```go
func Logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        slog.Info("request",
            "method", r.Method, "path", r.URL.Path, "dur", time.Since(start))
    })
}
```

A middleware is `func(http.Handler) http.Handler`. It takes the next handler, returns a new one that does something before and/or after calling it.

```go
handler := Logging(Auth(RateLimit(mux)))
```

That's it. No `app.use()`, no `@Injectable`, no ordering annotations — **the nesting order in the source is the execution order**. `Logging` runs first on the way in and last on the way out.

Compare with the [[backend/frameworks/README|translation table]]: Express `app.use`, Nest interceptors/guards, Spring filters. Those are registries the framework walks. Go's is function composition, which means you can read the order off the page and there's no framework to consult about precedence.

## Chaining without the nesting

Deeply nested calls get unreadable, so the usual helper:

```go
type Middleware func(http.Handler) http.Handler

func Chain(h http.Handler, mw ...Middleware) http.Handler {
    for i := len(mw) - 1; i >= 0; i-- {     // reverse, so mw[0] is outermost
        h = mw[i](h)
    }
    return h
}

handler := Chain(mux, Logging, Recoverer, Auth, RateLimit)
```

Now the list reads top-to-bottom in execution order. This is ~8 lines and it's most of what a router's middleware support gives you.

## The essential middleware

### Panic recovery

```go
func Recoverer(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                slog.Error("panic", "err", rec, "stack", string(debug.Stack()))
                http.Error(w, "internal error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

`net/http` already recovers per-connection so one panic doesn't kill the process — but it closes the connection without a response, which the client sees as a truncated read rather than a 500. Your own recoverer logs the stack and returns a proper status.

**It only catches panics in the request's own goroutine.** A panic in a goroutine your handler spawned still kills the process. → [[languages/02-go/06-goroutines-and-channels|Goroutines]]

### Request ID and structured logging

```go
type ctxKey struct{ name string }
var requestIDKey = ctxKey{"request_id"}

func RequestID(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        id := r.Header.Get("X-Request-ID")
        if id == "" { id = uuid.NewString() }
        w.Header().Set("X-Request-ID", id)

        ctx := context.WithValue(r.Context(), requestIDKey, id)
        next.ServeHTTP(w, r.WithContext(ctx))     // r.WithContext returns a COPY
    })
}

func RequestIDFrom(ctx context.Context) string {
    id, _ := ctx.Value(requestIDKey).(string)
    return id
}
```

Two conventions here matter. The **unexported key type** prevents collisions between packages — a bare string key is a real bug. And `r.WithContext(ctx)` returns a *new* request; mutating `r` in place doesn't work.

This is the legitimate use of `context.Value` from [[languages/02-go/08-context|Context]]: request-scoped data crossing API boundaries, not function arguments in disguise.

### Capturing the status code

The awkward one. `http.ResponseWriter` has no getter for the status, so logging it requires wrapping:

```go
type statusWriter struct {
    http.ResponseWriter
    status int
    written int64
}

func (w *statusWriter) WriteHeader(code int) {
    w.status = code
    w.ResponseWriter.WriteHeader(code)
}

func (w *statusWriter) Write(b []byte) (int, error) {
    if w.status == 0 { w.status = http.StatusOK }   // implicit 200
    n, err := w.ResponseWriter.Write(b)
    w.written += int64(n)
    return n, err
}
```

> **Wrapping `http.ResponseWriter` breaks optional interfaces.** The real writer may also implement `http.Flusher`, `http.Hijacker`, or `io.ReaderFrom`. Your wrapper doesn't, so SSE, WebSocket upgrades and `sendfile` silently stop working.

The fix is to implement the ones you need:

```go
func (w *statusWriter) Flush() {
    if f, ok := w.ResponseWriter.(http.Flusher); ok { f.Flush() }
}

func (w *statusWriter) Hijack() (net.Conn, *bufio.ReadWriter, error) {
    if h, ok := w.ResponseWriter.(http.Hijacker); ok { return h.Hijack() }
    return nil, nil, errors.New("hijack not supported")
}
```

This is a genuine wart in the design, and it's why `chi/middleware.NewWrapResponseWriter` exists — it handles the interface matrix for you.

### Auth

```go
func Auth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")
        claims, err := verify(token)
        if err != nil {
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return                                    // do NOT call next
        }
        ctx := context.WithValue(r.Context(), userKey, claims)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

**Returning without calling `next` is how you short-circuit.** No `abort()`, no special return value — you just don't continue the chain. Forgetting the `return` after writing an error is a classic bug: the handler runs anyway and you get a doubled response.

### Timeout

```go
handler = http.TimeoutHandler(handler, 5*time.Second, "request timed out")
```

Standard library. Note it doesn't stop the handler goroutine — it stops *writing* the response. Real cancellation needs the handler to respect `ctx.Done()`, which is why context propagation matters more than this wrapper.

## Per-route middleware

The stdlib mux applies middleware to everything or nothing. Scoping it means composing at registration:

```go
mux.Handle("GET /admin/{$}", Chain(adminHandler, RequireAdmin))
mux.Handle("GET /public", publicHandler)
```

Workable, and verbose once you have twenty routes. **Route groups with shared middleware are the main practical reason to reach for a router.** → [[backend/frameworks/go/03-routers-chi-and-gin|Routers]]

(`{$}` matches the exact path only, without the trailing-slash subtree — a Go 1.22 addition that's easy to miss.)

## Ordering

Order is a correctness concern, not a preference:

```go
handler := Chain(mux,
    RequestID,     // 1. first — everything downstream logs the ID
    Logging,       // 2. wraps everything, so it times the full request
    Recoverer,     // 3. inside Logging, so panics still get logged as requests
    CORS,          // 4. before auth — preflight OPTIONS must not need a token
    RateLimit,     // 5. before auth — cheap rejection first
    Auth,          // 6.
)
```

Two that catch people: **CORS before auth**, because a preflight `OPTIONS` carries no credentials and must succeed; and **rate limiting before auth**, because verifying a token on a request you're about to reject is wasted work — and an unauthenticated flood is exactly what you're limiting.

Whether `Recoverer` goes inside or outside `Logging` is a real choice: inside means a panic is logged as a completed request with a 500; outside means the recoverer sees panics from the logger itself.

## Why this composes better than a registry

The standard interface means **middleware from unrelated libraries interoperates**. A `chi` middleware works with a Gin engine, with the stdlib mux, or with your own handler, because they all speak `http.Handler`.

That's not true in most ecosystems. Express middleware is Express-specific; a Spring filter isn't portable to a different framework. Go's ecosystem got composability by having one small interface everyone agreed on early — which is a good argument for defining the narrowest possible interface, from [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]].

The cost: no framework means no framework *features*. No automatic dependency injection into middleware, no declarative ordering, no per-route metadata. You write the wiring, and it's explicit.

---

## Related
- [[backend/frameworks/go/01-net-http-in-depth|net/http in Depth]] — the `Handler` interface this builds on
- [[backend/frameworks/go/03-routers-chi-and-gin|Routers: Chi and Gin]] — what a router adds
- [[languages/02-go/08-context|Go: Context]] — request-scoped values and cancellation
- [[backend/06-cross-cutting/README|Cross-Cutting Concerns]] — what middleware is for, conceptually
- [[backend/frameworks/go/README|Go backends]]
