---
id: 9fb5cd0d-41d2-4599-ac87-a15c0e0b1ab0
---

# PERT 4: PERT on Costs and Estimates With a Parameter

The three-point method works just as well on money as on time, and when an exam writes the three estimates as algebra, the same formulas give the answer as an expression.

## Before you start
<!-- bite: 531974f6-3a74-46e4-93a6-d32aa61000c8 -->

You should have read [[planning-and-scheduling/18-pert-2|18 — PERT 2]].

After this lesson you will be able to:

1. find the mean and variance of a project's total cost from three cost estimates;
2. find the probability the cost falls between two values;
3. work PERT through when a, m and b are expressions in a parameter t.

## What PERT on costs is
<!-- bite: bd519d8c-aa43-4ffd-8b8a-70480f840169 -->

The fence builder is no surer of the cost than of the time. The wood might be N80,000 if prices hold, most likely N100,000, and N150,000 if there's a shortage. That's three estimates again, so the same formulas apply, with costs in place of times.

**Each activity's mean cost is a weighted average of its three cost estimates, and its variance is the square of a sixth of the range.**

$$\bar{C} = \frac{C_o + 4C_m + C_p}{6}, \qquad V = \left(\frac{C_p - C_o}{6}\right)^2$$

Here $C_o$ is the optimistic (lowest) cost, $C_m$ the most likely and $C_p$ the pessimistic (highest).

## The one difference from time: add everything
<!-- bite: b1f4b6e2-24a8-4909-b743-def57f88a1a4 -->

For time, you added only the critical path, because activities with float don't delay the finish. For cost there is no critical path: **every activity costs money**, whether it is critical or not. So:

1. The total mean cost is the sum of **all** the activities' mean costs.
2. The total variance is the sum of **all** their variances.

## The worked example (2023/24 Question 5b)
<!-- bite: 863dbb10-6ba7-49be-822c-5050932fef44 -->

Costs in naira:

| Activity | $C_o$ | $C_m$ | $C_p$ | Mean cost | Variance |
| --- | --- | --- | --- | --- | --- |
| A | 80 | 100 | 150 | 105.00 | 136.11 |
| B | 40 | 50 | 75 | 52.50 | 34.03 |
| C | 200 | 200 | 200 | 200.00 | 0 |
| D | 50 | 60 | 60 | 58.33 | 2.78 |
| E | 30 | 40 | 60 | 41.67 | 25.00 |
| **Total** | | | | **457.50** | **197.92** |

Check A: mean = (80 + 400 + 150) / 6 = 105; variance = (70/6)² = 136.11. C is certain: all three estimates agree, so its variance is 0.

The standard deviation of the total is √197.92 = **14.07**.

## The probability the cost lands in a range
<!-- bite: b1df0eb0-a2b6-4657-a38f-5de0c7e291b1 -->

The question asks for the chance the total cost is between N450 and N500. Find Z at each end and subtract.

1. Z₁ = (450 − 457.5) / 14.07 = −0.53, so P(cost below 450) = 0.297.
2. Z₂ = (500 − 457.5) / 14.07 = 3.02, so P(cost below 500) = 0.999.
3. P(between) = 0.999 − 0.297 = **0.70**, about 70%.

A range always works like this: the chance below the top, minus the chance below the bottom.

## Estimates written as a parameter
<!-- bite: 368e83fc-e7cd-4115-945c-8a84de724647 -->

The 2024/25 paper (Question 2d) writes the three estimates as expressions in t:

a = t² − t, m = t, b = t² + t

Nothing new: put them into the same formulas and simplify.

1. **Expected time**: $T_e = \dfrac{a + 4m + b}{6} = \dfrac{(t^2 - t) + 4t + (t^2 + t)}{6} = \dfrac{2t^2 + 4t}{6} = \mathbf{\dfrac{t^2 + 2t}{3}}$.
2. **Standard deviation**: σ = (b − a) / 6 = (2t) / 6 = **t / 3**. So the variance is t² / 9, which is the 2020/21 version of the question.

## The parameter version: the probability
<!-- bite: e6f6abae-7485-4641-bde3-1a603f861cf8 -->

