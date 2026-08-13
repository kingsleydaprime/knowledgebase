# Record ID Generator — ID Generation & Idempotency

Split out from the original single-file `learning.md`. Covers generating unique 12-digit IDs,
collision math, alternative ID strategies (UUID v4/v7, Snowflake, ULID, hash-based), and making
the pipeline idempotent via a `source_hash` column. See also `04-database-mysql-flyway.md`.

---

## 11. Generating Unique 12-Digit IDs

Requirements: numeric only (0–9), 12 digits, no hyphens, unique.

```java
import java.security.SecureRandom;

public class IdGeneratorService {
    private static final String DIGITS = "0123456789";
    private static final int LENGTH = 12;
    private final SecureRandom random = new SecureRandom();

    public String generate() {
        StringBuilder sb = new StringBuilder(LENGTH);
        for (int i = 0; i < LENGTH; i++) {
            sb.append(DIGITS.charAt(random.nextInt(DIGITS.length())));
        }
        return sb.toString();
    }
}
```

`SecureRandom` vs `Random`: `SecureRandom` is cryptographically strong — better for IDs that need to be unpredictable.

### Collision handling

10^12 = 1 trillion possible IDs. Collisions are rare but possible (birthday problem). Handle at DB level:

```sql
id VARCHAR(12) NOT NULL PRIMARY KEY  -- unique constraint
```

```java
// On SQLIntegrityConstraintViolationException, retry up to 3 times
int attempts = 0;
while (attempts < 3) {
    try {
        transaction.setId(idGenerator.generate());
        transactionRepository.save(transaction);
        return;
    } catch (SQLIntegrityConstraintViolationException e) {
        attempts++;
    }
}
```

### Exact Collision Probability — The Birthday Paradox Math

With 12 random decimal digits (k = 10^12 possible values) and n records, the expected number of collisions across the whole dataset is:

```
Expected collisions ≈ n² / (2k)
```

For 5.75M rows:
```
(5,750,000)² / (2 × 1,000,000,000,000) ≈ 16 collisions
```

So across a 5.75M row load you expect roughly **16 rows** to hit a collision — the retry loop fires 16 times and regenerates 16 IDs. Essentially zero impact on performance or correctness.

The 1-in-2-million threshold (where each new insert has a ~50% chance of colliding) is reached at roughly √(10^12) = **1 million rows**. Before that, collisions are extremely rare. After it, they become more frequent but still manageable with a retry limit of 3.

### In-Memory Dedup for Bulk Loads (No DB Round-Trip)

When the unique index is dropped during a bulk load (for speed — see Section 35), the DB can no longer catch collisions. Instead, track used IDs in a Java set before they ever reach the DB:

**HashSet\<Long\> (single-threaded, e.g. BulkLoader)**
```java
Set<Long> usedIds = new HashSet<>(8_000_000); // pre-sized
String id = idGenerator.generate();
while (!usedIds.add(Long.parseLong(id))) {    // add() returns false if already present
    id = idGenerator.generate();
}
// id is now guaranteed unique within this load
```

**ConcurrentHashMap.newKeySet() (shared across threads)**

When multiple consumer threads each generate IDs independently, they can collide with each other — not just with the DB. A thread-safe shared set prevents cross-thread duplicates:

```java
// In Main.java — created once, passed to all consumers
Set<Long> usedIds = ConcurrentHashMap.newKeySet(8_000_000);

// In FileConsumer — shared across all 10 consumers
private String generateUniqueId() {
    String id = idGenerator.generate();
    while (!usedIds.add(Long.parseLong(id))) {
        id = idGenerator.generate();
    }
    return id;
}
```

### Memory Cost and Alternatives

Storing 5.75M longs in a `ConcurrentHashMap` costs roughly **250–300MB** (boxed `Long` ≈ 48 bytes per entry including node overhead). For larger files this grows linearly:

| File size | ConcurrentHashMap | Bloom filter |
|---|---|---|
| 5.75M rows | ~300MB | ~6MB |
| 50M rows | ~2.4GB | ~60MB |
| 500M rows | OutOfMemoryError | ~600MB |

