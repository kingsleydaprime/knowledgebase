# Structuring a Go Service

**[Intermediate]** — Dependency injection without a container, the handler-as-method pattern, and why Go services have no `@Autowired`.

## No DI container, and why

Go has no framework container. There's no `@Injectable`, no `@Service`, no annotation scanning. Dependencies are **struct fields set in `main`**.

```go
type Server struct {
    users  UserStore
    mailer Mailer
    logger *slog.Logger
}

func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
    u, err := s.users.Get(r.Context(), r.PathValue("id"))
    ...
}
```

Handlers are **methods on a struct**, so they reach dependencies through the receiver. That's the entire pattern, and it replaces Spring's container and Nest's module system.

What you give up: automatic wiring, lifecycle scopes, and configuration-driven substitution. What you get: the dependency graph is a function you can read, it's checked at compile time, and there's no reflection or startup magic to debug.

## Wiring in `main`

```go
func main() {
    if err := run(); err != nil {
        slog.Error("fatal", "err", err)
        os.Exit(1)
    }
}

func run() error {
    cfg, err := LoadConfig()
    if err != nil { return fmt.Errorf("config: %w", err) }

    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    db, err := sql.Open("pgx", cfg.DatabaseURL)
    if err != nil { return fmt.Errorf("open db: %w", err) }
    defer db.Close()
    if err := db.PingContext(ctx); err != nil { return fmt.Errorf("ping db: %w", err) }

    srv := &Server{
        users:  postgres.NewUserStore(db),      // concrete type, satisfying an interface
        mailer: smtp.NewMailer(cfg.SMTP),
        logger: logger,
    }

    return srv.ListenAndServe(cfg.Addr)
}
```

**The `run() error` pattern matters.** `os.Exit` skips deferred functions, so `main` must not do the work — otherwise `defer db.Close()` never runs. Put everything in `run`, let `main` handle the exit. → [[languages/02-go/10-the-standard-library|Go: The Standard Library]]

Note the wiring is explicit and ordered: config, then logger, then database, then the things that need them. When startup fails you get a wrapped error naming the step, not a stack trace from inside a container.

## Interfaces declared by the consumer

The critical Go idiom, and the reason none of this needs a framework:

```go
// package server — declares what IT needs
type UserStore interface {
    Get(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, u *User) error
}
```

```go
// package postgres — knows nothing about `server`
type UserStore struct { db *sql.DB }

func (s *UserStore) Get(ctx context.Context, id string) (*User, error) { ... }
```

`postgres` doesn't import `server`, doesn't mention the interface, and doesn't declare that it implements anything. It just has the methods.

