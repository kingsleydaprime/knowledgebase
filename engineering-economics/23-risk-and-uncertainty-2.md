---
id: bf0d4be3-52df-4fc1-8a1d-f580e2ff82da
---

# Risk and Uncertainty 2: Measuring Risk

Risk is measured with three numbers: the expected value, the standard deviation and the coefficient of variation.

## Before you start
<!-- bite: c0c4ae1b-43ef-4186-96ec-268d812982d8 -->

You should know what risk is from [[engineering-economics/22-risk-and-uncertainty-1|Risk and Uncertainty 1]].

After this lesson you will be able to:

1. calculate the expected value of a set of outcomes;
2. calculate the variance and standard deviation, and explain why two bets with the same expected value can carry very different risk;
3. use the coefficient of variation to compare projects of different sizes, and describe the three attitudes to risk.

## What measuring risk means
<!-- bite: 342057ad-65c0-4063-9a59-0767a1ca7531 -->

Under risk you know the possible outcomes and their probabilities. That's a lot of information, but you can't compare five projects by staring at five lists of outcomes. You want a few numbers that sum each project up.

Two questions matter. On average, what do I get? And how far from that average could I land? The first is the expected value. The second is the standard deviation.

## Expected value (mean)
<!-- bite: 5f015a3d-4306-48c3-9f9e-5f757ef77b94 -->

The expected value is the weighted average of outcomes, with probabilities as weights. Multiply each outcome by its probability and add them up:

$$E(x) = \mu = \sum x_i p_i$$

**Example:** a recession has a 40% chance and gives profit of 100; no recession has 60% and gives 1,000. E = 0.4(100) + 0.6(1,000) = **640**.

Notice you never actually get 640. You get 100 or 1,000. The expected value is what you'd average if you could make the same bet many times.

## Variance and standard deviation
<!-- bite: d0eede99-bd8f-46ac-a460-bddc49c14f10 -->

Variance and standard deviation measure how far outcomes are spread around the mean. Two bets can have the same expected value but very different risk.

The variance is the probability-weighted average of the squared distance from the mean. The standard deviation is its square root, which puts it back in the same units as the outcomes:

$$\sigma^2 = \sum p_i (x_i - \mu)^2 \qquad \sigma = \sqrt{\sigma^2}$$

**Example:** win or lose 10 with equal chance has mean 0 and variance 100 (σ = 10). Win or lose 1,000 has mean 0 and variance 1,000,000 (σ = 1,000). Same mean, but the second is far riskier.

## Worked example: the recession bet
<!-- bite: 52ec6220-7b09-415f-bb69-74b7dc242220 -->

Take the recession example again: 100 with probability 0.4, 1,000 with probability 0.6, mean 640.

1. Distances from the mean: 100 − 640 = −540, and 1,000 − 640 = 360.
2. Squared and weighted: 0.4 × 540² = 116,640, and 0.6 × 360² = 77,760.
3. Variance = 116,640 + 77,760 = 194,400.
4. σ = √194,400 ≈ **441**.

So the profit is 640 on average, but typically lands about 441 away from that. This step-by-step working was added for this lesson.

## Coefficient of variation (CV)
<!-- bite: 9d640354-122a-43a4-92bb-b540af3ee25d -->

Standard deviation alone can mislead when projects are different sizes. A ₦150,000 project naturally swings by more naira than a ₦100,000 one. The **coefficient of variation** compares risk when the expected values differ: it is the spread per unit of expected return.

$$CV = \frac{\sigma}{\mu}$$

**Example:** project A has μ = 100,000 and σ = 30,000, so CV = 0.30. Project B has μ = 150,000 and σ = 40,000, so CV = 0.267. B has the bigger σ but is **less risky per unit of return**.

## Attitude to risk
<!-- bite: 6f23ac7e-21a6-4d25-a089-9f813d0c858c -->

Two people can look at the same numbers and choose differently, because they feel differently about risk.

- **Risk lover:** prefers the gamble, accepts a payoff above the expected value.
- **Risk averse:** prefers the certain outcome, the behaviour when the payoff is below the expected value.
- **Risk neutral:** payoff equals expected value, so only the expected value matters.

