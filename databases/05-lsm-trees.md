---
id: b45188af-4f1f-4b8a-9785-b2cc804658de
---

# LSM Trees

An LSM tree is a way of storing data that is built for writing a lot of data very fast. New writes are collected in memory and saved to disk in sorted batches, instead of changing the file in place each time. Systems that take in huge numbers of writes, like message logs and chat apps, often use it.

## The problem with B-trees on writes
<!-- bite: 4182f5eb-9a69-453b-a87d-c37d89d6ce03 -->

**A B-tree update is a random write.** Find the leaf, modify it in place, mark the page dirty, eventually write 8 KB back to disk.

**The costs:**

**Random I/O.** Catastrophic on spinning disks, and still meaningful on SSDs.

**Write amplification.** Changing 20 bytes writes an entire 8 KB page — **400× amplification**, plus the WAL record, plus a full-page image after a checkpoint.

**Page splits** cause fragmentation and extra writes under random-key insert patterns.

**On SSDs there's a further layer:** flash can't overwrite in place, so the FTL does its own garbage collection. **Database write amplification multiplies with device write amplification**, and it wears the drive.

## The LSM idea
<!-- bite: dd076a2f-09b9-49b0-906c-ad3b482d0291 -->

> **Never update in place. Only ever append, and sort later.**

```text
       WRITES
         │
         ▼
  ┌─────────────┐   in memory, sorted (skiplist / red-black tree)
  │  MEMTABLE   │   ← writes go here, plus a WAL record for durability
  └──────┬──────┘
         │ flush when full — ONE SEQUENTIAL WRITE
         ▼
  ┌─────────────┐
  │ L0: SSTable SSTable SSTable          │  overlapping key ranges
  ├─────────────┤
  │ L1: [SSTable][SSTable][SSTable]      │  non-overlapping, sorted
  ├─────────────┤
  │ L2: ... 10× larger                   │
  └─────────────┘
         ▲
    COMPACTION merges levels in the background
```

**A write:** append to the WAL (sequential), insert into the in-memory memtable. **Done.** No disk seek, no page read.

**When the memtable fills**, it's frozen and flushed as a new **SSTable** — a sorted, immutable file. **One large sequential write.**

**Compaction** merges SSTables in the background, discarding overwritten and deleted keys.

**Deletes write a tombstone** — a marker saying "this key is gone" — because you can't modify an immutable file. **The tombstone must survive until every older copy of the key has been compacted away**, which is why deletes in an LSM don't free space immediately, and why a delete-heavy workload can grow.

## Reads are the price
<!-- bite: aa2eab9f-8b90-445c-914a-da86f5c0a7c7 -->

**A read must check the memtable, then potentially every SSTable, newest first.**

**Three optimisations make this viable:**

**Bloom filters.** A small probabilistic structure per SSTable answering "is this key definitely absent?" **No false negatives, some false positives** — so a negative answer lets you skip the file entirely without reading it. **This is what makes LSM point lookups practical**, typically eliminating 99%+ of unnecessary file reads. → [[mathematics/02-discrete-math/06-combinatorics-and-counting|The probability behind it]]

**Sparse indexes and block caches** — each SSTable has an index of block offsets, so you binary-search within a file.

**Levelled compaction** keeps SSTables within a level **non-overlapping**, so a key can be in at most one file per level. **Bounded read amplification: one file per level.**

**Range scans remain harder than in a B-tree** — you must merge iterators across every level, so it's a $k$-way merge rather than a leaf-chain walk.

## The RUM conjecture
<!-- bite: 6f8aa2ce-cdf6-4fa4-b244-01955788b9be -->

**The framing that explains the whole trade:**

> **You can optimise for at most two of Read, Update, and Memory. Improving one costs you another.**

| | **B-tree** | **LSM tree** |
|---|---|---|
| **Read amplification** | **low** — ~3 page reads | higher — several levels |
| **Write amplification** | **high** — full page per change | **low** at write time, deferred to compaction |
| **Space amplification** | ~1.3× (fragmentation) | **higher** — obsolete versions until compacted |
| **Write pattern** | random | **sequential** |
| **Range scans** | **excellent** — linked leaves | good, needs merging |
| **Predictable latency** | **yes** | **no — compaction stalls** |

**LSM total write amplification is often 10–30×** once compaction is counted — sometimes worse than a B-tree in total bytes written. **The win is that those writes are sequential and off the critical path**, so the user-visible write latency is low.

**Compaction strategies trade differently:**

**Levelled** (RocksDB default) — low read and space amplification, **high write amplification**.

**Size-tiered** (Cassandra default) — **low write amplification**, higher read and space amplification. Can temporarily need 2× the disk during a major compaction.

**Which is why Cassandra recommends keeping disks half empty**, a detail that surprises operators.

## Where each is used
<!-- bite: 2587322b-5999-4e30-9ea4-61907394ab18 -->

**B-tree:** Postgres, MySQL/InnoDB, SQLite, SQL Server, Oracle. **Every traditional relational database.**

**LSM:** RocksDB and LevelDB (the embedded engines under a lot of things), Cassandra, ScyllaDB, HBase, MongoDB's WiredTiger (optionally), CockroachDB and TiDB (both on RocksDB/Pebble), ClickHouse's MergeTree, and Kafka's log is LSM-shaped.

**MyRocks** is MySQL on RocksDB — Facebook deployed it for the space saving, reporting roughly half the storage of InnoDB on their workload.

> **The pattern: LSM dominates where writes are heavy and the workload is known** — time series, event logs, metrics, message queues, and the storage layer of distributed databases. **B-trees dominate where reads are varied, latency must be predictable, and range scans matter.**

