# Record ID Generator — Database: MySQL, HikariCP & Flyway

Split out from the original single-file `learning.md`. Covers connection pooling, migrations,
prepared statements, the SQL reference for this project's tables, and primary-key design
(surrogate vs natural keys, the clustered-index page-split problem, and diagnosing PK
collisions). See also `05-rabbitmq-messaging.md` and `07-id-generation-and-idempotency.md`.

---

## 8. Database — MySQL + HikariCP + Flyway

### HikariCP — Connection Pooling

Opening a new DB connection every time is expensive. HikariCP maintains a **pool** of reusable connections.

```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:mysql://localhost:3306/itc_db");
config.setUsername("itc");
config.setPassword("itc");
config.setMaximumPoolSize(10); // max 10 concurrent connections

HikariDataSource dataSource = new HikariDataSource(config);

// Get a connection from the pool
Connection conn = dataSource.getConnection();
```

### Flyway — Database Migrations

Flyway runs SQL scripts automatically in order, tracking which ones have run. Never worry about manually creating tables again.

File: `resources/db/migration/V1__create_tables.sql`

```sql
CREATE TABLE transactions (
    id VARCHAR(12) NOT NULL PRIMARY KEY,
    payment_type_id VARCHAR(50),
    amount DECIMAL(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Naming convention: `V{version}__{description}.sql`

```java
Flyway flyway = Flyway.configure()
    .dataSource(url, user, password)
    .locations("classpath:db/migration")
    .load();
flyway.migrate(); // runs pending migrations on startup
```

### Prepared Statements

Never concatenate SQL strings — SQL injection risk. Always use `PreparedStatement`:

```java
String sql = "INSERT INTO transactions (id, amount) VALUES (?, ?)";
PreparedStatement stmt = conn.prepareStatement(sql);
stmt.setString(1, transaction.getId());
stmt.setBigDecimal(2, transaction.getAmount());
stmt.executeUpdate();
```

---


---

## 25. SQL — The Language of Databases

SQL (Structured Query Language) is how you communicate with a relational database. Every query falls into one of four categories:

| Category | Purpose | Commands |
|---|---|---|
| **DML** — Data Manipulation | Read and change rows | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| **DDL** — Data Definition | Create and change structure | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` |
| **TCL** — Transaction Control | Group operations | `COMMIT`, `ROLLBACK`, `BEGIN` |
| **DCL** — Data Control | Permissions | `GRANT`, `REVOKE` |

---

### SELECT — Reading Data

```sql
-- Every column
SELECT * FROM transactions;

-- Specific columns
SELECT id, amount, currency, source_date_created
FROM transactions;

-- With a condition
SELECT * FROM transactions
WHERE currency = 'GHS';

-- Multiple conditions
SELECT * FROM transactions
WHERE currency = 'GHS'
  AND amount > 100.00;

-- Pattern match (% = any characters, _ = one character)
SELECT * FROM transactions
WHERE accountname LIKE 'JOHN%';

-- Sort results
SELECT * FROM transactions
ORDER BY amount DESC;           -- highest first
ORDER BY source_date_created ASC;  -- oldest first

-- Limit rows returned
SELECT * FROM transactions
LIMIT 100;

-- Skip the first N rows (useful for pagination)
SELECT * FROM transactions
ORDER BY created_at DESC
LIMIT 50 OFFSET 100;  -- rows 101–150
```

---

### Aggregate Functions — Summary Queries

```sql
-- Count all rows
SELECT COUNT(*) FROM transactions;

-- Count non-null values in a column
SELECT COUNT(merchant_id) FROM transactions;

-- Sum, average, min, max
SELECT
    SUM(amount)   AS total_amount,
    AVG(amount)   AS avg_amount,
    MIN(amount)   AS min_amount,
    MAX(amount)   AS max_amount
FROM transactions;

-- Group results by a column
SELECT currency, COUNT(*), SUM(amount)
FROM transactions
GROUP BY currency;

-- Filter groups (HAVING is WHERE for aggregated results)
SELECT processor, COUNT(*) AS total
FROM transactions
GROUP BY processor
HAVING COUNT(*) > 1000;
```

