// Checks: the same scenarios and numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static async Task<Exception> Thrown(Func<Task> body)
{
    try { await body(); }
    catch (Exception e) { return e; }
    throw new Exception("expected an exception");
}

static TimeSpan Ms(double ms) => TimeSpan.FromMilliseconds(ms);

foreach (var s in new[] { 408, 429, 500, 502, 503, 529 }) Check(Reliability.IsRetryable(new CallError(s)), s);
foreach (var s in new[] { 400, 401, 403, 404, 422 }) Check(!Reliability.IsRetryable(new CallError(s)), s);
Check(Reliability.IsRetryable(new TimeoutException()) && Reliability.IsRetryable(new HttpRequestException("refused"))
    && !Reliability.IsRetryable(new InvalidOperationException("a bug")), "timeouts and no response");

var noon = new DateTimeOffset(2026, 10, 2, 12, 0, 0, TimeSpan.Zero);
Check(Reliability.ParseRetryAfter("7", noon) == Ms(7000), "seconds");
Check(Reliability.ParseRetryAfter("Fri, 02 Oct 2026 12:00:30 GMT", noon) == Ms(30_000), "date");
Check(Reliability.ParseRetryAfter("soon", noon) is null, "nonsense");

var ceilings = Enumerable.Range(1, 6).Select(n => Reliability.Backoff(n, 500, 10_000, () => 0.999999).TotalMilliseconds);
Check(ceilings.SequenceEqual([500.0, 1000, 2000, 4000, 8000, 10000]), string.Join(" ", ceilings));

// a transient failure is retried until it succeeds
var clock = new FakeClock();
var model = new Flaky("billing", 503, 429);
Check(await Reliability.WithRetry(_ => model.Run(), new RetryOptions(clock.Clock, () => 0.5)) == "billing", "reply");
Check(model.Calls.SequenceEqual([503, 429, 200]) && clock.Slept.SequenceEqual([250.0, 500]), string.Join(" ", clock.Slept));

// a 400 fails at once
var bad = new Flaky("", 400);
Check(await Thrown(() => Reliability.WithRetry(_ => bad.Run(), new RetryOptions(new FakeClock().Clock, () => 0.5))) is CallError { Status: 400 }
    && bad.Calls.Count == 1, "400");

// Retry-After beats our guess, and the attempts run out
var limitedClock = new FakeClock();
var limitedCalls = 0;
await Thrown(() => Reliability.WithRetry<string>(_ =>
{
    limitedCalls++;
    throw new CallError(429, Ms(7000));
}, new RetryOptions(limitedClock.Clock, Random.Shared.NextDouble)));
Check(limitedCalls == 3 && limitedClock.Slept.SequenceEqual([7000.0, 7000]), string.Join(" ", limitedClock.Slept));

// the deadline stops a wait that would overrun it
var deadlineClock = new FakeClock();
var down = new Flaky("", 503, 503, 503, 503);
await Thrown(() => Reliability.WithRetry(_ => down.Run(),
    new RetryOptions(deadlineClock.Clock, () => 0.999999, MaxAttempts: 10, BaseMs: 1000, Deadline: Ms(5000))));
Check(deadlineClock.Slept.SequenceEqual([1000.0, 2000]) && down.Calls.Count == 3, string.Join(" ", deadlineClock.Slept));

// a timeout cancels a call that would hang
var cancelled = new TaskCompletionSource();
var timeout = await Thrown(() => Reliability.WithTimeout(async ct =>
{
    try { await Task.Delay(Timeout.Infinite, ct); }
    catch (OperationCanceledException) { cancelled.SetResult(); throw; }
    return "never";
}, Ms(20)));
Check(timeout is TimeoutException, timeout);
await cancelled.Task.WaitAsync(TimeSpan.FromSeconds(5)); // the call saw its token cancelled: no request left running

