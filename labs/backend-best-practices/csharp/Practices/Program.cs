using System.Threading.RateLimiting;

// Microsoft ships a token bucket in System.Threading.RateLimiting (included with ASP.NET Core).
// ASP.NET Core wraps it as middleware: builder.Services.AddRateLimiter(...) + app.UseRateLimiter().
static TokenBucketRateLimiter Limiter(TimeSpan period) => new(new TokenBucketRateLimiterOptions
{
    TokenLimit = 3,               // the burst
    TokensPerPeriod = 1,          // with a 2 s period: 0.5 tokens per second
    ReplenishmentPeriod = period,
    AutoReplenishment = false,    // no background timer; TryReplenish() refills
    QueueLimit = 0,               // refuse rather than queue
});

using var limiter = Limiter(TimeSpan.FromSeconds(2));
var results = Enumerable.Range(0, 4).Select(_ => limiter.AttemptAcquire().IsAcquired).ToList();
Check(results.SequenceEqual([true, true, true, false]), "three allowed, then refused");
using (var refused = limiter.AttemptAcquire())
{
    Check(refused.TryGetMetadata(MetadataName.RetryAfter, out var retryAfter) && retryAfter == TimeSpan.FromSeconds(2),
        "Retry-After is 2 seconds");
}

// The limiter reads the real clock: TryReplenish adds tokens only once a real period has passed.
// So a refill test has to wait — kept short here with a 100 ms period.
using var fast = Limiter(TimeSpan.FromMilliseconds(100));
for (var i = 0; i < 3; i++) fast.AttemptAcquire();
fast.TryReplenish();
Check(!fast.AttemptAcquire().IsAcquired, "no refill before the period has really passed");
Thread.Sleep(150);
fast.TryReplenish();
Check(fast.AttemptAcquire().IsAcquired, "refilled after the period");
Console.WriteLine("ok: the built-in TokenBucketRateLimiter");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }
