# Product and Business Analytics

**[Intermediate → Advanced]** — the specific analyses that *are* the analyst job: funnels, cohorts, retention, and the unit economics that decide whether a business works.

## The kid version first

Most analyst work isn't abstract — it's a handful of standard, high-value analyses that every product and growth team needs: **where do users drop off (funnels), do they come back (retention/cohorts), and is each customer worth more than they cost (unit economics)?** These aren't exotic techniques; they're the bread and butter, and knowing them cold is most of being a product/business analyst.

## Funnel analysis — where do users drop off?

A **funnel** is a sequence of steps toward a goal, and the analysis is measuring how many users make it through each:

```
   Visited        10,000  ██████████
   Added to cart   3,000  ███         ← 70% drop here. Biggest leak
   Checkout        2,400  ██
   Purchased       1,800  ██          ← 3,000 → 1,800 = 60% checkout conversion
```

**The point is finding the biggest leak** — the step with the worst drop-off is where a fix has the most leverage. A 10% improvement at the step that loses 70% of users is worth far more than perfecting a step that already converts 90% → [[data-analysis/02-sql-for-analysis|funnels in SQL]].

**The subtleties that matter:**
- **Time window** — do steps have to happen in one session, or within N days? A "funnel" over an unbounded window overcounts
- **Order** — strict (must go A→B→C) or any-order? Real users skip and backtrack
- **The denominator** — conversion "of visitors" vs "of those who reached the previous step" are different numbers that answer different questions. **Be explicit about which**
- **Segment the funnel** — the overall funnel hides that mobile drops at checkout while desktop drops at cart → [[data-analysis/04-exploratory-and-diagnostic-analysis|segmentation]]

## Cohort analysis and retention — do they come back?

**A cohort is a group of users bound by when they started**, and cohort analysis tracks each group over time — which separates "are we growing?" from "are we *retaining*?" (a business can grow by acquisition while every cohort churns, which is a leaky bucket that eventually empties).

```
   Retention by signup cohort (% still active):
              Month 0   Month 1   Month 2   Month 3
   Jan cohort   100%      45%       38%       35%
   Feb cohort   100%      48%       41%       39%    ← Feb retains better — what changed?
   Mar cohort   100%      52%       —         —      ← improving. Good sign
```

**Reading a retention curve:**
- **The shape is the product's health.** A curve that keeps falling to zero = users never stick (a real problem, no acquisition fixes it). A curve that *flattens* = you've found a core of users who stay — **the "retention plateau" is the single most important signal of product-market fit**
- **Compare cohorts** to see if changes helped — did users who joined after the redesign retain better?
- **Retention beats acquisition** — retaining an existing user is far cheaper than acquiring a new one, and a product that doesn't retain can't grow no matter how much it spends → [[data-analysis/02-sql-for-analysis|cohorts in SQL]]

**Churn** is retention's mirror: the rate users leave. **Analysing churn** — who churns, when, and the leading signals that precede it → is one of the highest-value analyses, because a leading churn indicator lets you intervene *before* the customer is gone → [[data-analysis/03-metrics-and-kpis|leading indicators]].

## Unit economics — does the business work?

The analyses that decide whether a business is viable, not just growing:

- **CAC (Customer Acquisition Cost)** — what it costs to get one customer (marketing + sales ÷ customers acquired)
- **LTV (Lifetime Value)** — the total profit from a customer over their lifetime (roughly: average revenue per period × gross margin × expected lifetime, where lifetime ≈ 1/churn rate)
- **The LTV:CAC ratio** — **the number that decides if a business model works.** If you spend more to acquire a customer than they're ever worth (LTV:CAC < 1), you lose money on every sale and growth makes it *worse*. A healthy ratio is often cited as ~3:1
- **Payback period** — how long until a customer's revenue recovers their acquisition cost. Shorter is better; it's a cash-flow reality, not just a profitability one

**Why analysts own this:** these numbers connect the product metrics (retention, conversion) to whether the company survives. **A retention improvement isn't just "nicer" — it lengthens lifetime, raises LTV, and improves the ratio that justifies the whole growth engine.** Connecting product analytics to unit economics is what makes an analyst a business partner rather than a report generator → [[data-analysis/01-what-data-analysis-is|the deliverable is a decision]].

## Acquisition and engagement

The rest of the standard toolkit:

- **Acquisition analysis** — which *channels* bring users, at what cost and quality. **Cheap channels often bring worse-retaining users**, so cost-per-acquisition without quality is misleading → segment acquisition by downstream retention, not just volume
- **Engagement metrics** — DAU/MAU (daily over monthly active users — the "stickiness" ratio; high means people use it most days), session frequency and depth, feature adoption. These are the [[data-analysis/03-metrics-and-kpis|leading indicators]] of retention
- **Segmentation and personas** — grouping users by behaviour (power users vs dabblers) to understand who your product actually serves, often via RFM (recency, frequency, monetary) or [[ai-ml/02-ml-engineer/03-classical-ml/README|clustering]]

## The connective tissue

These aren't separate — they form one story:

```
   acquisition → activation (funnel) → retention (cohorts) → revenue (LTV)
        │              │                    │                    │
        CAC        conversion            churn               LTV:CAC
```

**A good analyst reads across the whole chain:** a funnel fix improves activation, which feeds retention, which raises LTV, which justifies more acquisition spend. Understanding how a change in one propagates to the others is what turns a pile of metrics into a growth model → [[data-analysis/03-metrics-and-kpis|the metric tree]].

## The tools

Beyond SQL, product analysts often use **product-analytics platforms** — Amplitude, Mixpanel, PostHog, GA4 — which specialise in funnels, cohorts and event-based analysis over user behaviour, so you don't rebuild them in SQL every time. They're event-tracking systems ([[data-engineering/05-kafka-and-event-streaming|the event stream]]) with a funnel/cohort UI on top. **Know both** — the platform for speed, SQL for anything custom or when you need to trust the number yourself.

## Key insight

**Product and business analytics is a small set of standard, high-value analyses — funnels (where users leak), cohorts and retention (whether they come back, and the plateau that signals product-market fit), and unit economics (LTV:CAC, the ratio that decides if the business works) — connected into one chain from acquisition through revenue.** The craft is reading *across* that chain: a retention improvement lengthens lifetime, raises LTV, and justifies acquisition spend. Knowing these cold, and connecting product metrics to the unit economics that determine survival, is what makes an analyst a business partner rather than a report generator.

## Related
- [[data-analysis/02-sql-for-analysis|SQL for analysis]] — funnels, cohorts, retention in SQL
- [[data-analysis/03-metrics-and-kpis|metrics and KPIs]] — the metrics these analyses produce
- [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]] — explaining when these move
- [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|A/B testing]] — proving a change caused an improvement

*Source: [reference] — Sep 2026.*
