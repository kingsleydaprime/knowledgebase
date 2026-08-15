# The Relational Model

**[Intermediate]** — Codd's idea, why SQL is declarative, and the algebra the optimiser actually manipulates.

## Codd's insight

**1970.** Databases at the time were hierarchical or network models — records linked by explicit pointers, and **queries were written as navigation instructions**: follow this pointer, then that one.

**The problem: your query code encoded the physical layout.** Reorganise the storage and every program broke.

**Codd's proposal** — *A Relational Model of Data for Large Shared Data Banks* — was **data independence**:

> **Describe the data as mathematical relations. Say *what* you want, not *how* to get it. Let the system decide the access path.**

**That separation is why databases can improve without your code changing.** Add an index, upgrade the optimiser, reorganise the storage — the query is unchanged, and it gets faster. **Every optimisation in notes 04–07 is only possible because the query didn't specify a plan.**

## A table is a relation

**Literally**, in the sense from [[foundations/discrete-math/04-sets-relations-and-functions|set theory]]:

**A relation is a subset of the Cartesian product of its attribute domains.**

| Formal | SQL |
|---|---|
| relation | table |
| tuple | row |
| attribute | column |
| domain | data type |
| cardinality | row count |
| degree | column count |

**Two properties of the mathematical definition are worth noticing**, because SQL violates both:

**A relation is a *set*** — no duplicates, no order. **SQL tables are *bags*** — duplicates are allowed unless you declare a key, and `SELECT` returns rows in whatever order the plan produced. **This is a deliberate departure**, made for performance (deduplicating on every operation is expensive), and it's why `SELECT DISTINCT` exists and why **a query without `ORDER BY` has no guaranteed order** — a rule people learn the hard way when a plan change reorders their output.

**Attribute order shouldn't matter.** In SQL it does, for `SELECT *` and `INSERT` without a column list. **Which is the argument for never using either in application code.**

## Relational algebra

**The operations the optimiser actually manipulates.** SQL is a surface syntax; the planner converts it into an algebraic tree and rewrites *that*. → [[databases/06-the-query-pipeline|The Query Pipeline]]

| Operation | Symbol | SQL |
|---|---|---|
| **Selection** — pick rows | $\sigma_{cond}(R)$ | `WHERE` |
| **Projection** — pick columns | $\pi_{cols}(R)$ | `SELECT` |
| **Union** | $R \cup S$ | `UNION` |
| **Difference** | $R - S$ | `EXCEPT` |
| **Cartesian product** | $R \times S$ | `CROSS JOIN` |
| **Rename** | $\rho$ | `AS` |

**Those six are primitive.** Everything else is derived:

$$R \bowtie_\theta S = \sigma_\theta(R \times S) \qquad\text{(join)}$$

$$R \cap S = R - (R - S) \qquad\text{(intersection)}$$

> **The join definition is worth staring at.** A join is *defined* as a Cartesian product followed by a filter. **Executing it that way would be catastrophic** — a million rows joined to a million is $10^{12}$ intermediate rows.
>
> **So the optimiser's entire job is to never do what the algebra literally says.** It pushes the filter down into the product, and it picks a physical algorithm (hash, merge, nested loop) that computes the same *result* without materialising the product. **The algebra defines correctness; the physical plan defines cost.** → [[databases/07-join-algorithms-and-the-optimiser|Join Algorithms]]

**Extensions SQL adds** that aren't in the pure algebra: aggregation with grouping, outer joins (which need NULL), sorting, and window functions.

### Equivalences the optimiser uses

**These rewrite rules are why declarative works:**

$$\sigma_c(R \bowtie S) \equiv \sigma_c(R) \bowtie S \quad\text{when } c \text{ only mentions } R$$

**Predicate pushdown** — filter before joining. **Usually the single biggest win available**, because it shrinks the input to the expensive operation.

$$(R \bowtie S) \bowtie T \equiv R \bowtie (S \bowtie T)$$

**Join reordering** — associativity and commutativity mean $n$ tables can be joined in many orders, and **the orders differ by orders of magnitude in cost.** Choosing among them is the hardest part of query planning.

$$\pi_a(\sigma_c(R)) \equiv \sigma_c(\pi_a(R)) \quad\text{when } c \text{ only uses } a$$

**Projection pushdown** — drop columns early, so less data moves.

## Declarative, and what it costs

**You write:**

```sql
SELECT c.name, SUM(o.total)
FROM customers c JOIN orders o ON o.customer_id = c.id
WHERE o.created_at > '2026-01-01'
GROUP BY c.name;
```

**You did not say:** which table to read first, whether to use an index, which join algorithm, whether to sort or hash for the grouping, or whether to parallelise. **The planner decides all of it.**

