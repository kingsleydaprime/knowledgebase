---
id: 09c568b8-97d5-4326-81e8-10f4b2b497b0
---

# Errors and Structured Responses

**A structured response means every answer your API gives has the same, predictable shape: successes look one way, errors look another, and every error says what went wrong in words a program can check and a person can read.** In Go, errors are ordinary values that functions return. That makes one design possible that's hard in other languages: handlers **return** their errors, and a single function decides how every error looks on the wire.

## Before you start
<!-- bite: f5e70236-7914-4191-b109-4d6a0d46ad58 -->

You should have:

1. Finished [[backend/frameworks/net-http/06-validation|lesson 6]], so every body goes through `httpx.Decode` and every ID through `httpx.PathID`.
2. Read [[languages/02-go/05-errors|Errors]] in the Go course, or be ready to. This lesson uses wrapping, `errors.Is` and `errors.As` a lot.

After this lesson you will be able to:

1. Wrap and unwrap errors, and say why `errors.Is` looks inside.
2. Give the app one error type that says what **kind** of thing went wrong, without knowing anything about HTTP.
3. Write handlers that return errors, and turn every error into a problem-details response in one place.
4. Give every request an ID that's in the response, the error and the log.
5. Wrap every success in the same `{ "data": ... }` envelope.

## Where we stopped
<!-- bite: 5077dee3-6ee3-4eb0-ab62-1cf0ba0b54e0 -->

Mama Put API answers in four different shapes: bare JSON for success, `{"error", "fields"}` for bad input, plain text from `http.Error` for "not found", and the mux's own `404 page not found` for unknown routes. Each package has its own `writeError` with its own `switch`. And every handler repeats:

```go
if err != nil {
	writeError(w, err)
	return
}
```

When a customer rings to say "the app said something went wrong", you have nothing to search your logs for.

## The kid version
<!-- bite: 7f4ada1f-e900-41d5-824d-1721e2f21443 -->

When something goes wrong at Mama's stand, she doesn't explain it a new way each time. She has three or four set answers: "that one has finished", "we're closed, come back at 7", "you can't order fifty plates". Her son knows them by heart, so whoever asks gets the same clear answer.

And every order slip gets a number written on it. When a customer comes back angry about "my order", Mama asks "what's your number?" and finds the slip at once.

**Where the picture stops working.** Mama only tells the customer what they need to know. She'd never say "the gas cylinder exploded and my son is in hospital". Your API must be the same: some errors (a database crash) are none of the client's business. They get a polite "something went wrong on our side, here's your number", and the full story goes in your log.

## Terms used in this lesson
<!-- bite: b32b4125-fa66-4dce-bcf4-68a85c2de276 -->

1. **Error value**: In Go, an error is a value of the built-in `error` interface, which has one method, `Error() string`. Functions return it; nothing is thrown.
2. **Wrapping**: This means making a new error that adds context ("place order: ...") and keeps the original inside it, so code higher up can still find the original.
3. **Error kind**: This is a small, fixed list of what can go wrong (not found, invalid, conflict, a broken rule) that the service uses to describe an error, without saying anything about HTTP.
4. **Problem details**: This is a standard JSON shape for HTTP API errors, from RFC 9457. It has a `type`, `title`, `status` and `detail`, and you can add your own fields. Its content type is `application/problem+json`.
5. **Envelope**: This is a wrapper object around every successful answer, like `{ "data": ... }`, so there's always room to add `meta` (page numbers, for example) without changing the shape.
6. **Request ID**: This is a unique label given to each request. It's sent back in a header and included in errors and logs, so one request can be followed everywhere.
7. **Context**: This is the `context.Context` every request carries (`r.Context()`). It can hold values for the request, like its ID, and it's cancelled when the client goes away.

## Step 1: wrapping, and why `errors.Is` looks inside
<!-- bite: fc0bf7b9-5f89-467d-84bc-0bae37e658eb -->

You met `fmt.Errorf("...: %w", err)` in lesson 5. Here's why it matters. Suppose `orders.Service.Place` adds context to an error before returning it:

```go
dish, err := s.dishes.Get(in.DishID)
if err != nil {
	return Order{}, fmt.Errorf("place order for dish %s: %w", in.DishID, err)
}
```

