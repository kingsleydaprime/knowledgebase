# Concurrency

**Source:** expanded from `record-id-generator-java/learning/06-concurrency-and-threads.md` (threads, graceful shutdown) and section 43 of `05-rabbitmq-messaging.md` (daemon threads/JVM keepalive), plus the `synchronized`/`ConcurrentHashMap` material scattered across both projects' data-storage notes. The original project note covered thread creation and one shutdown bug in 79 lines — this file adds the memory model, `java.util.concurrent`, locks, and atomics that sit underneath those examples, since none of that was written up anywhere in either project's notes.

> The **runtime** side of the JVM — class loading, the JIT, the heap/stack layout, and garbage collection — lives in [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]]. This file keeps only the *memory model* (below), because that's a concurrency concern specifically: it's the set of rules governing what one thread is guaranteed to see of another's writes.

## Threads — the starting point

A **thread** is an independent execution path; the JVM runs several simultaneously, mapped by the OS onto real CPU cores.

```java
Thread producerThread = new Thread(() -> producer.produce(filePath));
Thread consumerThread = new Thread(() -> consumer.consume());
consumerThread.start();   // start the consumer first — it needs to be ready before work arrives
producerThread.start();
producerThread.join();    // block the calling thread until producerThread finishes
```

Without threads, a slow producer (streaming a multi-GB file) and a slow consumer (writing to a DB) would run strictly sequentially. With threads, the producer fills a queue while the consumer drains it concurrently — this is the entire justification for reaching for threads at all: two operations with independent, overlapping I/O-wait time.

## Why "thread-safe" is a specific, narrow claim

A piece of code is thread-safe if multiple threads can call it concurrently without corrupting shared state, regardless of how the threads are scheduled or interleaved. It is **not** a property of "using threads carefully" — it's a property you can name for a specific class:

- `HashMap` is **not** thread-safe — concurrent writes can corrupt the internal bucket structure, or a write-during-iteration throws `ConcurrentModificationException`
- `ConcurrentHashMap` **is** thread-safe — internally partitioned/lock-striped so multiple threads can read and write without external synchronization
- `SecureRandom` is thread-safe by contract
- A plain `ArrayList` shared across threads is not — this is why the batching code below needs an explicit lock

The failure mode when you get this wrong is the worst kind of bug: it doesn't show up in single-threaded testing, doesn't show up under light load, and reproduces only intermittently under production concurrency — a **race condition**.

## synchronized — the built-in lock

Every Java object has an intrinsic lock (a "monitor"). `synchronized (someObject) { ... }` means: only one thread may execute that block while holding `someObject`'s lock at a time; any other thread calling it blocks until the lock is released.

This project's batching consumer accumulates records on a RabbitMQ callback thread while a separate `ScheduledExecutorService` timer flushes the same list on its own thread. Both threads touch the same `ArrayList`s:

```java
private final Object batchLock = new Object();   // a plain object used purely as a lock handle

// On the RabbitMQ callback thread:
synchronized (batchLock) {
    batch.add(transaction);
    if (batch.size() >= BATCH_SIZE) { /* snapshot and clear, still inside the lock */ }
}

// On the scheduler thread:
synchronized (batchLock) {
    if (batch.isEmpty()) return;
    /* snapshot and clear */
}
```

Two rules that matter in practice: **every** access path to the shared list must go through the same lock object (locking on one thread's copy of a reference doesn't protect anything), and the lock should be held for the shortest possible section — the actual DB flush happens *outside* the lock, since there's no reason to block the other thread while talking to MySQL.

## The JVM memory model, briefly

Modern CPUs and the JIT compiler are allowed to reorder instructions and cache values in per-core registers for performance, as long as a *single* thread can't observe the reordering. The problem: a second thread reading the same variable through main memory can observe stale or reordered values that never happen within one thread's own execution.

This is why a plain field update made on one thread is not guaranteed to become visible to another thread at all, let alone promptly — without a **happens-before** relationship between the write and the read, the JVM memory model makes no visibility guarantee whatsoever. `synchronized`, `volatile`, and the classes in `java.util.concurrent` all exist specifically to establish happens-before edges:

- Releasing a lock happens-before a later thread acquiring the *same* lock
- A write to a `volatile` field happens-before any later read of that same field
- Starting a thread happens-before anything that thread does; a thread finishing (via `join()`) happens-before the code after the `join()` call

```java
private volatile boolean shuttingDown = false;   // visible to all threads the instant it's set
```

