# Reliability and Plumbing in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]], which sorts failures into retryable and not, then builds backoff with jitter, a per-attempt timeout, a circuit breaker, a fallback and a token bucket in TypeScript. This page builds the same layers in Python, Go, Java, Rust and C#. Every lab runs **the same scenarios and gets the same numbers**: the same waits, the same breaker trace and the same five log lines when the layers meet an outage. What differs is how each language cancels a slow call and fakes the clock in tests, and that is most of what this page is about.

## Before you start

You can already:

- Explain retryable and permanent failures, full jitter, deadlines, the breaker's three states and the order of the layers → [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Name your ecosystem's library for retries and circuit breakers, and the one for rate limiting.
2. Cancel a slow call properly in your language, and say what happens to the request when you do.
3. Test code that waits for 30 seconds without the test taking 30 seconds.

## The kid version

Six families all have the same rule for a busy phone line: wait, then try again, waiting longer each time. They each use a different kitchen timer, and they each hang up differently. One family presses a button. Another unplugs the phone. A third says "please hang up" and hopes the person on the other end does. But give them all the same busy afternoon, and they should all make their calls at exactly the same moments.

**Where the analogy stops working.** Hanging up a phone always ends the call. In some languages, "cancelling" a call only asks it to stop, and a call that doesn't listen carries on in the background, still using the network and still costing money.

## 1. The tools, by ecosystem

| Language | Retries and breakers | Cancelling a call | Rate limiting | Fake clock in tests |
|---|---|---|---|---|
| TypeScript | the SDK's `maxRetries`; **cockatiel** (retry, breaker, timeout, bulkhead) | `AbortSignal`, passed to `fetch` | `p-limit` for concurrency; or by hand | inject a clock, or `node:test`'s `mock.timers` |
| Python | the SDK's `max_retries`; **tenacity** | `asyncio.timeout`; cancellation arrives at the next `await` | `aiolimiter` | inject a clock |
| Go | `cenkalti/backoff`, `sony/gobreaker` | `context.Context`, passed to every call | **`golang.org/x/time/rate`** | **`testing/synctest`**, built in |
| Java | **Resilience4j** (Retry, CircuitBreaker, TimeLimiter, RateLimiter, Bulkhead); Spring Retry | interrupt the thread | Resilience4j `RateLimiter` | inject a `Clock` |
| Rust | `backon`; **tower** layers (`Retry`, `Timeout`, `RateLimit`) | drop the future | **`governor`** | **tokio's paused time** (`start_paused`) |
| C# | **Polly**; `Microsoft.Extensions.Http.Resilience` | `CancellationToken` | `System.Threading.RateLimiting`, built in | `TimeProvider` with `FakeTimeProvider` |
| C, C++ | — | — | — | — |

In production, use the library in bold, or let your SDK or gateway do it: the labs write each layer by hand so you can see what the library does and check that it does it. Two things in the table matter more than the names.

**How cancelling works** decides whether a timeout really stops a request or only stops you waiting for it. Rust and Python cancel for real at the next `await`. Go and C# pass a token or context that the call is expected to check: a call that ignores it keeps running. Java interrupts a thread, which stops blocking I/O and sleeps.

**A fake clock** decides whether the breaker's 30-second cool-down can be tested in a millisecond. Go and Rust have one built in that works with the real time functions, so the code needs no clock parameter at all. The other languages pass a clock in.

There's no C or C++ section. Model calls are made by the application, and that is almost never written in C or C++. If it were, libcurl's `CURLOPT_TIMEOUT` (a total limit) and `CURLOPT_LOW_SPEED_TIME` (an idle limit) are the two timeouts from the main lesson's §4.

## 2. The same afternoon, in every language

Every lab asserts these results. If one language differs, it has a bug:

| Scenario | Expected in every language |
|---|---|
| retryable statuses | 408, 429, 500, 502, 503, 529, a timeout, no response |
| never retried | 400, 401, 403, 404, 422, and a bug in our own code |
| `Retry-After: 7` / a date 30 s ahead | 7000 ms / 30,000 ms |
| backoff ceilings, base 500 ms, cap 10 s | 500, 1000, 2000, 4000, 8000, 10,000 ms |
| 503 then 429 then success, jitter 0.5 | 3 calls, waits of 250 and 500 ms |
| a 400 | 1 call, no wait |
| 429 with `Retry-After: 7`, 3 attempts | 3 calls, waits of 7000 and 7000 ms |
| 503 forever, base 1 s, deadline 5 s | 3 calls, waits of 1000 and 2000 ms |
| breaker, threshold 3, cool-down 30 s | open after 3 failures; the 4th call isn't made; half-open at 30 s; a failed trial reopens it; a good trial closes it |
| all the layers, model down, threshold 4 | ticket 1: 3 calls then `billing` from the keywords; ticket 2: 1 call then `bug`; five identical log lines |
| token bucket, 3 tokens, 1 a second | six requests start at 0, 0, 0, 1000, 2000, 3000 ms |

The fallback in every lab is the evals lab's own keyword rules in that language, imported rather than copied, so there is one set of rules per language, as there is one golden set.

## Terms used in this lesson

1. **Cooperative cancellation**: This means a call is *asked* to stop, through a token, context or signal it is expected to check, and it stops only if it does check. Go's `context`, C#'s `CancellationToken` and JavaScript's `AbortSignal` work this way.
2. **Future**: In Rust, this is a value that represents work not yet done. It does nothing until it is awaited, and dropping it cancels the work.
3. **Interrupt**: In Java, this is a flag set on a thread that makes a blocking call in that thread, such as a sleep or a socket read, stop with an exception.
4. **Fake clock**: This is also called **virtual time**. It is a clock that tests control, so that a 30-second wait finishes instantly and time-dependent code gives the same result every run.
5. **Bubble**: In Go's `testing/synctest`, this is the group of goroutines a test starts. Inside it the clock is fake, and it jumps forward whenever every goroutine in the bubble is blocked.

## 3. Python

Python's `asyncio` cancels for real: when `asyncio.timeout` expires, the task gets a `CancelledError` at the `await` it is waiting on, and the request it was making stops. The test checks exactly that. Two Python details are worth knowing. **httpx**, which both the OpenAI and Anthropic Python SDKs use, splits its timeout into connect, read, write and pool, and its read timeout is per chunk: it is the idle timeout from the main lesson, so a slow stream never trips it. And **tenacity** is the usual retry library; its `wait_random_exponential` is the same full jitter as `backoff` here, and the test checks the ceilings match.

```python
"""Retry, timeout, circuit breaker, fallback and token bucket around an async model call.
The same behaviour, and the same numbers, as the TypeScript lab."""
import asyncio
import math
import random as _random
import time
from collections.abc import Awaitable, Callable
from email.utils import parsedate_to_datetime

Sleep = Callable[[float], Awaitable[None]]  # milliseconds


async def real_sleep(ms: float) -> None:
    await asyncio.sleep(ms / 1000)


def real_now() -> float:
    return time.monotonic() * 1000


class CallError(Exception):
    """A failed model call: the HTTP status, and the Retry-After wait if the server sent one."""

    def __init__(self, status: int, message: str = "", retry_after_ms: float | None = None):
        super().__init__(message or f"HTTP {status}")
        self.status = status
        self.retry_after_ms = retry_after_ms


class CircuitOpenError(Exception):
    pass


def is_retryable(error: BaseException) -> bool:
    if isinstance(error, CallError):
        return error.status in (408, 429) or error.status >= 500
    return isinstance(error, (TimeoutError, ConnectionError))  # our deadline fired, or no response at all


def parse_retry_after(header: str | None, now_s: float) -> float | None:
    """Seconds or an HTTP date, as milliseconds to wait. `now_s` is a Unix time in seconds."""
    if header is None or not header.strip():
        return None
    try:
        return max(0.0, float(header) * 1000)
    except ValueError:
        pass
    try:
        return max(0.0, (parsedate_to_datetime(header).timestamp() - now_s) * 1000)
    except (TypeError, ValueError):
        return None


def backoff(attempt: int, base_ms: float, cap_ms: float, random: Callable[[], float] = _random.random) -> int:
    """Full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1))."""
    return round(random() * min(cap_ms, base_ms * 2 ** (attempt - 1)))


async def with_retry[T](
    call: Callable[[int], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_ms: float = 500,
    cap_ms: float = 10_000,
    deadline_ms: float = math.inf,
    sleep: Sleep = real_sleep,
    random: Callable[[], float] = _random.random,
    now: Callable[[], float] = real_now,
    on_retry: Callable[[int, float, BaseException], None] | None = None,
) -> T:
    started = now()
    attempt = 1
    while True:
        try:
            return await call(attempt)
        except Exception as error:
            if not is_retryable(error) or attempt >= max_attempts:
                raise
            hinted = getattr(error, "retry_after_ms", None)
            wait = hinted if hinted is not None else backoff(attempt, base_ms, cap_ms, random)
            if now() - started + wait > deadline_ms:
                raise
            if on_retry:
                on_retry(attempt, wait, error)
            await sleep(wait)
            attempt += 1


async def with_timeout[T](call: Callable[[], Awaitable[T]], ms: float) -> T:
    """asyncio cancels the call at its next await when time runs out, and raises TimeoutError."""
    async with asyncio.timeout(ms / 1000):
        return await call()


class CircuitBreaker:
    def __init__(self, threshold: int = 5, cool_down_ms: float = 30_000, now: Callable[[], float] = real_now):
        self.threshold, self.cool_down_ms, self.now = threshold, cool_down_ms, now
        self.state, self.failures, self.opened_at, self.trial_running = "closed", 0, 0.0, False

    def current(self) -> str:
        if self.state == "open" and self.now() - self.opened_at >= self.cool_down_ms:
            self.state = "half-open"
        return self.state

    async def call[T](self, fn: Callable[[], Awaitable[T]]) -> T:
        state = self.current()
        if state == "open":
            raise CircuitOpenError("circuit open: not calling a dependency that keeps failing")
        if state == "half-open":
            if self.trial_running:
                raise CircuitOpenError("circuit half-open: one trial call is already running")
            self.trial_running = True
        try:
            result = await fn()
        except Exception as error:
            if is_retryable(error):  # a 400 is our bug, not the provider's outage
                self.failures += 1
                if state == "half-open" or self.failures >= self.threshold:
                    self.state, self.opened_at = "open", self.now()
            raise
        finally:
            if state == "half-open":
                self.trial_running = False
        self.state, self.failures = "closed", 0
        return result


async def first_that_works[T](
    options: list[tuple[str, Callable[[], Awaitable[T]]]],
    on_failure: Callable[[str, BaseException], None] = lambda name, error: None,
) -> tuple[str, T]:
    errors: list[Exception] = []
    for name, run in options:
        try:
            return name, await run()
        except Exception as error:
            if isinstance(error, CallError) and error.status in (400, 422):
                raise  # the request is wrong: every option would reject it
            on_failure(name, error)
            errors.append(error)
    raise ExceptionGroup(f"all {len(options)} options failed", errors)


class TokenBucket:
    def __init__(self, capacity: float, per_second: float, now: Callable[[], float] = real_now):
        self.capacity, self.per_second, self.now = capacity, per_second, now
        self.tokens, self.last = capacity, now()

    def try_take(self, cost: float = 1) -> int:
        if cost > self.capacity:
            raise ValueError(f"a cost of {cost} can never fit a bucket of {self.capacity}")
        elapsed = (self.now() - self.last) / 1000
        self.tokens = min(self.capacity, self.tokens + elapsed * self.per_second)
        self.last = self.now()
        if self.tokens >= cost:
            self.tokens -= cost
            return 0
        return math.ceil((cost - self.tokens) / self.per_second * 1000)

    async def take(self, cost: float = 1, sleep: Sleep = real_sleep) -> None:
        while (wait := self.try_take(cost)) > 0:
            await sleep(wait)


def describe(error: BaseException) -> str:
    return f"HTTP {error.status}" if isinstance(error, CallError) else type(error).__name__


def resilient(name: str, call: Callable[[str], Awaitable[str]], *, timeout_ms: float, retry: dict,
              breaker: CircuitBreaker, fallback: Callable[[str], Awaitable[str]] | None = None,
              log: Callable[[str], None] = lambda line: None):
    """fallback( retry( breaker( timeout( call ) ) ) ), as in the main lesson."""

    def retried(attempt: int, wait: float, error: BaseException) -> None:
        log(f"{name}: attempt {attempt} failed ({describe(error)}), retrying in {wait:g} ms")

    async def classify(text: str) -> tuple[str, str]:
        async def primary() -> str:
            return await with_retry(
                lambda _: breaker.call(lambda: with_timeout(lambda: call(text), timeout_ms)),
                on_retry=retried, **retry)

        options = [(name, primary)]
        if fallback:
            options.append(("fallback", lambda: fallback(text)))
        return await first_that_works(options, lambda by, error: log(f"{by}: gave up ({describe(error)})"))

    return classify
```

