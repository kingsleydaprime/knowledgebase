# Join Algorithms and the Optimiser

**[Advanced]** — The three ways to join two tables, how the planner chooses between them, and why it sometimes chooses catastrophically. You'll learn to read `EXPLAIN ANALYZE` for the one number that diagnoses most bad plans. Every claim about PostgreSQL here is checked by the lab on a real PostgreSQL 18 database.

## Before you start

You can already:

- Read an index scan, an index-only scan, a bitmap scan and a sequential scan in `EXPLAIN (ANALYZE, BUFFERS)`, and say what each costs → [[databases/04-b-trees-and-indexes/index|B-trees and indexes]].
- Write a SQL join and say what it returns.
- Explain a hash table's lookup and why it's about constant time → [[dsa/02-data-structures/03-hash-maps|hash maps]].
- Run Python with `uv`, and have PostgreSQL 16 or later installed locally; the lab creates and deletes its own database, as in the previous lesson.

After this lesson you will be able to:

1. Trace a nested loop, an index nested loop, a hash join and a merge join, and say which suits which sizes and conditions.
2. Read `EXPLAIN ANALYZE` and find the lowest node whose estimated rows differ badly from its actual rows.
3. Name the classic estimation failures (correlated columns, stale statistics, skew, functions) and the fix for each.
4. Take a slow query from a real project, diagnose it, fix it, and record the plan before and after.

**Study route:** sections 1–3 are the algorithms. Stop at the predictions in sections 2, 5 and 7 and try them before reading on. Section 9 is the lab. The practice task is this week's "by Sunday" task.

## The kid version

At home time, 300 children have to be matched with the grown-ups collecting them. One way: each child walks along the whole line of grown-ups looking for theirs. Another: the grown-ups stand in a list sorted by surname, so each child looks them up quickly. A third: everyone splits into 26 groups by the first letter of their surname, and matching happens inside each small group. A fourth: children and grown-ups both line up alphabetically and walk forward together. All four work; which is fastest depends on how many people there are and whether anyone is already in order. The teacher has to pick one before the doors open.

**Where the analogy stops working.** The teacher can count the children. A database planner has to *guess* how many rows each step will produce before running anything, from statistics gathered earlier. When the guess is wrong by a thousand times, it picks the method that was right for the guess, and that's how a query that took 10 ms one day takes an hour the next.

## 1. Why this exists

The shop's order page joins one customer's orders to the customer: 20 rows. The monthly report joins all million orders to all 50,000 customers. Both are written `JOIN customers c ON c.id = o.customer_id`, and they need opposite strategies: the order page should look up one customer through the primary key, and the report should build a hash table of customers once. The database picks the strategy itself, from estimates. When the estimate is right you never think about it. When it's wrong, the report can run as a million index lookups, or the order page can read the whole table. Reading the plan, and knowing why it was chosen, is how you find out which happened.

## Terms used in this lesson

1. **Join**: This is combining rows from two tables where a condition matches, such as an order's `customer_id` equalling a customer's `id`.
2. **Outer side and inner side**: In a join plan, these are the two inputs. The outer side is read once, and the inner side is searched for each outer row. They're unrelated to SQL's `OUTER JOIN`.
3. **Nested loop join**: This is a join that, for each outer row, searches the inner side for matches, either by reading it all or through an index.
4. **Hash join**: This is a join that builds a hash table from one side (the **build** side) and looks up each row of the other side (the **probe** side) in it.
5. **Merge join**: This is a join that walks two inputs already sorted by the join key in step, like merging two sorted lists.
6. **Equi-join**: This is a join whose condition is equality, such as `a.x = b.y`. Hash and merge joins in PostgreSQL need one.
7. **Cardinality**: This is the number of rows a step of a plan produces. The planner's estimate of it is shown as `rows=` in `EXPLAIN`.
8. **Statistics**: These are summaries of each column that `ANALYZE` collects: the number of distinct values, the most common values and how often they occur, and a histogram of the rest.
9. **Selectivity**: This is the share of rows a condition keeps, from 0 to 1.
10. **`work_mem`**: This is PostgreSQL's memory limit for one sort or hash operation. A hash table bigger than it **spills**: it's split into batches written to temporary files.
11. **Keyset pagination**: This is fetching the next page with `WHERE id > last_seen ORDER BY id LIMIT 20`, rather than `OFFSET`, so the database starts reading at the right place.

