// A tick-by-tick simulation of a cascade, Little's law, and a bulkhead.
// The same numbers as the TypeScript lab. One tick is 100 ms.
using System.Threading.RateLimiting;

public enum Kind { Search, Profile }

public sealed record Counts(int Ok = 0, int Failed = 0, int TimedOut = 0, int Rejected = 0, int Unfinished = 0);

/// <param name="Pools">The pool each kind uses: the same name means a shared pool.</param>
/// <param name="Sizes">Workers per pool, in the order pools start work.</param>
public sealed record Config(Dictionary<Kind, string> Pools, (string Pool, int Size)[] Sizes, int QueueLimit, int DependencyTimeoutTicks);

public sealed record Load(int Ticks, Dictionary<Kind, int> ArrivalsPerTick, Dictionary<Kind, int> ServiceTicks, int ClientTimeoutTicks);

public static class Resilience
{
    sealed class Request(Kind kind, int arrived)
    {
        public Kind Kind = kind;
        public int Arrived = arrived, EndsAt;
        public bool Failed;
    }

    public static Dictionary<Kind, Counts> Simulate(Config c, Load l)
    {
        var counts = new Dictionary<Kind, Counts> { [Kind.Search] = new(), [Kind.Profile] = new() };
        var queues = c.Sizes.ToDictionary(s => s.Pool, _ => new LinkedList<Request>());
        var running = c.Sizes.ToDictionary(s => s.Pool, _ => new List<Request>());
        for (var t = 0; t < l.Ticks; t++)
        {
            foreach (var busy in running.Values) // 1. finished work frees its worker
                busy.RemoveAll(r =>
                {
                    if (r.EndsAt > t) return false;
                    counts[r.Kind] = r.Failed ? counts[r.Kind] with { Failed = counts[r.Kind].Failed + 1 } : counts[r.Kind] with { Ok = counts[r.Kind].Ok + 1 };
                    return true;
                });
            foreach (var queue in queues.Values) // 2. callers who waited too long give up (the oldest are at the front)
                while (queue.First is { } oldest && t - oldest.Value.Arrived >= l.ClientTimeoutTicks)
                {
                    counts[oldest.Value.Kind] = counts[oldest.Value.Kind] with { TimedOut = counts[oldest.Value.Kind].TimedOut + 1 };
                    queue.RemoveFirst();
                }
            foreach (var kind in (Kind[])[Kind.Search, Kind.Profile]) // 3. new requests arrive, or are turned away
            {
                var queue = queues[c.Pools[kind]];
                for (var i = 0; i < l.ArrivalsPerTick[kind]; i++)
                    if (queue.Count >= c.QueueLimit) counts[kind] = counts[kind] with { Rejected = counts[kind].Rejected + 1 }; // load shedding
                    else queue.AddLast(new Request(kind, t));
            }
            foreach (var (pool, size) in c.Sizes) // 4. free workers take requests, oldest first
                while (running[pool].Count < size && queues[pool].First is { } next)
                {
                    queues[pool].RemoveFirst();
                    var r = next.Value;
                    int needs = l.ServiceTicks[r.Kind], limit = r.Kind == Kind.Search ? c.DependencyTimeoutTicks : int.MaxValue;
                    (r.EndsAt, r.Failed) = (t + Math.Min(needs, limit), needs > limit);
                    running[pool].Add(r);
                }
        }
        foreach (var r in queues.Values.SelectMany(q => q).Concat(running.Values.SelectMany(b => b)))
            counts[r.Kind] = counts[r.Kind] with { Unfinished = counts[r.Kind].Unfinished + 1 };
        return counts;
    }

    /// <summary>Little's law: requests in the system = arrival rate × time each one stays.</summary>
    public static double WorkersNeeded(double perSecond, double seconds) => perSecond * seconds;
}

public sealed class BulkheadFull(string message) : Exception(message);

/// <summary>
/// .NET has a bulkhead built in: ConcurrencyLimiter. OldestFirst serves waiters in the order they came, and a freed
/// place goes to the queue before any newcomer. (SemaphoreSlim makes no such promise, and has no queue limit.)
/// </summary>
public sealed class Bulkhead(int maxConcurrent, int maxQueue) : IDisposable
{
    readonly ConcurrencyLimiter limiter = new(new ConcurrencyLimiterOptions
    {
        PermitLimit = maxConcurrent,
        QueueLimit = maxQueue,
        QueueProcessingOrder = QueueProcessingOrder.OldestFirst, // NewestFirst would push the oldest waiter out instead
    });

    public async Task<T> Run<T>(Func<Task<T>> fn, TimeSpan maxWait)
    {
        using var gaveUp = new CancellationTokenSource(maxWait);
        RateLimitLease lease;
        try
        {
            lease = await limiter.AcquireAsync(1, gaveUp.Token);
        }
        catch (OperationCanceledException)
        {
            throw new BulkheadFull($"no place within {maxWait.TotalMilliseconds} ms"); // cancelling took us out of the queue
        }
        using (lease) // the place goes back when the lease is disposed, even if fn throws
        {
            if (!lease.IsAcquired) throw new BulkheadFull("the queue is full"); // a fast "no" beats a slow failure
            return await fn();
        }
    }

    public (long Free, long Waiting) Stats() => limiter.GetStatistics() is { } s ? (s.CurrentAvailablePermits, s.CurrentQueuedCount) : (0, 0);

    public void Dispose() => limiter.Dispose();
}
