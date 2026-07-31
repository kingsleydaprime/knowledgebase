# Persistence & Data Modeling

**Source:** merged from `record-id-generator-java/learning/04-database-mysql-flyway.md` and `direct-debit-sandbox-java/learning/04-data-storage-patterns.md`.

## HikariCP — connection pooling

Opening a new DB connection per operation is expensive. A pool keeps a set of reusable connections open:

```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:mysql://localhost:3306/itc_db");
config.setMaximumPoolSize(10);
HikariDataSource dataSource = new HikariDataSource(config);
Connection conn = dataSource.getConnection();   // borrowed from the pool, not opened fresh
```

Pool sizing rule: `maximumPoolSize` should comfortably exceed the number of concurrent consumers/threads doing DB work, with headroom for Flyway and startup overhead — otherwise threads block waiting for a connection (`waiting > 0` in HikariCP's pool stats is the signal).

## Flyway — versioned migrations

Flyway runs SQL scripts in order and tracks which have applied, so schema state is reproducible from source control instead of manual `CREATE TABLE` runs:

```sql
-- V1__create_tables.sql
CREATE TABLE transactions (
    id VARCHAR(12) NOT NULL PRIMARY KEY,
    amount DECIMAL(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Naming convention: `V{version}__{description}.sql`. `flyway.migrate()` runs pending migrations automatically at startup.

## Prepared statements — always

Never concatenate SQL strings — it's the canonical SQL injection vector. `PreparedStatement` parameterizes values instead:

```java
PreparedStatement stmt = conn.prepareStatement("INSERT INTO transactions (id, amount) VALUES (?, ?)");
stmt.setString(1, id);
stmt.setBigDecimal(2, amount);
```

## SQL quick reference

| Category | Purpose | Commands |
|---|---|---|
| DML | Read/change rows | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| DDL | Change structure | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` |
| TCL | Group operations | `COMMIT`, `ROLLBACK`, `BEGIN` |
| DCL | Permissions | `GRANT`, `REVOKE` |

```sql
SELECT currency, COUNT(*), SUM(amount) FROM transactions GROUP BY currency HAVING COUNT(*) > 1000;
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 50 OFFSET 100;  -- pagination
```

**`DELETE` vs `TRUNCATE`**: `DELETE FROM t` (no `WHERE`) removes rows one at a time, logging each — slow, but rollback-able inside a transaction. `TRUNCATE TABLE t` deallocates all data pages at once — near-instant, resets `AUTO_INCREMENT`, but not rollback-able in MySQL (auto-committed) and skips row-level triggers. Use `TRUNCATE` for a full development wipe; `DELETE` when you need specific rows or transactional safety.

| SQL type | Java type | Notes |
|---|---|---|
| `VARCHAR(n)` | `String` | Bounded text |
| `DECIMAL(18,2)` | `BigDecimal` | Exact decimal — always for money, see [[languages/01-java/01-language/01-fundamentals]] |
| `BIGINT` | `long` | Auto-increment IDs |
| `DATETIME`/`TIMESTAMP` | `LocalDateTime` | See the JDBC bridging note in [[languages/01-java/01-language/01-fundamentals]] |

## Primary key design — surrogate vs natural keys

A **surrogate key** carries no business meaning (a random generated ID) — stable and compact, but inserting the same source record twice under a new random ID isn't caught by the DB. A **natural key** uses a real business field — automatic deduplication, but business data can change or arrive dirty.

The resolution used in practice: keep a compact surrogate key as the primary key for internal identity, and add a separate business-key column (e.g. a content hash) with its own `UNIQUE` index purely for deduplication. Two different concerns, two different columns — see [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency]] for the full idempotency design this enables.

### The clustered index page-split problem

In InnoDB, **the primary key IS the table** — rows are physically stored in a B-tree ordered by PK value (a *clustered* index). A **random** PK (a `VARCHAR` filled with random digits, or a UUID v4) means every insert lands at a random tree position. When the target leaf page is full, InnoDB **splits** it into two half-full pages and updates the parent. At scale:

- Page splits happen on nearly every insert (random position ⇒ full pages constantly)
- The tree grows taller, so each insert traverses more levels
- The working set eventually exceeds the buffer pool → disk reads

Observed effect: batch throughput starts fast and degrades continuously as the table grows — not a code bug, a structural cost of random-key clustered indexes.

**Fix**: use a sequential `BIGINT AUTO_INCREMENT` as the clustered key (every insert appends to the right end of the tree — no splits), and move the random business ID to a secondary `UNIQUE` index. Secondary-index splits are far cheaper because a secondary index stores only the key plus a pointer, not the full row.