---

### INSERT — Adding Rows

```sql
-- Insert one row
INSERT INTO transactions (id, payment_type_id, amount, currency)
VALUES ('123456789012', 'MOMO', 34.10, 'GHS');

-- Insert multiple rows at once
INSERT INTO transactions (id, payment_type_id, amount, currency)
VALUES
    ('000000000001', 'CARD', 50.00, 'GHS'),
    ('000000000002', 'MOMO', 20.00, 'USD');
```

---

### UPDATE — Changing Existing Rows

```sql
-- Update specific rows
UPDATE transactions
SET processor = 'MTN_NEW'
WHERE processor = 'MTN';

-- Update multiple columns
UPDATE transactions
SET currency = 'GHS',
    country  = 'Ghana'
WHERE country = 'GH';
```

**Always include a WHERE clause.** Without it, every row in the table is updated.

---

### DELETE vs TRUNCATE — Removing Rows

This is the one you just used:

```sql
-- DELETE removes specific rows (or all rows with no WHERE)
DELETE FROM transactions WHERE year = 2023;

-- DELETE with no condition — removes all rows, slowly (row by row, logs each one)
DELETE FROM transactions;

-- TRUNCATE — removes ALL rows instantly
TRUNCATE TABLE transactions;
```

| | `DELETE` (no WHERE) | `TRUNCATE` |
|---|---|---|
| Speed | Slow — deletes row by row | Fast — deallocates all pages at once |
| Can be rolled back | Yes (inside a transaction) | No (in MySQL, it's auto-committed) |
| Resets AUTO_INCREMENT | No | Yes |
| Triggers | Fires row-level triggers | Does not fire triggers |
| WHERE clause | Yes | No |

Use `TRUNCATE` when you want to wipe a table clean and start fresh (e.g., re-running a data load during development). Use `DELETE` when you want to remove specific rows, or when you need rollback safety.

---

### DROP — Removing Structure

```sql
-- Remove the table entirely (structure + all data)
DROP TABLE transactions;

-- Remove only if it exists (safe to run even if table doesn't exist)
DROP TABLE IF EXISTS transactions;
```

`TRUNCATE` keeps the table, `DROP` destroys it. After a `DROP`, the table is gone and must be recreated (via Flyway migration in this project).

---

### Useful Queries for This Project's Tables

```sql
-- How many transactions were loaded?
SELECT COUNT(*) FROM transactions;

-- Total amount processed, by currency
SELECT currency, COUNT(*) AS count, SUM(amount) AS total
FROM transactions
GROUP BY currency
ORDER BY total DESC;

-- Transactions by processor
SELECT processor, COUNT(*) AS count
FROM transactions
GROUP BY processor
ORDER BY count DESC;

-- Transactions by year and month
SELECT year, month, COUNT(*) AS count, SUM(amount) AS total
FROM transactions
GROUP BY year, month
ORDER BY year, month;

-- Find any duplicate source_trans_id (data quality check)
SELECT source_trans_id, COUNT(*) AS occurrences
FROM transactions
GROUP BY source_trans_id
HAVING COUNT(*) > 1;

-- Check recent errors in the log table
SELECT level, source, message, payload, created_at
FROM logs
ORDER BY created_at DESC
LIMIT 20;

-- Count errors by source
SELECT source, COUNT(*) AS error_count
FROM logs
WHERE level = 'ERROR'
GROUP BY source;

-- Wipe transactions to re-run a load (development only)
TRUNCATE TABLE transactions;
```

---

### SQL Data Types Used in This Project

| SQL Type | Java Type | Use case |
|---|---|---|
| `VARCHAR(n)` | `String` | Text with a max length |
| `TEXT` | `String` | Long text (no length limit) |
| `DECIMAL(18,2)` | `BigDecimal` | Exact decimal — always for money |
| `INT` | `int` | Whole numbers |
| `BIGINT` | `long` | Large whole numbers (auto-increment IDs) |
| `DATETIME` | `LocalDateTime` | Date and time, no timezone |
| `TIMESTAMP` | `Timestamp` / `LocalDateTime` | Date + time, auto-set by DB |

`DECIMAL(18,2)` means: up to 18 total digits, 2 after the decimal point. Same precision guarantee as `BigDecimal` — this is why both are used together for money.

---


---

## 30. Primary Key Design — Generated ID vs Separate Concerns

This is a fundamental database design question: should your primary key carry business meaning, or should it be a pure internal identifier?

### Surrogate Key (what we have)

A **surrogate key** has no business meaning — it exists only as a database row identifier.

```sql
id VARCHAR(12) NOT NULL PRIMARY KEY  -- "483920174651" — meaningless outside this DB
```

Pros:
- Stable — never changes even if the business data changes
- Compact — 12 chars
- Fast — string comparisons on a short fixed-width column

Cons:
- Nothing stops you from inserting the same source transaction twice with different IDs
- Losing idempotency — re-running the pipeline creates duplicates

### Natural Key

A **natural key** uses a field from the business data as the PK.

```sql
source_trans_id VARCHAR(100) NOT NULL PRIMARY KEY
```

Pros:
- Automatic deduplication — re-running is safe
- Meaningful — you can join across systems using a shared identifier

Cons:
- Business data changes — what if `source_trans_id` gets corrected in the source system?
- May be null or non-unique at the source (data quality issues)
- Long strings are slower in B-tree indexes

### The Right Split for This Project

Keep the generated ID as PK. Add `source_hash` as a secondary `UNIQUE` constraint. Two separate concerns:

| Column | Type | Purpose |
|---|---|---|
| `id` VARCHAR(12) | Surrogate key | Internal DB row identifier |
| `source_hash` VARCHAR(64) | Business key | Deduplication, idempotency |

```sql
-- Updated schema
CREATE TABLE transactions (
    id          VARCHAR(12)  NOT NULL PRIMARY KEY,
    source_hash VARCHAR(64)  NOT NULL,
    ...
    UNIQUE INDEX ux_source_hash (source_hash)
);
```

This way:
- The PK stays stable and compact
- Re-running the pipeline skips already-processed rows (hash collision)
- You can query by either — `WHERE id = ?` for internal lookups, `WHERE source_hash = ?` for deduplication checks

The generated ID is fine as a PK. The problem it *doesn't* solve (idempotency) is what `source_hash` solves.

### The Clustered Index Problem — Why a Random VARCHAR PK Gets Slower Over Time

In InnoDB (MySQL's storage engine), the **primary key IS the table**. Rows are physically stored inside the B-tree, ordered by the PK value. This is called a **clustered index**.

When the PK is random (e.g. `VARCHAR(12)` filled with random digits), every new row has to be inserted at a random position in the tree. When the target leaf page is full, InnoDB splits it into two half-full pages and updates the parent — this is a **page split**. As the table grows:

- Page splits happen constantly (random inserts always find full pages)
- The tree gets taller → more levels to traverse per insert
- The working set grows beyond the buffer pool → disk reads

Observed impact: batch throughput starts fast and degrades with every batch until the pipeline takes hours instead of minutes.

### The Fix — V3 Migration: BIGINT AUTO_INCREMENT Clustered Key

Swap the PK to a sequential `BIGINT AUTO_INCREMENT`. Every new row appends to the right end of the tree — no splits, no random positioning. The random business ID moves to a separate `generated_id` column with a secondary unique index.

```sql
-- V3__optimize_pk.sql
ALTER TABLE transactions
    DROP INDEX ux_source_hash,
    DROP COLUMN source_hash,
    MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT,   -- sequential, no B-tree splits
    ADD COLUMN generated_id VARCHAR(12) NOT NULL DEFAULT '' AFTER id,
    ADD UNIQUE INDEX ux_generated_id (generated_id);   -- secondary index on random values
```

Updated schema:

| Column | Type | Role |
|---|---|---|
| `id` | `BIGINT AUTO_INCREMENT` | Clustered key — sequential, no page splits |
| `generated_id` | `VARCHAR(12) UNIQUE` | Business ID — random, in a secondary index |

**Why secondary index splits are less severe**: a secondary index only stores the key + a pointer to the row. The pages are smaller. Splits still happen (random values), but they don't involve moving actual row data. The main improvement is eliminating clustered index splits, which are far more expensive.

In Java, `id` is never set — MySQL handles it. Only `generated_id` is set from `IdGeneratorService`:

```java
// Before (random varchar was the PK)
transaction.setId(idGenerator.generate());

// After (random string is a business key, db handles the real PK)
transaction.setGeneratedId(idGenerator.generate());
```

**Important:** V3 requires an empty `transactions` table. Drop the Docker volume and restart before loading so all three migrations run on clean tables:

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
```

---


---

## 38. Removing source_hash for Clean Data

### What Changed and Why

Section 27 explains the `source_hash` system: a SHA-256 fingerprint stored as a `UNIQUE` column so that re-running the same CSV file doesn't insert duplicates. That system was built assuming the source data might be dirty or that the pipeline might need to be re-run safely.

When the data is **known to be clean** — one controlled load with no risk of re-running — the hash becomes pure overhead:

- SHA-256 is computed on every row before insert (CPU cost)
- The value is written to `source_hash VARCHAR(64)` (storage cost)
- MySQL checks the `ux_source_hash` unique index on every insert (the biggest cost — see Section 35 on why index maintenance slows down with scale)

We suspended the hash to measure raw insert throughput on clean data.

### What Changed in FileConsumer.java

```java
// Before — hash computed and stored on every row
transaction.setSourceHash(computeHash(transaction));
transaction.setId(idGenerator.generate());

// After — hash computation commented out
// transaction.setSourceHash(computeHash(transaction));
transaction.setId(idGenerator.generate());
```

**Import that was previously used by `computeHash`:**
```java
import java.security.MessageDigest;      // SHA-256 engine
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets; // for .getBytes(StandardCharsets.UTF_8)
import java.util.HexFormat;              // converts byte[] to hex string
```
These stay in the file because `computeHash` is still there (just not called), but if the method were removed they could be cleaned up.

### What Changed in TransactionRepository.java

`source_hash` was removed from all three INSERT statements and `setParams` was re-numbered:

```java
// Before — source_hash was column 2, everything else shifted by one
INSERT INTO transactions (
    id, source_hash, payment_type_id, ...
) VALUES (?, ?, ?, ...)
stmt.setString(2, t.getSourceHash());
stmt.setString(3, t.getPaymentTypeId());

// After — source_hash removed, 24 columns instead of 25
INSERT INTO transactions (
    id, payment_type_id, ...
) VALUES (?, ?, ...)
stmt.setString(2, t.getPaymentTypeId());
```

The `source_hash` column still exists in the database schema — it just receives `NULL` values. No migration needed. Flyway's V2 migration that created the column and index is unchanged; the index is still there, it just has no data in it.

### Performance Impact

Removing one `UNIQUE VARCHAR(64)` index from a table means:
- Every insert no longer triggers a B-tree lookup + possible page split on that index
- The `ux_source_hash` index stays empty, so those B-tree pages stay small and cold (irrelevant)
- MySQL only needs to maintain the primary key index (`id VARCHAR(12)`)

This is a meaningful speedup when inserting millions of rows. The tradeoff: if you re-run the same file, every row inserts again — duplicates in the database.

### When to Bring It Back

Re-enable both the hash computation and the `source_hash` column insert when:
- The pipeline needs to be idempotent (re-runs are safe)
- Source data might contain duplicates that should be silently skipped
- You are in production and cannot afford to re-examine every row manually

For development load-testing with known-clean CSVs, suspending it is the right call.

---

## 39. PK Collision — Find the Specific Row, Not the Whole Batch

### The Original Problem

When a bulk INSERT fails with a primary key collision (MySQL error 1062), the previous fallback strategy was:

```
Batch of 10,000 fails → retry every row one by one (10,000 individual inserts)
```

One collision penalises 9,999 innocent rows with individual round-trips. That batch becomes 50–100x slower than a normal batch flush.

### The New Strategy — Parse the MySQL Error Message

MySQL's 1062 error message always includes the duplicate key value:

```
Duplicate entry '047382910564' for key 'PRIMARY'
```

We extract that value with a regex, find the one transaction in the batch whose ID matches, regenerate just that ID, and retry the whole batch:

```java
// In flushBatch() — the retry loop
for (int attempt = 0; attempt <= maxPkRetries; attempt++) {
    try {
        skipped = transactionRepository.saveBatch(batch);
        break;  // success
    } catch (SQLException e) {
        if (e.getErrorCode() == 1062 && attempt < maxPkRetries) {
            String dupId = parseDuplicateId(e.getMessage());
            if (dupId == null) throw e;
            batch.stream()
                 .filter(t -> dupId.equals(t.getId()))
                 .findFirst()
                 .ifPresent(t -> {
                     log.warn("PK collision on id={}, retry {}/{}", dupId, currentAttempt + 1, maxPkRetries);
                     t.setId(idGenerator.generate());
                 });
        } else if (isRetriable(e)) {
            // deadlock/lock timeout → individual fallback (different problem)
            skipped = fallbackToIndividual(batch, batchLines, deliveryTags, channel);
            break;
        } else {
            throw e;
        }
    }
}

// Helper — extracts the colliding value from MySQL's error message
private String parseDuplicateId(String message) {
    if (message == null) return null;
    java.util.regex.Matcher m = java.util.regex.Pattern
            .compile("Duplicate entry '(.+?)' for key 'PRIMARY'")
            .matcher(message);
    return m.find() ? m.group(1) : null;
}
```

**Imports used:**
```java
import java.util.regex.Matcher;   // not needed — we used the fully-qualified name inline
import java.util.regex.Pattern;   // same — Pattern.compile() called inline
```

We used fully-qualified names (`java.util.regex.Pattern`) inside the method to avoid adding imports for a one-off helper. Either way is fine.

### The Lambda Effectively-Final Problem

Java requires variables used inside lambdas to be **effectively final** — their value cannot change after the lambda is written. `attempt` is a loop variable that changes every iteration, so it can't be used directly inside `ifPresent`:

```java
// Compile error — attempt is not effectively final
.ifPresent(t -> log.warn("retry {}", attempt + 1, maxPkRetries));

// Fix — capture the current value in a new final variable
final int currentAttempt = attempt;
.ifPresent(t -> log.warn("retry {}", currentAttempt + 1, maxPkRetries));
```

`currentAttempt` is assigned once and never changes, so Java accepts it inside the lambda. This is a very common pattern whenever you need a loop variable inside a lambda.

### Why Three Lists Instead of a Map

The batch is stored as three parallel lists (`batch`, `batchLines`, `deliveryTags`), not as a list of objects that bundle all three together. Index `i` in all three always refers to the same original message.

The stream search (`batch.stream().filter(t -> dupId.equals(t.getId()))`) only searches the `batch` list. Once found, the transaction object's ID is mutated in place — the corresponding entry in `batchLines` and `deliveryTags` is unaffected, because those don't store the ID. The lists stay in sync with no extra bookkeeping.

---

