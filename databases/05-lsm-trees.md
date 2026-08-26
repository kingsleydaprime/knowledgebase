# LSM Trees

**[Advanced]** — The write-optimised alternative to B-trees, and the amplification trade that decides between them.

## The problem with B-trees on writes

**A B-tree update is a random write.** Find the leaf, modify it in place, mark the page dirty, eventually write 8 KB back to disk.

**The costs:**

**Random I/O.** Catastrophic on spinning disks, and still meaningful on SSDs.

**Write amplification.** Changing 20 bytes writes an entire 8 KB page — **400× amplification**, plus the WAL record, plus a full-page image after a checkpoint.

**Page splits** cause fragmentation and extra writes under random-key insert patterns.

**On SSDs there's a further layer:** flash can't overwrite in place, so the FTL does its own garbage collection. **Database write amplification multiplies with device write amplification**, and it wears the drive.

## The LSM idea

> **Never update in place. Only ever append, and sort later.**

```
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

**A read must check the memtable, then potentially every SSTable, newest first.**

**Three optimisations make this viable:**

**Bloom filters.** A small probabilistic structure per SSTable answering "is this key definitely absent?" **No false negatives, some false positives** — so a negative answer lets you skip the file entirely without reading it. **This is what makes LSM point lookups practical**, typically eliminating 99%+ of unnecessary file reads. → [[foundations/discrete-math/06-combinatorics-and-counting|The probability behind it]]

**Sparse indexes and block caches** — each SSTable has an index of block offsets, so you binary-search within a file.

**Levelled compaction** keeps SSTables within a level **non-overlapping**, so a key can be in at most one file per level. **Bounded read amplification: one file per level.**

**Range scans remain harder than in a B-tree** — you must merge iterators across every level, so it's a $k$-way merge rather than a leaf-chain walk.

## The RUM conjecture

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

**B-tree:** Postgres, MySQL/InnoDB, SQLite, SQL Server, Oracle. **Every traditional relational database.**

**LSM:** RocksDB and LevelDB (the embedded engines under a lot of things), Cassandra, ScyllaDB, HBase, MongoDB's WiredTiger (optionally), CockroachDB and TiDB (both on RocksDB/Pebble), ClickHouse's MergeTree, and Kafka's log is LSM-shaped.

**MyRocks** is MySQL on RocksDB — Facebook deployed it for the space saving, reporting roughly half the storage of InnoDB on their workload.

> **The pattern: LSM dominates where writes are heavy and the workload is known** — time series, event logs, metrics, message queues, and the storage layer of distributed databases. **B-trees dominate where reads are varied, latency must be predictable, and range scans matter.**

## The operational reality

**LSM's genuine downside is that compaction is a background job competing with your foreground traffic.**

**Compaction stalls** — if writes arrive faster than compaction keeps up, L0 accumulates files, read amplification climbs, and eventually the database **throttles or blocks writes.** This is a well-known Cassandra and RocksDB operational problem.

**Latency is bimodal.** p50 excellent, p99 much worse, because a request can land during a compaction I/O burst. **A B-tree's latency distribution is far tighter**, which matters for latency-sensitive services. → [[foundations/computer-architecture/12-performance|Tail latency]]

**Tuning surface is large** — level sizes, compaction triggers, bloom filter bits, block cache, write buffer count. **RocksDB in particular has a reputation for needing an expert**, and its own documentation says so.

**Space can spike** during major compactions.

## Which to choose

**Use a B-tree (i.e. a normal relational database) unless you have a specific reason not to.** Predictable latency, mature tooling, and read flexibility are worth a lot.

**Consider LSM when:**

- **Write throughput is the binding constraint** and you've measured it
- **The workload is append-heavy** — events, logs, metrics, time series
- **Reads are mostly by key or by recent range**, not ad-hoc
- **Space matters** and your data compresses well (sorted immutable files compress excellently)

**And note you often don't choose directly** — you choose Cassandra or CockroachDB or ClickHouse, and the storage engine comes with it. **Knowing which you're on explains the operational behaviour you'll see**, which is the practical value of this note.

**The hybrid worth knowing:** several modern engines blur the line. **Bw-trees** are latch-free B-trees with delta records; **fractal trees** (TokuDB) buffer messages in internal nodes to amortise writes. Neither is mainstream, but they show the design space isn't binary.

---

## Related
- [[databases/04-b-trees-and-indexes|B-Trees and Indexes]] — the read-optimised alternative
- [[databases/03-storage-and-page-layout|Storage and Page Layout]] — pages and the buffer pool
- [[build-your-own-shit/06-your-own-database|build-your-own-database]] — which offers LSM as the easier storage engine to build
- [[databases/README|Databases map]]
