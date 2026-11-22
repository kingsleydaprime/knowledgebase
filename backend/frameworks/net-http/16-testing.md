---
id: 9fe8536c-8183-43af-af21-92bc5e1725d5
---

# Testing

**A test is a small program that runs a piece of your real program and checks it did the right thing, so that a computer, not you, re-checks every rule each time anything changes.** Go has testing built in: a `testing` package, a `go test` command, and `net/http/httptest` for sending requests to your handlers without a network. No framework to choose, nothing to install.

## Before you start
<!-- bite: cb37cee3-8f3e-42cf-bef7-2ee55c851371 -->

You should have:

1. Finished [[backend/frameworks/net-http/15-idempotency|lesson 15]]: the whole of Parts 1 to 3.
2. Written the first table-driven tests in [[backend/frameworks/net-http/05-wiring-dependencies|lesson 5]] and the contract test in [[backend/frameworks/net-http/11-api-docs|lesson 11]].

After this lesson you will be able to:

1. Choose which kind of test catches which kind of bug, and how many of each to write.
2. Use `go test`'s tools: subtests, `t.Helper`, `t.Cleanup`, `t.Context`, `t.Parallel`, `-race`, `-run`, `-shuffle` and coverage.
3. Test business rules with small fakes, and the whole HTTP app in memory with `httptest`.
4. Test permissions as a table, and run integration tests against a real Postgres behind a build tag.
5. Keep fakes honest with one set of store tests run against both the fake and the real store.

## Where we stopped
<!-- bite: aae42229-c739-41b7-a994-ad19d4ff721c -->

Count the `curl` checks from the last fifteen lessons: wrong passwords, refresh token reuse, Ada reading Bayo's order, the last plate, twenty orders for one key, too-big photos, deprecated v1 headers, CORS preflights. Easily a hundred.

Tomorrow you change one line in the auth service. Which of those hundred checks might it break? You don't know, so either you run them all by hand (you won't), or you ship and hope. Tests end that choice.

## The kid version
<!-- bite: 0d5ceb7e-a0ce-4785-a2d7-582f99a50820 -->

Before Mama Put opens each morning, Mama tastes every pot. Not a whole plate, just a spoon from each. If the stew is too salty, she finds out now, not from a customer at lunch.

Tests are those spoons. A quick taste of every important thing, every time anything changes, before customers find the problem.

**Where the picture stops working.** Mama tastes what she cooked today. Tests also taste what you cooked *last month*: every old bug you fixed gets a test, so it can never quietly come back.

## Terms used in this lesson
<!-- bite: 90a49d16-2b0c-4ffb-aa70-02f676988d93 -->

1. **Unit test**: This tests one small piece, like the orders service, on its own, with fakes standing in for what it depends on. It runs in microseconds.
2. **HTTP test**: This sends real requests through the whole app (routing, middleware, validation, errors) but with in-memory stores. `httptest` hands each request straight to the handler, with no port.
3. **Integration test**: This tests our code together with a real outside system, here a real Postgres database.
4. **Contract test**: This checks that what we send matches what we promised: our responses against our OpenAPI spec.
5. **Fake**: This is a small, simple, working version of a dependency, like a store that keeps things in a map. Go programmers prefer fakes to **mocks**, which are objects programmed with "expect this call, return that".
6. **Fixture**: This is the data a test starts from, like "a dish with 1 portion left and a customer called Ada".
7. **Subtest**: This is a named test inside a test, made with `t.Run`. Each row of a table test is one.
8. **Build tag**: This is a line at the top of a Go file, like `//go:build integration`, that leaves the file out of the build unless you ask for that tag.
9. **Flaky test**: This is a test that sometimes passes and sometimes fails with no code change. Flaky tests are worse than no tests, because people learn to ignore failures.

## Step 1: which tests, how many
<!-- bite: 3d016564-c2b7-4764-9958-44ca45cb3b6a -->

Different tests catch different bugs, at different costs:

| Kind | Example | Speed | Catches |
|---|---|---|---|
| Unit | "21 plates is `bad-quantity`" | microseconds | wrong business rules |
| HTTP | "`POST /v2/orders` without a token is 401, as a problem" | under a millisecond | wrong routes, guards, middleware order, status codes, shapes |
| Contract | "every dish in `GET /v2/menu` matches the spec" | a millisecond | docs and code drifting apart |
| Integration | "20 parallel orders for 5 portions give exactly 5" | tens of milliseconds | wrong SQL, missing constraints, races |

Write **many** unit and HTTP tests, because they're fast and point straight at the problem. Write **fewer** integration tests, for the things only a real database can show: SQL, constraints, transactions and races. That's the usual shape, sometimes drawn as a pyramid: lots at the bottom, fewer at the top.

## Step 2: what `go test` gives you
<!-- bite: e660436d-1ea2-40b9-8107-15281fc6833e -->

You've already used the basics: a file ending in `_test.go`, a function `func TestSomething(t *testing.T)`, and `go test ./...`. Here's the rest of the toolbox, all built in:

1. **`t.Run(name, func(t *testing.T) {...})`**: A subtest. Each row of a table gets a name, its own pass or fail, and can be run alone with `go test -run 'TestPlace/too_many'`. (Spaces in names become `_`.)
2. **`t.Helper()`**: Put it first in a helper function. When the helper calls `t.Fatal`, the error points at the **test's** line, not the helper's, which is the line you want.
3. **`t.Cleanup(func() {...})`**: Runs when the test ends, pass or fail. For closing things, emptying tables, removing files.
4. **`t.Context()`** (Go 1.24): A context that's cancelled when the test ends. Pass it to anything that takes a `ctx`, instead of `context.Background()`, so nothing a test starts outlives it.
5. **`t.TempDir()`**: A fresh empty folder, deleted after the test. Lesson 14's photos need one.
6. **`t.Parallel()`**: Lets this test run at the same time as other parallel tests in the package. Only for tests that share nothing.
7. **`go test -race ./...`**: The race detector from lesson 2, now on every run. A data race in a test is a data race in production.
8. **`go test -shuffle=on ./...`**: Runs tests in a random order, and prints the seed it used. A test that only passes after another one has run is caught.
9. **`go test -count=1 ./...`**: Go caches passing test results and skips packages that haven't changed. `-count=1` forces a real run.
10. **`go test -cover ./...`**: Shows the share of lines each package's tests ran. Step 9 says what to do with it.