## 2. The three join algorithms

**Every relational database has these three.** Knowing which one you're looking at explains most of a plan's behaviour.

### Nested loop

```
for each row r in OUTER:
    for each matching row s in INNER:
        emit (r, s)
```

**Cost:** $O(N \times M)$ naively, **but $O(N \times \log M)$ if the inner side has an index** on the join key, because the inner "scan" becomes a lookup.

**Good when:** the outer side is **small** and the inner side has an index. **It's the most common plan in transactional work**: fetch one order, look up its customer.

**Catastrophic when:** the outer side is large and the inner side has no index. **A million-row outer against a million-row inner is $10^{12}$ comparisons.**

> **A nested loop over a big outer input is the single most common cause of a query that "suddenly" takes hours.** The planner chose it believing the outer side would return 5 rows; it returned 500,000. **The plan was reasonable for the estimate and disastrous for the reality.**

### Hash join

```
BUILD:  read the smaller side, hash it into a table on the join key
PROBE:  scan the larger side, look up each row in the hash table
```

**Cost:** $O(N + M)$, **the best asymptotics of the three.** **Good when** both sides are large and it's an **equality** join. **It can't do** inequality joins (`ON a.x < b.y`), because a hash table only answers equality.

**It needs memory** for the build side. **If that doesn't fit in `work_mem`, it spills to disk**, partitioning both inputs by hash and joining one partition at a time. That's **much slower**, and visible in `EXPLAIN ANALYZE` as `Batches: 16` instead of `Batches: 1`, with temporary-file reads and writes. **The build side should be the smaller one**, and choosing wrong is a common result of a bad estimate.

### Merge join

```
sort both inputs by the join key (or use indexes that already provide that order)
walk both in lockstep, like merging two sorted lists
```

**Cost:** $O(N\log N + M\log M)$ if sorting is needed, **$O(N + M)$ if both inputs already arrive sorted.** **Good when** both sides have an index on the join key, or the output must be sorted anyway. **It streams**, so it needs little memory. In principle merge joins can handle some inequality joins, and some databases do; **PostgreSQL's merge join, like its hash join, needs an equality condition.**

**Predict before reading on.** Join 10,000 orders to 1,000 customers on the customer ID. Roughly how many steps does each algorithm take: a nested loop with no index, a nested loop through an index (a sorted list searched by halving), a hash join, and a merge join on inputs already sorted?

<details>
<summary>After your prediction</summary>

The lab counts them: **10,000,000** comparisons for the plain nested loop (N × M); **99,780** steps for the indexed one (about 10,000 lookups of 10 halvings each); **11,000** operations for the hash join (build 1,000, probe 10,000); and **10,999** for the merge join (N + M). All four return the same 10,000 rows. For just one customer's 10 orders, the indexed nested loop takes **100** steps while the hash join still takes **1,010**, because it builds the whole table first. That's why a small outer side means a nested loop.

</details>

| | Nested loop | Hash | Merge |
|---|---|---|---|
| Complexity | $O(N \times M)$ / $O(N\log M)$ with an index | **$O(N+M)$** | $O(N\log N)$, or $O(N+M)$ if sorted |
| Needs an equality condition? | no | **yes** | yes, in PostgreSQL |
| Memory | minimal | **the build side** | minimal |
| Needs sorted input | no | no | **yes (or sorts)** |
| Best for | **small outer + indexed inner** | **large ⋈ large** | **pre-sorted inputs, or ordered output** |

## 3. What PostgreSQL actually chooses

The lab gives PostgreSQL 50,000 customers and a million orders, and reads the plans:

1. **All orders joined to all customers:** a `Hash Join`, building a hash table of the 50,000 customers in **one batch** (2.2 MB, inside the default 4 MB `work_mem`) and probing it with the million orders.
2. **The same with `work_mem = 64kB`:** still a hash join, but in **16 batches**, with thousands of pages written to temporary files and read back.
3. **One customer's orders, with names:** a `Nested Loop`: one primary-key lookup for the customer, and an index lookup for their 20 orders. It reads a few dozen pages.
4. **`ON o.total < c.credit_limit`:** a `Nested Loop` with a join filter, and neither of the others, because the condition isn't equality.
5. **With hash joins switched off for the session (`SET enable_hashjoin = off`):** a `Merge Join` of two index-only scans, which already deliver both sides sorted by customer ID.

## 4. Join order

**This is the genuinely hard part.** Joining $n$ tables has $O(n!)$ possible orders, and they differ enormously in cost, because **intermediate result sizes compound.**

```
 A(1M) ⋈ B(1M) ⋈ C(10)

 (A ⋈ B) ⋈ C   →  an intermediate result of maybe 10M rows, then filtered to a few
 (A ⋈ C) ⋈ B   →  an intermediate result of maybe 10 rows, then joined
```

**Same result. Orders of magnitude apart.** The classic principle: **do the most selective operations first**, so every later step handles less data.

How the planner searches:

- **Dynamic programming**, System R's approach and still used, builds the best plans for progressively larger subsets of the tables. It's exponential, but tractable up to about 12 tables.
- **Genetic or heuristic search** above that. **PostgreSQL's GEQO is randomised**, so plans for a 15-table join can differ between identical runs, which is worth knowing before chasing a "flaky" performance problem.
- **Bushy versus left-deep.** Most planners consider only left-deep trees, where each join's right side is a base table, to shrink the search, at the cost of missing some good bushy plans.

## 5. Cost estimation, and where it fails

**The planner compares plans by estimated cost**, and the estimate is where things go wrong:

$$\text{cost} = \text{pages read} \times \text{page cost} + \text{rows processed} \times \text{CPU cost} + \ldots$$

**PostgreSQL's knobs:** `seq_page_cost` (1.0), `random_page_cost` (4.0 by default), `cpu_tuple_cost`, `cpu_index_tuple_cost`, `effective_cache_size`.

> **`random_page_cost = 4.0` assumes spinning disks.** On SSDs random reads are nearly as cheap as sequential ones, so **the default makes the planner unduly reluctant to use indexes.** Setting it to about **1.1** on SSD-backed storage is one of the highest-value single-line tuning changes, and it's still not the default, for compatibility.

**Statistics drive the row estimates**, collected by `ANALYZE`: the number of distinct values per column, the most common values and their frequencies, a histogram of the rest, and the correlation between physical order and value order. **Selectivity estimation** turns a condition into an expected row count: `WHERE status = 'x'` uses the most-common-values list; `WHERE created_at > '…'` uses the histogram.

**The four classic failures**, and recognising them is most of the diagnostic skill:

1. **Correlated columns.** In words: without being told otherwise, the planner assumes conditions on different columns are independent, so it multiplies their selectivities. When one column determines the other, that underestimates badly.

   $$P(\text{city} = \text{London} \wedge \text{country} = \text{UK}) \overset{\text{assumed}}{=} P(\text{city}) \times P(\text{country})$$

2. **Stale statistics.** A table grows a hundredfold after its last `ANALYZE`, and the planner still thinks it's small. Autovacuum normally keeps statistics fresh, but after a bulk load, run `ANALYZE` yourself.
3. **Skewed data.** 99% of rows have `status = 'complete'`. A single average is wrong for both the common and the rare values; the most-common-values list helps, if it's long enough.
4. **Expressions and functions.** `WHERE f(x) = 5` has no statistics at all, so the planner falls back to a fixed guess (often 0.5%). An expression index carries statistics, and fixes it.

**Predict before reading on.** 30,000 addresses in 10 cities, 3,000 in each. London, Manchester and Leeds are in the UK, so the UK is 30% of addresses. How many rows does PostgreSQL *estimate* for `WHERE city = 'London' AND country = 'UK'`, and how many are there?

<details>
<summary>After your prediction</summary>