Most firms with a lot to lose are risk averse, which is why they accept a lower expected return for less spread. The next lesson puts all of this to work on a real choice: which pricing strategy should a firm pick?

## Check your understanding
<!-- bite: fe969efa-8762-48a7-996e-c122776ea4bf -->

Try each one before you open the answer.

1. <!-- q: exact id="2e6e28df" answer="95" -->
   A project has a 30% chance of a profit of ₦200 million and a 70% chance of a profit of ₦50 million. What is its expected profit, in millions of naira?

   <details><summary>Answer</summary>

   E = 0.3 × 200 + 0.7 × 50 = 60 + 35 = ₦95 million.

   </details>

2. <!-- q: exact id="8b578307" answer="100" -->
   A bet pays ₦10 or ₦30 with equal probability (mean ₦20). What is its variance?

   <details><summary>Answer</summary>

   σ² = 0.5 × (10 − 20)² + 0.5 × (30 − 20)² = 0.5 × 100 + 0.5 × 100 = 100. The standard deviation is 10.

   </details>

3. <!-- q: mcq id="a19dc9b5" -->
   Project X has μ = ₦200,000 and σ = ₦50,000. Project Y has μ = ₦120,000 and σ = ₦36,000. Which is less risky per unit of return?

   - [x] X, with CV = 0.25
   - [ ] Y, with CV = 0.30
   - [ ] Y, because its standard deviation is smaller
   - [ ] They are equally risky

   <details><summary>Answer</summary>

   X. CV(X) = 50,000/200,000 = 0.25 and CV(Y) = 36,000/120,000 = 0.30. Y has the smaller σ, but X has less risk per naira of expected return.

   </details>

4. <!-- q: mcq id="997521d5" -->
   Two investments both have an expected return of 12%. One has a standard deviation of 2% and the other 9%. What does this tell you?

   - [ ] They are equally good, because the expected values are the same
   - [x] The second is riskier, because its outcomes are spread further from the mean
   - [ ] The second is better, because it can return more

   <details><summary>Answer</summary>

   The second is riskier. Same mean, but its outcomes are spread much further from it. A risk-averse investor would choose the first.

   </details>

5. <!-- q: mcq id="c8ef0f14" -->
   Offered a certain ₦45,000 or a 50-50 bet on ₦0 or ₦100,000 (expected value ₦50,000), a manager takes the certain ₦45,000. What is the manager's attitude to risk?

   - [ ] Risk lover
   - [x] Risk averse
   - [ ] Risk neutral

   <details><summary>Answer</summary>

   Risk averse: the manager prefers the certain outcome even though it is below the expected value of the gamble.

   </details>

6. <!-- q: exact id="06b6aa0d" answer="173.205" sigfigs="3" tolerance="0.5" -->
   A machine's yearly saving is ₦200 with probability 0.25 and ₦600 with probability 0.75. Its expected saving is ₦500. What is the standard deviation of the saving, in naira?

   <details><summary>Answer</summary>

   σ² = 0.25 × (200 − 500)² + 0.75 × (600 − 500)² = 22,500 + 7,500 = 30,000, so σ = √30,000 ≈ ₦173.

   </details>

## Before moving on
<!-- bite: 4d8d6122-3b47-41fa-860e-8be1c0d4e771 -->

You can calculate expected value, variance, standard deviation and the coefficient of variation, and describe the three attitudes to risk. **Next:** [[engineering-economics/24-risk-and-uncertainty-3|Risk and Uncertainty 3]]: making decisions under risk and under complete ignorance.

## Related
<!-- bite: 2c0eb4b5-0442-48bc-924d-5373071bd0a9 -->

- [[engineering-economics/index|Engineering economics map]]
- [[data-analysis/index|Data Analysis]]: mean, variance and standard deviation in general.

## About this lesson
<!-- bite: 0260818f-2460-4ae5-b0fa-e1ef64d1e58b -->

**Level:** Beginner. **Covers:** expected value, variance and standard deviation, the coefficient of variation, and attitudes to risk.

**Where it sits:** lesson 23 of 38, part 2 of 3 on risk and uncertainty.

**Source:** the author's own GEG 501 note, section 9. The step-by-step standard deviation of the recession example was added for this lesson.
