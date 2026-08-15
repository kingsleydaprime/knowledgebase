# Storage and Page Layout

**[Intermediate → Advanced]** — Pages, the buffer pool, row versus column layout, and why the disk block size shapes everything above it.

## Everything is pages

**The database does not read rows from disk. It reads pages.**

**A page is a fixed-size block** — 8 KB in Postgres, 16 KB in InnoDB, 4 KB in SQLite by default. **It is the unit of I/O, of caching, and of locking in some engines.**

**Why a fixed size:**

**Disks work in blocks.** Reading 100 bytes and reading 4 KB cost about the same on an SSD, and on a spinning disk the seek dominates entirely. **So read a useful amount at once.** → [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]]

**Fixed size makes memory management tractable** — the buffer pool is an array of identical slots, so no fragmentation and no variable-size allocation.

**It gives you an addressing scheme.** A row is identified by (page number, slot number), which is exactly what Postgres's `ctid` is.

## Inside a page

**The slotted page layout**, used by essentially every row-oriented database:

```
 ┌──────────────────────────────────────────┐
 │ HEADER  (checksum, LSN, free space ptrs) │
 ├──────────────────────────────────────────┤
 │ slot0│slot1│slot2│ ...  →                │  slot array grows down
 ├──────────────────────────────────────────┤
 │                                          │
 │            FREE SPACE                    │
 │                                          │
 ├──────────────────────────────────────────┤
 │              ← tuple2 │ tuple1 │ tuple0  │  tuples grow up
 └──────────────────────────────────────────┘
```

**The slot array grows down from the header; the tuples grow up from the end.** They meet in the middle, and the page is full.

> **Why the indirection through slots?** Because a row can be moved *within* a page — after an update or a compaction — **without changing its identity.** The slot number stays stable, so **indexes pointing at (page, slot) don't need updating** every time a row shifts by a few bytes.
>
> **This is the same trick as a handle table**, and it's the reason a page can defragment itself cheaply.

**Row storage within a tuple:** a header (visibility info, null bitmap), then the fixed-width columns, then the variable-width ones with their lengths. **Column order in storage often differs from your `CREATE TABLE` order** — Postgres reorders to minimise alignment padding, exactly as you would in a C struct. → [[foundations/computer-architecture/02-data-representation|Alignment]]

**Oversized values** don't fit in a page. **Postgres's TOAST** compresses them, and if still too large, splits them into chunks in a side table — so a 100 KB text column doesn't occupy the main tuple. **A consequence worth knowing: `SELECT *` on a table with large TOASTed columns is dramatically more expensive than selecting the columns you need**, because it detoasts everything.

## The buffer pool

**The database's own cache of pages, in its own memory.**

```
 ┌──────────────────────────────────────┐
 │  BUFFER POOL  (shared_buffers)       │
 │  ┌────┐┌────┐┌────┐┌────┐┌────┐     │
 │  │page││page││page││page││page│ ...  │
 │  └────┘└────┘└────┘└────┘└────┘     │
 │   dirty  clean  clean  dirty  pinned │
 └──────────────────────────────────────┘
              ↕ read / write
 ┌──────────────────────────────────────┐
 │              DISK                    │
 └──────────────────────────────────────┘
```

**Every page access goes through it.** Hit → return the in-memory page. Miss → evict something, read from disk, return.

**Page states:**

**Pinned** — in use right now, cannot be evicted. **Dirty** — modified in memory, not yet written to disk. **Clean** — matches disk, evictable for free.

**Eviction** is usually **clock-sweep** or a variant, not true LRU — approximating LRU with a reference bit per page and a rotating hand. **Cheaper than maintaining an LRU list under concurrency**, where the list head becomes a contention point.

**Two critical rules:**

> **A dirty page must not be written to disk before its WAL record.** That's the **write-ahead** rule, and it's what makes crash recovery possible. → [[databases/10-durability-and-recovery|Durability and Recovery]]

**Sequential scans get special handling.** A large scan would otherwise evict your entire working set — **the classic "one analytics query destroyed production latency" failure.** Postgres uses a small ring buffer for big scans so they can't sweep the pool clean.

**Sizing it:**

**Postgres: ~25% of RAM**, because it deliberately relies on the OS page cache as a second tier. Setting it to 80% double-caches and usually performs worse.

**MySQL/InnoDB: 50–80% of RAM**, because InnoDB uses `O_DIRECT` and bypasses the OS cache.

**The two answers differ because the architectures differ** — a genuinely confusing point if you carry advice from one to the other.

**Measure the hit ratio.** Below ~99% on an OLTP workload usually means your working set exceeds the pool.

## Row vs column storage

**The layout decision that defines OLTP versus OLAP.**