**What you gain:** the plan adapts to data size, indexes, and statistics — automatically, and it changes as your data grows.

**What you lose, and it's real:**

**You can't force it directly.** When the planner is wrong, you're reduced to indirect influence — hints (where supported), rewriting the query, adjusting statistics targets, or adding an index. **This is genuinely frustrating** and it's the main practical complaint against declarative querying.

**Performance is unpredictable across data changes.** A query fast at 10,000 rows can pick a different plan at 10 million and become pathological. **The query didn't change; the plan did.**

**You must read plans to debug.** `EXPLAIN` is not optional — it's the only window into what actually happened. → [[databases/07-join-algorithms-and-the-optimiser|Reading EXPLAIN]]

## NULL

**The relational model's most criticised addition**, and Codd himself argued about it for decades.

**NULL means "unknown", and it produces three-valued logic:**

| | Result |
|---|---|
| `NULL = NULL` | **NULL**, not true |
| `NULL <> NULL` | **NULL** |
| `NULL AND false` | **false** |
| `NULL AND true` | NULL |
| `NULL OR true` | **true** |

**The consequences that bite:**

**`WHERE x = NULL` never matches.** Use `IS NULL`.

**`NOT IN` with a NULL in the subquery returns nothing.** `x NOT IN (1, 2, NULL)` evaluates to NULL for every `x`, because `x <> NULL` is unknown. **This is a classic silent bug** — the query runs, returns zero rows, and looks like a data problem. **Use `NOT EXISTS`**, which handles it correctly.

**Aggregates skip NULLs.** `AVG(col)` averages the non-null values, so it differs from `SUM(col)/COUNT(*)`. `COUNT(col)` counts non-nulls; `COUNT(*)` counts rows.

**`UNIQUE` allows multiple NULLs** in most databases, since two unknowns aren't known to be equal.

> **The practical advice: use `NOT NULL` aggressively.** Every nullable column is a branch your code must handle and a chance for three-valued logic to surprise you. **Make nullability a deliberate decision, not the default** — and note that this is exactly the argument [[languages/03-rust/07-option-and-result|Rust's `Option`]] makes at the type level.

**Full treatment in [[databases/sql-reference|sql-reference]] §18.**

## Keys and integrity

**The constraints that make a relation more than a spreadsheet.**

**Primary key** — uniquely identifies a row. **Every table should have one**, and it determines physical clustering in some engines. → [[databases/04-b-trees-and-indexes|Clustered Indexes]]

**Natural vs surrogate keys** — a real-world identifier (email, ISBN) versus a generated one (auto-increment, UUID).

**Surrogate is usually right.** Natural keys change — people change email addresses, countries change codes — and a changing primary key means cascading updates everywhere it's referenced.

**Foreign key** — references another table's key. **Referential integrity**: the database refuses to create an orphan.

> **Foreign keys are increasingly skipped at scale, and that's a real trade rather than laziness.** They cost a lookup on every write, they complicate sharding (the referenced row may be on another node), and they interfere with bulk loading and some migration patterns.
>
> **But the alternative is enforcing integrity in application code**, which means every writer must get it right forever, including the migration script someone runs at 2am. **Keep them unless you have a specific, measured reason not to.**

**Other constraints:** `UNIQUE`, `CHECK`, `NOT NULL`, `DEFAULT`, and exclusion constraints in Postgres.

**Normalisation** — the process of eliminating redundancy so that each fact is stored once. **Fully covered in [[databases/database-design-reference|database-design-reference]] §7–8**, including when to denormalise deliberately.

## What survived

**The relational model is 55 years old and still the default.** Worth asking why.

**The mathematical foundation is genuine.** Because queries are algebra, they can be rewritten with provable equivalence. **No other data model has an optimiser story this strong** — you cannot automatically rewrite a hand-written traversal.

**Data independence held up.** SQL from 1990 runs today, faster, on storage engines that didn't exist then.

**Declarative scales with the system, not the programmer.** Every improvement to the planner benefits queries nobody revisits.

**It absorbed its competitors.** JSON columns, arrays, full-text, geospatial, graph-ish recursive CTEs — all now in Postgres. **The model was general enough to extend.**

**The genuine limits** are horizontal scaling of writes (partitioning breaks joins and cross-shard transactions), object-relational impedance mismatch, and hierarchical data being awkward. **The first is real and is what NewSQL systems attack.** → [[architecture/04-distributed-systems/13-partitioning|Partitioning]]

---

## Related
- [[databases/06-the-query-pipeline|The Query Pipeline]] — where this algebra gets used
- [[databases/database-design-reference|Database Design Reference]] — modelling, normalisation, keys in depth
- [[foundations/discrete-math/04-sets-relations-and-functions|Sets, Relations and Functions]] — the maths
- [[databases/README|Databases map]]