The error that comes out now has the message `place order for dish 7: dish not found`, which is much better in a log. But it's a **new** error value, so `err == menu.ErrDishNotFound` is false. That's why Go has `errors.Is`: it checks the error, then the error it wraps, then the one *that* wraps, all the way down. `%w` is what makes the chain. (`%v` would copy the message and break the chain.)

`errors.As` walks the same chain, looking for an error of a given **type**. That's what the rest of this lesson builds on: wherever an error comes from, and however many layers wrap it, one function at the top can find out what it really is.

## Step 2: one error type for the whole app
<!-- bite: 360fbcca-b030-4338-a1b3-6a7867431dd1 -->

Every feature has been inventing its own errors, and every `writeError` has its own idea of which status goes with which. Let's give the whole app one error type. Make a new package, `internal/apperr/apperr.go`:

```go
package apperr

import "strings"

type Kind int

const (
	Internal Kind = iota
	Invalid
	Unauthenticated
	Forbidden
	NotFound
	Conflict
	RuleBroken
	TooManyRequests
)

type FieldError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

type Error struct {
	Kind    Kind
	Code    string       // short and stable, for programs: "dish-not-found"
	Message string       // for people: "That dish isn't on the menu."
	Fields  []FieldError // for Invalid: which fields, and why
	Err     error        // what caused it, if anything; logged, never sent
}

func (e *Error) Error() string {
	if e.Err != nil {
		return e.Message + ": " + e.Err.Error()
	}
	return e.Message
}

func (e *Error) Unwrap() error { return e.Err }

func New(kind Kind, code, message string) *Error {
	return &Error{Kind: kind, Code: code, Message: message}
}

func InvalidFields(fields []FieldError) *Error {
	return &Error{Kind: Invalid, Code: "invalid-fields", Message: "Some fields are not valid.", Fields: fields}
}

// Title turns "dish-not-found" into "Dish not found".
func (e *Error) Title() string {
	t := strings.ReplaceAll(e.Code, "-", " ")
	if t == "" {
		return "Error"
	}
	return strings.ToUpper(t[:1]) + t[1:]
}
```

Look at what's in it and what isn't.

**A `Kind`, not a status code.** The service says "this was not found" or "this broke a rule". It never says 404 or 422. Remember from lesson 4: services don't know HTTP exists. The same error might come out of a background job, where there's no status at all. Only the HTTP layer turns a kind into a number.

**A `Code` for programs, a `Message` for people.** The phone app checks `code == "shop-closed"` to show a "come back at 7" screen. It must never parse the message, because you'll want to reword messages, and translate them one day. The code is a promise; the message isn't.

**`Err` and `Unwrap`.** If the error was caused by something else (a database error, for example), it's kept inside. `Unwrap` lets `errors.Is` and `errors.As` see it. It's logged and **never** sent to the client.

**`iota`** numbers the constants for you: `Internal` is 0, `Invalid` is 1, and so on. `Internal` is first on purpose, so a `Kind` someone forgot to set is treated as our fault, not the client's.

Now the features use it. In `internal/menu/menu.go`, replace the two sentinels:

```go
var (
	ErrDishNotFound = apperr.New(apperr.NotFound, "dish-not-found", "That dish isn't on the menu.")
	ErrBadDish      = apperr.New(apperr.Invalid, "bad-dish", "A dish needs a name and a positive price.")
)
```

And in `internal/orders/orders.go`:

```go
var (
	ErrOrderNotFound   = apperr.New(apperr.NotFound, "order-not-found", "We can't find that order.")
	ErrBadQuantity     = apperr.New(apperr.Invalid, "bad-quantity", "You can order between 1 and 20 plates.")
	ErrDishUnavailable = apperr.New(apperr.RuleBroken, "dish-unavailable", "That dish has finished for today.")
	ErrShopClosed      = apperr.New(apperr.RuleBroken, "shop-closed", "Mama Put is closed. We open at 7am.")
	ErrBadStatusChange = apperr.New(apperr.Conflict, "bad-status-change", "An order can't go back to an earlier status.")
)
```

They're still sentinels: made once, shared, checked with `errors.Is`. Your tests from lesson 5 pass without a change. Run `go test ./...` to see.

## Step 3: request IDs
<!-- bite: f76b6e1d-99fe-498d-b904-596a080cc4e7 -->

