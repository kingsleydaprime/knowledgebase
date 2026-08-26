# Build Your Own Database

**[Advanced]** — The one that makes you stop fearing databases. Pages, a B-tree, a SQL subset, and a write-ahead log — after which "how does Postgres do it" has an answer rather than a shrug.

## What you're building

A single-file, embedded, SQLite-shaped database: a pager over a file, a B-tree index, a subset of SQL, and crash-safe transactions via a WAL.

By the end, **killing the process mid-write and reopening leaves your data intact.** That's the hook, and it's a genuinely satisfying thing to demonstrate.

**What you're deliberately not building:** a client/server protocol, a query optimiser (you'll execute plans, not choose between them), joins beyond nested-loop, MVCC, or replication.

**Why this one:** it's the build where the abstraction gap is widest. Everyone uses a database; almost nobody knows that "durable" means a specific `fsync` at a specific moment.

## What you need first

| You should know | Where |
|---|---|
| **`fsync` and the durability boundary** | [[foundations/os/07-filesystems-and-storage\|os/07]] — **the load-bearing prerequisite** |
| **B-trees and how they differ from BSTs** | [[foundations/dsa/04-data-structures/05-trees/01-trees\|trees]] |
| **Parsing** — you're writing a SQL parser | [[foundations/compilers/03-parsing\|compilers/03]] |
| **SQL semantics** | [[databases/sql-reference\|sql-reference]] |
| **Transactions and isolation** | [[architecture/04-distributed-systems/10-distributed-transactions\|transactions]] |

**Do [[build-your-own-shit/04-your-own-language|the language guide]] first if you can** — the SQL parser is the same recursive-descent machinery, and you'll move much faster having done it once.

## The build order

### 1. The pager

Everything sits on this. The file is an array of fixed-size **pages** (4KB is conventional — it matches the OS page size and typical filesystem blocks).

```
read_page(n)   → seek to n * PAGE_SIZE, read 4096 bytes
write_page(n)  → seek, write
```

Add a small in-memory cache of pages, so repeated access doesn't hit the disk.

**Test:** write a page, read it back. Reopen the file, read it again.

**Watch for:** page 0 conventionally holds the **file header** — magic bytes, format version, page size, and the root page number. Write it on creation, verify it on open, and refuse to open a file that doesn't match. That check will save you when a format change silently corrupts your test database.

### 2. A row format

Serialise a row to bytes and back.

```
[4-byte id][32-byte username][255-byte email]     ← fixed-width, the easy start
```

**Test:** round-trip a row. Write several to a page and read them back.

**Watch for:** start **fixed-width** — it's much simpler and you can add variable-length later. When you do, you need a length prefix per field and a slot directory in the page (an array of offsets at one end, data growing from the other), which is how real databases do it.

Decide byte order and stick to it. Don't `memcpy` a struct to disk — [[languages/04-c/08-structs-unions-and-layout|padding]] makes that non-portable and it will bite you.

### 3. Append-only table, and a REPL

`INSERT` appends a row; `SELECT` scans everything. Parse two hard-coded statement shapes — no real parser yet.

```
db > insert 1 alice alice@example.com
db > select
(1, alice, alice@example.com)
```

**Test:** insert rows, select, restart the process, select again. **The data must survive.**

**You now have a working (terrible) database.** Everything after this makes it fast, correct, or expressive.

### 4. The B-tree

The heart of it. Replace the append-only heap with a B-tree keyed by primary key, so lookups are O(log n) instead of O(n).

**Why a B-tree and not a BST:** each node is one page, holding *many* keys. A tree of depth 3 with 4KB pages indexes millions of rows — so a lookup is 3 disk reads rather than 20. **The branching factor is chosen to match the page size**, and that's the entire insight. → [[foundations/dsa/04-data-structures/05-trees/01-trees|trees]]

```
                  [ 7 | 16 ]                    internal: keys + child pointers
                 /     |     \
        [1|3|5]   [8|11|14]   [18|21]           leaf: keys + rows
```

Build it in stages:
1. A single leaf node holding rows in sorted order
2. **Leaf splitting** when a node fills
3. An internal node, and a root
4. **Internal splitting** and root growth
5. Search descending from the root
6. Deletion and rebalancing — **do this last**, it's the hardest part

**Test:** insert enough rows to force several splits. Select them in order — the output must be sorted. Insert in random order and confirm ordering still holds.

**Watch for:** splitting is the fiddly part, especially the root case (the tree grows in *height*, and the root must keep its page number so the header stays valid). **Deletion with rebalancing is genuinely hard** — many toy databases legitimately skip it or use tombstones instead.

**Write a tree-printer early.** Dumping the structure page by page is the only way to debug a split bug, and you'll use it constantly.

