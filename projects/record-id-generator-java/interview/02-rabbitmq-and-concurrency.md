# record-id-generator-java — RabbitMQ & Concurrency

From [`../learning/05-rabbitmq-messaging.md`](../learning/05-rabbitmq-messaging.md) and
[`06-concurrency-and-threads.md`](../learning/06-concurrency-and-threads.md).

---

### Q1. [Beginner] 🔥 Why is there a message queue here at all? The producer and consumer are in the same JVM.

**Strong answer covers:** the honest answer first — for a single-process loader you could pass rows
over a `BlockingQueue` and skip the broker entirely. What the broker buys: **durability** (a crash
doesn't lose in-flight rows if messages are persistent), **decoupling of rate** (producer and
consumer run at their own speeds with the queue absorbing the difference), **independent scaling**
(add consumers without touching the producer), and a **retry/DLQ mechanism** you'd otherwise
hand-roll. It also makes the consumer deployable as a separate process later with no code change.

Saying "you wouldn't need this for the simplest version, here's what it earns" is a much stronger
answer than justifying it reflexively.

---

### Q2. [Intermediate] 🔥 What's the difference between `prefetchCount` and `BATCH_SIZE`? They're both 500 in your code.

**Strong answer covers:** they solve different problems and being the same number is a deliberate
choice, not a coincidence.
- **`BATCH_SIZE`** — how many rows the consumer accumulates in memory before writing to the
  database. A *database* tuning knob.
- **`prefetchCount`** (`channel.basicQos(500)`) — how many unacked messages RabbitMQ will deliver to
  this consumer at once. A *broker flow-control* knob.

Setting them equal means that by the time you have a full batch in memory, you've received exactly
as many messages as you can hold.

**The follow-up that shows you understand it:** you can deliberately separate them —
`basicQos(1000)` with `BATCH_SIZE = 500` lets the consumer receive messages 501–1000 *while* it's
still writing 1–500 to the database, overlapping network and disk work. Higher throughput, more
memory, larger blast radius on a crash.

---

### Q3. [Intermediate] 🔥 Explain backpressure here. What stops the producer flooding the system?

**Strong answer covers:** two layers.
- **Consumer-side:** `basicQos(500)` is the primary tool — RabbitMQ delivers at most 500 unacked
  messages and stops until they're acked. The consumer controls its own intake; a busy consumer
  simply stops receiving.
- **Broker-side:** RabbitMQ has its own flow control — when memory or disk thresholds are exceeded
  it blocks publisher connections until things clear.
- **Producer-side (optional):** check queue depth before publishing
  (`channel.messageCount(queue)`) and sleep if it exceeds a threshold, so the queue doesn't grow
  unboundedly while the consumer falls behind.

**The distinction to make:** prefetch protects the *consumer's memory*; producer-side depth checks
protect the *broker's memory*. They're different failure modes and only one of them is solved by
`basicQos`.

---

### Q4. [Intermediate] 🔥 Why is acking on failure a bug, and what does a DLQ do about it?

**Strong answer covers:** ack means "I've handled this, delete it." Acking a message you failed to
process silently discards data — the row is gone from the queue and never reached the database, with
nothing to indicate loss. Nacking without requeue-to-somewhere just moves the problem: requeue
`true` and a permanently-bad message loops forever (a poison message), starving the consumer.

A **dead-letter queue** is the third option: nack with `requeue=false` and the broker routes the
message to a dead-letter exchange/queue instead of destroying it. The bad message leaves the hot
path but survives for inspection, so you can see *what* failed and why, and replay it after a fix.

**Follow-up:** *"How do you replay from a DLQ?"* — the shovel plugin moves messages from the DLQ
back to the main queue once the underlying bug is fixed. Point worth adding: replay is only safe
because the pipeline is idempotent (`INSERT IGNORE` / unique key), otherwise replay is just
duplication.

---

### Q5. [Advanced] What makes a message "poison", and how do you stop it looping forever?

**Strong answer covers:** a message that fails deterministically — malformed data, an unparseable
row — so every retry fails identically. With `requeue=true` it returns to the queue, gets redelivered
immediately, and burns the consumer in a tight loop. Defences: dead-letter after N attempts (track
delivery count via the `x-death` header or a retry-count header), or classify errors and only requeue
*transient* ones (broker/DB unavailable) while dead-lettering *permanent* ones (bad data). That's the
same "retry only what retrying can fix" rule that governs HTTP status handling.

