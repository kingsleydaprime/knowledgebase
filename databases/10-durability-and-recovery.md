---
id: 7fbbab0c-98ce-4099-a013-bb3adc4b4d3b
---

# Durability and Recovery

Durability is a database's promise that once it says your change is saved, the change will survive even if the power goes off a second later. Recovery is how the database gets back to a correct state after such a crash. The main trick is to write each change to a log first, before updating the tables.

## The problem
<!-- bite: 9cde982d-27c1-4df1-b905-757e13635fc8 -->

**A commit must survive a crash.** But writing every changed page to disk at commit time would be:

**Slow** — random writes scattered across the file.

**Amplified** — an 8 KB page write for a 20-byte change.

**Not even atomic** — a torn page (partially written when power failed) leaves corruption, because a disk's atomic write unit is smaller than a database page.

## Write-ahead logging
<!-- bite: 016e33c0-deba-4bff-a920-f0bdcdd209a4 -->

> **The WAL rule: write the *description of the change* to a sequential log, and fsync that, before modifying the data pages.**

**A commit becomes one sequential append plus one fsync.** The actual pages are written lazily, later, in the background.

```text
 TRANSACTION
     │
     ├─► modify page in buffer pool (in memory, marked dirty)
     │
     └─► append WAL record ──► fsync ──► COMMIT RETURNS ✅
                                              │
                    ... minutes later ...     │
                    CHECKPOINT writes dirty pages to disk
```

**A WAL record says what changed:** "in relation X, page 42, offset 128, the old bytes were A and the new bytes are B."

**Why it works:** if you crash after the WAL is durable but before the pages are written, **the log has enough information to redo the change.** If you crash mid-transaction, the log has enough to undo it.

**The two invariants:**

**Write-ahead** — the WAL record hits disk before the corresponding data page. Enforced by tracking each page's **LSN** (log sequence number) and refusing to flush a page whose LSN exceeds the flushed log position.

**Force-at-commit** — the WAL up to the commit record is fsynced before the commit is acknowledged.

**Both `pg_wal` (Postgres) and `ib_logfile` (InnoDB) are this.**

## ARIES
<!-- bite: ec56dc25-d7f6-40e3-a5f2-5a77d3a9eb8a -->

**The recovery algorithm essentially everyone implements** (Mohan et al., 1992). **Three phases after a crash:**

**1. Analysis** — scan forward from the last checkpoint. Determine which transactions were in flight and which pages were dirty.

**2. Redo** — **repeat history.** Replay *every* logged change since the checkpoint, including those from transactions that will be rolled back. **This restores the exact state at the moment of the crash.**

**3. Undo** — roll back the transactions that hadn't committed, writing **compensation log records** as it goes.

> **"Repeat history, then undo" is the counterintuitive part.** Why redo work you're about to undo? **Because it makes recovery restartable.** If you crash *during* recovery, you can start over — the state is always well-defined, and compensation records mean undo is itself idempotent. **That's what makes ARIES robust rather than merely correct on the happy path.**

## Checkpoints
<!-- bite: 15abf56c-cd20-49dd-b3ee-5baa1a7bdfdb -->

**A checkpoint writes all dirty buffer pages to disk and records the position in the log.**

**It bounds recovery time** — you only replay from the last checkpoint, not from the beginning of time.

**The trade:**

**Frequent checkpoints** → fast recovery, **more I/O during normal operation**, and I/O spikes that hurt latency.

**Infrequent checkpoints** → less steady-state I/O, **long recovery** after a crash.

**Postgres spreads checkpoint writes over time** (`checkpoint_completion_target`, now 0.9 by default) rather than dumping them at once, precisely to avoid the latency spike. **A checkpoint storm — where the write burst stalls foreground queries — is a classic symptom of this being tuned wrong**, and `log_checkpoints = on` is how you see it.

**Full-page writes:** after a checkpoint, the first modification to each page logs the **entire page**, not just the delta. **This protects against torn pages**, and it's why WAL volume spikes right after a checkpoint. Disabling it is only safe on filesystems with atomic page writes (ZFS, or hardware with battery-backed cache).

## fsync, and the ways it lies
<!-- bite: 1d389e02-f43f-4b4b-b8e3-5641ae1412b8 -->

**`fsync()` is the system call that makes durability real** — and there are more layers of caching between your write and the platter than people expect.

