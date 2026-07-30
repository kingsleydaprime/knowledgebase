# Record ID Generator — RabbitMQ Messaging

Split out from the original single-file `learning.md`. Covers RabbitMQ fundamentals, Dead
Letter Queues, consumer flow control (backpressure, prefetch, flushing), file descriptor limits,
competing consumers for horizontal scaling, per-consumer connections, timed flush, double
buffering, and JVM keepalive during drain mode. See also `06-concurrency-and-threads.md` and
`10-docker-and-performance-tuning.md`.

---

## 9. RabbitMQ — Message Queue

RabbitMQ is a **message broker**. It decouples producers (who create messages) from consumers (who process them).

```
[File] → [Producer] → [RabbitMQ Queue] → [Consumer] → [MySQL]
```

Why? The producer can push millions of records without waiting for the DB. The consumer processes at its own pace. If the consumer crashes, messages stay in the queue — nothing is lost.

### Key concepts:
- **Queue** — holds messages until consumed
- **Channel** — a virtual connection inside a connection
- `basicPublish` — send a message
- `basicConsume` — listen and receive messages
- `basicAck` — acknowledge: "I processed this, remove it from queue"
- `basicQos(1)` — process one message at a time (fair dispatch)

```java
// Producer
channel.queueDeclare("record.queue", true, false, false, null);
//                   name           durable
channel.basicPublish("", "record.queue", null, message.getBytes());

// Consumer
channel.basicConsume("record.queue", false, (tag, delivery) -> {
    String message = new String(delivery.getBody());
    // process...
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
}, tag -> {});
```

`durable: true` means the queue survives a RabbitMQ restart.

---


---

## 28. Dead Letter Queues (DLQ)

### The Problem with Acking on Failure

The current consumer acks every message — even failures:

```java
} catch (Exception e) {
    logError(e, line);
    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);  // message is gone
}
```

This means a bad message (malformed CSV, a field that doesn't parse, a DB constraint violation you didn't expect) is **permanently lost** from the queue. It's in the `logs` table, but you can't replay it from RabbitMQ.

### What a DLQ Does

A Dead Letter Queue is a second queue where messages are sent automatically when they fail — either because:
- They were rejected (`basicNack` or `basicReject` with `requeue=false`)
- They expired (message TTL reached)
- The queue reached max length

```
Main Queue ──→ Consumer (fails) ──nack──→ Dead Letter Exchange ──→ DLQ
```

You configure it at queue declaration time:

```java
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "");           // use default exchange
args.put("x-dead-letter-routing-key", "record.queue.dlq");  // route to this queue

channel.queueDeclare("record.queue", true, false, false, args);
channel.queueDeclare("record.queue.dlq", true, false, false, null);
```

Then in the consumer, **nack instead of ack on failure**:

```java
} catch (Exception e) {
    logError(e, line);
    channel.basicNack(delivery.getEnvelope().getDeliveryTag(), false, false);
    // false, false = don't requeue → message goes to DLQ instead
}
```

Now failed messages sit in `record.queue.dlq`. You can:
- Inspect them in the RabbitMQ management UI
- Write a separate consumer to replay them after fixing the bug
- Set up alerts when DLQ depth grows

### Nack vs Ack

| | `basicAck` | `basicNack(... false)` | `basicNack(... true)` |
|---|---|---|---|
| Message fate | Deleted from queue | Sent to DLQ (if configured) | Put back at front of queue |
| Use when | Processed successfully | Failed, don't retry | Failed, retry immediately |
| Risk | — | — | Infinite loop if always failing |

`basicNack` with `requeue=true` is dangerous — if the message always fails, it gets requeued forever (poison pill loop). Only use it for transient failures (e.g., DB temporarily unreachable).

### Investigating the DLQ — Finding Out What Failed

When the pipeline finishes and the row count in the database is lower than the CSV row count, the first place to check is the DLQ. The gap is almost always sitting there. In the RabbitMQ management UI (`http://localhost:15672`), go to **Queues and Streams** and look for `record.queue.dlq`. The message count is the number of rows that failed.

To see what the actual error was, query the `logs` table:

```sql
SELECT level, source, message, payload, created_at
FROM logs
ORDER BY created_at DESC
LIMIT 50;
```

`payload` contains the raw CSV line that failed. `message` contains the Java exception message. This is why the log table stores the payload — you can see exactly what data caused the failure and fix the parsing or processing logic before replaying.

### Replaying from the DLQ — The Shovel Plugin

Once you've fixed the bug, you need to move the failed messages back to the main queue so they get processed again. RabbitMQ's **Shovel plugin** does this — it reads messages from one queue and publishes them to another.

Enable it inside the Docker container:

```bash
# Find the container name
docker ps

# Enable the plugin
docker exec record-id-generator-rabbitmq-1 rabbitmq-plugins enable rabbitmq_shovel rabbitmq_shovel_management
```

