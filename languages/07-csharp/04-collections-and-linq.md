# Collections and LINQ

> **[Beginner → Intermediate]** · The standard collections, and LINQ — the feature that most distinguishes C# from its neighbours.

## The collections

| Type | Is | Cost |
|---|---|---|
| `T[]` | Fixed-size array | O(1) index |
| `List<T>` | Dynamic array | O(1) index, amortised O(1) add |
| `Dictionary<K,V>` | Hash map | **O(1)** average lookup |
| `HashSet<T>` | Hash set | **O(1)** membership |
| `Queue<T>` / `Stack<T>` | FIFO / LIFO | O(1) |
| `LinkedList<T>` | Doubly linked | O(1) insert given a node; **rarely the right answer** |
| `SortedDictionary<K,V>` | Tree-backed | O(log n), ordered |
| `ImmutableArray<T>` etc. | Immutable | Cheap reads, copy on write |
| `ConcurrentDictionary<K,V>` | Thread-safe | For concurrent access |

**Same costs as everywhere** → [[foundations/programming-fundamentals/07-collections|collections]]. And the same commonest mistake: `list.Contains(x)` in a loop is O(n·m); a `HashSet<T>` makes it O(n).

**Interfaces matter here.** Accept the least specific thing that works — `IEnumerable<T>` for "I'll iterate it once", `IReadOnlyList<T>` for "I need indexing", `ICollection<T>` if you must add. **Returning `IEnumerable<T>` from a method that does I/O is how you accidentally re-query.**

## LINQ

**Language-Integrated Query** — a uniform query syntax over anything enumerable.

```csharp
var topSpenders = orders
    .Where(o => o.Status == Status.Paid)
    .GroupBy(o => o.CustomerId)
    .Select(g => new { CustomerId = g.Key, Total = g.Sum(o => o.Amount) })
    .OrderByDescending(x => x.Total)
    .Take(10)
    .ToList();
```

**In most languages that's twenty lines of loops and a dictionary.** LINQ is the single feature that C# developers miss most when they leave.

**The operators worth knowing cold:** `Where`, `Select`, `SelectMany` (flatten), `OrderBy`/`ThenBy`, `GroupBy`, `Join`, `Any`/`All`, `First`/`FirstOrDefault`, `Single`/`SingleOrDefault`, `Sum`/`Count`/`Average`/`Min`/`Max`, `Distinct`, `Take`/`Skip`, `Zip`, `Aggregate`, `ToList`/`ToArray`/`ToDictionary`.

**`First` vs `Single`** is a real distinction: `First` takes the first match; **`Single` throws if there isn't exactly one.** Using `Single` where you mean `First` turns a data anomaly into an exception — which is sometimes exactly what you want, and should be deliberate.

## Deferred execution — the part that bites

**LINQ queries are lazy.** Building one executes nothing; enumerating it does.

```csharp
var query = items.Where(x => Expensive(x));   // nothing has run
foreach (var x in query) { }                  // runs now
foreach (var x in query) { }                  // runs AGAIN — the whole thing
```

**Three consequences, and all three cause real bugs:**

**Re-enumeration re-executes.** If the source is a database or a file, you've done the work twice. **Materialise with `.ToList()` when you'll use it more than once.**

**The query sees the source's state at enumeration time.** Modify the collection between building and enumerating and the result reflects the modification — or throws.

**Closures capture variables, not values** — the same late-binding trap as [[languages/06-python/04-functions-and-scope|Python]] and [[frontend/interview/02-javascript-and-typescript|JavaScript]]. Building queries in a loop over a mutable loop variable captures the variable.

**The rule: return `IEnumerable<T>` for composability, but materialise at the boundary where the work should actually happen.**

## LINQ to Objects vs IQueryable

**This distinction is the source of most LINQ performance disasters.**

**`IEnumerable<T>`** — LINQ to Objects. Runs **in memory**, in your process.

**`IQueryable<T>`** — the query is built as an **expression tree** and translated by a provider (Entity Framework) into SQL, executed by the database.

```csharp
db.Orders.Where(o => o.Total > 100).ToList();        // ✓ WHERE clause in SQL
db.Orders.ToList().Where(o => o.Total > 100);        // ✗ loads EVERY order, filters in C#
```

**Those two lines look almost identical and differ by the entire table.** The second is the C# equivalent of `SELECT *` and a client-side filter → [[databases/13-practice-exercises|databases]].

**And not everything translates.** A C# method inside a `Where` on an `IQueryable` either throws or — in older EF versions — silently fell back to client-side evaluation. **Know which of the two you're holding.**

## Performance, honestly

**LINQ allocates.** Each operator creates an iterator object, and lambdas capturing variables create closure objects. In ordinary application code this is irrelevant. **In a per-frame game loop or a hot server path it is not** → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

**Unity code frequently bans LINQ in `Update`** for exactly this reason, and that's a legitimate rule — not a general indictment.

**The judgement:** write LINQ by default because it's clearer; replace it with a loop where a profiler says it matters. **Not before** → [[foundations/computer-architecture/12-performance|performance method]].

## Related
- [[languages/07-csharp/06-delegates-events-and-lambdas|delegates and lambdas]] — what LINQ is built on
- [[languages/07-csharp/08-memory-gc-and-spans|memory and GC]] — LINQ's cost
- [[foundations/programming-fundamentals/07-collections|collections]] · [[databases/README|databases]]

*Source: [reference] — from the .NET documentation, Aug 2026.*
