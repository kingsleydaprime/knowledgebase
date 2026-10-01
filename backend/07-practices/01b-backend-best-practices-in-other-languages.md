# Backend Best Practices in Other Languages

> **[Intermediate]** · A companion to [[backend/07-practices/01-backend-best-practices|backend best practices]], which builds an error contract, validation, redacted logs, a token bucket and idempotency keys in Node. Error mapping is covered in [[backend/03-structuring-a-backend/01b-layers-in-other-languages|layers in other languages]] and idempotent consumers in [[backend/03-structuring-a-backend/05b-modular-monolith-in-other-languages|the modular monolith companion]]. This one covers what's left: **each ecosystem's tools**, and two pieces worth seeing in code — **rate limiting** and **structured, redacted logging**.

## Before you start

You can already:

- Build the main lesson's endpoint: one error shape, boundary validation, JSON logs with a request ID, a token bucket, idempotency keys → [[backend/07-practices/01-backend-best-practices|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Name your framework's central error handler, validation library, structured logger and rate limiter.
2. Implement or configure a token bucket in your language, with a testable clock.
3. Write redacted, request-scoped JSON logs with your language's standard tools.

## The kid version

Every school needs a register, a lost-property box and a rule about how many people can be in the tuck shop at once. Some schools are given the cupboard and forms by the education board (**built into the framework**); others buy them from a shop (**a library**); a few make their own (**written by hand**). The rules are the same in all of them.

**Where the analogy stops working.** A shop-bought register can't be wrong about the date — but a library rate limiter that reads the real clock can make your tests wait, or flaky. Whether you can *inject* the clock matters more than who made the tool. §2 shows one that can't.

## 1. The tools, by ecosystem

| Language / framework | Central error handler | Validation | Structured logging | Rate limiting |
|---|---|---|---|---|
| TypeScript — Express / NestJS | error middleware / exception filter | zod, class-validator | pino | `express-rate-limit`, `@nestjs/throttler` |
| Python — FastAPI / Django | `exception_handler` / DRF `EXCEPTION_HANDLER` | **Pydantic** / DRF serializers | `logging` + JSON formatter, structlog | slowapi, django-ratelimit |
| Go | a wrapping middleware | go-playground/validator | **`log/slog`** — standard library | **`golang.org/x/time/rate`** |
| Java — Spring | `@RestControllerAdvice` | **Bean Validation** (`@Valid`, `@NotNull`) | SLF4J + Logback, **MDC** for the request ID | Bucket4j, Resilience4j |
| Rust — Axum | `impl IntoResponse` for your error | `validator`, `garde` | **`tracing`** | `governor` / `tower_governor` |
| C# — ASP.NET Core | `IExceptionHandler` + `ProblemDetails` | DataAnnotations, FluentValidation | **`ILogger`** with scopes, Serilog | **`AddRateLimiter`** — built in |
| C, C++ | return codes / exceptions at the handler | by hand | spdlog (C++) | by hand |

**Request IDs follow the language's "context" mechanism:** a `ContextVar` in Python, a value in `context.Context` (read by an `slog` handler) in Go, the **MDC** (a per-thread map that Logback adds to every line) in Java, a `tracing` span in Rust, a logging **scope** in .NET, `AsyncLocalStorage` in Node. That's the same mechanism as the scope-bug fix in [[backend/03-structuring-a-backend/03b-dependency-injection-in-other-languages|DI in other languages]].

## 2. Rate limiting: the clock decides how testable it is

The main lesson's token bucket — burst of 3, refilling at 0.5 per second, fourth request told to wait 2 seconds — is the scenario every lab below runs. The interesting difference is the clock:

| Language | Token bucket | Clock |
|---|---|---|
| Go | `x/time/rate` | **passed per call** (`ReserveN(now, 1)`) — fully testable |
| Python, Java, Rust, C, C++ | written here (or a library) | injected |
| C# | `TokenBucketRateLimiter` | **reads the real clock** — tests must wait |

