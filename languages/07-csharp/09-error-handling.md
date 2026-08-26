# Error Handling

> **[Intermediate]** · Exceptions, the ones you should never catch, and the result-type debate.

```csharp
try
{
    var data = await LoadAsync(path, ct);
    Process(data);
}
catch (FileNotFoundException ex)
{
    _logger.LogWarning(ex, "Config missing at {Path}, using defaults", path);
    Process(Defaults);
}
catch (JsonException ex)
{
    throw new ConfigurationException($"Malformed config at {path}", ex);   // chain it
}
finally
{
    _semaphore.Release();          // runs regardless
}
```

## The hierarchy

`Exception` at the root. The ones worth knowing:

- **`ArgumentException`** / `ArgumentNullException` / `ArgumentOutOfRangeException` — **the caller's fault**
- **`InvalidOperationException`** — right arguments, wrong state ("the connection isn't open")
- **`NullReferenceException`** — a bug, always. Never catch it; fix it → [[languages/07-csharp/02-the-type-system|nullable reference types]]
- **`OperationCanceledException`** — **expected**, not a failure → [[languages/07-csharp/07-async-await-and-tasks|note 07]]
- **`OutOfMemoryException`**, `StackOverflowException` — **you cannot meaningfully handle these.** `StackOverflowException` can't even be caught; the process dies

**`throw;` vs `throw ex;`** — a small syntax difference with a real consequence:

```csharp
catch (Exception ex) { LogIt(ex); throw; }      // ✓ preserves the original stack trace
catch (Exception ex) { LogIt(ex); throw ex; }   // ✗ RESETS it to this line
```

**`throw ex;` destroys the evidence you need.** Use bare `throw;` to rethrow, or wrap with an inner exception.

## What not to do

```csharp
try { DoThing(); } catch { }              // ✗ swallows everything, silently
catch (Exception) { return null; }        // ✗ turns a failure into a null
```

**Same argument as [[languages/06-python/09-errors-and-exceptions|Python's `except: pass`]]:** you catch your own bugs, discard the diagnostics, and continue in an unknown state. The failure then surfaces somewhere unrelated.

**Catching broadly is legitimate at a boundary** — the top of a request handler, a message-consumer loop, a background worker — precisely so one bad item doesn't kill the process. **Everywhere else it's hiding something.** And at that boundary, **log with the exception object**, not `ex.Message`, or you lose the stack trace.

## Exception filters

C#-specific and genuinely useful:

```csharp
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
{
    await Task.Delay(backoff, ct);
}
```

**`when` filters run *before* the stack unwinds**, so if the filter returns false the exception continues with its original stack intact. That's better than catching, testing and rethrowing — and it's a nice diagnostic trick: `catch (Exception ex) when (Log(ex))` where `Log` always returns false logs without ever handling.

## Custom exceptions

```csharp
public class InsufficientFundsException(decimal requested, decimal available)
    : Exception($"Requested {requested:C} but only {available:C} available")
{
    public decimal Requested { get; } = requested;
    public decimal Available { get; } = available;
}
```

**Carry structured data as properties**, not just a formatted string — the message is for humans, the properties are for the code deciding what to do.

**One base exception per application** (`AppException`) is worth having on day one: it lets callers write `catch (AppException)` meaning "something *we* raised" as distinct from "something broke" → [[languages/06-python/09-errors-and-exceptions|the same advice in Python]].

## The result-type debate

**Exceptions are for exceptional cases. Failure that's part of normal operation arguably isn't exceptional.**

```csharp
// exceptions
var user = await GetUserAsync(id);       // throws if not found

// result type
Result<User> result = await GetUserAsync(id);
if (result.IsSuccess) { … } else { … }
```

**The case for results:** the failure is in the *type signature*, so the compiler makes you handle it. You can't forget. And exceptions are expensive when thrown frequently — a throw costs microseconds, which matters in a hot loop.

**The case against, in C# specifically:** the language and the entire BCL are exception-based, so you end up converting at every boundary. There's no built-in `Result<T>`, no `?` operator, and no exhaustiveness checking on your own union — so you get the verbosity without the guarantees → [[languages/03-rust/README|Rust's `Result`]] and [[languages/02-go/05-errors|Go's errors as values]].

**The pragmatic position, and the one most codebases land on:** exceptions for genuinely exceptional and unrecoverable conditions; **`TryParse`-style methods or a result type for expected failures** — "not found", "invalid input", "already exists".

```csharp
if (int.TryParse(input, out var n)) { … }        // the BCL's own answer
```

**`TryX` is C#'s idiomatic result type**, and it's been there since the beginning.

## Guard clauses

```csharp
ArgumentNullException.ThrowIfNull(user);
ArgumentOutOfRangeException.ThrowIfNegative(amount);
```

**Fail fast, at the boundary, with a message naming the parameter.** These helpers (.NET 6+) replaced a lot of hand-written `if (x is null) throw` and are worth using — an exception at the point of the bad argument beats a `NullReferenceException` three frames deeper.

## Related
- [[languages/07-csharp/07-async-await-and-tasks|async and tasks]] — exceptions across await
- [[languages/06-python/09-errors-and-exceptions|Python's version]] · [[languages/02-go/05-errors|Go's]]
- [[foundations/programming-fundamentals/10-errors-and-debugging|errors and debugging]]

*Source: [reference] — from the .NET documentation, Aug 2026.*
