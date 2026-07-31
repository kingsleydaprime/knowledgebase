# Virtual Threads

**Source:** **[reference]** — the projects used platform threads and thread pools ([[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]]); virtual threads (Project Loom, finalized in **Java 21**) postdate them. Included because they're the biggest change to Java concurrency in a decade and directly reframe the thread-pool sizing decisions the projects actually made.

## The problem they solve

A **platform thread** is a thin wrapper over an OS thread. OS threads are expensive — roughly 1MB of stack each, and context-switching between thousands of them thrashes the scheduler. So the entire ecosystem worked around thread scarcity: bounded thread pools ([[languages/01-java/02-jvm-and-concurrency/02-concurrency|the `ExecutorService` sizing there]]), async/reactive callbacks, `CompletableFuture` chains — all machinery to *avoid* blocking a precious OS thread.

That machinery has a cost: async code is hard to write, hard to read, and hard to debug (stack traces fragment across callbacks). The thread-per-request model is far simpler — but it didn't scale, because you couldn't afford a platform thread per request.

## What a virtual thread is

A **virtual thread** is a lightweight thread scheduled by the *JVM*, not the OS. It costs a few hundred bytes, not a megabyte, so millions can exist at once. The JVM multiplexes many virtual threads onto a small pool of **carrier** (platform) threads:

```
millions of virtual threads  ──scheduled onto──►  a handful of carrier (platform) threads  ──►  OS
```

The key mechanic: **when a virtual thread blocks on IO, the JVM unmounts it from its carrier thread and mounts another virtual thread there.** The carrier never blocks; the OS thread stays busy. A blocking call *looks* blocking in your code but doesn't waste an OS thread underneath.

```java
// A virtual thread per task — this would be insane with platform threads, trivial here
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (var request : requests) {
        executor.submit(() -> handle(request));   // blocking IO inside is fine — the carrier is freed
    }
}
```

## What actually changes

- **Write blocking, get async performance.** Straight-line `conn.query(); http.call();` code — readable, debuggable, real stack traces — now scales like hand-written async, because the JVM frees the carrier during each blocking call. This is the headline: it retires most of the reason reactive frameworks existed for IO-bound web services.
- **Don't pool virtual threads.** Pools exist to share a scarce resource; virtual threads are not scarce. Create one per task (`newVirtualThreadPerTaskExecutor`) and let it end. Pooling them is an anti-pattern.
- **Don't size them by CPU count.** A platform-thread pool is sized to cores (`ExecutorService` in [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]]); virtual threads are sized to *concurrent tasks*, which can be millions.

## Where they help — and where they don't

Virtual threads help **IO-bound** concurrency (waiting on a DB, an HTTP call, a queue) — most web backends. They do **not** speed up **CPU-bound** work: a virtual thread doing pure computation just occupies its carrier the whole time, so you're still bounded by cores, and a fixed platform-thread pool remains correct there. This maps cleanly onto the projects: the RabbitMQ consumer is IO-bound (network + DB), a natural virtual-thread fit; the CSV parsing / SHA-256 hashing is CPU-bound, where more virtual threads than cores buys nothing.

## The pinning pitfall

A virtual thread can't always be unmounted. If it blocks **inside a `synchronized` block** or during a **native (JNI) call**, it stays *pinned* to its carrier — the carrier blocks, defeating the purpose. The fix is to prefer `ReentrantLock` over `synchronized` around blocking sections in code meant to run on virtual threads. (Later JDKs have been reducing `synchronized` pinning, but the guidance — lock, don't `synchronized`, around blocking IO on virtual threads — still holds as the safe default.) This is a concrete reason the `ReentrantLock`-vs-`synchronized` distinction from [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] suddenly matters more than it used to.

## Structured concurrency

The companion feature: `StructuredTaskScope` treats a group of concurrent subtasks as a single unit of work with a clear lifetime — if one fails, siblings are cancelled; the parent waits for all before proceeding. It brings the "child work can't outlive its parent" discipline (and clean error propagation) to concurrent code, replacing ad-hoc `Future` juggling:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user  = scope.fork(() -> fetchUser(id));      // concurrent subtasks
    var order = scope.fork(() -> fetchOrder(id));
    scope.join().throwIfFailed();                      // wait for both; propagate any failure
    return new Result(user.get(), order.get());
}
```

## The honest framing

For a low-latency / systems target, virtual threads are the modern answer to *concurrency scaling*, but they don't replace the deep material in [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] and [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — they sit on top of it. You still need the memory model to reason about shared state (virtual or not), still need lock-free structures under contention, and still care about GC because millions of cheap threads still allocate. They change *how many threads you can afford*, not the rules those threads play by.

## Related
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — the primitives (locks, atomics, memory model) virtual threads run on
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — the execution model virtual threads are scheduled within
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — the IO-bound consumer pattern virtual threads suit
