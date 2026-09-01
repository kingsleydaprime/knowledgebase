# Dashboards and BI

**[Intermediate]** — the tools that let a whole organisation see the data, the semantic layer that keeps everyone's numbers agreeing, and why most dashboards fail.

## The kid version first

An analyst can't personally answer every question for every person — so **business intelligence tools let people see the data themselves**, through dashboards and reports that update automatically. Done well, this frees the analyst from repetitive pulls and lets the business self-serve. Done badly — and it usually is — you get a graveyard of unused dashboards, and three teams reporting three different revenue numbers because everyone defined it differently.

## What BI tools do

A **BI (business intelligence) tool** connects to the [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouse]], lets you build charts and dashboards over it, and lets non-technical people explore and filter without writing SQL:

| Tool | Character |
|---|---|
| **Tableau** | The powerful incumbent — rich visualisation, steep-ish, expensive |
| **Power BI** | Microsoft's — strong, cheaper, dominant in Microsoft shops |
| **Looker** | Code-first, built around a **semantic layer** (LookML) — governed, engineer-friendly |
| **Metabase** | Open-source, simple, great for self-serve and smaller teams |
| **Superset** | Open-source, the Airbnb-origin one |
| **Mode / Hex** | SQL-notebook hybrids — analyst-first, blend SQL, Python and viz |

**They all generate SQL underneath** and run it against the warehouse → [[data-analysis/02-sql-for-analysis|SQL]]. The differences are governance, cost, and how technical the builder needs to be. **The tool matters less than how you use it.**

## The semantic layer — the fix for "whose number is right?"

**The most important BI concept, and the one that separates a trustworthy analytics setup from chaos.**

The problem: without a shared definition, marketing calculates "active users" one way, product another, finance a third — and every dashboard disagrees, so nobody trusts any of them. Meetings become arguments about whose number is right instead of what to do.

**The semantic layer is a central place where metrics are defined *once*** — "revenue," "active user," "churn" each have one canonical definition, in code, that every dashboard and query inherits:

```
   raw warehouse tables
        │
   SEMANTIC LAYER   ← "revenue = SUM(amount) WHERE status='completed' AND is_test=false"
        │              defined ONCE, governed, versioned
   every dashboard, every query, same number
```

**This is where BI meets [[data-engineering/07-transformation-and-dbt|dbt]]** — the transformation layer and the semantic layer are how "one definition of every metric" actually gets enforced. LookML (Looker), dbt's semantic layer, Cube, and others implement it. **A metric defined in twelve dashboards is a metric defined twelve slightly-different ways; a metric defined in the semantic layer is defined once and trusted.** → [[data-analysis/03-metrics-and-kpis|defining a metric precisely]].

## Self-serve analytics — the goal and the trap

**The dream: business users answer their own questions, and analysts do high-value work instead of pulling numbers.** Real, and worth pursuing — but it fails in predictable ways:

- **Without governance, self-serve produces contradictory numbers** — everyone builds their own slightly-wrong version. The semantic layer is the prerequisite, not an optional extra
- **Non-analysts misinterpret** — they read correlation as causation, ignore [[data-analysis/06-time-series-analysis|seasonality]], or draw conclusions from a tiny segment. Self-serve gives people rope
- **The dashboard graveyard** — most dashboards built get used a few times and abandoned. Building dashboards nobody uses is a huge, common waste

**Self-serve works when the metrics are governed (semantic layer), the common questions are anticipated, and users are taught enough to not mislead themselves.** It's a socio-technical problem, not just a tooling one.

## Dashboard design — most are bad

A dashboard is a *communication* artefact, and the [[ai-ml/01-data-scientist/05-data-visualization|data-visualization principles]] apply with force. The common failures and their fixes:

- **Too much** — 40 charts, no hierarchy, no story. **A dashboard should answer a specific set of questions for a specific audience**, not display everything possible. Cut ruthlessly
- **No context** — a number with no comparison (vs target, vs last period, vs benchmark) is meaningless → [[data-analysis/03-metrics-and-kpis|comparability]]. Every metric needs a reference point
- **Wrong chart** — a pie chart with 12 slices, a line chart for categories, dual axes that mislead → [[ai-ml/01-data-scientist/05-data-visualization|choosing the right chart]]
- **No clear action** — the viewer should know what to *do*, or at least what to look at first. Lead with the headline
- **Vanity over signal** — big impressive cumulative numbers instead of the rates that show performance → [[data-analysis/03-metrics-and-kpis|vanity metrics]]

**Match the format to the need**, which is the decision most people skip:

| Need | Format |
|---|---|
| Monitor the same metrics continuously | **Dashboard** (live, glanceable) |
| Answer a specific one-off question | **A report / analysis** (narrative, a "so what") → [[data-analysis/08-communicating-analysis\|communicating]] |
| Explore freely | **A BI exploration tool / notebook** |
| A number checked daily by one person | **An alert**, not a dashboard |

**A dashboard is for *monitoring* known metrics; a report is for *answering* a question.** Building a dashboard to answer a one-time question (and a report for something checked daily) is a common mismatch that wastes effort and buries the insight.

## Key insight

**BI tools let an organisation see its own data, but the tool matters far less than the semantic layer — the central, coded, single definition of every metric that stops three teams from reporting three different revenue numbers.** Self-serve analytics is a real goal that fails without that governance, plus anticipated questions and enough user education to prevent misinterpretation. And most dashboards fail as *communication*: too much, no context, no clear action, and built to answer one-time questions that a report should have answered. Design a dashboard for monitoring known metrics with reference points and a clear headline — and if nobody uses it, stop building it.

## Related
- [[data-analysis/03-metrics-and-kpis|metrics and KPIs]] — what the semantic layer defines
- [[data-engineering/07-transformation-and-dbt|dbt]] — where the semantic layer lives
- [[ai-ml/01-data-scientist/05-data-visualization|data visualization]] — choosing charts that don't mislead
- [[data-analysis/08-communicating-analysis|communicating analysis]] — dashboards vs reports

*Source: [reference] — Sep 2026.*
