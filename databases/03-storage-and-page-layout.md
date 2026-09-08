# Storage and Page Layout

**[Intermediate → Advanced]** — How a database fits variable-sized rows into fixed-sized pages, finds them again after they move, and keeps useful pages in memory. `[reference]`.

## Before you start

You should know what a table, row, and primary key are from [[databases/02-the-relational-model|the relational model]]. For the lab, you need Python 3 and familiarity with lists, tuples, classes, and byte slices. If the code is unfamiliar, take a detour through [[languages/06-python/03-built-in-types-and-collections|Python collections]] and [[languages/06-python/05-classes-and-the-object-model|classes]]. No database server or third-party packages are required.

By the end, you should be able to:

1. Draw a page and calculate whether another row will fit, including its metadata.
2. Explain why moving row bytes does not necessarily change the row's slot number.
3. Implement and test compaction for a small in-memory page.
4. Explain how caching and row/column layout change the amount of data an operation reads.

**Study route:** work through the page trace and lab first. Attempt the compaction exercise before looking at its hints. The engine-specific sections afterwards connect the model to real databases; they are not prerequisites for writing the lab.

## Everything is pages

Suppose you store names in a file, one after another:

```text
AliceBobCara
```

You immediately have two problems. How do you know where one name ends? And if `Bob` changes to `Robert`, where do the extra bytes go without moving everything after it?

A database needs an arrangement that supports finding, changing, caching, and writing records. Many database engines organise that work around a **page**: a fixed-sized chunk of bytes containing records and bookkeeping information.

Think of a page as a storage box. The rows are differently sized items; an inventory card records where each item sits. Rearranging the contents is fine if the inventory stays accurate. The limitation of the analogy: the database counts exact byte positions, not approximate physical locations.

| Term           | Meaning here                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------ |
| Byte offset    | A position counted from the start of the page; the first byte is at offset 0                     |
| Record / tuple | The stored representation of a row, including any row metadata                                   |
| Page header    | Bookkeeping about the page, such as its free-space boundaries                                    |
| Slot           | A small entry giving a record's location; our lab stores an offset and length                    |
| Compaction     | Moving live records together to turn scattered holes into one free region                        |
| Indirection    | Looking up a location through another entry, instead of storing the location directly everywhere |

### Why fixed-sized chunks?

A typical PostgreSQL build uses 8 KiB pages, InnoDB defaults to 16 KiB, and SQLite defaults to 4 KiB. These are database choices, not a rule that database pages must equal disk sectors or operating-system pages.

- Storage and operating systems transfer data in blocks. Fetching a useful chunk can amortise I/O overhead; the exact cost depends on caching, device, and request size.
- A cache can reserve equal-sized frames for pages rather than allocate differently sized space for every row.
- A page number identifies a location in a file; a slot identifies a record within that page.

An SQL query asks for rows, but the storage machinery commonly fetches and caches the pages containing those rows. See [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]] for the same reasoning at the CPU-cache level.

## Inside a page

A common design for variable-length records is a **slotted page**. This is a useful model, not the exact layout of every row-oriented engine.

```text
low byte offsets                                      high byte offsets
+--------+----------------+------------------+---------------------------+
| header | slot directory |    free space    |     record bytes          |
+--------+----------------+------------------+---------------------------+
                         -->              <--
                 slots grow right    records grow left
```

The slot directory and records grow towards one another. Inserting a record needs space for **both the bytes and its slot**.

### Work through a 64-byte page

Our teaching format reserves 8 bytes for the header and 4 bytes per slot. Real formats have different sizes. We write ranges as `[start, end)`: include `start`, exclude `end`, so their length is `end - start`.

Initially, bytes `[8, 64)` are available: `64 - 8 = 56` bytes.

1. Insert `b"Alice"` (5 bytes). Slot 0 occupies `[8, 12)` and points to the record at `[59, 64)`.
2. Insert `b"Bob"` (3 bytes). Slot 1 occupies `[12, 16)` and points to `[56, 59)`.