It estimates **900**: 30,000 × 10% × 30%. There are **3,000**, because every London address is in the UK. A threefold underestimate is mild; with more conditions it compounds, and an underestimate is what turns a hash join into a nested loop that never finishes. **The fix:** `CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses`, then `ANALYZE`. The lab checks that the estimate becomes exactly **3,000**. Extended statistics (PostgreSQL 10+) are underused, and they directly solve a real class of bad plans.

</details>

## 6. When the planner is wrong

**Diagnose first**, always:

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

**Compare `rows=` (estimated) with `actual rows=` on every node.** A large difference at some node is the root cause, and everything above it inherited the bad assumption. **Find the *lowest* node with a bad estimate**; that's where to fix it. Note that for a node inside a loop, `actual rows` is per loop, so multiply by `loops` before comparing.

**Then, in rough order of preference:**

1. **`ANALYZE` the table.** It's free, and fixes the commonest case.
2. **Raise the statistics target** for a skewed column: `ALTER TABLE t ALTER COLUMN c SET STATISTICS 1000;` (the default is 100). More buckets give a finer histogram and a longer most-common-values list.
3. **`CREATE STATISTICS`** for correlated columns.
4. **Add or fix an index**, especially a composite one matching the condition's order → [[databases/04-b-trees-and-indexes/index|B-trees and indexes]].
5. **Rewrite the query.** Turn a correlated subquery into a join; split an `OR` into a `UNION`; use `LATERAL` for top-N-per-group.
6. **Tune the cost constants**: `random_page_cost` for SSDs, `effective_cache_size` to reflect the real memory.
7. **Raise `work_mem`** if hash joins or sorts spill. It's **per operation, not per connection**: a query with three sorts can use three times `work_mem`, on every connection running it.
8. **Last resort: force the plan.** PostgreSQL has no hints by design. You get blunt session settings like `enable_nestloop = off`, or the `pg_hint_plan` extension. MySQL, Oracle and SQL Server have real hints.

> **PostgreSQL's refusal to add hints is a deliberate and contested design decision.** The argument: hints freeze a plan that was right for last year's data. The counter-argument: sometimes you know something the planner can't, and the query has to work *today*. **Both are right**, which is why the extension exists.

## 7. Pagination: the cost you can't see in the query

**Predict before reading on.** `SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20` returns 20 rows. How many rows does PostgreSQL read to produce them? And for `WHERE id > 100000 ORDER BY id LIMIT 20`?

<details>
<summary>After your prediction</summary>

The `OFFSET` query reads **100,020** rows through the primary-key index, about 800 pages, and throws away the first 100,000. The keyset query reads **20** rows and 4 pages, because the index search starts at `id > 100000`. The cost of `OFFSET` grows with the page number; keyset pagination costs the same for page 1 and page 5,000. The lab checks both. **Use keyset pagination** for anything users can page deep into, passing the last seen ID (and any tie-breaking column) to the next request.

</details>

## 8. Practical notes

- **Estimated against actual rows is the diagnostic.** Learn to read that one comparison before anything else.
- **Set `random_page_cost = 1.1` on SSDs.**
- **`ANALYZE` after bulk loads and large migrations.** Autovacuum is triggered by thresholds of changed rows, and can lag badly after an unusual burst of writes.
- **Watch for `Batches: N` above 1** on hash nodes and `Sort Method: external` on sorts; both mean a spill to disk.
- **Test plans against production-sized data.** A plan chosen for 1,000 rows tells you nothing about 10 million, and **plan changes at scale are the commonest "it worked in staging" failure.**

## 9. The lab: join algorithms counted, and PostgreSQL's choices checked

`joins.py` writes out the nested loop, the index nested loop, the hash join and the merge join, each counting its work, plus the independence estimate and the pagination arithmetic. `test_joins.py` checks they give the same rows and counts their steps. `test_postgres.py` loads 50,000 customers, a million orders and 30,000 addresses into a throwaway PostgreSQL, and checks every plan in sections 3, 5 and 7 by reading `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`. It uses the same [`with-postgres.sh`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/shared) as the previous lesson: a temporary cluster with autovacuum and parallel query off, so plans repeat exactly.