### 5. A SQL parser

Now a real one. Lexer → recursive descent → an AST of statements. → [[foundations/compilers/03-parsing|parsing]]

```sql
SELECT id, name FROM users WHERE age > 21;
INSERT INTO users VALUES (1, 'alice', 30);
CREATE TABLE users (id INT, name TEXT, age INT);
```

**Test:** parse each statement into an AST and print it back. Reject malformed SQL with a useful message and a position.

**Watch for:** SQL's grammar is large — **implement a deliberate subset** and reject the rest clearly. Keywords are case-insensitive; string literals use single quotes with `''` as the escape. Identifiers may be quoted with double quotes.

### 6. Execution

Walk the AST and run it. The clean design is an **iterator (volcano) model**: each node exposes `next()`, and pulling from the top drives the whole pipeline.

```
Projection(id, name)
    └── Filter(age > 21)
            └── SeqScan(users)
```

`next()` on Projection calls Filter, which calls SeqScan until a row passes. **Rows stream through — no intermediate materialisation**, so memory is constant regardless of table size.

**Test:** `SELECT * FROM users WHERE age > 21` returns the right rows.

**Watch for:** this is where a **catalog** becomes necessary — schema metadata (tables, columns, types) stored in the database itself, usually in a reserved table. That's what `sqlite_master` is.

If a `WHERE` clause matches your B-tree key, use an index scan instead of a full scan. **That choice is the beginning of a query planner** — and stopping at "use the index when the predicate matches the key" is a perfectly good place to stop.

### 7. Transactions and the WAL

The milestone that makes it a *database* rather than a file format.

The problem: a crash midway through writing several pages leaves the file inconsistent — a B-tree with a split half-applied is corrupt, not merely stale.

**Write-ahead logging:**

```
1. Write the change to the LOG. fsync the log.        ← now it's durable
2. Then modify the pages in the page cache.
3. Flush pages to the main file later (a "checkpoint").
4. On startup: replay any log entries past the last checkpoint.
```

> **The rule: the log record must reach disk before the corresponding page change.** That ordering is the entire guarantee, and it's what "write-ahead" means.

**Test — the one that matters:**

```bash
# start a transaction inserting 1000 rows
kill -9 <pid>       # mid-write, no cleanup
# restart
# either ALL 1000 rows are there, or NONE. Never 437.
```

**Watch for:**

- **`write()` is not durable.** You must `fsync` the log before applying changes, and it costs milliseconds — which is exactly why databases batch commits (**group commit**) rather than fsyncing per transaction. → [[foundations/os/07-filesystems-and-storage|fsync]]
- **Checksum your log records**, or a torn write (a partial page from a power cut) gets replayed as valid garbage
- **`fsync` the directory too** after creating the log file, or the file's *name* may not survive

This milestone is where the [[foundations/os/07-filesystems-and-storage|filesystems note]] stops being theory.

### 8. Extras, in order of value

