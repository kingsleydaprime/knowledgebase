package resilience;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import resilience.Resilience.Bulkhead;
import resilience.Resilience.BulkheadFull;
import resilience.Resilience.Config;
import resilience.Resilience.Kind;
import resilience.Resilience.Load;

/** Checks, run with `java -ea`. The same numbers as every other language. */
public final class ResilienceCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static final int NONE = Integer.MAX_VALUE;
    static final Load HEALTHY = new Load(600, Map.of(Kind.SEARCH, 2, Kind.PROFILE, 3), Map.of(Kind.SEARCH, 2, Kind.PROFILE, 1), 20);
    static final Load DEGRADED = new Load(600, HEALTHY.arrivalsPerTick(), Map.of(Kind.SEARCH, 50, Kind.PROFILE, 1), 20);

    static <V> LinkedHashMap<String, V> ordered(String k1, V v1, String k2, V v2) {
        var m = new LinkedHashMap<String, V>();
        m.put(k1, v1);
        if (k2 != null) m.put(k2, v2);
        return m;
    }

    static Config shared(int timeout) {
        return new Config(Map.of(Kind.SEARCH, "shared", Kind.PROFILE, "shared"), ordered("shared", 50, null, null), NONE, timeout);
    }

    public static void main(String[] args) throws Exception {
        check(Resilience.workersNeeded(20, 0.2) + Resilience.workersNeeded(30, 0.1) == 7 && Resilience.workersNeeded(20, 5) == 100, "little");

        var healthy = Resilience.simulate(shared(NONE), HEALTHY);
        check(healthy.get(Kind.SEARCH).ok == 1196 && healthy.get(Kind.PROFILE).ok == 1797, healthy);
        var cascade = Resilience.simulate(shared(NONE), DEGRADED).get(Kind.PROFILE);
        check(cascade.ok == 72 && cascade.timedOut == 1668, cascade);
        check(Resilience.simulate(shared(30), DEGRADED).get(Kind.PROFILE).ok == 270, "3 s timeout");
        var one = Resilience.simulate(shared(10), DEGRADED);
        check(one.get(Kind.PROFILE).ok == 1797 && one.get(Kind.SEARCH).failed == 1180, one);
        var walls = new Config(Map.of(Kind.SEARCH, "search", Kind.PROFILE, "profile"), ordered("search", 20, "profile", 30), 10, 30);
        var w = Resilience.simulate(walls, DEGRADED);
        check(w.get(Kind.PROFILE).ok == 1797 && w.get(Kind.SEARCH).toString().equals("ok=0 failed=380 timedOut=190 rejected=600 unfinished=30"), w);

        try (var pool = Executors.newVirtualThreadPerTaskExecutor()) { // a thread per call is cheap with virtual threads
            // A limit, a short queue, and an immediate no.
            var bulkhead = new Bulkhead(2, 1);
            var release = new CountDownLatch(1);
            var started = new CountDownLatch(2);
            var calls = new ArrayList<Future<String>>();
            for (int i = 0; i < 3; i++) calls.add(pool.submit(() -> bulkhead.run(() -> { started.countDown(); release.await(); return "done"; }, 5_000)));
            started.await();
            while (bulkhead.waiting() < 1) Thread.onSpinWait();
            try {
                bulkhead.run(() -> "never", 5_000);
                check(false, "a fourth call should be turned away");
            } catch (BulkheadFull expected) {
                // turned away at once, without waiting
            }
            release.countDown();
            for (var call : calls) check(call.get().equals("done"), "done");
            check(bulkhead.free() == 2 && bulkhead.waiting() == 0, "all places back");

            // Never more than the limit, however the threads interleave.
            var three = new Bulkhead(3, 1000);
            var running = new AtomicInteger();
            var most = new AtomicInteger();
            var all = new ArrayList<Future<Integer>>();
            for (int i = 0; i < 200; i++) {
                all.add(pool.submit(() -> three.run(() -> {
                    most.accumulateAndGet(running.incrementAndGet(), Math::max);
                    Thread.sleep(1);
                    return running.decrementAndGet();
                }, 60_000)));
            }
            for (var f : all) f.get();
            check(most.get() <= 3, most.get() + " ran at once in a bulkhead of three");

            // A caller who stops waiting leaves the queue and doesn't take a place with them.
            var small = new Bulkhead(1, 1);
            var hold = new CountDownLatch(1);
            var first = pool.submit(() -> small.run(() -> { hold.await(); return "first"; }, 5_000));
            while (small.free() == 1) Thread.onSpinWait();
            try {
                small.run(() -> "never", 20);
                check(false, "should give up");
            } catch (BulkheadFull expected) {
                check(small.waiting() == 0, "left the queue");
            }
            hold.countDown();
            check(first.get().equals("first") && small.free() == 1, "the place came back");
        }
        System.out.println("all resilience checks passed");
    }
}
