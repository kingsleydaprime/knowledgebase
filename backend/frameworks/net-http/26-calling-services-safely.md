---
id: 98dac4f2-8c88-4e2c-a6b7-497aca90186a
---

# Calling Other Services Safely

**Calling another service safely means never waiting longer than the answer is worth, retrying only what's safe to repeat and only when it might help, stopping calls to a service that's clearly unwell so you don't make it worse, and proving who you are when you call.** Each call between services is a small bet that the other side is healthy. These are the habits that stop one lost bet from spreading through the whole system.

## Before you start
<!-- bite: bd4d06be-766b-4baa-b83e-b4b202cec228 -->

You should have finished [[backend/frameworks/net-http/25-splitting-out-a-microservice|lesson 25]], with the API and the notifications service both running. This lesson builds on lesson 22's deadlines and status codes, lesson 12's careful token checks, and lesson 13's default-deny policy, now for programs instead of people.

After this lesson you will be able to:

1. Explain cascading failures, and why slow is often worse than down.
2. Use Go contexts so every call has a deadline, and the remaining time is passed on by itself.
3. Retry only temporary errors, a couple of times, with backoff and jitter, and never past the deadline.
4. Wrap calls in a circuit breaker with gobreaker, counting only failures that mean "unwell".
5. Choose fallbacks, and keep the number of calls in flight small.
6. Prove which service is calling with short-lived signed tokens on every gRPC call, check them with a default-deny table, and know when to add TLS.

## What to install
<!-- bite: 63291733-3dba-4fe1-9f70-f21b276b9310 -->

One Go module, for the circuit breaker:

```bash
go get github.com/sony/gobreaker/v2@latest
```

**gobreaker** is a small, widely used circuit breaker. Version 2 is generic: a breaker for calls that return a `*menuv1.GetDishResponse` is a `*gobreaker.CircuitBreaker[*menuv1.GetDishResponse]`, so results come back typed.

You'll also make a key pair for the notifications service with `openssl`, which comes with Linux and macOS (on Windows it comes with Git for Windows, in Git Bash). Check with `openssl version`.

## Where we stopped
<!-- bite: 5655770d-f01f-4a9b-b846-87e287f01707 -->

Picture lunchtime next Friday:

1. The API is busy, and its database is slow for a minute. `GetContact` normally takes 5 ms; now it takes 4 seconds.
2. Suppose notifications had no deadline on its calls. Each one waits the whole 4 seconds.
3. Events pile up in the stream. Notifications' code, seeing errors when calls finally fail, retries straight away. Then again.
4. The API, already slow, now gets three times as many `GetContact` calls as usual, from the retries. It slows down more. Customers' order requests on the API, which share the same database and CPU, start timing out too.

Nothing was broken. One database was slow for a minute. But the way notifications *called* the API turned a slow minute into an outage for customers placing orders. That chain reaction is called a **cascading failure**, and it's the classic way systems of many services fall over.

And separately, there's the hole lesson 25 left open: anything on the internal network can call `GetContact` and read any customer's email and phone number.

## The kid version
<!-- bite: 1db308a2-1ee7-46ae-9963-becb48877fe2 -->

Mama sends her boy to the market for tomatoes. She says: "Be back in 30 minutes, whatever happens."

If the tomato seller's queue is long, the boy waits... until 25 minutes, then comes home with whatever he has. He doesn't stand there all day while Mama's stew burns.

If the seller was out of tomatoes this morning, and again at noon, Mama doesn't send him a third time at 12:30. She says "the tomato seller is closed today; use tinned tomatoes", and tries again later.

And the seller only gives the boy Mama's usual order if he shows Mama's card. A stranger saying "Mama sent me" gets nothing.

The 30 minutes is a deadline. Not sending him a third time is a circuit breaker. Tinned tomatoes are a fallback. The card is a service token.

**Where the picture stops working.** The boy can see the queue and judge it. A service can't see inside the one it calls; it only sees how long answers take and how often they fail. So everything here is decided from those two numbers.

## Terms used in this lesson
<!-- bite: 2ed4fcff-a7e3-4a5d-bbbb-42603f386a60 -->

1. **Cascading failure**: This is when a problem in one service spreads to the services that call it, and then to the services that call *them*.
2. **Deadline**: This is the latest time a caller will wait for an answer. A **timeout** is the same idea written as a length of time ("500 ms").
3. **Deadline propagation**: This is passing the remaining time on to the next call, so a service doesn't start work its caller has already stopped waiting for.
4. **Retry storm**: This is when many callers retry at once, multiplying the load on a service that's already struggling.
5. **Jitter**: This is randomness added to retry waits, so callers don't all retry at the same instant.
6. **Circuit breaker**: This is a switch in the caller that stops calling a service for a while after too many failures, fails at once instead, and then tries again carefully.
7. **Fallback**: This is what you do instead when a call fails: a default, a cached answer, or "try later".
8. **Bulkhead**: This is a limit on how many calls to one service can be in progress at once, so one slow service can't take up everything you have. (Named after the walls in a ship that stop one leak from sinking the whole ship.)
9. **Service identity**: This is proof of *which service* is calling, as opposed to which user.

## Step 1: why waiting is the enemy
<!-- bite: 168f2187-27e7-44f1-bb52-3c0825e5694d -->

Every call that's waiting holds something: a goroutine, memory, a slot in the consumer, a database connection, a person waiting for an answer. Waiting calls pile up faster than you'd think.

If a service gets 100 calls a second and each takes 5 ms, about **half a call** is in progress at any moment. If each takes 4 seconds, **400 calls** are in progress at once, each holding its resources. Same traffic, 800 times the resources, just from slowness.