```python
import asyncio
import sys
import unittest
from pathlib import Path

from tenacity import RetryCallState, wait_exponential

from reliability import (CallError, CircuitBreaker, CircuitOpenError, TokenBucket, backoff, first_that_works,
                         is_retryable, parse_retry_after, resilient, with_retry, with_timeout)

sys.path.insert(0, str(Path(__file__).parents[3] / "12-evals" / "labs" / "python"))
from evals import keywords  # noqa: E402  the same keyword rules the evals lab scores


class FakeClock:
    """Sleeping moves time forward instantly, so tests about waiting take no time."""

    def __init__(self):
        self.t, self.slept = 0.0, []

    def now(self) -> float:
        return self.t

    async def sleep(self, ms: float) -> None:
        self.slept.append(ms)
        self.t += ms


def flaky(statuses: list[int], reply: str = "billing"):
    calls: list[int] = []

    async def run(*_):
        status = statuses[len(calls)] if len(calls) < len(statuses) else None
        calls.append(status or 200)
        if status:
            raise CallError(status)
        return reply

    return calls, run


class Reliability(unittest.IsolatedAsyncioTestCase):
    def test_only_failures_a_second_try_could_fix_are_retryable(self):
        for status in (408, 429, 500, 502, 503, 529):
            self.assertTrue(is_retryable(CallError(status)), status)
        for status in (400, 401, 403, 404, 422):
            self.assertFalse(is_retryable(CallError(status)), status)
        self.assertTrue(is_retryable(TimeoutError()))
        self.assertTrue(is_retryable(ConnectionRefusedError()))
        self.assertFalse(is_retryable(TypeError("a bug in our code")))

    def test_retry_after_comes_as_seconds_or_a_date(self):
        now = 1790942400.0  # 2026-10-02 12:00:00 UTC
        self.assertEqual(parse_retry_after("7", now), 7000)
        self.assertEqual(parse_retry_after("Fri, 02 Oct 2026 12:00:30 GMT", now), 30_000)
        self.assertIsNone(parse_retry_after(None, now))
        self.assertIsNone(parse_retry_after("soon", now))

    def test_backoff_ceilings_match_tenacity(self):
        top = lambda: 0.999999  # noqa: E731
        self.assertEqual([backoff(n, 500, 10_000, top) for n in range(1, 7)], [500, 1000, 2000, 4000, 8000, 10000])
        # tenacity's wait_random_exponential picks uniformly below exactly these ceilings (in seconds)
        ceiling = wait_exponential(multiplier=0.5, max=10)
        state = RetryCallState(None, None, (), {})
        ceilings = []
        for n in range(1, 7):
            state.attempt_number = n
            ceilings.append(ceiling(state) * 1000)
        self.assertEqual(ceilings, [500, 1000, 2000, 4000, 8000, 10000])

    async def test_a_transient_failure_is_retried_until_it_succeeds(self):
        clock = FakeClock()
        calls, run = flaky([503, 429])
        self.assertEqual(await with_retry(run, sleep=clock.sleep, now=clock.now, random=lambda: 0.5), "billing")
        self.assertEqual(calls, [503, 429, 200])
        self.assertEqual(clock.slept, [250, 500])

    async def test_a_400_fails_at_once(self):
        clock = FakeClock()
        calls, run = flaky([400])
        with self.assertRaises(CallError):
            await with_retry(run, sleep=clock.sleep, now=clock.now)
        self.assertEqual(len(calls), 1)

    async def test_retry_after_beats_our_guess_and_attempts_run_out(self):
        clock = FakeClock()
        calls = []

        async def limited(_):
            calls.append(1)
            raise CallError(429, "rate limited", 7000)

        with self.assertRaises(CallError):
            await with_retry(limited, sleep=clock.sleep, now=clock.now, max_attempts=3)
        self.assertEqual((len(calls), clock.slept), (3, [7000, 7000]))

    async def test_the_deadline_stops_a_wait_that_would_overrun_it(self):
        clock = FakeClock()
        calls, run = flaky([503] * 4)
        with self.assertRaises(CallError):
            await with_retry(run, sleep=clock.sleep, now=clock.now, random=lambda: 0.999999,
                             max_attempts=10, base_ms=1000, deadline_ms=5000)
        self.assertEqual((clock.slept, len(calls)), ([1000, 2000], 3))

    async def test_a_timeout_cancels_a_call_that_would_hang(self):
        cancelled = False

        async def hangs():
            nonlocal cancelled
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled = True
                raise

        with self.assertRaises(TimeoutError):
            await with_timeout(hangs, 20)
        self.assertTrue(cancelled)  # cancelled for real, at its await: no request left running

    async def test_the_breaker_opens_then_tests_recovery_with_one_trial(self):
        clock = FakeClock()
        breaker = CircuitBreaker(threshold=3, cool_down_ms=30_000, now=clock.now)
        calls, down = flaky([503] * 5)
        for _ in range(3):
            with self.assertRaises(CallError):
                await breaker.call(down)
        self.assertEqual(breaker.current(), "open")
        with self.assertRaises(CircuitOpenError):
            await breaker.call(down)
        self.assertEqual(len(calls), 3)
        clock.t += 30_000
        self.assertEqual(breaker.current(), "half-open")
        with self.assertRaises(CallError):
            await breaker.call(down)
        self.assertEqual(breaker.current(), "open")
        clock.t += 30_000

        async def ok():
            return "ok"

        self.assertEqual(await breaker.call(ok), "ok")
        self.assertEqual(breaker.current(), "closed")

    async def test_a_400_does_not_trip_the_breaker(self):
        breaker = CircuitBreaker(threshold=2)
        _, bad = flaky([400] * 3)
        for _ in range(3):
            with self.assertRaises(CallError):
                await breaker.call(bad)
        self.assertEqual(breaker.current(), "closed")

    async def test_fallback_tries_each_option_and_wont_hide_a_bad_request(self):
        failures = []
        result = await first_that_works([("primary", flaky([503])[1]), ("secondary", flaky([], "bug")[1])],
                                        lambda name, error: failures.append(f"{name}: {error.status}"))
        self.assertEqual((result, failures), (("secondary", "bug"), ["primary: 503"]))
        with self.assertRaises(CallError):
            await first_that_works([("primary", flaky([400])[1]), ("secondary", flaky([])[1])])
        with self.assertRaises(ExceptionGroup):
            await first_that_works([("only", flaky([503])[1])])

    async def test_all_the_layers_together(self):
        clock, lines = FakeClock(), []
        calls, run = flaky([503] * 20)

        async def fallback(text):
            return keywords(text)

        classify = resilient("model", run, timeout_ms=1000,
                             retry=dict(sleep=clock.sleep, now=clock.now, random=lambda: 0.5, max_attempts=3),
                             breaker=CircuitBreaker(threshold=4, now=clock.now), fallback=fallback, log=lines.append)
        self.assertEqual(await classify("I was charged twice."), ("fallback", "billing"))
        self.assertEqual(len(calls), 3)
        self.assertEqual(await classify("The app crashes on start."), ("fallback", "bug"))
        self.assertEqual(len(calls), 4)
        self.assertEqual(lines, [
            "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
            "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
            "model: gave up (HTTP 503)",
            "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
            "model: gave up (CircuitOpenError)",
        ])

    async def test_a_token_bucket_allows_a_burst_then_paces(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=3, per_second=1, now=clock.now)
        started = []
        for _ in range(6):
            await bucket.take(1, clock.sleep)
            started.append(clock.t)
        self.assertEqual(started, [0, 0, 0, 1000, 2000, 3000])
        with self.assertRaises(ValueError):
            bucket.try_take(5)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/13-reliability-and-plumbing/labs/python). `python3 labs/run.py reliability-and-plumbing/python` from the vault root.

## 4. Go

Go changes the design more than any other language here. **The deadline isn't an option; it's the context.** The caller makes a context with `context.WithTimeout(ctx, 5*time.Second)` and passes it down, and every layer reads the same deadline: `Retry` checks `ctx.Deadline()` before waiting, the sleep returns early when `ctx.Done()` closes, and each attempt gets a child context with its own shorter timeout. One subtlety follows: both the attempt's timeout and the caller's deadline produce `context.DeadlineExceeded`. The first is worth retrying and the second isn't, so `Retry` checks `ctx.Err()` (the caller's context) before deciding.

Go can't stop a goroutine from outside. A context is a request to stop, and `http.NewRequestWithContext` honours it by aborting the request. A call that ignores its context keeps running.

The tests use **`testing/synctest`**: inside `synctest.Test`, `time.Now`, `time.Sleep`, timers and context deadlines all use a fake clock that jumps forward whenever every goroutine is blocked. So the code uses the real time functions with no clock parameter, and the token-bucket test that "waits" three seconds runs in microseconds. Also notice the `sync.Mutex` in the breaker and the bucket: Go code is called from many goroutines at once, so shared state needs a lock. Methods can't take type parameters in Go, so the breaker's `Call` is a function.

```go
// Package reliability: retry, timeout, circuit breaker, fallback and token bucket around a model call,
// with the deadline carried by a context.Context instead of passed around as a number.
package reliability