After enabling, refresh the management UI and go to **Queues → record.queue.dlq**. Scroll down to **Move messages**, set the destination to `record.queue`, and click Move. The failed messages are now back in the main queue. Run the consumer in drain mode to process them:

```bash
./gradlew run
```

The fixed code will parse them correctly this time. Any that still fail go back to the DLQ, keeping the failure set isolated and inspectable.

### The Full Failure Cycle

```
CSV row with comma in field
    ↓
parseLine() → NumberFormatException → caught by callback catch block
    ↓
logError() → writes to logs table (payload + stack trace)
    ↓
basicNack(tag, false, false) → message goes to record.queue.dlq
    ↓
Fix the bug (splitCsv instead of split(","))
    ↓
Move DLQ → record.queue via Shovel
    ↓
Consumer processes successfully → INSERT → basicAck
```

The DLQ is not just a safety net — it's a processing inbox for your failure cases. Every failure is preserved, inspectable, and replayable. Nothing is permanently lost unless you explicitly delete the DLQ.

---


---

## 31. Consumer Flow Control — Backpressure, Prefetch, and Flushing

These concepts come up when you're tuning a message consumer for reliability and throughput. They are related but solve different problems.

---

### Backpressure

**Backpressure** is the mechanism that stops a fast producer from overwhelming a slow consumer. Without it, the producer can flood the queue faster than the consumer can process, causing the RabbitMQ broker to run out of memory.

`basicQos` is the primary backpressure tool on the consumer side:

```java
channel.basicQos(500);
```

This tells RabbitMQ: "deliver at most 500 unacked messages to me at once." Once our batch fills and we ack all 500, RabbitMQ delivers the next 500. The consumer controls its own intake. If the consumer is busy, RabbitMQ simply stops delivering — the producer can keep publishing into the queue, but the consumer won't be overwhelmed.

**Producer-side backpressure** (optional — if the queue grows too large):

```java
// Before publishing each line, check queue depth
long depth = channel.messageCount(RabbitMQConfig.getQueueName());
if (depth > 50_000) {
    Thread.sleep(500);  // pause — consumer is falling behind
}
```

RabbitMQ also has its own built-in flow control: when its memory or disk threshold is exceeded, it automatically blocks all publisher connections until things clear.

---

### prefetchCount vs BATCH_SIZE

These are the same number in our code — both set to 500. They serve two different purposes:

```java
private static final int BATCH_SIZE = 500;      // how many rows to accumulate before saving
channel.basicQos(BATCH_SIZE);                   // how many messages RabbitMQ delivers at once
```

**`prefetchCount` (the `basicQos` argument)** controls how many messages RabbitMQ delivers to this consumer without waiting for an ack. Setting it equal to `BATCH_SIZE` means: by the time we have a full batch in memory, we've received exactly as many messages as we can hold. They're kept in sync deliberately.

You could separate them:
```java
channel.basicQos(1000);    // prefetch 1000 — keep the consumer busy
// BATCH_SIZE = 500        — but only flush to DB every 500
```

This can improve throughput: the consumer receives messages 501–1000 while it's still writing messages 1–500 to the DB.

---

### channel.sendToQueue returning false and drain (Node.js)

If you encounter this in Node.js code or documentation, here is what it means — and what the Java equivalent is.

In the Node.js `amqplib` library:

```javascript
const ok = channel.sendToQueue(queue, Buffer.from(message));
if (!ok) {
    // The TCP write buffer is full — stop publishing
    // Resume when the buffer drains
    channel.once('drain', () => {
        resumePublishing();
    });
}
```

`sendToQueue` returns `false` when the underlying TCP socket's write buffer is backed up. The `drain` event fires when the buffer empties. This is **TCP-level backpressure** bubbling up through the AMQP client.

In Java, the AMQP client handles this transparently — `basicPublish()` **blocks internally** until there is space in the write buffer. You never see a `false` return value. The blocking behaviour is the Java equivalent of pausing on `false` and waiting for `drain`.

---

### The Partial Batch Problem and flushIntervalMs

The current code only flushes when the batch hits exactly `BATCH_SIZE`:

```java
if (batch.size() >= BATCH_SIZE) {
    flushBatch(channel, batch, batchLines, deliveryTags);
}
```

If the file has 5,487 rows: the first 5,000 are processed in 10 clean batches of 500. The last **487 sit in the batch buffer unacked forever** — never flushed because they never hit 500.

When the process exits, those 487 messages are lost from memory. RabbitMQ still holds them as unacked and **redelivers them on the next run**. With `source_hash` they'll be processed as normal inserts (or duplicates if somehow the process saved some before crashing). This works but it's wasteful — every run reprocesses the tail.

**`flushIntervalMs`** is the configurable timeout that solves this: flush the partial batch every N milliseconds even if it hasn't hit `BATCH_SIZE`.

```java
private static final long FLUSH_INTERVAL_MS = 5_000;  // flush at least every 5 seconds
```

Implementation using a `ScheduledExecutorService`:

