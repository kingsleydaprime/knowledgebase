# Memory, GC and Spans

> **[Advanced]** · How the garbage collector works, why allocation matters in a game loop, and the tools for writing allocation-free C#.

## The GC

.NET uses a **generational, tracing, compacting** collector.

**Generational** — most objects die young, so the heap is split into **Gen 0** (new), **Gen 1** (survived one collection), **Gen 2** (long-lived). Gen 0 collections are frequent and very fast; Gen 2 collections are rare and expensive.

**Compacting** — after collection, survivors are moved together, eliminating fragmentation and making allocation a pointer bump.

**The Large Object Heap (LOH)** holds anything ≥ 85,000 bytes. **It is not compacted by default**, so it fragments — which is why repeatedly allocating large arrays or buffers is a genuine problem and why pooling them matters.

**Server GC vs Workstation GC** — server GC uses per-core heaps and threads for throughput; workstation GC optimises for latency. A default worth checking on a busy service.

## Why allocation matters in a game loop

**Not the allocation — the collection.**

A Gen 0 collection is fast (sub-millisecond typically), but **it pauses your threads.** Within a **16 ms frame budget** → [[game-development/01-what-game-development-actually-is|note 01]], a pause at the wrong moment is a visible stutter. Allocate every frame and you're inviting one regularly.

**Unity makes this worse.** Its historical GC is **non-generational and non-compacting** (Boehm), so collections scan the whole heap and cost grows with heap size. Unity's incremental GC helps; the underlying advice stands: **do not allocate in `Update`** → [[game-development/engines/unity|Unity]].

**The allocations people don't notice:**

```csharp
void Update()
{
    var s = "Score: " + score;        // string concat → allocation, every frame
    foreach (var x in someList) { }   // fine for List<T>; boxes for some collections
    var arr = new float[10];          // obviously allocates
    DoThing(x => x + offset);         // CAPTURING lambda → closure allocation
    obj.GetComponent<Rigidbody>();    // Unity: a lookup, and can allocate
}
```

**Strings are immutable, so every concatenation allocates.** Use `StringBuilder`, or `string.Create`, or cache the result.

**Boxing** is the subtle one: assigning a value type to `object` or a non-generic interface allocates a heap box → [[languages/07-csharp/02-the-type-system|note 02]]. `Dictionary<int, X>` doesn't box; the old non-generic `Hashtable` does. `struct` implementing an interface, then used *through* that interface, boxes.

## `Span<T>` — the modern answer

**`Span<T>` is a view over contiguous memory** — array, string, stack, or unmanaged — with no copy and no allocation.

```csharp
ReadOnlySpan<char> text = "hello world";
var word = text[..5];                       // NO allocation — a view
int sum = 0;
Span<int> nums = stackalloc int[64];        // on the STACK, no heap at all
```

**Compare with `Substring`**, which allocates a new string and copies. In a parser processing a million lines, that's a million allocations you can delete by switching to spans.

**The restrictions are the price**, and they're enforced by the compiler: `Span<T>` is a **`ref struct`** — it lives on the stack only. It **cannot** be a field of a class, be boxed, be captured by a lambda, or be used across an `await`. **`Memory<T>` is the heap-friendly sibling** for exactly those async cases.

**Related tools:** `ArrayPool<T>.Shared` for renting large buffers instead of allocating them; `stackalloc` for small fixed buffers; `ref struct` for your own stack-only types.

## Struct vs class, decided by allocation

**The performance argument for structs** → [[languages/07-csharp/03-classes-records-and-structs|note 03]]:

- A `List<Vector3>` of structs is **one contiguous block** — cache-friendly, no per-element allocation
- A `List<Vector3>` of classes is a pointer array plus N scattered heap objects — a cache miss per element

**On modern hardware that difference is often 10× or more**, because a cache miss costs hundreds of cycles → [[foundations/computer-architecture/09-caches-in-depth|caches]]. **This is why game engines use structs for maths types**, and it's the same data-oriented argument as [[game-development/02-engines-and-the-game-loop|ECS]].

## `IDisposable` — deterministic cleanup

**The GC handles memory. It does not handle file handles, sockets, database connections or locks** — those need releasing at a known time.

```csharp
using var file = File.OpenRead(path);      // disposed at end of scope
// or
await using var conn = new SqlConnection(cs);
```

**`using` is C#'s RAII** → [[languages/05-cpp/03-classes-and-raii|C++ RAII]] and [[languages/06-python/07-decorators-and-context-managers|Python's `with`]] — same problem, same shape of solution.

**Finalizers (`~MyClass()`) are a last-resort backstop**, not a cleanup mechanism: they run non-deterministically, they promote the object to the next generation (making collection *more* expensive), and you generally shouldn't write one. **If you hold an unmanaged resource, implement `IDisposable` and let the caller `using` it.**

## Measuring

```bash
dotnet-counters monitor --process-id <pid>     # live GC and allocation rates
dotnet-trace collect --process-id <pid>        # traces for analysis
```

**BenchmarkDotNet** is the standard for microbenchmarks and reports **allocations per operation** alongside time — which is exactly the number you're optimising here.

**Measure before optimising.** Allocation-free C# is meaningfully harder to read, and most code has no reason to be → [[foundations/computer-architecture/12-performance|performance method]].

## Related
- [[languages/07-csharp/02-the-type-system|the type system]] — boxing
- [[languages/07-csharp/13-performance-and-the-runtime|performance and the runtime]]
- [[foundations/os/05-memory-allocation|memory allocation]] · [[game-development/engines/unity|Unity]]

*Source: [reference] — from the .NET GC documentation, Aug 2026.*
