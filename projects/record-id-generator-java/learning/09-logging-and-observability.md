# Record ID Generator — Logging & Observability

Split out from the original single-file `learning.md`. Covers SLF4J/Logback, the `logs` database
table pattern, throughput/latency/duplicate-rate/queue-depth metrics, and reading the RabbitMQ
management UI and pipeline logs during a run. See also `05-rabbitmq-messaging.md`.

---

## 13. Logging — SLF4J + Logback

Never use `System.out.println` in production. Use a proper logging framework.

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FileProducer {
    private static final Logger log = LoggerFactory.getLogger(FileProducer.class);

    public void produce(String filePath) {
        log.info("Producer started: {}", filePath);
        log.debug("Debug detail here");
        log.warn("Something suspicious");
        log.error("Something failed", exception);
    }
}
```

Log levels (low → high): `TRACE → DEBUG → INFO → WARN → ERROR`

SLF4J is the interface. Logback is the implementation. They're configured via `logback.xml` in resources.

---

## 14. Log Tables — A Standard You Should Always Apply

A **log table** in your database captures processing errors alongside the data they belong to. This is separate from application logs (which go to files/stdout).

```sql
CREATE TABLE logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(10),          -- ERROR, WARN, INFO
    source VARCHAR(100),        -- which class/service
    message TEXT,               -- what happened
    stack_trace TEXT,           -- full Java stack trace
    payload TEXT,               -- the raw data that failed
    correlation_id VARCHAR(100),-- trace across services
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Why a log table?
- **Reprocessing** — you have the exact payload that failed; replay it later
- **Auditing** — prove what happened and when
- **Debugging** — stack traces stored permanently, not lost when the app restarts
- **Reporting** — query error rates, patterns, affected records

Apply this to every project that processes data: ETL pipelines, API servers, background jobs, file imports.

---


---

## 29. Observability — Measuring What's Happening

Running a pipeline and waiting until it finishes is flying blind. Observability means instrumenting your code to answer: *is it working, how fast, and where is it breaking?*

### Four Key Metrics for This Pipeline

#### 1. Messages per second (throughput)

How fast is the producer publishing, and how fast is the consumer processing?

```java
// Simple counter — increment on every message processed
private long messagesProcessed = 0;
private long startTime = System.currentTimeMillis();

// In the callback, after successful save:
messagesProcessed++;
if (messagesProcessed % 10_000 == 0) {
    long elapsed = System.currentTimeMillis() - startTime;
    double rate = messagesProcessed / (elapsed / 1000.0);
    log.info("Processed {} records at {}/sec", messagesProcessed, String.format("%.0f", rate));
}
```

**The lifetime rate is a lie (measurement artifact).** `totalProcessed / elapsed` is a cumulative average from the moment the app started. Early batches look fast because `elapsed` is small. As time grows, the number drags toward the true long-term average even if every batch runs at identical speed — creating a perception of slowing that is partly just math.

Always log **both** per-batch rate and lifetime rate:

```java
private void logStats(int batchSize, int skipped, long batchMs) {
    long elapsed = System.currentTimeMillis() - startTime;
    double batchRate    = batchMs > 0 ? (batchSize - skipped) / (batchMs / 1000.0) : 0;
    double lifetimeRate = totalProcessed / (elapsed / 1000.0);
    log.info("Batch {}: inserted={} skipped={} in {}ms | batch={}/s lifetime={}/s total={} dupes={} errors={}",
            batchSize, batchSize - skipped, skipped, batchMs,
            String.format("%.0f", batchRate), String.format("%.0f", lifetimeRate),
            totalProcessed, totalDuplicates, totalErrors);
}
```

`batchRate` tells you actual instantaneous throughput. `lifetimeRate` tells you overall progress. If `batchRate` is stable but `lifetimeRate` looks like it's declining, that's the math artifact — not a real slowdown.

#### 2. Batch insert latency

How long does each `executeBatch()` take? Spikes indicate DB pressure.

```java
long start = System.currentTimeMillis();
stmt.executeBatch();
conn.commit();
long latencyMs = System.currentTimeMillis() - start;
log.info("Batch of {} inserted in {}ms", transactions.size(), latencyMs);
```

#### 3. Duplicate rate

If you've added `source_hash` (Section 27), count how many inserts were skipped as duplicates:

```java
private long duplicatesSkipped = 0;

// In the catch block for hash duplicates:
duplicatesSkipped++;
if (duplicatesSkipped % 1000 == 0) {
    log.warn("Duplicate rate: {} skipped so far", duplicatesSkipped);
}
```

High duplicate rate = the source file has duplicate records, or you're reprocessing already-loaded data.

#### 4. Queue depth

How many messages are waiting in RabbitMQ? If depth grows continuously, the consumer is slower than the producer.

```java
// Check queue depth via the AMQP channel
long depth = channel.messageCount(RabbitMQConfig.getQueueName());
log.info("Queue depth: {}", depth);
```

Or via the RabbitMQ Management API at `http://localhost:15672` (guest/guest by default) — the management UI shows queue depth, publish rate, and consumer rate in real time.

### Reading the RabbitMQ Management UI

The management UI is the fastest way to diagnose whether the pipeline is running, stalled, or broken. Here is what each number means and what to look for.

**Connections tab** — shows every TCP connection from your app to RabbitMQ:

| Column | What to check |
|---|---|
| State | Should be `running`. `blocked` means RabbitMQ's memory alarm is active. |
| Channels | How many AMQP channels are open on this connection. 0 means the channel was closed after use (e.g. the setup channel). |
| To client (B/s) | Data flowing FROM RabbitMQ TO your app. `2 B/s` = heartbeat only, no message delivery. If consumers are registered but this is low, RabbitMQ is not dispatching messages. |
| From client (B/s) | Data flowing FROM your app TO RabbitMQ. Heartbeats + acks. |

During a healthy load: **To client** should be KB/s or MB/s per consumer connection as messages stream in.

**Queues and Streams → record.queue** — the single most useful page:

| Field | Meaning |
|---|---|
| Ready | Messages waiting to be delivered to a consumer |
| Unacked | Messages delivered but not yet acked (currently being processed) |
| Consumers | Number of registered consumers. Should match `NUM_CONSUMERS`. |
| Consumer capacity | 100% = consumers are fully utilising their prefetch quota. Low % = consumers are idle. |
| State | `idle` = queue has consumers but is currently empty. `running` = messages flowing. |
| Deliver (manual ack) rate | Messages/sec being sent to consumers. 0.00/s with non-zero Ready = consumers are not receiving. |

**What specific states mean:**

```
Ready=98337, Unacked=0, Consumers=0
→ No consumers connected. App is not running or failed before basicConsume.

Ready=98337, Unacked=0, Consumers=10
→ Consumers ARE registered but not receiving. RabbitMQ is connected but not dispatching.
  Check the "To client" B/s on the Connections tab — if it's 2 B/s (heartbeat only),
  the issue is server-side (queue state, flow control, or a silent channel error).

Ready=0, Unacked=2000, Consumers=10
→ Healthy: all Ready messages delivered, consumers are processing them.

Ready=0, Unacked=0, Consumers=10, State=idle
→ Queue is empty. Processing is complete (or producer hasn't published yet).
```

### For Production — Micrometer + Prometheus

The manual counter approach above works for development. In production, use **Micrometer** — a metrics facade (like SLF4J, but for metrics) that sends data to Prometheus, Datadog, CloudWatch, or any other backend.

```java
// Add to build.gradle.kts
implementation("io.micrometer:micrometer-core:1.13.0")
implementation("io.micrometer:micrometer-registry-prometheus:1.13.0")

// Instrument your code
MeterRegistry registry = new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
Counter processed = registry.counter("pipeline.messages.processed");
Timer batchLatency = registry.timer("pipeline.batch.latency");

// In the consumer:
processed.increment(batch.size());
batchLatency.record(() -> transactionRepository.saveBatch(batch));
```

Prometheus scrapes the metrics endpoint every 15s. Grafana visualises them. You get dashboards showing throughput, latency percentiles (p50, p95, p99), and error rates over time — without any manual logging.

---


---

## 34. Reading Pipeline Logs — What Everything Means

Understanding what the logs are telling you is as important as writing the code. Here is a full walkthrough of a real run, line by line.

### Startup Phase

```
09:58:20.557 [main] DEBUG FlywayExecutor -- Memory usage: 19 of 252M
```
Flyway is scanning for migration files. `main` thread = the app hasn't started its producer/consumer threads yet.

