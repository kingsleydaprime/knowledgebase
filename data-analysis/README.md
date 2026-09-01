# Data Analysis

**Turning data into a decision.** The analyst discipline — distinct from [[data-engineering/README|data engineering]] (which builds the pipeline) and [[ai-ml/01-data-scientist/README|data science]] (which builds models) — and the **most common data job**. An 8-note course built Sep 2026, filling the "last mile" gap between the warehouse and the model.

> **The one idea:** the deliverable is a **decision, not a number.** A correct analysis nobody acts on has failed — which reframes the whole craft around asking questions tied to real decisions, and communicating findings as a "so what" rather than a data dump.

## Why this exists — and the data stack it completes

The vault had [[data-engineering/README|data engineering]] (build the warehouse) and [[ai-ml/01-data-scientist/README|data science]] (statistical inference and models), but the enormous middle — **analysts turning warehouse data into business decisions with SQL and BI** — was missing. The data-scientist track even *distinguished* the analyst role without covering it. This closes that, so the three data domains read as one stack:

```
   DATA ENGINEERING   →   DATA ANALYSIS   →   DATA SCIENCE
   (build the warehouse)   (decisions from      (models &
                            data — this track)   rigorous inference)
```

It **borrows** the statistical rigour ([[ai-ml/01-data-scientist/03-inferential-statistics|hypothesis testing]], [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|A/B testing]], [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal inference]]) from the data-scientist track rather than duplicating it, and consumes the warehouse the data-engineering track builds.

## Reading order

**01 sets the frame; 02 is the primary skill; 04–05 are the daily job.**

1. [[data-analysis/01-what-data-analysis-is|what-data-analysis-is]] — **[Beginner]** — analyst vs engineer vs scientist, the descriptive→prescriptive spectrum, the workflow, and **"the deliverable is a decision, not a number"**
2. [[data-analysis/02-sql-for-analysis|sql-for-analysis]] — **[Intermediate]** — the analyst's primary tool: **window functions and CTEs**, the analytical query patterns (running totals, cohorts, funnels), and the traps
3. [[data-analysis/03-metrics-and-kpis|metrics-and-kpis]] — **[Intermediate]** — defining what's worth measuring: vanity vs actionable, leading vs lagging, the metric tree, the North Star, and **Goodhart's Law**
4. [[data-analysis/04-exploratory-and-diagnostic-analysis|exploratory-and-diagnostic-analysis]] — **[Intermediate]** — trusting a dataset, and **"why did this number change?"** — the method: confirm → decompose → segment → correlate → verify
5. [[data-analysis/05-product-and-business-analytics|product-and-business-analytics]] — **[Intermediate → Advanced]** — **the analyses that *are* the job**: funnels, cohorts/retention, and the unit economics (LTV:CAC) that decide if a business works
6. [[data-analysis/06-time-series-analysis|time-series-analysis]] — **[Intermediate → Advanced]** — trend/seasonality/noise decomposition, moving averages, forecasting — **and why most "changes" are just seasonality**
7. [[data-analysis/07-dashboards-and-bi|dashboards-and-bi]] — **[Intermediate]** — BI tools, **the semantic layer** (one definition of every metric), self-serve, and why most dashboards fail
8. [[data-analysis/08-communicating-analysis|communicating-analysis]] — **[Intermediate]** — **the half of the job that isn't technical**: lead with the answer, the "so what" test, honest storytelling, insight → action

## If you only take three things

1. **The deliverable is a decision** — start from "what would we do differently?", not from the data ([[data-analysis/01-what-data-analysis-is|01]]).
2. **Learn window functions** — they're the line between querying a database and analysing one ([[data-analysis/02-sql-for-analysis|02]]).
3. **Most "the number changed!" alarms are seasonality** — compare like-with-like before investigating ([[data-analysis/06-time-series-analysis|06]]).

## Build it

[[data-analysis/projects|projects/]] — graded reps with a *done-when* for each. Start with a **real diagnostic** ("why did this metric change?") on a public dataset — it exercises SQL, segmentation and the "so what" in one go.

## Interview

[[data-analysis/interview/README|interview/]] — the analyst round: the SQL screen (window functions, fan-out), a metric-definition question, a diagnostic case ("this dropped 20% — walk me through it"), and the product-analytics staples (funnels, retention, LTV).

## Related
- [[data-engineering/README|data engineering]] — the layer below · [[ai-ml/01-data-scientist/README|data science]] — the rigorous end
- [[databases/README|databases]] — the SQL engine underneath · [[ai-ml/00-foundations/04-python-and-data-tools/README|the Python data stack]] — the second tool
- [[ai-ml/01-data-scientist/05-data-visualization|data visualization]] — choosing charts that don't mislead

*Source: [reference] — Sep 2026.*