```python
"""The three join algorithms, written out, each counting its work; and the arithmetic of two classic estimation
failures. Rows are (key, value) pairs; every join returns (outer value, inner value) pairs for matching keys."""
from collections import defaultdict


def nested_loop(outer: list, inner: list) -> tuple[list, int]:
    """For every outer row, look at every inner row: N × M comparisons."""
    out, comparisons = [], 0
    for ok, ov in outer:
        for ik, iv in inner:
            comparisons += 1
            if ok == ik:
                out.append((ov, iv))
    return out, comparisons


def index_nested_loop(outer: list, inner_sorted: list) -> tuple[list, int]:
    """The inner side has an index (here, a sorted list searched by bisection): about N × log₂ M steps."""
    keys = [k for k, _ in inner_sorted]
    out, steps = [], 0
    for ok, ov in outer:
        lo, hi = 0, len(keys)
        while lo < hi:  # find the first inner key >= ok
            steps += 1
            mid = (lo + hi) // 2
            if keys[mid] < ok:
                lo = mid + 1
            else:
                hi = mid
        while lo < len(keys) and keys[lo] == ok:
            out.append((ov, inner_sorted[lo][1]))
            lo += 1
    return out, steps


def hash_join(outer: list, inner: list) -> tuple[list, int]:
    """Build a hash table on the inner (smaller) side, then probe it once per outer row: N + M operations.
    Equality only: a hash table can't answer 'less than'."""
    table = defaultdict(list)
    for ik, iv in inner:  # build
        table[ik].append(iv)
    out = []
    for ok, ov in outer:  # probe
        out.extend((ov, iv) for iv in table.get(ok, []))
    return out, len(inner) + len(outer)


def merge_join(outer_sorted: list, inner_sorted: list) -> tuple[list, int]:
    """Both sides sorted by key: walk them together like merging two sorted lists, about N + M steps."""
    out, steps, i, j = [], 0, 0, 0
    while i < len(outer_sorted) and j < len(inner_sorted):
        steps += 1
        ok, ik = outer_sorted[i][0], inner_sorted[j][0]
        if ok < ik:
            i += 1
        elif ok > ik:
            j += 1
        else:
            j_end = j
            while j_end < len(inner_sorted) and inner_sorted[j_end][0] == ok:  # every inner row with this key
                out.append((outer_sorted[i][1], inner_sorted[j_end][1]))
                j_end += 1
            i += 1  # the next outer row may have the same key, so j stays where the group starts
    return out, steps


def independent_estimate(rows: int, *selectivities: float) -> float:
    """What a planner assumes for `a AND b` without extended statistics: the selectivities multiply."""
    estimate = rows
    for s in selectivities:
        estimate *= s
    return estimate


def rows_read_for_page(offset: int, limit: int, keyset: bool) -> int:
    """OFFSET reads and discards every skipped row; keyset pagination (WHERE id > last_seen) starts at the right place."""
    return limit if keyset else offset + limit
```