Before the error responses, every request needs an ID, because every error response will include it.

The ID has to reach code deep inside the request (the error writer, the logger), without passing it as an argument through every function. That's what `context.Context` is for. Every request has one, `r.Context()`, and you can make a new context that carries one extra value. Make `internal/httpx/requestid.go`:

```go
package httpx

import (
	"context"
	"crypto/rand"
	"net/http"
	"regexp"
)

type ctxKey int

const requestIDKey ctxKey = 0

var safeID = regexp.MustCompile(`^[A-Za-z0-9_-]{1,64}$`)

func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := r.Header.Get("X-Request-ID")
		if !safeID.MatchString(id) {
			id = rand.Text()
		}
		w.Header().Set("X-Request-ID", id)
		ctx := context.WithValue(r.Context(), requestIDKey, id)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func RequestIDFrom(ctx context.Context) string {
	id, _ := ctx.Value(requestIDKey).(string)
	return id
}
```

What each part does:

1. **It keeps an ID the caller sent, if it's safe.** When the phone app or another service already has an ID for this request, using it means one ID follows the request across every system (lesson 27 builds on this). "Safe" means short and plain: a client could otherwise send a 10 MB header, or text with newlines that forges extra lines in your logs.
2. **Otherwise it makes one.** `crypto/rand.Text()` gives 26 random characters, like `GQ7XKZ5V2M4NA6PBRWH3JCTYDE`. Random enough that two requests never share one.
3. **It sends it back** in the `X-Request-ID` response header, so the client can show it or log it.
4. **It puts it in the context**, under a key whose type is `ctxKey`, which is unexported. No other package can make a key of that type, so no other package can accidentally overwrite or read our value except through `RequestIDFrom`. Always use your own unexported key type for context values.

`r.WithContext(ctx)` makes a copy of the request with the new context, and that's what goes down the chain.

Now the logger. It'd be useful if every log line written during a request already included the request ID, without each caller adding it. Change `LogRequests` in `middleware.go` so it builds a logger for this request and puts it in the context too:

```go
const loggerKey ctxKey = 1

func LoggerFrom(ctx context.Context) *slog.Logger {
	if l, ok := ctx.Value(loggerKey).(*slog.Logger); ok {
		return l
	}
	return slog.Default()
}

func LogRequests(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			reqLogger := logger.With("requestId", RequestIDFrom(r.Context()))
			ctx := context.WithValue(r.Context(), loggerKey, reqLogger)
			rec := &statusRecorder{ResponseWriter: w, status: http.StatusOK}

			next.ServeHTTP(rec, r.WithContext(ctx))

			reqLogger.Info("request",
				"method", r.Method,
				"path", r.URL.Path,
				"status", rec.status,
				"duration", time.Since(start),
			)
		})
	}
}
```

`logger.With("requestId", ...)` makes a new logger that adds that field to every line it writes. Anything during the request that calls `httpx.LoggerFrom(r.Context())` gets it. `RequestID` must run **before** `LogRequests`, so the ID is there when the logger is made; we'll fix the order in the chain in step 6.

Change `RecoverPanic` too: it no longer needs its own logger, because it can use `LoggerFrom(r.Context())`. You'll rewrite its body in step 5.

## Step 4: the problem-details response
<!-- bite: be368d22-8db5-4040-813e-a7d65049035a -->

Here's the shape every error will have. A missing dish:

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
X-Request-ID: GQ7XKZ5V2M4NA6PBRWH3JCTYDE

{
  "type": "https://mamaput.example/problems/dish-not-found",
  "title": "Dish not found",
  "status": 404,
  "detail": "That dish isn't on the menu.",
  "code": "dish-not-found",
  "requestId": "GQ7XKZ5V2M4NA6PBRWH3JCTYDE"
}
```

The first four fields come from the standard, RFC 9457. `type` is a URL naming this kind of problem (it can point at a page explaining it, though it doesn't have to), `title` is a short summary that's the same every time, `status` repeats the HTTP status, and `detail` explains this case. We add `code`, the short form for programs, `requestId`, and for bad input, `errors`, the list of fields.

Using a standard shape means client developers, and the tools they use, may already know how to read it. Make `internal/httpx/errors.go`:

```go
package httpx

