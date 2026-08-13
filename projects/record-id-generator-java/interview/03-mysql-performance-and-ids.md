# record-id-generator-java — MySQL Performance & ID Design

From [`../learning/04-database-mysql-flyway.md`](../learning/04-database-mysql-flyway.md),
[`07-id-generation-and-idempotency.md`](../learning/07-id-generation-and-idempotency.md),
[`10-docker-and-performance-tuning.md`](../learning/10-docker-and-performance-tuning.md).

**This is the file that wins the interview.** Everything here is measured, specific, and
non-obvious.

---

### Q1. [Advanced] 🔥🔥 You wrote a batch insert with `addBatch()` / `executeBatch()` and it was still slow. What was happening?

**The single best story in the project. Tell it in this order:**

1. **The expectation:** `executeBatch()` should send one statement —
   `INSERT INTO transactions (...) VALUES (?,?),(?,?),(?,?)...`
2. **The reality:** without a specific URL parameter, the MySQL JDBC driver **silently breaks the
   batch back into individual statements** — 1,000 separate `INSERT`s, one round-trip each.
3. **Why it's insidious:** the code compiles, runs, throws nothing, and the logs show batches
   completing. Nothing anywhere says "your batch is not a batch." It's a performance bug with no
   error surface.
4. **The fix — one config value:**
   `jdbc:mysql://localhost:3306/records_db?rewriteBatchedStatements=true`
5. **The magnitude:** typically **10–50× faster** on the write phase alone.

**The generalisable lesson to land:** a library API's *shape* doesn't guarantee its *behaviour*.
"It ran without error" is not evidence that it did the thing the method name implies — for anything
performance-critical, verify with the query log or with measurement, not with the API's naming.

---

### Q2. [Intermediate] 🔥 Name the three bottlenecks in a slow bulk pipeline and their fixes.

**Strong answer covers (this is a table worth memorising):**

| Bottleneck | Root cause | Fix |
|---|---|---|
| Network round-trips | One INSERT per row, or "batches" that aren't really batched | `rewriteBatchedStatements=true` + a large batch size |
| Transaction overhead | MySQL flushes the log to disk on every commit | `innodb_flush_log_at_trx_commit=2` |
| Consumer starvation | `basicQos` too low — consumer idles between deliveries | Raise prefetch to match batch size |

The reason this lands well is that it spans three different layers — driver, database, broker — and
shows you diagnosed rather than guessed.

---

### Q3. [Advanced] 🔥 `innodb_flush_log_at_trx_commit=2` — what exactly does that change, and what are you giving up?

**Strong answer covers:** it controls when the InnoDB redo log is flushed to disk.

| Value | Behaviour | Trade-off |
|---|---|---|
| `1` (default) | Flush on every commit | Slowest, fully durable — survives OS crash |
| `2` | Write to OS cache on commit, flush once/second | Fast; a **host/OS** crash can lose ~1s, a MySQL process crash cannot |
| `0` | Write and flush once/second | Fastest; a MySQL crash can lose ~1s |

**Why it's safe *here*:** this is a bulk load from a CSV that still exists, and the pipeline is
idempotent — losing a second of writes means re-running, not losing data. That justification is the
answer. Setting this on a transactional production system handling payments would be a completely
different conversation, and saying so unprompted is what makes it a senior answer.

---

### Q4. [Advanced] 🔥🔥 Insert rate dropped with every batch. Why, and what's load-then-index?

**Strong answer covers:**

**Why it degrades:** every insert must also maintain the secondary/unique index. A B-tree index on
*random* values means each insert touches an arbitrary page. While the index fits in the buffer
pool, that's a memory write; once it outgrows the pool, each insert becomes a random *disk* read to
fetch the page plus a write. Throughput doesn't decline linearly — it falls off a cliff at the point
the working set stops fitting in RAM. That's why the rate drops with each successive batch.

**The fix — load-then-index:** drop the unique/secondary index, bulk-load everything, then build
the index once at the end. Index construction on a full table is a bulk sort-and-build, which is
dramatically cheaper than N random insertions. Hours → minutes.

**The consequence you must handle:** with no unique index during the load, the database can no
longer catch duplicate IDs — which is exactly why dedup moves into an in-memory set for the duration
of the load (see Q8).

**Follow-up:** *"Why not just disable unique checks (`SET unique_checks=0`)?"* — it defers the
checking but the index is still maintained, so you keep the random-write cost and lose the safety.
Dropping the index removes the actual work.

---

### Q5. [Advanced] 🔥 What is `innodb_buffer_pool_size` and why does it dominate this workload?

**Strong answer covers:** it's the in-memory cache for InnoDB data and index pages — the single most
important MySQL memory setting. The whole load-then-index story is really a story about whether the
index fits in it: while it does, index maintenance is RAM-speed; when it doesn't, every insert
becomes random disk I/O. Sizing it so the working index fits (512M in the Docker config here) is
what keeps the rate flat. On a dedicated database server the conventional guidance is a large
fraction of system RAM; in a container it's whatever you've given the container, which is why it's
set explicitly in `docker-compose.dev.yml` rather than left at the default.