```python
import unittest

from joins import hash_join, index_nested_loop, independent_estimate, merge_join, nested_loop, rows_read_for_page

# 10,000 orders across 1,000 customers: the order's customer is its key.
ORDERS = [(1 + i % 1_000, f"order {i}") for i in range(10_000)]
CUSTOMERS = [(c, f"customer {c}") for c in range(1, 1_001)]


class Joins(unittest.TestCase):
    def test_all_three_algorithms_give_the_same_answer(self):
        expected = sorted(nested_loop(ORDERS, CUSTOMERS)[0])
        self.assertEqual(len(expected), 10_000)
        self.assertEqual(sorted(index_nested_loop(ORDERS, CUSTOMERS)[0]), expected)
        self.assertEqual(sorted(hash_join(ORDERS, CUSTOMERS)[0]), expected)
        self.assertEqual(sorted(merge_join(sorted(ORDERS), CUSTOMERS)[0]), expected)

    def test_they_differ_enormously_in_work(self):
        self.assertEqual(nested_loop(ORDERS, CUSTOMERS)[1], 10_000_000)  # N × M
        self.assertEqual(index_nested_loop(ORDERS, CUSTOMERS)[1], 99_780)  # about N × log₂ M = 10,000 × 10
        self.assertEqual(hash_join(ORDERS, CUSTOMERS)[1], 11_000)  # build 1,000, probe 10,000
        self.assertEqual(merge_join(sorted(ORDERS), CUSTOMERS)[1], 10_999)  # about N + M, once both are sorted

    def test_a_small_outer_side_makes_the_indexed_nested_loop_cheapest(self):
        one_customer = [row for row in ORDERS if row[0] == 42]  # 10 orders
        self.assertEqual(index_nested_loop(one_customer, CUSTOMERS)[1], 100)  # 10 lookups of 10 steps
        self.assertEqual(hash_join(one_customer, CUSTOMERS)[1], 1_010)  # still builds the whole table

    def test_correlated_columns_fool_the_independence_assumption(self):
        # 30,000 addresses in 10 cities; London is 10% of them, the UK is 30%, and every London address is in the UK.
        self.assertEqual(round(independent_estimate(30_000, 0.1, 0.3)), 900)  # what the planner assumes
        self.assertEqual(round(independent_estimate(30_000, 0.1)), 3_000)  # the truth: London implies the UK

    def test_offset_pagination_reads_everything_it_skips(self):
        self.assertEqual(rows_read_for_page(100_000, 20, keyset=False), 100_020)
        self.assertEqual(rows_read_for_page(100_000, 20, keyset=True), 20)


if __name__ == "__main__":
    unittest.main()
```