import (
	"encoding/json"
	"errors"
	"net/http"

	"mamaput/internal/apperr"
)

const problemsBase = "https://mamaput.example/problems/"

type problem struct {
	Type      string              `json:"type"`
	Title     string              `json:"title"`
	Status    int                 `json:"status"`
	Detail    string              `json:"detail"`
	Code      string              `json:"code"`
	RequestID string              `json:"requestId"`
	Errors    []apperr.FieldError `json:"errors,omitempty"`
}

var statusFor = map[apperr.Kind]int{
	apperr.Internal:        http.StatusInternalServerError,
	apperr.Invalid:         http.StatusBadRequest,
	apperr.Unauthenticated: http.StatusUnauthorized,
	apperr.Forbidden:       http.StatusForbidden,
	apperr.NotFound:        http.StatusNotFound,
	apperr.Conflict:        http.StatusConflict,
	apperr.RuleBroken:      http.StatusUnprocessableEntity,
	apperr.TooManyRequests: http.StatusTooManyRequests,
}

// WriteError is the one place an error becomes an HTTP response.
func WriteError(w http.ResponseWriter, r *http.Request, err error) {
	var appErr *apperr.Error
	if !errors.As(err, &appErr) || appErr.Kind == apperr.Internal {
		LoggerFrom(r.Context()).Error("unexpected error", "error", err)
		appErr = apperr.New(apperr.Internal, "internal", "Something went wrong on our side. Quote the request ID if you contact us.")
	} else if appErr.Err != nil {
		LoggerFrom(r.Context()).Warn("request failed", "code", appErr.Code, "error", err)
	}

	status := statusFor[appErr.Kind]
	body, _ := json.Marshal(problem{
		Type:      problemsBase + appErr.Code,
		Title:     appErr.Title(),
		Status:    status,
		Detail:    appErr.Message,
		Code:      appErr.Code,
		RequestID: RequestIDFrom(r.Context()),
		Errors:    appErr.Fields,
	})

	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(status)
	w.Write(body)
}
```

Read the first `if` carefully, because it's the most important security line in the lesson. If the error is **not** an `*apperr.Error` (a database error, a nil map, anything nobody planned for), or it's one marked `Internal`, the client gets a generic message and nothing else. The real error, with everything in it, goes to the log, under the request ID. An error message from a database can contain table names, column names, even customer data. It must never reach the client.

When it **is** an `*apperr.Error`, the client gets its kind, code and message, all written on purpose for them to see. If it was caused by something (`appErr.Err`), that cause is logged as a warning, and still never sent.

## Step 5: handlers that return errors
<!-- bite: 01526845-e41a-46c3-aaf5-ae6d35686f96 -->

Now the part that tidies every handler. Add to `internal/httpx/errors.go`:

```go
// HandlerFunc is a handler that returns an error instead of writing it.
type HandlerFunc func(w http.ResponseWriter, r *http.Request) error

func (f HandlerFunc) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if err := f(w, r); err != nil {
		WriteError(w, r, err)
	}
}
```

It's the same trick as `http.HandlerFunc` from lesson 1: a function type with a `ServeHTTP` method, so it **is** an `http.Handler`. The difference is the function returns an `error`, and `ServeHTTP` sends any error it returns to `WriteError`. The mux, the middleware and everything else just see a normal handler.

And the success side. Replace `WriteJSON` in `json.go` with:

```go
type envelope struct {
	Data any `json:"data"`
	Meta any `json:"meta,omitempty"`
}

