# The Standard Library

**[Intermediate]** — The packages you'll actually use, and why Go's stdlib being genuinely sufficient is a cultural fact, not just a technical one.

## Why it matters more here

In Node you reach for a package. In Go you reach for the standard library first, and usually stop there. `net/http` is a production-grade HTTP server — not a toy you replace with Express. `encoding/json` is the JSON library. `database/sql` is the database layer.

The consequence is a dependency graph you can read. A typical Go service has ten direct dependencies where the Node equivalent has four hundred, which changes the [[devops/06-ci-cd/10-pipeline-security|supply-chain]] and upgrade story completely.

The trade is that the stdlib is *deliberately* minimal, so some things you'd expect are missing and you write them yourself.

## `io` — the composition layer

```go
type Reader interface{ Read(p []byte) (n int, err error) }
type Writer interface{ Write(p []byte) (n int, err error) }
```

Learn these before anything else. A file, a network connection, an HTTP request body, a gzip stream, a hash, an in-memory buffer, and `os.Stdin` are all `io.Reader`s — so anything written against `io.Reader` works with all of them.

```go
io.Copy(dst, src)                  // stream, constant memory
io.ReadAll(r)                      // read everything into memory — bounded input only
io.LimitReader(r, 1<<20)           // cap at 1MB; use on ANY untrusted input
io.TeeReader(r, w)                 // read from r while writing a copy to w
io.MultiWriter(w1, w2)             // write to both
```

`io.Copy` streaming a 4GB file in constant memory, versus `io.ReadAll` loading it all — that's the difference between a service that works and one that OOMs. Reach for `Copy` by default.

## `net/http`

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /users/{id}", getUser)     // method + wildcard routing, Go 1.22+
mux.HandleFunc("POST /users", createUser)

srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  120 * time.Second,
}
log.Fatal(srv.ListenAndServe())
```

**Always construct an `http.Server` explicitly.** `http.ListenAndServe(":8080", mux)` has **no timeouts at all** — a slow-loris client can hold connections open indefinitely. This is the most common production mistake in Go web code.

Go 1.22 gave the standard mux method-aware routing and path wildcards, which removed most of the reason to pull in a router at all.

```go
func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")            // 1.22+
    ctx := r.Context()
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)       // must come AFTER headers, BEFORE body
    json.NewEncoder(w).Encode(user)
}
```

Writing to `w` implicitly calls `WriteHeader(200)`, so setting a status afterwards is silently ignored — the "superfluous WriteHeader call" log line.

Middleware is just a function wrapping a handler, with no framework required:

```go
func Logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

handler := Logging(Recoverer(mux))
```

That's the whole middleware concept — no registration, no ordering config, just function composition. → [[backend/frameworks/go/README|Go Backends]]

### As a client

```go
client := &http.Client{Timeout: 10 * time.Second}   // the DEFAULT CLIENT HAS NO TIMEOUT
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := client.Do(req)
if err != nil { return err }
defer resp.Body.Close()      // MANDATORY — otherwise you leak the connection
```

Both comments are load-bearing. `http.DefaultClient` waits forever, and a body you don't close is a connection that never returns to the pool.

## `encoding/json`

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
    pass  string `json:"-"`              // unexported: never marshalled anyway
}

data, err := json.Marshal(u)
err = json.Unmarshal(data, &u)

json.NewEncoder(w).Encode(u)     // stream to a Writer — preferred for HTTP
json.NewDecoder(r.Body).Decode(&u)
```

**Only exported fields are marshalled.** A lowercase field is invisible to `encoding/json`, silently — the most common "why is my JSON empty" cause.

Unmarshalling into a struct **ignores unknown fields** by default and leaves missing ones at their zero value. That means you cannot distinguish "field absent" from "field was 0" without a pointer field or `json.RawMessage`. For strictness:

```go
dec := json.NewDecoder(r.Body)
dec.DisallowUnknownFields()
```

## `time`

```go
time.Now()
time.Since(start)                    // NOT time.Now().Sub(start)
time.Now().Add(24 * time.Hour)
d := 500 * time.Millisecond          // Duration is an int64 of nanoseconds
time.Sleep(d)
```

Durations being a typed integer means `5 * time.Second` type-checks and `5` alone doesn't — a good example of the named-type discipline paying off.

Formatting uses a **reference time**, not format specifiers, which is Go's most-mocked API:

```go
t.Format("2006-01-02 15:04:05")      // the reference date is 01/02 03:04:05PM '06 -0700
t.Format(time.RFC3339)               // use the constants
```

For anything measuring elapsed time, prefer `time.Since` — it uses the monotonic clock and isn't affected by NTP adjustments.

## `os` and `flag`

```go
os.Getenv("PORT")
v, ok := os.LookupEnv("PORT")        // distinguishes empty from unset
os.ReadFile(path) / os.WriteFile(path, data, 0644)
os.Exit(1)                           // does NOT run deferred functions

port := flag.Int("port", 8080, "port to listen on")
flag.Parse()
```

`os.Exit` skipping defers is worth remembering — put cleanup in a `run() error` function and let `main` do the exiting:

```go
func main() {
    if err := run(); err != nil {
        log.Fatal(err)     // log.Fatal is os.Exit(1) — defers in run() already ran
    }
}
```

## `strings`, `strconv`, `bytes`

```go
strings.Split / Join / Contains / HasPrefix / TrimSpace / ReplaceAll / Fields
strings.EqualFold(a, b)              // case-insensitive comparison, done right

var sb strings.Builder               // O(n) concatenation
sb.WriteString("x")
sb.String()

strconv.Itoa(42) / strconv.Atoi("42")
strconv.ParseFloat(s, 64) / strconv.FormatInt(n, 10)
```

Building strings with `+=` in a loop is O(n²) because strings are immutable — `strings.Builder` is the fix, same as Java's `StringBuilder`.

`bytes` mirrors `strings` for `[]byte`. Working in bytes avoids conversions in hot paths.

## `log/slog` — structured logging

Since Go 1.21, structured logging is standard:

```go
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
slog.SetDefault(logger)

slog.Info("request handled", "method", r.Method, "status", 200, "dur", elapsed)
logger.With("request_id", id).Info("processing")
```

Use it over `log` for anything that ships. JSON output is what makes logs queryable in [[devops/10-observability/README|an observability stack]] — the difference between grep and a real query.

## The rest, briefly

| Package | For |
|---|---|
| `database/sql` | the DB interface; you add a driver |
| `regexp` | RE2 — linear time, no backtracking, so no ReDoS |
| `sort` | mostly superseded by `slices` |
| `errors` | `Is`, `As`, `Join` |
| `context` | → [[languages/02-go/08-context\|Context]] |
| `sync`, `sync/atomic` | → [[languages/02-go/07-concurrency-patterns\|Concurrency Patterns]] |
| `crypto/*` | real cryptography; `crypto/rand` for anything security-relevant |
| `embed` | compile files into the binary — `//go:embed static/*` |
| `testing` | → [[languages/02-go/11-testing-and-benchmarking\|Testing]] |

`embed` deserves a mention: `//go:embed` bakes templates, migrations and static assets into the binary, so "one static file to deploy" stays true even for a web app.

---

## Related
- [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] — why `io.Reader` composes
- [[backend/frameworks/go/README|Go Backends]] — `net/http` in anger
- [[languages/02-go/12-modules-and-project-layout|Modules and Project Layout]] — adding the few dependencies you need
- [[languages/02-go/README|Go course map]]