## Terms used in this lesson

1. **MDC (mapped diagnostic context)**: The letters stand for those three words. In Java logging, it is a per-thread map whose values (such as the request ID) are added to every log line.
2. **Span**: In Rust's `tracing` and in OpenTelemetry, this is a named, timed section of work; fields recorded on it appear on every event inside it.
3. **Logging scope**: In .NET, this is a set of values attached to all log messages written inside a `using` block.
4. **Bean Validation**: This is Java's standard annotation-based validation (`@NotNull`, `@Email`), run by Spring on `@Valid` request bodies.

## 3. Go

Both tools are first-party. `x/time/rate` is a token bucket maintained by the Go team, and its methods **take the current time as an argument**, so tests need no fake clock. `log/slog`, in the standard library since Go 1.21, writes JSON, and its `ReplaceAttr` hook is the natural place for redaction.

```go
// Package practices: rate limiting with golang.org/x/time/rate (the Go team's token bucket)
// and structured, redacted logging with log/slog (standard library since Go 1.21).
package practices

import (
	"io"
	"log/slog"
	"regexp"
	"time"

	"golang.org/x/time/rate"
)

// NewLimiter: bursts of 3, refilling at 0.5 tokens per second.
func NewLimiter() *rate.Limiter { return rate.NewLimiter(rate.Limit(0.5), 3) }

// Allow takes the time as an argument, so tests control the clock. It returns how long to wait if not.
func Allow(l *rate.Limiter, now time.Time) (ok bool, retryAfter time.Duration) {
	r := l.ReserveN(now, 1)
	if delay := r.DelayFrom(now); delay > 0 {
		r.CancelAt(now) // give the token back: we're refusing, not queueing
		return false, delay
	}
	return true, 0
}

var secretKey = regexp.MustCompile(`(?i)token|password|secret|authorization|card`)

// NewLogger writes one JSON object per line and redacts secret-looking keys centrally.
func NewLogger(w io.Writer) *slog.Logger {
	return slog.New(slog.NewJSONHandler(w, &slog.HandlerOptions{
		ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
			if a.Key == slog.TimeKey {
				return slog.Attr{} // drop the timestamp so the test output is stable
			}
			if secretKey.MatchString(a.Key) {
				return slog.String(a.Key, "[redacted]")
			}
			return a
		},
	}))
}
```

```go
package practices

import (
	"bytes"
	"strings"
	"testing"
	"time"
)

func TestTokenBucket(t *testing.T) {
	l := NewLimiter()
	start := time.Date(2026, 10, 5, 9, 0, 0, 0, time.UTC)
	var got []bool
	for range 4 {
		ok, _ := Allow(l, start)
		got = append(got, ok)
	}
	if got[0] != true || got[1] != true || got[2] != true || got[3] != false {
		t.Fatalf("burst = %v, want three allowed then refused", got)
	}
	if _, wait := Allow(l, start); wait != 2*time.Second {
		t.Fatalf("retry after %v, want 2s", wait)
	}
	if ok, _ := Allow(l, start.Add(2*time.Second)); !ok {
		t.Fatal("refilled after 2s")
	}
}

func TestLogsAreJSONAndRedacted(t *testing.T) {
	var buf bytes.Buffer
	NewLogger(&buf).Info("payment.charged", "requestId", "req_1", "cardToken", "tok_visa_4242", "amountKobo", 500000)
	line := strings.TrimSpace(buf.String())
	want := `{"level":"INFO","msg":"payment.charged","requestId":"req_1","cardToken":"[redacted]","amountKobo":500000}`
	if line != want {
		t.Fatalf("\n got %s\nwant %s", line, want)
	}
}
```

**Lab:** `labs/backend-best-practices-go/` — checked with Go 1.26; `go test` downloads `golang.org/x/time` on the first run.

## 4. Python