func WriteData(w http.ResponseWriter, status int, data any) error {
	body, err := json.Marshal(envelope{Data: data})
	if err != nil {
		return fmt.Errorf("encode response: %w", err)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	w.Write(body)
	return nil
}
```

Notice it encodes into memory first (`json.Marshal`), **then** writes. Lesson 1's `json.NewEncoder(w).Encode` wrote straight down the pipe, so if encoding failed halfway, a 200 and half a body had already gone. Now an encoding failure is an error returned before anything is sent, and it becomes a proper 500.

Change `Decode` and `PathID` in `json.go` to return `apperr` errors: `apperr.New(apperr.Invalid, "bad-json", describeJSONError(err))` for decoding, `apperr.InvalidFields(fields)` for the validator, and `apperr.New(apperr.Invalid, "bad-id", name+" must be a positive whole number.")` for IDs. Then delete `InputError`, `WriteInputError` and both packages' `writeError` functions. You won't need them again.

Here's the menu handler file now, `internal/menu/handlers.go`:

```go
func (h *Handler) Register(mux *http.ServeMux, staff func(http.Handler) http.Handler) {
	mux.Handle("GET /menu", httpx.HandlerFunc(h.list))
	mux.Handle("GET /menu/specials", httpx.HandlerFunc(h.specials))
	mux.Handle("GET /menu/{id}", httpx.HandlerFunc(h.get))
	mux.Handle("POST /menu", staff(httpx.HandlerFunc(h.add)))
	mux.Handle("PATCH /menu/{id}", staff(httpx.HandlerFunc(h.change)))
	mux.Handle("DELETE /menu/{id}", staff(httpx.HandlerFunc(h.remove)))
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) error {
	onlyAvailable, err := httpx.QueryBool(r, "available")
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, h.svc.List(onlyAvailable))
}

func (h *Handler) specials(w http.ResponseWriter, r *http.Request) error {
	return httpx.WriteData(w, http.StatusOK, h.svc.Specials())
}

func (h *Handler) get(w http.ResponseWriter, r *http.Request) error {
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	dish, err := h.svc.Get(id)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, dish)
}

func (h *Handler) add(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[NewDish](w, r)
	if err != nil {
		return err
	}
	dish, err := h.svc.Add(in)
	if err != nil {
		return err
	}
	w.Header().Set("Location", "/menu/"+dish.ID)
	return httpx.WriteData(w, http.StatusCreated, dish)
}

func (h *Handler) change(w http.ResponseWriter, r *http.Request) error {
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	in, err := httpx.Decode[DishChanges](w, r)
	if err != nil {
		return err
	}
	dish, err := h.svc.Change(id, in)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, dish)
}

func (h *Handler) remove(w http.ResponseWriter, r *http.Request) error {
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	if err := h.svc.Remove(id); err != nil {
		return err
	}
	w.WriteHeader(http.StatusNoContent)
	return nil
}
```

Every handler is now the same pattern: get something or `return err`, call the service or `return err`, write the answer. No status picking for errors, no `writeError`, no forgotten `return` after writing an error (the old lesson 2 bug), because returning **is** how you report the error. That's about a third of the lines gone.

A `DELETE` returns 204 with no body, so it doesn't use the envelope. "Every success is `{ data }`" really means every success that has a body.

The orders handlers change the same way. Write them yourself; the pattern is identical.

`KitchenOnly` should use the same shape. Change its failure branch to:

```go
WriteError(w, r, apperr.New(apperr.Unauthenticated, "staff-key-required", "Kitchen staff only. Send your staff key in X-Staff-Key."))
return
```

And `RecoverPanic`'s deferred function, after the `http.ErrAbortHandler` check, becomes:

```go
LoggerFrom(r.Context()).Error("panic", "error", err, "stack", string(debug.Stack()))
w.Header().Set("Connection", "close")
WriteError(w, r, apperr.New(apperr.Internal, "internal", "Something went wrong on our side."))
```

Passing an `Internal` error means `WriteError` sends the generic message. The panic itself is already logged, with its stack.

## Step 6: the mux's own 404 and 405
<!-- bite: 16dd821f-7114-49e1-927a-0560b09fec2b -->

One shape left to fix. For an unknown path, the mux writes `404 page not found` as plain text, and for a wrong method, `Method Not Allowed`. The standard mux has no setting to change those. (There's a long-running proposal to add one.) So we catch them on the way out: a small wrapper that notices the mux starting a plain-text 404 or 405, and writes a problem instead.

Add to `internal/httpx/errors.go`:

```go
// MuxProblems turns the mux's own plain-text 404 and 405 answers into problems.
func MuxProblems(mux *http.ServeMux) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if _, pattern := mux.Handler(r); pattern != "" {
			mux.ServeHTTP(w, r) // a route matched: nothing to fix
			return
		}
		mux.ServeHTTP(&muxErrorCatcher{ResponseWriter: w, r: r}, r)
	})
}

type muxErrorCatcher struct {
	http.ResponseWriter
	r       *http.Request
	replied bool
}

