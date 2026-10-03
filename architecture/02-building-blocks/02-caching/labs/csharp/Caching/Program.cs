// Checks: the same numbers as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static string Fixed(double x, int places) => x.ToString("F" + places, CultureInfo.InvariantCulture);

// A full LRU cache evicts the entry used longest ago.
var lru = new LruCache<string>(3, () => 0);
foreach (var k in new[] { "a", "b", "c" }) lru.Set(k, k.ToUpperInvariant(), 1_000);
lru.TryGet("a", out _);
lru.Set("d", "D", 1_000);
Check(lru.Keys().SequenceEqual(["c", "a", "d"]) && !lru.TryGet("b", out _), string.Join(",", lru.Keys()));

// An entry is served until its TTL runs out.
long now = 0;
var prices = new LruCache<int>(10, () => Interlocked.Read(ref now));
prices.Set("price:42", 10, 60_000);
now = 59_999;
Check(prices.TryGet("price:42", out var p) && p == 10, "before expiry");
now = 60_000;
Check(!prices.TryGet("price:42", out _), "after expiry");

// Cache-aside: the first read misses and loads, the rest hit.
var loads = 0;
var products = new CacheAside<string>(new LruCache<string>(100, () => 0), _ => { loads++; return Task.FromResult("kettle"); }, 60_000);
for (var i = 0; i < 5; i++) Check(await products.Get("product:7") == "kettle", "kettle");
Check(loads == 1 && products.Hits == 4 && products.Misses == 1 && CacheMath.HitRatio(products.Hits, products.Misses) == 0.8, (loads, products.Hits));

// The hit ratio decides what the database sees.
Check(new[] { 0.8, 0.9, 0.99 }.Select(h => Fixed(CacheMath.StoreReadsPerSecond(5_000, h), 0)).SequenceEqual(["1000", "500", "50"]), "reads");
Check(new[] { 0, 0.8, 0.99 }.Select(h => Fixed(CacheMath.AverageReadMs(h, 1, 20), 1)).SequenceEqual(["21.0", "5.0", "1.2"]), "average");
Check(CacheMath.StoreReadsPerSecond(5_000, 0) == 5_000, "cache down");

// Skewed traffic: a small cache answers most reads.
var ratios = new[] { 500, 2_500, 5_000, 10_000 }.Select(size =>
{
    var next = CacheMath.Zipf(50_000, 1, CacheMath.Seeded(1));
    var cache = new LruCache<bool>(size, () => 0);
    long hits = 0, misses = 0;
    for (var i = 0; i < 200_000; i++)
    {
        var key = next().ToString(CultureInfo.InvariantCulture);
        var hit = cache.TryGet(key, out _);
        if (!hit) cache.Set(key, true, long.MaxValue);
        if (i >= 50_000) _ = hit ? hits++ : misses++;
    }
    return Fixed(CacheMath.HitRatio(hits, misses), 2);
}).ToArray();
Check(ratios.SequenceEqual(["0.48", "0.65", "0.72", "0.80"]), string.Join(", ", ratios));

// A stampede: every waiting request loads, unless they share one load. Each load is held until all 100 callers
// have missed, so the count doesn't depend on how the tasks happen to be scheduled.
foreach (var coalesce in new[] { false, true })
{
    long clock = 0;
    var count = 0;
    var gate = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var cache = new LruCache<string>(100, () => Interlocked.Read(ref clock));
    var hot = new CacheAside<string>(cache, async _ =>
    {
        Interlocked.Increment(ref count);
        await gate.Task; // the database takes a while
        return "kettle";
    }, 60_000, coalesce);
    cache.Set("product:7", "kettle", 60_000);
    Interlocked.Exchange(ref clock, 60_000); // the entry expires as 100 reads arrive
    var readers = Enumerable.Range(0, 100).Select(_ => Task.Run(() => hot.Get("product:7"))).ToArray();
    while (hot.Misses < 100) await Task.Delay(1);
    gate.SetResult();
    Check((await Task.WhenAll(readers)).All(n => n == "kettle"), "all kettle");
    Check(count == (coalesce ? 1 : 100), (coalesce, count));
}

// Delete-on-write can still leave a stale value, until the TTL runs out.
long t = 0;
var db = new System.Collections.Concurrent.ConcurrentDictionary<string, int> { ["price:42"] = 10 };
var hasRead = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var slowRead = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var first = 1;
var cachedPrices = new CacheAside<int>(new LruCache<int>(100, () => Interlocked.Read(ref t)), async key =>
{
    var value = db[key]; // the read happens now...
    if (Interlocked.Exchange(ref first, 0) == 1)
    {
        hasRead.SetResult();
        await slowRead.Task; // ...but the answer is delayed
    }
    return value;
}, 60_000);
var reader = cachedPrices.Get("price:42");
await hasRead.Task; // 1. the reader has read 10
await cachedPrices.Write("price:42", 12, (k, v) => { db[k] = v; return Task.CompletedTask; }); // 2. saves 12, deletes (nothing)
slowRead.SetResult();
Check(await reader == 10, "the reader caches the old 10"); // 3.
Check(await cachedPrices.Get("price:42") == 10, "stale");
Interlocked.Exchange(ref t, 60_000);
Check(await cachedPrices.Get("price:42") == 12, "fresh after the TTL");

// Jitter spreads out expiry.
var random = CacheMath.Seeded(3);
var expiries = Enumerable.Range(0, 1_000).Select(_ => CacheMath.Jittered(60_000, 0.1, random)).ToArray();
var busiest = expiries.CountBy(ms => (int)(ms / 1_000)).Max(g => g.Value);
Check(expiries.Min() >= 54_000 && expiries.Max() <= 66_000 && busiest < 120, busiest);
Console.WriteLine("all caching checks passed");
