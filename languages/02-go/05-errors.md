# Errors

**[Intermediate]** — Errors as ordinary values, wrapping and unwrapping, when to use sentinel vs typed errors, and the narrow legitimate use of `panic`.

## `error` is just an interface

```go
type error interface {
    Error() string
}
```

That's the whole thing. There's no stack trace, no cause chain, no hierarchy — an error is any value that can describe itself as a string. Everything else is convention built on top.

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    return fmt.Errorf("computing ratio: %w", err)
}
```

## The `if err != nil` question

You will type this constantly, and it's the most-criticised thing about the language. The defence, honestly stated:

**For:** error handling is visible in the control flow. You can see every place a function can fail by reading it top to bottom. There is no invisible non-local jump, no "what does this throw" question, no catch block three frames up silently swallowing something.

**Against:** it's genuinely noisy, it triples the length of I/O-heavy functions, and the ceremony makes it *easier* to write `if err != nil { return err }` without thinking than to handle the error properly.

Both are true. What's not true is that it prevents mistakes — the common Go bug is bubbling an error up unchanged until it reaches a log line with no context about where it came from. Which is what wrapping is for.

## Wrapping — the thing to actually learn

```go
if err != nil {
    return fmt.Errorf("fetching user %d: %w", id, err)
}
```

**`%w` wraps** — it keeps the original error retrievable. `%v` only formats it as text and loses it. Use `%w` unless you deliberately want to hide the cause.

Wrapping at each layer builds a readable trail, which is Go's substitute for a stack trace:

```
handling POST /orders: creating order: fetching user 42: sql: no rows in result set
```

The convention: **each layer adds what it was doing, in lowercase, with no trailing punctuation**, because the messages concatenate. `fmt.Errorf("Failed to fetch user!: %w", err)` produces garbage when three layers do it.

### Unwrapping

```go
errors.Is(err, sql.ErrNoRows)     // is this error, or does it wrap this error?
errors.As(err, &myErr)            // is any error in the chain this TYPE? if so, assign it
errors.Unwrap(err)                // one level down; you rarely call this directly
```

**Never compare errors with `==`** — it fails the moment someone wraps. `errors.Is` walks the chain.

```go
// WRONG — breaks as soon as the caller wraps
if err == sql.ErrNoRows { ... }

// RIGHT
if errors.Is(err, sql.ErrNoRows) { ... }
```

## Sentinel errors vs typed errors

**Sentinel** — a package-level value, for conditions the caller only needs to identify:

```go
var ErrNotFound = errors.New("not found")

if errors.Is(err, ErrNotFound) {
    w.WriteHeader(http.StatusNotFound)
}
```

Declared with `Err` prefix by convention. Note that a sentinel is part of your package's public API — changing it breaks callers, so add them sparingly.

**Typed** — a struct, when the caller needs *data* from the error:

```go
type ValidationError struct {
    Field  string
    Reason string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Reason)
}

var vErr *ValidationError
if errors.As(err, &vErr) {
    respond(400, map[string]string{vErr.Field: vErr.Reason})
}
```

`errors.As` takes a **pointer to the target variable**, which is why the argument is `&vErr` and not `vErr`. Getting this wrong is a runtime panic, not a compile error.

To make a custom type wrap another, give it an `Unwrap() error` method — then `errors.Is`/`As` traverse through it.

### Mapping errors to HTTP status

The pattern that connects this to [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]] — done by hand in Go, where Spring uses `@ControllerAdvice` and Nest uses exception filters:

```go
func statusFor(err error) int {
    switch {
    case errors.Is(err, ErrNotFound):     return http.StatusNotFound
    case errors.Is(err, ErrUnauthorized): return http.StatusUnauthorized
    default:
        var vErr *ValidationError
        if errors.As(err, &vErr) { return http.StatusBadRequest }
        return http.StatusInternalServerError
    }
}
```

One function, in one place, that every handler routes through. Writing this by hand is more code than an annotation — and it's also the only version where you can read what happens without knowing framework internals.

## `panic` and `recover`

`panic` unwinds the stack running deferred functions, then crashes the program. `recover` stops the unwinding, and only works inside a `defer`.

```go
defer func() {
    if r := recover(); r != nil {
        log.Printf("recovered: %v", r)
    }
}()
```

**Panic for programmer errors, not for expected failures.** A nil map write, an index out of range, an impossible switch branch — those are bugs, and crashing loudly at the point of the bug is correct. A missing file, a failed network call, invalid user input: those are ordinary conditions and they return errors.

The one place `recover` genuinely belongs is a **server boundary**: one panicking request handler should return 500, not take the whole process down with it.

```go
func Recoverer(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                log.Printf("panic: %v\n%s", rec, debug.Stack())
                http.Error(w, "internal error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

`net/http` actually does this per-connection already, but a middleware that logs the stack and returns a clean response is standard.

**`recover` only catches panics in the same goroutine.** A panic in a goroutine you spawned kills the process regardless of any recover in the parent — one of the sharper consequences of Go's concurrency model. → [[languages/02-go/06-goroutines-and-channels|Goroutines and Channels]]

`must`-style helpers are the accepted exception at init time, where a failure means the program can't run anyway:

```go
var tmpl = template.Must(template.ParseFiles("index.html"))
```

---

## Related
- [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] — the nil-interface trap, which shows up as a phantom error
- [[languages/02-go/08-context|Context]] — `context.Canceled` and `DeadlineExceeded` as sentinels
- [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]] — where error→status mapping belongs
- [[languages/01-java/01-language/06-exceptions|Java: Exceptions]] — checked exceptions, the road not taken
- [[languages/02-go/README|Go course map]]
