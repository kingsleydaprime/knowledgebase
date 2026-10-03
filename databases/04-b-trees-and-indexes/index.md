# B-Trees and Indexes

**[Intermediate → Advanced]** — Why databases use B+ trees and not binary trees, how an index is actually used, what a composite index can and can't serve, and when adding one makes things worse. Every claim about PostgreSQL in this lesson is checked by the lab on a real PostgreSQL 18 database with a million rows.

## Before you start

You can already:

- Explain that a database stores rows in fixed-size pages (8 KB in PostgreSQL) and reads whole pages at a time → [[databases/03-storage-and-page-layout|storage and page layout]].
- Write a `SELECT … WHERE … ORDER BY` query and read its result.
- Explain binary search on a sorted list, and why it takes about log₂ n steps → [[dsa/02-data-structures/01-arrays|arrays]].
- Run Python with `uv`, and have PostgreSQL 16 or later installed locally (`initdb` and `pg_ctl` on your `PATH`); the lab creates and deletes its own throwaway database.

After this lesson you will be able to:

1. Work out how many levels a B+ tree needs for a table, and how many page reads a lookup and a range scan cost.
2. Say which queries a composite index can serve, using the leftmost-prefix rule, and design one for a query.
3. Read `EXPLAIN (ANALYZE, BUFFERS)` well enough to tell an index scan, an index-only scan, a bitmap scan and a sequential scan apart, and to see the pages each read.
4. Explain four reasons the planner won't use an index you made, and what each index costs on every write.

**Study route:** sections 1–4 build the structure. Stop at the predictions in sections 3, 6 and 8 and try them before reading on. Section 10 is the lab. Next week's lesson builds on the plans you learn to read here.

## The kid version

A school's lost-property office has thousands of items in boxes. To find one, you'd have to open every box. So the office keeps a ring binder at the front: the first page says "A–F: shelf 1, G–M: shelf 2…", each shelf has its own card saying which box holds which names, and each box is sorted. You turn one page, read one card, open one box. Because each page of the binder points to hundreds of places, three steps are enough for a huge office.

**Where the analogy stops working.** The binder never changes in the analogy. A database index has to be updated every time anything is added, changed or removed, and each update costs work and disk writes. An office with ten binders, sorted ten different ways, spends its whole day updating binders. That cost is the second half of this lesson.

## 1. Why this exists

The shop has a million orders. "Show order 424242" without an index means reading the whole table, all 10,310 pages, to find one row. With an index, PostgreSQL reads four pages. "Show customer 42's orders since June" can be answered with a handful of pages or with all ten thousand, depending on which index exists and in what column order. And every index added to make reads fast makes every insert, update and delete slower. Indexes are the biggest performance lever in a database, and the easiest to pull the wrong way.

## Terms used in this lesson

1. **Index**: This is a separate data structure that keeps some of a table's columns in sorted order, with a pointer to each row, so rows can be found without reading the whole table.
2. **Page**: This is the fixed-size block, 8 KB in PostgreSQL, in which a database stores and reads data. A page read is the unit of cost.
3. **B+ tree**: This is the tree that almost every database index uses. Internal nodes hold only keys for routing; all the keys and row pointers are in the leaves, and the leaves are linked in order.
4. **Fanout**: This is how many children one internal node points to. With 8 KB pages and small keys, it's in the hundreds.
5. **Split**: This is what happens when a node is full and a key must be added: it divides in two and passes a key up to its parent.
6. **Clustered index**: This is an index whose leaves are the table rows themselves, so the table is stored in index order. MySQL's InnoDB stores every table this way, by primary key.
7. **Secondary index**: This is any other index. Its leaves hold the indexed columns and a pointer to the row.
8. **Heap**: In PostgreSQL, this is the table itself: rows stored in pages in no particular order. Indexes point into it.
9. **Index-only scan**: This is answering a query from the index alone, without reading the table, because every column it needs is in the index.
10. **Composite index**: This is an index on several columns, sorted by the first, then by the second within each value of the first, and so on.
11. **Selectivity**: This is the share of rows a condition matches. A condition matching 1% of rows is very selective; one matching 99% isn't.
12. **Sequential scan**: This is reading every page of a table in order. For a large share of rows, it beats an index.
13. **Planner**: This is also called the **optimiser**. It's the part of the database that chooses how to run a query, estimating the cost of each possible plan.
14. **WAL (write-ahead log)**: The letters stand for those words. It's the log every change is written to before the data pages, so changes survive a crash. More indexes means more of it per write.

## 2. Why not a binary tree

**A balanced binary search tree has $O(\log_2 n)$ lookup, which is optimal in comparisons.** It's also the wrong structure for disk.