```java
ScheduledExecutorService flushTimer = Executors.newSingleThreadScheduledExecutor();
flushTimer.scheduleAtFixedRate(() -> {
    synchronized (batch) {
        if (!batch.isEmpty()) {
            try {
                flushBatch(channel, batch, batchLines, deliveryTags);
            } catch (Exception e) {
                log.error("Timer flush failed", e);
            }
        }
    }
}, FLUSH_INTERVAL_MS, FLUSH_INTERVAL_MS, TimeUnit.MILLISECONDS);
```

The `synchronized (batch)` is necessary because the timer runs on a **different thread** than the RabbitMQ callback. Both threads touch the `batch` list — without synchronisation, you get a `ConcurrentModificationException` or silent data corruption. The same `synchronized` block must also wrap every `batch.add(...)` call inside the callback.

---

### Flushing on Process Exit (Shutdown Hook)

A JVM **shutdown hook** is a thread that runs when the process is about to exit — triggered by CTRL+C, `System.exit()`, or `main()` returning normally:

```java
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    log.info("Shutdown — flushing {} remaining messages", batch.size());
    synchronized (batch) {
        if (!batch.isEmpty()) {
            try {
                flushBatch(channel, batch, batchLines, deliveryTags);
                log.info("Final flush complete");
            } catch (Exception e) {
                log.error("Final flush failed — {} messages returned to queue", batch.size());
            }
        }
    }
    flushTimer.shutdown();
}));
```

This covers the partial batch gap: when the producer finishes and the process exits, the shutdown hook fires, flushes whatever remains, and the consumer exits cleanly.

The shutdown hook is also on a different thread. It works correctly here because by the time the hook runs, the RabbitMQ callback thread has stopped delivering messages (the connection is closing), so no concurrent modifications can happen.

---

### Keeping Messages Tied to Their Batch

This is what the three parallel lists in `FileConsumer` do:

```java
List<Transaction> batch       = new ArrayList<>();  // parsed objects to insert
List<String>      batchLines  = new ArrayList<>();  // raw CSV lines for error logging
List<Long>        deliveryTags = new ArrayList<>();  // RabbitMQ tags for ack/nack
```

They are always kept in sync — index `i` in all three refers to the same original message. This is important for two reasons:

**1. Multi-ack the whole batch:**
```java
// Ack everything up to and including the last tag
channel.basicAck(deliveryTags.get(deliveryTags.size() - 1), true);
//                                                           ^^^^
//                                                      multiple=true
```

**2. Per-message ack/nack on fallback:**
```java
for (int i = 0; i < batch.size(); i++) {
    try {
        saveWithRetry(batch.get(i));
        channel.basicAck(deliveryTags.get(i), false);         // saved — ack this one
    } catch (Exception e) {
        logError(e, batchLines.get(i));                        // log the raw CSV line
        channel.basicNack(deliveryTags.get(i), false, false);  // failed — DLQ
    }
}
```

Messages stay **unacked in RabbitMQ** for the entire time they sit in the batch buffer. If the app crashes before flushing, RabbitMQ automatically redelivers them to the next consumer that connects. This is **at-least-once delivery** — the message is guaranteed to be processed at least once. The `source_hash` constraint makes redelivery safe by turning duplicate saves into no-ops.

---

### requeue=true vs requeue=false

```java
channel.basicNack(tag, false, true);   // → back to front of queue (retry)
channel.basicNack(tag, false, false);  // → DLQ (park it)
```

Use **requeue=true** only for transient failures where retrying might work:
- DB connection momentarily dropped
- Timeout on a slow query
- Lock contention

Use **requeue=false** (DLQ) for permanent failures where retrying will never work:
- CSV field that won't parse (bad data)
- Constraint violation that won't go away
- Missing required field

The distinction matters because `requeue=true` on a permanently broken message creates a **poison pill loop**: the message goes back to the queue, the consumer picks it up again, fails again, requeues again — forever, at full speed, blocking other messages.

---

### Summary — What Each Knob Controls

| Concept | What it controls | In our code |
|---|---|---|
| `basicQos(n)` / `prefetchCount` | Max unacked messages RabbitMQ delivers | `BATCH_SIZE = 500` |
| `BATCH_SIZE` | How many rows to accumulate before DB insert | 500 |
| `FLUSH_INTERVAL_MS` | Max time a partial batch waits before flush | Not yet implemented |
| Shutdown hook | Flushes remaining batch on process exit | Not yet implemented |
| `basicAck(..., true)` | Acks all messages up to this tag at once | Used after every `flushBatch` |
| `basicNack(..., false)` | Parks message in DLQ | Used on unrecoverable errors |
| `basicNack(..., true)` | Requeues message for retry | Not used — reserved for transient DB failures |
| Backpressure | Slows producer when consumer is behind | Implicit via `basicQos` |

---


---

## 36. File Descriptors — Why RabbitMQ Warns About File Handles

### What the Warning Means

