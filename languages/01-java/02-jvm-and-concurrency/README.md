# 02 — JVM & Concurrency

How Java actually runs, and how to make it run correctly and fast under concurrent load. For a low-latency / systems-oriented target this is the highest-signal section in the domain — GC behavior, the memory model, and lock-free structures are exactly what such roles screen for. Part of the [[languages/01-java/README|Java course]].

1. [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — class loading, bytecode, the JIT, the runtime memory areas (heap/stack/metaspace), garbage collection (generational, G1/ZGC, pause behavior), escape analysis, and tuning
2. [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — threads, thread-safety, `synchronized`, the Java memory model (happens-before, `volatile`), `java.util.concurrent` (executors, `CompletableFuture`, atomics/CAS, locks), daemon threads, graceful shutdown
3. [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads]] — Project Loom: what changes when a thread costs almost nothing, structured concurrency, and where it does and doesn't help

## Practice
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Exercises]] — two unsolved, runnable exercises (a bounded blocking queue and a token-bucket rate limiter) with a red-to-green test harness. The notes give the vocabulary; these build the reps.

## Related
- [[languages/01-java/01-language/04-collections|Collections]] — the thread-safe variants (`ConcurrentHashMap`) live at the intersection of these two sections
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — where GC and concurrency show up as real throughput numbers
- [[languages/01-java/README|Java course index]]