That's why **slow is often worse than down**. A service that's down fails in a millisecond, and callers move on. A service that's slow holds every caller for as long as it's allowed to.

So the rules come down to: **don't wait long, don't wait for things that won't come, and don't make it worse.**

## Step 2: deadlines everywhere, and passed on
<!-- bite: e2e4e2aa-c05c-4411-a6ee-9df42f78b8cc -->

Lesson 22 put a deadline on every gRPC call with `context.WithTimeout`, and lesson 25's `GRPCCustomers` already gives `GetContact` 500 ms. How long should it be? Look at how long the call takes when things are healthy (lesson 27's metrics will tell you exactly), and set the deadline at a few times the slow end of normal. `GetContact` normally takes 5 ms, and on a bad day 50 ms; 300 ms gives plenty of room, and turns a 4-second disaster into a quick, clear failure:

```go
ctx, cancel := context.WithTimeout(ctx, 300*time.Millisecond)
defer cancel()
```

**Passing the remaining time on is where Go shines.** In most languages you have to do it by hand: work out how much time is left and give the next call no more. In Go, it happens by itself, for three reasons that fit together:

1. **`context.WithTimeout` can only shorten a deadline, never lengthen it.** If the parent context has 50 ms left, `WithTimeout(ctx, 300*time.Millisecond)` gives a context with 50 ms, not 300.
2. **gRPC sends the deadline with the call.** The server's handler gets a `ctx` whose deadline is the caller's (lesson 22 tested this: a 100 ms deadline stopped a 1-second handler in 0.10 s).
3. **Every call we make inside a handler uses that `ctx`.** Postgres queries, Redis calls, the next gRPC call: each inherits whatever time is left.

So if notifications gives the API 300 ms, and the API's `GetContact` handler had to call a third service after 250 ms of work, that call gets 50 ms, automatically. Nobody does work nobody's waiting for. **The only way to break it is to start a fresh context**, with `context.Background()` inside a handler, which throws the caller's deadline away. Don't, except on purpose, the way lesson 15 used `context.WithoutCancel` for a save that must finish.

The consumer adds one more layer: lesson 25 gave each event's handler 20 seconds in all, so even a handler making several calls can't hold a message past its ack wait.

## Step 3: retry carefully, or not at all
<!-- bite: 33d3d588-3c6d-46e5-9952-8acc281346b0 -->

Retries fix brief blips: a restart, a dropped connection. They also cause retry storms. So every retry needs four answers:

1. **Is the call safe to repeat?** `GetContact` and `GetDish` only read, so yes. A call that *does* something (charge a card, send a text) is only safe to retry if it's idempotent, with a key, like lesson 15.
2. **Is the error worth retrying?** Only temporary ones: `UNAVAILABLE` (lesson 22 kept that code for exactly this) and `RESOURCE_EXHAUSTED` ("I'm overloaded, back off"). Never `NOT_FOUND`, `INVALID_ARGUMENT` or `PERMISSION_DENIED`: they'll fail the same way every time. And not `DEADLINE_EXCEEDED`: the deadline has passed, so there's no time left to try again.
3. **How many times?** Few: two retries at most. Three layers each retrying three times means one failure becomes 27 calls at the bottom.
4. **How long to wait?** A little, growing, with jitter: about 50 ms, then about 100 ms, each plus a random amount.

`internal/resilience/retry.go`:

```go
// Package resilience holds the habits every call to another service needs. It knows nothing about Mama Put.
package resilience

import (
	"context"
	"math/rand/v2"
	"time"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// Temporary says whether a gRPC error is worth trying again: the service may answer next time.
func Temporary(err error) bool {
	switch status.Code(err) {
	case codes.Unavailable, codes.ResourceExhausted:
		return true
	}
	return false
}

// Retry calls fn up to 1+retries times, while it fails with an error retryable says is temporary.
// It waits base, then 2×base, ..., each plus up to the same again at random, and never past ctx's deadline.
func Retry[T any](ctx context.Context, retries int, base time.Duration, retryable func(error) bool,
	fn func(context.Context) (T, error)) (T, error) {
	var (
		res T
		err error
	)
	for attempt := 0; ; attempt++ {
		res, err = fn(ctx)
		if err == nil || attempt == retries || !retryable(err) {
			return res, err
		}
		wait := base << attempt
		wait += rand.N(wait) // jitter: callers that failed together don't retry together
		if dl, ok := ctx.Deadline(); ok && time.Until(dl) < wait {
			return res, err // no time left for another try; give up now with the real error
		}
		select {
		case <-ctx.Done():
			return res, err
		case <-time.After(wait):
		}
	}
}
```

1. **`Retry[T any]` is generic**, so it works for any call: `Retry(ctx, 2, 50*time.Millisecond, resilience.Temporary, func(ctx context.Context) (*menuv1.GetDishResponse, error) {...})` returns a `*menuv1.GetDishResponse`.
2. **`rand.N(wait)`** (from `math/rand/v2`) is a random duration between zero and `wait`, so the actual waits are 50–100 ms, then 100–200 ms. Two hundred notifications copies that all failed at 12:40:00.000 retry spread across 50 milliseconds instead of at once.
3. **It won't sleep past the deadline.** If there's 30 ms left and the next wait is 60 ms, there's no point waiting; it returns the real error now. That's the deadline from step 2, respected by the retry as well.
4. **The `select` on `ctx.Done()`** means a caller that gives up stops the waiting too, instead of sleeping on regardless.

The tests ran these against a real gRPC server over `bufconn`: a server that answered `UNAVAILABLE` twice and then succeeded was called **3** times and the call succeeded; a server that answered `NOT_FOUND` was called exactly **once**; and with only 60 ms left on the context, a failing call was tried once and gave up in 3 ms instead of waiting for a retry it had no time for.