```python
"""How PostgreSQL 18 chooses joins, and where its estimates go wrong. Run through ../shared/with-postgres.sh."""
import json
import unittest

import psycopg

SETUP = """
CREATE TABLE customers AS
SELECT i AS id, 'Customer ' || i AS name, i * 37 % 5000 AS credit_limit FROM generate_series(1, 50000) i;
ALTER TABLE customers ADD PRIMARY KEY (id);
CREATE TABLE orders AS
SELECT i AS id, 1 + i % 50000 AS customer_id, (i::bigint * 7919 % 10000)::int AS total FROM generate_series(1, 1000000) i;
ALTER TABLE orders ADD PRIMARY KEY (id);
CREATE INDEX orders_customer_id ON orders (customer_id);
CREATE TABLE addresses AS
SELECT i AS id,
       (ARRAY['London','Manchester','Leeds','Paris','Lyon','Lille','Berlin','Munich','Hamburg','Cologne'])[1 + i % 10] AS city,
       (ARRAY['UK','UK','UK','France','France','France','Germany','Germany','Germany','Germany'])[1 + i % 10] AS country
FROM generate_series(1, 30000) i;
VACUUM ANALYZE customers;
VACUUM ANALYZE orders;
ANALYZE addresses
"""


def nodes(plan: dict):
    yield plan
    for child in plan.get("Plans", []):
        yield from nodes(child)


class Postgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = psycopg.connect(autocommit=True)
        for statement in SETUP.split(";\n"):  # one at a time: VACUUM can't run inside a multi-statement call
            cls.db.execute(statement)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def explain(self, sql: str, analyze: bool = True) -> list[dict]:
        options = "ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON" if analyze else "FORMAT JSON"
        row = self.db.execute(f"EXPLAIN ({options}) {sql}").fetchone()
        plan = row[0] if isinstance(row[0], list) else json.loads(row[0])
        return list(nodes(plan[0]["Plan"]))

    def types(self, plan: list[dict]) -> list[str]:
        return [n["Node Type"] for n in plan]

    def test_large_to_large_on_equality_is_a_hash_join(self):
        plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id")
        self.assertIn("Hash Join", self.types(plan))
        hash_node = next(n for n in plan if n["Node Type"] == "Hash")
        self.assertEqual(hash_node["Hash Batches"], 1)  # the 50,000 customers fit in work_mem (4 MB by default)

    def test_too_little_memory_and_the_hash_join_spills_to_disk(self):
        self.db.execute("SET work_mem = '64kB'")
        try:
            plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id")
            hash_node = next(n for n in plan if n["Node Type"] == "Hash")
            self.assertEqual(hash_node["Hash Batches"], 16)  # split into 16 partitions, joined one at a time
            self.assertGreater(plan[0]["Temp Written Blocks"], 0)  # written to temporary files and read back
        finally:
            self.db.execute("RESET work_mem")

    def test_a_small_outer_side_is_a_nested_loop_through_an_index(self):
        plan = self.explain("SELECT c.name, o.total FROM orders o JOIN customers c ON c.id = o.customer_id WHERE o.customer_id = 42")
        self.assertEqual(plan[0]["Node Type"], "Nested Loop")
        self.assertEqual(plan[0]["Actual Rows"], 20)
        self.assertLess(plan[0]["Shared Hit Blocks"] + plan[0]["Shared Read Blocks"], 50)  # a few dozen pages, not thousands

    def test_an_inequality_join_can_only_be_a_nested_loop(self):
        plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON o.total < c.credit_limit WHERE c.id < 10 AND o.id < 1000", analyze=False)
        self.assertIn("Nested Loop", self.types(plan))
        self.assertFalse({"Hash Join", "Merge Join"} & set(self.types(plan)))  # neither works on '<' in PostgreSQL

    def test_a_merge_join_when_hashing_is_ruled_out_and_both_sides_come_sorted(self):
        self.db.execute("SET enable_hashjoin = off")  # a session setting for experiments, never for production
        try:
            plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id", analyze=False)
            merge = next(n for n in plan if n["Node Type"] == "Merge Join")
            self.assertEqual({p["Node Type"] for p in merge["Plans"]}, {"Index Only Scan"})  # sorted by the indexes: no sort
        finally:
            self.db.execute("RESET enable_hashjoin")

    def test_correlated_columns_are_underestimated_until_the_planner_is_told(self):
        query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'"
        before = self.explain(query)[0]
        self.assertEqual((before["Plan Rows"], before["Actual Rows"]), (900, 3000))  # 10% × 30%: assumed independent
        self.db.execute("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses")
        self.db.execute("ANALYZE addresses")
        after = self.explain(query)[0]
        self.assertEqual((after["Plan Rows"], after["Actual Rows"]), (3000, 3000))  # city decides country: now exact

    def test_offset_reads_every_row_it_skips_keyset_pagination_does_not(self):
        offset = self.explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20")
        keyset = self.explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20")
        self.assertEqual((offset[1]["Actual Rows"], keyset[1]["Actual Rows"]), (100020, 20))  # the scans under each Limit
        self.assertGreater(offset[0]["Shared Hit Blocks"] + offset[0]["Shared Read Blocks"], 800)
        self.assertLess(keyset[0]["Shared Hit Blocks"] + keyset[0]["Shared Read Blocks"], 10)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** the code is in [`databases/07-join-algorithms-and-the-optimiser/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/python). From the vault root, `python3 labs/run.py join-algorithms-and-the-optimiser/python` runs everything and checks this page still shows the same code. It needs PostgreSQL 16 or later installed. Expect 12 passing tests in under ten seconds.

## Common pitfalls

1. **Reading only the top line of a plan.** The total time is at the top; the cause is at the lowest node where estimated and actual rows part ways.
2. **Forgetting `loops`.** A node showing 20 actual rows with `loops=50000` produced a million.
3. **Never running `ANALYZE` after a bulk load.** The planner plans for the table you used to have.
4. **Assuming columns are independent.** City and country, model and manufacturer, status and closed date: tell the planner with `CREATE STATISTICS`.
5. **Raising `work_mem` globally to fix one query.** It's per operation per connection; a busy server can run out of memory. Raise it for the session or the role that needs it.
6. **`OFFSET` pagination over large tables.** It reads everything it skips.
7. **Leaving `enable_*` settings off.** They're for experiments, not production fixes.

## Check your understanding

1. A plan shows a nested loop whose outer side was estimated at 5 rows and returned 400,000. What went wrong, and where do you start fixing it?
2. Why can't PostgreSQL use a hash join for `ON a.price < b.budget`?
3. A hash node shows `Batches: 32`. What does that mean, and what are two ways to fix it?
4. Why does the planner estimate 900 rows for London addresses in the UK, and what makes it estimate 3,000?
5. A table had 1,000 rows at its last `ANALYZE` and now has 5 million. What kinds of bad plan might you see?
6. Page 5,000 of a product list, 20 per page, is slow with `OFFSET`. How many rows does it read, and how would you rewrite it?

