# Metrics and KPIs

**[Intermediate]** — how to define what's worth measuring, why most metrics mislead, and the laws that govern what happens once you start optimising one.

## The kid version first

Before you can analyse anything, you have to decide *what to measure* — and this is harder and more consequential than it looks. A badly chosen metric sends a whole company in the wrong direction: chasing signups while users churn, or page views while nobody buys. **A good metric captures something that actually matters and changes the decision; a bad one just looks impressive on a slide.**

Choosing metrics is a core analyst skill, and getting it wrong is expensive because the whole organisation steers by them.

## What makes a metric good

A metric worth tracking is:

- **Actionable** — it changes a decision. If the number moves and nobody would do anything differently, it's not worth a dashboard tile → [[data-analysis/01-what-data-analysis-is|the deliverable is a decision]]
- **A rate or ratio, usually, not a raw count** — "revenue *per user*," "conversion *rate*," "cost *per acquisition*." Raw counts grow with the business and hide whether things are actually improving. **Normalised metrics reveal efficiency; absolute ones only reveal size**
- **Comparable** — against a target, a prior period, a segment, or a benchmark. A number with no comparison is meaningless ("500 signups" — good or bad?)
- **Clearly defined** — everyone agrees exactly what counts. "Active user" must have a precise definition or two teams will report different numbers → the [[data-engineering/07-transformation-and-dbt|single-source-of-truth]] problem
- **Timely** — available fast enough to act on

## Vanity vs actionable metrics

**The most important distinction, because vanity metrics are the most common analytical mistake:**

| Vanity metric | Actionable counterpart |
|---|---|
| Total registered users (only goes up) | **Active** users, retention rate |
| Page views | Conversion rate, revenue per visit |
| Total downloads | Daily/monthly active users |
| Social media followers | Engagement rate, referral traffic |
| "Big" cumulative totals | Period-over-period *rate of change* |

**Vanity metrics make you feel good and tell you nothing** — they mostly measure how long you've existed, not how well you're doing. They rise even as the business declines. The tell: **a metric that can only go up is almost always vanity.** The fix is to ask "would this number ever go *down* if we were doing badly?" — if not, it's not measuring performance.

## Leading vs lagging indicators

Two kinds of metric, and you need both:

- **Lagging** — measures the outcome, after the fact. Revenue, churn, profit. **Accurate but too late to act on** — by the time churn spikes, the customers are gone
- **Leading** — predicts the outcome, early. Trial-to-paid conversion, product usage in week one, support ticket volume, NPS. **Actionable but noisier** — you can influence them *before* the lagging metric moves

**Good analytics pairs a lagging metric (the goal) with the leading metrics that drive it.** "Revenue is down" is a lagging observation; "week-one activation dropped a month ago" is the leading signal that explains it and could have caught it early → [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]].

## The metric tree — connecting them

Metrics aren't a flat list; they form a hierarchy that decomposes a top-level goal into the levers that move it:

```
   Revenue
     = Users × Conversion × Avg Order Value
              │             │            │
        (acquisition,   (funnel,     (pricing,
         retention)     UX, trust)    upsell)
```

**A metric tree turns "grow revenue" into a diagnosable structure** — when revenue drops, you walk the tree to find *which* factor moved, which is the whole of [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]]. It also prevents the trap of optimising one branch (more users) while another collapses (worse conversion), leaving the top unchanged.

## The North Star metric

Many companies pick a single **North Star metric** — the one number that best captures the value they deliver to customers, that the whole company aligns on. Not revenue (that's the company's value, not the customer's) but the *customer* value that drives revenue:

- Spotify: time spent listening
- Airbnb: nights booked
- A messaging app: messages sent between people

**The point is alignment** — one shared definition of success so teams don't optimise conflicting local metrics. **The risk is over-simplification** — one number can't capture everything, and a North Star chosen badly (or gamed) steers the whole company wrong.

## Goodhart's Law — the trap of optimising a metric

The single most important idea about metrics, and the one people forget:

> **"When a measure becomes a target, it ceases to be a good measure."** — Goodhart's Law

The moment you *optimise* a metric, people (and systems) game it, and it stops reflecting the thing you actually cared about:

- Optimise "calls resolved per hour" → agents rush and hang up, service gets *worse*
- Optimise "lines of code" → developers write bloated code
- Optimise "clicks" → clickbait, dark patterns
- Optimise a single conversion number → teams sacrifice long-term retention for short-term signups

**Defences:**
- **Pair metrics with a guardrail** — optimise conversion *without* letting churn rise, or speed *without* letting quality drop. A single metric is a single point of gaming; a metric plus a counter-metric is much harder to cheat
- **Watch for the gap between the metric and the *intent*** — the metric is a proxy; when it diverges from what you actually want, trust the intent
- **Rotate and re-examine** — a metric that was good becomes gamed over time

**This is why analysts must understand the *decision behind* the metric**, not just report the number — because the number will eventually lie once someone's incentivised by it.

## Defining a metric precisely

The unglamorous but critical part: **an ambiguous metric definition means every team reports a different number and nobody trusts the dashboard.** "Active user" — active how recently? Any action, or a meaningful one? Logged-in sessions or API calls? **Write the definition down, put it in one place** (the [[data-engineering/07-transformation-and-dbt|semantic/transformation layer]]), and make it the single source of truth. Analytics failures are as often *definitional* ("we're counting it differently") as technical.

## Key insight

**Choosing metrics is higher-stakes than analysing them, because the whole organisation steers by them — and the two failure modes are vanity metrics (numbers that only go up and measure how long you've existed, not how well you're doing) and Goodhart's Law (any metric you optimise gets gamed and stops meaning what you wanted).** Good metrics are actionable rates, comparable, precisely defined, and structured into a tree that decomposes a goal into diagnosable levers, with leading indicators paired to lagging goals and guardrails paired to targets. The analyst's job is to understand the *decision behind* each metric, because a number reported without that understanding will eventually mislead the people acting on it.

## Related
- [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]] — walking the metric tree to explain a change
- [[data-analysis/05-product-and-business-analytics|product and business analytics]] — the specific product metrics
- [[data-analysis/07-dashboards-and-bi|dashboards and BI]] — where metrics get surfaced (and their definitions live)
- [[foundations/systems-engineering/05-trade-studies|trade studies]] — weighting criteria, the same "what do we optimise" problem

*Source: [reference] — Goodhart's Law, and modern analytics practice. Sep 2026.*