**Isolation** — start with one writer at a time (SQLite's default, and honest). MVCC is a large step up.

**Joins** — nested-loop first (correct, O(n·m)), then hash join.

**Aggregates** — `COUNT`, `SUM`, `GROUP BY`.

**Secondary indexes** — another B-tree keyed by a non-primary column, whose values are primary keys.

**A query planner** — estimate costs and choose between scan strategies. A genuinely deep topic.

## The other design: LSM trees

Worth knowing that B-trees aren't the only answer.

| | B-tree | LSM tree |
|---|---|---|
| Writes | update in place — random I/O | **append to a sorted memtable, flush sequentially** |
| Write throughput | lower | **much higher** |
| Reads | one path down the tree | **check several levels** — slower |
| Space | fragmentation | compaction overhead, temporary duplication |
| Used by | SQLite, Postgres, MySQL/InnoDB | **RocksDB, LevelDB, Cassandra, ScyllaDB** |

An LSM is arguably **easier to build**: writes go to an in-memory sorted map plus a WAL; when it fills, flush it to an immutable sorted file (SSTable); background compaction merges files. There's no in-place update, so no split logic and no rebalancing.

**If the B-tree's split/merge code is defeating you, an LSM is a legitimate and equally instructive alternative** — and it's what most new storage engines choose. → [[architecture/02-building-blocks/03-databases-at-scale|databases at scale]]

## Per-language toolkit

| Milestone | C | C++ | Rust | Go | Python | JS/Node |
|---|---|---|---|---|---|---|
| **File I/O** | `open`/`pread`/`pwrite` | `fstream` | `File`, `seek_read` | `os.File.ReadAt` | `os.pread` | `fs.read` |
| **fsync** | `fsync` | `fsync` | `sync_all()` | `f.Sync()` | `os.fsync` | `fs.fsyncSync` |
| **Serialisation** | by hand | by hand | `bincode`, or by hand | `encoding/binary` | `struct` | `Buffer` |
| **Page cache** | by hand | `unordered_map` | `HashMap` | `map` | `dict` | `Map` |
| **SQL parse** | by hand | by hand | by hand; `nom` | by hand | by hand | by hand |
| **B-tree** | by hand | by hand | by hand | by hand | by hand | by hand |

**The B-tree is by hand everywhere — that's the project.** Don't use a library.

**Language notes:**

**C** — what `sqlite` is, and the byte-level page manipulation is the most direct. The [*Let's Build a Simple Database*](https://cstack.github.io/db_tutorial/) tutorial is in C and follows almost exactly this milestone order.

**Rust** — a genuinely good fit. Page borrows and lifetimes map onto the real invariants, and the enum-based AST helps the parser. Fighting the borrow checker over the page cache is instructive rather than annoying — it's asking the right questions about aliasing. → [[languages/03-rust/README|Rust]]

**Go** — clean file I/O, and `encoding/binary` handles serialisation. Good balance.

**Python** — fastest to a working prototype; use `struct` and `os.pread`/`os.pwrite`. Slow, and the concepts land identically.

## The parts that will bite you

**`write()` is not `fsync()`.** The single most important thing in this guide.

**Torn writes.** A 4KB page write is not atomic across a power cut. Checksums detect it; the WAL lets you recover.

**B-tree splitting, especially the root.** The tree grows upward, and the root must retain its page number.

**Deletion and rebalancing.** Genuinely hard. Tombstones are a legitimate simplification.

**Struct padding.** Never write a struct's memory directly to disk. Serialise field by field.

**Off-by-one in page arithmetic.** Page N starts at `N * PAGE_SIZE`. Getting this wrong corrupts the file in ways that look like B-tree bugs — write a tree validator that checks structural invariants after every operation.

**Cursor invalidation.** A page split moves rows, so an iterator holding a position must handle it — the same class of bug as [[languages/05-cpp/09-the-stl-containers|iterator invalidation]].

**Endianness**, if the file should be portable.

## How to know it works

**Crash testing is the real test:**

```bash
./mydb test.db < inserts.sql &
sleep 0.5 && kill -9 $!
./mydb test.db "SELECT COUNT(*) FROM users"    # a consistent count, never a corrupt file
```

Do it in a loop, killing at random points. **If any run leaves an unopenable file, your WAL is wrong.**

**Compare against SQLite** for the same SQL — same schema, same inserts, same queries, diff the output. It's the reference implementation and it's in every OS.

```bash
sqlite3 ref.db < script.sql > expected.txt
./mydb my.db  < script.sql > actual.txt
diff expected.txt actual.txt
```

**A B-tree validator** that walks the structure asserting the invariants (keys sorted, children within parent bounds, all leaves at the same depth) and runs after every insert in tests. It converts "the data looks wrong" into "the split at page 47 broke this invariant".

**Property-based testing** fits this unusually well: insert N random keys, assert that a scan returns exactly those keys in sorted order.

## Where to stop

**Stop after the WAL.** You'll have learned:

- Why databases use pages, and why the size matches the OS page
- Why B-trees rather than binary trees — branching factor versus disk reads
- That "durable" means a specific `fsync` at a specific moment, and what it costs
- Why a WAL exists, and why the ordering is the guarantee
- What a query plan is, and that a `SELECT` is a pipeline of iterators
- Why an index makes reads fast and writes slower

**Real databases additionally have:** a cost-based optimiser with statistics, MVCC and full isolation levels, concurrent B-tree access with latch coupling, replication, backup and point-in-time recovery, a wire protocol, connection pooling, and decades of correctness work. Jepsen exists because getting this right is hard even for well-funded teams. → [[architecture/04-distributed-systems/15-testing-distributed-systems|Testing Distributed Systems]]

**If you want to go further:** implement **MVCC** (each row gets version metadata; readers see a consistent snapshot without blocking writers — it's how Postgres achieves its isolation), or build the **LSM** variant and benchmark the write throughput difference against your B-tree. Both are genuinely illuminating.

---

## Related
- [[databases/README|Databases]] — the internals course: pages, B-trees, LSM, WAL, MVCC. **Read notes 03–05 and 10 before milestone 3**
- [[foundations/os/07-filesystems-and-storage|Filesystems and Storage]] — `fsync`, the page cache, journaling
- [[foundations/dsa/04-data-structures/05-trees/01-trees|Trees]] — the B-tree's ancestry
- [[databases/database-design-reference|Database Design]] · [[databases/sql-reference|SQL Reference]]
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — B-tree vs LSM in production
- [[build-your-own-shit/README|build-your-own-shit]]