`volatile` guarantees **visibility** (every thread sees the latest write) and prevents reordering around that field, but it does **not** provide atomicity for compound operations — `counter++` on a `volatile int` is still a read-modify-write race, because "read, increment, write" is three separate steps that can interleave across threads even though each individual step is visible. `synchronized` (or an atomic class, below) is what's needed once an operation is compound rather than a single read or write.

## java.util.concurrent — the real toolkit

`synchronized` is the primitive. `java.util.concurrent` (`j.u.c`) is the higher-level toolkit built on top of it, and is what production code actually reaches for.

### ExecutorService — thread pools

Creating a raw `new Thread()` per task doesn't scale — thread creation and teardown are expensive, and nothing bounds how many run at once. A thread pool reuses a fixed set of worker threads and queues excess work:

```java
ExecutorService pool = Executors.newFixedThreadPool(10);
pool.submit(() -> processMessage(msg));
pool.shutdown();   // stop accepting new tasks, let queued/running ones finish
```

The three knobs that actually matter, seen concretely in a Spring `ThreadPoolTaskExecutor` config:

```java
executor.setCorePoolSize(5);     // threads kept alive even when idle
executor.setMaxPoolSize(10);     // ceiling the pool can grow to under load
executor.setQueueCapacity(100);  // tasks queued once corePoolSize is busy, before maxPoolSize kicks in
```

Sizing logic: below `corePoolSize` concurrent tasks, a new thread is created per task. Beyond that, tasks queue (up to `queueCapacity`) rather than spinning up more threads immediately. Only once the queue is *also* full does the pool grow toward `maxPoolSize`. An undersized queue with a small `maxPoolSize` causes `RejectedExecutionException` under burst load; an oversized queue just hides backpressure by making callers wait longer instead of failing fast.

`ScheduledExecutorService` is the same idea for periodic/delayed work:

```java
ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
scheduler.scheduleAtFixedRate(this::flushPartialBatch, 10, 10, TimeUnit.SECONDS);
```

If the scheduled task throws an *unchecked* exception, **all future executions are silently cancelled** — no error, no log, the timer just stops firing. Always wrap the task body in try/catch if it can throw.

### CompletableFuture — composing async work

`ExecutorService.submit()` returns a `Future`, whose only real API is a blocking `.get()`. `CompletableFuture` (Java 8+) supports non-blocking composition — chaining, combining, and error handling without ever blocking a thread waiting on another:

```java
CompletableFuture<Transaction> future = CompletableFuture
        .supplyAsync(() -> fetchTransaction(id), pool)
        .thenApply(this::enrich)
        .exceptionally(ex -> { log.error("fetch failed", ex); return null; });
```

`thenApply` runs once the prior stage completes; `exceptionally` handles a failure anywhere upstream without a try/catch wrapping the whole chain. This is the standard replacement for nested callbacks when multiple async steps depend on each other.

### Atomic classes and lock-free updates

`AtomicLong`, `AtomicInteger`, `AtomicReference`, etc. wrap a single value and provide atomic compound operations without a `synchronized` block, implemented via **CAS (compare-and-swap)** — a single CPU instruction that says "set this memory location to a new value, but only if it still holds the value I last read; otherwise fail and let me retry."

```java
private final AtomicLong messagesProcessed = new AtomicLong();
messagesProcessed.incrementAndGet();          // atomic — no lost updates under concurrent increments
```

Internally, `incrementAndGet()` loops: read the current value, compute `current + 1`, attempt a CAS from `current` to `current + 1`; if another thread's write raced ahead of it and the CAS fails, retry with the freshly-read value. This is what "**lock-free**" means in practice — no thread ever blocks waiting for a lock; contention shows up as retries, not blocking, which scales far better under high contention because there's no OS-level context switch involved in a failed attempt.

`ConcurrentHashMap.newKeySet()` and `computeIfAbsent` (used for the shared cross-consumer ID-dedup set and secondary indexes in [[languages/01-java/04-persistence/01-jdbc-and-data-modeling]]) rely on the same CAS-based approach internally rather than locking the whole map on every operation — this is why `ConcurrentHashMap` scales far better under contention than `Collections.synchronizedMap(new HashMap<>())`, which locks the entire map on every single access.

### Locks beyond synchronized

`java.util.concurrent.locks.ReentrantLock` is an explicit alternative to `synchronized` with capabilities the built-in keyword doesn't have: `tryLock()` (attempt without blocking), a timeout on acquisition, and interruptibility while waiting. It must be released manually in a `finally` block — unlike `synchronized`, the compiler cannot guarantee release for you:

```java
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // critical section
} finally {
    lock.unlock();   // must be manual — a missed unlock deadlocks every future caller
}
```

