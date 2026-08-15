# `net/http` in Depth

**[Intermediate]** — The standard library as a production HTTP server, and the configuration that separates a toy from something you'd put on the internet.

**Source:** `[reference]`. Assumes [[languages/02-go/README|the Go course]] and [[backend/01-foundations/README|backend foundations]].

## The two interfaces

The entire server API is two types:

```go
type Handler interface {
    ServeHTTP(w http.ResponseWriter, r *http.Request)
}

type HandlerFunc func(http.ResponseWriter, *http.Request)   // adapts a func to Handler
```

That's it. Every router, every middleware, every framework in Go is built on `Handler` — which is why they interoperate. A Chi router is an `http.Handler`; so is a Gin engine; so is your own function. You can mix them in one process without adapters.

This is unusual. Express middleware doesn't work in Nest, and a Spring filter isn't a servlet you can hand elsewhere. Go's single small interface is the reason its HTTP ecosystem composes.

## Routing (Go 1.22+)

```go
mux := http.NewServeMux()

mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("DELETE /users/{id}", deleteUser)
mux.HandleFunc("GET /files/{path...}", serveFile)    // trailing wildcard
mux.HandleFunc("/", notFound)                         // catch-all

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
}
```

Go 1.22 gave the standard mux **method matching and path wildcards**, which is the change that made third-party routers optional. Before it, `mux.HandleFunc("/users/", ...)` matched a prefix and you parsed the method and the ID yourself — genuinely painful, and the reason everyone reached for Chi or Gin.

Precedence is **most-specific-wins**, not registration order: `/users/{id}` beats `/users/`, and a pattern with a method beats one without.

```go
mux.Handle("/api/", http.StripPrefix("/api", apiMux))   // sub-router by composition
```

## The server, configured properly

```go
srv := &http.Server{
    Addr:              ":8080",
    Handler:           mux,
    ReadHeaderTimeout: 5 * time.Second,
    ReadTimeout:       10 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       120 * time.Second,
    MaxHeaderBytes:    1 << 20,
    ErrorLog:          log.New(os.Stderr, "http: ", log.LstdFlags),
}
log.Fatal(srv.ListenAndServe())
```

> **`http.ListenAndServe(":8080", mux)` has no timeouts at all.** A client that opens a connection and sends one byte per minute holds a goroutine and a file descriptor indefinitely. That's **slowloris**, and it's the single most common production mistake in Go web code.

What each timeout covers:

| Field | Covers |
|---|---|
| `ReadHeaderTimeout` | connection accepted → headers fully read. **The slowloris defence** |
| `ReadTimeout` | connection accepted → request body fully read |
| `WriteTimeout` | end of headers → response written |
| `IdleTimeout` | keep-alive idle time between requests |

`WriteTimeout` is a wall-clock deadline covering the whole response, so it must exceed your slowest legitimate handler. For streaming or long-poll endpoints, set it to 0 and enforce per-request deadlines with `context` instead. → [[languages/02-go/08-context|Context]]

## The response writer

```go
func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")   // headers FIRST
    w.WriteHeader(http.StatusCreated)                     // status SECOND
    json.NewEncoder(w).Encode(user)                       // body LAST
}
```

**Order matters and is not enforced.** Writing the body implicitly calls `WriteHeader(200)`, so a status set afterwards is silently ignored and logged as `superfluous response.WriteHeader call`. Headers set after the first write don't appear at all.

The consequence for error handling: you must decide the status *before* writing anything. A handler that streams a partial response and then hits an error cannot change its mind — the status is already on the wire.

```go
http.Error(w, "not found", http.StatusNotFound)    // sets Content-Type, status, body
http.Redirect(w, r, "/new", http.StatusFound)
http.NotFound(w, r)
```

## Reading a request

```go
func createUser(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()                          // cancelled when the client disconnects

    r.URL.Query().Get("filter")
    r.Header.Get("Authorization")
    r.PathValue("id")

    var req CreateUserRequest
    dec := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20))   // CAP THE BODY
    dec.DisallowUnknownFields()
    if err := dec.Decode(&req); err != nil {
        http.Error(w, "invalid body", http.StatusBadRequest)
        return
    }
}
```