Two kinds of test file:

1. **`package orders`** in `service_test.go`: the test is inside the package, and can see unexported names. Good for testing small internal pieces.
2. **`package orders_test`**: the test is outside, and sees only what's exported, like any other user of the package. Good for testing the package's real promises, and it's the only way some tests can import packages that themselves import `orders` without an import cycle.

The `Makefile` gets two targets:

```makefile
test:
	go test -race -shuffle=on ./...

test-integration:
	go test -race -p 1 -tags integration ./...
```

`make test` runs everything that needs nothing running. `make test-integration` adds the database tests; step 7 explains `-p 1` and `-tags`.

## Step 3: unit tests for the rules
<!-- bite: e8f2f046-fa09-420a-8e12-ce9b70776e90 -->

You wrote the first ones in lesson 5, and lesson 8's practice gave the orders service a `fakeStore`. Here's the place rule tested properly, as one table, in `internal/orders/service_test.go`:

```go
func TestPlace(t *testing.T) {
	ada := int64(1)
	tests := []struct {
		name    string
		hour    int
		in      NewOrder
		store   error // what the fake store should fail with, if anything
		want    money.Kobo
		wantErr error
	}{
		{name: "charges price times quantity", hour: 12, in: NewOrder{DishID: 2, Quantity: 3}, want: 360000},
		{name: "before opening", hour: 6, in: NewOrder{DishID: 2, Quantity: 1}, wantErr: ErrShopClosed},
		{name: "after closing", hour: 21, in: NewOrder{DishID: 2, Quantity: 1}, wantErr: ErrShopClosed},
		{name: "too many plates", hour: 12, in: NewOrder{DishID: 2, Quantity: 21}, wantErr: ErrBadQuantity},
		{name: "a finished dish", hour: 12, in: NewOrder{DishID: 9, Quantity: 1}, wantErr: ErrDishUnavailable},
		{name: "no such dish", hour: 12, in: NewOrder{DishID: 404, Quantity: 1}, wantErr: menu.ErrDishNotFound},
		{name: "the store runs out", hour: 12, in: NewOrder{DishID: 2, Quantity: 1},
			store: ErrNotEnoughPortions, wantErr: ErrNotEnoughPortions},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			svc, err := NewService(&fakeStore{fail: tt.store}, testMenu, clockAt(tt.hour))
			if err != nil {
				t.Fatal(err)
			}

			order, err := svc.Place(t.Context(), &ada, tt.in)

			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("error = %v, want %v", err, tt.wantErr)
			}
			if err == nil && order.Total != tt.want {
				t.Errorf("total = %d, want %d", order.Total, tt.want)
			}
		})
	}
}
```

Look at the shape every row has:

(`fakeStore` from lesson 8's practice gets one more field, `fail error`: when it's set, `PlaceTakingPortions` returns it, so a row can make the store run out.)

1. **Arrange**: a fresh service, fake store and clock for **every** row. Nothing one row does can leak into the next. Tests that depend on each other's leftovers are the biggest cause of flaky tests.
2. **Act**: one call, `svc.Place(...)`.
3. **Assert**: `errors.Is(err, tt.wantErr)` works for both kinds of row. When `wantErr` is `nil`, `errors.Is(err, nil)` is true only if `err` is `nil` too. When it's a sentinel, it's true if `err` is that error, or wraps it.

The names read as the rules: "charges price times quantity", "too many plates". A failing row tells you which rule broke, in words:

```text
--- FAIL: TestPlace/after_closing
    service_test.go:41: error = <nil>, want the shop is closed; Mama Put opens at 7am
```

Notice what's being tested: **behaviour**. "Placing 21 plates is refused." Not "the service called `Get` once and then `PlaceTakingPortions` once". The first survives every tidy-up of the code; the second breaks every time, while the behaviour stays the same. That's why Go programmers prefer fakes to mocks: a fake *does* the job in a simple way, so the test can only check what came out.

## Step 4: the whole app, in memory
<!-- bite: fcfb5e2c-5569-4146-9151-d468063f6796 -->

Unit tests can't see mistakes like "`Authenticate` is outside `RequestID` in the chain" or "`POST /v2/orders` forgot `RequireUser`". For that, send real requests through the real app.

This is what lesson 5's `app.New(Deps)` was for. A test can build the whole app, exactly as `run` does, with in-memory pieces instead of Postgres. Lesson 11's contract test did it once, in a test file. Now it gets a package of its own, so every test in every package can use it: `internal/apptest`.

`internal/apptest/apptest.go`:

```go
// Package apptest builds the whole app with in-memory stores, for tests.
// Only _test.go files may import it.
package apptest

import (
	"bytes"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"mamaput/internal/app"
	"mamaput/internal/auth"
	"mamaput/internal/httpx"
	"mamaput/internal/menu"
	"mamaput/internal/orders"
)

type App struct {
	Handler http.Handler
	Tokens  *auth.Tokens
	Users   *MemoryUsers
	Clock   *Clock
}

// Clock is a clock the test moves by hand.
type Clock struct {
	mu  sync.Mutex
	now time.Time
}

func (c *Clock) Now() time.Time { c.mu.Lock(); defer c.mu.Unlock(); return c.now }

func (c *Clock) Advance(d time.Duration) { c.mu.Lock(); defer c.mu.Unlock(); c.now = c.now.Add(d) }

// New builds the app. The clock starts at 1pm in Lagos, when the shop is open.
func New(t *testing.T) *App {
	t.Helper()
	clock := &Clock{now: time.Date(2026, 11, 23, 12, 0, 0, 0, time.UTC)}
	must := func(err error) {
		t.Helper()
		if err != nil {
			t.Fatal(err)
		}
	}

	tokens, err := auth.NewTokens("test-secret-that-is-long-enough-for-hs256", clock.Now)
	must(err)
	users := NewMemoryUsers()
	authSvc, err := auth.NewService(users, NewMemoryRefreshTokens(), tokens,
		auth.Argon2{Memory: 64, Time: 1, Threads: 1}, clock.Now)
	must(err)

	dishes := menu.NewMemoryStore(SeedDishes())
	menuSvc := menu.NewService(dishes)
	orderSvc, err := orders.NewService(NewMemoryOrders(dishes), menuSvc, clock.Now)
	must(err)
	photos, err := menu.OpenPhotos(t.TempDir())
	must(err)

	handler := app.New(app.Deps{
		Logger:       slog.New(slog.NewTextHandler(io.Discard, nil)),
		Menu:         menuSvc,
		Orders:       orderSvc,
		Auth:         authSvc,
		Tokens:       tokens,
		Photos:       photos,
		Idempotency:  NewMemoryIdempotency(),
		GeneralLimit: httpx.NewLimiters(10_000, time.Millisecond),
		ClientIP:     httpx.ClientIP(0),
		V1Policy:     httpx.DeprecationPolicy{ /* as in run, with Now: clock.Now */ },
	})
	return &App{Handler: handler, Tokens: tokens, Users: users, Clock: clock}
}

// Login makes a user with this role and signs a token for them, skipping /login.
func (a *App) Login(t *testing.T, role auth.Role) string {
	t.Helper()
	u := a.Users.Add(role)
	tok, err := a.Tokens.Sign(auth.Identity{UserID: u.ID, Role: role})
	if err != nil {
		t.Fatal(err)
	}
	return tok
}

type Option func(*http.Request)

func Token(tok string) Option { return func(r *http.Request) { r.Header.Set("Authorization", "Bearer "+tok) } }
func Key(key string) Option   { return func(r *http.Request) { r.Header.Set("Idempotency-Key", key) } }

// Do sends one request through the app. body may be nil, a string (sent as-is) or anything to encode.
func (a *App) Do(t *testing.T, method, path string, body any, opts ...Option) *httptest.ResponseRecorder {
	t.Helper()
	var r io.Reader
	switch b := body.(type) {
	case nil:
	case string:
		r = strings.NewReader(b)
	default:
		data, err := json.Marshal(b)
		if err != nil {
			t.Fatal(err)
		}
		r = bytes.NewReader(data)
	}
	req := httptest.NewRequest(method, path, r)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	for _, opt := range opts {
		opt(req)
	}
	rec := httptest.NewRecorder()
	a.Handler.ServeHTTP(rec, req)
	return rec
}

// Decode reads a JSON response body into T, or fails the test.
func Decode[T any](t *testing.T, rec *httptest.ResponseRecorder) T {
	t.Helper()
	var v T
	if err := json.Unmarshal(rec.Body.Bytes(), &v); err != nil {
		t.Fatalf("decode %q: %v", rec.Body.String(), err)
	}
	return v
}

type Problem struct {
	Status int    `json:"status"`
	Code   string `json:"code"`
	Errors []struct {
		Field string `json:"field"`
	} `json:"errors"`
}
```

Three shortcuts make these tests fast and focused:

1. **A real argon2, made cheap.** `Argon2{Memory: 64, Time: 1, Threads: 1}` is the same code as production, with 64 KiB instead of 19 MiB. Each hash takes microseconds instead of tens of milliseconds, and nothing about *how* passwords are checked changes. No fake hasher needed.
2. **`Login` signs a token directly**, instead of going through `/v2/auth/login`. The auth routes have their own tests; every other test just needs "a logged-in customer".
3. **A clock the test controls.** `a.Clock.Advance(16 * time.Minute)` makes every token signed so far expire, with no waiting. And the tests pass at 3am, which is when the shop would be closed for real.

`apptest` is a normal package, not a `_test.go` file, so any package's tests can import it. That also means production code *could* import it by mistake, and then fake stores would be in the real program. Check it never happens:

```bash
go list -deps ./cmd/api | grep apptest
```

It should print nothing. Lesson 29 puts that line in CI.

The in-memory stores live in `apptest` too: `MemoryUsers`, `MemoryRefreshTokens`, `MemoryOrders` and `MemoryIdempotency`. Each is a map behind a mutex, satisfying the store interface from its package. Here's one, `internal/apptest/users.go`:

```go
type MemoryUsers struct {
	mu    sync.Mutex
	users map[int64]auth.User
	next  int64
}

func NewMemoryUsers() *MemoryUsers { return &MemoryUsers{users: map[int64]auth.User{}} }

func (m *MemoryUsers) Create(ctx context.Context, email, name, hash string) (auth.User, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	for _, u := range m.users {
		if strings.EqualFold(u.Email, email) {
			return auth.User{}, auth.ErrEmailTaken
		}
	}
	m.next++
	u := auth.User{ID: m.next, Email: email, Name: name, PasswordHash: hash, Role: auth.RoleCustomer}
	m.users[u.ID] = u
	return u, nil
}

// Add makes a user with a role, for Login.
func (m *MemoryUsers) Add(role auth.Role) auth.User {
	u, _ := m.Create(context.Background(), fmt.Sprintf("%s-%d@test.example", role, m.next+1), string(role), "x")
	m.mu.Lock()
	defer m.mu.Unlock()
	u.Role = role
	m.users[u.ID] = u
	return u
}

// FindByEmail, Find and SetRole follow the same pattern.
```