---

### Q6. [Advanced] 🔥 The redo log — what is it, and how does it become the bottleneck?

**Strong answer covers:** the redo log is InnoDB's write-ahead log: changes are written there first
so a crash can replay them, and dirty pages are flushed to the tablespace later. It's a fixed-size
circular buffer. Under a heavy write load it **fills up**, and when it does, InnoDB must force a
checkpoint — aggressively flushing dirty pages — before it can reuse space. The symptom is a write
throughput that stalls periodically rather than degrading smoothly.

**Fixes:** size the redo log large enough that a bulk load doesn't wrap it constantly, and raise
`innodb_log_buffer_size` so large transactions don't have to write to the log file mid-transaction.

**Why this is a strong thing to know:** most people can name the buffer pool. Being able to describe
the redo log and its checkpoint stall is what distinguishes "I read a tuning guide" from "I watched
this happen and worked out why."

---

### Q7. [Advanced] 🔥🔥 You migrated from a random VARCHAR primary key to a `BIGINT AUTO_INCREMENT`. Why?

**Strong answer covers:** InnoDB's primary key is a **clustered index** — the table's rows are
physically stored in primary-key order, and every secondary index stores the PK as its pointer.
That has three consequences with a random VARCHAR PK:

1. **Random insert position.** Each insert lands at an arbitrary point in the clustered index,
   causing page splits and fragmentation, and getting worse as the table grows — the table
   physically reorganises itself as you load it.
2. **Wide pointer.** Every secondary index carries a copy of the PK, so a long VARCHAR bloats every
   index on the table, meaning fewer entries per page and more I/O everywhere.
3. **Comparison cost.** String comparison with a collation is more expensive than integer
   comparison, on every single index traversal.

An auto-increment `BIGINT` appends monotonically to the end of the clustered index — no splits,
8-byte pointers, integer comparisons.

**The design split to state:** the generated 12-digit business ID is still a real requirement, so it
stays as a **unique-indexed column**, not as the PK. The lesson generalises: *the primary key is a
storage decision; the business identifier is a domain decision.* Making one value serve both is what
causes this.

**Bonus:** this shipped as a V3 Flyway migration, which is the right way to tell the story — the
design was wrong, the fix was versioned and repeatable, and nothing was edited retroactively.

---

### Q8. [Advanced] 🔥 Do the collision maths for your 12-digit random ID.

**Strong answer covers (know these numbers):**

- 12 decimal digits → k = 10¹² possible values.
- Expected collisions across n rows ≈ **n² / 2k**.
- At n = 5.75M: (5.75×10⁶)² / (2×10¹²) ≈ **16 collisions** across the entire load — the retry loop
  fires 16 times. Negligible.
- The threshold where each *new* insert has roughly a 50% chance of colliding is around
  √(10¹²) = **1 million rows**. Below that collisions are rare; above it they're more frequent but
  still absorbed by a bounded retry (limit 3).

**Why this answer is strong:** it's the birthday paradox applied to a real design decision with a
real number attached, and it ends with "so pure random is sufficient *at this scale*" — a
scale-qualified conclusion rather than a universal claim.

---

### Q9. [Advanced] How does collision detection work when the unique index has been dropped for the bulk load?

**Strong answer covers:** the database can't catch it, so dedup moves in-process — track generated
IDs in a set and regenerate on collision *before* the value ever reaches the database:

```java
Set<Long> usedIds = ConcurrentHashMap.newKeySet(8_000_000);   // shared across consumers
while (!usedIds.add(Long.parseLong(id))) id = idGenerator.generate();
```

Two details that matter: the set is **pre-sized** to avoid repeated rehashing of a multi-million
entry structure, and it's a **concurrent** set because multiple consumer threads generate
independently and can collide *with each other*, not just with the database. The single-threaded
bulk loader uses a plain `HashSet` for the same job — matching the tool to the actual concurrency.

**The cost to acknowledge:** ~8M boxed `Long`s is real heap. Alternatives if it didn't fit: a
primitive long set (Eclipse Collections/fastutil), a Bloom filter as a probabilistic pre-check with
DB fallback, or partitioning the ID space per consumer so threads structurally cannot collide.

---

### Q10. [Intermediate] 🔥 What alternatives to random IDs did you consider, and why did random win here?