func (c *muxErrorCatcher) WriteHeader(status int) {
	switch status {
	case http.StatusNotFound:
		WriteError(c.ResponseWriter, c.r, apperr.New(apperr.NotFound, "route-not-found", "There's nothing at this address."))
	case http.StatusMethodNotAllowed:
		c.ResponseWriter.Header().Del("Content-Type")
		c.writeProblem405()
	default:
		c.ResponseWriter.WriteHeader(status)
		return
	}
	c.replied = true
}

func (c *muxErrorCatcher) Write(b []byte) (int, error) {
	if c.replied {
		return len(b), nil // throw away the mux's plain text
	}
	return c.ResponseWriter.Write(b)
}

func (c *muxErrorCatcher) writeProblem405() {
	body, _ := json.Marshal(problem{
		Type: problemsBase + "method-not-allowed", Title: "Method not allowed",
		Status: http.StatusMethodNotAllowed, Code: "method-not-allowed",
		Detail:    "This address doesn't accept " + c.r.Method + ". See the Allow header.",
		RequestID: RequestIDFrom(c.r.Context()),
	})
	c.ResponseWriter.Header().Set("Content-Type", "application/problem+json")
	c.ResponseWriter.WriteHeader(http.StatusMethodNotAllowed)
	c.ResponseWriter.Write(body)
}
```

`mux.Handler(r)` asks the mux "which pattern would you use for this request?" without running anything. If a pattern matches, the request goes straight through, untouched. Only when no pattern matches (which is exactly when the mux will write its own 404 or 405) do we wrap the writer. The `Allow` header the mux sets for a 405 is kept, so clients still learn which methods work.

It's more code than one would like for something so small. It's also written once, tested once (that's in the practice), and every app on `net/http` that wants consistent errors has a version of it.

Now the chain in `internal/app/app.go`:

```go
return httpx.Chain(httpx.MuxProblems(mux),
	httpx.RequestID,
	httpx.LogRequests(d.Logger),
	httpx.RecoverPanic,
)
```

`RequestID` is outermost, so the ID exists before the logger is made. `LogRequests` next, so it sees everything. `RecoverPanic` inside it, protecting the rest. `RecoverPanic` no longer takes a logger, so it's passed as it is, without brackets.

## Trying it
<!-- bite: 31b1d9d8-35ab-4caf-b1c1-375fd51757f9 -->

```bash
STAFF_KEY=mama-secret go run -race ./cmd/api
```

```bash
curl -s localhost:8080/menu/2
# {"data":{"id":"2","name":"Beans and plantain","priceNaira":1200,"available":true,"special":false}}

curl -si localhost:8080/menu/99
# HTTP/1.1 404 Not Found
# Content-Type: application/problem+json
# X-Request-Id: 7ZK3...
# {"type":"https://mamaput.example/problems/dish-not-found","title":"Dish not found","status":404,
#  "detail":"That dish isn't on the menu.","code":"dish-not-found","requestId":"7ZK3..."}

curl -s localhost:8080/suya
# {"type":".../problems/route-not-found","title":"Route not found","status":404,...}

curl -si -X PUT localhost:8080/menu
# HTTP/1.1 405 Method Not Allowed
# Allow: GET, HEAD, POST
# {"type":".../problems/method-not-allowed",...}