Notice the fake keeps the **rules** the real store has: `ErrEmailTaken` for an email that differs only in case, just as the `lower(email)` index does. A fake that's more forgiving than the real thing lets tests pass that production would fail. Step 8 makes sure they stay the same.

Now, real requests. `internal/orders/handlers_test.go`, in `package orders_test`:

```go
package orders_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"mamaput/internal/apptest"
	"mamaput/internal/auth"
)

func TestPlaceNeedsALogin(t *testing.T) {
	a := apptest.New(t)
	rec := a.Do(t, "POST", "/v2/orders", map[string]any{"dishId": "1", "quantity": 1},
		apptest.Key("test-key-0001"))

	if rec.Code != http.StatusUnauthorized {
		t.Fatalf("status = %d, want 401", rec.Code)
	}
	if got := rec.Header().Get("Content-Type"); got != "application/problem+json" {
		t.Errorf("Content-Type = %q", got)
	}
	if rec.Header().Get("WWW-Authenticate") == "" {
		t.Error("no WWW-Authenticate header")
	}
	if p := apptest.Decode[apptest.Problem](t, rec); p.Code != "login-required" {
		t.Errorf("code = %q, want login-required", p.Code)
	}
}

func TestPlaceIsReplayedForTheSameKey(t *testing.T) {
	a := apptest.New(t)
	tok := a.Login(t, auth.RoleCustomer)
	send := func() *httptest.ResponseRecorder {
		return a.Do(t, "POST", "/v2/orders", map[string]any{"dishId": "1", "quantity": 2},
			apptest.Token(tok), apptest.Key("test-key-0002"))
	}
	type placed struct {
		Data struct {
			ID string `json:"id"`
		} `json:"data"`
	}

	first, second := send(), send()

	if first.Code != 201 || second.Code != 201 {
		t.Fatalf("statuses = %d, %d, want 201, 201", first.Code, second.Code)
	}
	if second.Header().Get("Idempotent-Replayed") != "true" {
		t.Error("second answer was not a replay")
	}
	if x, y := apptest.Decode[placed](t, first), apptest.Decode[placed](t, second); x.Data.ID != y.Data.ID {
		t.Errorf("order IDs %s and %s, want the same", x.Data.ID, y.Data.ID)
	}
}

func TestPlaceListsEveryProblem(t *testing.T) {
	a := apptest.New(t)
	tok := a.Login(t, auth.RoleCustomer)
	rec := a.Do(t, "POST", "/v2/orders", `{"quantity":"two"}`, apptest.Token(tok), apptest.Key("test-key-0003"))

	p := apptest.Decode[apptest.Problem](t, rec)
	if rec.Code != 400 || p.Code != "invalid-fields" {
		t.Fatalf("got %d %s, want 400 invalid-fields", rec.Code, p.Code)
	}
}
```

`a.Do` hands each request straight to the app's `ServeHTTP`. Nothing listens on a port, so tests never fight over port 8080, and every test gets its own app, its own stores and its own clock, so they can run in parallel safely. `httptest.NewRecorder` collects what the app wrote; `rec.Code`, `rec.Header()` and `rec.Body` are what a client would have received.

(The third test sends a **string**, `{"quantity":"two"}`, so it can send JSON that no Go struct would produce. Testing bad input means sending bad input.)

When you need a real network, say to test code that *calls* an HTTP API, `httptest.NewServer(handler)` starts a real server on a random free port and gives you its URL. Lesson 17 uses it to stand in for Paystack.

## Step 5: a table of permissions
<!-- bite: deacc1a4-c41b-4841-997a-23b3324c2e0f -->

Authorization has many combinations (three roles, many routes) and it's easy to get one corner wrong. Write them as a table, and let one loop test them all. `internal/app/permissions_test.go`:

```go
package app_test

import (
	"testing"

	"mamaput/internal/apptest"
	"mamaput/internal/auth"
)

func TestPermissions(t *testing.T) {
	newDish := map[string]any{"name": "Puff puff", "price": map[string]any{"amount": 20000, "currency": "NGN"}}
	tests := []struct {
		role   auth.Role
		method string
		path   string
		body   any
		want   int
	}{
		{auth.RoleCustomer, "POST", "/v2/menu", newDish, 403},
		{auth.RoleStaff, "POST", "/v2/menu", newDish, 201},
		{auth.RoleCustomer, "DELETE", "/v2/menu/1", nil, 403},
		{auth.RoleStaff, "DELETE", "/v2/menu/1", nil, 204},
		{auth.RoleCustomer, "PATCH", "/v2/orders/1/status", map[string]any{"status": "ready"}, 403},
		{auth.RoleStaff, "PATCH", "/v2/orders/1/status", map[string]any{"status": "ready"}, 200},
		{auth.RoleCustomer, "GET", "/v2/orders/1", nil, 404}, // somebody else's order
		{auth.RoleStaff, "GET", "/v2/orders/1", nil, 200},
		{auth.RoleStaff, "PATCH", "/v2/admin/users/1/role", map[string]any{"role": "staff"}, 403},
		{auth.RoleAdmin, "PATCH", "/v2/admin/users/1/role", map[string]any{"role": "staff"}, 200},
	}
	for _, tt := range tests {
		t.Run(string(tt.role)+" "+tt.method+" "+tt.path, func(t *testing.T) {
			t.Parallel()
			a := apptest.New(t)
			a.PlaceOrder(t) // order 1, belonging to its own customer (user 1)

			rec := a.Do(t, tt.method, tt.path, tt.body, apptest.Token(a.Login(t, tt.role)))

			if rec.Code != tt.want {
				t.Errorf("status = %d, want %d: %s", rec.Code, tt.want, rec.Body.String())
			}
		})
	}
}
```

