// Retry, timeout, circuit breaker, fallback and token bucket around an async model call.
// The same behaviour, and the same numbers, as the TypeScript lab.
using System.Globalization;

/// <summary>A failed model call: the HTTP status, and the Retry-After wait if the server sent one.</summary>
public sealed class CallError(int status, TimeSpan? retryAfter = null) : Exception($"HTTP {status}")
{
    public int Status => status;
    public TimeSpan? RetryAfter => retryAfter;
}

public sealed class CircuitOpenError() : Exception("circuit open: not calling a dependency that keeps failing");

/// <summary>Time, so tests can replace it. In production code, .NET's TimeProvider does this job.</summary>
public sealed record Clock(Func<TimeSpan> Now, Func<TimeSpan, CancellationToken, Task> Sleep)
{
    public static readonly Clock Real = new(() => TimeSpan.FromTicks(Environment.TickCount64 * TimeSpan.TicksPerMillisecond),
        (wait, ct) => Task.Delay(wait, ct));
}

public sealed record RetryOptions(Clock Clock, Func<double> Random, int MaxAttempts = 3, int BaseMs = 500, int CapMs = 10_000,
    TimeSpan? Deadline = null);

public static class Reliability
{
    public static bool IsRetryable(Exception error) => error switch
    {
        CallError e => e.Status is 408 or 429 or >= 500,
        TimeoutException => true, // our own deadline for one attempt
        TaskCanceledException { InnerException: TimeoutException } => true, // HttpClient.Timeout
        HttpRequestException { StatusCode: null } => true, // no response at all
        _ => false,
    };

    /// <summary>Seconds or an HTTP date, as a wait.</summary>
    public static TimeSpan? ParseRetryAfter(string? header, DateTimeOffset now)
    {
        if (string.IsNullOrWhiteSpace(header)) return null;
        if (double.TryParse(header, NumberStyles.Float, CultureInfo.InvariantCulture, out var seconds))
            return TimeSpan.FromSeconds(Math.Max(0, seconds));
        if (DateTimeOffset.TryParseExact(header.Trim(), "r", CultureInfo.InvariantCulture, DateTimeStyles.None, out var date))
            return date > now ? date - now : TimeSpan.Zero;
        return null;
    }

    /// <summary>Full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)).</summary>
    public static TimeSpan Backoff(int attempt, int baseMs, int capMs, Func<double> random) =>
        TimeSpan.FromMilliseconds(Math.Round(random() * Math.Min(capMs, baseMs * Math.Pow(2, attempt - 1))));

    public static async Task<T> WithRetry<T>(Func<int, Task<T>> call, RetryOptions o,
        Action<int, TimeSpan, Exception>? onRetry = null, CancellationToken ct = default)
    {
        var started = o.Clock.Now();
        for (var attempt = 1; ; attempt++)
        {
            try
            {
                return await call(attempt);
            }
            catch (Exception error) when (IsRetryable(error) && attempt < o.MaxAttempts)
            {
                var wait = (error as CallError)?.RetryAfter ?? Backoff(attempt, o.BaseMs, o.CapMs, o.Random); // the server knows best
                if (o.Deadline is { } deadline && o.Clock.Now() - started + wait > deadline) throw;
                onRetry?.Invoke(attempt, wait, error);
                await o.Clock.Sleep(wait, ct);
            }
        }
    }