```
09:58:20.914 [main] DEBUG DbMigrate -- Successfully completed migration of schema `records_db` to version "1 - create tables"
09:58:21.627 [main] DEBUG DbMigrate -- Successfully completed migration of schema `records_db` to version "2 - add source hash"
09:58:21.761 [main] INFO  DbMigrate -- Successfully applied 2 migrations to schema `records_db` (execution time 00:01.516s)
```
Both SQL migration files ran. Tables exist. App is ready to start.

### Producer and Consumer Threads Starting

```
09:58:21.782 [Thread-1] INFO  FileProducer -- Producer started for file: .../transactions.csv
```
Producer thread (`Thread-1`) started. It is now reading the CSV line by line and publishing to RabbitMQ.

```
09:58:21.826 [Thread-0] DEBUG ConsumerWorkService -- Creating executor service with 4 thread(s) for consumer work service
```
Consumer thread (`Thread-0`) registered its callback with RabbitMQ. RabbitMQ's internal thread pool (4 threads) will call the `DeliverCallback` as messages arrive. The consumer itself is now idle — waiting for messages.

### HikariCP Pool Initializing

```
09:58:27.628 [pool-1-thread-3] DEBUG HikariConfig -- jdbcUrl: jdbc:mysql://localhost:3306/records_db?rewriteBatchedStatements=true
09:58:27.719 [pool-1-thread-3] INFO  HikariDataSource -- HikariPool-1 - Starting...
09:58:27.847 [pool-1-thread-3] INFO  HikariPool -- HikariPool-1 - Added connection ...
```
HikariCP doesn't connect to MySQL at startup — it waits until the first query is needed (lazy initialization). This triggered 6 seconds after start, which means the first batch of 50,000 messages had accumulated in memory and was ready to flush. Watch the pool log sequence:

```
total=1, active=1   → first connection added and immediately used (batch insert starting)
total=2, active=1   → pool growing to minimum size (10)
total=3, active=1
...
total=10, active=1  → pool full, one connection still active (insert in progress)
```

### The Failure

```
09:58:48.168 [pool-1-thread-3] WARN  FileConsumer -- Batch insert failed, falling back to individual saves.
             Cause: Duplicate entry '0a77cf837768060d...' for key 'transactions.ux_source_hash'
```
Timestamp: 26 seconds after start. That means it took 26 seconds to accumulate 50,000 messages from RabbitMQ and attempt the batch insert.

**What went wrong:** the batch of 50,000 rows contained at least one row whose `source_hash` already existed in the database (or appeared twice in the CSV). `executeBatch()` threw `SQLIntegrityConstraintViolationException`. The `catch` block caught it, logged this WARN, and started the fallback loop — 50,000 individual `saveWithRetry` calls.

**How to spot this pattern:** any time you see `Batch insert failed, falling back to individual saves`, you are about to do N individual inserts instead of 1 batch. This will always be slow.

**The fix (now applied):** `INSERT IGNORE INTO` in `saveBatch()`. The duplicate is silently skipped, the batch succeeds, this WARN never appears again.

### The Fallback Running

```
09:58:57.986 [HikariPool-1 housekeeper] DEBUG -- Pool stats (total=10, active=0, idle=10, waiting=0)
```
`active=0` — all connections are idle. The individual fallback for all 50,000 rows **completed** in about 9 seconds (09:58:48 to 09:58:57). That's ~5,500 rows/sec on individual inserts — not terrible, but far slower than a proper batch.

```
09:59:57.987 [HikariPool-1 housekeeper] -- Pool stats (total=10, active=1, idle=9, waiting=0)
```
One minute later, `active=1` again — the second batch of 50,000 is being inserted. If this stays `active=1` for many minutes without a `logStats` line appearing, the second batch is also failing and doing the individual fallback.

### Reading HikariPool Stats

The housekeeper logs pool stats every 30 seconds:

```
Pool stats (total=10, active=1, idle=9, waiting=0)
```

| Field | Meaning | What to watch for |
|---|---|---|
| `total` | Connections in the pool | Should reach `maximumPoolSize` (10) during load |
| `active` | Connections currently executing a query | `active=0` means nothing is running |
| `idle` | Connections open but not in use | `idle=10` means the pipeline has stalled |
| `waiting` | Threads waiting for a connection | `waiting > 0` means pool is too small |

**Healthy bulk load**: `active=1` sustained for the duration of each batch insert, alternating with brief `active=0` between batches.

**Stalled pipeline**: `active=0` for many minutes with no `logStats` output — the consumer has stopped processing. Check for an exception above in the logs.