**At 100 million rows, $\lceil\log_2(10^8)\rceil = 27$ levels.** Each level is a pointer to a different place in memory or on disk, and **each is a potential page read.** 27 random reads per lookup is unusable.

In words: a B+ tree makes each node a whole page, holding hundreds of keys, so each level divides the search by hundreds instead of by two. The number of levels is the logarithm of the number of leaf pages, to the base of the fanout, plus one for the leaves. With a fanout of about 400 (an 8 KB page of small keys):

$$\log_{400}(10^8) \approx 3.07$$

so a 100-million-row index needs **four levels**, and a million-row index **three**. The lab's `levels` function gives exactly those, and PostgreSQL agrees: the million-row primary key's root is at level 2 (levels 2, 1 and 0), and a lookup reads **four pages**, three index pages and the one table page holding the row.

> **Four page reads instead of twenty-seven.** And the top two levels are almost always in memory, **so a lookup in a 100-million-row table is typically one or two physical reads.**
>
> **This is the same argument as [[computer-architecture/08-the-memory-hierarchy|cache lines]]:** you pay per *block fetched*, not per comparison, so make each block do as much work as possible. **A binary tree does one comparison per fetch; a B+ tree does hundreds.**

## 3. The structure, and how it grows

```
                  ┌───────────────────┐
   internal       │  [40]  [80]  [120]│    keys only — routing
                  └─┬────┬─────┬────┬─┘
          ┌─────────┘    │     │    └─────────┐
      ┌───▼───┐    ┌─────▼─┐ ┌─▼─────┐   ┌────▼──┐
 leaf │10 20 30│◄──►│45 60 70│◄►│85 90 │◄─►│130 140│   keys + row pointers
      └────────┘    └───────┘  └──────┘   └───────┘
                  linked list across the leaves
```

**The "+" in B+ tree means all values live in the leaves.** Internal nodes hold only keys, for routing. Three properties follow:

1. **Higher fanout.** Internal nodes hold no payload, so more keys fit per page, so the tree is shallower.
2. **Leaves are linked.** A range scan finds the start, then follows the leaf chain, with no tree traversal per row. That's why `WHERE created_at BETWEEN … AND …` is efficient, and why B+ trees beat hash indexes for ranges.
3. **All leaves are at the same depth.** Every lookup costs the same, so performance is predictable.

**Balance is kept on write.** A full leaf **splits** in half, and the right half's first key is copied up to the parent as a separator. If the parent is now full, it splits too, moving its middle key up. A split can climb to the root, and a root split is the only way the tree grows a level. Deletes can merge underfull nodes, though most databases defer that and tolerate some empty space.

**Predict before reading on.** A tree whose nodes hold at most 3 keys is given the keys 1 to 10 in order. How tall is it, how many pages does looking up 7 read, and how many does the range 4 to 8 read?

<details>
<summary>After your prediction</summary>

Height **3**: leaves `[1 2] [3 4] [5 6] [7 8] [9 10]`, two internal nodes above them, and a root holding `[7]`. Looking up 7 reads **3** pages, one per level, and so does looking up a key that isn't there. The range 4 to 8 reads **6**: three to reach the leaf holding 4, then along the chain through `[5 6]` and `[7 8]`, and one more leaf, `[9 10]`, to discover that 9 is past the end. The lab builds this tree and checks every number. It also inserts a million keys in random order into nodes of 400, gets height 3, and finds any key in 3 page reads.

</details>

**Concurrency** uses **latch crabbing**: hold a latch on the child, and release the parent once you know no split will propagate up. Modern engines use B-link trees, which add a right-sibling pointer so readers never block on a concurrent split.

## 4. Clustered and secondary indexes

**Covered in [[databases/03-storage-and-page-layout|note 03]], and it's the difference that decides an index's cost.**

