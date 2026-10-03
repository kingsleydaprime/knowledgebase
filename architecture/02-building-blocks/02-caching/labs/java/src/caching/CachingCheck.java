package caching;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.DoubleSupplier;
import java.util.function.IntSupplier;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class CachingCheck {
    private CachingCheck() {}

    private static String fixed(double x, int places) {
        return String.format(Locale.ROOT, "%." + places + "f", x);
    }

    /** Waits, without a fixed sleep, until another thread has done something. */
    private static void until(java.util.function.BooleanSupplier done) throws InterruptedException {
        while (!done.getAsBoolean()) Thread.sleep(1);
    }

    public static void main(String[] args) throws Exception {
        // A full LRU cache evicts the entry used longest ago.
        var lru = new Caching.LruCache<String>(3, () -> 0);
        for (String k : List.of("a", "b", "c")) lru.set(k, k.toUpperCase(Locale.ROOT), 1_000);
        lru.get("a");
        lru.set("d", "D", 1_000);
        assert lru.keys().equals(List.of("c", "a", "d")) : lru.keys();
        assert lru.get("b") == null;

        // An entry is served until its TTL runs out.
        var clock = new AtomicLong();
        var prices = new Caching.LruCache<Integer>(10, clock::get);
        prices.set("price:42", 10, 60_000);
        clock.set(59_999);
        assert prices.get("price:42") == 10;
        clock.set(60_000);
        assert prices.get("price:42") == null;

        // Cache-aside: the first read misses and loads, the rest hit.
        var loads = new AtomicInteger();
        var products = new Caching.CacheAside<String>(new Caching.LruCache<>(100, () -> 0), key -> {
            loads.incrementAndGet();
            return "kettle";
        }, 60_000, false);
        for (int i = 0; i < 5; i++) assert products.get("product:7").equals("kettle");
        assert loads.get() == 1 && products.hits.get() == 4 && products.misses.get() == 1;
        assert Caching.hitRatio(products.hits.get(), products.misses.get()) == 0.8;

        // The hit ratio decides what the database sees.
        List<String> reads = new ArrayList<>();
        for (double h : new double[] {0.8, 0.9, 0.99}) reads.add(fixed(Caching.storeReadsPerSecond(5_000, h), 0));
        assert reads.equals(List.of("1000", "500", "50")) : reads;
        List<String> avg = new ArrayList<>();
        for (double h : new double[] {0, 0.8, 0.99}) avg.add(fixed(Caching.averageReadMs(h, 1, 20), 1));
        assert avg.equals(List.of("21.0", "5.0", "1.2")) : avg;
        assert Caching.storeReadsPerSecond(5_000, 0) == 5_000;

        // Skewed traffic: a small cache answers most reads.
        List<String> ratios = new ArrayList<>();
        for (int size : new int[] {500, 2_500, 5_000, 10_000}) {
            IntSupplier next = Caching.zipf(50_000, 1, Caching.seeded(1));
            var cache = new Caching.LruCache<Boolean>(size, () -> 0);
            long hits = 0;
            long misses = 0;
            for (int i = 0; i < 200_000; i++) {
                String key = Integer.toString(next.getAsInt());
                boolean hit = cache.get(key) != null;
                if (!hit) cache.set(key, true, Long.MAX_VALUE);
                if (i >= 50_000) {
                    if (hit) hits++;
                    else misses++;
                }
            }
            ratios.add(fixed(Caching.hitRatio(hits, misses), 2));
        }
        assert ratios.equals(List.of("0.48", "0.65", "0.72", "0.80")) : ratios;

        // A stampede: every waiting request loads, unless they share one load. Each load is held at a gate until
        // all 100 callers have missed, so the count doesn't depend on how the threads happen to be scheduled.
        for (boolean coalesce : new boolean[] {false, true}) {
            var now = new AtomicLong();
            var count = new AtomicInteger();
            var gate = new CountDownLatch(1);
            var cache = new Caching.LruCache<String>(100, now::get);
            var hot = new Caching.CacheAside<String>(cache, key -> {
                count.incrementAndGet();
                gate.await(); // the database takes a while
                return "kettle";
            }, 60_000, coalesce);
            cache.set("product:7", "kettle", 60_000);
            now.set(60_000); // the entry expires...
            try (var threads = Executors.newVirtualThreadPerTaskExecutor()) {
                List<Future<String>> results = new ArrayList<>();
                for (int i = 0; i < 100; i++) results.add(threads.submit(() -> hot.get("product:7"))); // ...as 100 arrive
                until(() -> hot.misses.get() == 100);
                gate.countDown();
                for (var r : results) assert r.get().equals("kettle");
            }
            assert count.get() == (coalesce ? 1 : 100) : coalesce + ": " + count.get() + " loads";
        }

        // Delete-on-write can still leave a stale value, until the TTL runs out.
        var time = new AtomicLong();
        var db = new ConcurrentHashMap<>(new HashMap<>(java.util.Map.of("price:42", 10)));
        var hasRead = new CountDownLatch(1);
        var slowRead = new CountDownLatch(1);
        var firstLoad = new java.util.concurrent.atomic.AtomicBoolean(true);
        var cachedPrices = new Caching.CacheAside<Integer>(new Caching.LruCache<>(100, time::get), key -> {
            int value = db.get(key); // the read happens now...
            if (firstLoad.getAndSet(false)) {
                hasRead.countDown();
                slowRead.await(); // ...but the answer is delayed
            }
            return value;
        }, 60_000, false);
        try (var threads = Executors.newVirtualThreadPerTaskExecutor()) {
            var reader = threads.submit(() -> cachedPrices.get("price:42"));
            hasRead.await(); // 1. the reader has read 10
            cachedPrices.write("price:42", 12, db::put); // 2. the writer saves 12 and deletes (nothing)
            slowRead.countDown();
            assert reader.get() == 10; // 3. the reader caches the old 10
        }
        assert cachedPrices.get("price:42") == 10; // stale
        time.set(60_000);
        assert cachedPrices.get("price:42") == 12;

        // Jitter spreads out expiry.
        DoubleSupplier random = Caching.seeded(3);
        var perSecond = new HashMap<Integer, Integer>();
        double lo = Double.MAX_VALUE;
        double hi = 0;
        for (int i = 0; i < 1_000; i++) {
            double ms = Caching.jittered(60_000, 0.1, random);
            lo = Math.min(lo, ms);
            hi = Math.max(hi, ms);
            perSecond.merge((int) (ms / 1_000), 1, Integer::sum);
        }
        int busiest = perSecond.values().stream().mapToInt(Integer::intValue).max().orElseThrow();
        assert lo >= 54_000 && hi <= 66_000 && busiest < 120 : busiest;
        System.out.println("all caching checks passed");
    }
}
