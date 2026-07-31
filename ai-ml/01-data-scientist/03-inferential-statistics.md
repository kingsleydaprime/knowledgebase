# Inferential Statistics

**[reference]** — from the roadmap.sh `ai-data-scientist`/`data-analyst` roadmaps. The core discipline of data science: drawing trustworthy conclusions about a whole **population** from a limited **sample**, and knowing how much to trust them. This is the skill that separates a data scientist from someone who eyeballs a chart.

## Population vs sample — the whole point

You almost never have all the data (the whole population); you have a **sample** and want to conclude something about the population. Inferential statistics quantifies **how confident** you can be in that leap, and how much your answer would wobble if you'd drawn a different sample. Everything here is about honestly handling that uncertainty.

## Sampling distributions and the Central Limit Theorem

If you took many samples and computed each one's mean, those means would form a **sampling distribution**. The **Central Limit Theorem (CLT)** is the near-magical result underpinning most of inference: *the sampling distribution of the mean is approximately normal for a large enough sample, regardless of the population's shape.* This is why normal-based methods work so broadly — even on skewed data, the *mean* behaves normally.

The spread of that sampling distribution is the **standard error** (SE) — roughly `std / √n`. The key consequence: **more data → smaller SE → more precise estimates**, but with diminishing returns (halving the error needs 4× the data, because of the √n).

## Confidence intervals — an estimate with honest error bars

A point estimate ("the mean is 42") hides its uncertainty. A **confidence interval** gives a range: "we're 95% confident the true mean is between 38 and 46." Wider interval = less certain; narrower = more (from more data or less variance).

The subtle-but-important interpretation: a 95% CI means *if you repeated the sampling many times, 95% of the intervals would contain the true value* — not "95% probability the true value is in this one interval." In practice: **always report an interval, not just a point** — a naked number implies a false precision, and the width of the interval is often the most decision-relevant fact.

## Hypothesis testing — is this effect real or noise?

The formal framework for "did something actually happen, or could this be random chance?"

1. **Null hypothesis (H₀)** — the skeptical default: "no effect / no difference." (The new button doesn't change conversion.)
2. **Alternative hypothesis (H₁)** — what you suspect: "there is an effect."
3. Compute a **test statistic** and its **p-value**.
4. If the p-value is below a threshold (**significance level α**, usually 0.05), **reject H₀** — the effect is "statistically significant."

### What a p-value actually is

**The p-value is the probability of seeing data at least this extreme *if the null hypothesis were true*.** A small p-value means "this result would be surprising if there were really no effect," so you doubt the null. It is **not** the probability the null is true, and **not** the probability your result happened by chance — those are the near-universal misreadings.

### The pitfalls (this is where data scientists earn their keep)

- **Statistical ≠ practical significance.** With enough data, a *trivial* effect (0.01% lift) becomes "significant." Significance says an effect is *real*; the **effect size** says whether it *matters*. Always report both.
- **p = 0.049 vs 0.051 is not a real difference** — the 0.05 threshold is a convention, not a law of nature. Treat p-values as continuous evidence, not a pass/fail gate.
- **p-hacking / multiple comparisons** — test 20 things and ~1 will look "significant" at p<0.05 by pure chance. Testing many hypotheses, or peeking repeatedly and stopping when significant, manufactures false positives. Corrections (Bonferroni, FDR) and pre-registration guard against it. This is a major source of irreproducible results.
- **Absence of significance ≠ evidence of no effect** — failing to reject H₀ might just mean too little data (low power), not that there's no effect.

## Type I / Type II errors and power

Two ways to be wrong, and they trade off:

| | H₀ actually true | H₀ actually false |
|---|---|---|
| **Reject H₀** | **Type I error** (false positive, rate = α) | correct |
| **Fail to reject** | correct | **Type II error** (false negative, rate = β) |

**Statistical power** (1 − β) is the probability of detecting a real effect. Underpowered studies (too small a sample) miss real effects and produce noisy, unreplicable findings. Before an [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|experiment]], a **power analysis** computes the sample size needed to reliably detect an effect worth caring about — a step amateurs skip and regret.

## The common tests

Match the test to the data:

| Test | Use for |
|---|---|
| **t-test** | comparing the means of two groups (A/B test on a continuous metric) |
| **ANOVA** | comparing means across 3+ groups |
| **Chi-square** | association between two categorical variables |
| **Correlation test** | is a [[ai-ml/01-data-scientist/02-descriptive-statistics|correlation]] significantly different from zero? |
| **Mann-Whitney / non-parametric** | when normality assumptions don't hold |

```python
import scipy.stats as stats
stats.ttest_ind(group_a, group_b)   # returns statistic, p-value
```

Each test has **assumptions** (normality, equal variances, independence) — violating them invalidates the p-value, so check them (or use a robust/non-parametric alternative).

## Related
- [[ai-ml/01-data-scientist/02-descriptive-statistics|Descriptive Statistics]] — what you summarize before inferring
- [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|Experimentation & A/B Testing]] — hypothesis testing applied to real decisions
- [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/01-distributions|Distributions]] — the normal distribution the CLT invokes