The question then asks for the chance of finishing by T = t² + 2t. Find Z:

$Z = \dfrac{T - T_e}{\sigma} = \dfrac{(t^2 + 2t) - (t^2 + 2t)/3}{t/3} = \dfrac{\frac{2}{3}(t^2 + 2t)}{t/3} = \dfrac{2(t^2 + 2t)}{t} = \mathbf{2(t + 2)}$

So the probability is **Φ(2(t + 2))**. For example, with t = 1 that is Φ(6), which is practically 1.

Don't let the algebra frighten you. Every step is the ordinary PERT formula; only the numbers are letters.

## Common pitfalls
<!-- bite: 5a366275-d59d-4410-84e2-bf01793df548 -->

1. **Adding only critical activities for cost.** Every activity costs money, so add them all.
2. **Taking a range as one Z.** Find both ends and subtract.
3. **Losing a sign in the algebra.** Write a + 4m + b out in full before collecting terms.

That completes PERT's calculations. The next lesson steps back and compares PERT with CPM, and names what both of them assume.

## Check your understanding
<!-- bite: 72b6cbac-8c18-46f3-8d6e-4e46080a90b5 -->

Try each one before you open the answer.

1. <!-- q: exact id="2f8a6c03" answer="17" -->
   An activity's cost estimates are optimistic N10,000, most likely N16,000 and pessimistic N28,000. What is its mean cost, in thousands of naira?

   <details><summary>Answer</summary>

   17: (10 + 64 + 28) / 6 = 102 / 6.

   </details>

2. <!-- q: exact id="d5e1b947" answer="9" -->
   An activity's cost estimates are optimistic N10,000, most likely N16,000 and pessimistic N28,000. What is its cost variance, in thousands of naira squared?

   <details><summary>Answer</summary>

   9: ((28 − 10) / 6)² = 3² = 9.

   </details>

3. <!-- q: mcq id="7c30a4f8" -->
   A project has five activities, three on the critical path. To find the variance of the total cost, which do you add?

   - [ ] The three critical activities' variances
   - [x] All five activities' variances
   - [ ] The five standard deviations
   - [ ] Only the largest variance

   <details><summary>Answer</summary>

   All five variances: every activity costs money, critical or not.

   </details>

4. <!-- q: exact id="b91e2d56" answer="0.6826" sigfigs="2" -->
   A project's total cost has mean N500k and standard deviation N20k. What is the probability it costs between N480k and N520k? (Φ(1) = 0.8413.)

   <details><summary>Answer</summary>

   0.6826. Z = −1 and +1, so P = 0.8413 − (1 − 0.8413) = 0.6826.

   </details>

5. <!-- q: gap id="e48c7f1a" answers="7t/3;2t/3" -->
   An activity's estimates are a = t, m = 2t, b = 5t. Its expected time is ___ and its standard deviation is ___.

   <details><summary>Answer</summary>

   $7t/3$ and $2t/3$. $T_e = (t + 8t + 5t)/6 = 14t/6 = 7t/3$; $\sigma = (5t - t)/6 = 4t/6 = 2t/3$.

   </details>

## Before moving on
<!-- bite: d6af593b-7d99-42ca-85ee-5ca70a6ba723 -->

You can run PERT on costs and on estimates written in a parameter. **Next:** [[planning-and-scheduling/21-cpm-and-pert-compared|21 — CPM and PERT Compared]].

## Related
<!-- bite: e9c72155-5d07-4452-9478-d7daf5ee519f -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[engineering-economics/index|Engineering Economics]]: estimating and judging project costs.

## About this lesson
<!-- bite: 23615e21-c9c0-4e60-ac0b-54509873e5be -->

**Level:** Intermediate. **Covers:** cost PERT, the probability of a cost range, and PERT with estimates in a parameter.

**Where it sits:** lesson 20 of 35, in part 5 (PERT). Part 4 of 4 on PERT.

**Source:** the author's own SSG 513 study notes, sections 5 and 9.3 (2023/24 Question 5b, 2024/25 Question 2d). The numbers are checked in `scripts/diagrams/planning_scheduling.py`.
