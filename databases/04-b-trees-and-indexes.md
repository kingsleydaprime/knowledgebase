# B-Trees and Indexes

**[Intermediate → Advanced]** — Why B+ trees and not binary trees, how an index is actually used, and when adding one makes things worse.

## Why not a binary tree

**A balanced binary search tree has $O(\log_2 n)$ lookup — optimal in comparisons.** It's also the wrong structure for disk.

**At 100 million rows, $\log_2(10^8) \approx 27$ levels.** Each level is a pointer to a different place in memory or on disk, and **each is a potential I/O.** 27 random I/Os per lookup is unusable.

**A B+ tree with a fanout of ~400** (an 8 KB page holding ~400 keys):

$$\log_{400}(10^8) \approx 3 \text{ levels}$$

> **Three page reads instead of twenty-seven.** And the top two levels are almost always cached, **so a lookup in a 100-million-row table is typically one physical I/O.**
>
> **This is the same argument as [[foundations/computer-architecture/08-the-memory-hierarchy|cache lines]]:** you're paying per *block fetched*, not per comparison. So make each block do as much work as possible. **A binary tree does one comparison per fetch; a B+ tree does hundreds.**

## Structure

```
                  ┌───────────────────┐
   internal       │  [40]  [80]  [120]│    keys only — routing
                  └─┬────┬─────┬────┬─┘
          ┌─────────┘    │     │    └─────────┐
      ┌───▼───┐    ┌─────▼─┐ ┌─▼─────┐   ┌────▼──┐
 leaf │10 20 30│◄──►│45 60 70│◄►│85 90 │◄─►│130 140│   keys + values
      └────────┘    └───────┘  └──────┘   └───────┘
                  linked list across the leaves
```

**The "+" in B+ tree means all values live in the leaves.** Internal nodes hold only keys, for routing.

**Three properties follow, and each matters:**

**Higher fanout.** Internal nodes hold no payload, so more keys fit per page, so the tree is shallower.

**Leaves are linked.** **A range scan finds the start, then follows the leaf chain sequentially** — no tree traversal per row. This is why `WHERE created_at BETWEEN ... AND ...` is efficient and why B+ trees beat hash indexes for ranges.

**All leaves are at the same depth.** Every lookup costs the same, which makes performance predictable.

**Balance is maintained on write:** a full leaf **splits** in half, pushing a key up; if the parent is full it splits too, possibly to the root, which is the only way the tree grows a level. **Deletes merge** underfull nodes — though most databases defer merging, tolerating some sparsity.

**Concurrency** uses **latch crabbing** — hold a latch on the child, release the parent once you know no split will propagate. Modern engines use B-link trees, which add a right-sibling pointer so readers never block on a concurrent split.

## Clustered vs secondary

**Covered in [[databases/03-storage-and-page-layout|note 03]], and it's the difference that determines index cost.**

**Clustered (InnoDB primary key)** — the table *is* the tree. Leaves contain the full rows.

**Secondary index** — leaves contain the indexed key plus a pointer to the row.

**What the pointer is matters enormously:**

| | Secondary leaf holds | Lookup cost |
|---|---|---|
| **Postgres (heap)** | `ctid` — (page, slot) | index → heap page |
| **InnoDB (clustered)** | **the primary key** | index → **PK tree traversal** |

> **So in InnoDB every secondary index lookup is two B-tree traversals**, and **a wide primary key inflates every secondary index** — the PK is copied into each one. **A 40-byte natural primary key across six secondary indexes wastes a great deal of space and I/O.** Another argument for narrow surrogate keys.

## Index-only scans

**The optimisation worth designing for.**

If **every column the query needs is in the index**, the database never touches the table:

```sql
CREATE INDEX idx ON orders (customer_id, created_at, total);

SELECT created_at, total FROM orders WHERE customer_id = 42;
-- all three columns are in the index → no heap access
```

**This can be several times faster**, because you skip a random I/O per row.

**Postgres calls it an *index-only scan*, and it needs the visibility map to confirm the page is all-visible** — otherwise it must check the heap for row visibility anyway. **So a table that hasn't been vacuumed recently loses index-only scans**, which is a real and confusing performance regression. → [[databases/09-mvcc-and-concurrency-control|MVCC]]

**`INCLUDE` columns** (Postgres 11+, SQL Server) store extra columns in the leaves **without** making them part of the key — so they don't affect ordering or uniqueness, and don't bloat the internal nodes.

## Composite indexes and the leftmost rule

**An index on `(a, b, c)` is sorted by `a`, then `b` within equal `a`, then `c`.**

**Which means it can serve:**