Each row becomes its own subtest, with a readable name like `customer_DELETE_/v2/menu/1`. The table *is* the policy from lesson 13, checked against the running app, routes, guards and services all together. Add a route, add a row.

`t.Parallel()` lets the rows run at the same time. That's safe because each builds its own `apptest.New(t)` and shares nothing. (`a.PlaceOrder` is a small helper: log in a customer and place an order for them. Write it in `apptest`.) The body is a sensible valid one for each route, so the test checks **permission**, not validation.

Lesson 11's contract test moves here too. Its `newTestApp(t)` becomes `apptest.New(t).Handler`, and it now runs with logins, so add authorised requests to its list: `POST /v2/orders` as a customer, `PATCH /v2/orders/1/status` as staff, and the 401, 403 and 404 problems. The spec documents errors; the test checks them.

## Step 6: testing a middleware on its own
<!-- bite: 69e35f7d-a865-4424-acaf-5495d7e9be02 -->

Some middleware is easier to test alone than through the whole app. Lesson 14's `ClientIP` is pure logic; a table says it all:

```go
func TestClientIP(t *testing.T) {
	tests := []struct {
		name   string
		hops   int
		remote string
		xff    string
		want   string
	}{
		{"no proxy", 0, "203.0.113.7:5000", "", "203.0.113.7"},
		{"no proxy ignores the header", 0, "203.0.113.7:5000", "6.6.6.6", "203.0.113.7"},
		{"one proxy takes the last", 1, "10.0.0.1:5000", "6.6.6.6, 203.0.113.7", "203.0.113.7"},
		{"IPv6 grouped by /64", 0, "[2001:db8:1:2:3:4:5:6]:443", "", "2001:db8:1:2::/64"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := httptest.NewRequest("GET", "/", nil)
			r.RemoteAddr = tt.remote
			if tt.xff != "" {
				r.Header.Set("X-Forwarded-For", tt.xff)
			}
			if got := ClientIP(tt.hops)(r); got != tt.want {
				t.Errorf("ClientIP = %q, want %q", got, tt.want)
			}
		})
	}
}
```

The second row is the one that matters most: it's the attack. A test for a security rule should always include the attempt to break it.

For middleware that wraps a handler, give it a tiny handler that records whether it ran:

```go
func TestCORSAnswersPreflightsItself(t *testing.T) {
	reached := false
	next := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { reached = true })
	h := CORS(CORSPolicy{Origins: []string{"https://kitchen.mamaput.example"}})(next)

	r := httptest.NewRequest("OPTIONS", "/v2/orders", nil)
	r.Header.Set("Origin", "https://kitchen.mamaput.example")
	r.Header.Set("Access-Control-Request-Method", "POST")
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, r)

	if rec.Code != 204 || reached {
		t.Fatalf("status %d, reached the mux: %v; want 204 and false", rec.Code, reached)
	}
	if rec.Header().Get("Access-Control-Allow-Origin") != "https://kitchen.mamaput.example" {
		t.Error("allowed origin not echoed")
	}
}
```

## Step 7: integration tests on a real database
<!-- bite: 638ea3ab-80c7-4dc3-a7ab-52f606c631c1 -->

Some bugs only exist in SQL: a typo in a column name, a missing constraint, a race. For those, nothing replaces a real Postgres.

**A separate database**, so tests can't touch your development data:

```bash
docker exec -it mama-put-db createdb -U postgres mama_put_test
```

In `.env`:

```text
TEST_DATABASE_URL=postgres://postgres:mamaput@localhost:5432/mama_put_test
```

**A helper that refuses the wrong database.** `internal/dbtest/dbtest.go`:

```go
//go:build integration

// Package dbtest gives integration tests a clean, migrated test database.
package dbtest

import (
	"context"
	"net/url"
	"os"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"

	"mamaput/internal/db"
	"mamaput/migrations"
)

func Open(t *testing.T) *pgxpool.Pool {
	t.Helper()
	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("TEST_DATABASE_URL is not set")
	}
	u, err := url.Parse(dsn)
	if err != nil || !strings.HasSuffix(u.Path, "_test") {
		t.Fatalf("TEST_DATABASE_URL must name a database ending in _test, got %q", u.Path)
	}

	pool, err := db.Open(t.Context(), dsn)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(pool.Close)
	if err := db.Migrate(t.Context(), pool, migrations.FS); err != nil {
		t.Fatal(err)
	}

	_, err = pool.Exec(t.Context(), `TRUNCATE idempotency_keys, refresh_tokens, orders, users, dishes
		RESTART IDENTITY CASCADE`)
	if err != nil {
		t.Fatal(err)
	}
	return pool
}
```

Read it from the top:

1. **`//go:build integration`**: a build tag. This file, and every test file with the same line, is left out unless you run `go test -tags integration`. So `make test` never needs a database, and `make test-integration` adds these.
2. **`t.Skip`** if there's no test database at all: the test is reported as skipped, not failed, so a teammate without Docker still gets a clean `make test-integration` with a clear note.
3. **The name check.** `TRUNCATE` empties tables. Pointed at your real database by a typo in `.env`, that's every customer and every order gone. So the helper refuses to run unless the database's name ends in `_test`. Five lines that stop a disaster.
4. **`TRUNCATE ... RESTART IDENTITY CASCADE`** empties the tables and resets IDs to 1, so every test starts from the same clean state.
5. **`t.Cleanup(pool.Close)`** closes the pool when the test ends, whatever happens.

