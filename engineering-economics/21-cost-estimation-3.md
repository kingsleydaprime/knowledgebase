---
id: bfac501b-cf97-4c86-87dd-a576a0d0324b
---

# Cost Estimation 3: The Learning Curve, Errors and Best Practices

The learning curve, also called the experience curve, describes how the cost per unit falls as production experience grows.

## Before you start
<!-- bite: d2a8cada-8024-4ab5-8417-b879213982b6 -->

You should know parametric estimation, C = aX^b, from [[engineering-economics/20-cost-estimation-2|Cost Estimation 2]].

After this lesson you will be able to:

1. explain the learning curve and what an 80% learning curve means, and work out the cost of a later unit;
2. give the managerial implications of the learning curve;
3. list the causes of error in cost estimation, including scope creep, and the best practices that reduce them.

## What the learning curve is
<!-- bite: bdd26dd8-c25a-4d6b-a66b-3a93f8535688 -->

Think of the first time you tied a tie, or cooked egusi soup on your own. Slow, many mistakes. By the tenth time you're fast. Factories are the same: workers learn the job, find shortcuts and make fewer errors, so each unit takes less time than the one before.

Cost per unit falls as production experience grows. It has the same shape as the parametric equation from lesson 20, but now the power is negative, so cost falls as output rises:

$$Y = aX^{b} \quad (b < 0)$$

Y is the cost per unit, X is the cumulative output, and a is the cost of the first unit.

## The 80% learning curve
<!-- bite: f4fc9423-233d-46cd-a000-40907ec12c32 -->

If labour hours fall 20% each time output doubles, an **80% learning curve** applies. Each time cumulative output doubles, the cost of the next unit is 80% of what it was.

**Example:** the first unit takes 100 hours, on an 80% curve.

| Unit | Hours |
| --- | --- |
| 1 | 100 |
| 2 | 80 |
| 4 | 64 |
| 8 | 51.2 |

The exponent is b = log(0.8)/log(2) = −0.322, so you can find any unit, not just doubles: unit 10 takes 100 × 10^−0.322 ≈ 47.7 hours. This worked table was added for this lesson.

It is used in manufacturing, defence projects and aircraft production.

## Learning curve: managerial implications (general knowledge)
<!-- bite: 0946b832-5830-4c0d-96b1-d821ef834ec6 -->

A question on the learning curve usually also asks what it means for managers:

- **Cost estimating and budgeting:** do not use the cost of the first unit for the whole job. Estimate later units using the curve.
- **Pricing and bidding:** a firm that is further down the curve can bid lower and still earn a profit. Some firms price low early to win volume and move down the curve faster.
- **Labour planning and scheduling:** hours needed per unit fall, so fewer workers or less time are needed as production continues.
- **Competitive strategy:** a larger market share means more cumulative output, so lower unit cost, which is a barrier to new competitors.

## More implications, and the limits
<!-- bite: 5a8d1dc2-d1fb-4428-a4d8-b3c3acdaf06a -->

- **Make or buy and capacity:** the saving from repetition helps decide whether to produce in-house.
- **Training and motivation:** training, good supervision and stable crews speed up learning.
- **Limits:** the curve flattens after many units; it assumes the same product, stable workers and no major change in process; and the learning rate (80%, 90%) is an estimate.

## Causes of error in cost estimation
<!-- bite: 1b3fd44b-27c3-41eb-8bc7-0e7914aacde7 -->

Even with good techniques, estimates go wrong. The five usual causes:

1. Ignoring inflation.
2. Over-optimism bias.
3. Poor data quality.
4. **Scope creep:** the project quietly grows beyond what was planned and costed (your lecturer asked you to learn more about this).
5. Technological uncertainty.

Scope creep is worth a picture. A client asks for a 3-bedroom bungalow. Halfway through: "add a boys' quarters". Then "make the kitchen bigger", then "a small borehole sef". Each request is small, but none was in the estimate, and together they blow the budget.

## Best practices
<!-- bite: 7e99b592-2d20-4ad9-ac8b-0baec9a606b4 -->

Use several methods, update estimates as the project evolves, document your adjustments clearly, include contingency allowances, and carry out sensitivity analysis.

A **contingency allowance** is an extra amount added to the estimate to cover things that will go wrong but can't be named yet. Sensitivity analysis gets its own lesson (25).

