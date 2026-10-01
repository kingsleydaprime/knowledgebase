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
