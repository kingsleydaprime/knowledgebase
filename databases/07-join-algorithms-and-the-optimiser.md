# Join Algorithms and the Optimiser

**[Advanced]** — The three ways to join, how the planner chooses, and why it sometimes chooses catastrophically.

## The three join algorithms

**Every relational database has these three.** Knowing which one you're looking at in a plan explains most performance behaviour.

### Nested loop

```
for each row r in OUTER:
    for each matching row s in INNER:
        emit (r, s)
```

**Cost:** $O(N \times M)$ naively — **but $O(N \times \log M)$ if the inner side has an index** on the join key, because the inner "scan" becomes a lookup.

**Good when:** the outer side is **small**, and the inner has an index. **The dominant plan in OLTP** — fetch one order, look up its customer.

**Catastrophic when:** the outer side is large and the inner has no index. **A million-row outer against a million-row inner is $10^{12}$ comparisons.**

> **Nested loop over a big outer input is the single most common cause of a query that "suddenly" takes hours.** The planner chose it believing the outer would return 5 rows; it returned 500,000. **The plan was reasonable for the estimate and disastrous for the reality.**

### Hash join

```
BUILD:  read the smaller side, hash it into a table on the join key
PROBE:  scan the larger side, look up each row in the hash table
```

**Cost:** $O(N + M)$. **The best asymptotics of the three.**

**Good when:** both sides are large, and it's an **equality** join.

**Cannot do:** inequality joins (`ON a.x < b.y`) — a hash table only answers equality.

**Requires memory** for the build side. **If it doesn't fit in `work_mem`, it spills to disk** as a grace/hybrid hash join, partitioning both inputs by hash and joining partition-wise. **Much slower**, and visible in `EXPLAIN ANALYZE` as `Batches: 8` rather than `Batches: 1`.

**The build side should be the smaller one**, and choosing wrong is a common consequence of a bad estimate.

### Merge join

```
sort both inputs by the join key (or use indexes that already provide it)
walk both in lockstep, like merging two sorted lists
```

**Cost:** $O(N\log N + M\log M)$ if sorting is needed, **$O(N + M)$ if both inputs already arrive sorted.**

**Good when:** inputs are already sorted — **both sides have an index on the join key** — or the output needs to be sorted anyway. **Handles inequality joins**, unlike hash.

**Memory-efficient** — it streams, so it doesn't need to hold either side.

**The summary table:**

| | Nested loop | Hash | Merge |
|---|---|---|---|
| Complexity | $O(NM)$ / $O(N\log M)$ | **$O(N+M)$** | $O(N\log N)$ |
| Equality only? | no | **yes** | no |
| Memory | minimal | **build side** | minimal |
| Needs sorted input | no | no | **yes (or sorts)** |
| Best for | **small outer + indexed inner** | **large ⋈ large** | **pre-sorted, or ordered output** |

## Join order

**The genuinely hard part.**

**Joining $n$ tables has $O(n!)$ possible orders**, and they differ enormously in cost — because **intermediate result sizes compound.**

```
 A(1M) ⋈ B(1M) ⋈ C(10)

 (A ⋈ B) ⋈ C   →  intermediate of maybe 10M rows, then filter to few
 (A ⋈ C) ⋈ B   →  intermediate of maybe 10 rows, then join
```

**Same result. Orders of magnitude apart.**

**The classic principle: perform the most selective operations first**, so every subsequent operator handles less data.

**How the planner searches:**