```
[warning] Available file handles: 1024. Please consider increasing system limits
```

Every process on Linux is given a quota of **file descriptors** (FDs) — numbered slots it can use to hold open files, sockets, pipes, and other I/O resources. The default limit per process is 1024.

RabbitMQ uses file descriptors for:
- Every network connection (one FD per TCP socket — each producer and consumer uses at least one)
- Queue storage files (persistent queues are backed by files on disk)
- Internal Erlang runtime processes
- Log files

At 1024 FDs, a busy RabbitMQ node can run out. When it does, it cannot accept new connections and starts rejecting clients. For a development setup with one producer and one consumer the limit is unlikely to be hit, but the warning is still worth fixing — and it matters more as you scale.

### How to Fix It in Docker

Set `ulimits` on the RabbitMQ container in `docker-compose.dev.yml`:

```yaml
rabbitmq:
  image: rabbitmq:management
  ulimits:
    nofile:
      soft: 65536
      hard: 65536
```

`nofile` = "number of open files". `soft` is the default limit the process starts with. `hard` is the ceiling it can raise itself to. Setting both to 65536 (64K) matches RabbitMQ's recommendation for development and light production use.

Restart RabbitMQ to apply (no data is lost — queues are in-memory for dev):
```bash
docker compose -f docker-compose.dev.yml restart rabbitmq
```

After restart the warning disappears. You can verify:
```bash
docker exec $(docker compose -f docker-compose.dev.yml ps -q rabbitmq) \
    rabbitmqctl status | grep "File Descriptors"
# Should show: Total: 65536, Available: 65xxx
```

### For Direct Ubuntu Install (No Docker)

If RabbitMQ is installed directly on Ubuntu, set the limit in `/etc/security/limits.conf`:

```
rabbitmq soft nofile 65536
rabbitmq hard nofile 65536
```

Or in the systemd service override (`/etc/systemd/system/rabbitmq-server.service.d/limits.conf`):

```ini
[Service]
LimitNOFILE=65536
```

Then `sudo systemctl daemon-reload && sudo systemctl restart rabbitmq-server`.

### File Descriptor Sizing

| Setup | Recommended `nofile` |
|---|---|
| Development (1-2 connections) | 65536 |
| Small production (< 100 connections) | 65536 |
| Large production (100+ connections, many queues) | 500000+ |

RabbitMQ's own documentation recommends at least 65536 for any deployment. The Linux kernel default of 1024 is a historical artefact from an era when processes rarely needed more than a few hundred open files simultaneously.

---


---

## 37. Competing Consumers — Scaling Horizontally

### The Idea

The queue is a waiting room. Right now one consumer empties it. Put four consumers in the room and they empty it four times faster. RabbitMQ handles the distribution automatically — no coordination required between consumers.

```
                    ┌─ consumer-1 → batch 50k → MySQL
Producer → Queue ───┼─ consumer-2 → batch 50k → MySQL
                    ├─ consumer-3 → batch 50k → MySQL
                    └─ consumer-4 → batch 50k → MySQL
```

This is called the **Competing Consumers pattern**. RabbitMQ round-robins messages across all active consumers on the queue. Each consumer sees a different subset of messages — no message is delivered to two consumers simultaneously. Each consumer maintains its own batch buffer, its own delivery tags, its own DB connections. They never talk to each other.

The protocol guarantees: a message is delivered to exactly one consumer, and stays unacked in the queue until that consumer acks it. If a consumer crashes mid-batch, RabbitMQ redelivers its unacked messages to another consumer. `source_hash` + `INSERT IGNORE` makes this safe — the redelivered rows are just skipped.

---

### On the Same Machine — Multiple Threads

The simplest scaling: run multiple `FileConsumer` instances in the same JVM process. Each gets its own channel.

```java
private static final int NUM_CONSUMERS = 4;  // tune to your CPU core count

for (int i = 0; i < NUM_CONSUMERS; i++) {
    FileConsumer consumer = new FileConsumer();
    Thread t = new Thread(() -> consumer.consume());
    t.setName("consumer-" + (i + 1));
    t.start();
}
```

This is already in `Main.java`. A quad-core machine can run 4 consumers in parallel. Each uses one CPU core for CSV parsing and SHA-256 hashing, and one DB connection during a batch flush.

**Rule of thumb**: set `NUM_CONSUMERS` to the number of CPU cores available, minus 1 for the producer thread. On a 4-core machine: 3 consumers. On an 8-core machine: 7 consumers. In practice, the bottleneck is more often MySQL write throughput than CPU — so it is worth testing higher counts. **10 consumers ran successfully on this project's machine** without needing to be reduced, processing 5.75M rows across all 10 threads simultaneously. The initial concern that 10 connections might cause stability problems turned out to be a different bug (see the `declareQueues` race condition below) — once that was fixed, 10 consumers was completely stable.

### The declareQueues Race Condition