```
 ROW STORE (OLTP)                COLUMN STORE (OLAP)
 ┌─────────────────────┐         ┌───────────────────┐
 │ 1│Alice│30│London   │         │ 1│2│3│4│ ...       │  id
 │ 2│Bob  │25│Leeds    │         ├───────────────────┤
 │ 3│Cara │41│Bristol  │         │ Alice│Bob│Cara│…  │  name
 └─────────────────────┘         ├───────────────────┤
  whole row is contiguous        │ 30│25│41│ ...      │  age
                                 └───────────────────┘
                                  each column contiguous
```

**`SELECT * WHERE id = 2`** — row store reads one page. Column store reads from **every** column file and reassembles. **Row store wins.**

**`SELECT AVG(age) FROM users`** — row store reads every page to extract one small column, wasting most of the bandwidth. Column store reads only the age column. **Column store wins, often by 10–100×.**

**Column stores also compress far better**, and this is the underrated half:

- **Run-length encoding** — a sorted status column becomes `(active, 4M), (deleted, 12K)`
- **Dictionary encoding** — countries become small integers
- **Delta encoding** — sorted timestamps stored as differences
- **Bit-packing** — a value range of 0–1000 needs 10 bits, not 32

**Compression ratios of 10× are ordinary**, because a single column is far more homogeneous than a row. **And better compression means less I/O**, which compounds the scan advantage.

**Vectorised execution** is the third multiplier: process a batch of values from one column at a time, which is SIMD-friendly and branch-predictable. **This is why ClickHouse and DuckDB are as fast as they are** — layout, compression and execution model all reinforcing. → [[foundations/computer-architecture/03-instruction-sets|SIMD]]

**Hybrid formats** — Parquet and ORC — use **row groups subdivided by column** (PAX layout). You get columnar compression and scan efficiency while keeping a row group's data local. **The de facto standard for analytical files on object storage.**

## Table organisation

**Heap tables** — rows in no particular order, wherever there's free space. Postgres's only option. **Inserts are cheap** (append to any page with room), **and there's no cheap ordered scan** — you need an index.

**Clustered / index-organised tables** — the table *is* the primary key's B-tree, with rows stored in the leaves. **InnoDB's only option**, and available in SQL Server and Oracle.

| | Heap | Clustered |
|---|---|---|
| Primary key lookup | index → heap fetch (**two steps**) | **one step**, row is in the leaf |
| Range scan on PK | random I/O | **sequential** |
| Secondary index | points to row location | **points to the PK**, then a second lookup |
| Insert order matters? | no | **yes — random keys fragment badly** |

> **This is why InnoDB primary key choice matters so much more than Postgres's.** A random UUID primary key in InnoDB inserts into random pages, causing **page splits and fragmentation across the whole table.** A monotonic key appends to the rightmost page.
>
> **If you need UUIDs in InnoDB, use a time-ordered variant** — UUIDv7, or ULID. **Same uniqueness, sequential prefix.** This is a real, measurable production problem, not a micro-optimisation.

**Fill factor** leaves free space in each page so updates can stay in place rather than moving the row. **Lower it for update-heavy tables**, raise it for read-only ones.

## Free space and fragmentation

**Deleting a row doesn't shrink the file.** It marks space reusable.

**Postgres tracks it in a free space map** and reclaims via `VACUUM`. **The table file only shrinks with `VACUUM FULL`**, which takes an exclusive lock and rewrites the whole table — so it's an outage, not routine maintenance.

**Fragmentation** — pages half-full, rows out of order — degrades scans because you read more pages for the same data. **Rebuilding an index or the table restores density**; `pg_repack` and `pt-online-schema-change` do it without the long lock.

**Bloat is the Postgres-specific version**, caused by MVCC keeping dead row versions until vacuumed. → [[databases/09-mvcc-and-concurrency-control|MVCC]]

## What to actually do

**Choose column types that are as small as correct.** `int` not `bigint` where the range allows; `timestamptz` not text. **Smaller rows mean more rows per page, which means fewer pages read** — the same argument as [[foundations/computer-architecture/08-the-memory-hierarchy|cache lines]], one level down.

**Order columns to minimise padding** in Postgres — fixed-width and largest-alignment first. It can save 10–20% on narrow tables.

**Avoid `SELECT *`**, especially with TOASTed columns.

**Use a monotonic primary key in InnoDB.** UUIDv7 if you need UUIDs.

**Size the buffer pool for your engine**, and check the hit ratio rather than guessing.

**Consider a column store for analytics** rather than adding more indexes to an OLTP table. **DuckDB embedded is often the answer** for analysis over exports, and it costs nothing to try.

**Watch for bloat** — `pg_stat_user_tables`, and `pgstattuple` when you need detail.

---

## Related
- [[databases/04-b-trees-and-indexes|B-Trees and Indexes]] — the structure built on these pages
- [[databases/05-lsm-trees|LSM Trees]] — the write-optimised alternative
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — the same argument, one level down
- [[databases/README|Databases map]]