**Pool exhausted**: `waiting > 0` — increase `maximumPoolSize` in `DatabaseConfig` or reduce concurrency.

### The Producer Count Bug

```
INFO  FileProducer -- Producer finished. Total records published: 0
```

This is not an error — the producer DID publish records. The count variable was declared but never incremented:

```java
long count = 0;
while ((line = reader.readLine()) != null) {
    channel.basicPublish(...);
    // count++ was missing here
}
log.info("Total records published: {}", count);  // always 0
```

The consumer receiving messages proves the producer worked. The log was just wrong. The fix (`count++` inside the loop) is now in `FileProducer.java`. This is a common silent bug — the code compiles and runs correctly, only the metric is wrong.

---

### The "All Skipped" Pattern

```
Batch 50000: inserted=0 skipped=50000 in 29417ms | total=0 rate=0/sec dupes=50000 errors=0
Batch 50000: inserted=0 skipped=50000 in 42155ms | total=0 rate=0/sec dupes=100000 errors=0
```

**What it means:** every single row in every batch is a duplicate. The database already contains all of this data from a previous run. `INSERT IGNORE` is doing its job — no wrong data is entering the DB — but it is expensive because MySQL checks the unique index for each of the 50,000 rows before deciding to skip.

**Why it's getting slower:** the second batch (42,155ms) took longer than the first (29,417ms). As more index pages are loaded into the buffer pool by the first batch's lookups, memory pressure increases and older pages are evicted. The buffer pool (512MB) is not large enough to hold the entire index warm, causing increasing cache misses.

**How to fix:** `TRUNCATE TABLE transactions` and run again. The table is empty, there are no duplicates to find, every row inserts cleanly and fast.

**How to distinguish from a stuck pipeline:** a stuck pipeline shows `active=1` in HikariPool stats but never produces a log line. The "all skipped" pattern produces log lines regularly — it IS making progress, just through an expensive path.

### Re-run vs Fresh Load — Why Performance Is So Different

```
Batch 50000: inserted=0 skipped=50000 in 104839ms   ← re-run: 100+ seconds
Batch 50000: inserted=50000 skipped=0 in 1200ms     ← fresh load: 1-2 seconds
```

On a **fresh load** (table was TRUNCATE'd before running), performance is fast because:
- The unique index (`ux_source_hash`) is empty or nearly empty
- Each INSERT adds a new B-tree leaf — leaf pages are mostly in the buffer pool and mostly sequential
- No conflict checks needed — MySQL confirms the key doesn't exist with a single B-tree traversal that always ends at an empty slot

On a **re-run** against an existing table, every row in every batch requires:
1. A full B-tree traversal of `ux_source_hash` to find the existing key
2. The index for 5M rows of VARCHAR(64) is ~320MB — larger than what fits in the buffer pool hot path
3. Cold index pages = disk reads = 5–50ms per cache miss
4. With 50,000 rows per batch, even 2ms average per lookup = 100 seconds

This is not a code bug — it is the fundamental cost of checking uniqueness against an existing dataset. The only way to avoid it is to not check (`TRUNCATE` first) or to not have the index during the load (drop it, load, recreate).

**Rule of thumb**: if you are re-running purely to test performance, always `TRUNCATE TABLE transactions` first. A fresh-load benchmark is the only meaningful one.

---

### What Good Logs Look Like

After the `INSERT IGNORE` fix, every batch should produce one stats line and no WARN:

```
INFO  FileProducer -- Producer started for file: .../transactions.csv
INFO  HikariDataSource -- HikariPool-1 - Start completed.
INFO  FileConsumer -- Batch 50000: inserted=50000 skipped=0 in 340ms | total=50000 rate=8333/sec dupes=0 errors=0
INFO  FileConsumer -- Batch 50000: inserted=49997 skipped=3 in 312ms | total=99997 rate=8547/sec dupes=3 errors=0
INFO  FileConsumer -- Batch 50000: inserted=50000 skipped=0 in 298ms | total=149997 rate=8721/sec dupes=3 errors=0
...
INFO  FileProducer -- Producer finished. Total records published: 5000000
```

If you see `WARN Batch insert failed` — `INSERT IGNORE` is not in the SQL. If `logStats` stops appearing and `active=1` is sustained indefinitely — the batch is hanging (check for a lock or an extremely slow query). If `rate` is under 1,000/sec — `rewriteBatchedStatements=true` is not in the JDBC URL.

---

