---
id: 605af7e6-d4a1-4d08-82f4-c59f0c17b867
---

# Expectation and Variance

Expectation is the centre of a distribution; variance is its spread.

## What expectation and variance are
<!-- bite: 58b3be41-9e16-498f-a6c7-0aa16ebf1dbf -->

Two numbers that summarize a probability distribution without needing to describe its entire shape: expectation tells you the center, variance tells you the spread. Both show up constantly in how ML models are evaluated.

Next: each one in turn, then why you need both.

## Expectation (mean) — the average outcome
<!-- bite: d76f7a07-b21b-4316-8f5d-cd235f5b4f45 -->

The expected value of a random process is its average outcome, weighted by probability — "what value do I expect on average, across many repetitions?" For a model's error on a test set, the mean error is the single most commonly reported evaluation number.

## Variance — how spread out outcomes are
<!-- bite: f16d8202-42ca-4c6f-a381-096ca2a8e37d -->

Variance measures how far outcomes typically fall from the mean. Low variance means outcomes cluster tightly around the average; high variance means they're scattered widely, including possibly far from it.

```text
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

## Check your understanding
<!-- bite: 03489f5d-b10b-40ef-9420-1dd0ef58b540 -->

Try each one before you open the answer.

1. <!-- q: exact id="a8d064de" answer="50" accept="fifty" -->
   The outcomes are 48, 51, 49, 50, 52. What is the mean?

   <details><summary>Answer</summary>

   50. (48 + 51 + 49 + 50 + 52) ÷ 5 = 250 ÷ 5 = 50.

   </details>

2. <!-- q: mcq id="911db258" -->
   Two sets of outcomes: A is 48, 51, 49, 50, 52 and B is 10, 90, 45, 5, 95. Which has the higher variance?

   - [ ] A
   - [x] B
   - [ ] They have the same variance

   <details><summary>Answer</summary>

   B. Both have a mean around 50, but B's outcomes are scattered much further from it.

   </details>

3. <!-- q: gap id="71507bc9" answers="square root;standard deviation" -->
   Fill in the gaps. Variance is in squared units, so we usually report its ___, which is called the ___.

   <details><summary>Answer</summary>

   Square root, then standard deviation. It is back in the original units, so "off by about $12,000" makes sense to a reader.

   </details>

4. <!-- q: mcq id="28b62521" -->
   Model A has a slightly lower average error than model B but sometimes makes huge misses. B is consistent. Which statement is right?

   - [ ] A is always better because its average error is lower
   - [x] B may be safer when a rare bad miss is expensive
   - [ ] They are the same because averages are what count

   <details><summary>Answer</summary>

   B may be safer. The mean hides the spread. When a rare bad failure costs a lot, a predictable model can be the better choice.

   </details>

5. <!-- q: open id="30eb88f8" -->
   What is calibration, and how is it different from accuracy?

   <details><summary>Answer</summary>

   A calibrated model's stated confidence matches how often it is right: across all its "80% likely" answers, about 80% are correct. Accuracy is just how often it is right overall. A model can be accurate on average while being over- or under-confident.

   </details>

## Check your understanding: worked problems
<!-- bite: 1cbaad3d-c58f-40a1-9d51-3565a5a6d9af -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="485e3c6b" answer="3.5" accept="7/2" -->
   What is the expected value when you roll a fair six-sided die?

   <details><summary>Answer</summary>

   3.5. (1 + 2 + 3 + 4 + 5 + 6) ÷ 6 = 21 ÷ 6 = 3.5. It is an average, so it doesn't have to be a possible roll.

   </details>

2. <!-- q: exact id="6bcc3599" answer="2.66666666667" accept="8/3" sigfigs="2" -->
   The outcomes 2, 4 and 6 are equally likely. Variance is the average squared distance from the mean. What is the variance?

   <details><summary>Answer</summary>

   About 2.67. The mean is 4. The squared distances are 4, 0 and 4, and their average is 8/3 ≈ 2.67.

   </details>

3. <!-- q: exact id="1b53b979" answer="1.63299316186" sigfigs="2" -->
   Using the same outcomes, what is the standard deviation?

   <details><summary>Answer</summary>

   About 1.63. It is the square root of the variance: √(8/3) ≈ 1.633, back in the original units.

   </details>

## Related
<!-- bite: 9aaddb7a-dbe1-4ce4-a4cd-259533be7a01 -->
- [[01-distributions|distributions]]
- [[03-bayes-theorem|bayes-theorem]]