```text
0        8      12      16                    56    59       64
+--------+-------+-------+---------------------+-----+---------+
| header | slot0 | slot1 | free: 40 bytes      | Bob | Alice   |
+--------+-------+-------+---------------------+-----+---------+
          (59,5) (56,3)
```

To read slot 1, use its entry `(56, 3)` and read three bytes starting at offset 56. The caller needs the slot number, not the byte offset.

Now delete Alice by marking slot 0 unused. Bob stays where it is. There are 45 unused payload-space bytes in total, but only 40 in the central free region; the other 5 form a hole at the end.

Compaction moves Bob from `[56, 59)` to `[61, 64)` and changes **slot 1's offset** from 56 to 61. Slot 1 remains slot 1. Slot 0 remains deleted.

| State          | Slot 0    | Slot 1    | Directory end | Record-region start | Contiguous free bytes |
| -------------- | --------- | --------- | ------------: | ------------------: | --------------------: |
| Empty          | —         | —         |             8 |                  64 |                    56 |
| Alice inserted | `(59, 5)` | —         |            12 |                  59 |                    47 |
| Bob inserted   | `(59, 5)` | `(56, 3)` |            16 |                  56 |                    40 |
| Alice deleted  | deleted   | `(56, 3)` |            16 |                  56 |                    40 |
| Compacted      | deleted   | `(61, 3)` |            16 |                  61 |                    45 |

**Pause and predict:** after compaction, will a 42-byte record fit in a new slot? No: it needs `42 + 4 = 46` bytes, but only 45 are free.

This is why slots are useful: references to a surviving slot need not change just because its bytes move within the page. It does **not** mean physical identifiers are permanent database keys. PostgreSQL's `ctid` identifies a row version by block and item position; updates and table rewrites can change it. Use a logical key for application identity.

### What real tuples add

Real rows also need information such as null markers, field lengths, and transaction visibility. A page header may carry a checksum and an **LSN** (log sequence number: a position in the recovery log). You do not need those to understand slot indirection; [[databases/09-mvcc-and-concurrency-control|MVCC]] and [[databases/10-durability-and-recovery|recovery]] explain why they are needed.

PostgreSQL does **not** automatically reorder your columns to minimise padding. Field alignment and declared column order can affect row size; the exact layout also depends on nulls and variable-width values. See [[foundations/computer-architecture/02-data-representation|data representation]] for alignment. Measure before redesigning a schema for a possible space saving.

Oversized values need another strategy. PostgreSQL's **TOAST** mechanism can compress eligible values and/or store them out of line in chunks. Retrieving large values may require extra reads and decompression, so select the columns you need rather than routinely returning every large field.

## Lab — build the page before building the database

**Runnable example:** save this block as `page_lab.py` in a scratch directory and run `python3 page_lab.py`. It uses only memory; it does not read or modify a database.

This is deliberately a model: header and slot bytes are reserved in the capacity calculation, but their actual values live in Python attributes. It is **not a serialised database page**. Dumping `data` to a file would lose the metadata needed to read it back.

```python
class SlottedPage:
    HEADER_SIZE = 8
    SLOT_SIZE = 4

    def __init__(self, size=64):
        if size < self.HEADER_SIZE:
            raise ValueError("page is smaller than its header")
        self.data = bytearray(size)
        self.slots = []
        self.free_end = size

    @property
    def free_start(self):
        return self.HEADER_SIZE + self.SLOT_SIZE * len(self.slots)

    @property
    def free_bytes(self):
        return self.free_end - self.free_start

    def insert(self, payload):
        if not isinstance(payload, bytes) or not payload:
            raise ValueError("payload must be non-empty bytes")
        needed = self.SLOT_SIZE + len(payload)
        if needed > self.free_bytes:
            raise ValueError("page full: need a slot as well as record bytes")

        offset = self.free_end - len(payload)
        self.data[offset:self.free_end] = payload
        self.slots.append((offset, len(payload)))
        self.free_end = offset
        return len(self.slots) - 1

    def read(self, slot_id):
        if not 0 <= slot_id < len(self.slots):
            raise KeyError(slot_id)
        entry = self.slots[slot_id]
        if entry is None:
            raise KeyError(slot_id)
        offset, length = entry
        return bytes(self.data[offset:offset + length])

    def delete(self, slot_id):
        self.read(slot_id)  # Validate before changing the directory.
        self.slots[slot_id] = None


if __name__ == "__main__":
    page = SlottedPage()
    alice = page.insert(b"Alice")
    bob = page.insert(b"Bob")
    assert (alice, bob) == (0, 1)
    assert page.slots == [(59, 5), (56, 3)]
    assert page.free_bytes == 40
    assert page.read(bob) == b"Bob"

    page.delete(alice)
    assert page.free_bytes == 40
    assert page.read(bob) == b"Bob"
    print("page_lab: insert, read and delete checks passed")
```

