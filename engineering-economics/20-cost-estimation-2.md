---
id: c4219872-a374-4f0c-b2d5-862a3267cba0
---

# Cost Estimation 2: Parametric, Capacity and Detailed Estimates

Parametric and capacity estimates work out a cost from a formula built on past data, and a detailed estimate adds up the cost of every component.

## Before you start
<!-- bite: 0b7f59b8-b63f-4030-ae50-9c2f82c1a994 -->

You should know what cost estimation is and the judgement-based techniques from [[engineering-economics/19-cost-estimation-1|Cost Estimation 1]], and inflation and price indices from [[engineering-economics/09-inflation-1|Inflation 1]].

After this lesson you will be able to:

1. use a parametric cost equation C = aX^b;
2. scale a plant's cost with the capacity factoring (power-sizing) model, and explain economies of scale;
3. build a detailed estimate, and adjust an old cost for inflation with a cost index.

## What the quantitative techniques are
<!-- bite: e1801e84-da85-4850-af9f-975388f8777c -->

Remember the two limits of the judgement methods: they're subjective, and analogy assumes cost rises in proportion to size? The quantitative techniques fix both. They use a statistical relationship found from many past projects, so the estimate is less about one person's feeling.

We take them from quickest to most accurate: parametric, capacity factoring, then detailed. Then one tool every technique needs: adjusting old costs for inflation.

## B1. Parametric estimation
<!-- bite: 45a7c0b1-a2b9-412b-996d-2369f101c4dd -->

Parametric estimation uses a statistical relationship between cost and a key parameter such as size, capacity or power. Cost is a constant times the parameter raised to a power:

$$C = aX^{b}$$

X is the cost-driving parameter. a and b are constants found from historical data.

**Example:** C = 500X^0.6 with X = 16 gives 500 × 16^0.6 = 500 × 5.278 = **2,639**.

- **Advantages:** more objective, good for preliminary design.
- **Limits:** needs reliable historical data and assumes stable cost relationships.

## B2. Capacity factoring (power-sizing model)
<!-- bite: 3a7fa548-f1fa-43c4-89d8-eb6626e9aeb4 -->

Capacity factoring is used when cost scales with capacity. You take the cost of a plant you know, and scale it by the ratio of the capacities raised to a power n:

$$C_2 = C_1\left(\frac{Q_2}{Q_1}\right)^{n}$$

n is the cost-capacity exponent, usually between 0.5 and 0.8.

**Example:** a 100 MW power plant costs ₦120B. The cost of a 200 MW plant with n = 0.6 is 120 × (200/100)^0.6 = 120 × 1.5157 ≈ **₦182B**.

- **Advantages:** widely used, captures economies of scale.
- **Limits:** sensitive to the exponent you choose.

## Economies of scale
<!-- bite: 4114c8c9-fdf8-4f06-bb76-34035466c11f -->

Look at that answer again. Doubling the size does not double the cost: twice the power for about 1.5 times the money. That is the idea of **economies of scale**.

Why? A plant twice as big doesn't need twice the control room, twice the engineers or twice the access road. Many costs grow more slowly than capacity. Because n is less than 1, the formula builds that in. (Analogy estimation in lesson 19 assumes n = 1, which is why it overestimates big projects.)

## C. Detailed (bottom-up) estimation
<!-- bite: 6cf5b3db-00c0-4fa9-bd0c-dc43b02417d4 -->

Detailed estimation is the most accurate technique. Break the project into components, estimate the cost of each, and add them up.

| Item | Cost (₦ million) |
| --- | --- |
| Equipment | 120 |
| Installation | 40 |
| Labour | 30 |
| Utility | 10 |
| **Total** | **200** |

- **Advantages:** high accuracy and good for final budgeting.
- **Limits:** time-consuming and needs a detailed design.

So in practice a project starts with judgement or parametric estimates and moves to a detailed estimate once the design is done.

## Adjusting old costs for inflation (cost index method)
<!-- bite: 89fec76d-5471-4f9c-a046-5df64219347c -->

All these techniques use historical cost data, but prices have changed since then, so you adjust with an index. The new cost is the old cost scaled by how much the index has risen:

$$C_{new} = C_{old} \times \frac{I_{new}}{I_{old}}$$

**Example:** a project cost ₦80M in 2018 when the index was 150. In 2024 the index is 210, so the cost is 80 × 210/150 = **₦112M**.

Common indexes: consumer price index (CPI), construction cost index (CCI) and producer price index (PPI). This connects to inflation in lesson 09.

Every technique so far assumes the cost per unit is fixed. But a factory gets faster at a job the more times it does it, so the 100th unit costs less than the 1st. That's the learning curve, in the next lesson.

## Check your understanding
<!-- bite: efd3cb37-d72f-48c1-ad62-24f05e741126 -->

Try each one before you open the answer.

1. <!-- q: exact id="b67854a9" answer="2442.54" sigfigs="4" tolerance="2" -->
   A firm's past data gives the cost equation C = 300X^0.7, where X is the tank volume in cubic metres. What is the estimated cost of a 20 cubic metre tank?

   <details><summary>Answer</summary>

   C = 300 × 20^0.7 = 300 × 8.1418 ≈ 2,442.5.

   </details>

2. <!-- q: exact id="950e5b95" answer="77.327" sigfigs="3" tolerance="0.1" accept="₦77.3B|77.3B" -->
   A 50 MW solar farm cost ₦40 billion. Using capacity factoring with n = 0.6, estimate the cost of a 150 MW farm, in billions of naira.

   <details><summary>Answer</summary>

   C2 = 40 × (150/50)^0.6 = 40 × 3^0.6 = 40 × 1.9332 ≈ ₦77.3 billion. Three times the capacity for under twice the cost: economies of scale.

   </details>

3. <!-- q: exact id="57a3ce7c" answer="75" accept="₦75M|75M|₦75 million|75 million" -->
   A bridge cost ₦50 million when the construction cost index was 180. The index is now 270. What would the same bridge cost today, in millions of naira?

   <details><summary>Answer</summary>

   C_new = 50 × 270/180 = 50 × 1.5 = ₦75 million.

   </details>

4. <!-- q: mcq id="c8fcd475" -->
   Which estimation technique is the most accurate, but needs a detailed design and takes the most time?

   - [ ] Expert judgement
   - [ ] Parametric estimation
   - [ ] Capacity factoring
   - [x] Detailed (bottom-up) estimation

   <details><summary>Answer</summary>

   Detailed (bottom-up) estimation: break the project into components, cost each one and add them up.

   </details>

5. <!-- q: gap id="642a4ffb" answers="0.5;0.8" -->
   Fill in the gaps. In the capacity factoring model, the cost-capacity exponent n is usually between ___ and ___.

   <details><summary>Answer</summary>

   Between 0.5 and 0.8. Because it is below 1, cost grows more slowly than capacity.

   </details>

6. <!-- q: open id="a4a0a762" -->
   Using the capacity factoring model, explain what economies of scale means.

   <details><summary>Answer</summary>

   In C2 = C1(Q2/Q1)^n, the exponent n is less than 1 (usually 0.5 to 0.8), so cost rises more slowly than capacity. Doubling a 100 MW plant to 200 MW with n = 0.6 multiplies the cost by only 2^0.6 = 1.52, not 2. So the cost per unit of capacity falls as plants get bigger, because many costs (control systems, staff, roads, design) don't grow in proportion to size. That is economies of scale.

   </details>

## Before moving on
<!-- bite: a9b74229-d6af-41f9-ad89-dd38fa53304e -->

You can use a parametric equation, scale a plant's cost by capacity, build a detailed estimate and adjust an old cost with an index. **Next:** [[engineering-economics/21-cost-estimation-3|Cost Estimation 3]]: the learning curve, and why estimates go wrong.

## Related
<!-- bite: 46d1bdd9-18b9-4a0a-809e-ae696a7a34f6 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 63c9403b-8149-466b-8563-2768cefeaa7d -->

**Level:** Beginner. **Covers:** parametric estimation, capacity factoring and economies of scale, detailed (bottom-up) estimation, and the cost index method.

**Where it sits:** lesson 20 of 38, part 2 of 3 on cost estimation.

**Source:** the author's own GEG 501 note, section 8.
