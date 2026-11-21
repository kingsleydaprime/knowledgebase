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