Expected output:

```text
page_lab: insert, read and delete checks passed
```

### Connect the implementation to the picture

- `free_start` is derived from the number of slots, including deleted ones. This model never reuses or renumbers a slot.
- `free_end` is the left edge of the record region. Insertion subtracts the payload length to grow that region leftwards.
- The capacity check happens **before mutation**. A failed insertion must leave existing records readable and boundaries unchanged.
- `read` follows the slot entry. It does not assume that records are stored in slot order.
- `delete` removes the reference, not the bytes. It creates a hole but does not move the free-space boundary. Deleting is not secure erasure.

The model's invariants—facts that every operation must preserve—are:

```text
HEADER_SIZE <= free_start <= free_end <= len(data)
Every live slot points to its own valid, non-overlapping record range.
A surviving record keeps its slot ID even if its bytes move.
```

### Guided change: observe fragmentation

Add a third record, `b"Cara"`, after deleting Alice but before compaction. Predict its slot, byte offset, and remaining contiguous space before running your change.

You should obtain slot 2 at offset 52 and 32 contiguous free bytes. Alice's five-byte hole is still unusable by this simple insertion routine. Sketch the page to explain where the other unused bytes are.

### Independent implementation: `compact()`

Close the worked implementation after studying it. First reconstruct `insert` and `read` from the diagram. Then reopen your own file and add a `compact(self)` method using this contract:

- Keep every live record's bytes and slot ID unchanged.
- Keep deleted entries as `None`; do not shorten or reorder the slot directory.
- Pack live records against the end of the page and update their slot offsets.
- Set `free_end` so all reclaimed payload space is in the central free region.
- Leave `free_start` unchanged. Compacting twice must preserve records and free-space size.
- Empty pages and pages whose records have all been deleted must work.

Packing order is your choice. Aim for a clear implementation using temporary storage, not in-place byte juggling. This lab has no concurrency, transactions, automatic compaction, slot reuse, or durability; do not add them yet.

**Exercise checks:** save this separate block as `test_page_lab.py` alongside your implementation, then run `python3 test_page_lab.py`. It requires your new method; the worked example alone is not expected to pass it.

