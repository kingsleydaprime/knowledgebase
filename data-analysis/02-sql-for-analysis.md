---
id: 7e401d3b-ff6a-4e4e-9cc8-9ab98a199b2c
---

# SQL for Analysis

SQL is the language people use to ask questions of the data stored in a database. When a bank app shows your spending for the month, some SQL query added up your transactions behind the scenes. For a data analyst, SQL is the main everyday tool.

## The kid version first
<!-- bite: 445c4d97-76d1-4ea2-a6af-5ad78c0db56d -->

Most people learn SQL for *transactions* — insert a row, fetch a user, update an order. **Analytical SQL is a different dialect of the same language**, built for questions like "rank customers by spend," "what's the running total by month," "how does this week compare to last." The workhorses are **window functions** and **CTEs** — and once they click, a huge fraction of the analyst job is one well-written query.

This note assumes you know [[databases/sql-reference|basic SQL]] (SELECT, JOIN, GROUP BY, WHERE) and goes to the analytical layer on top.

## Why SQL is the analyst's tool
<!-- bite: cff41d83-2245-4c87-9b98-0904c46e61d4 -->

Not Python, not a BI tool — **SQL is where analysts spend most of their time**, because:

- **The data is already in the warehouse**, and SQL runs *in* the warehouse — no exporting, no moving gigabytes to your laptop → [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses]]
- **It's declarative** — you say *what* you want, the engine figures out *how*, over billions of rows → [[databases/07-join-algorithms-and-the-optimiser/index|the optimiser]]
- **It's the shared language** — analysts, engineers, and BI tools all speak it, so a SQL analysis is reproducible and reviewable
- **BI tools generate SQL underneath** — understanding it means you can debug and extend what the dashboard does → [[data-analysis/07-dashboards-and-bi|BI]]

**Python and pandas are the analyst's second tool** — for stats, complex reshaping, and anything SQL is awkward at → [[machine-learning/00-foundations/04-python-and-data-tools/03-pandas|pandas]]. But start in SQL; leave it only when you must.

## Window functions — the single most important skill
<!-- bite: b1420a53-d34e-421c-a90b-4edc1d195630 -->

**A window function computes across a set of rows *related to the current row*, without collapsing them into one** — which is the difference from `GROUP BY`. This one feature unlocks ranking, running totals, period-over-period, and cohort analysis.

```sql
SELECT
    customer_id,
    order_date,
    amount,
    -- running total per customer, ordered by date
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total,
    -- rank each customer's orders by size
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS order_rank,
    -- compare to the previous order
    LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_amount
FROM orders;
```

The anatomy: `function() OVER (PARTITION BY ... ORDER BY ...)`:
- **`PARTITION BY`** — the groups to compute within (like `GROUP BY`, but rows survive)
- **`ORDER BY`** — the order within each partition (needed for running totals, `LAG`, ranking)

**The functions you'll use constantly:**

| Function | For |
|---|---|
| `ROW_NUMBER()` / `RANK()` / `DENSE_RANK()` | Ranking; "top N per group"; deduplication |
| `SUM/AVG/COUNT() OVER (...)` | Running totals, moving windows |
| `LAG()` / `LEAD()` | Compare to previous/next row — **period-over-period growth** |
| `FIRST_VALUE()` / `LAST_VALUE()` | The first/last in a window (first purchase, latest status) |
| `NTILE(n)` | Bucket into n groups — quartiles, deciles |

**"Top N per group"** — a question that's genuinely hard without windows and trivial with them:

```sql
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS rn
    FROM products
) WHERE rn <= 3;          -- top 3 products in each category
```

**If you learn one thing from this note, learn window functions.** They're the dividing line between someone who can query a database and someone who can *analyse* one.

## CTEs — making complex queries readable
<!-- bite: d6c03680-79de-4b3e-9e36-22789f54cf31 -->

A **Common Table Expression** (`WITH`) names a subquery so you can build an analysis in readable steps instead of a nested-subquery nightmare:

```sql
WITH monthly_revenue AS (
    SELECT date_trunc('month', order_date) AS month, SUM(amount) AS revenue
    FROM orders GROUP BY 1
),
with_growth AS (
    SELECT month, revenue,
           LAG(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly_revenue
)
SELECT month, revenue,
       ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS growth_pct
FROM with_growth;
```

**CTEs read top-to-bottom like a recipe** — each step builds on the last, named for what it represents. This is the single biggest readability improvement in analytical SQL, and it's how you (and the reviewer) follow a 100-line query. **Chain CTEs; avoid deeply nested subqueries** — they're the same logic, but one is legible and one isn't. It's also exactly how [[data-engineering/07-transformation-and-dbt|dbt models]] are structured.

