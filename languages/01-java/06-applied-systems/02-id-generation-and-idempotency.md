# ID Generation & Idempotency

**Source:** `record-id-generator-java/learning/07-id-generation-and-idempotency.md`.

## Generating unique IDs

```java
public class IdGeneratorService {
    private static final String DIGITS = "0123456789";
    private final SecureRandom random = new SecureRandom();   // cryptographically strong — unpredictable, unlike Random

    public String generate() {
        StringBuilder sb = new StringBuilder(12);
        for (int i = 0; i < 12; i++) sb.append(DIGITS.charAt(random.nextInt(DIGITS.length())));
        return sb.toString();
    }
}
```

## The birthday paradox — when collisions actually become likely

With k possible values and n generated IDs, the expected number of collisions across the whole set is approximately `n² / (2k)`. The counterintuitive part: collisions become non-negligible once n approaches **√k**, not k itself.

For 12 random decimal digits (`k = 10¹²`), the 50%-per-insert collision threshold is reached around `√(10¹²) ≈ 1,000,000` rows — comfortably past a typical single load of a few million rows, where the expected collision count stays in the low tens, cheaply absorbed by a retry loop:

```java
int attempts = 0;
while (attempts < 3) {
    try {
        entity.setId(idGenerator.generate());
        repository.save(entity);
        return;
    } catch (SQLIntegrityConstraintViolationException e) {
        attempts++;   // retry with a freshly generated ID
    }
}
```

**In-memory dedup for bulk loads with no DB round-trip** (used when the unique index is dropped for load speed — see [[languages/01-java/06-applied-systems/03-batch-processing-and-performance]]): track generated IDs in a set before they ever reach the DB.

```java
// Single-threaded
Set<Long> usedIds = new HashSet<>(8_000_000);
String id = idGenerator.generate();
while (!usedIds.add(Long.parseLong(id))) id = idGenerator.generate();   // add() returns false if already present

// Shared across multiple consumer threads
Set<Long> usedIds = ConcurrentHashMap.newKeySet(8_000_000);   // thread-safe add() — see 04-concurrency-and-the-jvm
```

At scale, a `HashSet<Long>` of several million boxed longs costs hundreds of MB. A **Bloom filter** (e.g. Guava) trades exactness for ~50x less memory — it can false-positive (says "seen" when it hasn't, triggering a harmless extra regeneration) but never false-negatives, which is exactly the failure mode you want for ID dedup.

## Comparing ID strategies

| Strategy | Collision space | Sortable | Notes |
|---|---|---|---|
| Pure random digits | Large (10ⁿ) | No | Simple; fine below the √k threshold |
| Timestamp prefix + random suffix | Small — bounded by the suffix width | Yes | Sorts chronologically, but the random part must be wide enough for daily/monthly volume or collisions start almost immediately |
| UUID v4 | 2¹²⁸ — negligible | No | Universal, zero coordination — but fully random, so as an indexed/PK column it causes the clustered-index page-split problem in [[languages/01-java/04-persistence/01-jdbc-and-data-modeling]] |
| UUID v7 | 2¹²⁸ — negligible | Yes (ms timestamp prefix) | Same universality as v4, but new rows insert near the "right end" of a B-tree index instead of at random positions — the fix for v4's index-fragmentation cost |
| Snowflake (Twitter) | `[41-bit ms timestamp][10-bit worker id][12-bit sequence]` in a 64-bit long | Yes | Compact, numeric, coordination-free across machines via the worker-ID bits; 4096 IDs/ms/machine |
| ULID | 48-bit timestamp + 80-bit random, Base32 | Yes | URL-safe, same 128 bits as a UUID |
| Hash-based (deterministic) | Depends on truncation length | No | Same source data always produces the same ID — free deduplication with no retry logic, at the cost of truncation collision risk if hashed and cut short |

The general lesson in choosing between these: a timestamp-prefixed ID *looks* like a strict improvement (sortable, meaningful) but the math often runs backwards for high-volume ingestion — a narrow random suffix (say, 4 digits for daily precision) hits its own birthday-paradox threshold at a few hundred rows, while 12 fully random digits doesn't hit it until roughly a million. **Sortability and low collision risk are in tension**, and the right tradeoff depends entirely on expected volume per unit of time precision.

## Idempotent pipelines

A pipeline is **idempotent** if running it once or a hundred times against the same input produces the same end state — critical because pipelines fail and get re-run.

**Making a random-PK design idempotent**: since the surrogate key changes on every attempt (it's random), it can't detect a re-run by itself. Add a **business key** — a deterministic fingerprint of the fields that identify a source record — as a secondary unique constraint:

```java
private String computeHash(Transaction t) {
    String input = t.getSourceTransId() + "|" + t.getSourceId() + "|" + t.getSourceDateCreated();
    byte[] hash = MessageDigest.getInstance("SHA-256").digest(input.getBytes(StandardCharsets.UTF_8));
    return HexFormat.of().formatHex(hash);
}
```

```sql
ALTER TABLE transactions ADD COLUMN source_hash VARCHAR(64) NOT NULL, ADD UNIQUE INDEX ux_source_hash (source_hash);
```

On re-run, the same source record produces the same hash, and the unique index rejects the duplicate insert — a violation that's expected and handled as a no-op, not an error:

```java
} catch (SQLIntegrityConstraintViolationException e) {
    if (e.getMessage().contains("ux_source_hash")) {
        log.info("Skipping duplicate: {}", t.getSourceTransId());   // already processed — not an error
    } else {
        attempts++;   // an actual PK collision — regenerate and retry
    }
}
```

MySQL can also absorb this at the SQL level instead of the application level: `INSERT IGNORE` silently skips a row that would violate a unique constraint (no exception thrown, batch continues), while `ON DUPLICATE KEY UPDATE` overwrites instead of skipping. `INSERT IGNORE` also silently swallows *other* kinds of errors (type mismatches, etc.), which can mask real bugs — a deliberate tradeoff, not a free lunch.

## Related
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|Persistence & Data Modeling]] — the surrogate-key/business-key split this idempotency design depends on
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — at-least-once delivery is exactly why consumers need an idempotent write path
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — `INSERT IGNORE` performance cost under bulk load

## Seen in the wild
- [[projects/record-id-generator-java/learning/07-id-generation-and-idempotency|record-id-generator]] — this exact design, built and tuned for throughput
- [[projects/direct-debit-sandbox-java/learning/05-async-scheduling-retry|direct-debit-sandbox]] — idempotency where getting it wrong means double-charging someone
- [[languages/01-java/interview/03-spring-persistence-and-systems|Interview: Q6]]
