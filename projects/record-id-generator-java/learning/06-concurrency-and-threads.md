# Record ID Generator — Concurrency & Threads

Split out from the original single-file `learning.md`. Covers Java threads and the producer/
consumer graceful-shutdown gap. See also `05-rabbitmq-messaging.md`.

---

## 10. Threads — Running Code Concurrently

A **thread** is an independent execution path. The JVM runs multiple threads simultaneously.

```java
// Create a thread
Thread producerThread = new Thread(() -> {
    producer.produce(filePath); // runs in parallel
});

Thread consumerThread = new Thread(() -> {
    consumer.consume(); // also runs in parallel
});

// Start both
consumerThread.start(); // start consumer first — it needs to be ready
producerThread.start();

// Wait for producer to finish before exiting main
producerThread.join();
```

### Why threads here?

- **Producer** reads 1.46GB CSV and pushes to queue — slow I/O
- **Consumer** listens on queue and writes to DB — separate pace

Without threads, they'd run sequentially: produce everything, then consume. With threads, they run at the same time — producer fills the queue as consumer drains it.

### Thread safety

When multiple threads share data, conflicts can happen. In this project:
- Producer and consumer don't share state — RabbitMQ is the middleman
- HikariCP handles concurrent DB connections safely
- `SecureRandom` in `IdGeneratorService` is thread-safe

---


---

## 24. Graceful Shutdown — The join() Gap

In `Main.java`, the producer thread is joined but the consumer thread is not:

```java
consumerThread.start();
producerThread.start();

producerThread.join();  // waits for producer to finish
// main() returns here — JVM exits
```

When `main()` returns, the JVM calls `System.exit()` internally, which **kills all threads** — including the consumer, which may still be processing messages it pulled from the queue but hasn't saved to the database yet.

In practice this often works because the consumer processes faster than the producer publishes, so by the time the producer finishes, the queue is already drained. But it's a race condition: under load, the last batch of messages could be lost.

The correct fix is to signal the consumer to stop and then wait for it:

```java
// Option 1: join the consumer too (if consume() returns at some point)
consumerThread.join();

// Option 2: use a CountDownLatch or poison pill message
// Producer sends a special "DONE" message as the last item
// Consumer exits its loop when it sees it, then the thread ends naturally
```

This is a general lesson: **always think about what happens when your app shuts down**. Data pipelines can silently lose the last few records if shutdown isn't handled explicitly.

---


---

## The general version of this
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java course)]] — the standalone treatment: memory model, locks, atomics
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Concurrency exercises]] — build a bounded blocking queue and a rate limiter
- [[foundations/os/interview/01-processes-memory-and-io|OS: what a context switch actually costs]]

↑ [[projects/README|All projects and the domains they exercise]]