A token bucket over an injected clock, and the standard `logging` module with a JSON formatter that reads the request ID from a `ContextVar` and redacts by key. In FastAPI, a middleware sets the `ContextVar` once per request; **Pydantic** models do the validation, reporting every field error at once by default.

```python
"""practices.py — a token bucket with an injected clock, and stdlib logging that writes
redacted JSON lines with a request ID taken from a context variable."""
import json
import logging
import math
import re
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")


class TokenBucket:
    def __init__(self, capacity: float, per_second: float, clock):
        self.capacity, self.per_second, self.clock = capacity, per_second, clock
        self.buckets: dict[str, tuple[float, float]] = {}

    def take(self, key: str) -> tuple[bool, int]:
        """Returns (allowed, retry_after_seconds)."""
        now = self.clock()
        tokens, at = self.buckets.get(key, (self.capacity, now))
        tokens = min(self.capacity, tokens + (now - at) * self.per_second)
        if tokens >= 1:
            self.buckets[key] = (tokens - 1, now)
            return True, 0
        self.buckets[key] = (tokens, now)
        return False, math.ceil((1 - tokens) / self.per_second)


SECRET = re.compile(r"token|password|secret|authorization|card", re.I)


class JsonFormatter(logging.Formatter):
    """One JSON object per line. Extra fields come from `logger.info(msg, extra={...})`."""

    def format(self, record: logging.LogRecord) -> str:
        fields = getattr(record, "fields", {})
        entry = {"level": record.levelname, "msg": record.getMessage(), "requestId": request_id.get()}
        entry.update({k: "[redacted]" if SECRET.search(k) else v for k, v in fields.items()})
        return json.dumps(entry)


def make_logger(stream) -> logging.Logger:
    logger = logging.getLogger("shop")
    logger.handlers.clear()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
```

**Lab:** `labs/backend-best-practices-python/` — checked with Python 3.14.

## 5. Java

In Spring, validation is **Bean Validation** annotations on the request record plus `@Valid` on the controller parameter; the request ID goes in the **MDC** from a filter, and Logback's JSON encoder writes it on every line. Rate limiting comes from Bucket4j or Resilience4j. The lab shows the bucket itself, with `java.time.Clock` injected:

```java
package practices;

import java.time.Clock;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

// A token bucket with an injected java.time.Clock. In Spring projects, Bucket4j or
// Resilience4j's RateLimiter provide this, and Redis-backed versions share it between servers.
public final class TokenBucket {
    public record Decision(boolean allowed, long retryAfterSeconds) {}

    private record State(double tokens, long atMillis) {}

    private final double capacity, perSecond;
    private final Clock clock;
    private final Map<String, State> buckets = new HashMap<>();

    public TokenBucket(double capacity, double perSecond, Clock clock) {
        this.capacity = capacity; this.perSecond = perSecond; this.clock = clock;
    }

    public synchronized Decision take(String key) {
        long now = clock.millis();
        State s = buckets.getOrDefault(key, new State(capacity, now));
        double tokens = Math.min(capacity, s.tokens() + (now - s.atMillis()) / 1000.0 * perSecond);
        if (tokens >= 1) {
            buckets.put(key, new State(tokens - 1, now));
            return new Decision(true, 0);
        }
        buckets.put(key, new State(tokens, now));
        return new Decision(false, (long) Math.ceil((1 - tokens) / perSecond));
    }

    // A clock the test can move forward.
    public static final class MutableClock extends Clock {
        private java.time.Instant now;
        public MutableClock(java.time.Instant start) { now = start; }
        public void advance(Duration d) { now = now.plus(d); }
        @Override public java.time.Instant instant() { return now; }
        @Override public java.time.ZoneId getZone() { return java.time.ZoneOffset.UTC; }
        @Override public Clock withZone(java.time.ZoneId zone) { return this; }
    }

    public static void main(String[] args) {
        var clock = new MutableClock(java.time.Instant.parse("2026-10-05T09:00:00Z"));
        var bucket = new TokenBucket(3, 0.5, clock);
        for (int i = 0; i < 3; i++) assert bucket.take("u1").allowed();
        assert bucket.take("u1").equals(new Decision(false, 2));
        assert bucket.take("u2").allowed();
        clock.advance(Duration.ofSeconds(2));
        assert bucket.take("u1").allowed();
        System.out.println("ok: token bucket with an injected Clock");
    }
}
```

