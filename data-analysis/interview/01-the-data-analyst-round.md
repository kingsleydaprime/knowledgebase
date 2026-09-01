# The Data Analyst Round

**[Intermediate]** — what gets asked, what a strong answer covers, and the detail that separates memorised from understood. 🔥 marks the ones asked constantly. The analyst round is **half SQL screen, half case study.**

## The SQL screen — expect it, live

**🔥 Q: Get the top 3 products by sales in each category.**

**A strong answer covers:** a window function — `ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC)` in a subquery/CTE, then filter `rn <= 3`.

**The detail worth adding:** knowing why `GROUP BY` can't do this (it collapses rows; you need per-row ranking that keeps the rows), and `RANK()` vs `ROW_NUMBER()` for ties → [[data-analysis/02-sql-for-analysis|window functions]]. **This exact question, or a close variant, is the most common analyst SQL screen.**

**🔥 Q: Compute month-over-month revenue growth.**

**A strong answer covers:** aggregate to monthly revenue (CTE), then `LAG(revenue) OVER (ORDER BY month)` and the percentage change. Building it as chained CTEs, not nested subqueries.

**The detail worth adding:** the integer-division trap (`100.0 *`), and handling the first month's NULL prev-value.

**Q: Your query says £2M revenue, finance says £2.4M. What's wrong?**

**A strong answer covers:** almost certainly a **join fan-out** (a one-to-many join multiplying rows — check with `COUNT(*)` vs `COUNT(DISTINCT)`), a filter excluding rows finance includes, or a **definition mismatch** ("completed" orders vs all orders, test data in or out).

**The detail worth adding:** the instinct to *stop and reconcile against a known source* before trusting any analysis → [[data-analysis/04-exploratory-and-diagnostic-analysis|sanity-check totals]]. Naming fan-out as the #1 analytical SQL bug shows real experience.

## The diagnostic case — the heart of the round

**🔥 Q: Revenue dropped 20% last week. Walk me through how you'd investigate.**

**A strong answer covers the method, not a guess:**
1. **Is it real?** Check against normal variation and **seasonality** — is last week actually low, or is it just a holiday/weekend effect? → [[data-analysis/06-time-series-analysis|seasonality]]
2. **Decompose** — revenue = users × conversion × order value. Which factor moved? → [[data-analysis/03-metrics-and-kpis|the metric tree]]
3. **Segment** the moved factor — by device, geography, channel — to localise it
4. **Correlate with events** — a release, a price change, an outage, a campaign ending
5. **Form and verify a hypothesis**

**The detail worth adding, and it's what they're testing:** **structure over intuition.** A weak candidate starts guessing causes; a strong one runs the search systematically and says "associated with" until they've verified. Mentioning that most such drops turn out to be seasonality or a deploy shows you've done this for real → [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]].

**Q: A/B test — variant B has higher conversion. Ship it?**

**A strong answer covers:** not yet — is the difference **statistically significant**, and is the **sample big enough**? Check for pitfalls: sample-ratio mismatch, peeking (stopping early when it looked good), novelty effects, and whether a *guardrail* metric (retention, revenue) got worse while conversion improved → [[data-analysis/03-metrics-and-kpis|guardrails]].

**The detail worth adding:** effect size *and* confidence interval, not just a p-value; and Goodhart — optimising conversion alone can hurt what you actually care about → [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|A/B testing]].

## Metrics and product

**🔥 Q: How would you measure the success of [feature / product]?**

**A strong answer covers:** start from the **decision/goal**, pick an **actionable** metric (a rate, not a vanity count), pair a **leading indicator** with the **lagging** goal, and name a **guardrail** so you don't win one metric while losing another. Define it precisely.

**The detail worth adding:** distinguishing the *North Star* (customer value) from revenue, and flagging the vanity trap ("total users only goes up") → [[data-analysis/03-metrics-and-kpis|metrics and KPIs]]. This question is really "do you think in decisions or in numbers?"

**Q: Define "active user."**

**A strong answer covers:** there's no universal answer — it depends on the product — but it must be *precise and singular*: active how recently (DAU/WAU/MAU?), doing what (any action vs a meaningful one?). The point is that an ambiguous definition means every team reports a different number → [[data-analysis/07-dashboards-and-bi|the semantic layer]].

**Q: What's a cohort analysis, and why use it?**

**A strong answer covers:** grouping users by when they started and tracking each group over time — because it separates *growth* from *retention* (you can grow by acquisition while every cohort churns). The retention curve *flattening* is the product-market-fit signal → [[data-analysis/05-product-and-business-analytics|cohorts]].

**Q: LTV:CAC — what is it and why does it matter?**

**A strong answer covers:** lifetime value over acquisition cost — the ratio that decides if the business model works. Below 1, you lose money on every customer and growth makes it worse. A retention improvement raises LTV and the ratio → [[data-analysis/05-product-and-business-analytics|unit economics]].

## Communication and judgement

**🔥 Q: How do you present a finding to a non-technical executive?**

**A strong answer covers:** **lead with the answer** (bottom line up front), state the "so what" and its size, then support it — tailored to what *they* need (the decision and magnitude, not your process). One chart, one message, message in the title.

**The detail worth adding:** honesty about uncertainty, not misleading with a truncated axis, and offering a *recommendation* rather than a neutral data dump → [[data-analysis/08-communicating-analysis|communicating analysis]]. This is often the question that most separates candidates, because it reveals whether they understand the deliverable is a decision.

**Q: You found the data doesn't support what your stakeholder hoped. What do you do?**

**A strong answer covers:** present the honest finding, clearly and tactfully, with the evidence. Analyst integrity is presenting what the data *says*, not what someone wanted — and credibility (the analyst's real currency) is destroyed by one confident wrong answer.

## What this round tests

1. **Live SQL fluency** — window functions especially, and the instinct to sanity-check
2. **Structured diagnosis** — a method for "why did it change," not guessing
3. **Product/metric sense** — thinking in decisions and actionable metrics, not vanity numbers
4. **Communication** — leading with the answer, honest, tied to an action

## Related
- [[data-analysis/README|the data analysis course]] · [[data-analysis/projects|projects]]
- [[databases/interview/README|databases interview]] — deeper SQL · [[ai-ml/interview/README|ai-ml interview]] — the stats/DS side
- [[INTERVIEW|Interview Prep Index]]
