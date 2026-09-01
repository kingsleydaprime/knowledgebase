# What Data Analysis Is

**[Beginner]** — the analyst discipline, how it differs from data science and data engineering, and the one thing that defines the job.

## The kid version first

A company collects mountains of data — every order, click, signup, support ticket. On its own it's just numbers. **Data analysis is the work of answering questions with that data so someone can make a better decision:** *"Why did sales drop last month?" "Which customers are about to churn?" "Is the new feature working?"*

The analyst's job isn't to build the warehouse (that's engineering) or to train a predictive model (that's science) — it's to **turn data into a decision**, usually with SQL and a chart, fast enough to matter.

## The three data roles, distinguished

This is the most common confusion, so it's worth being precise. The three data disciplines form a stack, each with a different deliverable:

| | Deliverable | Primary tools | The question |
|---|---|---|---|
| **Data engineer** | A reliable pipeline / warehouse | SQL, Python, Spark, dbt, Kafka | "How do we get the data here, clean and fresh?" |
| **Data analyst** | **A decision or a recommendation** | **SQL, BI tools, spreadsheets, stats** | "What does the data say we should do?" |
| **Data scientist** | A model or a rigorous statistical answer | Python/R, stats, ML | "Can we predict / prove this?" |

- **[[data-engineering/README|Data engineering]]** builds the warehouse the analyst queries → the plumbing
- **Data analysis** (this track) turns that data into answers → **the last mile, and the most common data job**
- **[[ai-ml/01-data-scientist/README|Data science]]** brings statistical rigour and predictive modelling → the deep end

**The lines blur** — a "data analyst" at a small company does all three; "analytics engineer" is a hybrid of analyst and engineer who models data in [[data-engineering/07-transformation-and-dbt|dbt]]; and the analyst reaches into the [[ai-ml/01-data-scientist/README|data-scientist toolkit]] for [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|A/B tests]] and [[ai-ml/01-data-scientist/03-inferential-statistics|hypothesis testing]]. But the *deliverable* distinguishes them: **the analyst's output is a decision, communicated to someone who acts on it.**

## The analytics maturity spectrum

Analysis comes in four levels of ambition, and knowing which one a question needs keeps you from over- or under-engineering the answer:

```
   DESCRIPTIVE   "what happened?"           ← reports, dashboards. Most analysis
       ↓
   DIAGNOSTIC    "why did it happen?"        ← drill-down, root-cause. The hard, valuable part
       ↓
   PREDICTIVE    "what will happen?"         ← forecasting, models → data science
       ↓
   PRESCRIPTIVE  "what should we do?"        ← optimisation, recommendation
```

**Most day-to-day analysis is descriptive and diagnostic** — what happened and why — and *diagnostic is where analysts earn their keep*, because "sales dropped" is easy and "sales dropped *because* the checkout broke for mobile users in Germany" is the insight someone can act on → [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]]. Predictive and prescriptive shade into [[ai-ml/README|data science]].

## The analysis workflow

Every good analysis follows the same arc, and the beginner mistake is starting in the middle (at the data) instead of the start (the question):

```
1. QUESTION    what decision does this inform? Be specific
2. DATA        find it, get it, understand it, TRUST it
3. ANALYSE     explore, slice, compute, test
4. COMMUNICATE the finding — as a decision, not a data dump
5. DECISION    someone acts. THIS is the point
```

**Steps 1 and 4 are where analyses fail, and they're the non-technical ones.** A technically perfect analysis of the wrong question is useless; a correct finding communicated as a wall of numbers gets ignored. **The analyst's real skill is bracketing the technical middle with a sharp question and a clear "so what"** → [[data-analysis/08-communicating-analysis|communicating]].

## The one idea that defines the job

> **The deliverable is a decision, not a number.**

An analysis that produces a correct number nobody acts on has failed. This reframes everything:

- **Start from the decision**, not the data — "what would we do differently depending on the answer?" If nothing, don't do the analysis
- **Precision matters only up to the decision** — you don't need the churn rate to four decimal places if the action is the same at 8% and 8.4%
- **Communication is half the job**, not an afterthought — the [[ai-ml/01-data-scientist/01-the-data-scientist-role|same lesson the data-scientist track opens with]]
- **Actionable beats interesting** — a small finding that changes a decision beats a fascinating one that changes nothing

This is why the best analysts are as much *business* people as technical ones: they understand what the organisation is trying to do, so they ask the questions worth answering.

## What this track covers

The analyst's actual toolkit, and where each fits:

- **[[data-analysis/02-sql-for-analysis|SQL for analysis]]** — the primary tool. Window functions, CTEs, the analytical query patterns
- **[[data-analysis/03-metrics-and-kpis|Metrics and KPIs]]** — defining what's worth measuring
- **[[data-analysis/04-exploratory-and-diagnostic-analysis|Exploratory and diagnostic analysis]]** — the "why did it change" skill
- **[[data-analysis/05-product-and-business-analytics|Product and business analytics]]** — funnels, cohorts, retention, LTV
- **[[data-analysis/06-time-series-analysis|Time series]]** — trends, seasonality, forecasting
- **[[data-analysis/07-dashboards-and-bi|Dashboards and BI]]** — self-serve, the semantic layer, dashboard design
- **[[data-analysis/08-communicating-analysis|Communicating analysis]]** — turning findings into decisions

It **borrows** the statistical rigour (hypothesis testing, A/B tests, causal inference) from the [[ai-ml/01-data-scientist/README|data-scientist track]] rather than duplicating it, and consumes the warehouse the [[data-engineering/README|data-engineering track]] builds.

## Key insight

**Data analysis is the discipline of turning data into a decision — distinct from engineering (which builds the pipeline) and science (which builds models) by its deliverable, which is an answer someone acts on.** Most of the work is descriptive and diagnostic ("what happened, and why"), the primary tool is SQL, and the two places analyses actually fail are the non-technical bookends: asking a question tied to a real decision, and communicating the finding as a "so what" rather than a number. Internalise "the deliverable is a decision, not a number" and the rest of the craft organises itself around it.

## Related
- [[data-analysis/02-sql-for-analysis|SQL for analysis]] — the analyst's primary tool
- [[data-engineering/README|data engineering]] — the layer that feeds this · [[ai-ml/01-data-scientist/README|data science]] — the rigorous end
- [[data-analysis/03-metrics-and-kpis|metrics and KPIs]] — defining what to measure
- [[ai-ml/01-data-scientist/01-the-data-scientist-role|the data scientist role]] — the neighbouring discipline

*Source: [reference] — Sep 2026.*