Three things worth making habits:

**`http.MaxBytesReader`** — without it, `json.Decode` will happily read a 10GB body into memory. The server does not bound request bodies for you.

**`DisallowUnknownFields`** — turns a typo'd field name from a silently-ignored zero value into a 400.

**`r.Context()`** — cancelled on client disconnect. Pass it into every database call and outbound request, or you'll keep doing work for a client that left. This is the whole point of [[languages/02-go/08-context|context]] and it's the most commonly skipped step.

`r.Body` is closed by the server; you don't need to. But if you *don't* read it to completion, the connection can't be reused for keep-alive.

## Graceful shutdown

```go
func main() {
    srv := &http.Server{Addr: ":8080", Handler: mux}

    go func() {
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            log.Fatalf("listen: %v", err)
        }
    }()

    ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
    defer stop()
    <-ctx.Done()                                  // wait for SIGINT/SIGTERM

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    if err := srv.Shutdown(shutdownCtx); err != nil {
        log.Printf("forced shutdown: %v", err)
    }
}
```

`Shutdown` stops accepting new connections and waits for in-flight requests to finish, up to the deadline. Without it, a deploy kills requests mid-flight.

This matters more than it sounds under [[devops/05-orchestration/README|Kubernetes]]: the moment a pod is marked terminating, it gets `SIGTERM` while the load balancer may still send it traffic for a few seconds. Handle the signal, drain, then exit.

`ErrServerClosed` is the expected return from `ListenAndServe` after `Shutdown` — treating it as an error is a common noisy-log bug.

## As a client

```go
client := &http.Client{
    Timeout: 10 * time.Second,           // the DEFAULT CLIENT HAS NO TIMEOUT
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,          // default is 2 — usually too low
        IdleConnTimeout:     90 * time.Second,
    },
}

req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
resp, err := client.Do(req)
if err != nil { return err }
defer resp.Body.Close()                   // MANDATORY

io.Copy(io.Discard, resp.Body)            // drain, so the connection is reused
```

Three real bugs live here:

**`http.DefaultClient` waits forever.** Always construct your own with a timeout.

**A body you don't close leaks the connection**, and the goroutine reading it. This is the most common source of "my Go service slowly runs out of file descriptors".

**`MaxIdleConnsPerHost: 2`** is the default, which throttles you badly when calling one backend heavily — connections get closed and reopened instead of pooled.

**Reuse one `http.Client`.** Creating one per request defeats connection pooling entirely.

## TLS

```go
srv.ListenAndServeTLS("cert.pem", "key.pem")
```

In practice you usually terminate TLS at a reverse proxy or load balancer and run plain HTTP behind it. If you do terminate in Go, `autocert` handles Let's Encrypt. → [[foundations/networking/12-tls-and-transport-security|TLS]]

## What the stdlib doesn't give you

Being honest about the gaps, because "the stdlib is enough" is true but not unconditionally:

- **No middleware chaining helper** — trivial to write, and note 02 does
- **No request validation** — you write it or use a library
- **No structured request logging** — you write it
- **No route grouping with shared middleware** — the main thing routers add
- **No graceful-shutdown wiring** — the code above, every time
- **No dependency injection** — deliberate; Go uses struct fields

None of these are hard. They're each 10–50 lines you write once. The question is whether you'd rather write and own them or take a dependency — which is what [[backend/frameworks/go/03-routers-chi-and-gin|note 03]] is about.

---

## Related
- [[backend/frameworks/go/02-middleware-as-composition|Middleware as Composition]] — the next layer up
- [[backend/frameworks/go/06-testing-and-production|Testing and Production]] — `httptest` and observability
- [[languages/02-go/10-the-standard-library|Go: The Standard Library]] — the `io` interfaces underneath
- [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]] — the model this implements
- [[backend/frameworks/go/README|Go backends]]