```python
from page_lab import SlottedPage


def expect_error(error, action):
    try:
        action()
    except error:
        return
    raise AssertionError(f"expected {error.__name__}")


def check_layout(page):
    assert page.HEADER_SIZE <= page.free_start <= page.free_end <= len(page.data)
    occupied = set()
    for entry in page.slots:
        if entry is None:
            continue
        offset, length = entry
        assert page.free_end <= offset < offset + length <= len(page.data)
        positions = set(range(offset, offset + length))
        assert not occupied.intersection(positions)
        occupied.update(positions)
    assert len(occupied) == len(page.data) - page.free_end


page = SlottedPage()
alice = page.insert(b"Alice")
bob = page.insert(b"Bob")
page.delete(alice)
page.compact()
assert page.slots[alice] is None
assert page.read(bob) == b"Bob"
assert page.free_start == 16
assert page.free_end == 61
assert page.free_bytes == 45
expect_error(KeyError, lambda: page.read(alice))
expect_error(KeyError, lambda: page.read(-1))
expect_error(KeyError, lambda: page.read(99))
check_layout(page)

before = (bytes(page.data), list(page.slots), page.free_end)
expect_error(ValueError, lambda: page.insert(b"x" * 42))
assert (bytes(page.data), page.slots, page.free_end) == before

large = page.insert(b"x" * 41)
assert large == 2
assert page.free_bytes == 0
assert page.read(bob) == b"Bob"
assert page.read(large) == b"x" * 41
page.compact()
assert page.free_bytes == 0
assert page.read(bob) == b"Bob"
assert page.read(large) == b"x" * 41
check_layout(page)

for slot_id in (bob, large):
    page.delete(slot_id)
page.compact()
assert page.slots == [None, None, None]
assert page.free_end == 64
assert page.free_bytes == 44  # The three directory entries still occupy space.
check_layout(page)

empty = SlottedPage()
empty.compact()
assert empty.free_bytes == 56
check_layout(empty)

mixed = SlottedPage(96)
ids = [mixed.insert(value) for value in (b"a", b"bravo", b"cc", b"delta")]
mixed.delete(ids[1])
for _ in range(2):
    mixed.compact()
    assert [mixed.read(ids[i]) for i in (0, 2, 3)] == [b"a", b"cc", b"delta"]
    assert mixed.slots[ids[1]] is None
    assert mixed.free_bytes == 64  # 96 - header 8 - slots 16 - live bytes 8.
    check_layout(mixed)

print("test_page_lab: compaction checks passed")
```

Expected output after a correct implementation: `test_page_lab: compaction checks passed`.

### Hints — only after an attempt

1. Collect `(slot_id, payload)` for every live entry **before** moving any bytes. Otherwise an early write could overwrite a record you have not copied yet.
2. Start a new write boundary at `len(self.data)`. For each saved payload, subtract its length, write it there, and replace that slot's offset/length pair.
3. Do not rebuild the directory with only live entries: that would silently change slot IDs.
4. If the all-deleted test reports 56 free bytes, you probably removed the directory entries. Only the fresh empty page has 56; the page with three deleted entries has 44.

**Done when:** the checks pass, you can trace a new insertion/deletion/compaction sequence on paper, and you can explain why stable slot IDs require updating directory entries rather than callers. Add your own test with adjacent deletions and a rejected insertion before calling the lab complete.

## The buffer pool

The page lab manipulates one in-memory page. A real database must decide which of many pages to keep in memory. Its **buffer pool** is a cache of database pages.

```text
request page 17
      |
      v
is page 17 in a memory frame?
      | yes                         | no
      v                             v
use cached page             find an available frame
                                    |
                                    v
                             load page 17 into it
```

A cache hit avoids fetching the page from the underlying file. A miss may be served from the operating system's cache rather than the physical device; “buffer miss” does not automatically mean “disk read”.

| Property | Meaning                                               | Consequence                                        |
| -------- | ----------------------------------------------------- | -------------------------------------------------- |
| Pinned   | An operation is currently using this frame            | It cannot be evicted while pinned                  |
| Dirty    | The page has changes not yet written to its data file | It needs a write before its frame can be reused    |
| Clean    | No outstanding changes relative to the data file      | An unpinned frame can be reused without writing it |

Pinning and dirtiness are separate properties: a page can be both pinned and dirty.

Eviction policies vary. PostgreSQL uses a clock-sweep-style policy with usage counts rather than maintaining a perfect least-recently-used ordering on every access. Large sequential scans can use a limited ring of buffers to reduce displacement of frequently reused pages.

A dirty page is also part of the crash-recovery story. In a write-ahead logging system, the relevant **WAL** (write-ahead log: recovery information about changes) must be made durable before the changed data page is written. The page itself is not the whole transaction. Continue with [[databases/10-durability-and-recovery|durability and recovery]] for the ordering rules.

### Sizing is an experiment, not a constant