When each consumer thread calls `consume()`, the original code called `RabbitMQConfig.declareQueues(channel)` at the start — declaring the DLQ and main queue from within each consumer's own connection. With 10 consumers starting simultaneously on 10 different connections, all 10 sent `Queue.Declare` frames to RabbitMQ for the same queues at the same instant.

RabbitMQ serialises concurrent declarations of the same queue internally. With 10 simultaneous requests, the server backed up and the consumer threads blocked indefinitely waiting for `Queue.DeclareOk` — no exception, no error, no log output. The connections showed as `running` in the management UI, channels were open, but `basicConsume` was never reached. Unacked stayed at 0.

The diagnostic clue was the **"To client: 2 B/s"** column in the Connections tab — 2 bytes per second is just heartbeat traffic. If messages were being delivered, it would show KB/s or MB/s. Heartbeat-only traffic with consumers registered means `basicConsume` was never called.

The fix: declare queues exactly **once** from the main thread before any consumer starts, then remove the call from `consume()`.

```java
// Main.java — before starting consumer threads
try (Channel setupChannel = RabbitMQConfig.createChannel()) {
    RabbitMQConfig.declareQueues(setupChannel);  // done once, not 10 times racing
}

// FileConsumer.consume() — declaration removed
Channel channel = RabbitMQConfig.createChannel();
channel.basicQos(BATCH_SIZE * 2);
// ... no declareQueues call here anymore
channel.basicConsume(...);
```

The rule: queue declaration is the producer's job (or the app's one-time setup job). Consumers should assume the queue exists and just consume from it.

---

### On Multiple Machines — True Horizontal Scale

If one machine isn't enough, run consumer instances on N machines all pointing at the same RabbitMQ and MySQL:

```
Machine 1: producer + 4 consumers ──┐
Machine 2: 4 consumers ─────────────┼──→ RabbitMQ ──→ MySQL
Machine 3: 4 consumers ─────────────┘
```

The only requirement: each machine can reach RabbitMQ and MySQL over the network. The `application.properties` hosts would change from `localhost` to the actual server IPs.

To run only the consumer (no producer) on a machine, you'd split `Main.java` into two modes — or just let the producer finish quickly while the consumers on all machines drain the queue together.

---

### What Limits the Scaling

Adding more consumers helps until something else becomes the bottleneck:

**MySQL concurrent writes**: multiple consumers flushing 50,000 rows simultaneously compete for InnoDB write resources — the redo log, the buffer pool, and index page locks. Typically useful up to 4-8 concurrent batch writers on a single MySQL instance. Beyond that, lock contention grows faster than throughput.

**MySQL connection pool**: each consumer needs one connection during a batch flush. With 4 consumers × pool size of 20 = up to 20 simultaneous connections. MySQL's default `max_connections = 151` handles this easily. Increase if you scale to many machines.

**RabbitMQ throughput**: a single RabbitMQ node can handle millions of messages/sec. For 15M rows it is never the bottleneck.

**Network bandwidth**: if consumers are on different machines, the data travels: RabbitMQ → consumer network → MySQL. A 1Gbps network handles ~100MB/sec, sufficient for this workload.

---

### Performance Estimate — 15M Rows With 4 Consumers

Without the unique index during load (drop-then-rebuild pattern):

| Consumers | Rows/sec | 15M rows |
|---|---|---|
| 1 | ~25,000 | ~10 min |
| 4 | ~80,000 | ~3 min |
| 8 | ~120,000 | ~2 min |

Gains are not perfectly linear because MySQL write throughput is shared. 4 consumers is typically the sweet spot for a single MySQL instance on a dev machine. Beyond 4, you get diminishing returns unless MySQL is on dedicated hardware.

---

### Connection Pool Sizing

With multiple consumers, the HikariCP pool needs to be large enough that no consumer waits for a connection during a flush:

```java
// Rule: pool size ≥ NUM_CONSUMERS + a small buffer for Flyway and overhead
config.setMaximumPoolSize(20);  // covers 4 consumers with room to spare
```