```text
 application write()
      ↓
 OS page cache        ← lost on power failure
      ↓  fsync()
 disk write cache     ← lost on power failure unless flushed
      ↓
 persistent media     ← actually durable
```

**Historical and ongoing problems:**

**Drives that ignore flush commands.** Consumer SSDs have shipped claiming a flush completed while data sat in volatile cache. **A power cut then loses acknowledged commits.**

**Virtualised and networked storage** adds layers, each with its own caching and its own honesty.

> **The fsyncgate incident (2018)** is the one worth knowing. **On Linux, if a writeback error occurs, `fsync()` may report the error *once* and then return success on subsequent calls** — with the dirty pages already discarded. **Postgres was treating a failed fsync as retryable, and retrying got a success.**
>
> **The fix, across Postgres, MySQL and others: panic and crash the server on fsync failure**, forcing recovery from the WAL rather than continuing with possibly-lost data. **The correct response to "I cannot confirm durability" is to stop**, and it took the industry a surprisingly long time to conclude that.

**Group commit** is the throughput fix: **batch the fsyncs of several concurrent transactions into one.** Each transaction waits a moment for others to join, then one fsync commits them all. **Turns one fsync per transaction into one per batch** — a large throughput win at a small latency cost. `commit_delay` in Postgres; on by default in InnoDB.

**Testing durability honestly requires pulling the power.** `diskchecker.pl` and similar tools exist for this. **Nobody does it, and that's why storage stacks lie for years before anyone notices.**

## Synchronous commit
<!-- bite: 21901f08-c924-42a8-9a64-99c494e4155b -->

**The knob that trades durability for throughput**, and it's a legitimate choice.

**Postgres `synchronous_commit`:**

| Setting | Meaning |
|---|---|
| `on` | **fsync locally before acknowledging.** Default |
| `off` | acknowledge immediately, fsync within `wal_writer_delay` |
| `local` | fsync locally, don't wait for replicas |
| `remote_write` | wait for a replica to receive it |
| `remote_apply` | wait for a replica to apply it |

> **`synchronous_commit = off` can be several times faster and does *not* risk corruption** — the database stays consistent, because the WAL rule still holds. **You lose only the last few hundred milliseconds of committed transactions** on a crash.
>
> **That's an acceptable trade for analytics, event ingestion, or anything where losing a moment of data is survivable — and unacceptable for payments.** It can be set per-transaction, which is the right granularity: run the payment path synchronously and the metrics path asynchronously.

**InnoDB's equivalent** is `innodb_flush_log_at_trx_commit`: `1` (fsync per commit, ACID), `2` (write to OS, fsync per second), `0` (fsync per second). **`2` survives a process crash but not an OS crash.**

## Backups and PITR
<!-- bite: f9e43a55-4cb8-4c9c-941e-e3f9515933e6 -->

**The WAL enables more than crash recovery.**

**Physical backup + WAL archiving = point-in-time recovery.** Take a base backup, archive every WAL segment, and you can restore to **any moment** — including "one second before someone ran `DELETE` without a `WHERE`".

**Postgres:** `pg_basebackup` plus `archive_command`, or **pgBackRest / WAL-G**, which handle compression, parallelism, retention and verification. **Use one of those rather than hand-rolling.**

**Logical backup** (`pg_dump`) is portable across versions and architectures, and **restores slowly** — it replays SQL. Fine for small databases and schema migration; too slow for large recovery.

> **The rules that matter more than the tooling:**
>
> **A backup you haven't restored is not a backup.** Test restores on a schedule, and time them — **your RTO is whatever a restore actually takes**, not what you hoped.
>
> **Keep backups off the machine, and off the account.** Ransomware and a compromised credential both take out backups stored alongside production.
>
> **Replication is not a backup.** A replica faithfully replicates `DROP TABLE` in milliseconds. **Backups protect against *mistakes*; replicas protect against *hardware*.** These are different threats and you need both. → [[databases/11-replication-and-scaling|Replication]]

**Define your targets explicitly:** **RPO** (how much data may be lost) and **RTO** (how long recovery may take). **They determine your architecture** — `synchronous_commit`, replication mode, and backup frequency all follow from the numbers.

## Practical notes
<!-- bite: 80b5ec2f-5764-4d4d-9ebf-e8bcc87c5482 -->

**Put the WAL on its own fast device** if you can. It's sequential and latency-critical; keeping it off the same spindles as random data I/O helps.

**Size `max_wal_size` generously.** Too small forces frequent checkpoints and constant full-page writes.