import (
	"cmp"
	"context"
	"errors"
	"fmt"
	"math"
	"math/rand/v2"
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// CallError is a failed model call: its HTTP status, and the Retry-After wait if the server sent one.
type CallError struct {
	Status     int
	RetryAfter time.Duration // 0 when the server didn't say
}

func (e *CallError) Error() string { return fmt.Sprintf("HTTP %d", e.Status) }

// ErrCircuitOpen is returned without calling, while the breaker is open.
var ErrCircuitOpen = errors.New("circuit open: not calling a dependency that keeps failing")

// IsRetryable: could the same request succeed if sent again?
func IsRetryable(err error) bool {
	if ce, ok := errors.AsType[*CallError](err); ok {
		return ce.Status == 408 || ce.Status == 429 || ce.Status >= 500
	}
	if errors.Is(err, context.DeadlineExceeded) {
		return true // one attempt's own timeout; Retry checks separately whether the caller's deadline has passed
	}
	_, noResponse := errors.AsType[*net.OpError](err) // DNS, refused, reset
	return noResponse
}

// ParseRetryAfter reads seconds or an HTTP date. ok is false when there is no usable value.
func ParseRetryAfter(header string, now time.Time) (wait time.Duration, ok bool) {
	header = strings.TrimSpace(header)
	if header == "" {
		return 0, false
	}
	if seconds, err := strconv.ParseFloat(header, 64); err == nil {
		return max(0, time.Duration(seconds*float64(time.Second))), true
	}
	if date, err := http.ParseTime(header); err == nil {
		return max(0, date.Sub(now)), true
	}
	return 0, false
}

// Backoff is full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)).
func Backoff(attempt int, base, cap time.Duration, random func() float64) time.Duration {
	ceiling := math.Min(float64(cap), float64(base)*math.Pow(2, float64(attempt-1)))
	return time.Duration(math.Round(random()*ceiling/1e6)) * time.Millisecond // whole milliseconds, as in the other labs
}

type RetryOptions struct {
	MaxAttempts int // every try, including the first
	Base, Cap   time.Duration
	Random      func() float64
	OnRetry     func(attempt int, wait time.Duration, err error)
}

// Retry calls until success, a permanent error, the attempt limit, or the context's deadline.
// The deadline isn't an option: it's whatever deadline the caller's context carries.
func Retry[T any](ctx context.Context, o RetryOptions, call func(ctx context.Context, attempt int) (T, error)) (T, error) {
	o.MaxAttempts = cmp.Or(o.MaxAttempts, 3)
	o.Base, o.Cap = cmp.Or(o.Base, 500*time.Millisecond), cmp.Or(o.Cap, 10*time.Second)
	if o.Random == nil {
		o.Random = rand.Float64
	}
	for attempt := 1; ; attempt++ {
		result, err := call(ctx, attempt)
		if err == nil || ctx.Err() != nil || !IsRetryable(err) || attempt >= o.MaxAttempts {
			return result, err
		}
		wait := Backoff(attempt, o.Base, o.Cap, o.Random)
		if ce, ok := errors.AsType[*CallError](err); ok && ce.RetryAfter > 0 {
			wait = ce.RetryAfter // the server knows best
		}
		if deadline, ok := ctx.Deadline(); ok && time.Now().Add(wait).After(deadline) {
			return result, err // waiting would blow the deadline: fail now
		}
		if o.OnRetry != nil {
			o.OnRetry(attempt, wait, err)
		}
		if err := sleep(ctx, wait); err != nil {
			return result, err
		}
	}
}

func sleep(ctx context.Context, d time.Duration) error {
	timer := time.NewTimer(d)
	defer timer.Stop()
	select {
	case <-timer.C:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// WithTimeout gives one attempt its own deadline. Go can't stop a goroutine from outside, so the
// call must honour ctx — http.NewRequestWithContext does, and aborts the request when it expires.
func WithTimeout[T any](ctx context.Context, d time.Duration, call func(ctx context.Context) (T, error)) (T, error) {
	ctx, cancel := context.WithTimeout(ctx, d)
	defer cancel()
	return call(ctx)
}

type Breaker struct {
	Threshold int
	CoolDown  time.Duration

	mu           sync.Mutex // many goroutines share one breaker
	state        string
	failures     int
	openedAt     time.Time
	trialRunning bool
}

func (b *Breaker) Current() string {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.current()
}

func (b *Breaker) current() string {
	if b.state == "" {
		b.state = "closed"
	}
	if b.state == "open" && time.Since(b.openedAt) >= b.CoolDown {
		b.state = "half-open"
	}
	return b.state
}

// Call runs fn unless the breaker is open. A free function because Go methods can't have type parameters.
func Call[T any](b *Breaker, fn func() (T, error)) (T, error) {
	var zero T
	b.mu.Lock()
	state := b.current()
	if state == "open" || (state == "half-open" && b.trialRunning) {
		b.mu.Unlock()
		return zero, ErrCircuitOpen
	}
	if state == "half-open" {
		b.trialRunning = true
	}
	b.mu.Unlock()

	result, err := fn()

	b.mu.Lock()
	defer b.mu.Unlock()
	if state == "half-open" {
		b.trialRunning = false
	}
	switch {
	case err == nil:
		b.state, b.failures = "closed", 0
	case IsRetryable(err): // a 400 is our bug, not the provider's outage
		b.failures++
		if state == "half-open" || b.failures >= b.Threshold {
			b.state, b.openedAt = "open", time.Now()
		}
	}
	return result, err
}

type Option[T any] struct {
	Name string
	Run  func(ctx context.Context) (T, error)
}

// FirstThatWorks tries each option in turn. A 400 or 422 is returned at once: every option would reject it.
func FirstThatWorks[T any](ctx context.Context, options []Option[T], onFailure func(name string, err error)) (string, T, error) {
	var errs []error
	for _, o := range options {
		value, err := o.Run(ctx)
		if err == nil {
			return o.Name, value, nil
		}
		if ce, ok := errors.AsType[*CallError](err); ok && (ce.Status == 400 || ce.Status == 422) {
			return "", value, err
		}
		if onFailure != nil {
			onFailure(o.Name, err)
		}
		errs = append(errs, err)
	}
	var zero T
	return "", zero, fmt.Errorf("all %d options failed: %w", len(options), errors.Join(errs...))
}

// TokenBucket paces requests under a rate limit. golang.org/x/time/rate is the production version.
type TokenBucket struct {
	mu        sync.Mutex
	capacity  float64
	perSecond float64
	tokens    float64
	last      time.Time
}

func NewTokenBucket(capacity, perSecond float64) *TokenBucket {
	return &TokenBucket{capacity: capacity, perSecond: perSecond, tokens: capacity, last: time.Now()}
}

// TryTake takes cost tokens and returns 0, or takes nothing and returns how long until there are enough.
func (b *TokenBucket) TryTake(cost float64) (time.Duration, error) {
	if cost > b.capacity {
		return 0, fmt.Errorf("a cost of %g can never fit a bucket of %g", cost, b.capacity)
	}
	b.mu.Lock()
	defer b.mu.Unlock()
	now := time.Now()
	b.tokens = min(b.capacity, b.tokens+now.Sub(b.last).Seconds()*b.perSecond)
	b.last = now
	if b.tokens >= cost {
		b.tokens -= cost
		return 0, nil
	}
	return time.Duration(math.Ceil((cost-b.tokens)/b.perSecond*1000)) * time.Millisecond, nil
}

func (b *TokenBucket) Take(ctx context.Context, cost float64) error {
	for {
		wait, err := b.TryTake(cost)
		if err != nil || wait == 0 {
			return err
		}
		if err := sleep(ctx, wait); err != nil {
			return err
		}
	}
}

type Layers struct {
	Timeout  time.Duration
	Retry    RetryOptions
	Breaker  *Breaker
	Fallback func(input string) (string, error)
	Log      func(line string)
}

// Resilient wraps call as fallback( retry( breaker( timeout( call ) ) ) ).
func Resilient(name string, call func(ctx context.Context, input string) (string, error), l Layers) func(ctx context.Context, input string) (string, string, error) {
	log := l.Log
	if log == nil {
		log = func(string) {}
	}
	retry := l.Retry
	retry.OnRetry = func(attempt int, wait time.Duration, err error) {
		log(fmt.Sprintf("%s: attempt %d failed (%s), retrying in %d ms", name, attempt, describe(err), wait.Milliseconds()))
	}
	return func(ctx context.Context, input string) (string, string, error) {
		options := []Option[string]{{Name: name, Run: func(ctx context.Context) (string, error) {
			return Retry(ctx, retry, func(ctx context.Context, _ int) (string, error) {
				return Call(l.Breaker, func() (string, error) {
					return WithTimeout(ctx, l.Timeout, func(ctx context.Context) (string, error) { return call(ctx, input) })
				})
			})
		}}}
		if l.Fallback != nil {
			options = append(options, Option[string]{Name: "fallback", Run: func(context.Context) (string, error) { return l.Fallback(input) }})
		}
		return FirstThatWorks(ctx, options, func(by string, err error) { log(fmt.Sprintf("%s: gave up (%s)", by, describe(err))) })
	}
}

func describe(err error) string {
	if ce, ok := errors.AsType[*CallError](err); ok {
		return ce.Error()
	}
	if errors.Is(err, ErrCircuitOpen) {
		return "CircuitOpenError"
	}
	return err.Error()
}
```

```go
package reliability

import (
	"context"
	"errors"
	"net"
	"slices"
	"testing"
	"testing/synctest"
	"time"

	"evals" // the evals lab's keyword rules, as the fallback
)

const ms = time.Millisecond

// flaky fails with each status in turn, then answers.
type flaky struct {
	statuses []int
	reply    string
	calls    []int
}

func (f *flaky) run(context.Context) (string, error) {
	if i := len(f.calls); i < len(f.statuses) {
		f.calls = append(f.calls, f.statuses[i])
		return "", &CallError{Status: f.statuses[i]}
	}
	f.calls = append(f.calls, 200)
	return f.reply, nil
}

func half() float64 { return 0.5 }
func top() float64  { return 0.999999 }

func TestOnlyFailuresASecondTryCouldFixAreRetryable(t *testing.T) {
	for _, s := range []int{408, 429, 500, 502, 503, 529} {
		if !IsRetryable(&CallError{Status: s}) {
			t.Errorf("%d should be retryable", s)
		}
	}
	for _, s := range []int{400, 401, 403, 404, 422} {
		if IsRetryable(&CallError{Status: s}) {
			t.Errorf("%d should not be retryable", s)
		}
	}
	if !IsRetryable(context.DeadlineExceeded) || !IsRetryable(&net.OpError{Op: "dial", Err: errors.New("refused")}) {
		t.Error("timeouts and connection failures should be retryable")
	}
	if IsRetryable(errors.New("a bug in our code")) {
		t.Error("an unknown error should not be retried")
	}
}

func TestRetryAfterComesAsSecondsOrADate(t *testing.T) {
	now := time.Date(2026, 10, 2, 12, 0, 0, 0, time.UTC)
	if w, _ := ParseRetryAfter("7", now); w != 7000*ms {
		t.Errorf("got %v", w)
	}
	if w, _ := ParseRetryAfter("Fri, 02 Oct 2026 12:00:30 GMT", now); w != 30_000*ms {
		t.Errorf("got %v", w)
	}
	if _, ok := ParseRetryAfter("soon", now); ok {
		t.Error("nonsense should give no wait")
	}
}

func TestBackoffCeilingsDoubleUpToACap(t *testing.T) {
	var got []time.Duration
	for n := 1; n <= 6; n++ {
		got = append(got, Backoff(n, 500*ms, 10*time.Second, top))
	}
	want := []time.Duration{500 * ms, 1000 * ms, 2000 * ms, 4000 * ms, 8000 * ms, 10000 * ms}
	if !slices.Equal(got, want) {
		t.Errorf("got %v", got)
	}
}

// Inside a synctest bubble the clock is fake: time only moves when every goroutine is blocked,
// and then it jumps straight to the next timer. Real time.Sleep, real contexts, no waiting.
func TestATransientFailureIsRetriedUntilItSucceeds(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		start := time.Now()
		model := &flaky{statuses: []int{503, 429}, reply: "billing"}
		var slept []time.Duration
		reply, err := Retry(t.Context(), RetryOptions{Random: half, OnRetry: func(_ int, w time.Duration, _ error) { slept = append(slept, w) }},
			func(ctx context.Context, _ int) (string, error) { return model.run(ctx) })
		if err != nil || reply != "billing" || !slices.Equal(model.calls, []int{503, 429, 200}) {
			t.Fatalf("got %q %v %v", reply, err, model.calls)
		}
		if !slices.Equal(slept, []time.Duration{250 * ms, 500 * ms}) || time.Since(start) != 750*ms {
			t.Errorf("slept %v, elapsed %v", slept, time.Since(start))
		}
	})
}

func TestA400FailsAtOnce(t *testing.T) {
	model := &flaky{statuses: []int{400}}
	_, err := Retry(t.Context(), RetryOptions{}, func(ctx context.Context, _ int) (string, error) { return model.run(ctx) })
	if ce, ok := errors.AsType[*CallError](err); !ok || ce.Status != 400 || len(model.calls) != 1 {
		t.Errorf("got %v after %d calls", err, len(model.calls))
	}
}

func TestRetryAfterBeatsOurGuessAndAttemptsRunOut(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		start, calls := time.Now(), 0
		_, err := Retry(t.Context(), RetryOptions{MaxAttempts: 3}, func(context.Context, int) (string, error) {
			calls++
			return "", &CallError{Status: 429, RetryAfter: 7 * time.Second}
		})
		if err == nil || calls != 3 || time.Since(start) != 14*time.Second {
			t.Errorf("err %v, %d calls, %v", err, calls, time.Since(start))
		}
	})
}

func TestTheDeadlineStopsAWaitThatWouldOverrunIt(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		ctx, cancel := context.WithTimeout(t.Context(), 5*time.Second) // the caller's deadline travels in ctx
		defer cancel()
		start, model := time.Now(), &flaky{statuses: []int{503, 503, 503, 503}}
		_, err := Retry(ctx, RetryOptions{MaxAttempts: 10, Base: time.Second, Random: top},
			func(ctx context.Context, _ int) (string, error) { return model.run(ctx) })
		if err == nil || len(model.calls) != 3 || time.Since(start) != 3*time.Second {
			t.Errorf("err %v, %d calls, %v", err, len(model.calls), time.Since(start)) // slept 1 s + 2 s; 4 s more would pass 5 s
		}
	})
}

func TestATimeoutCancelsACallThatWouldHang(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		hangs := func(ctx context.Context) (string, error) {
			<-ctx.Done() // a well-behaved call: it gives up when its context does
			return "", ctx.Err()
		}
		if _, err := WithTimeout(t.Context(), 20*ms, hangs); !errors.Is(err, context.DeadlineExceeded) {
			t.Errorf("got %v", err)
		}
	})
}

func TestTheBreakerOpensThenTestsRecoveryWithOneTrial(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		b := &Breaker{Threshold: 3, CoolDown: 30 * time.Second}
		down := &flaky{statuses: []int{503, 503, 503, 503, 503}}
		run := func() (string, error) { return down.run(t.Context()) }
		for range 3 {
			Call(b, run)
		}
		if _, err := Call(b, run); b.Current() != "open" || !errors.Is(err, ErrCircuitOpen) || len(down.calls) != 3 {
			t.Fatalf("state %s, err %v, %d calls", b.Current(), err, len(down.calls))
		}
		time.Sleep(30 * time.Second)
		if b.Current() != "half-open" {
			t.Fatal(b.Current())
		}
		if Call(b, run); b.Current() != "open" {
			t.Fatal("a failed trial should open it again")
		}
		time.Sleep(30 * time.Second)
		if reply, _ := Call(b, func() (string, error) { return "ok", nil }); reply != "ok" || b.Current() != "closed" {
			t.Fatal("a good trial should close it")
		}
	})
}