**Why `-p 1`?** `go test ./...` normally tests several **packages at once**, each in its own process. Two packages' integration tests would then `TRUNCATE` the same database at the same time, and wipe each other's data mid-test: the flakiest kind of failure. `-p 1` runs one package at a time. (Bigger projects give each package its own database, or each test its own schema, so they can run in parallel. Start simple.)

Now the test that matters most, the last plate from lesson 8, in `internal/orders/postgres_test.go`:

```go
//go:build integration

package orders_test

import (
	"errors"
	"fmt"
	"sync"
	"testing"

	"mamaput/internal/dbtest"
	"mamaput/internal/orders"
)

func TestTwentyCustomersRaceForFivePortions(t *testing.T) {
	pool := dbtest.Open(t)
	ctx := t.Context()
	_, err := pool.Exec(ctx, `
		INSERT INTO dishes (name, price_kobo, available, portions_left) VALUES ('Jollof rice', 150000, true, 5);
		INSERT INTO users (email, name, password_hash) VALUES ('ada@test.example', 'Ada', 'x');`)
	if err != nil {
		t.Fatal(err)
	}
	store := orders.NewPostgresStore(pool)
	ada := int64(1)

	var wg sync.WaitGroup
	results := make(chan error, 20)
	for i := range 20 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, err := store.PlaceTakingPortions(ctx, &ada, orders.NewOrder{
				DishID: 1, Quantity: 1, IdempotencyKey: fmt.Sprintf("race-%02d", i),
			})
			results <- err
		}()
	}
	wg.Wait()
	close(results)

	placed, refused := 0, 0
	for err := range results {
		switch {
		case err == nil:
			placed++
		case errors.Is(err, orders.ErrNotEnoughPortions):
			refused++
		default:
			t.Errorf("unexpected error: %v", err)
		}
	}
	if placed != 5 || refused != 15 {
		t.Errorf("placed %d, refused %d; want 5 and 15", placed, refused)
	}

	var left int
	if err := pool.QueryRow(ctx, "SELECT portions_left FROM dishes WHERE id = 1").Scan(&left); err != nil {
		t.Fatal(err)
	}
	if left != 0 {
		t.Errorf("portions left = %d, want 0", left)
	}
}
```

Twenty goroutines start at once, each with its own connection from the pool, so they really do race inside Postgres. The channel collects every answer; `wg.Wait()` waits for all twenty; `close(results)` lets the `range` loop end. If anyone ever "simplifies" `PlaceTakingPortions` into "read the portions, check them in Go, then update", this test fails. That's what tests are for: they remember *why* the code looks the way it does, long after everyone has forgotten.

Write the same kind of test for the idempotency layer from lesson 15: twenty goroutines, **one** key, and exactly one row in `orders` afterwards.

```bash
make test-integration
```

## Step 8: one set of tests for the fake and the real store
<!-- bite: bb5b8382-ab93-48fa-a714-ba027a90c148 -->

The HTTP tests trust `apptest`'s memory stores to behave like the Postgres ones. If the fake accepts something the database refuses (an email that differs only in case, a status that skips a step), tests pass that production fails. So write the store's promises down **once**, and run them against both.

`internal/auth/authtest/users.go`:

```go
// Package authtest holds tests every auth.Users store must pass.
package authtest

import (
	"errors"
	"testing"

	"mamaput/internal/auth"
)

// Users checks the promises of an auth.Users store. newStore must return an empty one.
func Users(t *testing.T, newStore func(t *testing.T) auth.Users) {
	t.Run("an email is taken whatever its case", func(t *testing.T) {
		s := newStore(t)
		if _, err := s.Create(t.Context(), "ada@example.com", "Ada", "h"); err != nil {
			t.Fatal(err)
		}
		_, err := s.Create(t.Context(), "ADA@example.com", "Ada again", "h")
		if !errors.Is(err, auth.ErrEmailTaken) {
			t.Errorf("error = %v, want ErrEmailTaken", err)
		}
	})
	t.Run("find by email ignores case", func(t *testing.T) {
		s := newStore(t)
		made, _ := s.Create(t.Context(), "bayo@example.com", "Bayo", "h")
		got, err := s.FindByEmail(t.Context(), "Bayo@Example.com")
		if err != nil || got.ID != made.ID {
			t.Errorf("got %v, %v; want user %d", got, err, made.ID)
		}
	})
	t.Run("a missing user is ErrUserNotFound", func(t *testing.T) {
		_, err := newStore(t).Find(t.Context(), 999)
		if !errors.Is(err, auth.ErrUserNotFound) {
			t.Errorf("error = %v, want ErrUserNotFound", err)
		}
	})
}
```

Then two tiny tests call it, one for each store. The Postgres one must be in `package auth_test`, the external test package: `authtest` imports `auth`, so a test *inside* `auth` importing `authtest` would be an import cycle.


```go
// internal/apptest/users_test.go
func TestMemoryUsers(t *testing.T) {
	authtest.Users(t, func(*testing.T) auth.Users { return apptest.NewMemoryUsers() })
}
```

```go
//go:build integration

// internal/auth/postgres_test.go
package auth_test

func TestPostgresUsers(t *testing.T) {
	authtest.Users(t, func(t *testing.T) auth.Users { return auth.NewPostgresUsers(dbtest.Open(t)) })
}
```

Now the fake and the real store are held to exactly the same promises. Change a rule in one, and the other's test fails until they agree again. Do the same for the menu, orders, refresh tokens and idempotency stores. These shared tests are sometimes called **store contract tests**: the contract between a store interface and everything that implements it.

## Step 9: what makes tests trustworthy
<!-- bite: 3052622c-cf73-412d-8211-a8348b8138c3 -->

