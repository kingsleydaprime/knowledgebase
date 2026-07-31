# Concurrency Exercises

Two unsolved exercises to build the reps that [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] only gives you the vocabulary for. Each folder has a stub class (every method throws `UnsupportedOperationException("implement me")`) and a test file that exercises correctness under single-threaded use, blocking behavior, and concurrent load. No JUnit, no build tool — just the JDK.

**These are deliberately unsolved.** No reference implementation lives in this vault or anywhere in this repo's history — writing the solution yourself is the entire point. If you want to check your understanding against a known-correct implementation afterward, do that as a separate step once you've got your own passing.

## How to run

```bash
cd bounded-blocking-queue    # or rate-limiter
javac --release 17 *.java
java BoundedBlockingQueueTest   # or RateLimiterTest
```

Right now, both fail immediately with `UnsupportedOperationException: implement me` — that's the starting (red) state. Implement the stub class until every test prints `PASS` and the summary line reads `N passed, 0 failed`.

## 1. [[bounded-blocking-queue/BoundedBlockingQueue.java|Bounded Blocking Queue]]

A fixed-capacity queue where `put()` blocks while full and `take()` blocks while empty, safe under multiple concurrent producers and consumers. This is the exact shape of the batching problem in [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] and [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]]'s `batchLock` example — except here you're building the primitive instead of using one someone else already wrote (`java.util.concurrent.ArrayBlockingQueue` is the real one; don't use it, that's the class you're re-deriving).

Forces you to actually reason about: `wait()`/`notifyAll()` (or `Condition`/`await()`/`signalAll()` if you use `ReentrantLock` instead of `synchronized`), spurious wakeups (why the wait condition must be checked in a `while` loop, not an `if`), and what exactly a monitor guarantees vs. what it doesn't.

## 2. [[rate-limiter/RateLimiter.java|Token-Bucket Rate Limiter]]

A non-blocking `tryAcquire()` that allows bursts up to a bucket capacity, refilling continuously at a fixed rate, safe under concurrent callers.

Forces you to reason about: representing continuous time-based state (fractional token accumulation, not "wait for a whole token") under concurrent access, and the difference between locking the whole operation (`synchronized`) vs. a lock-free CAS retry loop (see the atomics section of [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]]) — worth implementing once with `synchronized` and, if you want the harder version, once again with `AtomicReference`/CAS and no lock at all.

## Related
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — the concepts these exercises exercise
- [[languages/01-java/README|Java course index]]
