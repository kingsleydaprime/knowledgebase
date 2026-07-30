# Record ID Generator — Docker & Performance Tuning

Split out from the original single-file `learning.md`. Covers Docker/docker-compose, streaming
vs chunking vs batch inserts, high-speed bulk ingestion (the `rewriteBatchedStatements=true`
driver gotcha, MySQL server tuning, the redo log bottleneck), and the load-then-index pattern.
See also `04-database-mysql-flyway.md` and `05-rabbitmq-messaging.md`.

---

## 15. Docker — Reproducible Environments

Docker packages your app and its dependencies (MySQL, RabbitMQ) into isolated containers. Same behavior on every machine.

### Key concepts
- **Image** — a blueprint (mysql:8, rabbitmq:management)
- **Container** — a running instance of an image
- **Volume** — persists data beyond container lifecycle
- **docker-compose** — orchestrates multiple containers

### Dev compose
```yaml
services:
  mysql:
    image: mysql:8
    ports:
      - "3306:3306"     # host:container
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: itc_db
      MYSQL_USER: itc
      MYSQL_PASSWORD: itc
    volumes:
      - mysql_data:/var/lib/mysql   # data survives container restarts

  rabbitmq:
    image: rabbitmq:management
    ports:
      - "5672:5672"     # AMQP protocol
      - "15672:15672"   # Management UI → http://localhost:15672

volumes:
  mysql_data:
```

```bash
docker compose -f docker-compose.dev.yml up -d    # start in background
docker compose -f docker-compose.dev.yml ps       # check status
docker compose -f docker-compose.dev.yml down     # stop
```

### Dockerfile (multi-stage build)
```dockerfile
# Stage 1: Build
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY . .
RUN ./gradlew build -x test  # -x test skips tests

# Stage 2: Run (smaller image, no JDK)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/app/build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

Multi-stage keeps your production image small — JRE only, no build tools.

---


---

## 26. Performance at Scale — Streaming vs Chunking vs Batch Inserts

When you're dealing with a 1.5GB file, three concepts come up. They solve different problems and are often confused.

---

### Streaming — Reading Without Loading

**Streaming** means processing data one piece at a time as it arrives, never holding the whole thing in memory.

`BufferedReader` in `FileProducer` is already doing this:

```java
BufferedReader reader = new BufferedReader(new FileReader(filePath));
String line;
while ((line = reader.readLine()) != null) {
    channel.basicPublish("", queueName, null, line.getBytes());
}
```

Each `readLine()` call fetches the next line from disk. Only one line is in memory at a time. The JVM's memory usage stays flat whether the file is 1MB or 10GB. **This is already solved in this project.**

`BufferedReader` internally reads a chunk (typically 8KB) from disk into a buffer, then hands you lines from that buffer one at a time — so you get streaming semantics with good disk I/O efficiency. You don't need to implement this yourself.

---

### Chunking — Processing in Groups

**Chunking** means deliberately collecting N items together before doing something with them. It's a throughput strategy, not a memory strategy.

Example: instead of publishing messages one at a time, you could collect 1000 lines and publish them together. This is useful when the per-item overhead (network round-trip, transaction cost) is expensive.

```java
// Streaming: publish every line immediately — N round-trips for N lines
channel.basicPublish("", queueName, null, line.getBytes());

// Chunked: accumulate, then publish as a batch — 1 round-trip per 1000 lines
List<String> chunk = new ArrayList<>();
chunk.add(line);
if (chunk.size() == 1000) {
    publishBatch(channel, chunk);  // one network operation
    chunk.clear();
}
```

---

### The Real Bottleneck — One INSERT Per Message

The file reading is fine. The problem is on the **consumer side**.

Currently:
- `basicQos(1)` — RabbitMQ sends only 1 message at a time to the consumer
- One `INSERT` per message — every single record is its own database round-trip

For a file with 500,000 rows, that's **500,000 individual SQL inserts**. Each one:
1. Borrows a connection from HikariCP
2. Sends the INSERT to MySQL over the network
3. MySQL writes it, flushes to disk, responds
4. Returns the connection to the pool

A single INSERT takes ~1–5ms. 500,000 × 2ms = **~17 minutes**. This is the actual bottleneck.

```
Current flow (slow):
Message 1 → INSERT → ack
Message 2 → INSERT → ack
Message 3 → INSERT → ack
... (500,000 times)