If `waiting > 0` appears in HikariPool stats, the pool is too small. Increase `maximumPoolSize` (and check MySQL's `max_connections` allows it).

---

### Cross-Consumer ID Dedup — The Shared Set Problem

When the unique index is dropped for speed (drop-then-rebuild pattern), each consumer independently generates IDs with no DB-level safety net. Two consumers can generate the same `generated_id` simultaneously and both insert it — silent duplicates in the database.

A per-consumer `HashSet` only prevents collisions within one consumer's own generated IDs. It can't see what the other 9 consumers have generated.

**The fix: a shared `ConcurrentHashMap.newKeySet()` passed to all consumers at startup:**

```java
// Main.java — file-load mode only
Set<Long> usedIds = ConcurrentHashMap.newKeySet(8_000_000);

// Each consumer gets the same set reference
FileConsumer consumer = new FileConsumer(usedIds);
```

```java
// FileConsumer.java — the set is checked atomically
private String generateUniqueId() {
    if (usedIds == null) return idGenerator.generate();  // drain mode: index handles it
    String id = idGenerator.generate();
    while (!usedIds.add(Long.parseLong(id))) {           // add() is atomic in ConcurrentHashMap
        id = idGenerator.generate();
    }
    return id;
}
```

`ConcurrentHashMap.newKeySet()` is thread-safe — multiple threads calling `add()` simultaneously is safe with no external synchronisation. `add()` returns `false` if the value was already present, `true` if newly added. The `while` loop retries until the current thread successfully "claims" the ID.

**Two modes, two strategies:**

| Mode | Index during load | ID dedup mechanism |
|---|---|---|
| File load (`args.length > 0`) | Dropped for speed | Shared `ConcurrentHashMap` across all consumers |
| Drain (no file) | Present | DB unique index catches rare collisions via retry |

The `usedIds` field is `null` in drain mode — `generateUniqueId()` falls back to plain `idGenerator.generate()`, and the existing retry-on-1062 logic handles the ~16 collisions the DB will catch.

---

### This Is Why the Architecture Uses RabbitMQ

Direct CSV-to-MySQL (without a queue) can only use one writer at a time per file — you'd need to split the file manually to parallelise. With RabbitMQ, the queue automatically distributes work to however many consumers you add, on however many machines you have. Adding a new consumer is just starting a new process — no file splitting, no coordination, no code change.

This is the core value proposition of a message queue in a data pipeline.

---


---

## 40. Per-Consumer Connections — Removing the Shared Reader Thread

### Original Design — One Shared Connection

`RabbitMQConfig` originally had a **static** `Connection`:

```java
public class RabbitMQConfig {
    private static Connection connection;  // ONE connection, shared by everything

    static {
        // runs once at class load
        connection = factory.newConnection();
    }

    public static Channel createChannel() throws IOException {
        return connection.createChannel();  // all channels share this one connection
    }
}
```

All 6 (later 10) consumers called `createChannel()` and got channels on the same underlying TCP connection.

### The Problem — One Reader Thread for All Consumers

A RabbitMQ `Connection` has one **reader thread** — a single thread that reads all AMQP frames off the TCP socket and routes them to the correct channel. With 6 consumers sharing one connection:

```
RabbitMQ server
     │
     TCP socket (one reader thread)
     │
     ├─ channel-1 → consumer-1 callback
     ├─ channel-2 → consumer-2 callback
     ├─ channel-3 → consumer-3 callback
     ├─ channel-4 → consumer-4 callback
     ├─ channel-5 → consumer-5 callback
     └─ channel-6 → consumer-6 callback
```

All 6 consumers' messages had to pass through that single reader thread. With 140,000+ messages in the queue, the reader thread became the bottleneck — it was routing frames faster than it could keep up under load.

### The Fix — One Connection Per Consumer

```java
public class RabbitMQConfig {
    private static final ConnectionFactory factory;  // factory is shared, connections are not

    static {
        factory = new ConnectionFactory();
        factory.setHost(props.getProperty("rabbitmq.host"));
        // ... other config ...
    }

    // Each call creates a fresh Connection → its own reader thread
    public static Channel createChannel() throws IOException, TimeoutException {
        return factory.newConnection().createChannel();
    }
}
```

Now each consumer gets its own TCP connection when it calls `createChannel()`. Each connection has its own reader thread:

```
RabbitMQ server
     │
     ├─ TCP connection-1 (reader thread 1) → consumer-1
     ├─ TCP connection-2 (reader thread 2) → consumer-2
     ├─ TCP connection-3 (reader thread 3) → consumer-3
     ├─ TCP connection-4 (reader thread 4) → consumer-4
     ├─ TCP connection-5 (reader thread 5) → consumer-5
     └─ TCP connection-6 (reader thread 6) → consumer-6
```

Message delivery to all 6 consumers now happens in parallel. No single reader thread is a bottleneck.

**Import change:** `createChannel()` now throws `TimeoutException` (because `factory.newConnection()` can time out), so the method signature changed from `throws IOException` to `throws IOException, TimeoutException`. This required updating `consume()` in `FileConsumer` — but `consume()` already declared `throws java.util.concurrent.TimeoutException`, so no change was needed there.

**Why the channel stays alive after `consume()` returns:** the `channel` local variable is captured by the callback lambda and the scheduler lambda. Java keeps it alive as long as those lambdas are referenced. The connection behind the channel stays alive because the channel references it internally, and the connection's reader/writer threads are GC roots.

---

## 41. Timed Flush — Draining the Tail Without a Full Batch

### The Problem — Partial Batches That Never Flush

Each consumer only flushes when its batch reaches `BATCH_SIZE` (10,000 rows). With 140,000 messages remaining in the queue across 10 consumers:

```
140,000 / 10 = 14,000 messages per consumer
14,000 / 10,000 = 1 full flush + 4,000 leftover
```

Those 4,000 leftover messages per consumer sit in the in-memory batch list. They are **unacked in RabbitMQ** (held but not yet acknowledged). Since `BATCH_SIZE` is never reached again (the queue is empty), they are never flushed. The database never receives them. The consumers just sit there waiting for a batch that will never fill up.

### The Fix — ScheduledExecutorService

A `ScheduledExecutorService` fires a "timed flush" every `FLUSH_INTERVAL_SECONDS` seconds. If the batch has anything in it, it's flushed immediately regardless of size:

```java
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

// In FileConsumer fields:
private static final int FLUSH_INTERVAL_SECONDS = 10;
private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

// In consume():
scheduler.scheduleAtFixedRate(() -> {
    List<Transaction> batchSnapshot;
    List<String>      linesSnapshot;
    List<Long>        tagsSnapshot;

    synchronized (batchLock) {
        if (batch.isEmpty()) return;          // nothing to flush
        batchSnapshot = new ArrayList<>(batch);
        linesSnapshot = new ArrayList<>(batchLines);
        tagsSnapshot  = new ArrayList<>(deliveryTags);
        batch.clear();
        batchLines.clear();
        deliveryTags.clear();
    }

    log.info("Timed flush: flushing {} buffered messages", batchSnapshot.size());
    submitFlush(channel, batchSnapshot, linesSnapshot, tagsSnapshot);

}, FLUSH_INTERVAL_SECONDS, FLUSH_INTERVAL_SECONDS, TimeUnit.SECONDS);
```

**`scheduleAtFixedRate(task, initialDelay, period, unit)`** — runs `task` after `initialDelay`, then again every `period`. If the task throws an unchecked exception, future executions are silently cancelled (this is a known gotcha — wrap the task body in try-catch if exceptions are possible).

### Thread Safety — Why synchronized Is Needed

The RabbitMQ callback runs on RabbitMQ's internal `ConsumerWorkService` thread. The scheduler runs on its own thread. Both threads touch the same `batch`, `batchLines`, and `deliveryTags` lists.

Without synchronisation, two threads modifying a non-thread-safe `ArrayList` simultaneously causes `ConcurrentModificationException` or silent data corruption (lists appearing to have inconsistent lengths, entries pointing to the wrong index).

The fix is a **lock object** shared by both threads:

```java
private final Object batchLock = new Object();
```

Every access to the batch is wrapped:

```java
// In the RabbitMQ callback:
synchronized (batchLock) {
    batch.add(transaction);
    batchLines.add(line);
    deliveryTags.add(delivery.getEnvelope().getDeliveryTag());

    if (batch.size() >= BATCH_SIZE) {
        // snapshot and clear inside the lock
    }
}

// In the scheduler:
synchronized (batchLock) {
    if (batch.isEmpty()) return;
    // snapshot and clear inside the lock
}
```

`synchronized (batchLock)` means: only one thread can execute this block at a time. If the callback is in the middle of `batch.add()`, the scheduler waits until the lock is released before snapshotting. This prevents partial reads and concurrent modification.

The actual flush (`submitFlush`) happens **outside** the lock — there's no reason to hold the lock while talking to MySQL. Only the list operations need protection.

### submitFlush — Extracting the Flush Submission

To avoid duplicating the `flushExecutor.submit(...)` lambda in both the batch-full path and the timed flush path, a private helper method was extracted:

```java
private void submitFlush(Channel channel, List<Transaction> batchSnapshot,
                          List<String> linesSnapshot, List<Long> tagsSnapshot) {
    flushExecutor.submit(() -> {
        try {
            flushBatch(channel, batchSnapshot, linesSnapshot, tagsSnapshot);
        } catch (Exception e) {
            log.error("Flush failed, nacking {} messages to DLQ: {}", tagsSnapshot.size(), e.getMessage(), e);
            for (Long tag : tagsSnapshot) {
                try { channel.basicNack(tag, false, false); } catch (IOException ignored) {}
            }
        }
    });
}
```

Both the batch-full path and the timed flush path call `submitFlush`. The `flushExecutor` is single-threaded, so flushes are serialised — they never run concurrently, even if both the batch-full condition and the timer fire at the same moment.

---

## 42. Double-Buffering — Eliminating the Idle Gap With 2x Prefetch

### The Idle Gap Problem

With `basicQos(BATCH_SIZE)` (prefetch = 10,000) and a MySQL insert that takes 25 seconds, here is what a consumer's timeline looks like:

```
t=0s:   RabbitMQ delivers 10,000 messages (prefetch quota filled)
t=0s:   Batch fills up → flush submitted to flushExecutor
t=0s:   Consumer is now idle — all 10,000 messages are "unacked", prefetch quota full
        RabbitMQ won't send more until some are acked
t=25s:  MySQL insert completes
t=25s:  basicAck sent — all 10,000 messages acked
t=25s:  RabbitMQ delivers next 10,000 messages
t=25s:  Consumer idle again while next batch accumulates
...
```

The consumer is **idle for 25 seconds** waiting for the MySQL insert. That idle time is wasted throughput.

### The Fix — basicQos(BATCH_SIZE * 2)

With prefetch set to twice the batch size:

```java
channel.basicQos(BATCH_SIZE * 2);  // was: BATCH_SIZE
```

The timeline becomes:

```
t=0s:   RabbitMQ delivers 20,000 messages (new prefetch quota)
t=0s:   First 10,000 fill the batch → flush submitted → MySQL insert begins
t=0s:   Consumer continues receiving messages 10,001–20,000 into the NEXT batch
t=10s:  Second batch fills (10,000 more messages) → timed flush fires or batch full
t=25s:  First MySQL insert completes → ack sent for first 10,000
t=25s:  RabbitMQ can now deliver another 10,000 (quota is back at 10,000 available)
t=25s:  Second MySQL insert completes → ack sent → third batch begins
```

The consumer now has the **next batch ready** as soon as the current insert finishes. MySQL inserts continuously with no gap between them.

### Why This Works — The flushExecutor Queue

`flushExecutor` is a single-threaded executor. When the second batch fills while the first flush is still running, the second flush task is **queued** in the executor. The moment the first flush completes, the executor immediately picks up the second task. No waiting.

```
flushExecutor queue:
  [flush batch 1] → running (MySQL insert, 25 seconds)
  [flush batch 2] → waiting  ← filled during batch 1's insert
  
After batch 1 completes:
  [flush batch 2] → now running immediately (no idle gap)
  [flush batch 3] → waiting (being filled while batch 2 inserts)
```

The practical effect: instead of MySQL being busy 50% of the time (25s insert, 25s idle), it is busy nearly 100% of the time.

### The Trade-Off

Doubling the prefetch means up to `2 × BATCH_SIZE` messages are "in-flight" (unacked) in the consumer's memory at any time. For `BATCH_SIZE = 10,000`, that's 20,000 messages held in memory. Each message is a CSV line (~200–500 bytes), so ~4–10MB per consumer — negligible.

The risk: if the consumer crashes with 20,000 unacked messages instead of 10,000, RabbitMQ redelivers 20,000 rows on the next run. With the clean-data assumption (no `source_hash`), those rows would be inserted again. This is only a problem if: (a) the table was NOT truncated before re-running AND (b) you care about duplicate rows.

---

## 43. JVM Keepalive — Why Drain Mode Was Silently Exiting

### The Problem

`basicConsume` is **non-blocking**. It registers a callback with RabbitMQ's internal thread pool and returns immediately. The consumer thread that called `consume()` then exits:

```java
// In Main.java — what happens when no file is provided:
for (int i = 0; i < NUM_CONSUMERS; i++) {
    Thread t = new Thread(() -> consumer.consume());
    t.start();  // consumer.consume() returns in milliseconds
}

log.info("No file provided — consumers are draining the existing queue");
// main() returns here → JVM checks for remaining non-daemon threads → finds none → exits
```

After all 10 consumer threads call `consume()` and return, the JVM has no more user threads keeping it alive. It exits — closing all RabbitMQ connections and abandoning any messages that were in transit.

RabbitMQ logs this as `client unexpectedly closed TCP connection`, which is exactly what it was.

### Why the Producer Run Didn't Have This Problem

When the producer is running (`args.length > 0`), `main()` calls `producerThread.join()` — which blocks the main thread until the producer finishes. The main thread staying alive kept the JVM alive throughout the entire producer + consumer run. Drain mode (no producer) had no such anchor.

### The Fix

```java
} else {
    log.info("No file provided — consumers are draining the existing queue");
    Thread.currentThread().join();  // block main thread forever (until Ctrl+C)
}
```

`Thread.currentThread().join()` tells the current thread to wait for itself to finish — which never happens. The main thread blocks indefinitely, keeping the JVM alive while the consumers and their scheduler/executor threads do their work.

When you press Ctrl+C, the JVM receives `SIGINT`, the shutdown sequence begins, and all threads are cleanly terminated.

**Why not `Thread.sleep(Long.MAX_VALUE)`?** Both work. `join()` is semantically cleaner — "wait for this thread to die" rather than "sleep for 292 years". In practice there is no observable difference.

### The Non-Daemon Thread Subtlety

Java has two kinds of threads:
- **User threads** (non-daemon) — the JVM stays alive as long as any of these exist
- **Daemon threads** — the JVM can exit even if these are still running (e.g., GC thread)

`Executors.newSingleThreadScheduledExecutor()` and `Executors.newSingleThreadExecutor()` create **non-daemon** threads by default. So the scheduler and flushExecutor threads should technically keep the JVM alive even without the `join()`. In practice, the thread may not be created until the first task is submitted — if `consume()` returns before the first task fires (10 seconds for the scheduler), there is a window where no non-daemon threads exist. The `join()` on the main thread closes that window entirely, no matter what the executor threads do.

---

