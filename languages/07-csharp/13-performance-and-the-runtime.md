# Performance and the Runtime

> **[Advanced]** · What the CLR does with your IL, tiered JIT, AOT, and where C# actually sits between Java and C++.

## The pipeline

1. **C# → IL** (Intermediate Language) by Roslyn, plus metadata
2. **IL → machine code** by the **JIT**, at runtime, per method, on first call
3. **Tiered compilation** — Tier 0 compiles fast and badly; hot methods are **re-JITted** at Tier 1 with full optimisation

**Why tiering exists:** it trades startup time against steady-state speed. Tier 0 gets the app running quickly; anything called enough gets recompiled properly.

**Two consequences that catch people out:**

**Your first measurements are wrong.** A method timed on its first invocations is running Tier 0 code. **This is exactly why BenchmarkDotNet warms up before measuring**, and why hand-rolled `Stopwatch` benchmarks routinely report nonsense → [[languages/07-csharp/12-testing-and-tooling|note 12]].

**On-stack replacement (OSR)** lets a long-running loop be promoted to Tier 1 *mid-execution* — without it, a hot loop entered once would run Tier 0 code forever.

## What the JIT can do that AOT can't

**It knows the actual machine.** It emits AVX-512 if the CPU has it, without you shipping multiple binaries.

**It devirtualises and inlines using runtime information.** If an interface only ever has one implementation loaded, the JIT can inline through it — a static compiler generally cannot.

**Which is the real answer to "is C# slow?"**: for long-running server workloads, JIT-compiled .NET is typically **within ~1.5–3× of optimised C++**, and sometimes matches it. **It is not an interpreted language** → [[languages/06-python/14-performance-and-the-runtime|contrast with CPython]].

**Where it loses:** startup time (JIT work upfront), memory footprint (runtime + GC headroom), and **latency predictability** — GC pauses → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

## Native AOT

```xml
<PublishAot>true</PublishAot>
```

Compiles to a **self-contained native binary** ahead of time. No JIT, no runtime install.

**What you gain:** millisecond startup (vs tens/hundreds of ms), much smaller memory footprint, a single file, no warmup.

**What you give up:**
- **No runtime code generation** — `Reflection.Emit`, dynamic proxies, and anything building types at runtime
- **Reflection is restricted** — reflection-based serialisers, DI containers and ORMs may break. **`System.Text.Json` source generators exist precisely for this**
- **Bigger binaries than a framework-dependent build** (though smaller than self-contained JIT)
- **No profile-guided runtime optimisation** — you lose the JIT's machine-specific tricks

**Where it wins clearly:** serverless functions (cold start is the whole cost model → [[devops/03-cloud/02-serverless|serverless]]), CLI tools, containers where image size matters, short-lived processes.

**Where it doesn't:** long-running servers, where the JIT's advantages compound and startup is amortised to nothing.

## The optimisation ladder

**Same order as everywhere** → [[foundations/computer-architecture/12-performance|performance method]]:

**1. Algorithm.** `List.Contains` in a loop → `HashSet`. No runtime feature rescues O(n²) → [[foundations/dsa/README|DSA]].

**2. I/O.** Most "slow C#" in production is an N+1 query, a missing index, or serial HTTP calls that should be `Task.WhenAll` → [[databases/13-practice-exercises|databases]] · [[languages/07-csharp/07-async-await-and-tasks|note 07]].

**3. Allocation.** Then `Span<T>`, `ArrayPool<T>`, structs, avoiding boxing and capturing lambdas → [[languages/07-csharp/08-memory-gc-and-spans|note 08]].

**4. The runtime knobs** — Server GC for throughput, `<TieredPGO>` (on by default now), `<ReadyToRun>` for faster startup without full AOT.

**5. Vectorise.** `System.Numerics.Vector<T>` and the `System.Runtime.Intrinsics` namespaces give you portable SIMD from C#:
```csharp
var sum = Vector<float>.Zero;
for (int i = 0; i < span.Length; i += Vector<float>.Count)
    sum += new Vector<float>(span.Slice(i));
```
**This is unusual for a managed language** and genuinely closes much of the gap with C for numeric loops → [[foundations/gpu-and-parallel-computing/README|parallel computing]].

**6. `unsafe` and pointers** — available, rarely necessary, and you've left the safety guarantees.

## Measuring

```bash
dotnet-counters monitor -p <pid>          # live GC, allocation, thread pool
dotnet-trace collect -p <pid>             # traces for PerfView / speedscope
dotnet-dump collect -p <pid>              # heap analysis
```

**BenchmarkDotNet for microbenchmarks. A profiler for real workloads.** Never `Stopwatch` in a loop and never trust a number from a debug build → [[languages/07-csharp/12-testing-and-tooling|note 12]].

## Where C# sits

| | Startup | Throughput | Latency predictability | Memory |
|---|---|---|---|---|
| **C/C++/Rust** | Instant | Best | **Best** — no GC | Lowest |
| **C# (JIT)** | ms–100s ms | **Very good** | GC pauses | Moderate |
| **C# (AOT)** | **Instant** | Good | GC pauses | Low |
| **Java** | Slower | Very good | GC pauses | Higher |
| **Python** | Fast | **Poor** | GIL | Moderate |

**The honest summary: C# gives you most of the performance of a native language with most of the productivity of a managed one**, and the price is a GC you must respect in latency-sensitive code — which is exactly why game code avoids allocation in `Update` → [[game-development/engines/unity|Unity]].

## Related
- [[languages/07-csharp/08-memory-gc-and-spans|memory, GC and spans]]
- [[foundations/computer-architecture/12-performance|performance method]]
- [[languages/01-java/README|Java]] — the closest comparison

*Source: [reference] — from the .NET runtime documentation, Aug 2026.*