---

### Q6. [Advanced] 🔥🔥 Walk me through the graceful-shutdown bug in `Main`.

**Strong answer covers:** the producer thread is joined; the consumer thread is not.

```java
consumerThread.start();
producerThread.start();
producerThread.join();   // main() returns here — JVM exits
```

When `main()` returns and no non-daemon threads remain to hold it open, the JVM exits and kills the
consumer mid-flight — it may hold messages pulled from the queue but not yet written to the
database. **In practice it usually works**, because the consumer drains faster than the producer
publishes, so the queue is empty by the time the producer finishes. That's precisely what makes it
dangerous: it's a race condition that hides under normal load and loses the last batch under
pressure.

**The fixes:** join the consumer too (needs the consume loop to actually terminate), or signal
termination explicitly — a `CountDownLatch`, or a **poison-pill** message the producer sends last,
which the consumer recognises as "no more work" and exits cleanly after flushing its partial batch.

**The general lesson to state:** always ask what happens at shutdown. Data pipelines silently lose
their last few records when shutdown isn't explicit — and "it worked in testing" is exactly the
symptom.

---

### Q7. [Intermediate] What in this system is shared between threads, and how is it made safe?

**Strong answer covers:** with multiple consumer threads each generating IDs, the in-memory dedup
set is shared and a plain `HashSet` would corrupt under concurrent mutation *and* would let two
threads generate the same ID without noticing. So it's
`ConcurrentHashMap.newKeySet(8_000_000)` — created once in `Main` and passed to every consumer.
`add()` returning `false` is an atomic test-and-set, which is exactly the primitive needed. Other
shared state: the Hikari pool (thread-safe by design, one connection checked out per thread) and the
RabbitMQ channel — and channels are **not** thread-safe, so each consumer thread needs its own.

**Worth pre-empting:** the single-threaded bulk loader uses a plain pre-sized `HashSet` instead,
because there's no sharing — matching the tool to the actual concurrency rather than defensively
using the concurrent type everywhere.

---

### Q8. [Advanced] Why does `add()` returning false matter more than `contains()` then `add()`?

**Strong answer covers:** `contains` followed by `add` is a check-then-act race — two threads can
both see "not present" and both proceed. `Set.add()` on a concurrent set is a single atomic
operation returning whether the element was newly added, so the check and the claim happen together.
It's the same shape as a guarded conditional update in SQL (`UPDATE ... WHERE balance >= x`) rather
than a `SELECT` followed by an `UPDATE`.

---

### Q9. [Intermediate] How many consumer threads, and how would you decide?

**Strong answer covers:** the work is I/O-bound (network to broker, network+disk to MySQL), not
CPU-bound, so thread count isn't bounded by cores — it's bounded by what the database will accept
without contention, which in practice means the **Hikari pool size**. More consumers than pool
connections just means threads blocking to check out a connection. So the honest sizing rule is:
consumers ≈ pool size, then measure — and watch for the point where MySQL's own lock/IO contention
makes additional writers *reduce* throughput.

---

### Q10. [Advanced] What ordering guarantees does this pipeline have, and does it need any?

**Strong answer covers:** RabbitMQ preserves order within a single queue to a single consumer, but
with multiple consumers and prefetch, rows are processed out of order relative to the file — and on
requeue, order breaks entirely. It doesn't matter here, because each row is independent and gets a
generated ID, so there's no cross-row dependency. Say this explicitly: knowing you *don't* need
ordering is as important as knowing you do, because ordering requirements are what force you back to
a single consumer and destroy the parallelism.

---

### Q11. [Beginner] Explain the RabbitMQ concepts you actually used: exchange, queue, routing key, ack.

**Strong answer covers:** a producer publishes to an **exchange**, which routes by **routing key** to
one or more **queues**; consumers subscribe to a queue and **ack** each message once handled, at
which point the broker deletes it. A default/direct exchange with one queue is all this pipeline
needs. Add the durability dimension — durable queue plus persistent messages means a broker restart
doesn't lose the backlog, at the cost of writing every message to disk, which is a real throughput
consideration for a bulk load.
