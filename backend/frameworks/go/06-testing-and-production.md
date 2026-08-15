# Testing and Production

**[Intermediate]** — `httptest`, testing without a mocking framework, and what a Go service needs before it faces real traffic.

## `httptest`

Two tools, covering both directions.

**Testing a handler directly** — no network, no port:

```go
func TestGetUser(t *testing.T) {
    srv := &Server{users: &fakeUserStore{
        users: map[string]*User{"1": {ID: "1", Email: "k@example.com"}},
    }}

    req := httptest.NewRequest(http.MethodGet, "/users/1", nil)
    req.SetPathValue("id", "1")               // Go 1.22+, for handlers using PathValue
    rec := httptest.NewRecorder()

    srv.handleGetUser(rec, req)

    if rec.Code != http.StatusOK {
        t.Fatalf("status = %d, want 200", rec.Code)
    }
    var got User
    if err := json.NewDecoder(rec.Body).Decode(&got); err != nil {
        t.Fatalf("decode: %v", err)
    }
    if got.Email != "k@example.com" {
        t.Errorf("email = %q", got.Email)
    }
}
```

**Testing through the router** — a real server on a random port, which exercises middleware and routing too:

```go
func TestAPI(t *testing.T) {
    srv := httptest.NewServer(newRouter(deps))
    defer srv.Close()

    resp, err := srv.Client().Get(srv.URL + "/users/1")
    if err != nil { t.Fatal(err) }
    defer resp.Body.Close()
}
```

`httptest.NewServer` is the one to use when you want to test the whole stack including middleware ordering. `NewRecorder` is faster and better for a single handler's logic.

## Fakes, not mocks

Because [[languages/02-go/04-methods-and-interfaces|interfaces are satisfied implicitly]], a test double is just a struct:

```go
type fakeUserStore struct {
    users map[string]*User
    err   error                     // to force the failure path
}

func (f *fakeUserStore) Get(ctx context.Context, id string) (*User, error) {
    if f.err != nil { return nil, f.err }
    u, ok := f.users[id]
    if !ok { return nil, ErrNotFound }
    return u, nil
}
```

No mocking framework, no annotations, no generated code. This is the practical payoff of consumer-declared, small interfaces — and it's also the feedback loop that keeps them small, because faking a twelve-method interface is miserable enough to make you split it.

`mockall`-style generators (`gomock`, `mockery`) exist. They earn their place for large interfaces with strict call-order assertions; for most services a hand-written fake is shorter and clearer.

## Table-driven tests

The dominant Go idiom, and worth applying to handlers:

```go
func TestCreateUser(t *testing.T) {
    tests := []struct {
        name       string
        body       string
        storeErr   error
        wantStatus int
    }{
        {"valid", `{"email":"a@b.com"}`, nil, http.StatusCreated},
        {"bad json", `{`, nil, http.StatusBadRequest},
        {"missing email", `{}`, nil, http.StatusBadRequest},
        {"duplicate", `{"email":"a@b.com"}`, ErrEmailTaken, http.StatusConflict},
        {"store down", `{"email":"a@b.com"}`, errors.New("boom"), http.StatusInternalServerError},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            srv := &Server{users: &fakeUserStore{err: tt.storeErr}}
            req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(tt.body))
            rec := httptest.NewRecorder()

            srv.handleCreateUser(rec, req)

            if rec.Code != tt.wantStatus {
                t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
            }
        })
    }
}
```

Adding an error case is one line, which is exactly the pressure you want — the error paths are where handler bugs live. → [[languages/02-go/11-testing-and-benchmarking|Testing and Benchmarking]]

## Integration tests against a real database

```go
func TestUserStore(t *testing.T) {
    if testing.Short() { t.Skip("integration test") }

    ctx := context.Background()
    container, err := postgres.Run(ctx, "postgres:16-alpine",
        postgres.WithDatabase("test"),
        testcontainers.WithWaitStrategy(wait.ForListeningPort("5432/tcp")))
    if err != nil { t.Fatal(err) }
    t.Cleanup(func() { container.Terminate(ctx) })

    dsn, _ := container.ConnectionString(ctx, "sslmode=disable")
    db, _ := sql.Open("pgx", dsn)
    runMigrations(t, db)

    store := postgres.NewUserStore(db)
    // ...real SQL against a real Postgres
}
```

**Test SQL against the real database.** A fake store proves your handler logic; it proves nothing about your queries. `testcontainers-go` spins up a real Postgres per test package, which is fast enough now that mocking the database is hard to justify.

`go test -short` to skip them locally, run everything in CI.

## Race detection

```bash
go test -race ./...
```

**In CI, always.** Handlers run concurrently by definition — one goroutine per request — so any shared mutable state in a `Server` struct is a race waiting to happen. This is the single highest-value flag in Go testing. → [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]]

