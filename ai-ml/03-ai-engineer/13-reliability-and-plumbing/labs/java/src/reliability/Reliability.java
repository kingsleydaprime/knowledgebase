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
