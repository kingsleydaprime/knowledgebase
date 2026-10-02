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