## Observability

### Structured logging

```go
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
slog.SetDefault(logger)

func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
    log := s.logger.With("request_id", RequestIDFrom(r.Context()), "path", r.URL.Path)
    log.Info("fetching user", "id", id)
}
```

`log/slog` since Go 1.21 — JSON output that a log aggregator can actually query, with a request ID threading through every line of a request. That correlation is what makes logs useful during an incident. → [[devops/10-observability/README|Observability]]

### Metrics

```go
var requestDuration = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Buckets: prometheus.DefBuckets,
    },
    []string{"method", "route", "status"},
)

// in middleware:
requestDuration.WithLabelValues(r.Method, route, strconv.Itoa(sw.status)).
    Observe(time.Since(start).Seconds())

mux.Handle("GET /metrics", promhttp.Handler())
```

> **Label with the route pattern (`/users/{id}`), not the actual path (`/users/12345`).** Every distinct label value is a separate time series; using raw paths produces unbounded cardinality and will take down your Prometheus.

### Tracing

```go
import "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"

handler = otelhttp.NewHandler(mux, "api")
```

OpenTelemetry has good `net/http` integration precisely because everything is an `http.Handler`. Traces matter once one request fans out across services.

### pprof

```go
import _ "net/http/pprof"

go func() { log.Println(http.ListenAndServe("localhost:6060", nil)) }()
```

> **Bind pprof to localhost or a separate admin port.** `/debug/pprof` on a public interface is a real information leak — and the blank import registers it on `http.DefaultServeMux`, so if you serve `DefaultServeMux` publicly, you've exposed it by accident.

```bash
go tool pprof http://localhost:6060/debug/pprof/goroutine?debug=2   # check FIRST
go tool pprof -http=:8081 http://localhost:6060/debug/pprof/profile?seconds=30
```

**The goroutine profile is the first thing to check** in a mysterious production problem. A count that only climbs is a leak — usually a goroutine blocked on a channel nobody sends to, or an HTTP response body never closed. → [[languages/02-go/13-performance-and-runtime|Performance and the Runtime]]

## Containers

```dockerfile
FROM golang:1.24-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download                          # cached layer — deps change rarely
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app ./cmd/api

FROM gcr.io/distroless/static-nonroot
COPY --from=build /app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

**`CGO_ENABLED=0`** produces a genuinely static binary, which is what lets the final image be `distroless/static` or `scratch` — a few megabytes with no shell, no package manager, and almost no attack surface. This is Go's biggest practical deployment advantage. → [[devops/02-docker/README|Docker]]

**`-ldflags="-s -w"`** strips debug info; smaller binary, and you lose symbol names in stack traces, so decide deliberately.

## The container gotcha

```go
import _ "go.uber.org/automaxprocs"
```

**Go reads the host's CPU count, not the cgroup limit.** A 2-CPU container on a 64-core node gets `GOMAXPROCS=64`, causing heavy context switching and CFS throttling. Combined with `GOMEMLIMIT` for the heap:

```go
// or set GOMEMLIMIT=450MiB in the environment, just under the container limit
debug.SetMemoryLimit(450 << 20)
```

These two lines fix the most common Go-on-Kubernetes performance complaints, and neither is on by default.

## The production checklist

1. **Server timeouts set** — `ReadHeaderTimeout` especially → [[backend/frameworks/go/01-net-http-in-depth|net/http]]
2. **Graceful shutdown** on `SIGTERM`
3. **`SetMaxOpenConns`** on the database pool → [[backend/frameworks/go/05-database-access|Database Access]]
4. **Request body size capped** with `MaxBytesReader`
5. **Panic recovery middleware** with stack logging
6. **Structured logs with a request ID**
7. **Liveness and readiness split**, liveness checking nothing external
8. **Metrics with bounded label cardinality**
9. **pprof on a private port**
10. **`automaxprocs` and `GOMEMLIMIT`** in containers
11. **`go test -race` in CI**
12. **`govulncheck ./...`** in CI — scans your dependency graph against the Go vulnerability database

```bash
go vet ./...
staticcheck ./...
govulncheck ./...
go test -race -cover ./...
```

---

## Related
- [[backend/frameworks/go/01-net-http-in-depth|net/http in Depth]] — timeouts and shutdown
- [[languages/02-go/11-testing-and-benchmarking|Go: Testing and Benchmarking]] — the testing idioms
- [[devops/10-observability/README|Observability]] · [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]]
- [[backend/07-practices/02-testing-a-backend|Testing a Backend]] — the strategy behind this
- [[backend/frameworks/go/README|Go backends]]