Reach for `ReentrantLock` only when `synchronized` genuinely can't do the job (needing `tryLock`, fairness ordering, or multiple wait-conditions via `Condition`); otherwise `synchronized` is simpler and less error-prone since the JVM releases it automatically, including on an exception.

`CountDownLatch` coordinates "wait until N things have happened" without polling:

```java
CountDownLatch startGate = new CountDownLatch(1);
// worker threads: startGate.await();   — block until released
// main thread:    startGate.countDown(); — release all waiters at once
```

## Daemon vs non-daemon threads, and why the JVM exits underneath you

Java has two kinds of threads. **User (non-daemon) threads** keep the JVM alive as long as any one of them is running. **Daemon threads** don't — the JVM can exit even while daemon threads are still executing (this is how the garbage collector thread works: it never blocks shutdown).

`Executors.newSingleThreadScheduledExecutor()` and friends create **non-daemon** threads by default — but a thread isn't necessarily created the instant the executor is built; some implementations lazily create the worker on first task submission. This produces a genuinely subtle bug: `basicConsume()` on a message queue client is non-blocking — it registers a callback and returns immediately, so the thread that called it exits right after. If that was the *only* non-daemon thread the JVM had, and the scheduler's first task hasn't fired yet to create its own non-daemon thread, there's a real window where the JVM has zero non-daemon threads and exits — silently closing every in-flight connection and abandoning work mid-flight, with no exception anywhere in the logs.

```java
} else {
    log.info("No file provided — draining the existing queue");
    Thread.currentThread().join();   // block the main thread on itself, forever, until SIGINT
}
```

`Thread.currentThread().join()` is the idiomatic fix — "wait for this thread to finish," which for the thread calling it on itself never happens, so it blocks indefinitely and anchors the JVM alive regardless of what any executor thread is doing. `Thread.sleep(Long.MAX_VALUE)` achieves the same effect but is less semantically honest about *why* the thread is waiting.

## Graceful shutdown — the join() gap

A common shutdown bug: joining the producer thread but not the consumer.

```java
consumerThread.start();
producerThread.start();
producerThread.join();   // main() returns right after this — JVM calls System.exit() internally
// consumer may still be mid-processing when the JVM tears down every thread
```

When `main()` returns, the JVM exits and **kills every thread**, including a consumer still holding unprocessed work it pulled off a queue but hasn't persisted yet. This often "works" in testing because the consumer is usually faster than the producer, so the queue is already drained by the time the producer finishes — which makes it a genuine race condition: correct under light load, silently dropping the tail of the data under heavier load. The general lesson: **always trace through what happens to in-flight work at shutdown**, not just the happy path while running. Fixes are either joining every worker thread explicitly, or a **shutdown hook**:

```java
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    synchronized (batchLock) {
        if (!batch.isEmpty()) flushBatch(batch);   // flush whatever's still buffered
    }
}));
```

A shutdown hook runs on its own thread when the JVM begins its exit sequence (`System.exit()`, `Ctrl+C`/`SIGINT`, or `main()` returning normally) — the last chance to flush in-memory state before the process is gone.

## Why any of this matters beyond one pipeline

Every pattern above — CAS-based atomics over locks, bounded thread pools over unbounded thread creation, explicit happens-before reasoning over "it worked when I tested it" — exists because lock contention and context-switch overhead are real, measurable costs, not just correctness footguns. A `synchronized` block under heavy contention forces the OS to park and later wake blocked threads, which costs far more than the work being protected; that's the entire reason lock-free structures and fine-grained locking (per-bucket in `ConcurrentHashMap`, per-partition in most production message queues) exist. Reasoning correctly about visibility and happens-before, not just "add `synchronized` until it stops crashing," is the difference between code that happens to pass a test and code that's actually correct under concurrent load.

## Practice, not just theory

Everything above is vocabulary. It doesn't prove you can write correct concurrent code under pressure — only building something with it does. [[languages/01-java/02-jvm-and-concurrency/exercises/README|Two unsolved exercises]] sit alongside this file: a bounded blocking queue and a token-bucket rate limiter, each with a real test harness (single-threaded correctness, blocking behavior, concurrent load) that starts red and stays red until the implementation is actually correct.

## Related
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — the runtime (GC, JIT, memory areas) the memory model above sits within
- [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads]] — what changes when a thread costs almost nothing
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|Persistence & Data Modeling]] — `ConcurrentHashMap` as an in-memory store, secondary indexes under concurrent writes
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — backpressure and per-consumer connections, a concurrency problem at the network layer
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — the timed-flush/double-buffering design that motivates the `synchronized` example above
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Concurrency Exercises]] — build the reps
