# record-id-generator-java — Operations, Observability & Story

From [`../learning/09-logging-and-observability.md`](../learning/09-logging-and-observability.md),
[`10-docker-and-performance-tuning.md`](../learning/10-docker-and-performance-tuning.md).

---

### Q1. [Intermediate] 🔥 How do you know this pipeline is healthy? What do you actually measure?

**Strong answer covers:** four metrics that answer different questions —
- **Throughput** (rows/sec, ideally per phase) — the headline number, and the one that revealed the
  degrading-rate problem.
- **Queue depth** — the single best indicator of producer/consumer imbalance. Growing depth means the
  consumer is losing; zero depth with a busy producer means the consumer is starved (a prefetch
  problem).
- **Error/DLQ rate** — how much is failing, and whether it's climbing.
- **Rows written vs rows read** — the correctness check. Everything else can look healthy while rows
  quietly vanish.

**The distinction to state:** throughput tells you if it's fast; read-vs-written tells you if it's
*right*. Only one of those is a real health check.

---

### Q2. [Intermediate] What does the RabbitMQ management UI actually tell you?

**Strong answer covers:** queue depth over time, publish rate versus deliver/ack rate (the two lines
that diverge when the consumer falls behind), unacked message count — which should hover around your
prefetch value, and a useful sanity check that `basicQos` is actually in effect — and consumer count,
which catches "the worker never started" faster than any log grep.

---

### Q3. [Advanced] 🔥 You had a producer count bug. How did the logs reveal it?

**Strong answer covers:** the shape of the answer matters more than the specific bug — logging
**counts at each stage** (lines read, messages published, rows batched, rows inserted, rows skipped)
means a discrepancy between adjacent stages localises the fault immediately. A count that doesn't
match its neighbour is a defect you can *see*, whereas a pipeline that only logs "done" gives you
nothing to compare. That's the argument for count-based logging over event-based logging in data
work.

---

### Q4. [Intermediate] 🔥 What does "all skipped" in the logs mean, and why is a re-run so much faster than a fresh load?

**Strong answer covers:** "all skipped" means every row hit the unique key and `INSERT IGNORE`
discarded it — i.e. the data was already fully loaded. It's the expected output of a second run and
proof idempotency works.

**Why faster:** no page splits, no index inserts, no redo log pressure, no dirty-page flushing —
just parse and index-lookup per row (Q14 in
[03-mysql-performance-and-ids.md](03-mysql-performance-and-ids.md)). **The trap to name:** a re-run's
timing is *not* a valid benchmark of your load performance, and comparing them is how people
convince themselves an optimisation worked when they actually just measured a no-op.

---

### Q5. [Intermediate] What are you reading in the HikariCP pool stats?

**Strong answer covers:** the numbers are `active / idle / waiting`. Sustained **waiting > 0** means
threads are blocked on connection checkout — the pool is the bottleneck, not the database.
Persistently high **idle** means the pool is oversized. And connection acquisition timeouts in the
log usually mean a **leak** — a connection checked out on an error path and never returned, which is
the exact failure try-with-resources exists to prevent.

---

### Q6. [Beginner] Why SLF4J plus Logback rather than `System.out.println`?

**Strong answer covers:** SLF4J is a facade, Logback the implementation — so libraries compile
against the facade and the application picks the backend, without every dependency dragging in its
own logging framework. Practically you get levels (so debug detail can exist without shipping in
production), structured output and appenders, parameterised messages (`log.info("loaded {} rows", n)`)
that skip string concatenation when the level is disabled, and per-package configuration. `println`
gives you none of that and can't be turned off.

---

### Q7. [Intermediate] 🔥 You keep log *tables* in the database, not just log files. Why?

**Strong answer covers:** a run record — start/end time, source file, counts, status — is
**queryable state**, not text. It answers "was this file already loaded, and what happened?" without
grepping, survives log rotation, and gives the pipeline something to reason about programmatically
(a run that started and never finished is a crashed run). The general standard: for any batch job,
record the *run* as a row, not only as output. Log files are for diagnosis; log tables are for
control.

---

### Q8. [Intermediate] What would Micrometer + Prometheus add over what you have?

**Strong answer covers:** logs tell you what happened once; metrics tell you what's happening over
time. Micrometer is the facade, Prometheus scrapes and stores, and you get rate/histogram/percentile
views plus alerting thresholds — "throughput dropped below X for five minutes" is not something you
can express with log lines. The honest framing: for a one-shot loader run by hand, logs and counts
are proportionate; the moment it runs on a schedule and nobody watches it, metrics and alerts stop
being optional.

---

