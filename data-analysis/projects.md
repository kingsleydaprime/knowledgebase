# Data Analysis — Projects

*The domain where **the reps are the job** — every one is a self-contained analysis you could show a stakeholder. All run on free public datasets and a warehouse-or-DuckDB, and the highest-signal ones end in a "so what," not a chart.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **A real diagnostic** — take a public dataset with a time dimension (e-commerce, a public metrics set), find a metric that changed, and explain *why* using the method: confirm it's real → decompose → segment → correlate with events. **Done when:** you can state the cause in one sentence with a "so what" — *"X dropped because Y, so we should Z"* → [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]]. **Do this first** — it exercises SQL, segmentation and communication in one go.

- 🟢 ⭐ **Window-function gauntlet** — on any dataset, write queries for: top-N per group, a running total, period-over-period growth, and a rank. **Done when:** all four work and you understand `PARTITION BY` vs `GROUP BY` cold → [[data-analysis/02-sql-for-analysis|SQL for analysis]]. **The single highest-leverage analyst skill.**

- 🟢 **Kill a vanity metric** — take a dashboard or dataset, find a metric that "only goes up," and replace it with the actionable rate it hides. **Done when:** you can explain what the vanity version concealed → [[data-analysis/03-metrics-and-kpis|metrics]].

- 🟡 ⭐ **A cohort retention analysis** — group users by signup month, compute retention over time, and plot the curve. **Done when:** you can read the curve's shape (does it flatten? that's the product-market-fit signal) and compare two cohorts → [[data-analysis/05-product-and-business-analytics|cohorts and retention]].

- 🟡 **A funnel with the biggest leak** — build a multi-step funnel, segment it, and identify where the largest drop-off is and for whom. **Done when:** you've named the step and segment where a fix has the most leverage → [[data-analysis/05-product-and-business-analytics|funnels]].

- 🟡 **Unit economics of a business** — for a dataset with customers and revenue, compute CAC, LTV, and the LTV:CAC ratio. **Done when:** you can say whether the business model works and what would improve the ratio → [[data-analysis/05-product-and-business-analytics|unit economics]].

- 🟡 **Separate signal from seasonality** — take a daily time series, decompose it (or use a 7-day moving average) to reveal the trend under the weekly pattern, then forecast next month with a seasonal-naive baseline. **Done when:** you can show that a "drop" you'd have investigated was just day-of-week → [[data-analysis/06-time-series-analysis|time series]].

- 🟡 **Build a governed dashboard** — in Metabase or Superset (both free), build a dashboard for a *specific audience and question*, with every metric defined once and every number carrying a comparison. **Done when:** someone else can read it without you explaining it → [[data-analysis/07-dashboards-and-bi|dashboards and BI]].

- 🔴 ⭐ **The full analyst deliverable** — take a business question end to end: question → SQL → analysis → a one-page writeup that **leads with the answer and a recommendation**, tailored to a non-technical reader. **Done when:** a stranger reads the first sentence and knows what to do → [[data-analysis/08-communicating-analysis|communicating analysis]]. **This is the portfolio piece** — it's what the job actually produces.

- 🔴 **An A/B test analysis, rigorously** — analyse (or simulate) experiment data properly: effect size *and* confidence interval, and check the pitfalls (SRM, peeking, Simpson's). **Done when:** you can state whether the change worked and how sure you are → [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|A/B testing]] (borrowed from the data-science track).

## If you only do one

**The full analyst deliverable.** Everything else is a component of it, and it's the thing a hiring manager actually wants to see: a real question answered in SQL, communicated as a decision a non-technical person can act on. That one-pager *is* the job.

## Related
- [[data-analysis/README|the data analysis course]] · [[data-analysis/interview/README|interview bank]]
- [[data-engineering/projects|data engineering projects]] — the layer below · [[ai-ml/projects|ai-ml projects]] — the data-science reps
- [[project-ideas|Project Ideas]] — the vault-wide index