Batched flow (fast):
Message 1  ┐
Message 2  │
...        ├─→ single INSERT with 500 rows → ack all 500
Message 500┘
```

---

### The Fix — Batch Inserts

Batch inserts use a single `PreparedStatement` with multiple value rows, all in one transaction:

```sql
-- Instead of 500 separate INSERTs:
INSERT INTO transactions (id, amount, currency) VALUES (?, ?, ?);
INSERT INTO transactions (id, amount, currency) VALUES (?, ?, ?);
-- ... 498 more

-- One batch INSERT:
INSERT INTO transactions (id, amount, currency) VALUES
    (?, ?, ?),
    (?, ?, ?),
    (?, ?, ?);
-- ... all 500 in one statement
```

In Java, you use `addBatch()` and `executeBatch()`:

```java
try (Connection conn = DatabaseConfig.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql)) {

    conn.setAutoCommit(false);  // wrap everything in one transaction

    for (Transaction t : batch) {
        stmt.setString(1, t.getId());
        stmt.setBigDecimal(2, t.getAmount());
        stmt.setString(3, t.getCurrency());
        stmt.addBatch();        // stage the row, don't execute yet
    }

    stmt.executeBatch();        // send all rows to MySQL in one shot
    conn.commit();              // commit the whole batch
}
```

Two changes are required:
1. **`basicQos(500)`** — tell RabbitMQ to prefetch 500 messages so the consumer has a full batch to work with
2. **Accumulate in a `List<Transaction>`**, then flush when it reaches the batch size

Performance improvement is typically **50–100x** because:
- Network round-trips: 500 → 1
- Transaction overhead: 500 → 1
- MySQL buffer flushing: 500 → 1

---

### Tradeoff — Batch Failure Handling

With individual inserts, each record either succeeds or fails independently. With batch inserts, a single bad row can fail the whole batch.

Three strategies:

| Strategy | How | Tradeoff |
|---|---|---|
| **Fail fast** | Let `executeBatch()` throw, log the whole batch as failed | Simple, but re-running requires reprocessing the whole batch |
| **Retry individually** | On batch failure, retry each row one-by-one to isolate the bad one | Correct, but adds complexity |
| **Skip and log** | On batch failure, catch the error, log the raw payloads, continue | No data loss in the log, but bad rows are discarded |

This project already uses the "skip and log" pattern for individual rows — the same approach applies to batches. The `logs` table with `payload` column is exactly what you need: save the raw CSV line that failed so you can investigate and replay later.

---

### When to Use Each

| Technique | Solves | Use when |
|---|---|---|
| Streaming (`BufferedReader`) | Memory — file never fully loaded | Always, for large files |
| Chunking (collect N, process together) | Throughput — fewer round-trips | Network or transaction overhead is the bottleneck |
| Batch insert (`addBatch` / `executeBatch`) | DB throughput — one transaction for N rows | Writing many rows to a database |
| Increasing `basicQos` | Consumer throughput — prefetch more messages | Consumer is waiting idle between messages |

---


---

## 32. High-Speed Bulk Ingestion — Making It Run in Minutes

This section explains why a seemingly correct batch pipeline can still take hours, and exactly what to change to bring it down to minutes.

---

### The Driver Deception — Why Your Batch Was a Lie

This is the single most important thing in this entire document for performance.

When you call `stmt.executeBatch()` in Java, you expect the driver to send one large SQL statement like:

```sql
INSERT INTO transactions (id, amount) VALUES (?, ?), (?, ?), (?, ?), ...
```

Without a specific URL parameter, the MySQL JDBC driver **does not do this**. It silently breaks your batch back into individual statements:

```sql
INSERT INTO transactions (id, amount) VALUES (?, ?);
INSERT INTO transactions (id, amount) VALUES (?, ?);
INSERT INTO transactions (id, amount) VALUES (?, ?);
-- ... 999 more
```

Your `addBatch()` / `executeBatch()` code compiles and runs without errors. The logs show batches completing. But it is doing 1,000 individual inserts, not one batch. The fix is one parameter appended to the JDBC URL:

```properties
db.url=jdbc:mysql://localhost:3306/records_db?rewriteBatchedStatements=true
```

With this set, the driver rewrites your 1,000 staged rows into a single `INSERT ... VALUES (...), (...), (...)` payload. The difference is typically **10–50x faster** for the DB write phase alone. This is now set in `application.properties`.

---

### The Three Bottlenecks and Their Fixes

Every slow bulk pipeline has the same three problems:

| Bottleneck | Root cause | Fix |
|---|---|---|
| Network round-trips | One INSERT per row or small batches that aren't really batched | `rewriteBatchedStatements=true` + large batch size |
| Transaction overhead | MySQL commits and flushes to disk on every transaction | `innodb_flush_log_at_trx_commit=2` |
| Consumer backpressure | `basicQos` too low — consumer waits idle between deliveries | Raise prefetch count to match batch size |

---

### MySQL Server Tuning for Bulk Loads

These settings make MySQL stop being conservative about every write. They are safe for a bulk load scenario where you can re-run from the CSV if anything goes wrong.

#### Via Docker (configured in `docker-compose.dev.yml`)

The `command:` block passes arguments to the MySQL daemon at startup:

```yaml
mysql:
  image: mysql:8
  command: >
    --innodb-flush-log-at-trx-commit=2
    --innodb-buffer-pool-size=512M
    --max-allowed-packet=256M
    --innodb-log-buffer-size=64M