**Lab:** `labs/backend-best-practices-java/` — checked with Java 21.

## 6. Rust

In Axum, errors implement `IntoResponse`, validation uses `validator` or `garde`, and logging is **`tracing`** — fields recorded on a request span appear on every log event inside it. `tower_governor` provides rate-limiting middleware. The bucket, generic over a `Clock` trait:

```rust
//! A token bucket over an injected clock. In Axum services, the `governor` crate (via
//! `tower_governor`) provides this as middleware.
use std::collections::HashMap;
use std::time::Duration;

pub trait Clock {
    /// Time since an arbitrary start; only differences matter.
    fn now(&self) -> Duration;
}

pub struct TokenBucket<C: Clock> {
    capacity: f64,
    per_second: f64,
    clock: C,
    buckets: HashMap<String, (f64, Duration)>,
}

#[derive(Debug, PartialEq)]
pub enum Decision {
    Allowed,
    Limited { retry_after_secs: u64 },
}

impl<C: Clock> TokenBucket<C> {
    pub fn new(capacity: f64, per_second: f64, clock: C) -> Self {
        TokenBucket {
            capacity,
            per_second,
            clock,
            buckets: HashMap::new(),
        }
    }

    pub fn take(&mut self, key: &str) -> Decision {
        let now = self.clock.now();
        let (tokens, at) = self
            .buckets
            .get(key)
            .copied()
            .unwrap_or((self.capacity, now));
        let tokens = (tokens + (now - at).as_secs_f64() * self.per_second).min(self.capacity);
        if tokens >= 1.0 {
            self.buckets.insert(key.into(), (tokens - 1.0, now));
            Decision::Allowed
        } else {
            self.buckets.insert(key.into(), (tokens, now));
            Decision::Limited {
                retry_after_secs: ((1.0 - tokens) / self.per_second).ceil() as u64,
            }
        }
    }

    pub fn clock(&self) -> &C {
        &self.clock
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;

    struct FakeClock(Cell<Duration>);
    impl Clock for FakeClock {
        fn now(&self) -> Duration {
            self.0.get()
        }
    }

    #[test]
    fn burst_then_refill() {
        let mut bucket = TokenBucket::new(3.0, 0.5, FakeClock(Cell::new(Duration::ZERO)));
        for _ in 0..3 {
            assert_eq!(bucket.take("u1"), Decision::Allowed);
        }
        assert_eq!(
            bucket.take("u1"),
            Decision::Limited {
                retry_after_secs: 2
            }
        );
        assert_eq!(bucket.take("u2"), Decision::Allowed);
        bucket.clock().0.set(Duration::from_secs(2));
        assert_eq!(bucket.take("u1"), Decision::Allowed);
    }
}
```

**Lab:** `labs/backend-best-practices-rust/` — checked with Rust 1.96.

## 7. C and C++

Rarely the language for an HTTP API, but rate limiting turns up in any network service. C does it in **integer milli-tokens**, avoiding floating point; C++ makes the bucket **generic over a clock type**, so `std::chrono::steady_clock` in production and a test clock both fit.