curl -s -H "X-Request-ID: from-the-app-123" localhost:8080/menu/abc
# {"type":".../problems/bad-id",...,"requestId":"from-the-app-123"}
```

And in the server's log, each line has its `requestId`, matching what the client saw. Ask the customer for their number, `grep` the log for it, and you have the whole story.

## The Go in this lesson
<!-- bite: fe28a062-a1d0-42ed-811c-454c8d20a5d7 -->

1. **`fmt.Errorf("place order for dish %s: %w", id, err)`**: `%w` wraps `err`, so the new error remembers it. Only `%w` does this; `%v` and `%s` just copy the text.
2. **`func (e *Error) Unwrap() error`**: The method `errors.Is` and `errors.As` call to look inside an error. Your own error types should have it whenever they hold a cause.
3. **`type Kind int` with `const ( Internal Kind = iota; Invalid; ... )`**: `iota` counts up from 0 inside a `const` block. Each line without a value repeats the previous one's type and expression, with `iota` one higher. It's Go's way of making an enum.
4. **`t[:1]` and `t[1:]`**: **Slicing** a string: the part from the start up to (not including) index 1, and the part from index 1 to the end. Fine here because codes are plain ASCII letters.
5. **`type ctxKey int` and `const requestIDKey ctxKey = 0`**: A private type for context keys. Two values are only equal if their types are too, so no other package's key can ever clash with ours.
6. **`context.WithValue(r.Context(), key, value)`** and **`r.WithContext(ctx)`**: The first returns a new context with one extra value; contexts never change, you only make new ones. The second returns a copy of the request using it.
7. **`id, _ := ctx.Value(requestIDKey).(string)`**: `ctx.Value` returns `any`. The `.(string)` is a **type assertion**: "I expect this to be a string". With two results, it never panics: if it isn't a string (or the value is missing), `id` is `""`.
8. **`regexp.MustCompile(...)`**: Compiles a regular expression. `Must` means it panics if the pattern is broken, which is fine at start-up for a pattern written in the code.
9. **`rand.Text()`**: From `crypto/rand` (new in Go 1.24). Returns a random string, safe to use for IDs and even secrets.
10. **`logger.With("requestId", id)`**: Returns a new `*slog.Logger` that adds those fields to every line. The original logger is unchanged.
11. **`map[apperr.Kind]int{ ... }`**: A map from kinds to status codes. A kind missing from the map would give 0, which is why `Internal` is the zero value and always listed.
12. **`json.Marshal(v)`**: Encodes `v` into a `[]byte` in memory, returning an error if it can't, without writing anything anywhere.
13. **`type HandlerFunc func(w, r) error` with a `ServeHTTP` method**: A function type that satisfies `http.Handler`. The same idea as the standard `http.HandlerFunc`, with one extra return value.
14. **`if _, pattern := mux.Handler(r); pattern != ""`**: `mux.Handler` returns the handler and the pattern it would use. An empty pattern means no route matched.
15. **`httpx.RecoverPanic` with no brackets**: Passing the function itself as a value, because it already has the shape `func(http.Handler) http.Handler`. `LogRequests(d.Logger)` has brackets because it's a function that *makes* a middleware.

## Your project so far
<!-- bite: 9fa5ae2b-6427-4cd6-bbc7-2d13b579840e -->

```text
mama-put/
├── .gitignore
├── go.mod
├── go.sum
├── cmd/
│   └── api/
│       └── main.go
└── internal/
    ├── apperr/
    │   └── apperr.go            ← NEW: Kind, Error (Code, Message, Fields, Err), New, InvalidFields, Title
    ├── app/
    │   └── app.go               ← chain: RequestID, LogRequests, RecoverPanic, MuxProblems(mux)
    ├── httpx/
    │   ├── errors.go            ← NEW: problem, statusFor, WriteError, HandlerFunc, MuxProblems
    │   ├── json.go              ← WriteData (the envelope), Decode[T], PathID, QueryBool → apperr errors
    │   ├── middleware.go        ← LogRequests puts a request logger in the context; LoggerFrom
    │   └── requestid.go         ← NEW: RequestID middleware, RequestIDFrom
    ├── menu/
    │   ├── menu.go              ← sentinels are now *apperr.Error
    │   ├── store.go
    │   ├── service.go
    │   ├── service_test.go
    │   └── handlers.go          ← every handler returns an error; no writeError
    └── orders/
        ├── orders.go            ← sentinels are now *apperr.Error
        ├── store.go
        ├── service.go
        ├── service_test.go      ← unchanged, still passes
        └── handlers.go          ← the same pattern
