# Descriptive Statistics

**[reference]** — from the roadmap.sh `data-analyst`/`ai-data-scientist` roadmaps. Summarizing a dataset honestly — the first thing you do with any data, and the foundation [[ai-ml/01-data-scientist/03-inferential-statistics|inference]] builds on. Complements the probability basis in [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|foundations]].

Descriptive statistics *describe the data you have* (no claims beyond it); [[ai-ml/01-data-scientist/03-inferential-statistics|inferential]] statistics generalize from a sample to a population. This note is the first.

## Central tendency — the "typical" value

| Measure | What it is | When to use |
|---|---|---|
| **Mean** | the average | symmetric data with no extreme outliers |
| **Median** | the middle value | **skewed** data or data with outliers — robust |
| **Mode** | the most frequent value | categorical data, or finding the most common case |

The single most important instinct: **the mean is not robust to outliers.** One billionaire in a room makes the *mean* income misleading while the *median* stays honest. Income, house prices, and response times are famously right-skewed — report the median. Whenever mean and median diverge a lot, the distribution is skewed, and which one you report can change the story (sometimes dishonestly).

## Dispersion — how spread out the data is

A "typical value" means little without knowing the spread around it. Two datasets can share a mean while one is tightly clustered and the other wildly variable.

- **Range** — max − min. Simple, but entirely determined by the two most extreme points.
- **Variance** — the average squared distance from the mean ([[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/02-expectation-and-variance|expectation & variance]]). Squaring makes units awkward.
- **Standard deviation** — the square root of variance, back in the original units — the everyday measure of spread ("scores are 72 ± 8").
- **IQR (interquartile range)** — the range of the middle 50% (Q3 − Q1). Robust to outliers, and the basis of the box plot and a common outlier rule (points beyond 1.5×IQR from the quartiles).

```python
import numpy as np
np.mean(x), np.median(x), np.std(x)
np.percentile(x, [25, 50, 75])   # quartiles → IQR
```

## Distribution shape

Beyond center and spread, the *shape*:

- **Skewness** — asymmetry. **Right-skewed** (positive): a long tail to the right, mean > median (income). **Left-skewed** (negative): long left tail, mean < median. Symmetric ≈ 0.
- **Kurtosis** — "tailedness": how heavy the tails are. High kurtosis means more extreme outliers than a normal distribution — critical in finance, where fat tails mean rare catastrophic events are more likely than a normal model assumes.

Why shape matters: many methods assume roughly normal (bell-shaped) data. Strong skew or heavy tails can invalidate those assumptions, mislead the mean, and call for a transformation (e.g. log) or a robust method. Always *look* at the distribution ([[ai-ml/01-data-scientist/05-data-visualization|visualize]] it) before trusting a summary number — this is the heart of [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]].

## Correlation — how two variables move together

**Correlation** measures whether two variables rise and fall together, from −1 (perfect inverse) through 0 (none) to +1 (perfect positive):

- **Pearson** — measures *linear* correlation. Misses non-linear relationships and is sensitive to outliers.
- **Spearman** — rank-based; captures any *monotonic* relationship and is robust to outliers. Reach for it when the relationship is non-linear-but-consistent-direction.

```python
import scipy.stats as stats
stats.pearsonr(x, y)    # linear
stats.spearmanr(x, y)   # monotonic, robust
```

**The cardinal warning: correlation is not causation.** Two variables can correlate because one causes the other, because a third thing causes both (a *confounder*), or by pure chance (spurious correlation — ice-cream sales and drownings both rise in summer). Descriptive correlation *describes* an association; establishing *cause* requires the [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal inference]] tools, ideally a controlled [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|experiment]]. Confusing the two is the single most common — and most consequential — mistake in data analysis.

## The one habit

Compute the summary numbers *and* plot the data. **Anscombe's quartet** — four datasets with identical mean, variance, and correlation but wildly different shapes (a line, a curve, an outlier-driven fit) — is the classic proof that summary statistics alone lie. Numbers plus a picture, always.

## Related
- [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/02-expectation-and-variance|Expectation & Variance]] — the probability basis of variance
- [[ai-ml/01-data-scientist/03-inferential-statistics|Inferential Statistics]] — generalizing beyond the sample
- [[ai-ml/01-data-scientist/04-exploratory-data-analysis|Exploratory Data Analysis]] — descriptive stats as a process