- **Clustered (InnoDB's primary key)**: the table *is* the tree. Leaves contain the full rows.
- **Secondary index**: leaves contain the indexed key plus a pointer to the row.

**What the pointer is matters enormously:**

| | Secondary leaf holds | Lookup cost |
|---|---|---|
| **PostgreSQL (heap)** | `ctid`: (page, slot) | index → heap page |
| **InnoDB (clustered)** | **the primary key** | index → **primary-key tree traversal** |

> **So in InnoDB every secondary index lookup is two B-tree traversals**, and **a wide primary key inflates every secondary index**, because the primary key is copied into each one. **A 40-byte natural primary key across six secondary indexes wastes a great deal of space and reading.** That's another argument for narrow surrogate keys.

## 5. Index-only scans

**The optimisation worth designing for.** If **every column the query needs is in the index**, the database never touches the table:

```sql
CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total);

SELECT total FROM orders WHERE customer_id = 42;
-- both columns are in the index → no heap access
```

**PostgreSQL calls it an *index-only scan*, and it needs the visibility map to confirm each page is all-visible.** Otherwise it must check the heap for each row's visibility anyway. In the lab, right after `VACUUM`, the plan shows `Index Only Scan` with **`Heap Fetches: 0`**. After an `UPDATE` of customer 42's orders, with no vacuum since, the same query shows `Heap Fetches: 40`: still called an index-only scan, but reading the table for every row. **So a table that hasn't been vacuumed recently loses index-only scans**, which is a real and confusing performance regression → [[databases/09-mvcc-and-concurrency-control|MVCC]].

**`INCLUDE` columns** (PostgreSQL 11+, SQL Server) store extra columns in the leaves **without** making them part of the key, so they don't affect ordering or uniqueness, and don't bloat the internal nodes.

## 6. Composite indexes and the leftmost rule

**An index on `(a, b, c)` is sorted by `a`, then by `b` within each `a`, then by `c`.** In words: the index can only narrow a search using its columns from the left, each tested for equality, and then at most one range. A column after a gap, or after a range, can only filter rows the index has already found.

| Query | Uses index? |
|---|---|
| `WHERE a = 1` | ✅ |
| `WHERE a = 1 AND b = 2` | ✅ |
| `WHERE a = 1 AND b = 2 AND c = 3` | ✅ fully |
| `WHERE b = 2` | ❌ **cannot narrow** (but see skip scan, below) |
| `WHERE a = 1 AND c = 3` | ⚠️ narrows by `a` only, then filters |
| `WHERE a > 1 AND b = 2` | ⚠️ a range on `a` stops `b` narrowing |

The lab's `usable_prefix` encodes the table, and its tests check every row of it.

> **The leftmost prefix rule.** Think of a phone book sorted by (surname, forename): finding everyone called "Smith" is easy; finding everyone called "John" means reading the whole book.
>
> **Note the last row: once you use a range, later columns can't narrow the search.** So **put equality columns before range columns** when ordering a composite index. That one rule fixes a lot of underperforming indexes.

**Ordering guidance:** equality columns first, then the range column, then columns needed only for output. **Selectivity matters less than people say**; the leftmost rule dominates.

**Predict before reading on.** The shop's orders have an index on `(customer_id, created_at)`, with 50,000 different customers. What does PostgreSQL do for `WHERE customer_id = 42 AND created_at > '2026-06-01'`? For `WHERE created_at` in one particular hour, with no customer? Now replace the index with one on `(status, created_at)`, where `status` has only two values. What happens to the hour query?

<details>
<summary>After your prediction</summary>

The first uses the index, with both columns narrowing the search. The hour query **can't use it**, and PostgreSQL reads the whole table: a `Seq Scan` through all 10,310 pages, throwing away 999,880 rows to find 120.

The third is new in **PostgreSQL 18: skip scan**. With `(status, created_at)`, the planner searches the index once for each `status` value, as if you'd written `status = 'complete' AND …` and then `status = 'pending' AND …`. The hour query becomes an `Index Scan` reading 21 pages. It works only when the leading column has **few distinct values**. With 50,000 customers it would mean 50,000 searches, so the planner still prefers the sequential scan. The leftmost rule still describes what a B-tree can narrow; skip scan is a way to run several narrow searches cheaply. The lab checks all three plans.

</details>

## 7. Index types beyond B-tree

| Type | Good for | Cannot do |
|---|---|---|
| **B-tree** | equality, **ranges**, sorting, prefix `LIKE` | — the default for a reason |
| **Hash** | equality only | ranges, ordering |
| **GIN** | **arrays, JSONB, full-text**: many keys per row | slow to update |
| **GiST** | geometric, ranges, nearest-neighbour | |
| **BRIN** | **huge naturally ordered tables**: tiny index | unordered data |
| **Bitmap** | low-cardinality columns in OLAP | high update rates |

**BRIN deserves a mention** because it's underused: it stores the minimum and maximum per range of pages, so an index on a billion-row time-series table can be **kilobytes** rather than gigabytes. **It only works if the data's physical order follows the indexed column**, which is exactly true for append-only time series.

**Partial indexes** index a subset of rows:

```sql
CREATE INDEX orders_pending ON orders (created_at) WHERE status = 'pending';
```

**If 1% of orders are pending, the index is about 1% of the size**: in the lab, 240 KB against 21.4 MB for the same index on every row. It stays hot in memory, which makes it **excellent for queue-like tables**.

**Expression indexes** index a computed value, `lower(email)`, which is required for an index to serve `WHERE lower(email) = …` (section 8).

## 8. When indexes make things worse

**Every index is a cost**, and this is the half people skip:

- **Writes slow down.** Every `INSERT`, `UPDATE` and `DELETE` must maintain every index, and log the change to each. In the lab, 10,000 inserts into a table with four extra indexes write **3.0 times** the WAL of the same inserts with only a primary key.
- **Space.** Indexes commonly exceed the table's size in total.
- **Memory pressure.** Index pages compete with table pages for the buffer cache.
- **The planner gets more choices**, and more chances to choose badly.

**Predict before reading on.** An index exists on `status`. 99% of orders are `complete` and 1% `pending`. Which of `WHERE status = 'complete'` and `WHERE status = 'pending'` uses the index?

<details>
<summary>After your prediction</summary>

Only `pending`. For `complete`, the planner chooses a **sequential scan**, and it's right: fetching 99% of rows one index entry at a time means jumping around the table, which costs more than reading it straight through. The lab checks both plans. This surprises people more than anything else about indexes.

</details>

**When an index won't be used at all:**

1. **Low selectivity**, as above.
2. **A function applied to the column.** In the lab, `WHERE lower(email) = 'user42@example.com'` is a `Seq Scan` despite an index on `email`; after `CREATE INDEX ON orders (lower(email))` it's an `Index Scan`.
3. **Implicit type casts.** `WHERE varchar_col = 123` may cast the column, not the literal.
4. **A leading wildcard.** `LIKE '%foo'` can't use a B-tree prefix. Use trigrams (`pg_trgm`) or full-text search.
5. **`OR` across columns**, which is sometimes better as a `UNION` of two indexed queries.

**Find unused indexes:**

```sql
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

**Drop them.** An index with zero scans is pure write cost → [[databases/12-operating-a-database|operating a database]].

## 9. Practical notes

- **Index your foreign keys.** Most databases don't do it automatically, and **an unindexed foreign key makes deletes on the parent table scan the child**, a common cause of mysterious lock contention.
- **Index what you filter, join and sort on**, in that order of priority.
- **Prefer fewer, wider composite indexes** to many single-column ones. One index on `(a, b)` serves `WHERE a` too; two separate indexes serve neither combination well.
- **`CREATE INDEX CONCURRENTLY`** in PostgreSQL. A plain `CREATE INDEX` blocks writes for the duration; on a large production table, that's an outage.
- **Rebuild bloated indexes** with `REINDEX CONCURRENTLY`.
- **Check it's used.** `EXPLAIN (ANALYZE, BUFFERS)`. **Creating an index and not verifying it's used is the most common wasted effort in database tuning** → [[databases/07-join-algorithms-and-the-optimiser/index|reading EXPLAIN]].

## 10. The lab: a model tree, and a real database

`btree.py` is a B+ tree you can watch: inserts with splits, lookups and range scans that count page reads, the `levels` arithmetic, and the leftmost-prefix rule. `test_btree.py` checks the model. `test_postgres.py` loads a million orders into a real PostgreSQL database and checks every PostgreSQL claim in this lesson by reading `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`: the index depth with `pageinspect`, the four pages per lookup, the composite and skip-scan plans, index-only scans before and after an update, the selectivity and expression-index cases, the partial index's size, and the write cost in WAL bytes.

[`labs/shared/with-postgres.sh`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/shared) creates a throwaway PostgreSQL cluster in a temporary folder, reachable only through a socket there, runs the tests, and deletes it. It turns off autovacuum and parallel query, so plans are the same on every run, and durability, because nothing is kept.

```python
"""A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule of composite indexes.
A teaching model: one node is one "page", and every node visited counts as one page read."""
import math
from dataclasses import dataclass, field
from typing import Any


def levels(rows: int, keys_per_leaf: int, fanout: int) -> int:
    """How many levels a B+ tree needs: one level of leaves, then enough internal levels to point at them all."""
    leaves = math.ceil(rows / keys_per_leaf)
    return 1 + max(0, math.ceil(math.log(leaves, fanout) - 1e-12))  # tiny slack so exact powers don't round up


@dataclass
class Leaf:
    keys: list = field(default_factory=list)
    values: list = field(default_factory=list)
    next: "Leaf | None" = None  # the leaves form a linked list, for range scans


@dataclass
class Internal:
    keys: list = field(default_factory=list)  # routing only: children[i] holds keys < keys[i]
    children: list = field(default_factory=list)


class BPlusTree:
    """Keys and values live only in the leaves. A node holds at most `max_keys` keys; one more and it splits."""

    def __init__(self, max_keys: int):
        if max_keys < 3:
            raise ValueError("max_keys must be at least 3")
        self.max_keys = max_keys
        self.root: Leaf | Internal = Leaf()
        self.height = 1

    def search(self, key) -> tuple[Any, int]:
        """(value or None, pages read). Always reads exactly `height` pages: every leaf is at the same depth."""
        node, pages = self.root, 1
        while isinstance(node, Internal):
            node, pages = node.children[self._child(node, key)], pages + 1
        i = self._find(node.keys, key)
        return (node.values[i] if i < len(node.keys) and node.keys[i] == key else None), pages

    def range(self, lo, hi) -> tuple[list, int]:
        """Values for lo <= key <= hi, and pages read: down the tree once, then along the leaf chain."""
        node, pages = self.root, 1
        while isinstance(node, Internal):
            node, pages = node.children[self._child(node, lo)], pages + 1
        found = []
        while node is not None:
            for k, v in zip(node.keys, node.values):
                if k > hi:
                    return found, pages
                if k >= lo:
                    found.append(v)
            node = node.next
            if node is not None:
                pages += 1
        return found, pages

    def insert(self, key, value) -> None:
        split = self._insert(self.root, key, value)
        if split:  # the root split: the only way the tree grows a level
            separator, right = split
            self.root = Internal([separator], [self.root, right])
            self.height += 1

    def _insert(self, node, key, value):
        if isinstance(node, Leaf):
            i = self._find(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value  # an existing key: replace
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) <= self.max_keys:
                return None
            mid = len(node.keys) // 2  # split in half; the right half's first key is copied up
            right = Leaf(node.keys[mid:], node.values[mid:], node.next)
            node.keys, node.values, node.next = node.keys[:mid], node.values[:mid], right
            return right.keys[0], right
        i = self._child(node, key)
        split = self._insert(node.children[i], key, value)
        if not split:
            return None
        separator, right = split
        node.keys.insert(i, separator)
        node.children.insert(i + 1, right)
        if len(node.keys) <= self.max_keys:
            return None
        mid = len(node.keys) // 2  # an internal split moves the middle key up, rather than copying it
        up = node.keys[mid]
        sibling = Internal(node.keys[mid + 1:], node.children[mid + 1:])
        node.keys, node.children = node.keys[:mid], node.children[:mid + 1]
        return up, sibling

    @staticmethod
    def _find(keys: list, key) -> int:
        lo, hi = 0, len(keys)
        while lo < hi:
            mid = (lo + hi) // 2
            if keys[mid] < key:
                lo = mid + 1
            else:
                hi = mid
        return lo

    @staticmethod
    def _child(node: Internal, key) -> int:
        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1
        return i


def usable_prefix(index: tuple[str, ...], equal: set[str], ranges: set[str]) -> list[str]:
    """The index columns that narrow the search: equality columns from the left, then at most one range column.
    Columns after a range, or after a gap, can only filter rows the index has already found."""
    used = []
    for column in index:
        if column in equal:
            used.append(column)
        elif column in ranges:
            used.append(column)
            break  # after a range, the next column isn't sorted within it
        else:
            break  # a gap: nothing to the right can be used to narrow
    return used
```

```python
import math
import random
import unittest

from btree import BPlusTree, Internal, Leaf, levels, usable_prefix


class Model(unittest.TestCase):
    def test_why_not_a_binary_tree(self):
        self.assertEqual(math.ceil(math.log2(10**8)), 27)  # a balanced binary tree over 100 million keys: 27 levels
        self.assertEqual(levels(10**8, 367, 400), 4)  # a B+ tree: 4, and the top two or three stay in memory
        self.assertEqual(levels(10**6, 367, 400), 3)  # a million rows: 3, as Postgres reports below

    def test_splits_keep_every_leaf_at_the_same_depth(self):
        tree = BPlusTree(max_keys=3)
        for k in range(1, 11):
            tree.insert(k, f"v{k}")
        self.assertEqual(tree.height, 3)
        self.assertIsInstance(tree.root, Internal)
        self.assertEqual(tree.root.keys, [7])  # the separator that last moved up
        leaves, node = [], tree.root
        while isinstance(node, Internal):
            node = node.children[0]
        while node:
            leaves.append(node.keys)
            node = node.next
        self.assertEqual(leaves, [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])  # linked, in order

    def test_a_lookup_reads_one_page_per_level(self):
        tree = BPlusTree(max_keys=3)
        for k in range(1, 11):
            tree.insert(k, f"v{k}")
        self.assertEqual(tree.search(7), ("v7", 3))
        self.assertEqual(tree.search(99), (None, 3))  # a miss costs the same
        self.assertEqual(tree.range(4, 8), (["v4", "v5", "v6", "v7", "v8"], 6))  # down once, then along the leaves

    def test_a_million_keys_three_pages(self):
        keys = list(range(1_000_000))
        random.Random(1).shuffle(keys)
        tree = BPlusTree(max_keys=400)
        for k in keys:
            tree.insert(k, k)
        self.assertEqual((tree.height, tree.search(424_242)), (3, (424_242, 3)))

    def test_the_leftmost_prefix_rule(self):
        index = ("a", "b", "c")
        self.assertEqual(usable_prefix(index, {"a"}, set()), ["a"])
        self.assertEqual(usable_prefix(index, {"a", "b", "c"}, set()), ["a", "b", "c"])
        self.assertEqual(usable_prefix(index, {"b"}, set()), [])  # no leading column: can't narrow
        self.assertEqual(usable_prefix(index, {"a", "c"}, set()), ["a"])  # a gap at b: c only filters
        self.assertEqual(usable_prefix(index, {"b"}, {"a"}), ["a"])  # a range on a: b only filters
        self.assertEqual(usable_prefix(index, {"a"}, {"b"}), ["a", "b"])  # equality first, then the range


if __name__ == "__main__":
    unittest.main()
```

```python
"""The same ideas, checked on a real PostgreSQL 18 with a million rows. Run through ../shared/with-postgres.sh."""
import json
import unittest

import psycopg

SETUP = """
CREATE EXTENSION IF NOT EXISTS pageinspect;
CREATE TABLE orders AS
SELECT i AS id, i % 50000 AS customer_id,
       timestamptz '2026-01-01 00:00Z' + i * interval '30 seconds' AS created_at,
       (i::bigint * 7919 % 10000)::int AS total,       -- i * 7919 alone overflows a 32-bit integer
       CASE WHEN i % 100 = 0 THEN 'pending' ELSE 'complete' END AS status,
       'User' || i || '@Example.com' AS email
FROM generate_series(1, 1000000) AS i;
ALTER TABLE orders ADD PRIMARY KEY (id);
VACUUM ANALYZE orders;
"""


def nodes(plan: dict):
    """Every node of an EXPLAIN plan, top first."""
    yield plan
    for child in plan.get("Plans", []):
        yield from nodes(child)


class Postgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = psycopg.connect(autocommit=True)  # PGHOST etc. come from with-postgres.sh
        for statement in SETUP.split(";\n"):  # one at a time: several in one call run as one transaction,
            if statement.strip():  # and VACUUM refuses to run inside a transaction
                cls.db.execute(statement)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def explain(self, sql: str) -> list[dict]:
        row = self.db.execute(f"EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}").fetchone()
        plan = row[0] if isinstance(row[0], list) else json.loads(row[0])
        return list(nodes(plan[0]["Plan"]))

    def pages(self, plan: list[dict]) -> int:
        top = plan[0]
        return top["Shared Hit Blocks"] + top["Shared Read Blocks"]  # the top node's counts include its children's

    def test_a_million_row_index_has_three_levels_and_a_lookup_reads_four_pages(self):
        level = self.db.execute("SELECT level FROM bt_metap('orders_pkey')").fetchone()[0]
        self.assertEqual(level, 2)  # the root is at level 2: levels 2, 1 and 0 (the leaves)
        plan = self.explain("SELECT * FROM orders WHERE id = 424242")
        self.assertEqual(plan[0]["Node Type"], "Index Scan")
        self.assertEqual(self.pages(plan), 4)  # three index pages, then the table page with the row

    def test_a_composite_index_serves_its_leading_column_not_the_second_alone(self):
        self.db.execute("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)")
        try:
            both = self.explain("SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'")
            self.assertIn("orders_customer_created", [n.get("Index Name") for n in both])
            second = self.explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'")
            self.assertEqual(second[0]["Node Type"], "Seq Scan")  # 50,000 customers to skip through: not worth it
        finally:
            self.db.execute("DROP INDEX orders_customer_created")

    def test_skip_scan_uses_an_index_without_its_leading_column_when_that_has_few_values(self):
        self.db.execute("CREATE INDEX orders_status_created ON orders (status, created_at)")
        try:
            plan = self.explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'")
            self.assertEqual((plan[0]["Node Type"], plan[0]["Index Name"]), ("Index Scan", "orders_status_created"))
            self.assertEqual(plan[0]["Actual Rows"], 120)
            self.assertLess(self.pages(plan), 50)  # a few searches, one per status value: 21 pages; a full scan reads 10,310
        finally:
            self.db.execute("DROP INDEX orders_status_created")

    def test_an_index_only_scan_needs_a_vacuumed_table(self):
        self.db.execute("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)")
        try:
            self.db.execute("VACUUM orders")
            clean = self.explain("SELECT total FROM orders WHERE customer_id = 42")
            self.assertEqual((clean[0]["Node Type"], clean[0]["Heap Fetches"]), ("Index Only Scan", 0))
            self.db.execute("UPDATE orders SET total = total + 1 WHERE customer_id = 42")  # pages no longer all-visible
            dirty = self.explain("SELECT total FROM orders WHERE customer_id = 42")
            self.assertGreater(dirty[0]["Heap Fetches"], 0)  # it had to check the table after all
        finally:
            self.db.execute("DROP INDEX orders_customer_total")
            self.db.execute("VACUUM orders")

    def test_the_planner_refuses_an_index_that_matches_most_rows(self):
        self.db.execute("CREATE INDEX orders_status ON orders (status)")
        try:
            self.db.execute("ANALYZE orders")
            self.assertEqual(self.explain("SELECT * FROM orders WHERE status = 'complete'")[0]["Node Type"], "Seq Scan")  # 99%
            self.assertEqual(self.explain("SELECT * FROM orders WHERE status = 'pending'")[0]["Node Type"], "Index Scan")  # 1%
        finally:
            self.db.execute("DROP INDEX orders_status")

    def test_a_function_on_the_column_needs_an_expression_index(self):
        self.db.execute("CREATE INDEX orders_email ON orders (email)")
        try:
            query = "SELECT * FROM orders WHERE lower(email) = 'user42@example.com'"
            self.assertEqual(self.explain(query)[0]["Node Type"], "Seq Scan")  # the index on email doesn't help
            self.db.execute("CREATE INDEX orders_email_lower ON orders (lower(email))")
            self.db.execute("ANALYZE orders")
            self.assertEqual(self.explain(query)[0]["Node Type"], "Index Scan")
        finally:
            self.db.execute("DROP INDEX IF EXISTS orders_email; DROP INDEX IF EXISTS orders_email_lower")

    def test_a_partial_index_is_a_fraction_of_the_size(self):
        self.db.execute("CREATE INDEX orders_pending ON orders (created_at) WHERE status = 'pending'")
        self.db.execute("CREATE INDEX orders_created ON orders (created_at)")
        try:
            partial, full = self.db.execute("SELECT pg_relation_size('orders_pending'), pg_relation_size('orders_created')").fetchone()
            self.assertLess(partial / full, 0.02)  # 1% of the rows, about 1% of the size
        finally:
            self.db.execute("DROP INDEX orders_pending; DROP INDEX orders_created")

    def test_every_index_is_paid_for_on_every_write(self):
        self.db.execute("""
            CREATE TABLE plain (id int PRIMARY KEY, a int, b int, c int, d int);
            CREATE TABLE indexed (id int PRIMARY KEY, a int, b int, c int, d int);
            CREATE INDEX ON indexed (a); CREATE INDEX ON indexed (b); CREATE INDEX ON indexed (c); CREATE INDEX ON indexed (d);
        """)
        wal = []
        for table in ["plain", "indexed"]:
            before = self.db.execute("SELECT pg_current_wal_insert_lsn()").fetchone()[0]
            self.db.execute(f"INSERT INTO {table} SELECT i, i * 31 % 1000, i * 37 % 1000, i * 41 % 1000, i * 43 % 1000 FROM generate_series(1, 10000) i")
            wal.append(self.db.execute("SELECT pg_wal_lsn_diff(pg_current_wal_insert_lsn(), %s)", [before]).fetchone()[0])
        self.assertGreater(wal[1] / wal[0], 2.5)  # four more indexes: about three times the log written


if __name__ == "__main__":
    unittest.main()
```

**Lab:** the code is in [`databases/04-b-trees-and-indexes/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/python). From the vault root, `python3 labs/run.py b-trees-and-indexes/python` runs everything and checks this page still shows the same code. It needs PostgreSQL 16 or later installed (`initdb` and `pg_ctl`); `uv` fetches the psycopg driver on the first run. Expect 13 passing tests in about 25 seconds, most of it loading the million rows and the model's million inserts.