func TestA400DoesNotTripTheBreaker(t *testing.T) {
	b := &Breaker{Threshold: 2, CoolDown: time.Minute}
	bad := &flaky{statuses: []int{400, 400, 400}}
	for range 3 {
		Call(b, func() (string, error) { return bad.run(t.Context()) })
	}
	if b.Current() != "closed" {
		t.Error(b.Current())
	}
}

func TestFallbackTriesEachOptionAndWontHideABadRequest(t *testing.T) {
	var failures []string
	by, value, err := FirstThatWorks(t.Context(), []Option[string]{
		{"primary", (&flaky{statuses: []int{503}}).run},
		{"secondary", (&flaky{reply: "bug"}).run},
	}, func(name string, err error) { failures = append(failures, name+": "+err.Error()) })
	if by != "secondary" || value != "bug" || err != nil || !slices.Equal(failures, []string{"primary: HTTP 503"}) {
		t.Errorf("%s %s %v %v", by, value, err, failures)
	}
	_, _, err = FirstThatWorks(t.Context(), []Option[string]{{"primary", (&flaky{statuses: []int{400}}).run}, {"secondary", (&flaky{}).run}}, nil)
	if ce, ok := errors.AsType[*CallError](err); !ok || ce.Status != 400 {
		t.Errorf("a 400 should come straight back, got %v", err)
	}
}

func TestAllTheLayersTogether(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		var lines []string
		model := &flaky{statuses: slices.Repeat([]int{503}, 20)}
		classify := Resilient("model", func(ctx context.Context, _ string) (string, error) { return model.run(ctx) }, Layers{
			Timeout:  time.Second,
			Retry:    RetryOptions{Random: half, MaxAttempts: 3},
			Breaker:  &Breaker{Threshold: 4, CoolDown: 30 * time.Second},
			Fallback: evals.Keywords,
			Log:      func(line string) { lines = append(lines, line) },
		})
		if by, label, _ := classify(t.Context(), "I was charged twice."); by != "fallback" || label != "billing" || len(model.calls) != 3 {
			t.Fatalf("%s %s after %d calls", by, label, len(model.calls))
		}
		if by, label, _ := classify(t.Context(), "The app crashes on start."); by != "fallback" || label != "bug" || len(model.calls) != 4 {
			t.Fatalf("%s %s after %d calls", by, label, len(model.calls))
		}
		want := []string{
			"model: attempt 1 failed (HTTP 503), retrying in 250 ms",
			"model: attempt 2 failed (HTTP 503), retrying in 500 ms",
			"model: gave up (HTTP 503)",
			"model: attempt 1 failed (HTTP 503), retrying in 250 ms",
			"model: gave up (CircuitOpenError)",
		}
		if !slices.Equal(lines, want) {
			t.Errorf("got %q", lines)
		}
	})
}

func TestATokenBucketAllowsABurstThenPaces(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		start, bucket := time.Now(), NewTokenBucket(3, 1)
		var started []time.Duration
		for range 6 {
			bucket.Take(t.Context(), 1)
			started = append(started, time.Since(start))
		}
		if !slices.Equal(started, []time.Duration{0, 0, 0, 1000 * ms, 2000 * ms, 3000 * ms}) {
			t.Errorf("got %v", started)
		}
		if _, err := bucket.TryTake(5); err == nil {
			t.Error("a cost bigger than the bucket should be an error")
		}
	})
}
```

`go.mod` imports the evals lab with a `replace` directive, `replace evals => ../../../12-evals/labs/go`, so `evals.Keywords` is the same function the evals lab tests.

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/13-reliability-and-plumbing/labs/go). `python3 labs/run.py reliability-and-plumbing/go`.

## 5. Java

Java's version is **blocking, and that is fine**. Since Java 21, virtual threads make a thread that sleeps between retries almost free, so a plain loop with `Thread.sleep` is the simple, correct design, and there's no need for `CompletableFuture` chains. The timeout runs the attempt on a virtual thread and waits for it with a limit; when the limit passes, it **interrupts** the thread, which stops a blocking `HttpClient.send` or a sleep with an exception. The check waits for that interrupt with a latch, rather than hoping it happened.

Java's exceptions also sort neatly with a pattern-matching `switch`: `CallError`, `TimeoutException`, `HttpTimeoutException` (from `HttpClient`'s own request timeout) and `ConnectException` each get a line. In production, **Resilience4j** provides each layer as a decorator, and its documentation describes the same order of layers as the main lesson.

```java
package reliability;

import java.net.ConnectException;
import java.net.http.HttpTimeoutException;
import java.time.Duration;
import java.time.Instant;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.function.BiConsumer;
import java.util.function.Consumer;
import java.util.function.DoubleSupplier;
import java.util.function.UnaryOperator;

/** Retry, timeout, circuit breaker, fallback and token bucket around a blocking model call.
 *  Blocking is fine: on a virtual thread, a sleeping retry loop costs almost nothing. */
public final class Reliability {
    private Reliability() {}

    /** Time, so tests can replace it. Milliseconds throughout. */
    public interface Clock {
        long nowMs();

        void sleep(long ms) throws InterruptedException;

        Clock REAL = new Clock() {
            public long nowMs() { return System.nanoTime() / 1_000_000; }

            public void sleep(long ms) throws InterruptedException { Thread.sleep(ms); }
        };
    }

    /** A failed model call: the HTTP status, and the Retry-After wait if the server sent one. */
    public static final class CallError extends RuntimeException {
        public final int status;
        public final Long retryAfterMs;

        public CallError(int status, Long retryAfterMs) {
            super("HTTP " + status);
            this.status = status;
            this.retryAfterMs = retryAfterMs;
        }

        public CallError(int status) { this(status, null); }
    }

    public static final class CircuitOpenError extends RuntimeException {
        public CircuitOpenError(String message) { super(message); }
    }

    public static boolean isRetryable(Throwable error) {
        return switch (error) {
            case CallError e -> e.status == 408 || e.status == 429 || e.status >= 500;
            case TimeoutException e -> true;      // our own deadline for one attempt
            case HttpTimeoutException e -> true;  // HttpClient's request timeout
            case ConnectException e -> true;      // no response at all
            default -> false;
        };
    }

    /** Seconds or an HTTP date, as milliseconds to wait. */
    public static Optional<Long> parseRetryAfter(String header, Instant now) {
        if (header == null || header.isBlank()) return Optional.empty();
        try {
            return Optional.of(Math.max(0, Math.round(Double.parseDouble(header.trim()) * 1000)));
        } catch (NumberFormatException notSeconds) {
            try {
                Instant date = ZonedDateTime.parse(header.trim(), DateTimeFormatter.RFC_1123_DATE_TIME).toInstant();
                return Optional.of(Math.max(0, Duration.between(now, date).toMillis()));
            } catch (DateTimeParseException notADate) {
                return Optional.empty();
            }
        }
    }

    /** Full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)). */
    public static long backoff(int attempt, long baseMs, long capMs, DoubleSupplier random) {
        return Math.round(random.getAsDouble() * Math.min(capMs, baseMs * Math.pow(2, attempt - 1)));
    }

    public record RetryOptions(int maxAttempts, long baseMs, long capMs, long deadlineMs, Clock clock, DoubleSupplier random) {
        public static RetryOptions defaults(Clock clock, DoubleSupplier random) {
            return new RetryOptions(3, 500, 10_000, Long.MAX_VALUE, clock, random);
        }

        public RetryOptions withMaxAttempts(int n) { return new RetryOptions(n, baseMs, capMs, deadlineMs, clock, random); }

        public RetryOptions withDeadline(long baseMs, long deadlineMs) {
            return new RetryOptions(maxAttempts, baseMs, capMs, deadlineMs, clock, random);
        }
    }

    public interface Attempt<T> {
        T call(int attempt) throws Exception;
    }

    public interface OnRetry {
        void retrying(int attempt, long waitMs, Exception error);
    }

    public static <T> T withRetry(Attempt<T> call, RetryOptions o, OnRetry onRetry) throws Exception {
        long started = o.clock().nowMs();
        for (int attempt = 1; ; attempt++) {
            try {
                return call.call(attempt);
            } catch (Exception error) {
                if (!isRetryable(error) || attempt >= o.maxAttempts()) throw error;
                long wait = error instanceof CallError e && e.retryAfterMs != null
                        ? e.retryAfterMs // the server knows best
                        : backoff(attempt, o.baseMs(), o.capMs(), o.random());
                if (o.clock().nowMs() - started + wait > o.deadlineMs()) throw error;
                if (onRetry != null) onRetry.retrying(attempt, wait, error);
                o.clock().sleep(wait);
            }
        }
    }

    /** One attempt on its own virtual thread. When time runs out, the thread is interrupted, which
     *  aborts a blocking HttpClient.send, and the caller gets a TimeoutException. */
    public static <T> T withTimeout(Callable<T> call, long ms) throws Exception {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<T> future = executor.submit(call);
            try {
                return future.get(ms, TimeUnit.MILLISECONDS);
            } catch (TimeoutException e) {
                future.cancel(true);
                throw new TimeoutException("timed out after " + ms + " ms");
            } catch (ExecutionException e) {
                throw e.getCause() instanceof Exception cause ? cause : e;
            }
        }
    }

    public static final class Breaker {
        private final int threshold;
        private final long coolDownMs;
        private final Clock clock;
        private String state = "closed";
        private int failures;
        private long openedAt;
        private boolean trialRunning;

        public Breaker(int threshold, long coolDownMs, Clock clock) {
            this.threshold = threshold;
            this.coolDownMs = coolDownMs;
            this.clock = clock;
        }

        public synchronized String current() {
            if (state.equals("open") && clock.nowMs() - openedAt >= coolDownMs) state = "half-open";
            return state;
        }

        public <T> T call(Callable<T> fn) throws Exception {
            String before;
            synchronized (this) {
                before = current();
                if (before.equals("open") || (before.equals("half-open") && trialRunning))
                    throw new CircuitOpenError("circuit open: not calling a dependency that keeps failing");
                if (before.equals("half-open")) trialRunning = true;
            }
            try {
                T result = fn.call();
                synchronized (this) {
                    state = "closed";
                    failures = 0;
                }
                return result;
            } catch (Exception error) {
                synchronized (this) {
                    if (isRetryable(error)) { // a 400 is our bug, not the provider's outage
                        failures++;
                        if (before.equals("half-open") || failures >= threshold) {
                            state = "open";
                            openedAt = clock.nowMs();
                        }
                    }
                }
                throw error;
            } finally {
                if (before.equals("half-open")) synchronized (this) { trialRunning = false; }
            }
        }
    }

    public record Option<T>(String name, Callable<T> run) {}

    public record Answer<T>(String by, T value) {}

    public static <T> Answer<T> firstThatWorks(List<Option<T>> options, BiConsumer<String, Exception> onFailure) throws Exception {
        var failed = new RuntimeException("all " + options.size() + " options failed");
        for (Option<T> option : options) {
            try {
                return new Answer<>(option.name(), option.run().call());
            } catch (Exception error) {
                if (error instanceof CallError e && (e.status == 400 || e.status == 422)) throw error;
                onFailure.accept(option.name(), error);
                failed.addSuppressed(error);
            }
        }
        throw failed;
    }

    /** Resilience4j's RateLimiter is the production version of this. */
    public static final class TokenBucket {
        private final double capacity, perSecond;
        private final Clock clock;
        private double tokens;
        private long last;

        public TokenBucket(double capacity, double perSecond, Clock clock) {
            this.capacity = capacity;
            this.perSecond = perSecond;
            this.clock = clock;
            this.tokens = capacity;
            this.last = clock.nowMs();
        }

        public synchronized long tryTake(double cost) {
            if (cost > capacity) throw new IllegalArgumentException("a cost of " + cost + " can never fit a bucket of " + capacity);
            tokens = Math.min(capacity, tokens + (clock.nowMs() - last) / 1000.0 * perSecond);
            last = clock.nowMs();
            if (tokens >= cost) {
                tokens -= cost;
                return 0;
            }
            return (long) Math.ceil((cost - tokens) / perSecond * 1000);
        }

        public void take(double cost) throws InterruptedException {
            for (long wait = tryTake(cost); wait > 0; wait = tryTake(cost)) clock.sleep(wait);
        }
    }

    public interface ModelCall {
        String call(String input) throws Exception;
    }

    /** fallback( retry( breaker( timeout( call ) ) ) ), as in the main lesson. */
    public static Answer<String> resilient(String name, ModelCall call, long timeoutMs, RetryOptions retry, Breaker breaker,
                                           UnaryOperator<String> fallback, Consumer<String> log, String input) throws Exception {
        var options = new ArrayList<Option<String>>();
        options.add(new Option<>(name, () -> withRetry(
                attempt -> breaker.call(() -> withTimeout(() -> call.call(input), timeoutMs)), retry,
                (attempt, wait, error) -> log.accept(name + ": attempt " + attempt + " failed (" + describe(error) + "), retrying in " + wait + " ms"))));
        if (fallback != null) options.add(new Option<>("fallback", () -> fallback.apply(input)));
        return firstThatWorks(options, (by, error) -> log.accept(by + ": gave up (" + describe(error) + ")"));
    }

    static String describe(Exception error) {
        return error instanceof CallError e ? "HTTP " + e.status : error.getClass().getSimpleName();
    }
}
```

```java
package reliability;

