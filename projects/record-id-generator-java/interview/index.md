# record-id-generator-java — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). This is the strongest project in the vault for **backend/data
engineering** interviews — it's a real high-throughput ingestion pipeline with measured performance
work, a message broker, and a database that fought back.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked. 🔥🔥 = build your whole prep around it.

## Files

| File | Covers |
|---|---|
| [01-java-and-architecture.md](01-java-and-architecture.md) | Java fundamentals in context, Gradle, layering, try-with-resources, `BigDecimal`, CSV parsing |
| [02-rabbitmq-and-concurrency.md](02-rabbitmq-and-concurrency.md) | Producer/consumer threads, prefetch vs batch size, backpressure, DLQ, graceful shutdown |
| [03-mysql-performance-and-ids.md](03-mysql-performance-and-ids.md) | Batch inserts, the driver deception, load-then-index, redo log, clustered index, ID design, idempotency |
| [04-operations-and-story.md](04-operations-and-story.md) | Docker, logging/observability, reading the logs, trade-offs, behavioural |

---

## Before anything else: the 60-second pitch

> A Java bulk-ingestion pipeline: it streams a large CSV, publishes each row onto RabbitMQ, and a
> pool of consumers assigns each record a unique 12-digit ID and batch-inserts it into MySQL —
> around 5.75 million rows. Most of the interesting work was performance. The naive version was
> hours; getting it to minutes came from three things: turning on `rewriteBatchedStatements` (the
> MySQL JDBC driver silently un-batches your batch without it, so my "batch insert" was 1,000
> individual inserts and the code looked completely correct), loading before indexing rather than
> maintaining a unique index during the load, and sizing the InnoDB redo log so the write path
> stopped stalling. The ID design has a real collision analysis behind it — birthday-paradox maths
> says about 16 collisions across 5.75M rows, which a bounded retry absorbs.

The driver-deception line is the single best thing you own for a backend interview. It's a real,
non-obvious, measurable bug that produced no error at all.

---

## Numbers worth memorising

| Thing | Value |
|---|---|
| Rows loaded | ~5.75M |
| ID space | 12 decimal digits = 10¹² |
| Expected collisions at 5.75M rows | ≈ 16 (`n²/2k`) |
| 50%-collision-per-insert threshold | ≈ √10¹² = 1M rows |
| `BATCH_SIZE` / `basicQos` prefetch | 500 |
| `rewriteBatchedStatements=true` gain | ~10–50× on the write phase |

Interviewers trust specifics. Vague "it got much faster" reads as someone repeating a blog post.