## Common pitfalls

1. **Indexing a column, then filtering on a function of it.** `lower(email)`, `date(created_at)`: index the expression instead.
2. **Composite indexes in the wrong order.** Equality columns first, then the range column.
3. **Expecting an index to be used for a common value.** For a large share of rows, a sequential scan is right.
4. **Never vacuuming a table that relies on index-only scans.** Every row goes back to the table.
5. **Adding indexes "just in case".** Each one is paid for on every write. Check `idx_scan` and drop unused ones.
6. **`CREATE INDEX` without `CONCURRENTLY` on a busy production table.** Writes are blocked until it finishes.
7. **Not checking the plan.** An index that isn't in `EXPLAIN` output isn't helping.

## Check your understanding

1. Why does a B+ tree over 100 million rows need about four levels, where a balanced binary tree needs 27?
2. A lookup in PostgreSQL reads four pages. Where does each one come from?
3. An index on `(customer_id, created_at)` exists. Which of these can it narrow, and how far: `WHERE created_at > X`; `WHERE customer_id = 7 AND created_at > X`; `WHERE customer_id > 7 AND created_at = X`?
4. Why did PostgreSQL 18 use an index on `(status, created_at)` for a query on `created_at` alone, but not one on `(customer_id, created_at)`?
5. An index-only scan's `Heap Fetches` goes from 0 to 40 after an `UPDATE`. Why, and what brings it back to 0?
6. Why is a sequential scan the right plan for `WHERE status = 'complete'` when 99% of rows match?