```

What each one does:

**`--innodb-flush-log-at-trx-commit=2`**
Controls when MySQL flushes the write-ahead log to disk.

| Value | Behaviour | Speed |
|---|---|---|
| `1` | Flush on every commit (default) | Slowest — safest |
| `2` | Write on every commit, flush once/second | Fast — safe for bulk load |
| `0` | Write and flush once/second | Fastest — can lose 1s of data on hard crash |

For a bulk load where you can replay the CSV, `2` gives you most of the speed benefit without the risk of `0`.

**`--innodb-buffer-pool-size=512M`**
The memory buffer InnoDB uses to cache data and indexes before writing to disk. Default is 128MB. Increasing it means MySQL can hold more of the table in memory during the load, reducing disk I/O. A good rule: set to 50–70% of available RAM if this machine is dedicated to MySQL.

**`--max-allowed-packet=256M`**
Maximum size of a single SQL statement. With `rewriteBatchedStatements=true` and a batch size of 5,000 rows × ~500 bytes/row, your INSERT statement can be ~2.5MB. The default 64MB limit is fine for batch sizes up to ~100,000 rows, but increasing it gives headroom.

**`--innodb-log-buffer-size=64M`**
The buffer MySQL uses to accumulate log writes before flushing. Larger = fewer disk flushes during the load.

#### Via SQL (if you need to tune a running instance)

If you can't restart MySQL (e.g., a shared server), run these before starting the load:

```sql
-- Flush logs once per second instead of per commit — biggest single speedup
SET GLOBAL innodb_flush_log_at_trx_commit = 2;

-- Disable constraint checking during the load
SET UNIQUE_CHECKS = 0;
SET FOREIGN_KEY_CHECKS = 0;

-- Increase query size limit
SET GLOBAL max_allowed_packet = 268435456;  -- 256MB
```

**After the load completes, restore safe defaults:**

```sql
SET GLOBAL innodb_flush_log_at_trx_commit = 1;
SET UNIQUE_CHECKS = 1;
SET FOREIGN_KEY_CHECKS = 1;
```

> `UNIQUE_CHECKS=0` tells MySQL to skip unique index validation during inserts. Only safe if your data is clean. We rely on `source_hash` to prevent duplicates at the application level — if you disable `UNIQUE_CHECKS`, MySQL won't catch duplicates. Re-enable before normal use.

---

### Optimal Batch Size

With `rewriteBatchedStatements=true`, larger batches are more efficient up to a point. The sweet spot for a single-machine bulk load:

| Batch size | Batches for 5M rows | Notes |
|---|---|---|
| 500 | 10,000 | Original — fine without rewrite, slow with it |
| 1,000 | 5,000 | Current setting — good |
| 5,000 | 1,000 | Recommended — fewer round-trips, manageable memory |
| 50,000 | 100 | Aggressive — ~50MB per batch in memory, fastest |

The current `BATCH_SIZE = 1000` in `FileConsumer` is already a good setting. To push further, increase it and also increase `basicQos` to match.

---

### Putting It All Together — The Complete Flow

With all optimisations in place:

```
1. FileProducer
   └─ BufferedReader streams 1 line at a time (flat memory usage)
   └─ basicPublish → record.queue

2. RabbitMQ delivers 1,000 messages at once (basicQos = BATCH_SIZE)

3. FileConsumer callback accumulates 1,000 Transaction objects

4. flushBatch() called:
   └─ setAutoCommit(false)
   └─ addBatch() × 1,000
   └─ executeBatch()
        └─ driver rewrites → single INSERT with 1,000 rows (rewriteBatchedStatements=true)
        └─ MySQL writes 1,000 rows in one transaction
        └─ innodb_flush_log_at_trx_commit=2 → no per-commit disk flush
   └─ commit()
   └─ basicAck(lastTag, multiple=true) → clears all 1,000 from queue in one call