    /// <summary>One attempt with its own deadline. The token cancels the request; WaitAsync releases the
    /// caller on time even if the call ignores the token.</summary>
    public static async Task<T> WithTimeout<T>(Func<CancellationToken, Task<T>> call, TimeSpan limit, CancellationToken ct = default)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(limit);
        try
        {
            return await call(cts.Token).WaitAsync(cts.Token);
        }
        catch (OperationCanceledException) when (!ct.IsCancellationRequested)
        {
            throw new TimeoutException($"timed out after {limit.TotalMilliseconds} ms");
        }
    }

    public static async Task<(string By, T Value)> FirstThatWorks<T>(IEnumerable<(string Name, Func<Task<T>> Run)> options,
        Action<string, Exception>? onFailure = null)
    {
        var errors = new List<Exception>();
        foreach (var (name, run) in options)
        {
            try
            {
                return (name, await run());
            }
            catch (Exception error) when (error is not CallError { Status: 400 or 422 }) // a bad request would fail everywhere
            {
                onFailure?.Invoke(name, error);
                errors.Add(error);
            }
        }
        throw new AggregateException($"all {errors.Count} options failed", errors);
    }

    /// <summary>fallback( retry( breaker( timeout( call ) ) ) ), as in the main lesson.</summary>
    public static Func<string, Task<(string By, string Value)>> Resilient(string name, Func<string, CancellationToken, Task<string>> call,
        TimeSpan timeout, RetryOptions retry, Breaker breaker, Func<string, string>? fallback, Action<string> log) =>
        input =>
        {
            var options = new List<(string, Func<Task<string>>)>
            {
                (name, () => WithRetry(_ => breaker.Call(() => WithTimeout(ct => call(input, ct), timeout)), retry,
                    (attempt, wait, error) => log($"{name}: attempt {attempt} failed ({Describe(error)}), retrying in {wait.TotalMilliseconds} ms"))),
            };
            if (fallback is not null) options.Add(("fallback", () => Task.FromResult(fallback(input))));
            return FirstThatWorks(options, (by, error) => log($"{by}: gave up ({Describe(error)})"));
        };

    static string Describe(Exception error) => error is CallError e ? $"HTTP {e.Status}" : error.GetType().Name;
}

public sealed class Breaker(int threshold, TimeSpan coolDown, Clock clock)
{
    readonly Lock gate = new();
    string state = "closed";
    int failures;
    TimeSpan openedAt;
    bool trialRunning;

    public string Current
    {
        get
        {
            lock (gate) return Refresh();
        }
    }

    string Refresh()
    {
        if (state == "open" && clock.Now() - openedAt >= coolDown) state = "half-open";
        return state;
    }

    public async Task<T> Call<T>(Func<Task<T>> fn)
    {
        string before;
        lock (gate)
        {
            before = Refresh();
            if (before == "open" || (before == "half-open" && trialRunning)) throw new CircuitOpenError();
            if (before == "half-open") trialRunning = true;
        }
        try
        {
            var result = await fn();
            lock (gate) (state, failures) = ("closed", 0);
            return result;
        }
        catch (Exception error) when (Reliability.IsRetryable(error)) // a 400 is our bug, not the provider's outage
        {
            lock (gate)
            {
                failures++;
                if (before == "half-open" || failures >= threshold) (state, openedAt) = ("open", clock.Now());
            }
            throw;
        }
        finally
        {
            if (before == "half-open") lock (gate) trialRunning = false;
        }
    }
}

/// <summary>System.Threading.RateLimiting.TokenBucketRateLimiter is the built-in version of this.</summary>
public sealed class TokenBucket
{
    readonly Lock gate = new();
    readonly double capacity, perSecond;
    readonly Clock clock;
    double tokens;
    TimeSpan last;

    public TokenBucket(double capacity, double perSecond, Clock clock)
    {
        (this.capacity, this.perSecond, this.clock) = (capacity, perSecond, clock);
        (tokens, last) = (capacity, clock.Now());
    }

    public TimeSpan TryTake(double cost = 1)
    {
        ArgumentOutOfRangeException.ThrowIfGreaterThan(cost, capacity);
        lock (gate)
        {
            var now = clock.Now();
            tokens = Math.Min(capacity, tokens + (now - last).TotalSeconds * perSecond);
            last = now;
            if (tokens >= cost)
            {
                tokens -= cost;
                return TimeSpan.Zero;
            }
            return TimeSpan.FromMilliseconds(Math.Ceiling((cost - tokens) / perSecond * 1000));
        }
    }

    public async Task Take(double cost = 1, CancellationToken ct = default)
    {
        for (var wait = TryTake(cost); wait > TimeSpan.Zero; wait = TryTake(cost)) await clock.Sleep(wait, ct);
    }
}
