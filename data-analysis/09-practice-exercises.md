# Practice Exercises

> **[Intermediate]** · Twelve drills, weighted toward SQL — because **the analyst SQL screen rewards fluency you only get from writing the queries, not reading them**, and the diagnostic case rewards a *method* you build by running it.

Use any warehouse or **DuckDB** (free, in-process, reads CSV/Parquet directly — the easiest way to practise). A public dataset with orders/users/events works for most; the [TPC-H sample](https://duckdb.org/docs) or any e-commerce dataset is ideal. Solutions and expected shapes in [[data-analysis/10-practice-exercises-solutions|note 10]].

---

## Part A — Analytical SQL (note 02)

**1. Top-N per group.**
For each product category, return the top 3 products by total sales.
**Done when:** you've used `ROW_NUMBER() OVER (PARTITION BY category ORDER BY ...)` in a subquery/CTE and filtered `rn <= 3` — and you can say why `GROUP BY` alone can't do this → [[data-analysis/02-sql-for-analysis|note 02]].

**2. Running total.**
Compute a cumulative revenue total per customer, ordered by date.
**Done when:** `SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date)` produces a monotonically increasing total per customer.

**3. Month-over-month growth.**
Aggregate revenue by month, then compute the percentage change from the previous month.
**Done when:** you've chained CTEs (monthly → with-`LAG` → growth), handled the first month's NULL, and avoided the integer-division trap (`100.0 *`).

**4. Deduplicate with a window.**
Given a table with duplicate rows (same natural key, different load times), keep only the latest version of each.
**Done when:** `ROW_NUMBER() OVER (PARTITION BY key ORDER BY loaded_at DESC)` + filter `= 1` returns one row per key.

**5. Catch a join fan-out.**
Join orders to a one-to-many table (e.g. order_items), then `SUM(orders.amount)`. Compare the total to summing orders alone.
**Done when:** you've *seen* the total inflate, you can explain why (the join multiplied order rows), and you can fix it (aggregate before joining, or `COUNT(DISTINCT)`). **This is the #1 analytical SQL bug — reproduce it deliberately.**

## Part B — Metrics and diagnosis (notes 03–04)

**6. Spot the vanity metric.**
Take a dataset and compute both "total registered users" (cumulative) and "weekly active users." Plot both over time for a scenario where the business is declining.
**Done when:** the cumulative metric keeps rising while the active metric falls — and you can articulate why the first one hides the truth → [[data-analysis/03-metrics-and-kpis|note 03]].

**7. Run a diagnostic.**
Take a metric that changed between two periods (engineer one into a dataset if needed: e.g. drop mobile conversion after a date). Find the cause using the method: confirm it's real → decompose → segment → correlate with the event.
**Done when:** you can state the cause in one sentence with a "so what," and you localised it by *segmenting* rather than guessing → [[data-analysis/04-exploratory-and-diagnostic-analysis|note 04]].

**8. Fall into (then escape) Simpson's paradox.**
Construct or find data where a treatment looks better *overall* but worse *in every segment* (or vice versa), driven by unequal segment sizes.
**Done when:** you've reproduced the reversal and can explain why the aggregate lied — the reason you always segment → [[data-analysis/04-exploratory-and-diagnostic-analysis|note 04]].

## Part C — Product analytics and time series (notes 05–06)

**9. Cohort retention.**
Group users by signup month, then compute the % still active in each subsequent month. Build the triangular cohort table.
**Done when:** you can read the retention curve's shape — does it flatten (a retained core, the product-market-fit signal) or fall to zero (a leaky bucket)? → [[data-analysis/05-product-and-business-analytics|note 05]].

**10. Funnel with the biggest leak.**
Compute how many users reach each step of a funnel (viewed → cart → checkout → purchased), using conditional aggregation. Then segment by device.
**Done when:** you've found the step with the worst drop-off and shown it differs by segment (where a fix has the most leverage) → [[data-analysis/05-product-and-business-analytics|note 05]].

**11. Separate signal from seasonality.**
Take a daily time series with a weekly pattern. Apply a 7-day moving average to reveal the underlying trend, and compare a raw day-over-day "drop" to the same day last week.
**Done when:** you've shown that a scary-looking drop was just day-of-week, and the moving average reveals the real trend underneath → [[data-analysis/06-time-series-analysis|note 06]].

## Part D — Communication (note 08)

**12. Write the one-pager.**
Take your diagnostic from #7 and write it up for a non-technical executive: **lead with the answer**, state the size and the "so what," support with one chart (message in the title), and end with a recommendation.
**Done when:** a stranger reads your first sentence and knows what to do — and there's not a p-value or a table in the opening → [[data-analysis/08-communicating-analysis|note 08]]. **This is the deliverable the whole track builds toward.**

---

## The meta-point

If you do only three: **#5** (reproduce a join fan-out — the bug that silently wrongs your numbers), **#7** (run a real diagnostic — the case-study half of the interview), and **#12** (write the one-pager — because the deliverable is a decision, not a query). The SQL drills #1–4 are worth doing until they're *reflexive*, because the live SQL screen doesn't wait.

## Related
- [[data-analysis/README|the data analysis course]] · [[data-analysis/projects|projects]] — the larger deliverables
- [[data-analysis/10-practice-exercises-solutions|solutions]]
- [[databases/13-practice-exercises|the databases exercises]] — deeper on SQL internals