```c
/* token_bucket.c — a token bucket in milli-tokens (integers, no floating point), with the
 * current time passed in by the caller. */
#include <assert.h>
#include <stdio.h>

typedef struct {
    long capacity_milli;     /* 3 tokens = 3000 */
    long refill_milli_per_s; /* 0.5 tokens/s = 500 */
    long tokens_milli;
    long at_ms;
} token_bucket;

/* Returns 0 if allowed; otherwise the seconds to wait. */
static long take(token_bucket *b, long now_ms) {
    long refilled = b->tokens_milli + (now_ms - b->at_ms) * b->refill_milli_per_s / 1000;
    b->tokens_milli = refilled < b->capacity_milli ? refilled : b->capacity_milli;
    b->at_ms = now_ms;
    if (b->tokens_milli >= 1000) {
        b->tokens_milli -= 1000;
        return 0;
    }
    long missing = 1000 - b->tokens_milli;
    return (missing * 1000 / b->refill_milli_per_s + 999) / 1000;   /* round up to whole seconds */
}

int main(void) {
    token_bucket b = {.capacity_milli = 3000, .refill_milli_per_s = 500, .tokens_milli = 3000, .at_ms = 0};
    assert(take(&b, 0) == 0 && take(&b, 0) == 0 && take(&b, 0) == 0);
    assert(take(&b, 0) == 2);       /* fourth request: wait 2 seconds */
    assert(take(&b, 2000) == 0);    /* refilled */
    puts("ok: integer token bucket");
    return 0;
}
```

```cpp
// token_bucket.cpp — a token bucket generic over its clock type, using std::chrono.
// Production uses std::chrono::steady_clock; the test uses a clock it can move.
#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <iostream>
#include <map>
#include <string>

using namespace std::chrono;

template <class Clock>
class TokenBucket {
public:
    TokenBucket(double capacity, double per_second) : capacity_(capacity), per_second_(per_second) {}

    // Returns 0 if allowed, otherwise whole seconds to wait.
    long take(const std::string& key) {
        const auto now = Clock::now();
        auto [it, fresh] = state_.try_emplace(key, State{capacity_, now});
        auto& s = it->second;
        const double elapsed = duration<double>(now - s.at).count();
        s.tokens = std::min(capacity_, s.tokens + elapsed * per_second_);
        s.at = now;
        if (s.tokens >= 1) { s.tokens -= 1; return 0; }
        return static_cast<long>(std::ceil((1 - s.tokens) / per_second_));
    }

private:
    struct State { double tokens; typename Clock::time_point at; };
    double capacity_, per_second_;
    std::map<std::string, State> state_;
};

// A test clock with the same interface as the standard clocks.
struct FakeClock {
    using duration = milliseconds;
    using time_point = std::chrono::time_point<FakeClock>;
    static inline time_point current{};
    static time_point now() { return current; }
};

int main() {
    TokenBucket<FakeClock> bucket(3, 0.5);
    assert(bucket.take("u1") == 0 && bucket.take("u1") == 0 && bucket.take("u1") == 0);
    assert(bucket.take("u1") == 2);
    assert(bucket.take("u2") == 0);
    FakeClock::current += seconds(2);
    assert(bucket.take("u1") == 0);
    std::cout << "ok: token bucket over a chrono clock type\n";
}
```

**Labs:** `labs/backend-best-practices-c/` and `labs/backend-best-practices-cpp/` — checked with GCC 16.

## 8. C#

ASP.NET Core has the most built in: `IExceptionHandler` and `ProblemDetails` for errors, `ILogger` scopes for request IDs, and a **rate limiter** in `System.Threading.RateLimiting`, wired with `AddRateLimiter` and `UseRateLimiter`. It **reads the real clock**: even with automatic replenishment off, `TryReplenish()` only adds tokens once a real period has passed — so the test below waits 150 ms. In a console app, add the `System.Threading.RateLimiting` package; ASP.NET Core includes it.