**Strong answer covers:** name the field and why each doesn't fit —
- **Auto-increment:** perfectly dense and index-friendly, but guessable and leaks volume (customer
  #5,750,000 tells a competitor your row count). Also needs the DB to assign it, so the value isn't
  known until after insert.
- **UUIDv4:** collision-free for practical purposes, but 128 bits and random — the exact clustered
  index problem from Q7, and 36 characters is unusable as a human-readable reference.
- **Timestamp + random hybrid (Snowflake-ish):** roughly monotonic so it's index-friendly, and
  encodes ordering — genuinely better for a distributed system, but needs worker-ID coordination and
  produces longer IDs.
- **Random 12-digit:** the actual requirement is a short, non-guessable, human-quotable reference.
  It wins here because the maths (Q8) shows collisions are negligible at this scale and the retry
  loop handles them.

**Ending on "at this scale" is the point** — the answer changes at 10⁹ rows and you should say so.

---

### Q11. [Intermediate] 🔥 What makes this pipeline idempotent, and why does it need to be?

**Strong answer covers:** re-running must not duplicate rows, because a crashed load's recovery
strategy is "run it again" and DLQ replay would otherwise be pure duplication. Two mechanisms: a
**content hash (SHA-256) of the source row** as a natural dedup key so the same input maps to the
same identity, and `INSERT IGNORE` / `ON DUPLICATE KEY` so a re-inserted row is skipped rather than
erroring.

**The nuance worth adding:** `source_hash` was later *removed* for clean data, because maintaining
another unique index costs exactly what Q4 describes — index maintenance on random values during a
bulk load. That's a real trade: idempotency-by-hash is bought with insert throughput, and it's only
worth it when re-runs on dirty data are actually expected.

---

### Q12. [Advanced] 🔥 `INSERT IGNORE` vs `ON DUPLICATE KEY UPDATE` vs `REPLACE` — when does each apply?

**Strong answer covers:**
- **`INSERT IGNORE`** — skip conflicting rows, keep going. Correct when the existing row is
  authoritative and duplicates are expected. The danger: it downgrades *all* errors to warnings, not
  just duplicate-key ones, so a truncated value or a bad type silently becomes a warning and
  possibly a mangled row.
- **`ON DUPLICATE KEY UPDATE`** — upsert; conflicting rows get updated. Correct when the new data
  should win.
- **`REPLACE`** — delete-then-insert, which fires delete triggers, breaks foreign keys pointing at
  the row, and burns auto-increment values. Almost always the wrong choice.

For this pipeline `INSERT IGNORE` is right — the row is already loaded, there's nothing to update —
with the caveat about error suppression stated explicitly.

---

### Q13. [Advanced] 🔥 `executeBatch()` returned `SUCCESS_NO_INFO`. What does that mean for your "rows skipped" counter?

**Strong answer covers:** `executeBatch()` returns a per-statement update count, and drivers are
permitted to return `Statement.SUCCESS_NO_INFO` (-2) meaning "this succeeded but I can't tell you
how many rows it affected" — which is exactly what happens once the batch is rewritten into a single
multi-row statement. So counting skipped rows by summing the returned array **silently produces the
wrong number**. The correct source is the connection's affected-row count or `SHOW WARNINGS` /
comparing table counts before and after.

**Why this pairs beautifully with Q1:** the same optimisation that made the pipeline fast is what
broke the counting — a performance fix changing an observability guarantee. That's a genuinely
sophisticated thing to have noticed.

---

### Q14. [Intermediate] Why is `INSERT IGNORE` not free? A skipped row does no work, surely?

**Strong answer covers:** it isn't free — the server still has to parse the statement, and crucially
still has to **look up the index** to discover the conflict. On a large table that lookup is a real
B-tree traversal, possibly a disk read. So a re-run over data that's entirely already loaded is
faster than a fresh load but nowhere near free, which is exactly what the "re-run vs fresh load"
timing difference in the logs shows.

---

### Q15. [Intermediate] What is Flyway giving you, and what's the rule that comes with it?

**Strong answer covers:** versioned, ordered, checksummed migrations applied automatically and
recorded in a history table, so every environment converges to the same schema and drift is
detectable. The rule: **migrations are append-only** — once a version is applied anywhere, you add
V4, you never edit V3. Flyway enforces this with checksums, so editing an applied migration fails
validation rather than silently diverging. The V3 clustered-index migration in this project is the
model: a design mistake fixed forward, in a versioned, repeatable way.

---

### Q16. [Advanced] When would you skip all of this and use `LOAD DATA LOCAL INFILE`?

**Strong answer covers:** it's the fastest bulk path in MySQL by a wide margin — the server reads the
file directly, bypassing per-row statement overhead entirely. It's the right answer when the job is
purely "get this file into this table." It's *not* what this project needed, because each row needs
a generated ID and passes through a broker where per-row logic lives. Naming the faster tool you
deliberately didn't use, and why, is a stronger answer than not knowing it exists.

**Follow-up:** *"Could you have used it anyway?"* — yes, by generating IDs up front and writing a
transformed CSV, then loading that. It's a genuine architectural alternative: batch-transform then
bulk-load, versus stream-through-a-queue. The queue version wins on incrementality and restartability;
`LOAD DATA` wins on raw speed.
