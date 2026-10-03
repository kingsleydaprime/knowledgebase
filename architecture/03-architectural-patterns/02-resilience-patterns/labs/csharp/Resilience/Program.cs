// Checks: the same numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

const int None = int.MaxValue;
var healthy = new Load(600, new() { [Kind.Search] = 2, [Kind.Profile] = 3 }, new() { [Kind.Search] = 2, [Kind.Profile] = 1 }, 20);
var degraded = healthy with { ServiceTicks = new() { [Kind.Search] = 50, [Kind.Profile] = 1 } };
Config Shared(int timeout) => new(new() { [Kind.Search] = "shared", [Kind.Profile] = "shared" }, [("shared", 50)], None, timeout);

Check(Resilience.WorkersNeeded(20, 0.2) + Resilience.WorkersNeeded(30, 0.1) == 7 && Resilience.WorkersNeeded(20, 5) == 100, "little");
var h = Resilience.Simulate(Shared(None), healthy);
Check(h[Kind.Search].Ok == 1196 && h[Kind.Profile].Ok == 1797, h[Kind.Search]);
var cascade = Resilience.Simulate(Shared(None), degraded)[Kind.Profile];
Check(cascade.Ok == 72 && cascade.TimedOut == 1668, cascade);
Check(Resilience.Simulate(Shared(30), degraded)[Kind.Profile].Ok == 270, "3 s timeout");
var one = Resilience.Simulate(Shared(10), degraded);
Check(one[Kind.Profile].Ok == 1797 && one[Kind.Search].Failed == 1180, one[Kind.Search]);
var walls = Resilience.Simulate(new(new() { [Kind.Search] = "search", [Kind.Profile] = "profile" }, [("search", 20), ("profile", 30)], 10, 30), degraded);
Check(walls[Kind.Profile].Ok == 1797 && walls[Kind.Search] == new Counts(0, 380, 190, 600, 30), walls[Kind.Search]);

// A limit, a short queue, an immediate no, and a freed place going to the waiter, not a latecomer.
using (var bulkhead = new Bulkhead(1, 2))
{
    var order = new List<string>();
    var gates = new System.Collections.Concurrent.ConcurrentDictionary<string, TaskCompletionSource<string>>(); // read from other threads
    Task<string> Call(string name)
    {
        gates[name] = new(TaskCreationOptions.RunContinuationsAsynchronously);
        return bulkhead.Run(() => { lock (order) order.Add(name); return gates[name].Task; }, TimeSpan.FromSeconds(5));
    }
    bool Started(string name) { lock (order) return order.Contains(name); }
    var first = Call("first");
    var waiter = Call("waiter");
    var other = Call("other");
    Check(bulkhead.Stats() == (0, 2), bulkhead.Stats());
    try
    {
        await bulkhead.Run(() => Task.FromResult("never"), TimeSpan.FromSeconds(5));
        Check(false, "a fourth call should be turned away");
    }
    catch (BulkheadFull) { }
    gates["first"].SetResult("done");
    await first;
    var latecomer = Call("latecomer"); // arrives just as first finishes
    foreach (var name in (string[])["waiter", "other", "latecomer"])
    {
        while (!Started(name)) await Task.Delay(1);
        gates[name].SetResult("done");
    }
    await Task.WhenAll(waiter, other, latecomer);
    Check(order.SequenceEqual(["first", "waiter", "other", "latecomer"]), string.Join(",", order));
    Check(bulkhead.Stats() == (1, 0), bulkhead.Stats());
}

// A caller who stops waiting leaves the queue and doesn't take a place with them.
using (var bulkhead = new Bulkhead(1, 1))
{
    var hold = new TaskCompletionSource<int>();
    var first = bulkhead.Run(() => hold.Task, TimeSpan.FromSeconds(5));
    try
    {
        await bulkhead.Run(() => Task.FromResult(0), TimeSpan.FromMilliseconds(20));
        Check(false, "should give up");
    }
    catch (BulkheadFull) { Check(bulkhead.Stats() == (0, 0), bulkhead.Stats()); }
    hold.SetResult(1);
    await first;
    Check(bulkhead.Stats() == (1, 0), "the place came back");
}

// Never more than the limit, however the tasks interleave.
using (var bulkhead = new Bulkhead(3, 1000))
{
    int running = 0, most = 0;
    await Task.WhenAll(Enumerable.Range(0, 200).Select(_ => Task.Run(() => bulkhead.Run(async () =>
    {
        var n = Interlocked.Increment(ref running);
        for (var m = most; n > m && Interlocked.CompareExchange(ref most, n, m) != m; m = most) { }
        await Task.Delay(1);
        return Interlocked.Decrement(ref running);
    }, TimeSpan.FromMinutes(1)))));
    Check(most <= 3, $"{most} ran at once in a bulkhead of three");
}

Console.WriteLine("all resilience checks passed");