1. **Independent.** Every test builds its own state. Run them in any order (`-shuffle=on`), or one alone (`-run`), and they pass the same.
2. **Deterministic.** No real clocks and no randomness you can't control. The clock is a dependency (lesson 5), so a test sets it. For code with real waiting in it, timers and tickers, Go 1.25's `testing/synctest` runs it on a fake clock that jumps ahead instantly.
3. **Testing behaviour, not wiring.** "21 plates is refused" survives a refactor. "The service called `Get` once" breaks every time you tidy the code.
4. **One reason to fail.** A test that checks ten things tells you less when it fails than ten small tests. Table rows give you that for free.
5. **The attack is a test case.** Every security rule gets a row that tries to break it: the faked `X-Forwarded-For`, the changed token, Bayo's order ID.
6. **A test for every bug.** When something breaks in production, first write the test that fails *because* of the bug, then fix it. That bug can never come back silently.
7. **`-race` always.** It's slower, and worth it. Lesson 29 runs it on every push.

How much is enough? Don't chase a coverage number. Look at what was never run:

```bash
go test -coverprofile=cover.out ./...
go tool cover -html=cover.out
```

The second command opens a page in your browser with every line coloured: green ran, red didn't. Look at the red and ask "is any of this a rule or a security check?". An untested error branch in `auth.Service.Refresh` matters far more than an untested log line. (Add `cover.out` to `.gitignore`.)

## The Go in this lesson
<!-- bite: f3f154d9-a278-4ece-821b-42eec3d540d6 -->

1. **`errors.Is(err, tt.wantErr)`** when `wantErr` may be `nil`: `errors.Is(nil, nil)` is true and `errors.Is(someErr, nil)` is false, so one line checks both "no error wanted" and "this error wanted".
2. **`t.Helper()`**: Marks a function as a helper, so failures inside it are reported at the caller's line.
3. **`t.Context()`** (Go 1.24): A context cancelled just before the test's cleanup runs.
4. **`t.Skip(reason)`**: Stops the test and reports it as skipped, not failed.
5. **`t.Parallel()`**: Pauses this test until the non-parallel ones are done, then runs it alongside the other parallel tests.
6. **`//go:build integration`**: A build constraint. It must be the first line, followed by a blank line. `go test -tags integration` includes the file.
7. **`package orders_test`**: An **external test package**, in the same folder. It can only use exported names, like a real caller.
8. **`body.(type)` in a `switch`**: A **type switch**: each `case` checks what type the `any` really holds, and inside the case `b` has that type.
9. **A function returning an `Option`** (`Token(tok)`, `Key(key)`): The functional-options pattern from lesson 12, used to keep `Do`'s signature short.
10. **`func Decode[T any](t *testing.T, rec ...) T`**: A generic test helper. `apptest.Decode[apptest.Problem](t, rec)` says which type to decode into.
11. **`for i := range 20`** (Go 1.22): Counts `i` from 0 to 19. Since Go 1.22, each turn of the loop has its own `i`, so each goroutine sees its own number.
12. **`sync.WaitGroup`** with **`Add`**, **`Done`** and **`Wait`**: Counts running goroutines; `Wait` blocks until the count is back to zero.
13. **A buffered channel, `make(chan error, 20)`**: Holds up to 20 values without anyone reading yet, so no goroutine blocks on sending. `close` then lets `range` finish.
14. **`go list -deps ./cmd/api`**: Lists every package the program is built from. A quick way to check what's really inside a binary.
15. **`go tool cover -html=cover.out`**: Shows a coverage profile as a coloured page of your code.

## Your project so far
<!-- bite: f123005a-013a-44d3-abf2-0cfce21814c9 -->

```text
mama-put/
├── Makefile                       ← test (-race -shuffle=on), test-integration (-p 1 -tags integration)
├── .env                           ← TEST_DATABASE_URL (a database ending in _test)
├── .gitignore                     ← cover.out
└── internal/
    ├── apptest/                   ← NEW: the whole app in memory, for tests only
    │   ├── apptest.go             ← New, Clock, Login, Do, Token, Key, Decode, Problem, PlaceOrder
    │   ├── users.go               ← MemoryUsers (and refresh tokens, orders, idempotency alongside)
    │   ├── seed.go                ← SeedDishes
    │   └── users_test.go          ← the memory stores pass the store contract tests
    ├── dbtest/
    │   └── dbtest.go              ← NEW (integration): Open refuses non-_test databases, migrates, truncates
    ├── app/
    │   ├── contract_test.go       ← uses apptest; logged-in requests and error responses added
    │   └── permissions_test.go    ← NEW: the policy as a table, through the real app
    ├── auth/
    │   ├── authtest/users.go      ← NEW: what every Users store must do
    │   ├── postgres_test.go       ← NEW (integration): Postgres users pass the same tests
    │   ├── password_test.go
    │   ├── policy_test.go
    │   └── tokens_test.go
    ├── httpx/
    │   ├── clientip_test.go       ← NEW: including the faked header
    │   └── cors_test.go           ← NEW: preflights never reach the mux
    ├── idempotency/
    │   └── middleware_test.go     ← from lesson 15's practice
    └── orders/
        ├── service_test.go        ← TestPlace as one table
        ├── handlers_test.go       ← NEW: 401 as a problem, replays, every field error
        └── postgres_test.go       ← NEW (integration): the twenty-customer race
```

## Common mistakes
<!-- bite: ac79f713-95cc-48f4-bfba-857449d9f777 -->