**Monitor WAL generation rate** — a sudden spike means either a write burst or something pathological (an unvacuumed table, a runaway update).

**Never disable full-page writes** unless you genuinely have atomic page writes.

**Never disable fsync in production.** `fsync = off` exists for bulk-loading a database you can rebuild, and nothing else. **The message in the docs is not being cautious for the sake of it.**

**Watch for archive failures.** If `archive_command` starts failing, WAL accumulates until the disk fills — **and a full WAL disk stops the database.**

**Test recovery, including wraparound and disk-full scenarios**, before they happen at 3am.

---

## Check your understanding
<!-- bite: 18d056ba-3301-419c-8f3d-0630b237b1cc -->

Try each one before you open the answer.

1. <!-- q: mcq id="196f8f22" -->
   Under the WAL rule, what must be on disk before a commit is acknowledged?

   - [ ] Every data page the transaction changed
   - [x] The WAL records up to and including the commit record
   - [ ] A checkpoint
   - [ ] A full backup

   <details><summary>Answer</summary>

   The WAL up to the commit record, fsynced. The data pages are written later by checkpoints. If the server crashes before then, the log has enough to redo the changes.

   </details>

2. <!-- q: gap id="f2055ed8" answers="analysis;redo;undo" -->
   ARIES recovers in three phases: ___ (find in-flight transactions and dirty pages), ___ (repeat history, replaying every logged change), then ___ (roll back transactions that never committed).

   <details><summary>Answer</summary>

   Analysis, redo, undo. Redoing even the changes that will be undone puts the database in the exact state of the crash, which makes recovery restartable if it crashes again.

   </details>

3. <!-- q: open id="9eb7c50f" -->
   During fsyncgate (2018), Postgres retried an `fsync()` that had failed, got success, and carried on. Why was that wrong, and what do databases do now?

   <details><summary>Answer</summary>

   On Linux, after a writeback error, `fsync()` may report the error once and then return success, with the dirty pages already thrown away. The retry's success meant nothing: the data was lost. Now Postgres, MySQL and others panic and crash on an fsync failure, forcing recovery from the WAL. If you can't confirm durability, stop.

   </details>

4. <!-- q: mcq id="f34b4d12" -->
   A service records page-view events and also takes payments. Where is `synchronous_commit = off` a sensible choice?

   - [x] For the page-view transactions only
   - [ ] For the payment transactions only
   - [ ] For both
   - [ ] Neither, because it corrupts the database

   <details><summary>Answer</summary>

   Page views only. `off` doesn't risk corruption, because the WAL rule still holds, but a crash can lose the last few hundred milliseconds of committed transactions. Losing a few page views is survivable; losing a payment isn't. It can be set per transaction.

   </details>

5. <!-- q: mcq id="43a34c70" -->
   Someone runs `DROP TABLE orders;` on the primary by mistake. What saves you?

   - [ ] The streaming replica
   - [x] A base backup plus archived WAL, restored to just before the drop
   - [ ] Group commit
   - [ ] A checkpoint

   <details><summary>Answer</summary>

   Point-in-time recovery from a backup and the WAL archive. The replica copies the `DROP TABLE` within milliseconds. Replicas protect against hardware failure; backups protect against mistakes.

   </details>

6. <!-- q: open id="94e9d983" -->
   What do RPO and RTO mean, and why does the lesson say "your RTO is whatever a restore actually takes"?

   <details><summary>Answer</summary>

   RPO, the recovery point objective, is how much data you may lose. RTO, the recovery time objective, is how long recovery may take. Until you have restored a real backup and timed it, the RTO you wrote down is a hope. Restores take as long as they take, so test them on a schedule.

   </details>

## Related
<!-- bite: 888279f5-5576-4112-a67f-f09561762c8e -->
- [[databases/09-mvcc-and-concurrency-control/index|MVCC]] — what the log is protecting
- [[databases/11-replication-and-scaling|Replication and Scaling]] — the same WAL, shipped elsewhere
- [[architecture/04-distributed-systems/12-the-log-and-state-machines|The Log and State Machines]] — the same idea, generalised
- [[databases/index|Databases map]]

## About this lesson
<!-- bite: f204a3b1-0795-49b6-9b53-6332bcefd3ff -->

**Level:** Advanced. **Covers:** The write-ahead log, what "committed" actually means, and why fsync is the most important system call in a database.
