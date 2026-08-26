# Async, Await and Tasks

> **[Intermediate → Advanced]** · C# invented the model everyone copied. Here's what it actually does, and the four ways to deadlock with it.

`async`/`await` shipped in C# 5 (2012) and was subsequently adopted by JavaScript, Python, Rust, Swift and Kotlin → [[languages/06-python/17-asyncio-in-depth|Python's version]].

## What it actually does

```csharp
public async Task<User> GetUserAsync(int id)
{
    var response = await _http.GetAsync($"/users/{id}");    // suspends here
    var json = await response.Content.ReadAsStringAsync();
    return JsonSerializer.Deserialize<User>(json)!;
}
```

**The compiler rewrites the method into a state machine.** At each `await`, if the awaited thing isn't finished, the method **returns** to its caller and registers a continuation. When the operation completes, the continuation resumes from that point.

**The crucial consequence: `await` does not block a thread.** The thread is released back to the pool. That's the entire point — a server handling 10,000 concurrent requests doesn't need 10,000 threads → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]].

## Async is not parallel

**The most common misunderstanding, and the same one as everywhere:**

```csharp
var a = await FetchA();      // sequential — 2 seconds
var b = await FetchB();

var ta = FetchA();           // both start
var tb = FetchB();
var (a, b) = (await ta, await tb);   // ~1 second

var results = await Task.WhenAll(FetchA(), FetchB());   // idiomatic
```

**`await` means "wait here".** Sequential awaits are async syntax with synchronous behaviour → [[languages/06-python/17-asyncio-in-depth|the same bug in Python]].

**`Task.WhenAll` vs `Task.WhenAny`:** all, or the first to complete. **`WhenAll` throws only the *first* exception** — the `Task`'s `Exception` property holds the rest as an `AggregateException`, and it's easy to lose them.

## The four ways to get this wrong

**1. `.Result` / `.Wait()` — deadlock.**

```csharp
var user = GetUserAsync(1).Result;      // ✗ deadlocks in some contexts
```

In a **synchronisation context** that pins continuations to one thread (classic ASP.NET, WinForms, WPF), the continuation waits for that thread, which is blocked waiting for the task. **Deadlock.** ASP.NET Core removed the context, so it often *appears* to work now — but it still consumes a pool thread doing nothing.

**The rule: async all the way down.** If you're calling async code, be async. `GetAwaiter().GetResult()` only at the true top of a console app.

**2. `async void` — uncatchable exceptions.**

```csharp
public async void DoWork()      // ✗ almost always wrong
```

An exception in `async void` cannot be caught by the caller — there's no Task to observe — and it **crashes the process**. Use `async Task`. **The single legitimate exception is an event handler**, whose signature forces `void`; wrap its body in try/catch.

**3. Blocking inside async.** `Thread.Sleep`, synchronous file I/O, or a CPU-heavy loop inside an async method occupies the thread and defeats the purpose.

**4. Fire-and-forget without observing.** An unawaited `Task` whose exception is never observed is silently swallowed. Keep a reference, or `await` it.

## `ConfigureAwait(false)`

```csharp
await SomethingAsync().ConfigureAwait(false);
```

**"Don't bother resuming on the original synchronisation context."** In **library** code this avoids needless context capture and removes a deadlock vector — so libraries should use it consistently.

**In ASP.NET Core application code it's unnecessary** (there's no context). In UI code you *need* the context to touch controls, so don't use it there.

**The short version: libraries yes, ASP.NET Core apps no, UI code no.**

## Cancellation

**Every async API that can take a `CancellationToken` should**, and you should pass it down:

```csharp
public async Task<Data> LoadAsync(CancellationToken ct = default)
{
    var res = await _http.GetAsync(url, ct);
    ct.ThrowIfCancellationRequested();
    return await Parse(res, ct);
}

using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
await LoadAsync(cts.Token);        // a timeout, expressed as cancellation
```

**Cancellation is cooperative** — nothing is forcibly stopped. A token ignored is a token that does nothing, which is why "pass it all the way down" matters.

**`OperationCanceledException` is expected**, not a failure. Don't log it as an error.

## `ValueTask` and hot paths

`Task` is a class — every async call allocates one. **`ValueTask<T>` avoids the allocation when the result is already available** (a cache hit, say).

**Use it only when profiling says so.** It has real restrictions: **await it exactly once**, never `.Result` it, don't store it. Misuse produces subtle corruption. **`Task` is the default; `ValueTask` is an optimisation** → [[languages/07-csharp/13-performance-and-the-runtime|note 13]].

## Where the model actually helps

**The one-sentence justification:** on a server, `await` frees the thread while waiting on I/O, so throughput is bounded by the work rather than by the thread count. Thread-per-request tops out in the low thousands; async scales past that on the same hardware.

**And where it doesn't:** CPU-bound work. `Task.Run` moves it to a pool thread so the caller isn't blocked, but the work still costs a thread — async doesn't create parallelism, it releases threads during waits → [[languages/06-python/12-concurrency-and-the-gil|the same distinction in Python]].

## Related
- [[languages/07-csharp/06-delegates-events-and-lambdas|delegates]] — `IAsyncEnumerable`
- [[backend/01-foundations/04-runtime-and-concurrency-models|runtime and concurrency models]]
- [[languages/06-python/17-asyncio-in-depth|asyncio]] · [[languages/01-java/README|Java's virtual threads]]

*Source: [reference] — from the .NET async documentation, Aug 2026.*