import evals.Evals;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import reliability.Reliability.*;

/** Checks, run with `java -ea`. The same scenarios and numbers as every other language. */
public final class ReliabilityCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    /** Sleeping moves time forward instantly, so tests about waiting take no time. */
    static final class FakeClock implements Clock {
        long t;
        final List<Long> slept = new ArrayList<>();

        public long nowMs() { return t; }

        public void sleep(long ms) {
            slept.add(ms);
            t += ms;
        }
    }

    /** Fails with each status in turn, then answers. */
    static final class Flaky {
        final List<Integer> statuses, calls = new ArrayList<>();
        final String reply;

        Flaky(String reply, Integer... statuses) {
            this.reply = reply;
            this.statuses = List.of(statuses);
        }

        String run() {
            if (calls.size() < statuses.size()) {
                int status = statuses.get(calls.size());
                calls.add(status);
                throw new CallError(status);
            }
            calls.add(200);
            return reply;
        }
    }

    static <T> Exception thrown(Attempt<T> body) {
        try {
            body.call(0);
        } catch (Exception e) {
            return e;
        }
        throw new AssertionError("expected an exception");
    }

    public static void main(String[] args) throws Exception {
        for (int s : new int[] {408, 429, 500, 502, 503, 529}) check(Reliability.isRetryable(new CallError(s)), s);
        for (int s : new int[] {400, 401, 403, 404, 422}) check(!Reliability.isRetryable(new CallError(s)), s);
        check(Reliability.isRetryable(new TimeoutException()) && !Reliability.isRetryable(new IllegalStateException("bug")), "timeouts");

        Instant now = Instant.parse("2026-10-02T12:00:00Z");
        check(Reliability.parseRetryAfter("7", now).orElseThrow() == 7000, "seconds");
        check(Reliability.parseRetryAfter("Fri, 02 Oct 2026 12:00:30 GMT", now).orElseThrow() == 30_000, "date");
        check(Reliability.parseRetryAfter("soon", now).isEmpty(), "nonsense");

        var ceilings = new ArrayList<Long>();
        for (int n = 1; n <= 6; n++) ceilings.add(Reliability.backoff(n, 500, 10_000, () -> 0.999999));
        check(ceilings.equals(List.of(500L, 1000L, 2000L, 4000L, 8000L, 10000L)), ceilings);

        // a transient failure is retried until it succeeds
        var clock = new FakeClock();
        var model = new Flaky("billing", 503, 429);
        check(Reliability.withRetry(a -> model.run(), RetryOptions.defaults(clock, () -> 0.5), null).equals("billing"), "reply");
        check(model.calls.equals(List.of(503, 429, 200)) && clock.slept.equals(List.of(250L, 500L)), clock.slept);

        // a 400 fails at once
        var bad = new Flaky("", 400);
        check(thrown(a -> Reliability.withRetry(b -> bad.run(), RetryOptions.defaults(new FakeClock(), () -> 0.5), null)) instanceof CallError e
                && e.status == 400 && bad.calls.size() == 1, bad.calls);

        // Retry-After beats our guess, and the attempts run out
        var limitedClock = new FakeClock();
        var limitedCalls = new ArrayList<Integer>();
        thrown(a -> Reliability.withRetry(b -> {
            limitedCalls.add(429);
            throw new CallError(429, 7000L);
        }, RetryOptions.defaults(limitedClock, Math::random), null));
        check(limitedCalls.size() == 3 && limitedClock.slept.equals(List.of(7000L, 7000L)), limitedClock.slept);

        // the deadline stops a wait that would overrun it
        var deadlineClock = new FakeClock();
        var down = new Flaky("", 503, 503, 503, 503);
        var retry = RetryOptions.defaults(deadlineClock, () -> 0.999999).withMaxAttempts(10).withDeadline(1000, 5000);
        thrown(a -> Reliability.withRetry(b -> down.run(), retry, null));
        check(deadlineClock.slept.equals(List.of(1000L, 2000L)) && down.calls.size() == 3, deadlineClock.slept);

        // a timeout interrupts a call that would hang
        var interrupted = new CountDownLatch(1);
        Exception timeout = thrown(a -> Reliability.withTimeout(() -> {
            try {
                Thread.sleep(Long.MAX_VALUE);
            } catch (InterruptedException e) {
                interrupted.countDown();
            }
            return "never";
        }, 20));
        check(timeout instanceof TimeoutException, timeout);
        check(interrupted.await(5, TimeUnit.SECONDS), "the call's thread was interrupted: no request left running");

        // the breaker opens, then tests recovery with one trial
        var breakerClock = new FakeClock();
        var breaker = new Breaker(3, 30_000, breakerClock);
        var outage = new Flaky("", 503, 503, 503, 503, 503);
        for (int i = 0; i < 3; i++) thrown(a -> breaker.call(outage::run));
        check(breaker.current().equals("open") && thrown(a -> breaker.call(outage::run)) instanceof CircuitOpenError && outage.calls.size() == 3, "open");
        breakerClock.t += 30_000;
        check(breaker.current().equals("half-open"), breaker.current());
        thrown(a -> breaker.call(outage::run));
        check(breaker.current().equals("open"), "a failed trial opens it again");
        breakerClock.t += 30_000;
        check(breaker.call(() -> "ok").equals("ok") && breaker.current().equals("closed"), "a good trial closes it");

        var notTripped = new Breaker(2, 30_000, new FakeClock());
        var malformed = new Flaky("", 400, 400, 400);
        for (int i = 0; i < 3; i++) thrown(a -> notTripped.call(malformed::run));
        check(notTripped.current().equals("closed"), "a 400 doesn't trip it");

        // fallback tries each option and won't hide a bad request
        var failures = new ArrayList<String>();
        var answer = Reliability.firstThatWorks(List.of(
                new Option<>("primary", new Flaky("", 503)::run), new Option<>("secondary", new Flaky("bug")::run)),
                (name, error) -> failures.add(name + ": " + ((CallError) error).status));
        check(answer.equals(new Answer<>("secondary", "bug")) && failures.equals(List.of("primary: 503")), failures);
        check(thrown(a -> Reliability.firstThatWorks(List.of(new Option<>("primary", new Flaky("", 400)::run),
                new Option<>("secondary", new Flaky("x")::run)), (n, e) -> {})) instanceof CallError e4 && e4.status == 400, "400");

        // all the layers together
        var layersClock = new FakeClock();
        var lines = new ArrayList<String>();
        var flakyModel = new Flaky("", Collections.nCopies(20, 503).toArray(Integer[]::new));
        var layerBreaker = new Breaker(4, 30_000, layersClock);
        var layerRetry = RetryOptions.defaults(layersClock, () -> 0.5);
        var first = Reliability.resilient("model", input -> flakyModel.run(), 1000, layerRetry, layerBreaker, Evals::keywords, lines::add, "I was charged twice.");
        check(first.equals(new Answer<>("fallback", "billing")) && flakyModel.calls.size() == 3, first);
        var second = Reliability.resilient("model", input -> flakyModel.run(), 1000, layerRetry, layerBreaker, Evals::keywords, lines::add, "The app crashes on start.");
        check(second.equals(new Answer<>("fallback", "bug")) && flakyModel.calls.size() == 4, second);
        check(lines.equals(List.of(
                "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
                "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
                "model: gave up (HTTP 503)",
                "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
                "model: gave up (CircuitOpenError)")), lines);

        // a token bucket allows a burst, then paces
        var bucketClock = new FakeClock();
        var bucket = new TokenBucket(3, 1, bucketClock);
        var started = new ArrayList<Long>();
        for (int i = 0; i < 6; i++) {
            bucket.take(1);
            started.add(bucketClock.t);
        }
        check(started.equals(List.of(0L, 0L, 0L, 1000L, 2000L, 3000L)), started);
        check(thrown(a -> bucket.tryTake(5)) instanceof IllegalArgumentException, "too big");

        System.out.println("all reliability checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/13-reliability-and-plumbing/labs/java). `check.sh` compiles the evals lab's `Evals.java` alongside, for the keyword rules, so it fetches the Jackson jars that file needs on the first run. `python3 labs/run.py reliability-and-plumbing/java`.

## 6. Rust

Rust changes two things. First, **errors are an enum**, and `is_retryable` is a `match` that must cover every variant. Add a new kind of failure and the compiler makes you decide whether it's retryable; in the other languages a new exception type silently falls into the default branch.

Second, **a future does nothing until it is awaited, and dropping it cancels it.** That makes the timeout simple and complete: `tokio::time::timeout` drops the attempt's future when time runs out, and the request stops at its next `.await`. The test proves it with a guard whose `Drop` runs. It also makes the breaker cheap: `breaker.call(down.run())` builds the request's future, but when the circuit is open it's never awaited, so no request is sent.

The tests use **tokio's paused clock**: with `#[tokio::test(start_paused = true)]`, time stands still and jumps to the next timer whenever every task is waiting, so real `sleep` and `timeout` run instantly, as with Go's `synctest`. Rust's `resilient` is the one version that doesn't reuse `first_that_works`: a list of boxed futures that borrow local values ran into lifetime trouble, and with one fallback, a `match` on the result is plainer anyway. In production, **tower** provides retry, timeout and rate limiting as layers that wrap a service, which is the main lesson's composition written as types.

```rust
//! Retry, timeout, circuit breaker, fallback and token bucket around an async model call.
//! The same behaviour, and the same numbers, as the TypeScript lab.
use std::future::Future;
use std::pin::Pin;
use std::sync::Mutex;
use std::time::{Duration, SystemTime};
use tokio::time::{Instant, sleep};

/// Every way a call can fail. A `match` on it must cover every variant, so adding one
/// forces a decision about whether it's retryable.
#[derive(Debug, Clone, PartialEq)]
pub enum CallError {
    Status {
        status: u16,
        retry_after: Option<Duration>,
    },
    Timeout,    // our own deadline for one attempt
    Connection, // no response at all
    CircuitOpen,
    AllFailed(Vec<CallError>),
}

impl CallError {
    pub fn status(status: u16) -> Self {
        CallError::Status {
            status,
            retry_after: None,
        }
    }

    pub fn is_retryable(&self) -> bool {
        match self {
            CallError::Status { status, .. } => matches!(status, 408 | 429 | 500..),
            CallError::Timeout | CallError::Connection => true,
            CallError::CircuitOpen | CallError::AllFailed(_) => false,
        }
    }

    fn describe(&self) -> String {
        match self {
            CallError::Status { status, .. } => format!("HTTP {status}"),
            CallError::CircuitOpen => "CircuitOpenError".into(),
            other => format!("{other:?}"),
        }
    }
}

/// Seconds or an HTTP date, as a wait.
pub fn parse_retry_after(header: &str, now: SystemTime) -> Option<Duration> {
    let header = header.trim();
    if let Ok(seconds) = header.parse::<f64>() {
        return Some(Duration::from_secs_f64(seconds.max(0.0)));
    }
    let date = httpdate::parse_http_date(header).ok()?;
    Some(date.duration_since(now).unwrap_or(Duration::ZERO))
}

/// Full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)), in whole milliseconds.
pub fn backoff(attempt: u32, base: Duration, cap: Duration, random: fn() -> f64) -> Duration {
    let ceiling = cap.min(base * 2u32.pow(attempt - 1)).as_millis() as f64;
    Duration::from_millis((random() * ceiling).round() as u64)
}

pub struct RetryOptions {
    pub max_attempts: u32,
    pub base: Duration,
    pub cap: Duration,
    pub deadline: Option<Duration>, // the whole operation, from the first try
    pub random: fn() -> f64,        // rand::random::<f64> in real code
}

impl RetryOptions {
    pub fn new(random: fn() -> f64) -> Self {
        RetryOptions {
            max_attempts: 3,
            base: Duration::from_millis(500),
            cap: Duration::from_secs(10),
            deadline: None,
            random,
        }
    }
}

pub async fn with_retry<T>(
    mut call: impl AsyncFnMut(u32) -> Result<T, CallError>,
    o: &RetryOptions,
    mut on_retry: impl FnMut(u32, Duration, &CallError),
) -> Result<T, CallError> {
    let started = Instant::now();
    let mut attempt = 1;
    loop {
        let error = match call(attempt).await {
            Ok(value) => return Ok(value),
            Err(error) if !error.is_retryable() || attempt >= o.max_attempts => return Err(error),
            Err(error) => error,
        };
        let wait = match &error {
            CallError::Status {
                retry_after: Some(wait),
                ..
            } => *wait, // the server knows best
            _ => backoff(attempt, o.base, o.cap, o.random),
        };
        if o.deadline
            .is_some_and(|deadline| started.elapsed() + wait > deadline)
        {
            return Err(error);
        }
        on_retry(attempt, wait, &error);
        sleep(wait).await;
        attempt += 1;
    }
}

/// When time runs out, the future is dropped. Dropping a future cancels it at its next `.await`,
/// so the request really stops; there is no separate cancel signal to pass along.
pub async fn with_timeout<T>(
    limit: Duration,
    call: impl Future<Output = Result<T, CallError>>,
) -> Result<T, CallError> {
    tokio::time::timeout(limit, call)
        .await
        .unwrap_or(Err(CallError::Timeout))
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum State {
    Closed,
    Open,
    HalfOpen,
}

struct BreakerInner {
    state: State,
    failures: u32,
    opened_at: Instant,
    trial_running: bool,
}

pub struct Breaker {
    threshold: u32,
    cool_down: Duration,
    inner: Mutex<BreakerInner>, // never held across an .await
}

impl Breaker {
    pub fn new(threshold: u32, cool_down: Duration) -> Self {
        let inner = BreakerInner {
            state: State::Closed,
            failures: 0,
            opened_at: Instant::now(),
            trial_running: false,
        };
        Breaker {
            threshold,
            cool_down,
            inner: Mutex::new(inner),
        }
    }

    pub fn current(&self) -> State {
        Self::refresh(&mut self.inner.lock().unwrap(), self.cool_down)
    }

    fn refresh(inner: &mut BreakerInner, cool_down: Duration) -> State {
        if inner.state == State::Open && inner.opened_at.elapsed() >= cool_down {
            inner.state = State::HalfOpen;
        }
        inner.state
    }

    /// A future does nothing until it's awaited, so when the circuit is open, `call` is never polled
    /// and no request is sent.
    pub async fn call<T>(
        &self,
        call: impl Future<Output = Result<T, CallError>>,
    ) -> Result<T, CallError> {
        let before = {
            let mut inner = self.inner.lock().unwrap();
            let state = Self::refresh(&mut inner, self.cool_down);
            if state == State::Open || (state == State::HalfOpen && inner.trial_running) {
                return Err(CallError::CircuitOpen);
            }
            inner.trial_running |= state == State::HalfOpen;
            state
        };
        let result = call.await;
        let mut inner = self.inner.lock().unwrap();
        if before == State::HalfOpen {
            inner.trial_running = false;
        }
        match &result {
            Ok(_) => (inner.state, inner.failures) = (State::Closed, 0),
            Err(error) if error.is_retryable() => {
                inner.failures += 1; // a 400 is our bug, not the provider's outage
                if before == State::HalfOpen || inner.failures >= self.threshold {
                    (inner.state, inner.opened_at) = (State::Open, Instant::now());
                }
            }
            Err(_) => {}
        }
        result
    }
}

pub type Pending<'a, T> = Pin<Box<dyn Future<Output = Result<T, CallError>> + 'a>>;

/// Tries each option in turn. Options are lazy futures, so the ones after a success never run.
pub async fn first_that_works<'a, T>(
    options: Vec<(&'a str, Pending<'a, T>)>,
    mut on_failure: impl FnMut(&str, &CallError),
) -> Result<(&'a str, T), CallError> {
    let mut errors = Vec::new();
    for (name, run) in options {
        match run.await {
            Ok(value) => return Ok((name, value)),
            Err(
                error @ CallError::Status {
                    status: 400 | 422, ..
                },
            ) => return Err(error), // every option would reject it
            Err(error) => {
                on_failure(name, &error);
                errors.push(error);
            }
        }
    }
    Err(CallError::AllFailed(errors))
}

/// The `governor` crate is the production version of this.
pub struct TokenBucket {
    capacity: f64,
    per_second: f64,
    state: Mutex<(f64, Instant)>, // tokens, last refill
}

impl TokenBucket {
    pub fn new(capacity: f64, per_second: f64) -> Self {
        TokenBucket {
            capacity,
            per_second,
            state: Mutex::new((capacity, Instant::now())),
        }
    }

    pub fn try_take(&self, cost: f64) -> Result<Duration, String> {
        if cost > self.capacity {
            return Err(format!(
                "a cost of {cost} can never fit a bucket of {}",
                self.capacity
            ));
        }
        let mut state = self.state.lock().unwrap();
        let (tokens, last) = *state;
        let tokens = self
            .capacity
            .min(tokens + last.elapsed().as_secs_f64() * self.per_second);
        if tokens >= cost {
            *state = (tokens - cost, Instant::now());
            return Ok(Duration::ZERO);
        }
        *state = (tokens, Instant::now());
        Ok(Duration::from_millis(
            ((cost - tokens) / self.per_second * 1000.0).ceil() as u64,
        ))
    }

    pub async fn take(&self, cost: f64) -> Result<(), String> {
        loop {
            match self.try_take(cost)? {
                Duration::ZERO => return Ok(()),
                wait => sleep(wait).await,
            }
        }
    }
}

pub struct Layers<'a> {
    pub timeout: Duration,
    pub retry: RetryOptions,
    pub breaker: &'a Breaker,
    pub fallback: Option<fn(&str) -> String>,
    pub log: &'a dyn Fn(String),
}

/// fallback( retry( breaker( timeout( call ) ) ) ), as in the main lesson. With one fallback, a
/// `match` on the primary's result says it more plainly than a list of boxed futures.
pub async fn resilient<'a>(
    name: &'a str,
    call: impl AsyncFn(&str) -> Result<String, CallError>,
    l: &Layers<'_>,
    input: &str,
) -> Result<(&'a str, String), CallError> {
    let primary = with_retry(
        async |_| l.breaker.call(with_timeout(l.timeout, call(input))).await,
        &l.retry,
        |attempt, wait, error| {
            (l.log)(format!(
                "{name}: attempt {attempt} failed ({}), retrying in {} ms",
                error.describe(),
                wait.as_millis()
            ))
        },
    )
    .await;
    match (primary, l.fallback) {
        (Ok(value), _) => Ok((name, value)),
        (
            Err(
                error @ CallError::Status {
                    status: 400 | 422, ..
                },
            ),
            _,
        ) => Err(error),
        (Err(error), fallback) => {
            (l.log)(format!("{name}: gave up ({})", error.describe()));
            fallback
                .map(|f| ("fallback", f(input)))
                .ok_or(CallError::AllFailed(vec![error]))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;
    use std::sync::atomic::{AtomicBool, Ordering};

    const MS: fn(u64) -> Duration = Duration::from_millis;

    fn half() -> f64 {
        0.5
    }
    fn top() -> f64 {
        0.999999
    }

    /// Fails with each status in turn, then answers.
    struct Flaky {
        statuses: Vec<u16>,
        reply: &'static str,
        calls: RefCell<Vec<u16>>,
    }

    impl Flaky {
        fn new(reply: &'static str, statuses: &[u16]) -> Self {
            Flaky {
                statuses: statuses.to_vec(),
                reply,
                calls: RefCell::new(vec![]),
            }
        }
        async fn run(&self) -> Result<String, CallError> {
            let mut calls = self.calls.borrow_mut();
            match self.statuses.get(calls.len()) {
                Some(&status) => {
                    calls.push(status);
                    Err(CallError::status(status))
                }
                None => {
                    calls.push(200);
                    Ok(self.reply.to_string())
                }
            }
        }
        fn count(&self) -> usize {
            self.calls.borrow().len()
        }
    }

    #[test]
    fn only_failures_a_second_try_could_fix_are_retryable() {
        assert!(
            [408, 429, 500, 502, 503, 529]
                .iter()
                .all(|&s| CallError::status(s).is_retryable())
        );
        assert!(
            ![400, 401, 403, 404, 422]
                .iter()
                .any(|&s| CallError::status(s).is_retryable())
        );
        assert!(CallError::Timeout.is_retryable() && CallError::Connection.is_retryable());
        assert!(!CallError::CircuitOpen.is_retryable());
    }

    #[test]
    fn retry_after_comes_as_seconds_or_a_date() {
        let now = httpdate::parse_http_date("Fri, 02 Oct 2026 12:00:00 GMT").unwrap();
        assert_eq!(parse_retry_after("7", now), Some(MS(7000)));
        assert_eq!(
            parse_retry_after("Fri, 02 Oct 2026 12:00:30 GMT", now),
            Some(MS(30_000))
        );
        assert_eq!(parse_retry_after("soon", now), None);
    }

    #[test]
    fn backoff_ceilings_double_up_to_a_cap() {
        let got: Vec<u128> = (1..=6)
            .map(|n| backoff(n, MS(500), MS(10_000), top).as_millis())
            .collect();
        assert_eq!(got, [500, 1000, 2000, 4000, 8000, 10000]);
    }

    // start_paused: tokio's clock is frozen, and jumps to the next timer whenever every task is
    // waiting. Real `sleep` and `timeout`, and a 30-second cool-down takes no time.
    #[tokio::test(start_paused = true)]
    async fn a_transient_failure_is_retried_until_it_succeeds() {
        let (start, model, slept) = (
            Instant::now(),
            Flaky::new("billing", &[503, 429]),
            RefCell::new(vec![]),
        );
        let reply = with_retry(
            async |_| model.run().await,
            &RetryOptions::new(half),
            |_, wait, _| slept.borrow_mut().push(wait),
        )
        .await;
        assert_eq!(reply, Ok("billing".into()));
        assert_eq!(*model.calls.borrow(), [503, 429, 200]);
        assert_eq!(
            (slept.into_inner(), start.elapsed()),
            (vec![MS(250), MS(500)], MS(750))
        );
    }

    #[tokio::test(start_paused = true)]
    async fn a_400_fails_at_once() {
        let model = Flaky::new("", &[400]);
        let result = with_retry(
            async |_| model.run().await,
            &RetryOptions::new(half),
            |_, _, _| {},
        )
        .await;
        assert_eq!((result, model.count()), (Err(CallError::status(400)), 1));
    }

    #[tokio::test(start_paused = true)]
    async fn retry_after_beats_our_guess_and_attempts_run_out() {
        let (start, calls) = (Instant::now(), RefCell::new(0));
        let limited = async |_| -> Result<(), CallError> {
            *calls.borrow_mut() += 1;
            Err(CallError::Status {
                status: 429,
                retry_after: Some(MS(7000)),
            })
        };
        assert!(
            with_retry(limited, &RetryOptions::new(half), |_, _, _| {})
                .await
                .is_err()
        );
        assert_eq!((calls.into_inner(), start.elapsed()), (3, MS(14_000)));
    }

    #[tokio::test(start_paused = true)]
    async fn the_deadline_stops_a_wait_that_would_overrun_it() {
        let (start, model) = (Instant::now(), Flaky::new("", &[503, 503, 503, 503]));
        let retry = RetryOptions {
            max_attempts: 10,
            base: MS(1000),
            deadline: Some(MS(5000)),
            ..RetryOptions::new(top)
        };
        assert!(
            with_retry(async |_| model.run().await, &retry, |_, _, _| {})
                .await
                .is_err()
        );
        assert_eq!((model.count(), start.elapsed()), (3, MS(3000))); // slept 1 s + 2 s; 4 s more would pass 5 s
    }

    #[tokio::test(start_paused = true)]
    async fn a_timeout_drops_a_call_that_would_hang() {
        static DROPPED: AtomicBool = AtomicBool::new(false);
        struct Guard;
        impl Drop for Guard {
            fn drop(&mut self) {
                DROPPED.store(true, Ordering::SeqCst);
            }
        }
        let hangs = async {
            let _guard = Guard;
            std::future::pending::<Result<String, CallError>>().await
        };
        assert_eq!(with_timeout(MS(20), hangs).await, Err(CallError::Timeout));
        assert!(DROPPED.load(Ordering::SeqCst)); // the call was dropped: cancelled, not left running
    }

    #[tokio::test(start_paused = true)]
    async fn the_breaker_opens_then_tests_recovery_with_one_trial() {
        let (breaker, down) = (
            Breaker::new(3, Duration::from_secs(30)),
            Flaky::new("", &[503; 5]),
        );
        for _ in 0..3 {
            let _ = breaker.call(down.run()).await;
        }
        assert_eq!(breaker.current(), State::Open);
        assert_eq!(breaker.call(down.run()).await, Err(CallError::CircuitOpen));
        assert_eq!(down.count(), 3); // the refused call's future was built but never run
        sleep(Duration::from_secs(30)).await;
        assert_eq!(breaker.current(), State::HalfOpen);
        let _ = breaker.call(down.run()).await;
        assert_eq!(breaker.current(), State::Open);
        sleep(Duration::from_secs(30)).await;
        assert_eq!(breaker.call(async { Ok("ok") }).await, Ok("ok"));
        assert_eq!(breaker.current(), State::Closed);
    }

    #[tokio::test(start_paused = true)]
    async fn a_400_does_not_trip_the_breaker() {
        let (breaker, bad) = (
            Breaker::new(2, Duration::from_secs(30)),
            Flaky::new("", &[400; 3]),
        );
        for _ in 0..3 {
            let _ = breaker.call(bad.run()).await;
        }
        assert_eq!(breaker.current(), State::Closed);
    }

    #[tokio::test]
    async fn fallback_tries_each_option_and_wont_hide_a_bad_request() {
        let (primary, secondary, failures) = (
            Flaky::new("", &[503]),
            Flaky::new("bug", &[]),
            RefCell::new(vec![]),
        );
        let options: Vec<(&str, Pending<String>)> = vec![
            ("primary", Box::pin(primary.run())),
            ("secondary", Box::pin(secondary.run())),
        ];
        let answer = first_that_works(options, |name, error| {
            failures
                .borrow_mut()
                .push(format!("{name}: {}", error.describe()))
        })
        .await;
        assert_eq!(answer, Ok(("secondary", "bug".to_string())));
        assert_eq!(failures.into_inner(), ["primary: HTTP 503"]);

        let (bad, unused) = (Flaky::new("", &[400]), Flaky::new("x", &[]));
        let options: Vec<(&str, Pending<String>)> = vec![
            ("primary", Box::pin(bad.run())),
            ("secondary", Box::pin(unused.run())),
        ];
        assert_eq!(
            first_that_works(options, |_, _| {}).await,
            Err(CallError::status(400))
        );
        assert_eq!(unused.count(), 0);
    }

    #[tokio::test(start_paused = true)]
    async fn all_the_layers_together() {
        let (model, lines) = (Flaky::new("", &[503; 20]), RefCell::new(vec![]));
        let breaker = Breaker::new(4, Duration::from_secs(30));
        let log = |line: String| lines.borrow_mut().push(line);
        let layers = Layers {
            timeout: MS(1000),
            retry: RetryOptions::new(half),
            breaker: &breaker,
            fallback: Some(evals::keywords),
            log: &log,
        };
        let call = async |_: &str| model.run().await;
        assert_eq!(
            resilient("model", call, &layers, "I was charged twice.").await,
            Ok(("fallback", "billing".into()))
        );
        assert_eq!(model.count(), 3);
        assert_eq!(
            resilient("model", call, &layers, "The app crashes on start.").await,
            Ok(("fallback", "bug".into()))
        );
        assert_eq!(model.count(), 4);
        assert_eq!(
            lines.into_inner(),
            [
                "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
                "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
                "model: gave up (HTTP 503)",
                "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
                "model: gave up (CircuitOpenError)",
            ]
        );
    }

    #[tokio::test(start_paused = true)]
    async fn a_token_bucket_allows_a_burst_then_paces() {
        let (start, bucket) = (Instant::now(), TokenBucket::new(3.0, 1.0));
        let mut started = vec![];
        for _ in 0..6 {
            bucket.take(1.0).await.unwrap();
            started.push(start.elapsed().as_millis());
        }
        assert_eq!(started, [0, 0, 0, 1000, 2000, 3000]);
        assert!(bucket.try_take(5.0).is_err());
    }
}
```

`Cargo.toml` depends on the evals lab by path, `evals = { path = "../../../12-evals/labs/rust" }`, and on tokio with `test-util` for the paused clock.

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/13-reliability-and-plumbing/labs/rust). `python3 labs/run.py reliability-and-plumbing/rust`.

## 7. C#

C# passes a **`CancellationToken`** through every async call, and the timeout is a linked token source with `CancelAfter`. The token asks the call to stop; `WaitAsync` releases the caller on time even if the call ignores it. Two .NET facts are worth knowing. `HttpClient.Timeout` defaults to 100 seconds and, when it fires, throws a `TaskCanceledException` whose inner exception is a `TimeoutException`, which `IsRetryable` recognises. And with `HttpCompletionOption.ResponseHeadersRead`, which streaming needs, that timeout stops counting once the headers arrive, so a stream that stalls afterwards needs a limit of your own.

In production, **`Microsoft.Extensions.Http.Resilience`** gives an `HttpClient` a standard pipeline in one call: a rate limiter, a total timeout, retries, a circuit breaker and a per-attempt timeout, in that order, outside to inside. That is the main lesson's order, with a total deadline added. The lab passes its clock in as two functions; production .NET code uses `TimeProvider`, and tests use `FakeTimeProvider` from `Microsoft.Extensions.TimeProvider.Testing`.

```csharp
// Retry, timeout, circuit breaker, fallback and token bucket around an async model call.
// The same behaviour, and the same numbers, as the TypeScript lab.
using System.Globalization;

/// <summary>A failed model call: the HTTP status, and the Retry-After wait if the server sent one.</summary>
public sealed class CallError(int status, TimeSpan? retryAfter = null) : Exception($"HTTP {status}")
{
    public int Status => status;
    public TimeSpan? RetryAfter => retryAfter;
}

public sealed class CircuitOpenError() : Exception("circuit open: not calling a dependency that keeps failing");

/// <summary>Time, so tests can replace it. In production code, .NET's TimeProvider does this job.</summary>
public sealed record Clock(Func<TimeSpan> Now, Func<TimeSpan, CancellationToken, Task> Sleep)
{
    public static readonly Clock Real = new(() => TimeSpan.FromTicks(Environment.TickCount64 * TimeSpan.TicksPerMillisecond),
        (wait, ct) => Task.Delay(wait, ct));
}

public sealed record RetryOptions(Clock Clock, Func<double> Random, int MaxAttempts = 3, int BaseMs = 500, int CapMs = 10_000,
    TimeSpan? Deadline = null);

public static class Reliability
{
    public static bool IsRetryable(Exception error) => error switch
    {
        CallError e => e.Status is 408 or 429 or >= 500,
        TimeoutException => true, // our own deadline for one attempt
        TaskCanceledException { InnerException: TimeoutException } => true, // HttpClient.Timeout
        HttpRequestException { StatusCode: null } => true, // no response at all
        _ => false,
    };

    /// <summary>Seconds or an HTTP date, as a wait.</summary>
    public static TimeSpan? ParseRetryAfter(string? header, DateTimeOffset now)
    {
        if (string.IsNullOrWhiteSpace(header)) return null;
        if (double.TryParse(header, NumberStyles.Float, CultureInfo.InvariantCulture, out var seconds))
            return TimeSpan.FromSeconds(Math.Max(0, seconds));
        if (DateTimeOffset.TryParseExact(header.Trim(), "r", CultureInfo.InvariantCulture, DateTimeStyles.None, out var date))
            return date > now ? date - now : TimeSpan.Zero;
        return null;
    }

    /// <summary>Full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)).</summary>
    public static TimeSpan Backoff(int attempt, int baseMs, int capMs, Func<double> random) =>
        TimeSpan.FromMilliseconds(Math.Round(random() * Math.Min(capMs, baseMs * Math.Pow(2, attempt - 1))));

    public static async Task<T> WithRetry<T>(Func<int, Task<T>> call, RetryOptions o,
        Action<int, TimeSpan, Exception>? onRetry = null, CancellationToken ct = default)
    {
        var started = o.Clock.Now();
        for (var attempt = 1; ; attempt++)
        {
            try
            {
                return await call(attempt);
            }
            catch (Exception error) when (IsRetryable(error) && attempt < o.MaxAttempts)
            {
                var wait = (error as CallError)?.RetryAfter ?? Backoff(attempt, o.BaseMs, o.CapMs, o.Random); // the server knows best
                if (o.Deadline is { } deadline && o.Clock.Now() - started + wait > deadline) throw;
                onRetry?.Invoke(attempt, wait, error);
                await o.Clock.Sleep(wait, ct);
            }
        }
    }

    /// <summary>One attempt with its own deadline. The token cancels the request; WaitAsync releases the
    /// caller on time even if the call ignores the token.</summary>
    public static async Task<T> WithTimeout<T>(Func<CancellationToken, Task<T>> call, TimeSpan limit, CancellationToken ct = default)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(limit);
        try
        {
            return await call(cts.Token).WaitAsync(cts.Token);
        }
        catch (OperationCanceledException) when (!ct.IsCancellationRequested)
        {
            throw new TimeoutException($"timed out after {limit.TotalMilliseconds} ms");
        }
    }

    public static async Task<(string By, T Value)> FirstThatWorks<T>(IEnumerable<(string Name, Func<Task<T>> Run)> options,
        Action<string, Exception>? onFailure = null)
    {
        var errors = new List<Exception>();
        foreach (var (name, run) in options)
        {
            try
            {
                return (name, await run());
            }
            catch (Exception error) when (error is not CallError { Status: 400 or 422 }) // a bad request would fail everywhere
            {
                onFailure?.Invoke(name, error);
                errors.Add(error);
            }
        }
        throw new AggregateException($"all {errors.Count} options failed", errors);
    }

    /// <summary>fallback( retry( breaker( timeout( call ) ) ) ), as in the main lesson.</summary>
    public static Func<string, Task<(string By, string Value)>> Resilient(string name, Func<string, CancellationToken, Task<string>> call,
        TimeSpan timeout, RetryOptions retry, Breaker breaker, Func<string, string>? fallback, Action<string> log) =>
        input =>
        {
            var options = new List<(string, Func<Task<string>>)>
            {
                (name, () => WithRetry(_ => breaker.Call(() => WithTimeout(ct => call(input, ct), timeout)), retry,
                    (attempt, wait, error) => log($"{name}: attempt {attempt} failed ({Describe(error)}), retrying in {wait.TotalMilliseconds} ms"))),
            };
            if (fallback is not null) options.Add(("fallback", () => Task.FromResult(fallback(input))));
            return FirstThatWorks(options, (by, error) => log($"{by}: gave up ({Describe(error)})"));
        };

    static string Describe(Exception error) => error is CallError e ? $"HTTP {e.Status}" : error.GetType().Name;
}

public sealed class Breaker(int threshold, TimeSpan coolDown, Clock clock)
{
    readonly Lock gate = new();
    string state = "closed";
    int failures;
    TimeSpan openedAt;
    bool trialRunning;

    public string Current
    {
        get
        {
            lock (gate) return Refresh();
        }
    }

    string Refresh()
    {
        if (state == "open" && clock.Now() - openedAt >= coolDown) state = "half-open";
        return state;
    }

    public async Task<T> Call<T>(Func<Task<T>> fn)
    {
        string before;
        lock (gate)
        {
            before = Refresh();
            if (before == "open" || (before == "half-open" && trialRunning)) throw new CircuitOpenError();
            if (before == "half-open") trialRunning = true;
        }
        try
        {
            var result = await fn();
            lock (gate) (state, failures) = ("closed", 0);
            return result;
        }
        catch (Exception error) when (Reliability.IsRetryable(error)) // a 400 is our bug, not the provider's outage
        {
            lock (gate)
            {
                failures++;
                if (before == "half-open" || failures >= threshold) (state, openedAt) = ("open", clock.Now());
            }
            throw;
        }
        finally
        {
            if (before == "half-open") lock (gate) trialRunning = false;
        }
    }
}

/// <summary>System.Threading.RateLimiting.TokenBucketRateLimiter is the built-in version of this.</summary>
public sealed class TokenBucket
{
    readonly Lock gate = new();
    readonly double capacity, perSecond;
    readonly Clock clock;
    double tokens;
    TimeSpan last;

    public TokenBucket(double capacity, double perSecond, Clock clock)
    {
        (this.capacity, this.perSecond, this.clock) = (capacity, perSecond, clock);
        (tokens, last) = (capacity, clock.Now());
    }

    public TimeSpan TryTake(double cost = 1)
    {
        ArgumentOutOfRangeException.ThrowIfGreaterThan(cost, capacity);
        lock (gate)
        {
            var now = clock.Now();
            tokens = Math.Min(capacity, tokens + (now - last).TotalSeconds * perSecond);
            last = now;
            if (tokens >= cost)
            {
                tokens -= cost;
                return TimeSpan.Zero;
            }
            return TimeSpan.FromMilliseconds(Math.Ceiling((cost - tokens) / perSecond * 1000));
        }
    }

    public async Task Take(double cost = 1, CancellationToken ct = default)
    {
        for (var wait = TryTake(cost); wait > TimeSpan.Zero; wait = TryTake(cost)) await clock.Sleep(wait, ct);
    }
}
```

```csharp
// Checks: the same scenarios and numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static async Task<Exception> Thrown(Func<Task> body)
{
    try { await body(); }
    catch (Exception e) { return e; }
    throw new Exception("expected an exception");
}

static TimeSpan Ms(double ms) => TimeSpan.FromMilliseconds(ms);

foreach (var s in new[] { 408, 429, 500, 502, 503, 529 }) Check(Reliability.IsRetryable(new CallError(s)), s);
foreach (var s in new[] { 400, 401, 403, 404, 422 }) Check(!Reliability.IsRetryable(new CallError(s)), s);
Check(Reliability.IsRetryable(new TimeoutException()) && Reliability.IsRetryable(new HttpRequestException("refused"))
    && !Reliability.IsRetryable(new InvalidOperationException("a bug")), "timeouts and no response");

var noon = new DateTimeOffset(2026, 10, 2, 12, 0, 0, TimeSpan.Zero);
Check(Reliability.ParseRetryAfter("7", noon) == Ms(7000), "seconds");
Check(Reliability.ParseRetryAfter("Fri, 02 Oct 2026 12:00:30 GMT", noon) == Ms(30_000), "date");
Check(Reliability.ParseRetryAfter("soon", noon) is null, "nonsense");

var ceilings = Enumerable.Range(1, 6).Select(n => Reliability.Backoff(n, 500, 10_000, () => 0.999999).TotalMilliseconds);
Check(ceilings.SequenceEqual([500.0, 1000, 2000, 4000, 8000, 10000]), string.Join(" ", ceilings));

// a transient failure is retried until it succeeds
var clock = new FakeClock();
var model = new Flaky("billing", 503, 429);
Check(await Reliability.WithRetry(_ => model.Run(), new RetryOptions(clock.Clock, () => 0.5)) == "billing", "reply");
Check(model.Calls.SequenceEqual([503, 429, 200]) && clock.Slept.SequenceEqual([250.0, 500]), string.Join(" ", clock.Slept));

// a 400 fails at once
var bad = new Flaky("", 400);
Check(await Thrown(() => Reliability.WithRetry(_ => bad.Run(), new RetryOptions(new FakeClock().Clock, () => 0.5))) is CallError { Status: 400 }
    && bad.Calls.Count == 1, "400");

// Retry-After beats our guess, and the attempts run out
var limitedClock = new FakeClock();
var limitedCalls = 0;
await Thrown(() => Reliability.WithRetry<string>(_ =>
{
    limitedCalls++;
    throw new CallError(429, Ms(7000));
}, new RetryOptions(limitedClock.Clock, Random.Shared.NextDouble)));
Check(limitedCalls == 3 && limitedClock.Slept.SequenceEqual([7000.0, 7000]), string.Join(" ", limitedClock.Slept));

// the deadline stops a wait that would overrun it
var deadlineClock = new FakeClock();
var down = new Flaky("", 503, 503, 503, 503);
await Thrown(() => Reliability.WithRetry(_ => down.Run(),
    new RetryOptions(deadlineClock.Clock, () => 0.999999, MaxAttempts: 10, BaseMs: 1000, Deadline: Ms(5000))));
Check(deadlineClock.Slept.SequenceEqual([1000.0, 2000]) && down.Calls.Count == 3, string.Join(" ", deadlineClock.Slept));

// a timeout cancels a call that would hang
var cancelled = new TaskCompletionSource();
var timeout = await Thrown(() => Reliability.WithTimeout(async ct =>
{
    try { await Task.Delay(Timeout.Infinite, ct); }
    catch (OperationCanceledException) { cancelled.SetResult(); throw; }
    return "never";
}, Ms(20)));
Check(timeout is TimeoutException, timeout);
await cancelled.Task.WaitAsync(TimeSpan.FromSeconds(5)); // the call saw its token cancelled: no request left running

// the breaker opens, then tests recovery with one trial
var breakerClock = new FakeClock();
var breaker = new Breaker(3, TimeSpan.FromSeconds(30), breakerClock.Clock);
var outage = new Flaky("", 503, 503, 503, 503, 503);
for (var i = 0; i < 3; i++) await Thrown(() => breaker.Call(outage.Run));
Check(breaker.Current == "open" && await Thrown(() => breaker.Call(outage.Run)) is CircuitOpenError && outage.Calls.Count == 3, "open");
breakerClock.T += TimeSpan.FromSeconds(30);
Check(breaker.Current == "half-open", breaker.Current);
await Thrown(() => breaker.Call(outage.Run));
Check(breaker.Current == "open", "a failed trial opens it again");
breakerClock.T += TimeSpan.FromSeconds(30);
Check(await breaker.Call(() => Task.FromResult("ok")) == "ok" && breaker.Current == "closed", "a good trial closes it");

var notTripped = new Breaker(2, TimeSpan.FromSeconds(30), new FakeClock().Clock);
var malformed = new Flaky("", 400, 400, 400);
for (var i = 0; i < 3; i++) await Thrown(() => notTripped.Call(malformed.Run));
Check(notTripped.Current == "closed", "a 400 doesn't trip it");

// fallback tries each option and won't hide a bad request
var failures = new List<string>();
var answer = await Reliability.FirstThatWorks<string>([("primary", new Flaky("", 503).Run), ("secondary", new Flaky("bug").Run)],
    (name, error) => failures.Add($"{name}: {((CallError)error).Status}"));
Check(answer == ("secondary", "bug") && failures.SequenceEqual(["primary: 503"]), string.Join(" ", failures));
Check(await Thrown(() => Reliability.FirstThatWorks<string>([("primary", new Flaky("", 400).Run), ("secondary", new Flaky("x").Run)]))
    is CallError { Status: 400 }, "400 comes straight back");

// all the layers together
var layersClock = new FakeClock();
var lines = new List<string>();
var flaky = new Flaky("", Enumerable.Repeat(503, 20).ToArray());
var classify = Reliability.Resilient("model", (_, _) => flaky.Run(), Ms(1000), new RetryOptions(layersClock.Clock, () => 0.5),
    new Breaker(4, TimeSpan.FromSeconds(30), layersClock.Clock), Evals.Keywords, lines.Add);
Check(await classify("I was charged twice.") == ("fallback", "billing") && flaky.Calls.Count == 3, flaky.Calls.Count);
Check(await classify("The app crashes on start.") == ("fallback", "bug") && flaky.Calls.Count == 4, flaky.Calls.Count);
Check(lines.SequenceEqual([
    "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
    "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
    "model: gave up (HTTP 503)",
    "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
    "model: gave up (CircuitOpenError)",
]), string.Join("\n", lines));

// a token bucket allows a burst, then paces
var bucketClock = new FakeClock();
var bucket = new TokenBucket(3, 1, bucketClock.Clock);
var started = new List<double>();
for (var i = 0; i < 6; i++)
{
    await bucket.Take();
    started.Add(bucketClock.T.TotalMilliseconds);
}
Check(started.SequenceEqual([0.0, 0, 0, 1000, 2000, 3000]), string.Join(" ", started));
Check(await Thrown(() => Task.FromResult(bucket.TryTake(5))) is ArgumentOutOfRangeException, "too big");

Console.WriteLine("all reliability checks passed");

/// <summary>Sleeping moves time forward instantly, so checks about waiting take no time.</summary>
sealed class FakeClock
{
    public TimeSpan T;
    public readonly List<double> Slept = [];
    public Clock Clock => new(() => T, (wait, _) =>
    {
        Slept.Add(wait.TotalMilliseconds);
        T += wait;
        return Task.CompletedTask;
    });
}

/// <summary>Fails with each status in turn, then answers.</summary>
sealed class Flaky(string reply, params int[] statuses)
{
    public readonly List<int> Calls = [];

    public Task<string> Run()
    {
        if (Calls.Count < statuses.Length)
        {
            var status = statuses[Calls.Count];
            Calls.Add(status);
            return Task.FromException<string>(new CallError(status));
        }
        Calls.Add(200);
        return Task.FromResult(reply);
    }
}
```

The project links the evals lab's `Evals.cs` for the keyword rules. `container.sh` copies both labs into a temporary folder, laid out as in the vault, and runs `check.sh` in the .NET SDK container.

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/13-reliability-and-plumbing/labs/csharp). `python3 labs/run.py reliability-and-plumbing/csharp` (needs Podman).