```csharp
using System.Threading.RateLimiting;

// Microsoft ships a token bucket in System.Threading.RateLimiting (included with ASP.NET Core).
// ASP.NET Core wraps it as middleware: builder.Services.AddRateLimiter(...) + app.UseRateLimiter().
static TokenBucketRateLimiter Limiter(TimeSpan period) => new(new TokenBucketRateLimiterOptions
{
    TokenLimit = 3,               // the burst
    TokensPerPeriod = 1,          // with a 2 s period: 0.5 tokens per second
    ReplenishmentPeriod = period,
    AutoReplenishment = false,    // no background timer; TryReplenish() refills
    QueueLimit = 0,               // refuse rather than queue
});

using var limiter = Limiter(TimeSpan.FromSeconds(2));
var results = Enumerable.Range(0, 4).Select(_ => limiter.AttemptAcquire().IsAcquired).ToList();
Check(results.SequenceEqual([true, true, true, false]), "three allowed, then refused");
using (var refused = limiter.AttemptAcquire())
{
    Check(refused.TryGetMetadata(MetadataName.RetryAfter, out var retryAfter) && retryAfter == TimeSpan.FromSeconds(2),
        "Retry-After is 2 seconds");
}

// The limiter reads the real clock: TryReplenish adds tokens only once a real period has passed.
// So a refill test has to wait — kept short here with a 100 ms period.
using var fast = Limiter(TimeSpan.FromMilliseconds(100));
for (var i = 0; i < 3; i++) fast.AttemptAcquire();
fast.TryReplenish();
Check(!fast.AttemptAcquire().IsAcquired, "no refill before the period has really passed");
Thread.Sleep(150);
fast.TryReplenish();
Check(fast.AttemptAcquire().IsAcquired, "refilled after the period");
Console.WriteLine("ok: the built-in TokenBucketRateLimiter");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }
```

**Lab:** `labs/backend-best-practices-csharp/` — runs in the .NET 10 SDK container. Finding this out took a probe: the first version assumed `TryReplenish()` refilled immediately, and the test failed.

## Check your understanding

1. Where does the request ID live in Python, Go, Java and C#, so every log line can include it?
2. Why is Go's `x/time/rate` easy to test, and .NET's `TokenBucketRateLimiter` not?
3. What is Java's MDC, and what's the Python equivalent?
4. Which framework validates request bodies from annotations, and which from type-annotated models?
5. Why does the C token bucket count milli-tokens?

<details>
<summary>Answers — after your attempt</summary>

1. Python: a `ContextVar`. Go: `context.Context`, read by a logging handler. Java: the MDC. C#: a logging scope (`ILogger.BeginScope`).
2. `x/time/rate`'s methods take the current time as an argument, so tests pass any time they like. The .NET limiter reads the system clock itself, so tests must actually wait for a period to pass.
3. A per-thread map of values added to every log line by the logging backend. Python's equivalent is a `ContextVar` read by a formatter or filter.
4. Annotations: Java's Bean Validation (and .NET's DataAnnotations). Type-annotated models: Python's Pydantic (as used by FastAPI).
5. To keep the arithmetic in integers — exact, and with no floating-point rounding — while still representing fractional tokens.

</details>

## Practice — independent task

**In your second language, on the flagship if it's written in it:** add the framework's own rate limiter to the most expensive route, a central error handler returning the main lesson's error contract, and JSON logs carrying a request ID from the language's context mechanism.

**Done when:** a test shows the fourth burst request refused with a `Retry-After` header, an unknown error returns the contract without internals, and two concurrent requests' log lines carry their own request IDs.

## Before moving on

You know your ecosystem's tools for errors, validation, logging and rate limiting, and how testable its rate limiter's clock is.

**Recap.** Go ships `slog` and maintains `x/time/rate`, which takes the time as an argument; .NET ships a rate limiter that reads the real clock; Spring has Bean Validation and the MDC; FastAPI has Pydantic; Rust has `tracing` and `governor`. Request IDs ride on each language's context mechanism.

**Next.** Back to the course: [[devops/10-observability/01-observability-fundamentals|observability fundamentals]].

## Related
- [[backend/07-practices/01-backend-best-practices|Backend best practices]] — the main lesson
- [[backend/03-structuring-a-backend/01b-layers-in-other-languages|Layers in other languages]] — error mapping per language
- [[backend/03-structuring-a-backend/05b-modular-monolith-in-other-languages|The modular monolith in other languages]] — idempotent consumers per language