**Dynamic programming** (System R's approach, still used) — build up optimal plans for progressively larger subsets. Exponential, but tractable to ~12 tables.

**Genetic / heuristic search** above that threshold. **Postgres's GEQO is randomised**, so plans for 15-table joins can differ between identical runs — which is worth knowing before you chase a "flaky" performance problem.

**Bushy vs left-deep** — most planners restrict to left-deep trees (each join's right side is a base table) to shrink the search space, at the cost of missing some good bushy plans.

## Cost estimation

**The planner compares plans by estimated cost**, and the estimate is where things go wrong.

$$\text{cost} = \text{(pages read)} \times \text{page cost} + \text{(rows processed)} \times \text{cpu cost} + \ldots$$

**Postgres's knobs:** `seq_page_cost` (1.0), `random_page_cost` (4.0 by default), `cpu_tuple_cost`, `cpu_index_tuple_cost`, `effective_cache_size`.

> **`random_page_cost = 4.0` assumes spinning disks.** On SSDs random I/O is nearly as cheap as sequential, so **the default makes the planner irrationally reluctant to use indexes.** Setting it to **1.1** on SSD-backed storage is one of the highest-value single-line tuning changes available, and it's still not the default for compatibility reasons.

**Statistics** drive the row estimates, collected by `ANALYZE`:

- **`n_distinct`** — number of distinct values per column
- **Most common values** and their frequencies
- **A histogram** of the value distribution
- **Correlation** between physical order and value order (which is what makes BRIN and index scans attractive)

**Selectivity estimation** turns a predicate into an expected row count. `WHERE status = 'x'` uses the MCV list; `WHERE created_at > '...'` uses the histogram.

### Where estimation fails

**The four classic failures**, and recognising them is most of the diagnostic skill:

**Correlated columns.** The planner assumes independence:

$$P(\text{city} = \text{'London'} \wedge \text{country} = \text{'UK'}) = P(\text{city}) \times P(\text{country})$$

**But every London is in the UK.** The true selectivity is that of `city` alone; the estimate is far smaller. **Underestimates cascade into nested-loop choices that then explode.**

**The fix:** `CREATE STATISTICS` (Postgres 10+) declares the dependency explicitly. **Underused, and it directly solves a real class of bad plans.**

**Stale statistics.** A table grows 100× since the last `ANALYZE` and the planner still thinks it's small. **Autovacuum handles this normally — until a bulk load, after which you should `ANALYZE` manually.**

**Skewed data.** 99% of rows have `status = 'complete'`. The average-case estimate is wrong for both the common and rare values.

**Expressions and functions.** `WHERE f(x) = 5` has no statistics at all — the planner falls back to a fixed guess (often 0.5% selectivity). **Expression indexes carry statistics** and fix this.

## When the planner is wrong

**Diagnosis first**, always:

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

**Compare `rows=` (estimated) with `actual rows=`.** A large divergence at some node is the root cause; everything above it inherited the bad assumption. **Find the *lowest* node with a bad estimate** — that's where to fix it.

**Then, in rough order of preference:**

**1. `ANALYZE` the table.** Free, and it fixes the commonest case.

**2. Raise the statistics target** for a skewed column:
```sql
ALTER TABLE t ALTER COLUMN c SET STATISTICS 1000;
```
Default is 100; more buckets means a finer histogram.

**3. `CREATE STATISTICS`** for correlated columns.

**4. Add or fix an index** — especially a composite one matching the predicate order.

**5. Rewrite the query.** Turn a correlated subquery into a join; split an `OR` into a `UNION`; add a `LATERAL` for a top-N-per-group.

**6. Tune the cost constants** — `random_page_cost` for SSDs, `effective_cache_size` to reflect actual RAM.

**7. Adjust `work_mem`** if you're spilling to disk. **Per-operation, not per-connection** — a query with three sorts can use 3× `work_mem`, per connection.

**8. Last resort — force the plan.** Postgres has no hints by design; you get `enable_nestloop = off` as a blunt session-level instrument, or the `pg_hint_plan` extension. MySQL, Oracle and SQL Server have real hints.

> **Postgres's refusal to add hints is a deliberate and contested design decision.** The argument: hints freeze a plan that was right for last year's data. The counter-argument: sometimes you know something the planner cannot, and you need the query to work *today*. **Both are correct**, which is why the extension exists.

## Practical notes

**Estimated vs actual rows is the diagnostic.** Learn to read that one number before anything else.

**Set `random_page_cost = 1.1` on SSDs.** Genuinely high-leverage.

**`ANALYZE` after bulk loads and large migrations.** Autovacuum is triggered by row-change thresholds and can lag badly after an unusual write burst.

**Watch for `Batches: N > 1`** on hash joins and `Sort Method: external` — both mean a disk spill.

**Beware `OFFSET` for pagination.** `OFFSET 100000` reads and discards 100,000 rows. **Use keyset pagination** — `WHERE id > :last_id ORDER BY id LIMIT 20` — which is $O(\log n)$ regardless of depth.

**Test plans against production-sized data.** A plan chosen on 1,000 rows tells you nothing about behaviour at 10 million, and **plan changes at scale are the commonest "it worked in staging" failure.**

---

## Related
- [[databases/06-the-query-pipeline|The Query Pipeline]] — where planning sits
- [[databases/04-b-trees-and-indexes|B-Trees and Indexes]] — the access methods being chosen between
- [[databases/sql-reference|SQL Reference]] — §26 on writing queries the planner handles well
- [[databases/README|Databases map]]
