# Exploratory and Diagnostic Analysis

**[Intermediate]** — understanding a dataset before you trust it, and answering the question that pays the analyst's salary: *"why did this number change?"*

## The kid version first

Two of the most common analyst tasks: first, **getting to know a new dataset** — what's in it, what's weird, what you can trust (exploratory). Second — and this is the valuable one — **explaining a change**: sales dropped, signups spiked, a metric moved, and someone needs to know *why* (diagnostic). "Revenue fell 12%" is a fact anyone can pull; "revenue fell 12% *because* mobile checkout broke in Germany after Tuesday's release" is the insight that leads to a fix.

## Exploratory data analysis — understand before you trust

Before any analysis, you explore the data to understand its shape and catch the problems that would otherwise silently corrupt your answer. This is [[ai-ml/01-data-scientist/04-exploratory-data-analysis|the data-scientist's EDA]] pointed at business questions rather than modelling:

**Profile every column:**
- **Completeness** — how much is missing, and is it missing *randomly* or systematically? A column that's null for all of last month signals a broken pipeline, not "no data"
- **Distribution** — the shape, the range, the outliers. Is "order value" mostly £20 with a few £50,000 (a data error, or a genuine whale)?
- **Cardinality and categories** — how many distinct values; are "UK", "U.K.", and "United Kingdom" three categories that should be one?
- **Relationships** — how columns relate, which is where the story usually is

**Always sanity-check before you trust:**
- **Do the totals match a known source?** If your query says £2M revenue and finance says £2.4M, *stop* — you have a join fan-out, a filter, or a definition mismatch → [[data-analysis/02-sql-for-analysis|join fan-out]]
- **Do the counts make sense?** More orders than users? More completed than started? These impossibilities reveal bugs
- **Look at the raw rows**, not just aggregates — a `GROUP BY` hides the individual weirdness that explains everything

**The discipline: distrust the data until it earns your trust.** The most expensive analytical mistakes are confident conclusions from data that was quietly wrong → [[data-engineering/10-data-quality-governance-and-the-stack|data quality]].

## Segmentation — the analyst's superpower

**Almost every real insight comes from breaking an aggregate apart.** The overall number hides the story; the segments reveal it:

```
   "Conversion is 3%"                    ← useless aggregate
        │ segment by device
   Desktop: 5%   Mobile: 1%              ← now there's a story
        │ segment mobile by country
   Mobile/UK: 4%   Mobile/DE: 0.2%       ← now there's a ROOT CAUSE
```

**Slicing by dimension — device, geography, channel, cohort, plan, time — is how you turn "something changed" into "*this specific thing* changed."** The skill is knowing which dimensions to slice by (the ones tied to plausible causes) and recognising when a segment is different enough to matter → [[data-analysis/05-product-and-business-analytics|segmentation in product analytics]].

## Diagnostic analysis — "why did it change?"

The high-value task, and it has a method rather than being pure intuition:

**1. Confirm the change is real.** Is the drop outside normal variation, or just noise? Check against the metric's usual week-to-week wobble before investigating → [[data-analysis/06-time-series-analysis|is it just seasonality?]]. Many "changes" are noise, and chasing noise wastes days.

**2. Walk the metric tree.** Decompose the metric into its factors and find *which one* moved → [[data-analysis/03-metrics-and-kpis|the metric tree]]:
```
   Revenue = Users × Conversion × Order Value
   → Users flat, Order Value flat, Conversion DOWN → the problem is conversion
```

**3. Segment the moved factor.** Once you know conversion dropped, slice it — by device, geography, channel, time — to localise *where*. The drop is rarely uniform; it's concentrated in a segment, and that segment points at the cause.

**4. Correlate with events.** Line the change up against a timeline: a release, a marketing change, a price change, an outage, a competitor move, a holiday. **"It started exactly when we deployed X" is the most common finding**, and it's why analysts keep a change log handy.

**5. Form a hypothesis and confirm it.** "Mobile-DE conversion dropped after Tuesday's release → probably the checkout." Then *verify* — look at the checkout errors, the funnel, the specific step → [[data-analysis/05-product-and-business-analytics|funnel analysis]].

**The structure is: confirm real → decompose → segment → correlate with events → verify.** It turns a vague "why did it drop?" from guesswork into a search.

## The traps that produce wrong conclusions

Diagnostic analysis is where analysts most often mislead themselves and others:

**Correlation is not causation.** Two things moving together doesn't mean one caused the other — a confounder may drive both, or it's coincidence. For a *causal* claim you need an [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|experiment]] or [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal inference]]. **Analysts should say "associated with" unless they've earned "caused by."**

**Simpson's Paradox** — a trend that appears in every segment can *reverse* in the aggregate (or vice versa), because of how segment sizes shift. A treatment can look worse overall but better in every subgroup. **This is why you segment**, and why an aggregate can lie even when it's arithmetically correct → [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|confounders]].

**Confirmation bias and cherry-picking** — finding the segment or timeframe that confirms what you (or your stakeholder) wanted, and stopping there. **Actively look for the segment that *breaks* your hypothesis.**

**Survivorship and selection bias** — analysing only the data that's present (the customers who stayed, the sessions that completed) and forgetting the ones that dropped out, which is often where the answer is.

## Key insight

**Exploratory analysis is distrusting data until it earns your trust (profile, sanity-check totals, look at raw rows), and diagnostic analysis is the high-value skill of explaining a change with a method rather than a guess: confirm the change is real, decompose the metric to find which factor moved, segment that factor to localise where, correlate with events to find when-and-therefore-what, and verify.** Segmentation is the superpower — almost every real insight comes from breaking an aggregate apart, and the aggregate itself can lie (Simpson's paradox). Throughout, the discipline is intellectual honesty: say "associated with" until you've earned "caused by," and hunt for the segment that breaks your hypothesis rather than the one that confirms it.

## Related
- [[data-analysis/03-metrics-and-kpis|the metric tree]] — the decomposition diagnostic analysis walks
- [[data-analysis/05-product-and-business-analytics|product and business analytics]] — the specific analyses
- [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA (data science)]] — the modelling-focused version
- [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal inference]] — when you need "caused by"

*Source: [reference] — Sep 2026.*
