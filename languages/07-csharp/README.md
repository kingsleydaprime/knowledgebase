# C#

The language, and the .NET platform around it. **Not the frameworks** — ASP.NET Core belongs in [[backend/frameworks/README|backend/frameworks/]] and Unity in [[game-development/engines/unity|game-development/engines/]], per [[languages/README|the rule]].

**~9,600 words across 13 notes.** Built August 2026. `[reference]`.

> **The one idea:** C# is what Java would look like if it had shipped its good ideas faster — **value types, reified generics, records, pattern matching, LINQ and `async`/`await` all arrived years earlier.** The cost is a garbage collector you must respect wherever latency is bounded, which is why the same language reads very differently in a web API and in a game loop.

## Why this exists

**C# was absent from the vault entirely**, and two things made that untenable: it's **Unity's language**, so the new [[game-development/README|game development track]] pointed at nothing; and it's one of the largest enterprise backend languages, so `languages/` had a Java-shaped hole in exactly the place a reader comparing them would look.

## Reading order

**01–03 are the model. 04–07 are the features that define the language. 08–13 are the runtime and the practice.**

1. [[languages/07-csharp/01-why-csharp-and-the-toolchain|Why C#, and the Toolchain]] — **[Beginner]** — the .NET naming mess untangled, the CLI, and **the Unity version footnote**
2. [[languages/07-csharp/02-the-type-system|The Type System]] — **[Beginner → Intermediate]** — value vs reference types, **nullable reference types**, and why reified generics beat erasure
3. [[languages/07-csharp/03-classes-records-and-structs|Classes, Records and Structs]] — **[Beginner → Intermediate]** — three ways to define a type, and **which to reach for**
4. [[languages/07-csharp/04-collections-and-linq|Collections and LINQ]] — **[Beginner → Intermediate]** — the standout feature, deferred execution, **and the `IQueryable` trap that loads your whole table**
5. [[languages/07-csharp/05-generics-and-constraints|Generics and Constraints]] — **[Intermediate]** — constraints, generic maths, variance, and the array-covariance wart
6. [[languages/07-csharp/06-delegates-events-and-lambdas|Delegates, Events and Lambdas]] — **[Intermediate]** — `Func`/`Action`, closures, **events as a memory leak**, and expression trees
7. [[languages/07-csharp/07-async-await-and-tasks|Async, Await and Tasks]] — **[Intermediate → Advanced]** — the model everyone copied, and **the four ways to deadlock**
8. [[languages/07-csharp/08-memory-gc-and-spans|Memory, GC and Spans]] — **[Advanced]** — generational GC, **why allocation matters in a game loop**, `Span<T>`, `IDisposable`
9. [[languages/07-csharp/09-error-handling|Error Handling]] — **[Intermediate]** — the hierarchy, exception filters, **`throw;` vs `throw ex;`**, and the result-type debate
10. [[languages/07-csharp/10-pattern-matching-and-modern-csharp|Pattern Matching and Modern C#]] — **[Intermediate]** — switch expressions, records-as-ADTs, and the syntax that removed the ceremony
11. [[languages/07-csharp/11-the-standard-library-and-ecosystem|The Standard Library and Ecosystem]] — **[Intermediate]** — the BCL, **DI as a platform feature**, EF Core and the N+1
12. [[languages/07-csharp/12-testing-and-tooling|Testing and Tooling]] — **[Intermediate]** — xUnit, Testcontainers, **Roslyn analyzers**, BenchmarkDotNet
13. [[languages/07-csharp/13-performance-and-the-runtime|Performance and the Runtime]] — **[Advanced]** — tiered JIT, Native AOT, SIMD, and where C# actually sits

## The things worth carrying

1. **".NET Framework" is the dead Windows-only one; ".NET 5+" is the live one** → [[languages/07-csharp/01-why-csharp-and-the-toolchain|01]]
2. **Unity trails the language by years.** Learn C# properly; adjust at the boundary → [[languages/07-csharp/01-why-csharp-and-the-toolchain|01]]
3. **You choose whether a type is copied or shared** — `struct` vs `class`. Java doesn't let you → [[languages/07-csharp/02-the-type-system|02]]
4. **`<Nullable>enable</Nullable>` is the highest-value line in the project file** → [[languages/07-csharp/02-the-type-system|02]]
5. **Reified generics mean `List<int>` stores unboxed ints.** A real performance gap over erasure → [[languages/07-csharp/02-the-type-system|02]]
6. **Records for data, classes for behaviour, `readonly record struct` for small values** → [[languages/07-csharp/03-classes-records-and-structs|03]]
7. **LINQ is lazy. Enumerating twice runs it twice** → [[languages/07-csharp/04-collections-and-linq|04]]
8. **`.ToList()` in the wrong place moves the filter from SQL into C#** and loads the table → [[languages/07-csharp/04-collections-and-linq|04]]
9. **`out` for producers, `in` for consumers** — and array covariance is an unsound wart → [[languages/07-csharp/05-generics-and-constraints|05]]
10. **An event subscription is a strong reference.** Always unsubscribe → [[languages/07-csharp/06-delegates-events-and-lambdas|06]]
11. **Sequential `await`s are not concurrent.** `Task.WhenAll` is → [[languages/07-csharp/07-async-await-and-tasks|07]]
12. **`async void` exceptions crash the process.** `.Result` deadlocks. Async all the way down → [[languages/07-csharp/07-async-await-and-tasks|07]]
13. **Boxing is invisible allocation**, and it's what kills frame times → [[languages/07-csharp/08-memory-gc-and-spans|08]]
14. **`Span<T>` slices without copying** — but it's stack-only and can't cross an `await` → [[languages/07-csharp/08-memory-gc-and-spans|08]]
15. **`throw;` preserves the stack trace; `throw ex;` destroys it** → [[languages/07-csharp/09-error-handling|09]]
16. **`TryX` is C#'s idiomatic result type**, and it's been there since v1 → [[languages/07-csharp/09-error-handling|09]]
17. **A switch *expression* is exhaustiveness-checked** — bugs move to compile time → [[languages/07-csharp/10-pattern-matching-and-modern-csharp|10]]
18. **Reuse `HttpClient`; use `DateTimeOffset`; never `Random` for secrets** → [[languages/07-csharp/11-the-standard-library-and-ecosystem|11]]
19. **Injecting a Scoped service into a Singleton captures it forever** → [[languages/07-csharp/11-the-standard-library-and-ecosystem|11]]
20. **Your first measurements are Tier 0 code.** Warm up, or use BenchmarkDotNet → [[languages/07-csharp/13-performance-and-the-runtime|13]]

## Where this connects

| | |
|---|---|
| [[game-development/engines/unity\|Unity]] | **The reason many readers arrive here** |
| [[languages/01-java/README\|Java]] | The closest neighbour — compare constantly |
| [[backend/README\|backend course]] | The concepts ASP.NET Core implements |
| [[languages/06-python/README\|Python]] · [[languages/03-rust/README\|Rust]] | The async and pattern-matching comparisons |
| [[foundations/computer-architecture/09-caches-in-depth\|caches]] | Why structs beat classes in arrays |

## The honest note

**`[reference]`** — no C# in this vault's [[projects/README|projects/]]; the backend work here is Node/Nest and Java/Spring. **Everything is read and cross-checked, not shipped.** Take note 13's performance positioning as reported rather than measured.

**What would close the gap:**

1. **`dotnet new webapi` and build one endpoint** with EF Core against a real Postgres in Testcontainers. **An afternoon**, and it makes notes 11 and 12 concrete
2. **Cause the N+1**, see it in the SQL log, fix it with `Include`, and record the query counts
3. **Run BenchmarkDotNet on string concatenation vs `StringBuilder` vs `string.Create`** with `[MemoryDiagnoser]`. **Note 08's allocation argument, in numbers**
4. **Turn `<Nullable>enable</Nullable>` on in an existing project** and count what it finds
5. **Then do it in Unity** — write the same maths as a `class` and a `readonly record struct`, put 100,000 in an array, and measure. **That single test is notes 02, 03 and 08 at once**

**What's missing:** ASP.NET Core in any depth (it belongs in `backend/frameworks/`, which doesn't yet have a `csharp/` folder), Blazor, MAUI, source generators, `unsafe` and interop (P/Invoke), Roslyn as a platform, and exercises.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[languages/README|languages/]] — the domain index
- [[game-development/README|game development]] · [[BUILD-PLAN|Build Plan]]
