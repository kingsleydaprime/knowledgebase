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