## Common pitfalls

1. **A timeout that doesn't cancel.** In Go and C#, a call that never checks its context or token keeps running after you've given up on it. Pass the context or token all the way to the HTTP call.
2. **Catching the cancellation by accident.** Python's `CancelledError`, Java's `InterruptedException` and C#'s `OperationCanceledException` must not be swallowed by a broad `catch` around the call, or a timed-out attempt looks like it's still running.
3. **Two deadlines that look the same.** In Go, the attempt's timeout and the caller's deadline both report `DeadlineExceeded`. Retry the first; never the second.
4. **Locks held across an `await`.** The Rust breaker releases its `Mutex` before awaiting the call. Holding a lock across an `await` blocks every other caller for as long as the slowest request.
5. **Tests that really sleep.** A breaker test that waits 30 real seconds gets skipped, then deleted. Use your language's fake clock.
6. **A default branch for unknown errors.** In every language but Rust, a new exception type is silently "not retryable". Write a test for each kind of failure your HTTP client can actually raise.

## Check your understanding

1. What happens to the request when the timeout fires, in Rust, Python, Go and C#?
2. Why do the Go and Rust labs need no clock parameter, when the others do?
3. Go's `Retry` checks `ctx.Err()` before deciding to retry a `DeadlineExceeded`. What goes wrong without that check?
4. Why is a blocking retry loop a reasonable design in Java 21 but not in Java 8?
5. In the Rust breaker test, `breaker.call(down.run())` is called while the circuit is open, yet the model isn't called. Why?
6. What does `Microsoft.Extensions.Http.Resilience`'s standard pipeline add to the main lesson's layers?

