# JVM Internals

**Source:** **[reference]** — neither project profiled or tuned the JVM directly, so this is built from [roadmap.sh Java](https://roadmap.sh/java) plus first principles. It's flagged reference, but it's the **single most target-relevant file in the domain**: a low-latency / high-throughput role screens hard on GC behavior, memory layout, and JIT warmup, and the batch pipeline's throughput story ([[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]) is ultimately a story about the JVM's allocation and GC behavior under load. Where a concept touches the pipeline, the connection is called out.

## What the JVM is

`javac` compiles `.java` → portable `.class` **bytecode**. The **JVM** loads that bytecode and executes it — interpreting at first, then JIT-compiling hot paths to native code. The JVM is the platform-specific piece; the bytecode is not. Three subsystems do the work: the **class loader**, the **runtime memory areas**, and the **execution engine** (interpreter + JIT + garbage collector).

## Class loading

Loading is lazy — a class is loaded the first time it's referenced, in three phases:

1. **Loading** — a class loader reads the `.class` bytes into memory.
2. **Linking** — *verification* (bytecode is well-formed and safe), *preparation* (static fields get default values), *resolution* (symbolic references resolved).
3. **Initialization** — static initializers and static field assignments run (this is when a `static { }` block from [[languages/01-java/01-language/01-fundamentals|Fundamentals]] fires).

Class loaders form a **parent-delegation** hierarchy: Bootstrap (core `java.*`) → Platform → Application (your classpath). A loader asks its parent before trying itself, which prevents your code from shadowing `java.lang.String`. This is also where "jar hell" / `ClassNotFoundException` vs `NoClassDefFoundError` problems come from, and how app servers and plugin systems isolate code with custom loaders.

## Runtime memory areas

The JVM partitions memory into distinct regions — knowing which is which is the difference between diagnosing a `StackOverflowError` and an `OutOfMemoryError`:

| Region | Shared? | Holds | Overflow error |
|---|---|---|---|
| **Heap** | all threads | every object and array (`new` allocates here) | `OutOfMemoryError: Java heap space` |
| **Stack** | per thread | frames of local variables + partial results, one frame per method call | `StackOverflowError` (e.g. unbounded recursion) |
| **Metaspace** | all threads | class metadata (native memory, since Java 8 — replaced PermGen) | `OutOfMemoryError: Metaspace` |
| **PC register** | per thread | address of the current bytecode instruction | — |
| **Native method stack** | per thread | native (JNI) call frames | — |

The critical mental model: **objects live on the heap; references to them live on the stack** (or in other objects on the heap). A local variable `Transaction t` is a reference on the stack pointing at a `Transaction` object on the heap. This is exactly why Java is pass-by-value-of-the-reference ([[languages/01-java/01-language/01-fundamentals|Fundamentals]]) and why the heap is what garbage collection manages.

## Garbage collection

Java has no manual `free()` — the GC reclaims objects that are no longer **reachable** from any GC root (stack locals, static fields, active threads). The dominant design is the **generational hypothesis**: *most objects die young*. So the heap is split:

- **Young generation** (Eden + two Survivor spaces) — new objects. A **minor GC** collects it frequently and cheaply; survivors are copied between survivor spaces and aged.
- **Old / Tenured generation** — objects that survived enough minor GCs get *promoted* here. A **major/full GC** collects it, and is more expensive.

Most allocations are cheap (a bump-pointer in Eden) and most collections are cheap (minor GC of mostly-dead young objects). The expensive events are full GCs and long **stop-the-world (STW) pauses**, where application threads freeze while the collector works.

### The collectors, and why the choice matters

| Collector | Optimizes for | STW pauses | Use when |
|---|---|---|---|
| **Serial** | simplicity, tiny heaps | long | single-core, small apps |
| **Parallel (Throughput)** | total throughput | long but infrequent | batch jobs where a pause is fine if total work/sec is maximized |
| **G1** (default since 11) | balanced, predictable pauses | medium, target-able (`-XX:MaxGCPauseMillis`) | most server apps |
| **ZGC / Shenandoah** | **ultra-low pause** (sub-millisecond, mostly concurrent) | very short, heap-size-independent | latency-critical services, large heaps |

This table *is* the low-latency conversation. A trading/market-data system cannot tolerate a 200ms full-GC pause, so it reaches for **ZGC or Shenandoah** (concurrent collectors that do almost all work without stopping application threads), tunes allocation rate down, and often moves hot data **off-heap** (via `ByteBuffer`/`Unmanaged` memory) to avoid GC entirely. Meanwhile the CSV batch pipeline ([[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]) is the *opposite* profile — it wants raw **throughput**, doesn't care about a pause here and there, so a throughput-oriented collector and large young gen (fewer promotions) suits it. **The right collector is workload-dependent; there's no universal best.**

### Allocation pressure — the lever you actually control

You rarely tune the collector directly; you reduce how hard it has to work. Every object allocated is future GC work, so allocation rate drives pause frequency. This connects straight to the language notes:

- Building a `String` in a loop with `+` allocates a new object each iteration → `StringBuilder` instead ([[languages/01-java/01-language/01-fundamentals|Fundamentals]]).
- Boxing (`Integer` for every `int`) allocates; primitive-specialized types (`OptionalInt`, `IntStream`, primitive arrays) don't — the pipeline's `HashSet<Long>` of millions of boxed longs is real allocation pressure, which is exactly why a Bloom filter (a fixed bit array) is offered as the low-memory alternative in [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation]].
- Pre-sizing collections (`new ArrayList<>(n)`) avoids reallocation churn.

**Escape analysis** is the JIT optimization that rewards this: if the JIT proves an object never "escapes" a method (never stored where another thread/method could see it), it can allocate it on the stack or eliminate it entirely — zero GC cost. Writing allocation-light, locally-scoped code is what lets this fire.

## The JIT compiler

The JVM starts by **interpreting** bytecode, while a profiler counts how often each method and loop runs. Once something crosses a threshold ("hot"), the **JIT compiler** compiles it to optimized native code. **Tiered compilation** uses two: **C1** (fast to compile, lightly optimized) for quick warmup, then **C2** (slow to compile, aggressively optimized) for the hottest code.

The consequences that matter in practice:

- **Warmup** — a freshly started JVM runs *interpreted*, so the first thousands of requests are slower until C2 kicks in. Latency-sensitive services warm the JVM before taking traffic; benchmarks that don't discard warmup are lying (this is why JMH exists — [[languages/01-java/03-tooling/04-testing|Testing]]).
- **Inlining** — the JIT inlines small hot methods, erasing call overhead. It's why small getters and lambdas cost nothing in a hot loop, and why "clean, small methods" isn't a performance tax.
- **Speculative optimization + deoptimization** — C2 optimizes on assumptions (e.g. a call site always hits one implementation) and *deoptimizes* back to the interpreter if an assumption breaks. Megamorphic call sites (many implementations) inline poorly — relevant when polymorphism ([[languages/01-java/01-language/02-oop|OOP]]) sits in a hot path.

## Tuning flags worth recognizing

```
-Xms4g -Xmx4g            # initial and max heap — set equal in production to avoid resize pauses
-XX:+UseZGC              # pick the low-pause collector
-XX:MaxGCPauseMillis=50   # G1 pause target
-Xss1m                   # per-thread stack size
-XX:+HeapDumpOnOutOfMemoryError   # capture a heap dump when it OOMs
```

You don't memorize these — you recognize them, and you reach for tooling to know what to change: **JFR (Java Flight Recorder)** + **JDK Mission Control** for low-overhead production profiling, **`jstat`/`jmap`/`jstack`** for quick heap/GC/thread snapshots, and **async-profiler** for allocation and CPU flame graphs. The senior instinct is *measure first* — diagnose from a GC log or a flight recording, don't guess at flags.

## Why this file is the target's home turf

The original gap analysis flagged this domain as "silent on every topic a low-latency market-data firm would care about." This file is the direct answer: GC collector choice and pause behavior, off-heap vs on-heap, allocation pressure, JIT warmup, and escape analysis *are* the low-latency Java conversation. Pairing this with the lock-free/atomics material in [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] covers the two things such a role actually probes.

## Related
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — the memory model and lock-free structures that run on top of this
- [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads]] — a runtime change built directly on the JVM's execution model
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — allocation and throughput in a real pipeline
