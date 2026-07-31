# Logging & Observability

**Source:** condensed from `record-id-generator-java/learning/09-logging-and-observability.md` — the original also includes a full log-reading walkthrough of a real pipeline run, worth reading directly for how to diagnose HikariCP pool stats and RabbitMQ management UI numbers in practice.

## SLF4J + Logback

Never use `System.out.println` for anything beyond throwaway debugging. SLF4J is the logging **interface**; Logback is the default **implementation**, configured via `logback.xml`:

```java
private static final Logger log = LoggerFactory.getLogger(FileProducer.class);
// or, via Lombok — see 03-lombok-and-builders.md
@Slf4j

log.info("Producer started: {}", filePath);   // {} placeholders — avoids string concat when the level is disabled
log.error("Save failed", exception);           // pass the Throwable directly — preserves the full stack trace
```

Levels, low to high severity: `TRACE → DEBUG → INFO → WARN → ERROR`.

### Facade vs implementation — why SLF4J exists

The single most important idea in Java logging: **SLF4J is a facade, not a logger.** Your code (and every library you depend on) compiles against the SLF4J API only; the actual logging backend is chosen at deploy time by which implementation is on the classpath. That decoupling is why a library can log without forcing its logging framework on you, and why you can swap backends without touching code.

| | Role | Notes |
|---|---|---|
| **SLF4J** | facade / API | what you write `log.info(...)` against |
| **Logback** | implementation | SLF4J's native backend, the common default; `logback.xml` config |
| **Log4j2** | implementation | high-throughput async logging (a lock-free ring buffer via the LMAX Disruptor); often chosen for performance-sensitive apps. Its predecessor Log4j 1.x is EOL — and Log4j2's *Log4Shell* (CVE-2021-44228) is the reason every Java shop now tracks logging-dependency versions closely |
| **tinylog** | implementation | a lightweight, minimal-dependency logger for small apps where Logback/Log4j2 are overkill |

Because everything targets the SLF4J facade, moving from Logback to Log4j2 (say, for async throughput) is a dependency swap, not a code change — the `log.info(...)` calls are identical.

## The log-table pattern

A **log table** stores processing errors in the database, alongside the data they belong to — distinct from application logs going to files/stdout, and worth applying to essentially any project that processes data (ETL pipelines, API servers, background jobs, file imports):

```sql
CREATE TABLE logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(10),
    source VARCHAR(100),         -- which class/service
    message TEXT,
    stack_trace TEXT,
    payload TEXT,                -- the raw input that failed — what makes replay possible
    correlation_id VARCHAR(100), -- trace one logical operation across services
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The `payload` column is the part that's easy to skip and expensive to have skipped — without the exact input that failed, debugging a production data-quality issue means trying to reconstruct what the bad row looked like from a stack trace alone.

## Metrics worth tracking on any data pipeline

**Throughput** — messages/rows per second, both per-batch and lifetime:

```java
double batchRate    = (batchSize - skipped) / (batchMs / 1000.0);
double lifetimeRate = totalProcessed / (elapsedMs / 1000.0);
```

**Gotcha — the lifetime rate is a measurement artifact, not a real slowdown indicator on its own.** `totalProcessed / elapsed` is a cumulative average from process start; early on it looks artificially fast because `elapsed` is still small, and it mathematically drags toward the long-run average over time even if every individual batch runs at an identical rate. Always log **both** numbers — if `batchRate` is flat but `lifetimeRate` looks like it's declining, that's the averaging math, not an actual regression. If both are declining together, that's real.

**Batch latency**, **duplicate rate** (rows skipped by an idempotency check — see [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency]]), and **queue depth** (via the broker's management API — a continuously growing depth means the consumer is falling behind the producer) round out the standard four signals for a queue-backed pipeline.

## From manual counters to production metrics

Manual `System.currentTimeMillis()` deltas and log lines work for development. In production, **Micrometer** is the SLF4J-equivalent facade for metrics — instrument once, ship to Prometheus/Datadog/CloudWatch/whatever backend without changing the instrumentation code:

```java
Counter processed = registry.counter("pipeline.messages.processed");
Timer batchLatency = registry.timer("pipeline.batch.latency");
processed.increment(batch.size());
batchLatency.record(() -> repository.saveBatch(batch));
```

This is what turns ad-hoc log-grepping into actual dashboards with latency percentiles (p50/p95/p99) and alerting.

## Related
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — what "duplicate rate" is measuring
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — the throughput numbers these metrics are diagnosing
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — queue depth and consumer capacity as observability signals
