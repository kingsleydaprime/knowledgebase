# Durability and Recovery

**[Advanced]** — The write-ahead log, what "committed" actually means, and why fsync is the most important system call in a database.

## The problem

**A commit must survive a crash.** But writing every changed page to disk at commit time would be:

**Slow** — random writes scattered across the file.

**Amplified** — an 8 KB page write for a 20-byte change.

**Not even atomic** — a torn page (partially written when power failed) leaves corruption, because a disk's atomic write unit is smaller than a database page.

## Write-ahead logging

> **The WAL rule: write the *description of the change* to a sequential log, and fsync that, before modifying the data pages.**

**A commit becomes one sequential append plus one fsync.** The actual pages are written lazily, later, in the background.

```
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

**The recovery algorithm essentially everyone implements** (Mohan et al., 1992). **Three phases after a crash:**

**1. Analysis** — scan forward from the last checkpoint. Determine which transactions were in flight and which pages were dirty.

**2. Redo** — **repeat history.** Replay *every* logged change since the checkpoint, including those from transactions that will be rolled back. **This restores the exact state at the moment of the crash.**

**3. Undo** — roll back the transactions that hadn't committed, writing **compensation log records** as it goes.

> **"Repeat history, then undo" is the counterintuitive part.** Why redo work you're about to undo? **Because it makes recovery restartable.** If you crash *during* recovery, you can start over — the state is always well-defined, and compensation records mean undo is itself idempotent. **That's what makes ARIES robust rather than merely correct on the happy path.**

## Checkpoints

**A checkpoint writes all dirty buffer pages to disk and records the position in the log.**

**It bounds recovery time** — you only replay from the last checkpoint, not from the beginning of time.

**The trade:**

**Frequent checkpoints** → fast recovery, **more I/O during normal operation**, and I/O spikes that hurt latency.

**Infrequent checkpoints** → less steady-state I/O, **long recovery** after a crash.

**Postgres spreads checkpoint writes over time** (`checkpoint_completion_target`, now 0.9 by default) rather than dumping them at once, precisely to avoid the latency spike. **A checkpoint storm — where the write burst stalls foreground queries — is a classic symptom of this being tuned wrong**, and `log_checkpoints = on` is how you see it.

**Full-page writes:** after a checkpoint, the first modification to each page logs the **entire page**, not just the delta. **This protects against torn pages**, and it's why WAL volume spikes right after a checkpoint. Disabling it is only safe on filesystems with atomic page writes (ZFS, or hardware with battery-backed cache).

## fsync, and the ways it lies

**`fsync()` is the system call that makes durability real** — and there are more layers of caching between your write and the platter than people expect.

```
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

**Put the WAL on its own fast device** if you can. It's sequential and latency-critical; keeping it off the same spindles as random data I/O helps.

**Size `max_wal_size` generously.** Too small forces frequent checkpoints and constant full-page writes.

**Monitor WAL generation rate** — a sudden spike means either a write burst or something pathological (an unvacuumed table, a runaway update).

**Never disable full-page writes** unless you genuinely have atomic page writes.

**Never disable fsync in production.** `fsync = off` exists for bulk-loading a database you can rebuild, and nothing else. **The message in the docs is not being cautious for the sake of it.**

**Watch for archive failures.** If `archive_command` starts failing, WAL accumulates until the disk fills — **and a full WAL disk stops the database.**

**Test recovery, including wraparound and disk-full scenarios**, before they happen at 3am.

---

## Related
- [[databases/09-mvcc-and-concurrency-control|MVCC]] — what the log is protecting
- [[databases/11-replication-and-scaling|Replication and Scaling]] — the same WAL, shipped elsewhere
- [[architecture/04-distributed-systems/12-the-log-and-state-machines|The Log and State Machines]] — the same idea, generalised
- [[databases/README|Databases map]]
