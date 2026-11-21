---
id: 7db5be35-19a5-4eeb-aa9d-78395c830a82
---

# Experimentation & A/B Testing

An A/B test is an experiment where you randomly show some users one version of something (A) and other users another version (B), then compare what they do. Because the groups are chosen at random, you can tell whether the change itself caused the difference. Apps you use, like shopping and social media apps, run tests like this on button colours, prices and layouts all the time.

## Why experiments beat observation
<!-- bite: 0c30a4d3-b798-4953-a653-b4c53bfd48e4 -->

[[ai-ml/01-data-scientist/02-descriptive-statistics|Correlation isn't causation]] — observational data can't cleanly tell whether X caused Y or a [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|confounder]] caused both. A **randomized controlled experiment** solves this: by randomly assigning subjects to a **control** group (current experience) and a **treatment** group (the change), randomization makes the groups statistically identical *on average* in every respect except the change — so any difference in outcome can be attributed to the change itself. This is why A/B testing is the causal gold standard, and why "we shipped it and metrics went up" (no control) is not evidence.

## Anatomy of an A/B test
<!-- bite: e35b9686-e1d7-4cbe-a8c8-248dd6c31f14 -->

1. **Hypothesis** — a specific, falsifiable claim: "changing the button from grey to blue will increase click-through."
2. **Metric** — pick the primary success metric *up front* (conversion rate, revenue per user). One primary metric avoids the temptation to fish for any metric that moved.
3. **Randomize** — split users randomly into control (A) and treatment (B). Randomization is what buys causality; a biased split (e.g. by time of day, or by device) reintroduces confounding.
4. **Sample size** — run a **power analysis** *before* starting ([[ai-ml/01-data-scientist/03-inferential-statistics|statistical power]]) to know how many users you need to detect an effect worth caring about. Too small → you can't distinguish a real effect from noise.
5. **Run it** — for a pre-decided duration (full business cycles — at least a week or two, to cover weekday/weekend and novelty effects).
6. **Analyze** — a [[ai-ml/01-data-scientist/03-inferential-statistics|hypothesis test]] on the primary metric, reporting the effect size **and** a confidence interval, not just a p-value.
7. **Decide** — ship, don't ship, or iterate — based on statistical *and* practical significance.

## The pitfalls (where experiments go wrong)
<!-- bite: 3e7d3d34-76cf-4a1f-8eff-e7651725c6e3 -->

These are exactly the mistakes a rigorous data scientist prevents:

- **Peeking / early stopping** — checking results continuously and stopping the moment it's "significant" massively inflates false positives (it's [[ai-ml/01-data-scientist/03-inferential-statistics|p-hacking]] in time). Decide the sample size and duration up front, or use sequential-testing methods designed for peeking.
- **Too many metrics** — testing 20 metrics and celebrating the one that's significant is the [[ai-ml/01-data-scientist/03-inferential-statistics|multiple-comparisons]] trap. Pre-register a primary metric; treat the rest as exploratory.
- **Novelty & primacy effects** — users react to *change itself* at first (a spike that fades, or resistance that fades). Short tests capture the reaction, not the steady state.
- **Sample ratio mismatch (SRM)** — if your 50/50 split arrives as 48/52, the randomization is broken (a bug, a bot, a redirect), and the whole test is suspect. Check it.
- **Network effects / interference** — when treating one user affects control users (social features, marketplaces, shared inventory), the groups aren't independent and standard A/B analysis breaks — needs cluster-randomization or a different design.
- **Simpson's paradox** — an effect that holds in every subgroup can *reverse* in the aggregate (or vice versa) when subgroup sizes differ. Always check whether a result survives segmentation.

## Beyond the simple A/B
<!-- bite: 12fad5fc-418d-47fe-a5a6-833d28292c45 -->

- **A/B/n** — more than two variants at once (costs more sample per variant).
- **Multivariate testing** — test combinations of several changes to find interactions (sample-hungry).
- **Multi-armed bandits** — dynamically shift traffic toward the winning variant *during* the test, trading some statistical cleanliness for less "regret" (fewer users seeing the worse option) — good for short-lived decisions like promos.
- **Quasi-experiments** — when you *can't* randomize (can't A/B a pricing law), the [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal inference]] toolkit (difference-in-differences, regression discontinuity) approximates an experiment from observational data.

## Related
<!-- bite: 1dde5520-bc59-4d41-96bb-998715a566c8 -->
- [[ai-ml/01-data-scientist/03-inferential-statistics|Inferential Statistics]] — the hypothesis testing and power analysis behind every experiment
- [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|Causal Inference & Econometrics]] — establishing causation when you can't randomize
- [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|Serving & Operations (ML-engineer)]] — A/B testing models on live traffic

## About this lesson
<!-- bite: 49af3b4a-ee4b-472d-80dd-521e3232c8b0 -->

**Level:** reference. **Covers:** from the roadmap.sh `ai-data-scientist` roadmap. The gold standard for answering "does X actually *cause* a better outcome?" — and one of the highest-impact things a data scientist does, since it directly drives product and business decisions.