### Q9. [Intermediate] 🔥 Explain the multi-stage Dockerfile and why it matters.

**Strong answer covers:** stage one uses a full JDK image with Gradle to build the jar; stage two
copies *only* the jar into a JRE (or slimmer) base. The final image contains no source, no build
tool, no Gradle caches — smaller, faster to pull, and a much smaller attack surface. The related
build-cache detail: copy the Gradle files and resolve dependencies *before* copying source, so a
source-only change doesn't invalidate the dependency layer and re-download everything.

---

### Q10. [Intermediate] Why put MySQL and RabbitMQ tuning in `docker-compose.dev.yml` rather than documenting it?

**Strong answer covers:** the tuning **is** the pipeline's performance. `innodb_flush_log_at_trx_commit=2`,
`innodb_buffer_pool_size=512M`, `max_allowed_packet=256M` and `innodb_log_buffer_size=64M` aren't
incidental environment details — they're the difference between hours and minutes, so they belong in
version control where every developer and CI run gets them automatically. A README instruction that
must be followed manually is a setting that will be wrong on someone's machine.

**Specific note on `max_allowed_packet`:** it has to be large *because* of
`rewriteBatchedStatements=true` — a rewritten batch is one enormous statement, and the default packet
limit rejects it. That's a genuinely nice detail: enabling the optimisation requires a second,
non-obvious setting to accommodate it, and hitting the packet-size error is how most people discover
the rewrite is finally working.

---

### Q11. [Advanced] 🔥 Someone says "5.75 million rows isn't big data, why did any of this matter?"

**Strong answer covers:** agree, and reframe. 5.75M rows is small — which is exactly the point: the
naive version still took hours, because the bottlenecks were **structural**, not volumetric. An
un-batched batch is 5.75M round-trips regardless of whether that's "big data"; a random-value index
outgrows the buffer pool at a size nobody would call large. The lesson is that these problems show
up far earlier than people expect, and the fixes are configuration and design rather than more
hardware. Being able to say "the win came from removing work, not from adding capacity" is the
answer.

---

### Q12. [Advanced] 🔥 Which optimisation gave the biggest win, and how did you know where to look?

**Strong answer covers:** `rewriteBatchedStatements=true` — 10–50× on the write phase from one URL
parameter. But the *method* is the real answer: the rate was degrading per batch, which pointed at
something growing (index maintenance), while the absolute throughput was low from the very first
batch, which pointed at per-row overhead. Two different symptoms, two different causes, found by
looking at the shape of the throughput curve rather than at a single average. Say that — "I looked
at how it changed over time, not just how fast it was" — because it's the transferable skill.

---

### Q13. [Intermediate] What are the trade-offs you knowingly accepted, and when would you reverse them?

**Strong answer covers:** name three and their reversal conditions —
- **`innodb_flush_log_at_trx_commit=2`** — safe only because the CSV is the source of truth and the
  load is re-runnable. Reverse immediately for transactional workloads.
- **Load-then-index** — trades duplicate protection during the load for speed, compensated by an
  in-memory set. Reverse if the dataset stops fitting in memory or if concurrent writers exist.
- **Dropping `source_hash`** — trades hash-based idempotency for insert throughput. Bring it back
  when re-runs over dirty or partially-overlapping data are expected.

Every one of these is "correct for a re-runnable bulk load, wrong for a live transactional system."
That's the frame to state up front.

---

### Q14. [Beginner] 🔥 Tell me about a bug in this project that taught you something.

**Strong answer covers:** the driver deception is the headline (a bug with no error), but the
**graceful-shutdown race** is the better *character* answer, because you found it by reasoning about
correctness rather than by seeing a failure — "it works because the consumer happens to be faster
than the producer" is a description of luck, not of a design. Being able to say *"this passed every
test I ran and was still wrong"* about your own code is a strong signal.

---

### Q15. [Advanced] If you rebuilt this today, what would you change?

**Strong answer covers:** commit to specifics —
- **Fix shutdown properly** — poison pill or `CountDownLatch`, not a joined producer and a hoped-for
  drain.
- **Stop parsing MySQL error strings** to find the offending row — it's version-coupled; use the
  batch update-count array (with the `SUCCESS_NO_INFO` caveat) or a smaller retry batch.
- **Decide up front whether the broker is earning its place** — for a single-machine loader,
  `LOAD DATA LOCAL INFILE` after an ID-generation pass may beat the whole architecture; keep the
  queue only if incrementality, restartability, or a future separate consumer are real requirements.
- **Measure before optimising, and keep the measurements** — the throughput-per-batch curve is what
  diagnosed everything, and it should have been a first-class output of every run, not something
  read off logs after the fact.