1. **Tests that share state.** One test's leftovers become the next one's surprise. Build everything fresh in each test.
2. **Mocks that check calls.** They break on every refactor and prove nothing about behaviour. Use fakes and check results.
3. **Fakes kinder than the real thing.** Then tests pass that production fails. Run the same store tests against both.
4. **`context.Background()` everywhere in tests.** Use `t.Context()`, so nothing a test starts outlives it.
5. **Integration tests against the development database.** `TRUNCATE` will find it one day. Refuse any database not named `_test`.
6. **Packages' integration tests running at once against one database.** Use `-p 1`, or separate databases.
7. **Forgetting `-race`.** The races that matter most only show up under it.
8. **No test for the attack.** A security rule is only tested when someone tries to break it in a test.
9. **Importing `apptest` from production code.** Check with `go list -deps`.
10. **Chasing 100% coverage.** Read the red lines and test the rules and checks among them.

## Check your understanding
<!-- bite: 7ff21df8-1ab3-4448-8330-8d2d6a50d945 -->

1. Which kind of test catches each of these: a `WHERE` clause missing `AND available`; `POST /v2/menu` forgetting its permission guard; v2's presenter leaving out `createdAt`; a wrong shop-closing hour?
2. Why does `apptest` use a real argon2 with tiny settings instead of a fake hasher?
3. Two packages' integration tests pass on their own and fail together. What's the likely cause, and the fix?
4. `MemoryUsers.Create` compares emails with `==`. Which test fails, and why does it matter even though production uses Postgres?
5. A test calls `time.Now()` to make an order "from 20 minutes ago". What's the problem, and what's the fix in this codebase?

<details>
<summary>Answers, after your attempt</summary>

1. The missing `AND available`: an integration test, because only a real database runs the SQL (the fake store has its own logic). The missing guard: an HTTP test, like the permissions table. The missing `createdAt`: a test that checks values, since the contract test only checks shapes and a zero time is still a valid date; an HTTP test that decodes the answer and checks the date isn't zero catches it. The wrong closing hour: a unit test of `Place`, with the clock set.
2. Because it tests the real code: the same hashing, the same PHC string, the same `Verify`. Only the cost changes. A fake hasher could hide a bug in the real one, and tests would never run the real one at all.
3. They `TRUNCATE` the same test database at the same time, because `go test ./...` runs packages in parallel. Run them with `-p 1`, or give each package its own database.
4. The store contract test "an email is taken whatever its case" fails for `MemoryUsers`. It matters because every HTTP test uses the fake: with it, a test could sign up `ADA@example.com` after `ada@example.com` and pass, while production refuses it. The tests would be describing an app that doesn't exist.
5. The test now depends on the real time: at 6am Lagos time the shop is closed and the test fails; around midnight the date changes. Use the app's `Clock`: set it, place the order, `Advance` it 20 minutes. Every test sees exactly the same times on every run.

</details>

## Practice
<!-- bite: cc5aa5e7-57fa-4382-a826-27d4c2fad773 -->

1. Write the rest of `apptest`'s memory stores (`MemoryRefreshTokens`, `MemoryOrders`, `MemoryIdempotency`) and `PlaceOrder`, then make `TestPermissions` pass.
2. Write `authtest.RefreshTokens`: `MarkUsed` is true only the first time; `RevokeAllForUser` revokes only that user's tokens. Run it against the memory and Postgres stores. Add a row that calls `MarkUsed` from 20 goroutines at once and checks exactly one gets `true`.
3. Test the refresh-token flow through the app: sign up, refresh, refresh again with the **old** token (401 `refresh-token-reused`), and check the new token is dead too. Then use `a.Clock.Advance(16 * time.Minute)` to check an access token expires.
4. Write the idempotency race test: twenty goroutines, one key, against Postgres. Exactly one row in `orders`.
5. Run `go test -coverprofile=cover.out ./... && go tool cover -html=cover.out`. Find one red line in `auth` or `orders` that's a rule or a check, and write the test that turns it green.

**Done when** `make test` and `make test-integration` both pass with `-race`, `-shuffle=on` passes three runs in a row, the permissions table covers every guarded route, and `go list -deps ./cmd/api | grep apptest` prints nothing.

## Before moving on
<!-- bite: fdd40c16-be77-4d9a-b0a6-89d416bc7285 -->

Mama Put API now checks itself. Rules are tested as tables, the whole app runs in memory in under a second, permissions are a table checked against real routes, the last-plate race runs against real Postgres, and the fakes are held to the same promises as the real stores. Change anything, run `make test`, and you know.

That's the end of Part 3: the API knows who's calling, what they may do, how to refuse attackers, how to survive retries, and how to prove all of it. Part 4 is what real products need next, and it starts with money: Mama wants customers to pay through Paystack, with webhooks telling us when a payment lands.

## Related
<!-- bite: 33538b00-6ac4-4655-9946-0c9488c39796 -->

- [[backend/frameworks/net-http/17-payments-and-webhooks|Next: Payments and Webhooks]]
- [[concepts/01-best-practices/03-testing-fundamentals/index|Testing Fundamentals]] — the ideas in any language
- [[languages/02-go/index|The Go course]] — the language, including its testing package
- [[backend/frameworks/express/16-testing|The same lesson in Express]] — `node:test` and supertest

## About this lesson
<!-- bite: a1a21d28-0ef8-4063-a363-f8c4e2979894 -->

**Level:** Intermediate → Advanced. Lesson 16 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`t.Context()`). Covers the kinds of tests and their costs, `go test`'s subtests, helpers, cleanup, parallelism, race detection, shuffling and coverage, table-driven unit tests with fakes, an `apptest` package that builds the whole app in memory for `httptest`, permission tables, middleware tests, integration tests behind a build tag against a guarded test database, `-p 1`, and store contract tests that keep fakes and real stores identical. This lesson replaced an older, shorter reference note on testing and production; the production half now lives in lessons 27 and 28.
