# Practice Exercises — Solutions

> **[Intermediate]** · Worked answers and expected shapes for [[data-analysis/09-practice-exercises|note 09]]. **Attempt each first** — the SQL screen rewards fluency you build by writing, not reading. These give the approach and the gotcha, not paste-ready code.

---

## Part A — Analytical SQL

**1. Top-N per group.**
```sql
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY total_sales DESC) AS rn
  FROM product_sales
) WHERE rn <= 3;
```
`GROUP BY` collapses rows to one per group, losing the individual products; the window function ranks *within* each group while keeping every row. Use `RANK()` if you want ties to share a rank (and possibly return >3), `ROW_NUMBER()` for exactly 3.

**2. Running total.**
`SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date)`. The `ORDER BY` inside `OVER` is what makes it *running* (a default frame of "start → current row"); without it you'd get each customer's grand total repeated on every row.

**3. Month-over-month.**
```sql
WITH monthly AS (SELECT date_trunc('month', order_date) m, SUM(amount) rev FROM orders GROUP BY 1)
SELECT m, rev, 100.0*(rev - LAG(rev) OVER (ORDER BY m))/LAG(rev) OVER (ORDER BY m) AS growth_pct
FROM monthly;
```
First month's growth is NULL (no prior) — correct, don't fake it. `100.0 *` forces float division; integer columns would truncate to 0.

**4. Deduplicate.**
`ROW_NUMBER() OVER (PARTITION BY natural_key ORDER BY loaded_at DESC)` then keep `= 1`. This is the canonical "latest version per key" pattern, everywhere in analytics over append-only or CDC data.

**5. Join fan-out.**
`orders JOIN order_items` produces one row *per item*, so `SUM(orders.amount)` counts each order's amount once per item — inflating the total by roughly the average items-per-order. **Fixes:** aggregate `order_items` to one row per order *before* joining, or sum a pre-deduplicated set, or `SUM(DISTINCT ...)` only if amounts are unique (usually unsafe). The lesson: whenever a total looks too high, suspect a one-to-many join first, and reconcile against a known figure.

## Part B — Metrics and diagnosis

**6. Vanity metric.** Cumulative registered users only ever rises — it measures how long you've existed, not how you're doing. Weekly-active falls as the business declines. Plotted together, the gap is the deception: a board looking at "total users, up and to the right" sees success while the product empties. The active/registered *ratio* falling is the tell.

**7. Diagnostic.** The method, applied: (1) **confirm real** — the drop exceeds normal week-to-week variance and isn't a holiday; (2) **decompose** — revenue = users × conversion × AOV; find conversion moved, others flat; (3) **segment** — slice conversion by device/geo/channel until it localises (mobile, one country); (4) **correlate** — it started the day of a release. Result: *"Mobile conversion halved after Tuesday's release, costing ~£X/week — roll back or hotfix the mobile checkout."* The "so what" and the action are the point, not the number.

**8. Simpson's paradox.** Classic setup: treatment A has a higher *overall* success rate than B, but B is higher in *both* a hard subgroup and an easy subgroup — because A got mostly easy cases and B mostly hard ones. Aggregating over unequal, outcome-correlated group sizes reverses the direction. The escape is always the same: **segment**, and be suspicious of any aggregate comparison across groups of very different composition → [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|confounders]].

## Part C — Product analytics and time series

**9. Cohort retention.** Compute each user's cohort month (`MIN(order_date)`), then for each cohort count distinct actives per subsequent month, as a % of the cohort's month-0 size. The triangular table shows each cohort aging down-right. **Reading it:** a curve that keeps falling to ~0 = users never stick (no acquisition rate saves this); a curve that *flattens* at some % = you've found a retained core, the strongest product-market-fit signal. Comparing rows shows whether a change improved retention.

**10. Funnel.** `COUNT(*) FILTER (WHERE step_reached)` per step gives the counts; each step's conversion is vs the previous step (or vs the top — state which). The biggest *drop* is the highest-leverage fix. Segmenting by device typically reveals the leak is concentrated (mobile checkout, say), which is where the diagnostic in #7 points.

**11. Signal vs seasonality.** The raw daily series wiggles with a 7-day period (weekends low for B2B, say). A 7-day moving average cancels the weekly pattern, revealing whether the underlying trend is up or down. A "20% drop since yesterday" is often just Friday→Saturday; comparing *this Saturday to last Saturday* controls for it without any modelling. Most "the metric crashed!" panics die here.

## Part D — Communication

**12. The one-pager.** Structure: **headline = the answer** (*"Mobile checkout is broken in Germany, costing ~£40k/week"*), then the evidence (one chart, its message in the title), then the recommendation (*"roll back Tuesday's release; re-test the DE payment flow"*). No process narrative, no p-values in the opening, tailored to what an exec needs (decision + size). The test: someone reads the first line and knows what to do. If your write-up opens with "I pulled the orders table and joined…", rewrite it — that's the journey, not the answer.

## The through-line

The two drills that most change how you work are **#5** (watching a join silently double your revenue number teaches lifelong distrust of an unreconciled total) and **#12** (writing the answer-first one-pager forces the shift from "I computed a number" to "here's the decision"). Everything else is fluency that compounds — and the SQL screen, unlike a take-home, gives you no time to look things up.

## Related
- [[data-analysis/09-practice-exercises|the exercises]]
- [[data-analysis/README|the data analysis course]] · [[data-analysis/interview/01-the-data-analyst-round|the interview round]]