## The operational reality
<!-- bite: dbcc7bf8-fc14-43bc-8504-d905e9495023 -->

**LSM's genuine downside is that compaction is a background job competing with your foreground traffic.**

**Compaction stalls** — if writes arrive faster than compaction keeps up, L0 accumulates files, read amplification climbs, and eventually the database **throttles or blocks writes.** This is a well-known Cassandra and RocksDB operational problem.

**Latency is bimodal.** p50 excellent, p99 much worse, because a request can land during a compaction I/O burst. **A B-tree's latency distribution is far tighter**, which matters for latency-sensitive services. → [[computer-architecture/12-performance|Tail latency]]

**Tuning surface is large** — level sizes, compaction triggers, bloom filter bits, block cache, write buffer count. **RocksDB in particular has a reputation for needing an expert**, and its own documentation says so.

**Space can spike** during major compactions.

## Which to choose
<!-- bite: 14fdd729-0c01-4aa6-8d23-432c6b391c78 -->

**Use a B-tree (i.e. a normal relational database) unless you have a specific reason not to.** Predictable latency, mature tooling, and read flexibility are worth a lot.

**Consider LSM when:**

- **Write throughput is the binding constraint** and you've measured it
- **The workload is append-heavy** — events, logs, metrics, time series
- **Reads are mostly by key or by recent range**, not ad-hoc
- **Space matters** and your data compresses well (sorted immutable files compress excellently)

**And note you often don't choose directly** — you choose Cassandra or CockroachDB or ClickHouse, and the storage engine comes with it. **Knowing which you're on explains the operational behaviour you'll see**, which is the practical value of this note.

**The hybrid worth knowing:** several modern engines blur the line. **Bw-trees** are latch-free B-trees with delta records; **fractal trees** (TokuDB) buffer messages in internal nodes to amortise writes. Neither is mainstream, but they show the design space isn't binary.

---

## Check your understanding
<!-- bite: a2ae903d-7dc4-40c3-b92e-8a62a3ea4841 -->

Try each one before you open the answer.

1. <!-- q: exact id="12ed0a3c" answer="200" -->
   A B-tree changes a 40-byte value in place, and the page size is 8 KB (8,000 bytes, to keep the numbers round). What is the write amplification for that one change, counting only the page write?

   <details><summary>Answer</summary>

   200×. 8,000 / 40 = 200 bytes written per byte changed. The WAL record and any full-page image add more on top.

   </details>

2. <!-- q: gap id="d460c860" answers="memtable;SSTable|sstable|sorted string table" -->
   In an LSM tree a write goes to the WAL and then into the in-memory ___. When that fills, it is flushed to disk as a sorted, immutable file called an ___.

   <details><summary>Answer</summary>

   Memtable, then SSTable. The flush is one large sequential write, which is why LSM writes are fast.

   </details>

3. <!-- q: mcq id="7199beed" -->
   An LSM read for key 42 asks an SSTable's Bloom filter, and the filter says "not present". What can the reader do?

   - [x] Skip that file completely, because a Bloom filter never gives a false "not present"
   - [ ] Read the file anyway, because the filter might be wrong
   - [ ] Stop the whole search; the key doesn't exist anywhere
   - [ ] Rebuild the filter first

   <details><summary>Answer</summary>

   Skip the file. Bloom filters have no false negatives, only some false positives. "Absent" is certain for that one file, but the key might still be in another SSTable or the memtable.

   </details>

4. <!-- q: open id="2f5a4d42" -->
   A user deletes a million rows from a Cassandra table, and the disk usage goes up instead of down. Why?

   <details><summary>Answer</summary>

   SSTables are immutable, so a delete writes a tombstone, a marker saying the key is gone. Space only comes back when compaction merges the files and every older copy of each key has been removed, and the tombstones must be kept until then. Until compaction catches up, you have the old data plus a million tombstones.

   </details>

5. <!-- q: mcq id="37a3f2ee" -->
   A payments service needs very predictable latency, with p99 close to p50, and runs many different range queries. Which storage engine suits it?

   - [x] A B-tree, as in Postgres or MySQL
   - [ ] An LSM tree, as in Cassandra
   - [ ] Either; they behave the same
   - [ ] A Bloom filter

   <details><summary>Answer</summary>

   A B-tree. Its latency distribution is tight and its linked leaves make range scans cheap. LSM latency is bimodal, because a request can land during a compaction burst.

   </details>

6. <!-- q: mcq id="3ff497a9" -->
   Which workloads suit an LSM tree? Choose all that apply.

   - [x] Ingesting millions of metric points per minute
   - [x] An append-only event log read mostly by key or recent time range
   - [ ] A banking ledger with many ad-hoc reports and strict p99 targets
   - [ ] A small admin app with a few hundred writes a day

   <details><summary>Answer</summary>

   The metrics and the event log: write-heavy, append-shaped and read in known ways. The other two are better served by an ordinary B-tree database.

   </details>

## Related
<!-- bite: f5d90fff-fb8e-4e58-a0be-87e250c7f777 -->
- [[databases/04-b-trees-and-indexes/index|B-Trees and Indexes]] — the read-optimised alternative
- [[databases/03-storage-and-page-layout|Storage and Page Layout]] — pages and the buffer pool
- [[build-your-own-shit/06-your-own-database|build-your-own-database]] — which offers LSM as the easier storage engine to build
- [[databases/index|Databases map]]

## About this lesson
<!-- bite: ca3e26a3-a0f2-4b59-baaa-4333744eaea9 -->

**Level:** Advanced. **Covers:** The write-optimised alternative to B-trees, and the amplification trade that decides between them.
