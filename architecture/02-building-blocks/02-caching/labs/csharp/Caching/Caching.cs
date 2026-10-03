// A cache in front of a slow store: an LRU cache with expiry, cache-aside with request coalescing, and the
// arithmetic that says how much a cache takes off the database. The same numbers as the TypeScript lab.
using System.Collections.Concurrent;

/// <summary>
/// At most <c>max</c> entries, evicting the least recently used. .NET's MemoryCache has no LRU (it compacts by
/// priority), so a LinkedList keeps the order and a Dictionary finds each key's node in O(1).
/// </summary>
public sealed class LruCache<V>
{
    private readonly record struct Entry(string Key, V Value, long Expires);

    private readonly int _max;
    private readonly Func<long> _now; // milliseconds
    private readonly LinkedList<Entry> _order = new(); // first: least recently used
    private readonly Dictionary<string, LinkedListNode<Entry>> _entries = [];
    private readonly Lock _lock = new();

    public LruCache(int max, Func<long> now)
    {
        ArgumentOutOfRangeException.ThrowIfLessThan(max, 1);
        (_max, _now) = (max, now);
    }

    public bool TryGet(string key, out V value)
    {
        lock (_lock)
        {
            value = default!;
            if (!_entries.TryGetValue(key, out var node)) return false;
            _order.Remove(node);
            if (_now() >= node.Value.Expires)
            {
                _entries.Remove(key); // expired: treat it as a miss
                return false;
            }
            _order.AddLast(node); // now the most recently used
            value = node.Value.Value;
            return true;
        }
    }

    public void Set(string key, V value, long ttlMs)
    {
        lock (_lock)
        {
            if (_entries.Remove(key, out var old)) _order.Remove(old);
            var expires = ttlMs == long.MaxValue ? long.MaxValue : _now() + ttlMs; // "never" mustn't overflow
            _entries[key] = _order.AddLast(new Entry(key, value, expires));
            if (_entries.Count > _max)
            {
                _entries.Remove(_order.First!.Value.Key);
                _order.RemoveFirst();
            }
        }
    }

    public void Delete(string key)
    {
        lock (_lock)
        {
            if (_entries.Remove(key, out var node)) _order.Remove(node);
        }
    }

    /// <summary>Least recently used first.</summary>
    public string[] Keys()
    {
        lock (_lock) return _order.Select(e => e.Key).ToArray();
    }
}

/// <summary>Check the cache; on a miss, load and fill it. With coalesce, concurrent misses share one load.</summary>
public sealed class CacheAside<V>(LruCache<V> cache, Func<string, Task<V>> load, long ttlMs, bool coalesce = false)
{
    private readonly ConcurrentDictionary<string, Lazy<Task<V>>> _inFlight = new();
    private long _hits, _misses;
    public long Hits => Interlocked.Read(ref _hits);
    public long Misses => Interlocked.Read(ref _misses);

    public async Task<V> Get(string key)
    {
        if (cache.TryGet(key, out var cached))
        {
            Interlocked.Increment(ref _hits);
            return cached;
        }
        if (!coalesce)
        {
            Interlocked.Increment(ref _misses);
            return await LoadAndFill(key);
        }
        // GetOrAdd may build more than one Lazy under a race, but only the one it stores is ever started.
        var mine = new Lazy<Task<V>>(() => LoadAndFill(key));
        var shared = _inFlight.GetOrAdd(key, mine);
        Interlocked.Increment(ref _misses);
        try
        {
            return await shared.Value;
        }
        finally
        {
            _inFlight.TryRemove(new KeyValuePair<string, Lazy<Task<V>>>(key, shared)); // only if it's still this load
        }
    }

    private async Task<V> LoadAndFill(string key)
    {
        var value = await load(key);
        cache.Set(key, value, ttlMs);
        return value;
    }

    /// <summary>Write to the store first, then delete the cached copy.</summary>
    public async Task Write(string key, V value, Func<string, V, Task> save)
    {
        await save(key, value);
        cache.Delete(key);
    }
}

public static class CacheMath
{
    public static double HitRatio(long hits, long misses) => (double)hits / (hits + misses);

    public static double AverageReadMs(double ratio, double cacheMs, double storeMs) => cacheMs + (1 - ratio) * storeMs;

    public static double StoreReadsPerSecond(double readsPerSecond, double ratio) => readsPerSecond * (1 - ratio);

    public static double Jittered(double ttlMs, double spread, Func<double> random) => ttlMs * (1 - spread + 2 * spread * random());

    /// <summary>Key k is requested in proportion to 1/(k+1)^s.</summary>
    public static Func<int> Zipf(int keys, double s, Func<double> random)
    {
        var cumulative = new double[keys];
        var total = 0.0;
        for (var k = 0; k < keys; k++) cumulative[k] = total += 1 / Math.Pow(k + 1, s);
        return () =>
        {
            var i = Array.BinarySearch(cumulative, random() * total);
            return i >= 0 ? i : ~i; // not found: BinarySearch returns the complement of the insertion point
        };
    }

    /// <summary>mulberry32, the same generator as week 1's lab.</summary>
    public static Func<double> Seeded(uint seed)
    {
        var a = seed;
        return () =>
        {
            a += 0x6d2b79f5;
            var t = (a ^ (a >> 15)) * (a | 1);
            t ^= t + (t ^ (t >> 7)) * (t | 61);
            return (t ^ (t >> 14)) / 4294967296.0;
        };
    }
}