```sql
ALTER TABLE transactions
    MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT,          -- clustered key: sequential
    ADD COLUMN generated_id VARCHAR(12) NOT NULL,
    ADD UNIQUE INDEX ux_generated_id (generated_id);          -- business ID: secondary index
```

This is the same reasoning behind why **UUID v7** (time-ordered) is preferred over UUID v4 as a primary/indexed key at scale — see [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency]].

## In-memory storage: ConcurrentHashMap as a lightweight store

A plain `HashMap` is not safe under concurrent reads/writes — data corruption or crashes that only reproduce under production load. `ConcurrentHashMap` handles concurrent access internally:

```java
private final Map<String, SubscriptionRecord> subscriptions = new ConcurrentHashMap<>();
```

See [[languages/01-java/02-jvm-and-concurrency/02-concurrency]] for why this matters and what "thread-safe" actually guarantees.

### Composite keys

`ConcurrentHashMap` only takes one key type. To look up by two fields, glue them into one string key with a separator that can't appear in either field:

```java
provisions.put(merchantId + ":" + productId, record);
```

This simulates a multi-column primary key the way a real database would use one — a database uses a genuine composite key; a map needs a manufactured single key.

### Secondary indexes — O(1) lookup by a non-primary field

Looking up by the map's key is O(1). Looking up by any *other* field means scanning every value — O(n), catastrophic at scale:

```java
// O(n) — reads every record until it finds a match
subscriptions.values().stream().filter(s -> s.getReferenceNo().equals(ref)).findFirst();
```

A **secondary index** is a second map: key = the field you want to search by, value = the primary key. A lookup becomes a two-hop O(1):

```java
Map<String, String> referenceIndex = new ConcurrentHashMap<>();   // referenceNo → subscriptionId
String id = referenceIndex.get(referenceNo);   // hop 1
return subscriptions.get(id);                   // hop 2
```

This is exactly what a database index does internally (usually a B-tree mapping column value → row ID) — here it's done manually with a second map. Cost: one extra map in memory, and **every write must keep it in sync** — create adds to both maps, delete removes from both, or lookups silently return stale/null results. For a `Map<String, Set<String>>` one-to-many index, `computeIfAbsent(key, k -> ConcurrentHashMap.newKeySet())` atomically creates-then-inserts in one call.

### Separate create from update

A single `save(id, record)` method used for both create and update becomes a bug magnet once secondary indexes exist — create must populate the indexes, update must not touch them. Splitting into two explicitly named methods (`createSubscription` vs `updateSubscription`) makes the side effects self-documenting: **method names should reflect intent, not implementation.**

## Data normalization

Normalization means storing every fact in exactly one place, so a value only ever needs updating in one row when it changes.

- **1NF** — every field holds a single, indivisible value (no comma-packed lists in one column)
- **2NF** — every non-key field depends on the *entire* primary key, not part of it (only relevant for composite keys)
- **3NF** — every non-key field depends *directly* on the primary key, not transitively through another non-key field

**3NF violation example**: a `callbackUrl` stored on every individual subscription record, when the URL actually belongs to the merchant+product combination. The dependency chain is `subscriptionId → merchantId → callbackUrl` — `callbackUrl` reaches the key only *through* `merchantId`, so changing a merchant's URL means updating every one of their subscription rows.

**The fix — a provision pattern**: move `callbackUrl` (and other merchant-level config) to its own record keyed by `merchantId + productId`, registered once. Every subscription just references `merchantId`/`productId`; resolving the callback URL is one lookup at fire-time, and changing it touches one row, not every historical subscription.

### Deliberate denormalization

Normalization is a default, not a law. A `TransactionRecord` that duplicates `debitAccount`, `merchantId`, and `channel` from its parent `SubscriptionRecord` is a conscious 3NF violation, justified because:

- Transaction records are read far more often than subscriptions are written — duplicating avoids a join/second-lookup on every read
- For a financial audit trail, you *want* the transaction to freeze what the account details were **at the time**, not reflect a later edit to the subscription — denormalization here is actually the more correct behavior, not just a performance shortcut

| Approach | Write complexity | Read complexity | Risk |
|---|---|---|---|
| Normalized | Simple | Requires joins/lookups | None — one source of truth |
| Denormalized | Must update every copy on change | Single lookup, fast | Copies can drift out of sync |

Default to normalized; denormalize deliberately, where read performance or point-in-time correctness justifies it, and document why.

## Related
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — `ConcurrentHashMap`'s actual thread-safety guarantees
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — the business-key/surrogate-key split in full
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — what happens to these indexes under bulk load
