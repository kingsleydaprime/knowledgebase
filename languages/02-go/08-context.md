---
id: 8021335e-58cb-4e50-9fab-d09818ee6608
---

# Context

## The problem it solves
<!-- bite: b2e1bdd9-912a-4c74-a824-abb5e561009c -->

A request arrives. Your handler calls a service, which calls a database and two HTTP APIs, each on its own goroutine. The client disconnects after 200ms.

Without a mechanism to say "stop, nobody wants this any more", every one of those goroutines runs to completion, holding a database connection and burning CPU for a response nobody will read. Under load that's how a service falls over: not from the work it's doing, but from work it should have abandoned.

`context.Context` is that mechanism — **cancellation and deadlines propagated across API boundaries and goroutines.**

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}      // closed when cancelled
    Err() error                 // why it was cancelled
    Value(key any) any
}
```

The whole design rests on `Done()` being a channel you can `select` on — which is why it composes with everything in [[languages/02-go/06-goroutines-and-channels|goroutines and channels]].

## Creating contexts
<!-- bite: de4c14ac-6ff3-432b-993c-7763bd8fda54 -->

```go
ctx := context.Background()   // the root; use in main, init, tests
ctx := context.TODO()         // "I haven't worked out the plumbing yet"

ctx, cancel := context.WithCancel(parent)
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
ctx, cancel := context.WithDeadline(parent, someTime)
defer cancel()                // ALWAYS — even on the success path
```

> **`defer cancel()` is not optional.** Skipping it leaks the context and its timer until the parent is cancelled. `go vet` flags the obvious cases; it can't catch all of them.

Contexts form a **tree**. Cancelling a parent cancels every descendant, which is exactly the propagation you want: the request context is cancelled, and every database call and outbound request beneath it stops.

## Consuming a context
<!-- bite: ada76570-1d03-4725-86fb-9f4a7e6d2e17 -->

```go
func work(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()          // context.Canceled or DeadlineExceeded
        case job := <-jobs:
            process(job)
        }
    }
}
```

For long CPU-bound loops with nothing to select on, poll:

```go
for i, item := range items {
    if i%1000 == 0 {
        if err := ctx.Err(); err != nil { return err }
    }
    process(item)
}
```

`ctx.Err()` returns `nil` while live, then `context.Canceled` or `context.DeadlineExceeded`. Both are sentinels — check with `errors.Is`, since callers will have wrapped them. → [[languages/02-go/05-errors|Errors]]

## The rules
<!-- bite: b96434a6-c0a9-4094-8e2c-ddcddd38631c -->

**1. `ctx` is the first parameter, always named `ctx`.**

```go
func GetUser(ctx context.Context, id int) (*User, error)
```

Not the second, not in an options struct. This is enforced by convention so strongly that violating it reads as a mistake.

**2. Never store a context in a struct.** It belongs to a call, not to an object. The one accepted exception is a struct that *is* a request, and even then it's frowned on.

**3. Never pass a nil context.** Use `context.TODO()` if you genuinely don't have one yet — it's greppable, which is the point.

**4. The caller owns cancellation.** A function that receives a context should not cancel it.

**5. Contexts are immutable.** `WithValue`/`WithTimeout` return *new* contexts; the parent is unchanged.

## `context.Value` — the part to be careful with
<!-- bite: 90bf3e0b-ac12-45a6-a44b-889562622f98 -->

```go
type ctxKey struct{}                            // unexported type — collision-proof

ctx = context.WithValue(ctx, ctxKey{}, traceID)
traceID, ok := ctx.Value(ctxKey{}).(string)
```

Never use a bare string as a key — two packages using `"user"` will silently clobber each other. An unexported struct type is unique by construction.

The real rule:

> **Context values are for request-scoped data that crosses API boundaries — not for passing arguments.**

Legitimate: trace/correlation IDs, authenticated user identity, request-scoped loggers. Illegitimate: anything a function actually needs to do its job. If a function can't work without a value, it should be a parameter — the type system should enforce it, not a runtime lookup returning `any`.

The smell to watch for is a handler pulling five values out of the context and a `nil` panic when one is missing. Values are untyped and unchecked; every one you add is a runtime failure you moved out of the compiler's reach.

## In the standard library
<!-- bite: e9932e1c-10c0-4e68-b509-fa86ea9f3253 -->

Context is wired through everything that does I/O:

```go
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := http.DefaultClient.Do(req)     // aborts if ctx is cancelled

rows, err := db.QueryContext(ctx, "SELECT ...")   // cancels the query
tx, err := db.BeginTx(ctx, nil)
```

Server-side, `net/http` gives you a context already cancelled when the client disconnects:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()      // cancelled on client disconnect
    user, err := svc.GetUser(ctx, id)
    ...
}
```

**Pass that context all the way down.** A `db.Query` without the request context is a query that keeps running after the client has gone — the exact failure this whole mechanism exists to prevent. Any `QueryContext`-shaped function called with `context.Background()` deep in a request path is a bug.

## Timeouts stack
<!-- bite: 50a05a1b-150c-46a0-abaa-28986f88360e -->

```go
ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
defer cancel()
```

The derived context fires at whichever comes first: the 3-second timeout, or the client disconnecting. Deriving a shorter timeout for a specific downstream call is how you stop one slow dependency consuming the whole request budget — the deadline-propagation idea from [[backend/interview/01-production-debugging|production debugging]], made concrete by the language.

Go's context is unusually good at this compared to most ecosystems, where cancellation is bolted on per-library if it exists at all. It's a real argument for Go in service code.

---

## Related
<!-- bite: 89f4bfb2-bf2a-42da-87e6-bbf4925ca811 -->
- [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]] — `errgroup.WithContext`
- [[languages/02-go/06-goroutines-and-channels|Goroutines and Channels]] — the `Done()` channel
- [[backend/frameworks/go/index|Go Backends]] — context through a real HTTP stack
- [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience Patterns]] — timeouts and deadlines as a design concern
- [[languages/02-go/index|Go course map]]

## About this lesson
<!-- bite: fb258c95-5e3f-43e0-9139-8c19ba6f4c44 -->

**Level:** Intermediate. **Covers:** The type threaded through every function in real Go code, why it exists, and the rules that stop it becoming a junk drawer.
