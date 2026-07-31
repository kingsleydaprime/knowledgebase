/**
 * A token-bucket rate limiter.
 *
 * Requirements:
 *  - The bucket holds at most `capacity` tokens, and starts full.
 *  - Tokens refill continuously at `permitsPerSecond` tokens/sec — accumulate
 *    fractional tokens over time; don't wait for a whole token before
 *    crediting any progress toward the next one.
 *  - tryAcquire() is non-blocking: if at least one token is available, consume
 *    it and return true immediately; otherwise return false immediately.
 *  - Safe to call from many threads concurrently — under concurrent callers,
 *    the total number of successful acquires in any time window must never
 *    exceed what the rate + accumulated burst capacity actually allows.
 *
 * Run RateLimiterTest.java against this once implemented — see
 * ../README.md for how to compile and run it.
 */
public class RateLimiter {

    public RateLimiter(double permitsPerSecond, int capacity) {
        throw new UnsupportedOperationException("implement me");
    }

    public boolean tryAcquire() {
        throw new UnsupportedOperationException("implement me");
    }
}