For PostgreSQL on a dedicated server, roughly 25% of RAM is a common starting point for `shared_buffers`, not a universal optimum. PostgreSQL also relies on the OS cache. Dedicated InnoDB deployments often allocate a larger share to their buffer pool; whether data-file I/O bypasses the OS cache depends on configuration and platform, not just the engine name.

Leave room for connections, query workspaces, the OS, and other processes. Inspect cache statistics **alongside** query latency, physical reads, memory pressure, and workload shape. A high hit ratio can coexist with bad performance; a scan-heavy workload need not achieve an arbitrary 99% target.

## Row vs column storage

A slotted page explains how to fit records. There is a separate question: should neighbouring bytes belong to the same **row** or the same **column**?

```text
Rows:                         Columns:
(1, Alice, 30)                id:   [1, 2, 3]
(2, Bob,   25)                name: [Alice, Bob, Cara]
(3, Cara,  41)                age:  [30, 25, 41]
```

- Fetch a whole customer by ID: a row-oriented layout keeps that customer's fields together. The lookup can still require index and table-page reads; “one row” does not mean “one I/O”.
- Average ages across millions of customers: a column-oriented layout can read the age values without also scanning every name and address.

This is why row storage often suits **OLTP** (many small operational reads/writes), while column storage often suits **OLAP** (large analytical scans). Indexes, compression, caching, and selectivity still matter; the labels alone do not determine the faster plan.

Columns often compress well because adjacent values share a type and may repeat:

| Encoding    | Small example                                               | What it saves                    |
| ----------- | ----------------------------------------------------------- | -------------------------------- |
| Run-length  | `active, active, active` → `(active, 3)`                    | Repeated consecutive values      |
| Dictionary  | `London, Leeds, London` → codes `0, 1, 0` plus a dictionary | Repeated long values             |
| Delta       | `1000, 1002, 1003` → base `1000`, differences `2, 1`        | Small changes between neighbours |
| Bit-packing | Integers from 0 to 1000 fit in 10 bits                      | Unused high-order bits           |

Columnar engines can also process batches rather than one row at a time. This **vectorised execution** can reduce per-row overhead and sometimes use [[foundations/computer-architecture/03-instruction-sets|SIMD instructions]]. Systems such as DuckDB and ClickHouse combine these techniques; do not assume a fixed speedup without measuring your query.

Hybrid analytical formats such as Parquet and ORC partition data into row groups or stripes and then store columns within those groups. This balances column-wise access with manageable chunks. It is related to the partition-attributes-across layout idea, rather than literally the small slotted page from our lab.

## Table organisation

Once rows occupy many pages, an engine needs a policy for placing them.

| Question               | Heap-organised table                                     | Clustered / index-organised table                                       |
| ---------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------- |
| Where do rows go?      | A page with available space, with no key-order guarantee | Into the leaves of the clustering B-tree                                |
| Primary-key lookup     | Often index lookup followed by heap access               | Tree traversal reaches the row in a leaf                                |
| Primary-key range scan | May visit scattered heap pages                           | Rows are nearby in key order, though not necessarily contiguous on disk |
| Secondary index        | Often refers to a physical row location                  | In InnoDB, stores the primary key for a subsequent clustered lookup     |

PostgreSQL's standard table storage is heap-organised; `CLUSTER` can rewrite a table in index order but does not maintain that order after later writes. InnoDB organises rows by a clustered index, normally the primary key. SQL Server and Oracle also offer heap and clustered/index-organised choices with their own details.

A random primary key in InnoDB distributes inserts across the clustered tree and can increase page splits and cache churn. Time-ordered keys, including suitably stored UUIDv7 values, can improve locality. They are not a universal free win: increasing keys may concentrate concurrent inserts on a hot region, and random keys still affect PostgreSQL's **indexes**, even though they do not determine heap placement.

**Fill factor** is a configurable amount of packing in some structures. Leaving room on PostgreSQL heap pages can help eligible updates create a new row version on the same page; it also makes the table larger. Choose it from observed update patterns, not a blanket “lower is better” rule. Index fill-factor settings have related but distinct purposes.