// the breaker opens, then tests recovery with one trial
var breakerClock = new FakeClock();
var breaker = new Breaker(3, TimeSpan.FromSeconds(30), breakerClock.Clock);
var outage = new Flaky("", 503, 503, 503, 503, 503);
for (var i = 0; i < 3; i++) await Thrown(() => breaker.Call(outage.Run));
Check(breaker.Current == "open" && await Thrown(() => breaker.Call(outage.Run)) is CircuitOpenError && outage.Calls.Count == 3, "open");
breakerClock.T += TimeSpan.FromSeconds(30);
Check(breaker.Current == "half-open", breaker.Current);
await Thrown(() => breaker.Call(outage.Run));
Check(breaker.Current == "open", "a failed trial opens it again");
breakerClock.T += TimeSpan.FromSeconds(30);
Check(await breaker.Call(() => Task.FromResult("ok")) == "ok" && breaker.Current == "closed", "a good trial closes it");

var notTripped = new Breaker(2, TimeSpan.FromSeconds(30), new FakeClock().Clock);
var malformed = new Flaky("", 400, 400, 400);
for (var i = 0; i < 3; i++) await Thrown(() => notTripped.Call(malformed.Run));
Check(notTripped.Current == "closed", "a 400 doesn't trip it");

// fallback tries each option and won't hide a bad request
var failures = new List<string>();
var answer = await Reliability.FirstThatWorks<string>([("primary", new Flaky("", 503).Run), ("secondary", new Flaky("bug").Run)],
    (name, error) => failures.Add($"{name}: {((CallError)error).Status}"));
Check(answer == ("secondary", "bug") && failures.SequenceEqual(["primary: 503"]), string.Join(" ", failures));
Check(await Thrown(() => Reliability.FirstThatWorks<string>([("primary", new Flaky("", 400).Run), ("secondary", new Flaky("x").Run)]))
    is CallError { Status: 400 }, "400 comes straight back");

// all the layers together
var layersClock = new FakeClock();
var lines = new List<string>();
var flaky = new Flaky("", Enumerable.Repeat(503, 20).ToArray());
var classify = Reliability.Resilient("model", (_, _) => flaky.Run(), Ms(1000), new RetryOptions(layersClock.Clock, () => 0.5),
    new Breaker(4, TimeSpan.FromSeconds(30), layersClock.Clock), Evals.Keywords, lines.Add);
Check(await classify("I was charged twice.") == ("fallback", "billing") && flaky.Calls.Count == 3, flaky.Calls.Count);
Check(await classify("The app crashes on start.") == ("fallback", "bug") && flaky.Calls.Count == 4, flaky.Calls.Count);
Check(lines.SequenceEqual([
    "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
    "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
    "model: gave up (HTTP 503)",
    "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
    "model: gave up (CircuitOpenError)",
]), string.Join("\n", lines));

// a token bucket allows a burst, then paces
var bucketClock = new FakeClock();
var bucket = new TokenBucket(3, 1, bucketClock.Clock);
var started = new List<double>();
for (var i = 0; i < 6; i++)
{
    await bucket.Take();
    started.Add(bucketClock.T.TotalMilliseconds);
}
Check(started.SequenceEqual([0.0, 0, 0, 1000, 2000, 3000]), string.Join(" ", started));
Check(await Thrown(() => Task.FromResult(bucket.TryTake(5))) is ArgumentOutOfRangeException, "too big");

Console.WriteLine("all reliability checks passed");

/// <summary>Sleeping moves time forward instantly, so checks about waiting take no time.</summary>
sealed class FakeClock
{
    public TimeSpan T;
    public readonly List<double> Slept = [];
    public Clock Clock => new(() => T, (wait, _) =>
    {
        Slept.Add(wait.TotalMilliseconds);
        T += wait;
        return Task.CompletedTask;
    });
}

/// <summary>Fails with each status in turn, then answers.</summary>
sealed class Flaky(string reply, params int[] statuses)
{
    public readonly List<int> Calls = [];

    public Task<string> Run()
    {
        if (Calls.Count < statuses.Length)
        {
            var status = statuses[Calls.Count];
            Calls.Add(status);
            return Task.FromException<string>(new CallError(status));
        }
        Calls.Add(200);
        return Task.FromResult(reply);
    }
}