5. logStats() → "Batch 1000 saved in 120ms | rate=8333/sec"
```

At 8,000 records/sec, 5 million rows = **~10 minutes**. With batch size 5,000 and MySQL tuning, you can reach 30,000–50,000 records/sec — bringing 5 million rows down to **under 3 minutes**.

---

### Quick Start — Running Everything from Scratch

```bash
# 1. Start MySQL and RabbitMQ
docker compose -f docker-compose.dev.yml up -d

# 2. Wait for MySQL to be ready (first startup takes ~20s)
docker compose -f docker-compose.dev.yml logs -f mysql
# Wait until you see: ready for connections

# 3. (Optional) Delete the old queue if it existed without DLQ args
curl -u guest:guest -X DELETE http://localhost:15672/api/queues/%2F/record.queue

# 4. Run the app
./gradlew run --args="/path/to/transactions.csv"
```

If MySQL was already running from a previous session with the old `itc_db` name:

```bash
# Recreate the containers so the new database name takes effect
docker compose -f docker-compose.dev.yml down -v   # -v removes the data volume
docker compose -f docker-compose.dev.yml up -d
```

> `-v` deletes the MySQL data volume. Only do this if you're OK losing existing data — which is fine during development since you can reload from the CSV.

---

### Direct Install (Ubuntu, no Docker)

If MySQL and RabbitMQ are installed directly on Ubuntu rather than via Docker:

**MySQL**

```bash
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql -u root -p

# In MySQL:
CREATE DATABASE records_db;
CREATE USER 'itc'@'localhost' IDENTIFIED BY 'itc';
GRANT ALL PRIVILEGES ON records_db.* TO 'itc'@'localhost';
FLUSH PRIVILEGES;

# Apply bulk load tuning (session-level, no restart needed)
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL max_allowed_packet = 268435456;
```

To make the tuning permanent without Docker, add to `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
[mysqld]
innodb_flush_log_at_trx_commit = 2
innodb_buffer_pool_size = 512M
max_allowed_packet = 256M
innodb_log_buffer_size = 64M
```

Then `sudo systemctl restart mysql`.

**RabbitMQ**

```bash
sudo apt install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management  # enable the web UI
```

The web UI will be at `http://localhost:15672` (guest / guest). No further config needed for this project.

---

## 33. INSERT IGNORE — Handling Duplicates Without Crashing the Batch

### The Problem With Regular INSERT

When a batch of 50,000 rows hits a single duplicate `source_hash`, the whole `executeBatch()` throws `SQLIntegrityConstraintViolationException`. The transaction rolls back. All 50,000 rows are discarded. The code falls back to 50,000 individual saves — one DB round-trip per row. That single duplicate just turned a fast batch into a slow loop.

This is what happened in the logs:
```
WARN  FileConsumer -- Batch insert failed, falling back to individual saves.
      Cause: Duplicate entry '0a77cf83...' for key 'transactions.ux_source_hash'
```

### INSERT IGNORE

`INSERT IGNORE` tells MySQL: if this row would violate a unique constraint, skip it silently and continue. No exception. No rollback. The rest of the batch succeeds.

```sql
-- Regular INSERT — one duplicate kills the whole batch
INSERT INTO transactions (id, source_hash, ...) VALUES (?, ?, ...);

-- INSERT IGNORE — duplicates are silently skipped, batch always succeeds
INSERT IGNORE INTO transactions (id, source_hash, ...) VALUES (?, ?, ...);
```

What MySQL does when it sees a duplicate with `INSERT IGNORE`:
1. Checks the unique indexes before inserting
2. If a conflict exists → skips the row, returns 0 rows affected for that row
3. Moves to the next row
4. No error, no rollback, no exception in Java

This is now the behaviour of `saveBatch()` in `TransactionRepository`. The `save()` method (used only in the individual fallback path) keeps regular `INSERT` so genuine errors still surface as exceptions.

### INSERT IGNORE vs ON DUPLICATE KEY UPDATE vs REPLACE

All three handle duplicates, but differently:

| Statement | On duplicate | Use when |
|---|---|---|
| `INSERT IGNORE` | Skip the row entirely | You want to keep existing data, duplicates are discarded |
| `ON DUPLICATE KEY UPDATE col = VALUES(col)` | Update the existing row | You want to overwrite existing data with new values |
| `REPLACE INTO` | Delete the old row, insert the new one | You want full replacement (dangerous — changes the PK) |

For this pipeline, `INSERT IGNORE` is correct: if the source transaction was already processed, we want to keep what's there and silently discard the new arrival.

### Counting What Was Skipped