```

## Common mistakes
<!-- bite: 1f15afcd-4fe2-493d-99d5-d810f50d6af9 -->

1. **Sending `err.Error()` for unexpected errors.** Database and library errors can hold table names, file paths, even data. Unknown errors get the generic message; the real one goes to the log.
2. **Status codes in services.** Services return kinds. Only `WriteError` knows numbers.
3. **Clients reading `detail`.** Messages change. Programs check `code`.
4. **`%v` instead of `%w`.** The chain breaks, and `errors.Is` stops finding your sentinel.
5. **A plain `string` as a context key.** Another package using `"requestId"` would clash. Use your own unexported key type.
6. **Trusting the incoming `X-Request-ID` blindly.** Limit its length and characters, or it becomes a way to forge log lines.
7. **Writing the body with an encoder straight onto `w`.** An encoding failure halfway leaves a 200 and broken JSON. Marshal first, then write.
8. **Mixing shapes.** One route returning a bare array breaks every client expecting `{ "data" }`.

## Check your understanding
<!-- bite: 0a11e6a6-f3c9-4aec-be93-4318752d3370 -->

1. `orders.Service.Place` returns `fmt.Errorf("place order: %w", menu.ErrDishNotFound)`. What status and `code` does the client get, and how does `WriteError` find them?
2. The memory store is swapped for a database, the database goes down, and `menu.Service.List` returns a connection error. What does the client see? What do you see?
3. Why does `apperr.Error` have a `Kind` and not a `Status int`?
4. A handler returns `nil` without writing anything. What does the client get?

<details>
<summary>Answers, after your attempt</summary>

1. A 404 with `code: "dish-not-found"`. `errors.As(err, &appErr)` walks the chain: the outer error from `fmt.Errorf` wraps `menu.ErrDishNotFound`, which is an `*apperr.Error` of kind `NotFound`. `statusFor` turns that into 404.
2. The client sees a 500 problem with the generic "Something went wrong on our side" message and a request ID. You see a log line `unexpected error` with the full connection error and the same request ID, because the error wasn't an `*apperr.Error`.
3. Because services return these errors, and services don't know about HTTP. The same error could come out of a background job, a gRPC call or a command-line tool, each with its own way of saying "not found". Only the HTTP layer turns a kind into a status.
4. An empty 200, because the server sends a 200 for any handler that returns without writing. It's a bug in the handler. A test for every route (lesson 16) catches it.

</details>

## Practice
<!-- bite: 03e2748f-33ac-435c-b611-2b8e3d66cd52 -->

1. Make `PATCH /orders/{id}/status` return the order with `{ "data" }`, and a 409 problem with `code: "bad-status-change"` when it would go backwards. Check both with `curl -i`.
2. Make `orders.Service.Place` wrap every error it passes up with `fmt.Errorf("place order: %w", err)`. Run `go test ./...`. Do the lesson 5 tests still pass? Why?
3. Write `internal/httpx/errors_test.go`. Build an `http.ServeMux` with one route, wrap it in `MuxProblems`, and use `httptest` to check: an unknown path gives a 404 problem, a wrong method gives a 405 problem with an `Allow` header, and the real route is untouched.

**Done when** every response from Mama Put API is either `{ "data": ... }`, a 204 with no body, or a problem with `application/problem+json`, every one has an `X-Request-ID` header, and the lesson 5 tests still pass.

## Before moving on
<!-- bite: fd4d20e9-489e-4320-a5bb-83279e06d7f3 -->

Every answer now has one of two shapes: data in an envelope, or a problem with a kind, a code, a message and a request ID. Handlers return errors, and one function turns them into responses, never leaking what the client shouldn't see. Every log line during a request carries its ID.

But stop the server and start it again. Mama's moi moi is gone. Every order is gone. Everything lives in memory, so every restart, every deploy, every crash wipes the shop. And two copies of the server behind a load balancer would each have their own menu. Mama Put API needs a real database. That's the next lesson, and it's also where the last-plate problem shows up: two customers ordering the final plate of jollof at the same moment.

## Related
<!-- bite: bb42693a-9ef8-4787-84fa-d7fcca71d0e4 -->

- [[backend/frameworks/net-http/08-data-with-postgres|Next: Data with PostgreSQL]]
- [[backend/06-cross-cutting/03-error-handling|Error Handling]] — the idea across languages
- [[languages/02-go/05-errors|Errors]] — wrapping, `errors.Is` and `errors.As` in the Go course
- [[languages/02-go/08-context|Context]] — what else a context carries
- [[backend/frameworks/express/07-errors|The same lesson in Express]] — a thrown `AppError` and an error-handling middleware

## About this lesson
<!-- bite: 35fbb1c4-6742-4de0-b7f4-9c508c6419b9 -->

**Level:** Intermediate. Lesson 7 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`crypto/rand.Text` needs 1.24).
