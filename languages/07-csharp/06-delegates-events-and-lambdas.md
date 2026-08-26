# Delegates, Events and Lambdas

> **[Intermediate]** · Functions as values — the machinery under LINQ, callbacks, and every event-driven API in .NET.

## Delegates

**A delegate is a type-safe function pointer.** Declaring one defines a *type*:

```csharp
public delegate int Transform(int x);

Transform t = x => x * 2;
t(5);                                  // 10
```

**In practice you almost never declare your own** — the built-in generic ones cover it:

```csharp
Func<int, int>         square = x => x * x;        // takes int, returns int
Func<int, int, int>    add    = (a, b) => a + b;   // last parameter is the return
Action<string>         log    = s => Console.WriteLine(s);   // returns void
Predicate<int>         isEven = n => n % 2 == 0;   // returns bool
```

**`Func` returns; `Action` doesn't.** That's the whole convention, and it's why `Where` takes a `Func<T, bool>` and `ForEach` takes an `Action<T>` → [[languages/07-csharp/04-collections-and-linq|LINQ]].

## Lambdas and closures

```csharp
int factor = 3;
Func<int, int> scale = x => x * factor;    // captures `factor`
```

**A lambda that captures a variable becomes a closure** — the compiler generates a class holding the captured variables, and the lambda becomes a method on it.

**Two consequences that matter:**

**Capture allocates.** A capturing lambda creates a heap object. A **non-capturing** lambda is cached and allocates nothing. In a hot loop this is the difference between zero allocation and one per iteration → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

**Closures capture the variable, not the value** — the same trap as every other language:

```csharp
var actions = new List<Action>();
for (int i = 0; i < 3; i++)
    actions.Add(() => Console.WriteLine(i));
// C# 5+: prints 0,1,2 for foreach; for a `for` loop, all three print 3
```

**C# 5 changed `foreach` to declare a fresh variable per iteration**, which fixed the commonest form. **A classic `for` loop still shares one `i`.** Copy into a local if you capture it → [[languages/06-python/04-functions-and-scope|the same trap in Python]].

## Events

**A delegate field with restrictions**, and the restrictions are the point:

```csharp
public class Downloader
{
    public event EventHandler<ProgressEventArgs>? Progress;

    protected virtual void OnProgress(int percent)
        => Progress?.Invoke(this, new ProgressEventArgs(percent));
}

downloader.Progress += (sender, e) => Console.WriteLine($"{e.Percent}%");
```

**What `event` buys over a public delegate field:** subscribers can only `+=` and `-=`. They **cannot** invoke it, and they cannot overwrite the whole list with `=`. Only the declaring type can raise it.

**Details that matter:**

- **`?.Invoke`** — a null delegate means no subscribers, and invoking null throws. **Always null-check**
- **Multicast**: a delegate holds an invocation list. **If one handler throws, later handlers never run**
- **Events are a memory-leak source.** A subscription is a **strong reference from publisher to subscriber**. A long-lived publisher keeps short-lived subscribers alive forever. **Always unsubscribe** — this is the single most common managed memory leak in .NET and Unity → [[frontend/interview/02-javascript-and-typescript|the same leak in JS]]

**The Unity note:** `OnEnable`/`OnDisable` exist largely for this — subscribe in one, unsubscribe in the other, or your pooled objects leak → [[game-development/engines/unity|Unity]].

## The observer pattern, three ways

C# gives you three, and they're for different scales:

| | Use for |
|---|---|
| **`event`** | Classic in-process notification, few subscribers |
| **`IObservable<T>` / Rx** | Streams of events, composition, backpressure |
| **`IAsyncEnumerable<T>`** | **Asynchronous sequences** — often the simplest modern answer |

```csharp
await foreach (var line in ReadLinesAsync(path))   // IAsyncEnumerable
    Process(line);
```

**`IAsyncEnumerable` (C# 8) replaced a lot of Rx** for the common "stream of things arriving over time" case, and it composes with `async`/`await` naturally → [[languages/07-csharp/07-async-await-and-tasks|note 07]].

## Expression trees — the LINQ magic

```csharp
Func<int, bool>            f = x => x > 5;   // compiled delegate
Expression<Func<int,bool>> e = x => x > 5;   // a DATA STRUCTURE describing the code
```

**The second is an object graph you can inspect and translate.** That's how Entity Framework turns a C# lambda into SQL — it walks the expression tree rather than executing it → [[languages/07-csharp/04-collections-and-linq|IQueryable]].

**This is genuinely unusual.** Most languages let you pass functions; C# lets you pass the *structure* of a function to something that reinterprets it. It's also why not every C# expression translates — the provider must understand each node.

## Related
- [[languages/07-csharp/04-collections-and-linq|collections and LINQ]] — built on all of this
- [[languages/07-csharp/07-async-await-and-tasks|async and tasks]]
- [[foundations/programming-fundamentals/14-programming-paradigms|paradigms]] — functions as values

*Source: [reference] — from the C# language reference, Aug 2026.*