`executeBatch()` returns an `int[]` — one entry per row in the batch. With `INSERT IGNORE`:
- `1` — row was inserted
- `0` — row was skipped (duplicate)
- `-2` (`Statement.SUCCESS_NO_INFO`) — driver can't tell (some JDBC implementations)

```java
int[] results = stmt.executeBatch();
conn.commit();

int inserted = 0;
for (int r : results) {
    if (r > 0) inserted += r;
}
int skipped = transactions.size() - inserted;
```

With MySQL Connector/J 8.x and `rewriteBatchedStatements=true`, MySQL returns 0 for ignored rows and 1 for inserted rows — so the count is accurate. If you ever see `SUCCESS_NO_INFO` (-2) values, it means the driver couldn't get per-row counts; the `skipped` count would then be overstated (showing the whole batch as skipped). This is a conservative failure mode — you'll see an inflated duplicate count in logs but nothing will be lost.

The stats log now shows both:
```
INFO  FileConsumer -- Batch 50000: inserted=49997 skipped=3 in 340ms | total=149991 rate=8333/sec dupes=3 errors=0
```

---

### Statement.SUCCESS_NO_INFO — When executeBatch() Lies

When you call `stmt.executeBatch()` you get back an `int[]` — one number per row, representing how many rows that statement affected. For a regular INSERT batch, you'd expect `1` per inserted row and `0` per ignored row.

With `rewriteBatchedStatements=true`, the MySQL driver rewrites your 50,000 individual staged rows into a single SQL statement: `INSERT IGNORE INTO ... VALUES (...), (...), ...`. That one statement produces one result from the database. The driver then has to fill in 50,000 positions in the `int[]` array without knowing which individual rows were affected. It fills them all with `Statement.SUCCESS_NO_INFO` (-2) — the JDBC standard value meaning "I don't know."

Our original counting code discarded -2 values:

```java
for (int r : results) {
    if (r > 0) inserted += r;  // -2 is not > 0, so it's ignored
}
// inserted stays 0, skipped = batch.size() = 50000
```

This is why the logs showed `inserted=0 skipped=50000` even when data WAS being inserted. The fix is `SELECT ROW_COUNT()` — a MySQL function that returns the number of rows actually affected by the last DML statement. It must be called on the same connection, before `commit()` and before any other statement:

```java
stmt.executeBatch();

// ROW_COUNT() returns actual rows inserted by INSERT IGNORE
// (ignored rows are not counted)
int actualInserted;
try (Statement s = conn.createStatement();
     ResultSet rs = s.executeQuery("SELECT ROW_COUNT()")) {
    rs.next();
    actualInserted = rs.getInt(1);
}

conn.commit();
return transactions.size() - actualInserted;  // accurate skipped count
```

`ROW_COUNT()` works because MySQL tracks the affected row count at the engine level, independent of what the JDBC driver reports. It is always accurate for INSERT IGNORE — returning the count of rows that passed the unique constraint check and were actually written.

---

### INSERT IGNORE Performance — Why Skipping Is Not Free

You might expect that skipping a row is instant — after all, nothing is being written. It is not. When MySQL encounters a row in an `INSERT IGNORE` statement, it must:

1. Hash the `source_hash` value
2. Walk the `ux_source_hash` B-tree index to check if that hash exists
3. Find a match → skip the row

Step 2 requires reading index pages from disk or the buffer pool. For a table with millions of rows, the index can be hundreds of megabytes. When the buffer pool is cold (process just started, Docker container restarted), those pages are not in memory — each lookup may require a disk read.

This is what the logs showed:
```
Batch 50000: inserted=0 skipped=50000 in 29417ms | total=0 rate=0/sec dupes=50000
Batch 50000: inserted=0 skipped=50000 in 42155ms | total=0 rate=0/sec dupes=100000
```

`inserted=0 skipped=50000` — every row was a duplicate. The database already had this data from a previous run. MySQL performed 50,000 unique index lookups and skipped every row. 29 seconds for 50,000 lookups = ~0.6ms per lookup — slow because the index pages were cold, getting even slower in the second batch as the buffer pool pressure increased.

**`INSERT IGNORE` is a safety net, not a shortcut.** It is essentially free on a first load (no conflicts → no extra work beyond normal inserts). On a re-run against existing data, it pays the full cost of checking every row against the unique index.

### The Development Workflow

During development you often want to reload the same CSV multiple times. The correct workflow is:

```bash
# Wipe the table — instant, no row-by-row deletion
docker exec -it $(docker compose -f docker-compose.dev.yml ps -q mysql) \
    mysql -u itc -pitc records_db -e "TRUNCATE TABLE transactions;"

# Then run the app again
./gradlew run --args="/path/to/transactions.csv"
```

`TRUNCATE` resets the table to empty in milliseconds regardless of how many rows it had. The next run inserts everything fresh — no duplicates, no index conflict checks, maximum speed.

`TRUNCATE` vs `DELETE FROM transactions`:
- `TRUNCATE` — deallocates the whole table's data pages at once, resets auto-increment. Instant.
- `DELETE FROM transactions` (no WHERE) — deletes row by row, logs each deletion, takes minutes on a large table.

Always use `TRUNCATE` for a full table wipe.

### When to TRUNCATE vs When to Let INSERT IGNORE Handle It

| Scenario | Action |
|---|---|
| Development: re-running the same CSV to test changes | `TRUNCATE TABLE transactions` then re-run |
| Production: recovering from a crash mid-file | Re-run as-is — `INSERT IGNORE` skips already-saved rows |
| Production: same file delivered again by the source | Re-run as-is — duplicates are skipped correctly |
| Production: intentional full reload of new data | `TRUNCATE TABLE transactions` then re-run |

---


---

## 35. The Load-Then-Index Pattern — Getting From Hours to Minutes

### Why the Rate Drops With Each Batch

```
Batch 1: 50,000 rows in 16s  → 2,221/sec
Batch 2: 50,000 rows in 21s  → 2,062/sec
Batch 3: 50,000 rows in 31s  → 1,772/sec
Batch 4: 50,000 rows in 64s  → 1,306/sec
Batch 5: 50,000 rows in 73s  → 1,080/sec
Batch 6: 50,000 rows in 58s  →   990/sec  ← still decelerating
```

The deceleration is caused by the `ux_source_hash` unique index. SHA-256 hashes are effectively random strings. Inserting random keys into a B-tree causes **page splits** — when a leaf page is full, MySQL has to split it into two pages, update the parent node, and write everything back. This happens constantly during random inserts.

Worse: as the index grows beyond the buffer pool size, MySQL starts reading index pages from disk. The `source_hash` index for 5.75M rows of `VARCHAR(64)` is roughly:
- 64 bytes per key × 5.75M rows = ~368MB raw data
- Plus B-tree node overhead (~50-100%): ~600-750MB total index size

With a 512MB buffer pool shared between data pages, index pages, and internal structures, the working set quickly overflows. Every overflow = a disk read for that page. At Docker I/O speeds, each page fault adds 5-50ms.

At 990 rows/sec with 5.45M rows remaining: **~1.5 hours**. Not minutes.

---

### The Solution — Load-Then-Index

Instead of maintaining the unique index row by row during inserts, drop it before loading and rebuild it after. MySQL rebuilds an index from scratch by **sorting all the keys and building the B-tree bottom-up** — a completely different algorithm that is 10-50x faster than inserting one key at a time into a live tree.

```
Per-row index maintenance (current):   each insert = B-tree traversal + possible page split
Bulk index build (rebuild after load):  sort all keys → build tree in one pass, no splits
```

**The workflow:**

```bash
# Step 1: Drop the unique index (keeps the column, removes the B-tree)
mysql -u itc -pitc records_db -e "ALTER TABLE transactions DROP INDEX ux_source_hash;"

# Step 2: Wipe existing data for a clean load
mysql -u itc -pitc records_db -e "TRUNCATE TABLE transactions;"

# Step 3: Run the load — INSERT IGNORE with no unique index is just INSERT
./gradlew run

# Step 4: After the app finishes, rebuild the index
# MySQL sorts all 5.75M source_hash values and builds the B-tree in one pass
mysql -u itc -pitc records_db -e "ALTER TABLE transactions ADD UNIQUE INDEX ux_source_hash (source_hash);"
```

Steps 1-3 run the same Java code unchanged — `INSERT IGNORE` with no unique index simply inserts every row (IGNORE has nothing to conflict against). The index rebuild in step 4 typically takes 1-3 minutes for 5-10M rows.

**Expected performance without the index:** 10,000-50,000 rows/sec. For 5.75M rows: **2-10 minutes**.

---

### Why Not Just Disable Unique Checks?

`SET UNIQUE_CHECKS=0` tells MySQL to skip uniqueness verification during inserts. It's faster than per-row checking, but it has a dangerous side effect: MySQL still adds keys to the unique index, just without checking for duplicates first. If two rows have the same `source_hash`, both keys end up in the index. You then have a unique index with duplicate values — a corrupt state that can cause subtle query bugs later.