## Free space and fragmentation

The lab already showed the central idea: deleting a record does not shrink its page. Deleting rows usually does not immediately shrink the database file either.

In PostgreSQL, old row versions can be reclaimed once no transaction needs them. `VACUUM` makes that space reusable, and the free space map helps locate pages with room. Ordinary vacuum can sometimes return wholly empty pages at the file's end; it generally does not compact all partially occupied pages into a smaller file.

`VACUUM FULL` rewrites a table and needs an exclusive lock. Rewriting/repacking tools have their own space, locking, and operational requirements; “online” does not mean risk-free or lock-free. Do not run maintenance experiments against a live database for this lesson.

Fragmentation and **bloat** mean extra space and potentially more reads for the same useful data. MVCC's old versions are one cause, not a phenomenon unique to PostgreSQL. Read [[databases/09-mvcc-and-concurrency-control|MVCC]] before interpreting dead-tuple counts as a command to rebuild everything.

## Check your understanding

Attempt these without the note, then compare your reasoning below.

1. A 128-byte teaching page has an 8-byte header and three 4-byte slots. Its live records total 90 bytes, with no holes. Can a 15-byte record fit in a new slot?
2. After compaction, why must slot 1 remain slot 1 even if slot 0 was deleted?
3. Why is a dirty page not necessarily eligible for eviction? Why is a clean page not necessarily eligible either?
4. Your analytical query reads one numeric column from a wide table. What can column storage save, and what would you measure before claiming it is faster?

### Answers — after your attempt

1. No. Free space is `128 - 8 - 12 - 90 = 18` bytes. The new record needs `15 + 4 = 19`. Ignoring metadata would accept a record that does not fit.
2. Callers hold slot IDs. Renumbering slots would make those references point to another record or an invalid entry. Change the byte offset **inside** the slot instead.
3. A dirty page needs its changes safely written before reuse; it may also be pinned. A clean page may be pinned too. “Clean” describes write state, not whether another operation is using it.
4. It can avoid reading unrelated fields and exploit compression/batched execution. Compare equivalent query results and inspect bytes read, cache conditions, query plans, and timings on representative data. Do not claim an engine-independent speed multiplier.

## What to actually do

- Choose types that represent the required range and semantics; smaller correct records can improve density. Do not undersize a field just to save bytes.
- Request only the columns you need, especially when values are large or stored out of line.
- Treat key choice, buffer sizing, and fill factor as workload-specific decisions.
- Start by observing. PostgreSQL's `pg_stat_user_tables` and the `pgstattuple` extension can help investigate space use, but some inspection operations themselves cost work.
- Consider a columnar engine for analytical scans, rather than assuming more indexes on an operational database are always the answer.

**Next:** [[databases/04-b-trees-and-indexes|B-Trees and Indexes]] uses pages to find records without scanning everything. Later, [[databases/13-practice-exercises|practice exercises]] 1–5 connect page and index reasoning to actual query plans; exercise 5 asks you to identify a heap/table fetch that an index can avoid. Use a disposable local database for those experiments.

For a larger implementation, [[build-your-own-shit/06-your-own-database|build your own database]] extends beyond this in-memory model into files, indexes, and recovery. Passing the lab proves your teaching model behaves as specified, not that you have implemented a production storage engine.

## Related

- [[databases/04-b-trees-and-indexes|B-Trees and Indexes]] — the structure built on these pages
- [[databases/05-lsm-trees|LSM Trees]] — the write-optimised alternative
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — the same argument, one level down
- [[databases/README|Databases map]]

## Further reading

- [PostgreSQL: Database Page Layout](https://www.postgresql.org/docs/current/storage-page-layout.html) — actual page headers, item identifiers, and tuple layout
- [PostgreSQL: TOAST](https://www.postgresql.org/docs/current/storage-toast.html) — storage of large attribute values
- [PostgreSQL: Routine Vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html) — reuse versus returning space to the operating system

These describe a real engine. The 64-byte Python page above is a deliberately smaller teaching format.
