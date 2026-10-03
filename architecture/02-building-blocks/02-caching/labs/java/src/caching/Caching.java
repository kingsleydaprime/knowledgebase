package caching;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.DoubleSupplier;
import java.util.function.IntSupplier;
import java.util.function.LongSupplier;

/** A cache in front of a slow store. The same numbers as the TypeScript lab. */
public final class Caching {
    private Caching() {}

    private record Entry<V>(V value, long expires) {}

    /**
     * At most {@code max} entries, evicting the least recently used. A LinkedHashMap in access order does the
     * bookkeeping: every get moves the key to the end, and removeEldestEntry drops the front when it's full.
     * A get changes that order, so even reads must hold the lock.
     */
    public static final class LruCache<V> {
        private final LongSupplier now; // milliseconds
        private final LinkedHashMap<String, Entry<V>> entries;

        public LruCache(int max, LongSupplier now) {
            if (max < 1) throw new IllegalArgumentException("a cache needs room for at least one entry");
            this.now = now;
            this.entries = new LinkedHashMap<>(16, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<String, Entry<V>> eldest) {
                    return size() > max;
                }
            };
        }

        public synchronized V get(String key) {
            Entry<V> e = entries.get(key);
            if (e == null) return null;
            if (now.getAsLong() >= e.expires()) {
                entries.remove(key);
                return null;
            }
            return e.value();
        }

        public synchronized void set(String key, V value, long ttlMs) {
            long expires = ttlMs == Long.MAX_VALUE ? Long.MAX_VALUE : now.getAsLong() + ttlMs; // "forever" mustn't overflow
            entries.remove(key); // so a re-set key counts as newly used
            entries.put(key, new Entry<>(value, expires));
        }

        public synchronized void delete(String key) {
            entries.remove(key);
        }

        /** Least recently used first. */
        public synchronized List<String> keys() {
            return new ArrayList<>(entries.keySet());
        }
    }

    @FunctionalInterface
    public interface Loader<V> {
        V load(String key) throws InterruptedException;
    }

    /** Check the cache; on a miss, load and fill it. With coalesce, concurrent misses share one load. */
    public static final class CacheAside<V> {
        private final LruCache<V> cache;
        private final Loader<V> load;
        private final long ttlMs;
        private final boolean coalesce;
        private final ConcurrentHashMap<String, CompletableFuture<V>> inFlight = new ConcurrentHashMap<>();
        public final AtomicLong hits = new AtomicLong();
        public final AtomicLong misses = new AtomicLong();

        public CacheAside(LruCache<V> cache, Loader<V> load, long ttlMs, boolean coalesce) {
            this.cache = cache;
            this.load = load;
            this.ttlMs = ttlMs;
            this.coalesce = coalesce;
        }

        public V get(String key) throws InterruptedException {
            V cached = cache.get(key);
            if (cached != null) {
                hits.incrementAndGet();
                return cached;
            }
            if (!coalesce) {
                misses.incrementAndGet();
                return loadAndFill(key);
            }
            var mine = new CompletableFuture<V>();
            var pending = inFlight.putIfAbsent(key, mine); // atomic: exactly one caller's future goes in
            misses.incrementAndGet();
            if (pending != null) return pending.join(); // someone is already loading this key: wait for their answer
            try {
                V value = loadAndFill(key);
                mine.complete(value);
                return value;
            } catch (InterruptedException | RuntimeException e) {
                mine.completeExceptionally(e);
                throw e;
            } finally {
                inFlight.remove(key, mine); // a failed load isn't kept: the next miss retries
            }
        }

        private V loadAndFill(String key) throws InterruptedException {
            V value = load.load(key);
            cache.set(key, value, ttlMs);
            return value;
        }

        /** Write to the store first, then delete the cached copy. */
        public void write(String key, V value, java.util.function.BiConsumer<String, V> save) {
            save.accept(key, value);
            cache.delete(key);
        }
    }

    public static double hitRatio(long hits, long misses) {
        return (double) hits / (hits + misses);
    }

    public static double averageReadMs(double ratio, double cacheMs, double storeMs) {
        return cacheMs + (1 - ratio) * storeMs;
    }

    public static double storeReadsPerSecond(double readsPerSecond, double ratio) {
        return readsPerSecond * (1 - ratio);
    }

    public static double jittered(double ttlMs, double spread, DoubleSupplier random) {
        return ttlMs * (1 - spread + 2 * spread * random.getAsDouble());
    }

    /** Key k is requested in proportion to 1/(k+1)^s. */
    public static IntSupplier zipf(int keys, double s, DoubleSupplier random) {
        double[] cumulative = new double[keys];
        double total = 0;
        for (int k = 0; k < keys; k++) cumulative[k] = total += 1 / Math.pow(k + 1, s);
        double sum = total;
        return () -> {
            int i = Arrays.binarySearch(cumulative, random.getAsDouble() * sum);
            return i >= 0 ? i : -i - 1; // not found: binarySearch returns -(insertion point) - 1
        };
    }

    /** mulberry32, the same generator as week 1's lab. */
    public static DoubleSupplier seeded(int seed) {
        int[] a = {seed};
        return () -> {
            a[0] += 0x6d2b79f5;
            int t = a[0];
            t = (t ^ (t >>> 15)) * (t | 1);
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            return Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
        };
    }
}