`DROP INDEX` before loading and `ADD UNIQUE INDEX` after is safer: the index doesn't exist during the load, so there's nothing to corrupt. The rebuild at the end either succeeds (no duplicates in the data) or fails with a clear error (duplicate found).

---

### innodb_buffer_pool_size — Keep the Index in RAM

Even without the load-then-index pattern, increasing the buffer pool helps by keeping more index pages in memory. The `source_hash` index alone is ~600-750MB for 5.75M rows:

```yaml
# docker-compose.dev.yml
--innodb-buffer-pool-size=2G
```

With 2GB, the entire `source_hash` index fits in memory. Cache miss rate drops dramatically. The per-row B-tree traversal still happens, but it hits RAM instead of disk. Expected improvement: 3-5x (from ~1,000/sec to 3,000-5,000/sec). Still not minutes for 5.75M rows, but significantly better.

Apply with a container restart (no data loss):
```bash
docker compose -f docker-compose.dev.yml restart mysql
```

---

### Choosing Your Strategy

| Goal | Approach |
|---|---|
| Fastest possible first load | Drop index → load → rebuild index |
| Idempotent re-runs (recover from crash) | Keep index, use `INSERT IGNORE` |
| Development iteration (re-run same file often) | TRUNCATE → drop index → load → rebuild |
| Production nightly load (new data only) | Keep index, `INSERT IGNORE` skips processed rows |

For a one-time bulk load of a CSV file, the drop-then-rebuild pattern is always faster. The unique index exists to protect against re-run duplicates — during a controlled first load where you TRUNCATE'd first, that protection adds cost with no benefit.

---

### LOAD DATA LOCAL INFILE — The Fastest Bulk Path

For one-time file loads where RabbitMQ isn't required, MySQL's native bulk loader is 5–20× faster than JDBC batch inserts. It bypasses the normal insert engine entirely.

**Setup (both client and server must opt in):**

```properties
# application.properties — client side
db.url=jdbc:mysql://localhost:3306/new_db?rewriteBatchedStatements=true&allowMultiQueries=true&allowLoadLocalInfile=true
```

```yaml
# docker-compose.dev.yml — server side
mysql:
  command: >
    --innodb-flush-log-at-trx-commit=2
    --innodb-buffer-pool-size=2G
    --innodb-redo-log-capacity=2G
    --local-infile=1          # ← required — disabled by default in MySQL 8
```

If either side is missing, MySQL throws: `Loading local data is disabled; this must be enabled on both the client and server sides`.

**The three-step flow (implemented in `BulkLoader.java`):**

```
Step 1 — Pre-process (~44s for 5.75M rows):
  Stream CSV line by line
  For each row: generate ID, check HashSet<Long>, regenerate if collision
  Write "generated_id,original_csv_line" to a temp file

Step 2 — Load (~60-90s):
  DROP INDEX ux_generated_id         ← no per-row B-tree maintenance
  LOAD DATA LOCAL INFILE temp_file   ← MySQL reads directly from client disk
  SELECT ROW_COUNT()                 ← actual rows loaded
  CREATE UNIQUE INDEX ux_generated_id ← bulk sort + build in one pass

Step 3 — Cleanup:
  Files.deleteIfExists(tempFile)
```

```java
// The LOAD DATA statement via JDBC
String sql = """
        LOAD DATA LOCAL INFILE '%s'
        INTO TABLE transactions
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        (generated_id, payment_type_id, source_id, ...)
        """.formatted(tempFile.toAbsolutePath().toString().replace("\\", "/"));

try (Connection conn = DatabaseConfig.getConnection();
     Statement stmt = conn.createStatement()) {
    stmt.execute("ALTER TABLE transactions DROP INDEX ux_generated_id");
    stmt.execute(sql);
    // ROW_COUNT() gives actual rows loaded
    stmt.execute("CREATE UNIQUE INDEX ux_generated_id ON transactions(generated_id)");
}
```

**Run via the `--bulk` flag (separate from the RabbitMQ pipeline):**

```bash
./gradlew run --args="--bulk /path/to/transactions.csv"
```

**Measured performance on 5.75M rows / 1.5GB:**

| Phase | Time |
|---|---|
| Pre-processing (ID gen + temp file write) | ~44s |
| LOAD DATA LOCAL INFILE | ~60-90s |
| Index rebuild | ~60-90s |
| **Total** | **~7 minutes** |

Compared to ~13 minutes for the RabbitMQ pipeline. The 6-minute gap is RabbitMQ overhead — publishing 5.75M messages, receiving and parsing them in consumers, and the extra network round trips. The MySQL write phase itself is equally fast in both paths (index dropped, sequential inserts).