<details>
<summary>Answers — after your attempt</summary>

1. Rust: the future is dropped, so the request stops at its next `.await`. Python: the task gets a `CancelledError` at its current `await`, so it stops too. Go and C#: the context or token is cancelled, and the request stops only if the call passed it on to the HTTP client, which the standard clients do.
2. Their test tools fake the real clock: Go's `synctest` and tokio's paused time replace what `time.Now`, `time.Sleep` and timers report inside the test. The others have no built-in way to do that for plain code, so the code takes a clock and the tests pass a fake one.
3. When the caller's own deadline has passed, every attempt fails with `DeadlineExceeded` straight away, and the loop would keep "retrying" work nobody is waiting for any more, until it hit the attempt limit.
4. A virtual thread that sleeps costs a few hundred bytes, so thousands of sleeping retry loops are fine. In Java 8, each sleeping loop held a full operating-system thread, which made blocking retries expensive at scale.
5. A future does nothing until it is awaited. The breaker returns `CircuitOpen` without awaiting it, so the request is never started.
6. A rate limiter on the outside and a total timeout around all the retries, as well as the per-attempt timeout. The main lesson's version had per-attempt timeouts and a deadline option in the retry loop; the standard pipeline makes both explicit layers.

</details>

## Practice — independent task

**Point your language's lab at a real failure.**

