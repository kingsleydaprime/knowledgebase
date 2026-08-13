# Messaging with RabbitMQ

**Source:** `record-id-generator-java/learning/05-rabbitmq-messaging.md` (condensed — the full version includes a real production debugging narrative worth reading in the original for the diagnostic process itself).

## Core concepts

RabbitMQ is a **message broker** — it decouples producers from consumers so each can run at its own pace:

```
[File] → [Producer] → [Queue] → [Consumer] → [MySQL]
```

The producer never waits on the database; the consumer never waits on the file. If the consumer crashes, unacked messages stay in the queue — nothing is lost.

```java
// Producer
channel.queueDeclare("record.queue", true, false, false, null);   // durable=true survives a broker restart
channel.basicPublish("", "record.queue", null, message.getBytes());

// Consumer
channel.basicConsume("record.queue", false, (tag, delivery) -> {
    // process...
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
}, tag -> {});
```

`basicConsume` is **non-blocking** — it registers the callback and returns immediately; the callback fires later on RabbitMQ's own internal thread pool. See [[languages/01-java/02-jvm-and-concurrency/02-concurrency]] for why this matters for JVM shutdown behavior.

## Dead Letter Queues

Acking a message on failure (`basicAck` inside a `catch` block) permanently discards it from the queue — it may still be logged to a database, but it can never be replayed from RabbitMQ. A **Dead Letter Queue (DLQ)** is a second queue that failed messages route to instead:

```java
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "");
args.put("x-dead-letter-routing-key", "record.queue.dlq");
channel.queueDeclare("record.queue", true, false, false, args);
```

```java
} catch (Exception e) {
    logError(e, line);
    channel.basicNack(delivery.getEnvelope().getDeliveryTag(), false, false);  // false, false → DLQ, not requeue
}
```

| | `basicAck` | `basicNack(..., false)` | `basicNack(..., true)` |
|---|---|---|---|
| Fate | Deleted from queue | Sent to DLQ | Put back at front of queue |
| Use when | Processed successfully | Failed, don't retry | Failed, retry immediately |

**`requeue=true` is dangerous for permanent failures** — a message that always fails (bad data, a broken parser) requeues forever at full speed, blocking every other message behind it (a "poison pill" loop). Reserve `requeue=true` for genuinely transient failures (a momentarily unreachable DB); use the DLQ for anything that will never succeed by retrying alone. Once fixed, RabbitMQ's **Shovel plugin** can move messages from the DLQ back to the main queue for replay.

## Backpressure, prefetch, and flushing

**Backpressure** stops a fast producer from overwhelming a slow consumer. `basicQos(n)` is the primary consumer-side lever — "deliver at most n unacked messages to me at once":

```java
channel.basicQos(500);
```

Once the consumer's 500 unacked messages are all acked, RabbitMQ delivers the next batch — the consumer controls its own intake regardless of how fast the producer publishes. (Note: Java's AMQP client blocks internally inside `basicPublish()` when the broker applies its own backpressure — unlike some other-language clients, there's no separate "drain" event to listen for; the block *is* the backpressure signal.)

**The partial-batch problem**: if a batch only flushes at exactly `BATCH_SIZE`, a file whose row count isn't a clean multiple of the batch size leaves a tail sitting unacked in memory forever, since it will never reach the threshold again. The fix is a timed flush on a separate `ScheduledExecutorService`, flushing whatever's buffered on an interval regardless of size — which is exactly the two-thread-touching-one-list scenario `synchronized` protects in [[languages/01-java/02-jvm-and-concurrency/02-concurrency]].

**Double buffering** — setting prefetch to `2 × BATCH_SIZE` instead of `1 × BATCH_SIZE` lets the consumer receive the *next* batch while the *current* batch's DB flush is still running, eliminating the idle gap where the consumer sits waiting for an insert to finish before it's allowed to receive more messages. The tradeoff is more messages held unacked in memory at once (negligible for small messages), and more re-delivery on a crash if the consumer dies mid-flight.

## Competing consumers — horizontal scaling

RabbitMQ round-robins messages across every active consumer on a queue automatically, with no coordination required between them — this is the **Competing Consumers** pattern:

```java
private static final int NUM_CONSUMERS = 4;   // rule of thumb: CPU core count, minus headroom for other threads
for (int i = 0; i < NUM_CONSUMERS; i++) {
    Thread t = new Thread(() -> new FileConsumer().consume());
    t.start();
}
```

The protocol guarantees a message goes to exactly one consumer, stays unacked until acked, and is redelivered to a *different* consumer if the original crashes mid-batch — this is **at-least-once delivery**, which is why idempotent writes (see [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency]]) matter for any consumer that might see the same message twice.

**One connection per consumer, not a shared one**: a RabbitMQ `Connection` has a single reader thread that demultiplexes all AMQP frames for every channel on that connection. Sharing one connection across many consumers funnels all their message delivery through that one reader thread — under load, it becomes the bottleneck. Giving each consumer its own `Connection` (and therefore its own reader thread) lets delivery to all consumers proceed in parallel.

**What eventually limits scaling**: not RabbitMQ itself (a single node handles millions of msgs/sec) but the downstream database's concurrent-write capacity — lock contention on shared index pages typically caps useful gains around 4-8 concurrent batch writers against a single MySQL instance; past that, added consumers buy diminishing returns.

## Related
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — the threading model underneath consumer scaling
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — why at-least-once delivery needs an idempotent write path
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — what happens on the database side once messages are flowing

## Seen in the wild
- [[projects/record-id-generator-java/learning/05-rabbitmq-messaging|record-id-generator]] — RabbitMQ in production: DLQs, prefetch, consumer scaling
- [[projects/socioboom/interview/02-queues-and-deployment|socioboom]] — queues and deployment, the same problems on a different stack