<details>
<summary>Answers — after your attempt</summary>

1. Each B+ tree node is a page holding hundreds of keys, so each level divides the search by hundreds: $\log_{400}(10^8) \approx 3.07$, rounded up to four levels. A binary tree divides by two per level: $\log_2(10^8) \approx 26.6$, so 27. Each level can be a separate page read.
2. Three from the index, the root (level 2), an internal page (level 1) and a leaf (level 0), and one from the table, the heap page holding the row the leaf points to.
3. `created_at > X` alone: it can't narrow (no leading column), so it's a sequential scan or a skip scan if the planner judges that cheaper. `customer_id = 7 AND created_at > X`: both columns narrow, equality then range. `customer_id > 7 AND created_at = X`: only `customer_id` narrows, because after a range, `created_at` isn't sorted across different customers, so it can only filter.
4. Skip scan searches the index once per distinct value of the leading column. `status` has two values, so two or so searches. `customer_id` has 50,000, so 50,000 searches, which costs more than reading the table, and the planner says no.
5. The `UPDATE` wrote new row versions, so those pages are no longer marked all-visible in the visibility map, and an index-only scan must check the table to see which version each transaction may see. `VACUUM` marks the pages all-visible again.
6. Fetching 99% of rows through the index means jumping between table pages almost a million times, in index order rather than physical order, and reading most pages several times. Reading the table straight through reads each page once, sequentially. Below a few per cent, the index wins; well above it, the sequential scan does.