**Bloom filter** (Guava): probabilistic, uses 50× less memory. Can have false positives (says "seen" when it hasn't — causes an unnecessary regeneration) but never false negatives (never misses an actual collision). For ID dedup, false positives are harmless — you just generate another ID.

```java
// build.gradle.kts: implementation("com.google.guava:guava:33.0.0-jre")
BloomFilter<Long> seen = BloomFilter.create(
    Funnels.longFunnel(), 50_000_000, 0.001); // 50M entries, 0.1% false positive rate
```

**Post-load dedup check**: no in-memory tracking at all. Load everything (index dropped), then find collisions with SQL after:
```sql
SELECT generated_id, COUNT(*) FROM transactions
GROUP BY generated_id HAVING COUNT(*) > 1;
```
Update those ~16 rows with fresh IDs, then create the unique index. Memory cost: zero during load.

---


---

## 26. ID Design — Is Random Enough, and Better Strategies

### Is the current 12-digit random ID sufficient?

Yes — but understanding *why* matters.

`SecureRandom` produces 10¹² (1 trillion) possible values. The danger is the **birthday problem**: collisions become likely when you've inserted roughly √(10¹²) = **1 million rows**. At that point, each new insert has about a 1-in-2-million chance of colliding. The retry mechanism handles this. For a 1.5GB file with a few million rows, you'll see at most a handful of retries across the whole run.

The current implementation is *safe*. The question is whether you can do *better*.

---

### The Timestamp + Random Hybrid

Your instinct is right — mixing time with randomness is a well-established pattern. The key is which part of the timestamp you use.

**Bad**: last 5 digits of Unix milliseconds
```
Unix ms ≈ 1748000000000
Last 5 digits: 00000–99999
Cycles every: 100,000 ms = 100 seconds
```
Two IDs generated 100 seconds apart could have the same prefix. Useless.

**Good**: date prefix — `YYYYMMDD` (8 digits) + 4 random

```java
// 8-digit date prefix + 4-digit random suffix = 12 digits total
// Example: 202406020387

String datePrefix = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd")); // "20240602"
String randomSuffix = String.format("%04d", random.nextInt(10000));                  // "0387"
String id = datePrefix + randomSuffix;                                                // "202406020387"
```

Benefits:
- IDs sort chronologically — queries like `WHERE id BETWEEN '20240601...' AND '20240630...'` work naturally
- The random part only needs uniqueness within a single day (10,000 values per date prefix)
- You can tell at a glance when a record was created from its ID alone

**Warning**: with only 4 random digits (10,000 values per day), collision risk is high if you're inserting more than a few thousand records per day. Adjust the split:

| Split | Date precision | Random space |
|---|---|---|
| `YYYYMMDD` (8) + 4 random | Day | 10,000 per day |
| `YYYYMMDD` (8) + 4 random | Day | 10,000 per day |
| `YYYYMM` (6) + 6 random | Month | 1,000,000 per month |
| `YYYYMMDDHHMI` (12) + 0 | Minute | Sequential, no randomness |

For a pipeline processing millions of records, `YYYYMMDD` (8) + 4 random is too tight. Stay with 12 fully random, or use one of the modern approaches below.

---

### Other ID Strategies

#### 1. UUID v4 — The Industry Default

```java
import java.util.UUID;
String id = UUID.randomUUID().toString();
// "550e8400-e29b-41d4-a716-446655440000"
```

- 128 bits of randomness — effectively zero collision probability
- Universally recognised across every language and system
- Downside: 36 characters with hyphens (or 32 without), not numeric, and random insertion order fragments B-tree indexes (bad for write-heavy tables)

#### 2. UUID v7 — Time-Ordered UUID (Modern Standard)

UUID v7 encodes a millisecond timestamp in the first 48 bits, then random bits. Looks like a standard UUID but sorts by creation time. Better for database indexes than v4 because new rows insert at the "right end" of the index rather than at random positions.

No built-in Java support yet — use a library like `uuid-creator`.

**UUID v4 and the random insert problem**: UUID v4 is fully random (128 bits). When used as a primary key or in a unique index, every new row lands at a random position in the B-tree — causing constant page splits, exactly like the random VARCHAR(12) PK problem described in Section 30. At scale (millions of rows), throughput degrades badly. UUID v7 solves this because the timestamp prefix keeps new rows near the right end of the index tree.

#### 3. Snowflake ID (Twitter's Approach)

A 64-bit integer composed of:
```
[ 41 bits: ms timestamp ] [ 10 bits: machine/worker ID ] [ 12 bits: sequence ]
```

- Fits in a `LONG` — fast, compact, numeric
- The sequence counter (0–4095) allows 4096 IDs per millisecond per machine
- Machine ID allows multiple servers to generate IDs without coordination
- Naturally time-sortable

Used by Twitter, Discord, Instagram (their variant). The right choice for distributed systems generating millions of IDs/second.

#### 4. ULID — Universally Unique Lexicographically Sortable Identifier

```
01ARZ3NDEKTSV4RRFFQ69G5FAV
├── 48-bit timestamp ──┤├── 80-bit random ──┤
```

26 characters, Crockford Base32 encoded. Sortable, URL-safe, and compatible with UUID storage (same 128 bits). Good for APIs and document stores.

#### 5. Hash-Based ID (Deterministic)

Instead of generating a random ID, derive it from the source data:

```java
import java.security.MessageDigest;

String input = sourceTransId + "|" + sourceId + "|" + sourceDateCreated;
MessageDigest digest = MessageDigest.getInstance("SHA-256");
byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
// Encode as hex string, take first 12 chars
String id = HexFormat.of().formatHex(hash).substring(0, 12);
```

Key property: **the same source transaction always produces the same ID**. This means:
- Re-running the pipeline on the same file produces the same IDs
- If a duplicate source transaction appears, it generates the same ID and the DB unique constraint rejects it — automatic deduplication
- No retry needed — if it exists, it exists

Downside: two completely different transactions could theoretically produce the same 12-char prefix (truncation collision). The full 64-char SHA-256 has no practical collision risk; truncating to 12 chars reintroduces it.

---

### Why Pure Random 12 Digits Wins for This Project's Scale

This is counterintuitive — adding a timestamp *sounds* better, but for a file with millions of records, the math shows the opposite.

The birthday problem tells you at what volume collisions become likely: roughly √(total possible values).

| Strategy | Collision space | Collisions likely after |
|---|---|---|
| `YYYYMMDD` (8) + 4 random | 10,000 per day | **~100 records** |
| `YYYYMM` (6) + 6 random | 1,000,000 per month | ~1,000 records |
| 12 pure random digits | 1,000,000,000,000 | ~1,000,000 records |

A 1.5GB CSV with ~5 million records: the `YYYYMMDD+4` approach would have constant retries from the first few hundred records onward. Pure random handles 5 million records with only a handful of retries across the whole run.

**The supervisor's requirement ("come up with your own way") is already satisfied by the current approach.** It is genuinely custom — `SecureRandom` over a numeric alphabet, 12 digits, with DB-level collision handling and retry logic. That is a design decision, not a library call.

The timestamp+random hybrid is the right choice when you need IDs that are **time-sortable** (useful for pagination, range queries, or debugging). If that matters, use `YYYYMM` (6) + 6 random = 12 total, which gives 1M slots per month. For this pipeline, `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` already gives you the time dimension — the ID doesn't need to encode it.

### Recommendation for This Project

Keep the generated ID as the primary key and keep the pure random approach. Add a **`source_hash`** column (full SHA-256, not truncated) as a secondary `UNIQUE` constraint. See Section 28 for the full explanation of why this is the right split.

---

## 27. Idempotent Pipelines

**Idempotent** means: running the operation once or a hundred times produces the same result.

A pipeline is idempotent if you can re-run it on the same data safely — no duplicates, no errors, no data loss. This is critical because pipelines fail and need to be restarted.

Currently this pipeline is **not idempotent**. Re-running it on the same CSV inserts every row again, creating duplicates (the primary key changes because the ID is random).

---

### Making It Idempotent with SHA-256

Add a `source_hash` column — a SHA-256 fingerprint of the fields that uniquely identify a source transaction:

```sql
-- Add to the transactions table (new Flyway migration)
ALTER TABLE transactions
ADD COLUMN source_hash VARCHAR(64) NOT NULL,
ADD UNIQUE INDEX ux_source_hash (source_hash);
```

Compute it in Java before saving:

```java
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.HexFormat;

private String computeHash(Transaction t) throws Exception {
    String input = t.getSourceTransId() + "|" + t.getSourceId() + "|" + t.getSourceDateCreated();
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
    return HexFormat.of().formatHex(hash);  // 64-char hex string
}
```

Now in `saveWithRetry`:
```java
transaction.setSourceHash(computeHash(transaction));
transaction.setId(idGenerator.generate());
transactionRepository.save(transaction);
```

When you re-run the pipeline, the same source transaction produces the same hash. MySQL rejects the insert with `SQLIntegrityConstraintViolationException` on the `source_hash` unique index. You catch it and skip — not an error, just a duplicate.

```java
} catch (SQLIntegrityConstraintViolationException e) {
    if (e.getMessage().contains("ux_source_hash")) {
        log.info("Skipping duplicate: {}", transaction.getSourceTransId());
        // not an error — already processed
    } else {
        attempts++;  // ID collision — regenerate and retry
        if (attempts == 3) throw e;
    }
}
```

### INSERT IGNORE / ON DUPLICATE KEY

MySQL also supports handling duplicates at the SQL level:

```sql
-- Silently skip duplicate rows (no error thrown)
INSERT IGNORE INTO transactions (...) VALUES (...);

-- Insert or update if duplicate
INSERT INTO transactions (id, source_hash, amount, ...)
VALUES (?, ?, ?, ...)
ON DUPLICATE KEY UPDATE amount = VALUES(amount);
```

`INSERT IGNORE` is useful when you want to re-run safely without any application-level handling. The downside is that it also silently ignores *other* errors (like type mismatches), which can hide bugs.

---


---

## The general version of this
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency (Java course)]]
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed transactions]] — why exactly-once is impossible and idempotency is the answer
- [[databases/interview/01-sql-modelling-and-internals|Databases: Q7]] — UUID primary key tradeoffs

↑ [[projects/README|All projects and the domains they exercise]]