<details>
<summary>Answers — after your attempt</summary>

1. The planner underestimated the outer side by 80,000 times, so it chose a nested loop that's cheap for 5 rows and runs the inner search 400,000 times. Start at the lowest node where estimated and actual rows diverge: usually missing or stale statistics (`ANALYZE`), correlated conditions (`CREATE STATISTICS`), or a function hiding the column from the statistics (an expression index).
2. A hash table finds rows with exactly equal keys. "Less than" can't be answered by hashing, so the planner needs a nested loop, which can test any condition.
3. The hash table didn't fit in `work_mem`, so it was split into 32 partitions written to temporary files and joined one at a time. Fix: raise `work_mem` for that session or role, or make the build side smaller, by filtering earlier, selecting fewer columns, or getting the planner to build on the smaller side by fixing its estimates.
4. Without extended statistics it multiplies the selectivities, 10% × 30% of 30,000, as if city and country were independent. With `CREATE STATISTICS … (dependencies)` and a new `ANALYZE`, it knows city determines country, so the UK condition adds nothing, and the estimate is 10% of 30,000.
5. Plans built for a tiny table: nested loops or index scans where a hash join or sequential scan would be right, hash joins building on the wrong side, and estimates far too low on every node above that table. Run `ANALYZE`.
6. It reads 100,000 rows (99,980 skipped plus 20 returned), and gets slower with every page. Rewrite as keyset pagination: `WHERE (name, id) > (:last_name, :last_id) ORDER BY name, id LIMIT 20`, with an index on `(name, id)`.

</details>

## Practice — independent task (this week's "by Sunday" task)

**Fix one slow query from a real project, with evidence.**

1. Pick a project with a PostgreSQL database: the flagship, nextvibe, or the direct-debit sandbox. Find a query that's slow, or one you suspect: a list page, a report, a search. Run it against realistic data; if the development database is small, generate more with `generate_series`, as the lab does.
2. Run `EXPLAIN (ANALYZE, BUFFERS)` and save the output.
3. Find the lowest node whose estimated and actual rows differ, or the node with the most buffers, and write one sentence on why.
4. Fix it with the least invasive change that works: `ANALYZE`, an index, extended statistics, a rewrite, keyset pagination.
5. Run it again and save the new plan.

**A smaller step first:** in the lab, add a fourth condition to the addresses query that's independent of the others, such as `id % 2 = 0`. Predict the estimate with and without the extended statistics before running it.

**Done when:** you have the query, both plans, the diagnosing node named with its estimated and actual rows, the change you made, and the before and after times and buffers, written up in your project's learning notes.

## Before moving on

You can trace the three join algorithms and say which fits which sizes and conditions, read a plan for its estimate-against-actual rows, name the classic estimation failures and their fixes, and fix a real slow query with evidence.

**Recap.** A nested loop is right for a small outer side with an indexed inner side, and catastrophic for a large one; a hash join is right for large equality joins, if the build side fits in `work_mem`; a merge join suits inputs already sorted. PostgreSQL needs equality for both hash and merge joins. The planner picks from estimates built on statistics, and its classic failures are correlated columns, stale statistics, skew and functions: in the lab, 900 estimated against 3,000 actual, fixed exactly by `CREATE STATISTICS`. Diagnose by finding the lowest node where `rows=` and `actual rows=` differ, then fix the cheapest way: `ANALYZE`, statistics, an index, a rewrite. And `OFFSET` reads everything it skips, so page with keysets.

**Next.** Week 6: [[databases/08-transactions-and-acid/index|transactions and ACID]] and [[databases/09-mvcc-and-concurrency-control/index|isolation and MVCC]], which change data safely while other queries read it.

## Related

- [[databases/06-the-query-pipeline|The query pipeline]]: where planning sits
- [[databases/04-b-trees-and-indexes/index|B-trees and indexes]]: the access methods being chosen between
- [[databases/sql-reference|SQL reference]]: §26 on writing queries the planner handles well
- [[databases/index|Databases map]]