</details>

## Practice — independent task

**Design indexes for three queries, predict, then verify.**

1. Extend `test_postgres.py`'s setup with a `customers` table (100,000 rows, with `country` and `signed_up_at`), and add `customer_id` as a foreign key on orders.
2. For each query, write down the index you'd create and the plan you expect *before* running anything:
   - the latest 20 orders for one customer, newest first;
   - all pending orders older than a week, oldest first;
   - customers from one country who signed up this year.
3. Create your indexes, and add a test per query that checks the plan's node type and index name, and that it reads fewer than 50 pages.

**Done when:** all three tests pass, your written predictions are next to the measured plans, and every wrong prediction has one sentence on why. (This week's "by Sunday" task, a slow query from a real project fixed with `EXPLAIN ANALYZE`, comes after the [[databases/07-join-algorithms-and-the-optimiser/index|next lesson]].)

<details>
<summary>Hints — after your attempt</summary>

- "Newest first" for one customer: `(customer_id, created_at DESC)` serves both the filter and the order, so there's no sort node.
- "Pending, oldest first": the partial index from section 7, `(created_at) WHERE status = 'pending'`.
- Country plus signed-up date: equality first, `(country, signed_up_at)`.

</details>

## Before moving on

You can work out a B+ tree's height and a lookup's page reads, design a composite index with equality before range, read an index scan, index-only scan, bitmap scan and sequential scan in `EXPLAIN`, and explain when an index won't be used and what each one costs.

**Recap.** A B+ tree puts hundreds of keys in each page-sized node, so a million rows need 3 levels and a hundred million 4; a lookup reads one page per level plus the row's table page, 4 pages in the lab. All values sit in linked leaves, so ranges are cheap. A composite index narrows by its leading equality columns and then one range; PostgreSQL 18's skip scan can work around a leading column with few values. Index-only scans skip the table when every needed column is in the index and the table is vacuumed. The planner rightly ignores an index for common values, and can't use one through a function without an expression index. Every index costs space, memory and write work: four extra indexes tripled the WAL per insert.

**Next.** [[databases/07-join-algorithms-and-the-optimiser/index|Join algorithms and the optimiser]]: how the planner chooses between these access paths and joins, and why it sometimes chooses badly.

## Related

- [[databases/05-lsm-trees|LSM trees]]: the write-optimised alternative
- [[databases/07-join-algorithms-and-the-optimiser/index|Join algorithms and the optimiser]]: how the planner decides to use these
- [[databases/database-design-reference|Database design reference]]: §11, index design strategy
- [[databases/index|Databases map]]