**`LOCAL` means the file comes from the client** (wherever Java is running), not the MySQL server. This works correctly even when MySQL is inside Docker — the file transfers from the host over the client connection.

---


---

## 36. MySQL Redo Log — The Hidden Write Bottleneck

### What the Redo Log Is

Every write in MySQL goes through the **redo log** (also called the write-ahead log or WAL) before it touches actual data files. This is how MySQL guarantees crash safety: if the process dies mid-write, MySQL replays the redo log on the next startup to restore consistency.

The redo log is a **circular buffer** on disk. Its size is fixed at startup. As writes come in, the log fills up. A background process called the **checkpoint thread** continuously flushes dirty pages from the buffer pool to the actual data files and recycles the used log space.

```
Your INSERT → redo log (fast sequential write) → checkpoint → data files (random writes)
             ↑                                                          ↓
             └─────────────── log space recycled ──────────────────────┘
```

### What Happens When It Fills Up

```
[Warning] [MY-014089] [InnoDB] Redo log writer is waiting for a new redo log file.
Consider increasing innodb_redo_log_capacity.
The current log capacity is 104857600 bytes.
The log capacity used is 104857600 bytes.
```

`104857600 bytes = 100MB` — the default. `capacity used = 100%` — completely full.

When the redo log is full, MySQL's write path **blocks entirely**. No new data can be written until the checkpoint thread flushes enough dirty pages to free log space. This is a hard pause — your `executeBatch()` call sits waiting inside MySQL with no error, no timeout, just silence.

This is exactly what caused the 60-100 second batch times. Not the unique index. Not Docker overhead. The redo log was full, MySQL was blocked, and the batch waited until the checkpoint thread freed space. The one 8-second batch happened to run right after a checkpoint completed, when the log was mostly empty.

### How to Fix It

Increase `innodb_redo_log_capacity`. For bulk loading millions of rows, 100MB is far too small:

In `docker-compose.dev.yml`:
```yaml
command: >
  --innodb-flush-log-at-trx-commit=2
  --innodb-buffer-pool-size=512M
  --innodb-redo-log-capacity=2G
  --innodb-log-buffer-size=256M
```

This change requires a MySQL restart (not a volume wipe — data is preserved):
```bash
docker compose -f docker-compose.dev.yml restart mysql
```

Also increased `innodb-log-buffer-size` from 64M to 256M. The log buffer is the in-memory staging area before redo log entries are written to disk. A larger buffer means fewer writes to disk during heavy batch activity.

### Sizing the Redo Log

The redo log must be large enough to hold all the writes that can accumulate between checkpoints. For a bulk load:

| Scenario | Recommended capacity |
|---|---|
| Small datasets (< 1M rows, dev) | 512M |
| Medium datasets (1M–10M rows) | 2G |
| Large datasets (10M+ rows) | 4G–8G |
| Production (sustained write load) | 4G–16G |

A general rule: the redo log should be large enough that checkpoints happen every few minutes, not every few seconds. If you see the `waiting for a new redo log file` warning, double the size and try again.

### innodb_log_buffer_size

The log buffer is MySQL's in-memory write buffer before entries hit the redo log on disk. Default is 16MB–64MB. For a bulk load producing large transactions (50,000 rows per commit), a large log buffer means the entire transaction can stage in memory before a single disk write — then flush once at commit time.

Increasing from 64M to 256M means each batch of 50,000 rows accumulates in memory and hits the redo log in one sequential write, instead of multiple smaller writes that cause more seeking.

### The Complete Picture of a Write

When you call `executeBatch()` and then `commit()`, here is what MySQL actually does:

```
1. executeBatch()
   ├─ Parse the 20MB INSERT IGNORE statement
   ├─ For each row: check unique index in buffer pool (or disk if cold)
   └─ Stage row changes in log buffer (memory)

2. commit()
   ├─ Flush log buffer → redo log file on disk (sequential write)
   │    (blocked here if redo log is full — the 100-second pause)
   ├─ Mark transaction committed in redo log
   └─ Return to Java

3. Background checkpoint thread (async)
   ├─ Reads dirty pages from buffer pool
   ├─ Writes them to .ibd data files (random writes — slow)
   └─ Frees redo log space
```

`innodb_flush_log_at_trx_commit=2` means step 2 writes to the OS page cache (not physical disk) and the OS flushes it once per second. This is why it's faster than the default (`=1` which syncs to physical disk on every commit) — but it means up to 1 second of data could be lost if the machine loses power.

---

