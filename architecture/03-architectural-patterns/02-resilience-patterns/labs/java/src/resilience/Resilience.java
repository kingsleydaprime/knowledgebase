package resilience;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/** A tick-by-tick simulation of a cascade, Little's law, and a bulkhead. The same numbers as the TypeScript lab. One tick is 100 ms. */
public final class Resilience {
    private Resilience() {}

    public enum Kind { SEARCH, PROFILE }

    public static final class Counts {
        public int ok, failed, timedOut, rejected, unfinished;

        @Override public String toString() {
            return "ok=%d failed=%d timedOut=%d rejected=%d unfinished=%d".formatted(ok, failed, timedOut, rejected, unfinished);
        }
    }

    /** pools: endpoint → pool name (the same name means a shared pool). sizes is a LinkedHashMap: its order decides who starts first. */
    public record Config(Map<Kind, String> pools, LinkedHashMap<String, Integer> sizes, int queueLimit, int dependencyTimeoutTicks) {}

    public record Load(int ticks, Map<Kind, Integer> arrivalsPerTick, Map<Kind, Integer> serviceTicks, int clientTimeoutTicks) {}

    private static final class Request {
        final Kind kind;
        final int arrived;
        int endsAt;
        boolean failed;

        Request(Kind kind, int arrived) { this.kind = kind; this.arrived = arrived; }
    }

    public static Map<Kind, Counts> simulate(Config c, Load l) {
        var counts = new EnumMap<Kind, Counts>(Kind.class);
        for (var k : Kind.values()) counts.put(k, new Counts());
        var queues = new LinkedHashMap<String, ArrayDeque<Request>>();
        var running = new LinkedHashMap<String, List<Request>>();
        c.sizes().keySet().forEach(pool -> { queues.put(pool, new ArrayDeque<>()); running.put(pool, new ArrayList<>()); });
        for (int t = 0; t < l.ticks(); t++) {
            final int now = t;
            running.values().forEach(busy -> busy.removeIf(r -> { // 1. finished work frees its worker
                if (r.endsAt > now) return false;
                if (r.failed) counts.get(r.kind).failed++; else counts.get(r.kind).ok++;
                return true;
            }));
            queues.values().forEach(queue -> queue.removeIf(r -> { // 2. callers who waited too long give up
                boolean gaveUp = now - r.arrived >= l.clientTimeoutTicks();
                if (gaveUp) counts.get(r.kind).timedOut++;
                return gaveUp;
            }));
            for (var kind : Kind.values()) { // 3. new requests arrive, or are turned away
                var queue = queues.get(c.pools().get(kind));
                for (int i = 0; i < l.arrivalsPerTick().get(kind); i++) {
                    if (queue.size() >= c.queueLimit()) counts.get(kind).rejected++; // load shedding
                    else queue.add(new Request(kind, t));
                }
            }
            for (var pool : c.sizes().keySet()) { // 4. free workers take requests, oldest first
                var queue = queues.get(pool);
                var busy = running.get(pool);
                while (busy.size() < c.sizes().get(pool) && !queue.isEmpty()) {
                    var r = queue.poll();
                    int needs = l.serviceTicks().get(r.kind);
                    int limit = r.kind == Kind.SEARCH ? c.dependencyTimeoutTicks() : Integer.MAX_VALUE;
                    r.endsAt = t + Math.min(needs, limit);
                    r.failed = needs > limit;
                    busy.add(r);
                }
            }
        }
        queues.values().forEach(q -> q.forEach(r -> counts.get(r.kind).unfinished++));
        running.values().forEach(b -> b.forEach(r -> counts.get(r.kind).unfinished++));
        return counts;
    }

    /** Little's law: requests in the system = arrival rate × time each one stays. */
    public static double workersNeeded(double perSecond, double seconds) { return perSecond * seconds; }

    public static final class BulkheadFull extends RuntimeException {
        private static final long serialVersionUID = 1L;
        BulkheadFull(String message) { super(message); }
    }

    /**
     * A fair Semaphore: when a place frees up it goes to the thread that has waited longest, so a latecomer can't barge in.
     * (new Semaphore(n) without "true" is unfair on purpose: faster, but a waiter can be passed over.)
     * Semaphore has no queue limit, so a counter turns away callers beyond maxQueue.
     */
    public static final class Bulkhead {
        private final Semaphore places;
        private final AtomicInteger waiting = new AtomicInteger();
        private final int maxQueue;

        public Bulkhead(int maxConcurrent, int maxQueue) {
            this.places = new Semaphore(maxConcurrent, true);
            this.maxQueue = maxQueue;
        }

        public <T> T run(Callable<T> fn, long maxWaitMillis) throws Exception {
            if (!places.tryAcquire(0, TimeUnit.MILLISECONDS)) { // the timed form respects fairness; plain tryAcquire() barges
                if (waiting.incrementAndGet() > maxQueue) {
                    waiting.decrementAndGet();
                    throw new BulkheadFull("%d waiting already".formatted(maxQueue)); // a fast "no" beats a slow failure
                }
                try {
                    if (!places.tryAcquire(maxWaitMillis, TimeUnit.MILLISECONDS)) throw new BulkheadFull("no place within " + maxWaitMillis + " ms");
                } finally {
                    waiting.decrementAndGet();
                }
            }
            try {
                return fn.call();
            } finally {
                places.release();
            }
        }

        public int waiting() { return waiting.get(); }
        public int free() { return places.availablePermits(); }
    }
}
