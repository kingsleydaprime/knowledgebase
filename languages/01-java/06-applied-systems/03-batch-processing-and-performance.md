# Batch Processing & Performance

**Source:** `record-id-generator-java/learning/08-csv-parsing-and-data-quality.md` and the streaming/bulk-load sections of `10-docker-and-performance-tuning.md`.

## Streaming — processing without loading

**Streaming** means processing one piece of data at a time, never holding the whole input in memory:

```java
BufferedReader reader = new BufferedReader(new FileReader(filePath));
String line;
while ((line = reader.readLine()) != null) {
    channel.basicPublish("", queueName, null, line.getBytes());
}
```

`BufferedReader` internally reads ~8KB chunks from disk into a buffer and hands lines out one at a time — JVM memory usage stays flat whether the file is 1MB or 100GB. This is a memory strategy, not a throughput strategy — it says nothing about how fast processing is, only that it won't run out of heap.

## The quoted-comma CSV bug

Naive CSV parsing (`line.replace("\"", "").split(",")`) silently breaks the moment any field legitimately contains a comma (a name like `"Smith, John"`, an address, a narration):

```
"Smith, John"  →  after replace("\"","")  →  Smith, John  →  split(",") sees TWO fields, not one
```

Every field after the broken one shifts index by one — an amount field silently receives a currency code, and `new BigDecimal("GHS")` throws deep inside the pipeline, far from the actual cause. A real CSV parser tracks quote state instead of blindly splitting on every comma:

```java
private String[] splitCsv(String line) {
    List<String> fields = new ArrayList<>();
    StringBuilder current = new StringBuilder();
    boolean inQuotes = false;
    for (char c : line.toCharArray()) {
        if (c == '"') inQuotes = !inQuotes;
        else if (c == ',' && !inQuotes) { fields.add(current.toString().trim()); current.setLength(0); }
        else current.append(c);
    }
    fields.add(current.toString().trim());
    return fields.toArray(new String[0]);
}
```

Rule of thumb: any time `split(",")` appears on real-world CSV data, ask whether any field can contain a comma — if the answer is yes (names, addresses, free text almost always can), the naive split will break silently on exactly those rows.

## Chunking and batch inserts

**Chunking** — deliberately collecting N items before acting on them — is a throughput strategy, distinct from streaming's memory strategy. The two combine: stream the file, chunk into batches, batch-insert each chunk.

One `INSERT` per row means one full network round-trip + transaction + disk flush per row — for 500,000 rows at ~2ms each, that's roughly 17 minutes, and it's the real bottleneck in most naive pipelines, not file I/O.

```java
conn.setAutoCommit(false);
for (Transaction t : batch) {
    stmt.setString(1, t.getId());
    stmt.addBatch();      // stage the row, don't execute yet
}
stmt.executeBatch();      // send every staged row in one round-trip
conn.commit();
```

Typical improvement: **50-100x**, because network round-trips, transaction overhead, and buffer flushing all collapse from N to 1.

### The driver rewrite gotcha

`addBatch()`/`executeBatch()` compiling and running without error does **not** mean the driver actually sent one combined SQL statement. Without an explicit URL flag, the MySQL JDBC driver silently rewrites a "batch" back into N individual INSERT statements — logs show batches completing, throughput is still terrible, and nothing in the Java code looks wrong:

```properties
db.url=jdbc:mysql://localhost:3306/db?rewriteBatchedStatements=true
```

With this flag, staged rows genuinely combine into one `INSERT ... VALUES (...), (...), (...)` statement — typically another **10-50x** on top of the batching change itself. This single connection-string parameter is one of the highest-leverage, easiest-to-miss performance fixes in JDBC bulk loading.

## MySQL server tuning for bulk loads

```yaml
# docker-compose.dev.yml
mysql:
  command: >
    --innodb-flush-log-at-trx-commit=2
    --innodb-buffer-pool-size=2G
    --innodb-redo-log-capacity=2G
    --max-allowed-packet=256M
```

| Setting | What it does |
|---|---|
| `innodb_flush_log_at_trx_commit=2` | Write to OS page cache on every commit, physically flush once/sec (default `1` flushes to disk every commit — much safer, much slower). Acceptable risk for a bulk load that can be replayed from source. |
| `innodb_buffer_pool_size` | In-memory cache for data + index pages. Undersized relative to the working index means constant disk reads on every lookup. |
| `innodb_redo_log_capacity` | The write-ahead log's fixed size. Too small under sustained heavy writes and MySQL's write path **blocks entirely** until the checkpoint thread frees space — a silent, unexplained multi-second-to-minute pause with no error, easily misdiagnosed as "the database is just slow." |
| `max_allowed_packet` | Ceiling on a single SQL statement's size — matters once batched INSERT statements grow large. |

## The load-then-index pattern

A unique index on a near-random key (a content hash, a UUID) degrades write throughput progressively as the table grows: every insert triggers a B-tree lookup against that index, and once the index exceeds the buffer pool, lookups start hitting disk. Observed symptom: batch throughput starts fast and decelerates continuously, not because of a code bug but because of the structural cost of maintaining a random-key index under growing data (see the clustered-index page-split discussion in [[languages/01-java/04-persistence/01-jdbc-and-data-modeling]] for the same root cause on a primary key specifically).

**Fix**: drop the index before a bulk load, load with no per-row index maintenance at all, then rebuild it once at the end. MySQL rebuilds an index by sorting all keys and building the B-tree bottom-up in one pass — a fundamentally different, far cheaper algorithm than maintaining a live tree one random insertion at a time.

```sql
ALTER TABLE transactions DROP INDEX ux_source_hash;
-- run the load — INSERT IGNORE with no index simply inserts everything
ALTER TABLE transactions ADD UNIQUE INDEX ux_source_hash (source_hash);   -- bulk rebuild, 10-50x faster than per-row maintenance
```

Not the same as `SET UNIQUE_CHECKS=0`, which skips validation but still writes to the index — if duplicates exist, they silently corrupt the index (two identical keys inside a supposedly-unique structure). Dropping the index entirely means there's nothing to corrupt; the rebuild step either succeeds cleanly or fails loudly on a genuine duplicate.

For one-time file loads where a message queue isn't otherwise required, MySQL's native `LOAD DATA LOCAL INFILE` bypasses the normal per-row insert engine entirely and is typically 5-20x faster again than JDBC batch inserts — the fastest available bulk-ingestion path, at the cost of needing both client and server to explicitly opt in (`allowLoadLocalInfile=true` client-side, `--local-infile=1` server-side, both disabled by default in MySQL 8).

## Choosing a strategy

| Goal | Approach |
|---|---|
| Fastest possible one-time bulk load | Drop index → load → rebuild index |
| Idempotent re-runs / crash recovery in production | Keep the index, rely on `INSERT IGNORE` |
| Iterating locally on the same file repeatedly | `TRUNCATE` → drop index → load → rebuild |
| Steady-state production loads of genuinely new data | Keep the index — `INSERT IGNORE` cost is near-zero when there's nothing to conflict with |

## Related
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|Persistence & Data Modeling]] — why random keys degrade B-tree indexes in the first place
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — the business-key design this bulk-load pattern is built around
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability]] — how to actually see a pipeline's throughput while it runs