| Query | Uses index? |
|---|---|
| `WHERE a = 1` | ✅ |
| `WHERE a = 1 AND b = 2` | ✅ |
| `WHERE a = 1 AND b = 2 AND c = 3` | ✅ fully |
| `WHERE b = 2` | ❌ **cannot** |
| `WHERE a = 1 AND c = 3` | ⚠️ uses `a` only, then filters |
| `WHERE a > 1 AND b = 2` | ⚠️ range on `a` stops `b` being useful |

> **The leftmost prefix rule.** Think of a phone book sorted by (surname, forename): finding everyone called "Smith" is easy; finding everyone called "John" requires reading the whole book.
>
> **And note the last row: once you use a range predicate, subsequent columns can't narrow the search** — they're only usable as filters. **So put equality columns before range columns** when ordering a composite index. That single rule fixes a lot of underperforming indexes.

**Ordering guidance:** equality predicates first, then the range column, then columns needed only for output. **Selectivity matters less than people say** — the leftmost rule dominates.

## Index types beyond B-tree

| Type | Good for | Cannot do |
|---|---|---|
| **B-tree** | equality, **ranges**, sorting, prefix `LIKE` | — the default for a reason |
| **Hash** | equality only | ranges, ordering |
| **GIN** | **arrays, JSONB, full-text** — many keys per row | slow to update |
| **GiST** | geometric, ranges, nearest-neighbour | |
| **BRIN** | **huge naturally-ordered tables** — tiny index | unordered data |
| **Bitmap** | low-cardinality columns in OLAP | high update rates |

**BRIN deserves a mention** because it's underused: it stores min/max per block range, so an index on a billion-row time-series table can be **kilobytes** rather than gigabytes. **It only works if the data's physical order correlates with the indexed column** — which is exactly true for append-only time series.

**Partial indexes** index a subset:

```sql
CREATE INDEX ON orders (created_at) WHERE status = 'pending';
```

**If 1% of orders are pending, this index is 1% of the size** and stays hot in memory. **Excellent for queue-like tables**, and a genuinely high-leverage technique.

**Expression indexes** index a computed value — `LOWER(email)` — which is required for the index to be used by `WHERE LOWER(email) = ...`.

## When indexes make things worse

**Every index is a cost**, and this is the half people skip.

**Writes slow down.** Every `INSERT`/`UPDATE`/`DELETE` must maintain every index. **Ten indexes means ten B-tree updates per insert**, plus WAL for each.

**Space.** Indexes commonly exceed the table size in aggregate.

**Buffer pool pressure.** Index pages compete with table pages for memory.

**The planner gets more choices**, and more chances to choose badly.

**When an index won't be used at all:**

- **Low selectivity.** `WHERE active = true` matching 90% of rows — **a sequential scan is genuinely faster**, because random I/O for 90% of rows costs more than reading everything sequentially. **The planner is right to refuse the index**, and this surprises people
- **Function applied to the column.** `WHERE LOWER(email) = 'x'` can't use an index on `email`
- **Implicit type casts** — `WHERE varchar_col = 123` may cast the column, not the literal
- **Leading wildcard** — `LIKE '%foo'` can't use a B-tree prefix. Use trigram (`pg_trgm`) or full-text
- **`OR` across columns** — sometimes better as `UNION` of two indexed queries

**Find unused indexes:**

```sql
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

**Drop them.** An index with zero scans is pure write cost. → [[databases/12-operating-a-database|Operating a Database]]

## Practical notes

**Index your foreign keys.** Most databases don't do it automatically, and **an unindexed FK makes deletes on the parent table scan the child** — a common cause of mysterious lock contention.

**Index what you filter, join and sort on** — in that order of priority.

**Prefer fewer, wider composite indexes** to many single-column ones. One index on `(a, b)` serves `WHERE a` too; two separate indexes serve neither combination well.

**`CREATE INDEX CONCURRENTLY`** in Postgres — a plain `CREATE INDEX` takes a write lock for the duration. On a large production table that's an outage.

**Rebuild bloated indexes** — `REINDEX CONCURRENTLY`.

**Check it's used.** `EXPLAIN (ANALYZE, BUFFERS)`. **Creating an index and not verifying it's used is the most common wasted effort in database tuning.** → [[databases/07-join-algorithms-and-the-optimiser|Reading EXPLAIN]]

---

## Related
- [[databases/05-lsm-trees|LSM Trees]] — the write-optimised alternative
- [[databases/07-join-algorithms-and-the-optimiser|Join Algorithms and the Optimiser]] — how the planner decides to use these
- [[databases/database-design-reference|Database Design Reference]] — §11, index design strategy
- [[databases/README|Databases map]]
