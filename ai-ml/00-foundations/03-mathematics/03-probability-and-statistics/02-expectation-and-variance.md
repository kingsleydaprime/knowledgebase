---
id: 605af7e6-d4a1-4d08-82f4-c59f0c17b867
---

# Expectation and Variance

Two numbers that summarize a probability distribution without needing to describe its entire shape: expectation tells you the center, variance tells you the spread. Both show up constantly in how ML models are evaluated.

## Expectation (mean) — the average outcome
<!-- bite: d76f7a07-b21b-4316-8f5d-cd235f5b4f45 -->

The expected value of a random process is its average outcome, weighted by probability — "what value do I expect on average, across many repetitions?" For a model's error on a test set, the mean error is the single most commonly reported evaluation number.

## Variance — how spread out outcomes are
<!-- bite: f16d8202-42ca-4c6f-a381-096ca2a8e37d -->

Variance measures how far outcomes typically fall from the mean. Low variance means outcomes cluster tightly around the average; high variance means they're scattered widely, including possibly far from it.

```
low variance:   outcomes near mean: 48, 51, 49, 50, 52
high variance:  outcomes near mean: 10, 90, 45, 5, 95     (same mean, wildly different spread)
```

## Why both numbers matter together for evaluating a model
<!-- bite: a70cdc36-f30f-4ae8-8681-4f4634807443 -->

Reporting only the mean error hides a critical distinction: a model with low average error but occasional huge misses (high variance) can be far more dangerous in practice than one with a slightly higher average error but consistent, predictable behavior (low variance) — depending on what a bad miss actually costs in the real application. Model evaluation reports that show only one aggregate accuracy number are, by construction, hiding this — which is why looking at the distribution of errors (not just its mean) matters for anything where the cost of a rare, bad failure is high.

## Standard deviation — variance, back in the original units
<!-- bite: 2f3c1f18-5d6d-4123-a1b1-b84505bcea8c -->

Variance is in *squared* units (a squared-dollar error doesn't mean much intuitively), so **standard deviation** — the square root of variance — is usually what's actually reported, since it's back in the same units as the original quantity. "Predictions are typically off by about $12,000" (a standard deviation) is more directly interpretable than a variance expressed in squared dollars.

## Gotchas
<!-- bite: 58466083-5c25-41f7-a74e-c8a4f79601e0 -->

- A model can have excellent mean accuracy purely by doing very well on the common/easy cases and being consistently wrong on a rare but important minority of inputs — always worth checking accuracy broken out by subgroup or input type, not just the overall average, especially when different kinds of input carry very different real-world stakes.
- **Calibration** is a related but distinct concept from accuracy: a well-calibrated model's stated confidence (e.g. "80% likely") should match its actual correctness rate across many predictions at that confidence level. A model can be accurate on average while being poorly calibrated (systematically over- or under-confident) — checking calibration is a separate exercise from checking accuracy.

## Related
<!-- bite: 9aaddb7a-dbe1-4ce4-a4cd-259533be7a01 -->
- [[01-distributions|distributions]]
- [[03-bayes-theorem|bayes-theorem]]