That inverts the dependency direction with no framework and no configuration — [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] falling out of the language. Compare with [[languages/01-java/03-tooling/02-dependency-injection|Spring's container]], which achieves the same inversion at runtime via reflection.

Two rules that follow:

**Keep interfaces small.** Two or three methods. A twelve-method interface is miserable to fake in a test, which is the feedback loop that keeps them small.

**Declare them where they're used, not where they're implemented.** An interface in the `postgres` package is usually the wrong place — it means the implementer is guessing at what consumers need.

## Layout

```
myservice/
├── cmd/api/main.go              ← wiring only
├── internal/
│   ├── config/config.go
│   ├── user/                    ← BY FEATURE
│   │   ├── service.go
│   │   ├── handler.go
│   │   └── store.go
│   ├── order/
│   └── platform/
│       ├── postgres/
│       └── smtp/
└── go.mod
```

**Organise by feature, not by layer.** `internal/user/` beats `internal/handlers/` + `internal/services/` + `internal/repositories/` — adding a feature touches one directory, and Go's package-level visibility actually enforces the boundary. → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Organising by Layer vs by Feature]]

`internal/` is compiler-enforced: nothing outside your module can import it. That's real access control, and it's the right default for a service. → [[languages/02-go/12-modules-and-project-layout|Modules and Project Layout]]

**Start flatter than this.** A `main.go` plus three packages is a perfectly good service. Structure when flatness hurts.

## Handler patterns

**Closure over dependencies**, when a handler needs one thing:

```go
func handleGetUser(store UserStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        u, err := store.Get(r.Context(), r.PathValue("id"))
        ...
    }
}

mux.Handle("GET /users/{id}", handleGetUser(store))
```

This is nice for per-handler setup — compile a template or a regex once, outside the returned closure, and it happens at startup rather than per request.

**Methods on a struct**, when handlers share several dependencies — the more common shape, and the one above.

## Error handling

Handlers returning `error` is cleaner than every handler writing its own response, but `http.HandlerFunc` doesn't return anything. The standard workaround:

```go
type apiHandler func(http.ResponseWriter, *http.Request) error

func (h apiHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if err := h(w, r); err != nil {
        writeError(w, err)
    }
}

func writeError(w http.ResponseWriter, err error) {
    var vErr *ValidationError
    switch {
    case errors.Is(err, ErrNotFound):
        http.Error(w, "not found", http.StatusNotFound)
    case errors.As(err, &vErr):
        writeJSON(w, http.StatusBadRequest, vErr)
    default:
        slog.Error("internal", "err", err)                  // log the detail
        http.Error(w, "internal error", http.StatusInternalServerError)  // don't leak it
    }
}
```

```go
mux.Handle("GET /users/{id}", apiHandler(s.getUser))

func (s *Server) getUser(w http.ResponseWriter, r *http.Request) error {
    u, err := s.users.Get(r.Context(), r.PathValue("id"))
    if err != nil { return fmt.Errorf("get user: %w", err) }
    return writeJSON(w, http.StatusOK, u)
}
```

One place maps errors to statuses, handlers just `return err`, and the two rules hold: **log internal detail, return generic**. This is Go's hand-written equivalent of Spring's `@ControllerAdvice` — more code, and no framework knowledge required to read it. → [[languages/02-go/05-errors|Go: Errors]]

## Config

```go
type Config struct {
    Addr        string
    DatabaseURL string
    LogLevel    slog.Level
}

func LoadConfig() (*Config, error) {
    cfg := &Config{
        Addr: envOr("ADDR", ":8080"),
    }
    cfg.DatabaseURL = os.Getenv("DATABASE_URL")
    if cfg.DatabaseURL == "" {
        return nil, errors.New("DATABASE_URL is required")
    }
    return cfg, nil
}
```

**Validate config at startup and fail loudly.** A service that boots with a missing database URL and fails on the first request is worse than one that refuses to start. → [[devops/09-secret-management/README|Secret Management]]

`envconfig` or `viper` if you want tags and file support; plain `os.Getenv` is fine and dependency-free for a handful of values.

## The service layer question

Whether to have one between handler and store:

**Skip it** when the handler is decode → store call → encode. A service that only forwards is noise.

**Add it** when there's business logic: multi-step operations, transactions spanning stores, or logic used by both HTTP and a background worker.

```go
func (s *UserService) Register(ctx context.Context, email string) (*User, error) {
    if _, err := s.store.GetByEmail(ctx, email); err == nil {
        return nil, ErrEmailTaken
    }
    u := &User{Email: email, ID: uuid.NewString()}
    if err := s.store.Create(ctx, u); err != nil {
        return nil, fmt.Errorf("create user: %w", err)
    }
    if err := s.mailer.SendWelcome(ctx, u); err != nil {
        s.logger.Warn("welcome email failed", "err", err)    // don't fail registration
    }
    return u, nil
}
```

Go's culture leans toward fewer layers than Java's. Add one when it earns its place, not by default. → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]]

## Wire, and whether you need it

`google/wire` does compile-time DI via code generation — you declare providers, it generates the wiring function.

For most services, hand-written wiring in `run()` is clearer and shorter than the generator setup. Wire earns its place when the graph is genuinely large (dozens of components with deep dependencies), which most services never reach.

**Never use a reflection-based DI container in Go.** They exist; they trade away the compile-time checking that makes explicit wiring worth its verbosity.

---

## Related
- [[backend/frameworks/go/05-database-access|Database Access]] — what the store layer does
- [[backend/frameworks/go/06-testing-and-production|Testing and Production]] — why small interfaces pay off
- [[languages/02-go/04-methods-and-interfaces|Go: Methods and Interfaces]] — consumer-declared interfaces
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|DI and Wiring]] — the concept, framework-agnostic
- [[backend/frameworks/go/README|Go backends]]