**Main takeaways:** cost estimation is the foundation of engineering economics. Detailed estimation gives accuracy while parametric methods give speed. Adjusting for inflation and scale is essential. Reliable estimates reduce financial project risk.

That last word, risk, is where part 6 starts. An estimate is a guess about the future, and the future is not certain.

## Check your understanding
<!-- bite: 4e7a8558-6b2a-4fa1-a575-03509f56c2e0 -->

Try each one before you open the answer.

1. <!-- q: exact id="d1031a05" answer="162" -->
   The first unit of a new pump takes 200 labour hours, and production follows a 90% learning curve. How many hours does the 4th unit take?

   <details><summary>Answer</summary>

   Output doubles twice from unit 1 to unit 4, so 200 × 0.9 × 0.9 = 162 hours.

   </details>

2. <!-- q: exact id="0864f294" answer="145.8" sigfigs="4" -->
   The first unit of a new pump takes 200 labour hours, and production follows a 90% learning curve. How many hours does the 8th unit take?

   <details><summary>Answer</summary>

   Three doublings (1 → 2 → 4 → 8): 200 × 0.9³ = 200 × 0.729 = 145.8 hours.

   </details>

3. <!-- q: gap id="895d4fdc" answers="20" -->
   Fill in the gap. An 80% learning curve means labour hours fall by ___% each time cumulative output doubles.

   <details><summary>Answer</summary>

   20%. Each doubling, the unit cost is 80% of what it was.

   </details>

4. <!-- q: mcq id="b67854aa" -->
   A client keeps adding small extra features to a building after the budget was agreed, and none of them were costed. Which cause of estimation error is this?

   - [ ] Over-optimism bias
   - [ ] Poor data quality
   - [x] Scope creep
   - [ ] Technological uncertainty

   <details><summary>Answer</summary>

   Scope creep: the project quietly grows beyond what was planned and costed.

   </details>

5. <!-- q: mcq id="950e5b96" -->
   A firm has made 5,000 aircraft parts and is far down its learning curve. A new rival has made 200. What does the learning curve suggest?

   - [x] The experienced firm can bid lower and still make a profit
   - [ ] The new rival has lower unit cost because its workers are fresh
   - [ ] Both firms have the same unit cost, because the product is the same

   <details><summary>Answer</summary>

   The experienced firm is further down the curve, so its unit cost is lower and it can bid lower and still profit. This is why market share is a barrier to new competitors.

   </details>

6. <!-- q: open id="950e5b97" -->
   Write a short note on learning curve theory and its managerial implications. (A 2.5-mark short note in the 2025/2026 exam.)

   <details><summary>Answer</summary>

   The learning curve says cost (or labour hours) per unit falls as cumulative output grows, because workers learn the job: Y = aX^b with b negative. On an 80% curve, the unit cost falls to 80% each time cumulative output doubles. It is used in manufacturing, defence and aircraft production. For managers: estimate later units with the curve, not the first unit's cost; a firm further down the curve can bid lower and still profit; fewer labour hours are needed as production continues; more market share means lower unit cost, a barrier to competitors; it helps make-or-buy decisions; and training and stable crews speed up learning. Its limits: it flattens after many units, assumes no big change in product or process, and the learning rate is only an estimate.

   </details>

## Before moving on
<!-- bite: a6b95867-88e2-4cd1-a10f-14d864999e4f -->

You can work out a learning-curve cost, explain what it means for managers, and list the causes of estimation error and the best practices. **Next:** [[engineering-economics/22-risk-and-uncertainty-1|Risk and Uncertainty 1]]: what risk and uncertainty are, and the five categories of risk.

## Related
<!-- bite: 4b56ea3a-2cdf-4949-9b13-7e2f6d7878a3 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 690176f3-e57a-4ccc-be3b-7aed9f131db7 -->

**Level:** Beginner. **Covers:** the learning curve and the 80% curve, a worked table, the managerial implications and limits, the causes of estimation error including scope creep, best practices and contingency.

**Where it sits:** lesson 21 of 38, part 3 of 3 on cost estimation.

**Source:** the author's own GEG 501 note, sections 8 and 14.2. The managerial implications are general knowledge, not from the lecture materials. The worked learning curve table and the scope creep example were added for this lesson.