## The analytical query patterns
<!-- bite: 827a91b1-5eee-422f-b7de-97e44edcc500 -->

A small set of recipes covers most analyst questions:

**Period-over-period** (this month vs last):
```sql
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly_revenue;
```

**Cohort / retention** — group users by when they joined, track them over time → [[data-analysis/05-product-and-business-analytics|cohorts]]:
```sql
WITH cohorts AS (
    SELECT user_id, date_trunc('month', MIN(order_date)) AS cohort_month
    FROM orders GROUP BY user_id
)
SELECT cohort_month, date_trunc('month', o.order_date) AS active_month,
       COUNT(DISTINCT o.user_id) AS active_users
FROM orders o JOIN cohorts c USING (user_id)
GROUP BY 1, 2;
```

**Funnel** — how many users reach each step → [[data-analysis/05-product-and-business-analytics|funnels]]:
```sql
SELECT
    COUNT(*) FILTER (WHERE viewed)     AS viewed,
    COUNT(*) FILTER (WHERE added_cart) AS added_to_cart,
    COUNT(*) FILTER (WHERE purchased)  AS purchased
FROM user_funnel;
```

**Conditional aggregation** — `COUNT/SUM(...) FILTER (WHERE ...)` or `CASE` inside an aggregate — pivots rows into columns and is one of the most-used analyst tricks.

## The traps
<!-- bite: 0f1ce331-a815-43dc-96e2-dae662f707e5 -->

Analytical SQL has specific footguns worth naming:

- **`COUNT(*)` vs `COUNT(DISTINCT x)`** — a JOIN that fans out rows makes `COUNT(*)` wrong. **Fan-out is the #1 analytical SQL bug** — a one-to-many join silently multiplies your numbers → [[databases/07-join-algorithms-and-the-optimiser/index|joins]]
- **NULLs break aggregates quietly** — `AVG` ignores NULLs, `COUNT(column)` skips them, `x = NULL` is never true (use `IS NULL`). A NULL you didn't expect skews the answer without an error
- **Integer division** — `sales / total` in integer columns truncates to 0. `100.0 * ...` or cast → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|the same trap everywhere]]
- **Timezone and date-boundary bugs** — "today" depends on the timezone; `date_trunc` and `BETWEEN` on timestamps have off-by-one edges
- **`WHERE` filters before aggregation, `HAVING` after** — filtering a windowed/grouped result needs the right clause or a wrapping CTE

## Beyond SQL
<!-- bite: 2faea5ed-c7e5-4974-b59c-bc2ad1863909 -->

Reach for **Python/pandas** when SQL gets awkward: statistical tests, complex reshaping, anything iterative, or joining SQL results with an API/file → [[machine-learning/00-foundations/04-python-and-data-tools/index|the Python data stack]]. And **spreadsheets** remain a legitimate analyst tool for small, ad-hoc, stakeholder-facing work — don't be a snob about them; the right tool is the one that answers the question fastest and most clearly.

## Key insight
<!-- bite: 9ff9fc2b-8ac3-4bd8-927e-b1c3c9ef571b -->

**Analytical SQL is the same language as transactional SQL pointed at a different question, and two features carry most of it: window functions (compute across related rows without collapsing them — ranking, running totals, period-over-period, cohorts) and CTEs (build a complex analysis as a readable top-to-bottom recipe).** Learn window functions above all else — they're the line between querying a database and analysing one. Then watch for the analytical footguns, chiefly join fan-out silently multiplying your numbers, and drop to pandas only when SQL genuinely can't express the question.

## Related
<!-- bite: 16e53142-1f44-42f6-b683-0ce0143ba36f -->
- [[databases/sql-reference|SQL reference]] — the syntax lookup · [[databases/index|the databases course]] — how the engine runs it
- [[data-analysis/05-product-and-business-analytics|product and business analytics]] — where these patterns get applied
- [[data-engineering/07-transformation-and-dbt|dbt]] — CTEs as the transformation layer
- [[machine-learning/00-foundations/04-python-and-data-tools/03-pandas|pandas]] — the second tool

## About this lesson
<!-- bite: e96f3c71-5aae-49c2-a7de-c79126e1f46e -->

**Level:** Intermediate. **Covers:** the analyst's primary tool, and the handful of patterns that separate analytical SQL from the transactional SQL of [[databases/index|the databases course]].

*Source: [reference] — Sep 2026.*
