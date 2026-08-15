# The Query Pipeline

**[Intermediate → Advanced]** — What happens between typing a query and getting rows back.

## The stages

```
 SQL text
    │
    ▼  PARSE          syntax → parse tree
    ▼  BIND/ANALYSE   resolve names, types, permissions
    ▼  REWRITE        expand views, apply rules, simplify
    ▼  PLAN           choose a physical plan (the expensive part)
    ▼  EXECUTE        run the plan operator by operator
 rows
```

**It's a compiler.** Parse, semantic analysis, optimisation, code generation, execution — **the same pipeline as [[foundations/compilers/01-what-a-compiler-is|a language compiler]]**, with a cost-based optimiser doing what register allocation and instruction selection do there.

## Parse

**SQL text → parse tree.** Standard lexing and recursive-descent or LALR parsing. → [[foundations/compilers/03-parsing|Parsing]]

**Only syntax is checked here.** `SELECT * FROM no_such_table` parses fine — the table's existence isn't a syntactic question.

**Errors at this stage are the good kind**: cheap and unambiguous.

## Bind and analyse

**Resolve every name against the catalog:**

- Do these tables and columns exist?
- **Type checking** — is `WHERE age > 'abc'` valid?
- **Permissions** — may this user read this table?
- Resolve `*` into an explicit column list
- Insert **implicit casts**

> **Implicit casts are a common silent performance bug.** `WHERE varchar_col = 12345` may cast the *column* rather than the literal, and **a function applied to a column disables the index on it.** The query works, returns correct rows, and does a sequential scan. **`EXPLAIN` is how you catch it.** → [[databases/04-b-trees-and-indexes|When indexes aren't used]]

## Rewrite

**Transformations that don't depend on cost** — always improvements:

**View expansion.** A view is substituted inline. **This is why a query over nested views can produce a surprising plan** — the planner sees the fully expanded tree, not your tidy abstraction.

**Subquery flattening.** Uncorrelated subqueries and many `IN`/`EXISTS` forms become joins, which the optimiser handles far better.

**Constant folding.** `WHERE x > 2 + 3` becomes `WHERE x > 5`.

**Predicate simplification**, and contradiction detection — `WHERE 1 = 0` can skip the scan entirely.

**Partition pruning** — with a partitioned table, drop partitions the predicate excludes.

**Predicate pushdown** — move filters as close to the scan as possible. **The single highest-value rewrite**, because it shrinks the input to everything above it. → [[databases/02-the-relational-model|Relational algebra equivalences]]

## Plan

**The expensive and interesting stage**, covered fully in the next note. In outline:

**Enumerate** candidate physical plans — which access method per table, which join algorithm, which join order.

**Estimate** the cost of each, using statistics about the data.

**Choose** the cheapest.

**The search space is enormous.** $n$ tables have $O(n!)$ join orders before you multiply by algorithm choices. **Postgres switches from exhaustive dynamic-programming search to a genetic algorithm above 12 tables** (`geqo_threshold`) — which means **plans for very large joins are non-deterministic and can vary between runs.**

**Plan caching** — prepared statements skip parse and plan on repeated execution. **The trade is that a cached generic plan may be worse than a fresh one for a particular parameter value.** Postgres tries five custom plans before deciding whether to switch to a generic one; `plan_cache_mode` forces it either way.

> **Parameter sniffing** is the corresponding SQL Server problem: the plan is built for the first parameter value seen and reused for all others. **A plan optimised for `status = 'rare'` is catastrophic for `status = 'common'`.** Real, well-known, and the reason `OPTION (RECOMPILE)` exists.

## Execute

**The plan is a tree of operators**, each producing rows for its parent.

```
        Aggregate
            │
        Hash Join
        ╱       ╲
  Seq Scan    Index Scan
  (orders)    (customers)
```

**Three execution models:**

**Volcano / iterator model** — each operator implements `next()`, pulling one row from its children. **Simple, composable, and the classic design.** Its cost is one virtual call per row per operator, which dominates at analytical scale.

**Vectorised** — `next()` returns a *batch* (typically 1,000+ values), amortising the call overhead and enabling SIMD. **What every modern analytical engine uses** — DuckDB, ClickHouse, Snowflake. → [[foundations/computer-architecture/03-instruction-sets|SIMD]]

**Compiled** — generate machine code for the whole plan via LLVM, eliminating interpretation entirely. **Postgres JITs expression evaluation for expensive queries**; HyPer and Umbra compile whole pipelines. → [[foundations/compilers/11-jit-compilation|JIT Compilation]]

**Pipelining vs blocking** is the distinction that matters for latency:

**Pipelined operators** stream — filters, projections, nested loop joins. **The first row can be returned immediately.**

**Blocking operators** must consume all input first — sorts, hash-join builds, aggregations without an index.

> **This is what `LIMIT` interacts with.** `SELECT ... LIMIT 10` over a pipelined plan stops after 10 rows. Over a plan with a sort, **the entire input must be sorted first.** It's why adding `ORDER BY` to a `LIMIT` query can change its cost by orders of magnitude — and why a "top N" query wants an index that provides the order.

**Memory limits** — `work_mem` in Postgres. **Exceed it and sorts and hashes spill to disk**, which is dramatically slower. `EXPLAIN ANALYZE` shows `Sort Method: external merge Disk: 40MB`, and that line is often the whole answer to "why is this slow".

## Reading a plan

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

**`EXPLAIN` alone shows the estimated plan. `ANALYZE` actually runs it and reports reality.** Always use `ANALYZE` when investigating — **and be careful, because it executes the statement**, including writes. Wrap it in a transaction you roll back.

**`BUFFERS` shows pages hit vs read**, which distinguishes "slow because of I/O" from "slow because of CPU".

**What to look for, in order:**

**Estimated vs actual rows.** `(cost=... rows=100) (actual rows=1000000)` — **a 10,000× misestimate means the whole plan above it is built on a false premise.** This is the single most useful signal in a plan, and it points at stale or insufficient statistics. → [[databases/07-join-algorithms-and-the-optimiser|Statistics]]

**Sequential scan on a large table** where you expected an index.

**Nested loop with a large outer input** — usually a misestimate.

**External merge / disk spills** — raise `work_mem` or reduce the data.

**The actual time distribution** — find the operator consuming the time, not the one at the top.

**Tools:** `explain.depesz.com` and `explain.dalibo.com` render plans far more readably than raw text, and `auto_explain` logs plans for slow queries in production.

## Where time actually goes

**Worth knowing so you look in the right place:**

| Stage | Typical share |
|---|---|
| Parse + bind | negligible |
| **Plan** | **can dominate for short queries** — sub-millisecond queries planned every time |
| **Execute** | dominates for anything substantial |

**For an OLTP workload of tiny queries, planning overhead is real** — which is the argument for prepared statements.

**And for many applications the database isn't the bottleneck at all**: network round trips, connection setup, and ORM overhead frequently exceed query time. **N+1 queries are the classic case** — 100 fast queries beat one slow query on paper and lose badly in practice, because each pays a round trip. → [[databases/12-operating-a-database|N+1 and ORMs]]

---

## Related
- [[databases/07-join-algorithms-and-the-optimiser|Join Algorithms and the Optimiser]] — the planning stage in depth
- [[foundations/compilers/README|Compilers]] — the same pipeline, for languages
- [[databases/sql-reference|SQL Reference]] — §26, query optimisation from the query-writing side
- [[databases/README|Databases map]]