**Remember the retries we already have.** The notifications consumer NAKs a message whose handler failed, and JetStream gives it back later, with growing delays (lesson 25). That's a slow outer retry, seconds to minutes apart. So the inner retry only needs to cover a blip of a few hundred milliseconds; anything longer is the stream's job. Two layers, each doing the job it's good at.

(gRPC can also retry by itself, set per method in a "service config" given to the client with `grpc.WithDefaultServiceConfig`. It's a fine alternative. Writing it out shows what it does, and lets the breaker in step 4 see each whole attempt.)

## Step 4: the circuit breaker
<!-- bite: 4fe87d3d-139c-4927-bcf4-bba035afbd93 -->

Retries help with blips. When the API is properly down or struggling for minutes, every call still waits for its deadline and fails, and every one of them adds load. Better to notice, and **stop calling for a while**.

A circuit breaker has three states:

```text
            5 unwell failures in a row
  CLOSED ─────────────────────────────────► OPEN
 (normal:                                  (every call fails at once,
  calls go through)                         without touching the network)
     ▲                                           │
     │ the trial call worked                     │ after 15 seconds
     │                                           ▼
     └──────────────────────────────────── HALF-OPEN
                  the trial call failed:   (one trial call goes through)
                  back to OPEN
```

`internal/resilience/breaker.go`:

```go
package resilience

import (
	"context"
	"errors"
	"log/slog"
	"time"

	"github.com/sony/gobreaker/v2"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// ErrOpen is returned at once, without calling, while a breaker is open.
var ErrOpen = gobreaker.ErrOpenState

// NewBreaker opens after 5 failures in a row that say the other service is unwell,
// stays open 15 s, then lets one trial call through.
func NewBreaker[T any](name string, log *slog.Logger) *gobreaker.CircuitBreaker[T] {
	return gobreaker.NewCircuitBreaker[T](gobreaker.Settings{
		Name:        name,
		MaxRequests: 1,                // one trial call when half-open
		Interval:    10 * time.Second, // while closed, forget old failures every 10 s
		Timeout:     15 * time.Second, // how long to stay open
		ReadyToTrip: func(c gobreaker.Counts) bool { return c.ConsecutiveFailures >= 5 },
		IsSuccessful: func(err error) bool {
			return err == nil || !Unwell(err) // "no such customer" is a healthy answer
		},
		IsExcluded: func(err error) bool {
			return errors.Is(err, context.Canceled) // our own caller gave up: says nothing about them
		},
		OnStateChange: func(name string, from, to gobreaker.State) {
			log.Warn("circuit breaker changed", "breaker", name, "from", from.String(), "to", to.String())
		},
	})
}

// Unwell says whether an error means the other service is struggling, not that it answered "no".
func Unwell(err error) bool {
	switch status.Code(err) {
	case codes.Unavailable, codes.DeadlineExceeded, codes.Internal, codes.ResourceExhausted, codes.Unknown:
		return true
	}
	return false
}
```

The settings that matter:

1. **`ReadyToTrip`**: open after 5 failures **in a row**. One success in between resets the count, so a service that's merely a bit flaky stays usable.
2. **`Timeout: 15s`**: how long to stay open. For 15 seconds the API gets a rest, and notifications stops wasting its own time on calls that will fail.
3. **`MaxRequests: 1`**: when half-open, exactly one trial call goes through; others fail at once until it answers.
4. **`IsSuccessful`**: which errors count against the API. A `NOT_FOUND` means the API is working fine and answered "no such customer". Counting it as a failure would let five deleted customers in a row shut off all notifications. So only errors that mean "unwell" count.
5. **`IsExcluded`**: a call *we* cancelled (notifications shutting down) says nothing about the API's health, so it isn't counted at all.
6. **`OnStateChange`** logs every change. "Breaker `customers` went from closed to open" is one of the most useful lines your logs will ever hold; lesson 27 turns it into a metric and an alert.

From the test, a server answering `UNAVAILABLE` every time:

```text
breaker call 1: Unavailable (server calls 1) open=false
breaker call 2: Unavailable (server calls 2) open=false
breaker call 3: Unavailable (server calls 3) open=false
breaker call 4: Unavailable (server calls 4) open=false
breaker call 5: Unavailable (server calls 5) open=false
breaker call 6: Unknown (server calls 5) open=true
breaker call 7: Unknown (server calls 5) open=true
```

Calls 6 and 7 never reached the server: the server's counter stayed at 5. And seven `NOT_FOUND` answers in a row left a second breaker closed, with every call going through.

**One breaker per service you call, shared by every call to it.** Make it once in `run`, beside the gRPC connection, and pass it to the client. A breaker made per call remembers nothing.

## Step 5: fallbacks, and putting it together
<!-- bite: 0ec174b3-4357-4363-8dbd-126a1dddc08d -->

When a call fails after its deadline, retries and the breaker, what then? It depends on what the data is for:

1. **The dish name** in "Thank you, Ada! 2 × Jollof rice, ₦3,000." Nice to have. If `GetDish` fails, say "2 plates, ₦3,000". A slightly plainer receipt now is better than a perfect one in ten minutes.
2. **The customer's email or phone number.** Essential: we can't send without it. No fallback: return the error, the consumer NAKs, and the stream retries in a few seconds.
3. **Cache what changes rarely.** Dish names change a few times a year. Keep them in notifications' memory for 10 minutes, and most messages won't call `GetDish` at all. Contact details change more and are personal, so don't keep them longer than one message needs.

The menu client in notifications, with all of it:

```go
type GRPCMenu struct {
	Client  menuv1.MenuServiceClient
	Breaker *gobreaker.CircuitBreaker[*menuv1.GetDishResponse]

	mu    sync.Mutex
	names map[int64]cachedName
}

type cachedName struct {
	name    string
	expires time.Time
}

// DishName gives the dish's name, or "" if it can't be had quickly. Callers word the message without it.
func (m *GRPCMenu) DishName(ctx context.Context, id int64) string {
	m.mu.Lock()
	if c, ok := m.names[id]; ok && time.Now().Before(c.expires) {
		m.mu.Unlock()
		return c.name
	}
	m.mu.Unlock()

	ctx, cancel := context.WithTimeout(ctx, 300*time.Millisecond)
	defer cancel()
	res, err := m.Breaker.Execute(func() (*menuv1.GetDishResponse, error) {
		return resilience.Retry(ctx, 2, 50*time.Millisecond, resilience.Temporary,
			func(ctx context.Context) (*menuv1.GetDishResponse, error) {
				return m.Client.GetDish(ctx, &menuv1.GetDishRequest{Id: id})
			})
	})
	if err != nil {
		return "" // the fallback: a plainer message, sent now
	}

	m.mu.Lock()
	if m.names == nil {
		m.names = map[int64]cachedName{}
	}
	m.names[id] = cachedName{name: res.GetDish().GetName(), expires: time.Now().Add(10 * time.Minute)}
	m.mu.Unlock()
	return res.GetDish().GetName()
}
```

The order matters: **the deadline outside everything, the breaker outside the retries.** One "call" to the breaker is a whole attempt, retries and all. If the retries were outside the breaker, a single message could count as three failures and trip it three times as fast. And the deadline covers the whole thing, retries included: 300 ms in total, not 300 ms each.

The `mu` mutex is there because the cache is shared by every message the service handles, and lesson 2 taught us that shared data needs a lock. Run the tests with `-race` and the race detector will check you didn't miss one.

The **customers client** is the same, without the fallback and without the cache: on failure it returns the error, and the message waits in the stream.

**Bulkheads.** lesson 25's `Consume` callback runs **one message at a time** for each copy of the service: the library calls our function and waits for it before handing over the next. So each copy has at most one handler, and so at most one or two calls to the API, in flight. That's a bulkhead already, and a tight one. If a service ever calls another in parallel (a handler that loads ten dishes at once), give it a limit of its own: a buffered channel used as a semaphore, like lesson 18's photo slot.

## Step 6: who's calling?
<!-- bite: d1dfc129-bdf3-424e-a025-580a26d6d248 -->

Now the open door from lesson 25. `GetContact` returns personal data, and right now it trusts anyone who can reach port 50051. "It's on the internal network" isn't enough: one compromised container, one misconfigured firewall, one curious engineer, and every customer's contact details walk out.

The API needs to know **which service** is calling and **what it's allowed to do**. The same idea as users (lessons 12 and 13), for programs.

There are two common approaches, and production systems often use both:

1. **Mutual TLS (mTLS).** Each service has its own certificate. Both sides check the other's certificate when connecting, so the connection is encrypted *and* each side knows who the other is. Strong, but managing certificates is real work; service meshes like Istio and Linkerd exist largely to do it for you.
2. **Signed service tokens.** Each service has its own private key. With each call, it sends a short-lived JWT, signed with that key, saying who it is and what it may do. The receiver checks the signature with that service's **public** key.

We'll do tokens, because they need nothing new to run and they carry *permissions*, not just identity. Then we'll turn on TLS for encryption.

### Notifications signs

`internal/servicetoken/servicetoken.go` (a shared package like `resilience`: it knows nothing about Mama Put, so add both to lesson 25's boundary allow-list):

```go
// Package servicetoken proves which of our services is calling, with short-lived signed tokens.
package servicetoken

import (
	"context"
	"crypto/ecdsa"
	"fmt"
	"strings"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

const Audience = "mama-put-api"

type Claims struct {
	Scope string `json:"scope"`
	jwt.RegisteredClaims
}

// Signer makes tokens for one service, and keeps each for most of its life.
// It is a gRPC credentials.PerRPCCredentials: grpc.WithPerRPCCredentials(signer).
type Signer struct {
	Service string // "notifications"
	Key     *ecdsa.PrivateKey
	Scopes  []string
	Secure  bool // true in production: refuse to send tokens over a connection without TLS
	Now     func() time.Time

	mu      sync.Mutex
	token   string
	expires time.Time
}

const lifetime = 2 * time.Minute

func (s *Signer) Token() (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	now := s.Now()
	if s.token != "" && now.Before(s.expires.Add(-30*time.Second)) {
		return s.token, nil
	}
	exp := now.Add(lifetime)
	t := jwt.NewWithClaims(jwt.SigningMethodES256, Claims{
		Scope: strings.Join(s.Scopes, " "),
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    s.Service,
			Audience:  jwt.ClaimStrings{Audience},
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(exp),
		},
	})
	signed, err := t.SignedString(s.Key)
	if err != nil {
		return "", fmt.Errorf("sign service token: %w", err)
	}
	s.token, s.expires = signed, exp
	return signed, nil
}

func (s *Signer) GetRequestMetadata(ctx context.Context, _ ...string) (map[string]string, error) {
	tok, err := s.Token()
	if err != nil {
		return nil, err
	}
	return map[string]string{"authorization": "Bearer " + tok}, nil
}

func (s *Signer) RequireTransportSecurity() bool { return s.Secure }
```

1. **`GetRequestMetadata` and `RequireTransportSecurity`** are the two methods of grpc-go's `credentials.PerRPCCredentials` interface. Having both makes `*Signer` one, so in `cmd/notifications/main.go`, one option adds a token to **every** call on the connection: `grpc.NewClient(addr, grpc.WithTransportCredentials(...), grpc.WithPerRPCCredentials(signer))`. No call can forget it.
2. **Tokens last 2 minutes**, and `Token` reuses one until 30 seconds before it expires: signing is cheap, but not free, and nobody needs a fresh token per call. The mutex makes that safe from many goroutines.
3. **`Secure: true` in production** makes grpc-go **refuse** to send the token over a connection without TLS. I tried it: `grpc.NewClient` fails with "the credentials require transport level security". A token sent in plain text on a shared network can be copied and reused for its two minutes.
4. **`Issuer` is the service's name**; `Audience` is the API. `Scopes` are what notifications needs: `customers:read-contact` and `menu:read`.

### The API checks

`internal/servicetoken/check.go`:

```go
// Caller is the service making this call, as proved by its token.
type Caller struct {
	Service string
	Scopes  []string
}

type callerKey struct{}

func CallerFrom(ctx context.Context) (Caller, bool) {
	c, ok := ctx.Value(callerKey{}).(Caller)
	return c, ok
}

// Check verifies service tokens on the API's gRPC server.
type Check struct {
	Keys  map[string]*ecdsa.PublicKey // each calling service's PUBLIC key, by name
	Rules map[string]string           // full method → the scope it needs; "" means no token needed
	Now   func() time.Time
}

var (
	errNoToken = status.Error(codes.Unauthenticated, "a service token is required")
	errBad     = status.Error(codes.Unauthenticated, "the service token is not valid")
	errScope   = status.Error(codes.PermissionDenied, "this service may not call this method")
)

func (c *Check) authorize(ctx context.Context, method string) (context.Context, error) {
	scope, ok := c.Rules[method]
	if !ok {
		return nil, errScope // a method with no rule: refused (lesson 13's default deny)
	}
	if scope == "" {
		return ctx, nil // health checks
	}
	md, _ := metadata.FromIncomingContext(ctx)
	vals := md.Get("authorization")
	if len(vals) != 1 || !strings.HasPrefix(vals[0], "Bearer ") {
		return nil, errNoToken
	}
	var claims Claims
	_, err := jwt.ParseWithClaims(strings.TrimPrefix(vals[0], "Bearer "), &claims,
		func(t *jwt.Token) (any, error) {
			iss, _ := t.Claims.GetIssuer() // not trusted yet: it only picks which key to check with
			key, ok := c.Keys[iss]
			if !ok {
				return nil, errBad
			}
			return key, nil
		},
		jwt.WithValidMethods([]string{"ES256"}),
		jwt.WithAudience(Audience),
		jwt.WithExpirationRequired(),
		jwt.WithIssuedAt(),
		jwt.WithTimeFunc(c.Now),
		jwt.WithLeeway(10*time.Second),
	)
	if err != nil {
		return nil, errBad
	}
	scopes := strings.Fields(claims.Scope)
	if !slices.Contains(scopes, scope) {
		return nil, errScope
	}
	return context.WithValue(ctx, callerKey{}, Caller{Service: claims.Issuer, Scopes: scopes}), nil
}

func (c *Check) Unary() grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
		ctx, err := c.authorize(ctx, info.FullMethod)
		if err != nil {
			return nil, err
		}
		return handler(ctx, req)
	}
}

type wrappedStream struct {
	grpc.ServerStream
	ctx context.Context
}

func (w wrappedStream) Context() context.Context { return w.ctx }

func (c *Check) Stream() grpc.StreamServerInterceptor {
	return func(srv any, ss grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) error {
		ctx, err := c.authorize(ss.Context(), info.FullMethod)
		if err != nil {
			return err
		}
		return handler(srv, wrappedStream{ServerStream: ss, ctx: ctx})
	}
}
```

And in `grpcapi.NewServer`, first in both chains, so an unauthorized call never reaches anything else:

```go
check := &servicetoken.Check{Keys: serviceKeys, Now: time.Now, Rules: map[string]string{
	"/mamaput.customers.v1.CustomersService/GetContact": "customers:read-contact",
	"/mamaput.menu.v1.MenuService/GetDish":              "menu:read",
	"/mamaput.menu.v1.MenuService/BatchGetDishes":       "menu:read",
	"/mamaput.menu.v1.MenuService/WatchPortions":        "menu:read",
	"/grpc.health.v1.Health/Check":                      "",
	"/grpc.health.v1.Health/List":                       "",
	"/grpc.health.v1.Health/Watch":                      "",
}}
srv := grpc.NewServer(
	grpc.ChainUnaryInterceptor(check.Unary(), Log(log), Errors(log), Recover(log)),
	grpc.ChainStreamInterceptor(check.Stream(), StreamErrors(log)),
	grpc.MaxRecvMsgSize(1<<20),
)
```

What this gives us:

1. **Only services we know** (whose public key is in the API's config) can call at all.
2. **Each service only does what it's allowed.** Notifications has `customers:read-contact` and `menu:read`. A future reporting service might get `menu:read` only, and asking for a contact gives `PERMISSION_DENIED`.
3. **A method with no rule is refused.** Lesson 13's default deny, again. Add an RPC to a `.proto` and forget its rule, and it's closed, not open.
4. **Tokens are short-lived**, so a stolen token is useless in minutes.
5. **The private key never leaves its service.** The API holds only public keys, which can't sign anything. If the API were broken into, the attacker still couldn't pretend to be notifications.
6. **Audience again** (lessons 12 and 24): a token for `mama-put-api` can't be replayed at some other service.
7. **The caller reaches the handler.** `servicetoken.CallerFrom(ctx)` tells `CustomersServer.GetContact` who's asking, so it can log "notifications read customer 7's contact": exactly the record you want when someone asks who has seen their data.

Two Go details:

1. **The key function reads the issuer before the token is checked.** golang-jwt decodes the claims first, then calls our function to get the key, then checks the signature with it. Reading `iss` there is safe because it only *chooses* a key; if someone writes `"iss": "notifications"` on a token they signed themselves, the signature check against notifications' real public key fails.
2. **`wrappedStream`** embeds `grpc.ServerStream` and replaces just `Context()`, so a streaming handler sees the caller in its context. Embedding an interface and overriding one method is the usual Go way to wrap anything.

**A completeness test.** `srv.GetServiceInfo()` lists every service and method the gRPC server has registered. Loop over it and check each has a rule:

```go
for name, info := range srv.GetServiceInfo() {
	for _, m := range info.Methods {
		if _, ok := check.Rules["/"+name+"/"+m.Name]; !ok {
			t.Errorf("no rule for /%s/%s", name, m.Name)
		}
	}
}
```

When I first wrote the rules with just `GetDish` and `Health/Check`, this test found four gaps: `BatchGetDishes`, `WatchPortions`, and the health service's `List` and `Watch`. Default deny kept them closed; the test made them visible. It's lesson 13's `TestEveryActionHasARule` for programs.

The tests for the check, all through `bufconn`: no token gives `UNAUTHENTICATED`; a token signed with the wrong key, a token for a service we don't know, and an expired token all give `UNAUTHENTICATED` with the same plain message; a good token with the wrong scope gives `PERMISSION_DENIED`; a method with no rule gives `PERMISSION_DENIED`; the health check works with no token; and a good token reaches the handler, which can see `Caller{Service: "notifications"}`.

### Keys

Generate a key pair once per calling service:

```bash
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out notifications-private.pem
openssl pkey -in notifications-private.pem -pubout -out notifications-public.pem
```

The private file goes into notifications' secrets (lesson 28); the public one into the API's config. **Neither goes in git.** Read them in `run` with `jwt.ParseECPrivateKeyFromPEM` and `jwt.ParseECPublicKeyFromPEM`. To change a key: add the new public key to the API under a second name, move notifications to the new private key, then remove the old public key.

### Encrypting the traffic

Tokens prove who's calling, but with `insecure.NewCredentials()` anyone who can watch the internal network can read the token and the contact details as they pass. In production, turn on TLS:

```go
// the API's gRPC server
creds, err := credentials.NewServerTLSFromFile("api-grpc.crt", "api-grpc.key")
srv := grpc.NewServer(grpc.Creds(creds), /* interceptors as above */)

// notifications' client
creds, err := credentials.NewClientTLSFromFile("internal-ca.crt", "api") // "api": the name on the API's certificate
conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(creds), grpc.WithPerRPCCredentials(signer))
```

With `Secure: true` on the signer, notifications now can't even start without TLS. For **mutual TLS**, the server's `tls.Config` gets `ClientAuth: tls.RequireAndVerifyClientCert` and the client presents a certificate of its own; then the connection itself proves which service is on the other end, and the token adds the permissions. Where certificates come from (an internal certificate authority, or a service mesh that hands them out) is an operations choice. In lesson 28's Docker Compose, the services share a private network that nothing outside can reach, and that's a reasonable place to stop for Mama Put.

## Step 7: the same habits for HTTP calls
<!-- bite: 7a6df084-13ae-4708-b03b-f37cf0679e18 -->

Everything above applies to plain HTTP calls too, like lesson 17's calls to Paystack:

1. **Deadline**: lesson 17's `http.Client{Timeout: 10 * time.Second}` and `NewRequestWithContext` were already there. Because the request carries the context, a customer who closes the app cancels the call to Paystack too.
2. **Retries**: only for safe calls. Paystack's `verify` is a read, so a retry is fine; `initialize` creates a transaction, so a blind retry could create two. Lesson 17 gave each checkout attempt its own reference, so a retried `initialize` is a new attempt, not a double charge, but there's still no reason to make two.
3. **Circuit breaker**: wrap Paystack calls in one, counting 5xx answers and timeouts, not 4xx. When Paystack is down, `StartCheckout` answers 502 at once ("payments are briefly unavailable") instead of making every customer wait 10 seconds for the same failure.
4. **Fallback**: there's no fallback for taking money. Fail fast and say so clearly.
5. **Lesson 17's outgoing webhooks** already had backoff with jitter, and a queue in Postgres, so a slow Okada Riders never holds anything up. That was this lesson, early.

## Step 8: testing failure on purpose
<!-- bite: 1681ffa9-7953-451c-9243-5c147956b202 -->

These behaviours only show up when things go wrong, so tests must make things go wrong. Every one of these is a `bufconn` test with a fake server whose answers the test controls (an `atomic.Int32` counting its calls, and a function deciding each answer):

1. **Deadlines**: a fake that waits 1 second; a client with a 100 ms deadline fails in about 100 ms.
2. **Retries**: `UNAVAILABLE` twice then success gives 3 calls and a success; `NOT_FOUND` gives exactly 1 call; with too little time left, no retry.
3. **The breaker**: five `UNAVAILABLE`s open it; the sixth call fails with `ErrOpen` without reaching the fake (its count stays at 5); seven `NOT_FOUND`s leave it closed. For half-open, give the test a breaker with `Timeout: 50 * time.Millisecond`, wait 60 ms, and check one call goes through.
4. **The fallback**: with `GetDish` failing, `order.paid` still produces a receipt, worded without the dish name.
5. **Auth**: the list at the end of step 6, and the completeness test.
6. **The whole chain, by hand**: run both services, pay for an order, and see the receipt. Then pause the API's process (`kill -STOP <pid>`) while you pay for a few more, watch notifications' log show the breaker opening, resume it (`kill -CONT <pid>`), and watch the breaker go half-open, then closed, and the receipts arrive.

## The Go in this lesson
<!-- bite: 9267e271-1414-43ba-b122-177a5b553d7d -->

1. **`context.WithTimeout` only ever shortens**: A child context's deadline is the earlier of its own and its parent's, which is what makes deadline propagation automatic.
2. **`ctx.Deadline()`**: The deadline and whether there is one, so code can decide there's no time for another try.
3. **A generic helper, `Retry[T any](..., fn func(context.Context) (T, error)) (T, error)`**: One retry loop for every kind of call, with typed results.
4. **`math/rand/v2`'s `rand.N(d)`**: A random value from 0 up to `d`, for any integer type, including `time.Duration`.
5. **`gobreaker.NewCircuitBreaker[T](settings)`** and **`cb.Execute(func() (T, error))`**: A generic breaker; `Execute` runs the call or fails at once with `ErrOpenState`.
6. **Functions in a settings struct**: `ReadyToTrip`, `IsSuccessful`, `IsExcluded` and `OnStateChange` let you decide the breaker's rules with plain functions.
7. **`credentials.PerRPCCredentials`**: Any type with `GetRequestMetadata` and `RequireTransportSecurity`. `grpc.WithPerRPCCredentials` attaches it to every call.
8. **`metadata.FromIncomingContext(ctx)`**: The gRPC headers of the call being handled; `md.Get("authorization")` returns every value for that key.
9. **A `jwt.Keyfunc` that picks a key by issuer**: The claims are decoded before the key is chosen, so the key can depend on them; the signature check makes that safe.
10. **Embedding an interface to override one method, `wrappedStream{grpc.ServerStream, ctx}`**: Every method passes through, except the one you write.
11. **`srv.GetServiceInfo()`**: Every service and method a gRPC server has registered, for completeness tests.
12. **`atomic.Int32`** in a fake: counts calls from the server's goroutines without a mutex, so the test can check how many reached it.

## Your project so far
<!-- bite: 1321d3db-881a-4949-8d32-cf13cd02e93d -->

```text
mama-put/
├── go.mod                         ← github.com/sony/gobreaker/v2
├── cmd/
│   ├── api/main.go                ← loads services' public keys (SERVICE_KEYS_DIR); TLS when GRPC_TLS_CERT is set
│   └── notifications/main.go      ← Signer from NOTIFICATIONS_PRIVATE_KEY; one breaker per API client; TLS in production
└── internal/
    ├── resilience/                ← NEW: shared, knows nothing about Mama Put
    │   ├── retry.go               ← Temporary, Retry[T]: backoff, jitter, never past the deadline
    │   └── breaker.go             ← NewBreaker[T]: 5 unwell failures, 15 s open, one trial; Unwell
    ├── servicetoken/              ← NEW: shared
    │   ├── servicetoken.go        ← Signer: ES256, 2-minute tokens reused, PerRPCCredentials, Secure
    │   ├── check.go               ← Check: rules per method (default deny), issuer picks the key, Caller in ctx
    │   └── servicetoken_test.go   ← every token failure, scopes, health, completeness, retries, the breaker
    ├── grpcapi/
    │   ├── server.go              ← check.Unary() and check.Stream() first in the chains; the rules table
    │   └── customers.go           ← logs which service read which customer's contact
    ├── payments/paystack.go       ← a breaker around Paystack calls
    └── notifications/
        ├── customers.go           ← 300 ms deadline, breaker, retries; no fallback
        ├── menu.go                ← DishName: cache, deadline, breaker, retries, "" as the fallback
        └── boundary_test.go       ← resilience and servicetoken added to the allow-list
```

## Common mistakes
<!-- bite: 5792fe99-0ee4-4879-8c3f-0fe70edcfb13 -->

1. **No deadline.** One slow service holds every caller. Every call gets one.
2. **`context.Background()` inside a handler.** It throws away the caller's deadline, and work carries on that nobody's waiting for.
3. **Retrying everything.** `NOT_FOUND` and `PERMISSION_DENIED` will fail the same way forever.
4. **Retrying without jitter.** Everyone retries at the same instant, and the struggling service gets a wave instead of a trickle.
5. **Retries at every layer.** They multiply. Retry at one layer, briefly, and let the stream do the slow retries.
6. **A breaker that counts "no" as "unwell".** A run of deleted customers switches off all notifications.
7. **Retries outside the breaker.** One message counts as three failures.
8. **A breaker per call.** It never remembers anything. One per service called, shared.
9. **"It's internal, so it's safe."** Check who's calling, with a token or a certificate.
10. **Private keys in more than one place.** Each service has its own; others hold only public keys.
11. **A method without a rule that's open by default.** Default deny, and a completeness test.
12. **Tokens over plain connections in production.** `Secure: true`, and TLS.

## Check your understanding
<!-- bite: c1e1b9e1-c875-4e33-bc5a-b19e738c104c -->

1. Why can a service that's slow do more damage than one that's down?
2. Notifications gives `GetContact` 300 ms. Inside, the API spends 250 ms and then calls a third service with `context.WithTimeout(ctx, time.Second)`. How long does the third call get, and why?
3. Which gRPC codes does `Retry` try again, which doesn't it, and why not `DEADLINE_EXCEEDED`?
4. Five customers in a row were deleted, and `GetContact` answered `NOT_FOUND` five times. Is the breaker open? Why does that matter?
5. Why is the breaker wrapped around `Retry`, and not the other way round?
6. Someone writes a token with `"iss": "notifications"` and signs it with their own key. Follow what the API's check does with it.
7. Lesson 25's consumer handles one message at a time per copy. What does that have to do with bulkheads?

<details>
<summary>Answers, after your attempt</summary>

1. A service that's down fails in milliseconds, and its callers move on. A slow one holds every caller (goroutines, connections, consumer slots) for as long as they'll wait, so resources pile up: 4-second calls at 100 a second means 400 in flight instead of half of one.
2. About 50 ms. `context.WithTimeout` can only shorten a deadline: the context it's given already ends 50 ms from now (the 300 ms notifications sent, minus the 250 ms spent), so asking for a second still gives 50 ms.
3. It retries `UNAVAILABLE` and `RESOURCE_EXHAUSTED`, which are temporary by definition. It doesn't retry codes that will fail the same way every time (`NOT_FOUND`, `INVALID_ARGUMENT`, `PERMISSION_DENIED`). `DEADLINE_EXCEEDED` means the time we had is gone, so there's no time for another try.
4. No. `IsSuccessful` treats `NOT_FOUND` as a healthy answer, because the API answered correctly. If "no" counted as a failure, a few deleted customers in a row would open the breaker and stop every notification for 15 seconds, while the API was perfectly well.
5. So one attempt, retries included, counts once. Retries inside the breaker try to rescue a blip; if the whole attempt still fails, that's one failure. With retries outside, each retry would be a separate failure, and one bad message would push the breaker three steps toward opening.
6. golang-jwt decodes the claims, and our key function reads `iss`, finds `notifications`, and returns notifications' real public key. The signature check against that key fails, because the token was signed with a different private key, so the call gets `UNAUTHENTICATED`. Reading the issuer only chose the key; it never trusted it.
7. A bulkhead limits how many calls to a service can be in flight at once. Because the callback handles one message at a time, each copy of notifications makes at most one or two calls to the API at any moment, so a slow API can never tie up more than that per copy.

</details>

## Practice
<!-- bite: 12952b45-6c0f-4413-ac50-74f9e15b4d82 -->

1. Write `internal/resilience` and its tests, including the half-open test with a 50 ms `Timeout`.
2. Build `GRPCMenu.DishName` and the customers client with deadlines, retries and breakers, and test the receipt's fallback wording when `GetDish` fails.
3. Write `internal/servicetoken` and every test from step 6, including the completeness test against the real `grpcapi.NewServer`.
4. Wrap the Paystack client from lesson 17 in a breaker that counts only 5xx responses, timeouts and connection errors, and make `StartCheckout` answer 502 straight away while it's open.
5. Generate self-signed certificates for the API's gRPC port with `openssl`, turn on TLS in both services, set `Secure: true`, and check that notifications refuses to start against a plain-text API.
6. Do the `kill -STOP` / `kill -CONT` exercise from step 8 and copy the breaker's log lines into your notes.

**Done when** a 1-second fake fails a 100 ms call in about 100 ms; `UNAVAILABLE` is retried and `NOT_FOUND` isn't; five unwell failures open the breaker and the next call never reaches the server; receipts still go out, plainer, while the menu is unreachable; `GetContact` without a token, with a bad token or with the wrong scope is refused; every gRPC method has a rule; and `make test` passes with `-race`.

## Before moving on
<!-- bite: 4fb44e60-7904-4d18-80c6-c1d3ca91fa2b -->

Calls between Mama Put's services now behave themselves. Every call has a deadline that shrinks as it travels, retries are few, short, spread out and only for errors that might pass, a breaker stops hammering a service that's unwell, plain fallbacks keep messages flowing, and the API knows exactly which service is asking for a phone number and whether it's allowed to.

That's the end of Part 6. We now have two services, a worker, a stream, two Redis servers and Postgres. When Ada says "I paid, but never got my receipt", where do you even start looking? Which program, which log, which second? Part 7 is about running all this for real, and it starts with being able to *see* it: logs you can search, numbers you can graph, and one trace that follows Ada's payment through every program it touched. That's observability, next.

## Related
<!-- bite: 165dbe3b-eaf6-439d-9e53-39b01a9b3910 -->

- [[backend/frameworks/net-http/27-observability|Next: Observability]]
- [[backend/frameworks/express/26-calling-services-safely|The same lesson in Express]] — a hand-written breaker, and deadlines passed on by hand
- [[backend/frameworks/net-http/22-grpc|gRPC]] — deadlines and the status codes retries depend on
- [[backend/frameworks/net-http/13-authorization|Authorization]] — default deny and the completeness test, first for people
- [[backend/frameworks/net-http/17-payments-and-webhooks|Payments and Webhooks]] — the HTTP calls that get the same habits

## About this lesson
<!-- bite: 6db1bf16-825f-4679-9fb0-6365d4c51b70 -->

**Level:** Advanced. Lesson 26 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, grpc-go, golang-jwt v5 and gobreaker v2. Covers cascading failures and why slow is worse than down, deadlines with contexts and why Go propagates them automatically, a generic retry helper with temporary-only codes, exponential backoff, jitter and deadline awareness, a generic circuit breaker with gobreaker that counts only "unwell" errors and ignores cancellations, the order of deadline, breaker and retries, fallbacks and small caches, bulkheads, service identity with short-lived ES256 tokens as per-call gRPC credentials, a default-deny method table with a completeness test, choosing the key by issuer safely, wrapping server streams, key handling and TLS or mutual TLS, the same habits for HTTP calls, and testing failures on purpose with `bufconn`.