1. Add a function that calls Ollama's chat endpoint through your language's HTTP client, passing the context, token or signal through, and turning a non-2xx response into the lab's `CallError` with its `Retry-After`.
2. Wrap it in `resilient`, with the keyword rules as the fallback.
3. Call it three ways: normally, with a 1 ms per-attempt timeout, and with a model name that doesn't exist.

**Done when:** each call gives the answer and log lines you predicted before running it, and in the 1 ms case you can show (with Ollama's log, or a counter in your code) that the abandoned requests were really cancelled rather than left running.

## Before moving on

You can name your ecosystem's resilience and rate-limiting libraries, cancel a slow call properly in your language, and test waits of any length with a fake clock.

**Recap.** The layers are the same everywhere; cancellation and time are what change. Rust drops futures and Python cancels at the next `await`, so both really stop the request. Go and C# pass a context or token that the call must honour. Java interrupts a thread, and virtual threads make blocking retries cheap. Go's `synctest` and tokio's paused time fake the real clock, and the other languages pass a clock in. In production, use Resilience4j, Polly, tenacity, tower or your SDK's settings, and know what each one is doing.

## Related
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|Reliability and plumbing]] — the main lesson
- [[ai-ml/03-ai-engineer/12-evals/in-other-languages|Evals in other languages]] — the keyword rules every fallback here imports
- [[ai-ml/03-ai-engineer/04-calling-models/in-other-languages|Calling models in other languages]] — each language's HTTP client and error types
- [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]] — the general patterns, for any dependency
