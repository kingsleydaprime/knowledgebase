---
id: a8be91a2-47b0-41f5-94cd-4d132354892d
---

# Cost Concepts 2: Average Cost, Marginal Cost and the Cost Sheet

Average cost, marginal cost and the cost sheet are the three ways engineers put numbers on the types of cost from lesson 02.

## Before you start
<!-- bite: 43406ac8-89b5-421f-a53d-21593ff0bd4b -->

You should know fixed, variable, direct and indirect cost from [[engineering-economics/02-cost-concepts-1|Cost Concepts 1]].

After this lesson you will be able to:

1. calculate average cost and marginal cost, and say why marginal cost depends on variable cost only;
2. build a cost sheet layer by layer, from prime cost to profit;
3. check a cost sheet's arithmetic, including a mistake in the 2019 material.

## What average cost, marginal cost and the cost sheet are
<!-- bite: f00bae81-42f7-4222-907b-49dfb0796405 -->

Remember the cost equation, total cost = fixed cost + variable cost × output? That gives one total. But a manager usually wants two other numbers: what each unit costs on average, and what the *next* unit will cost. Those are average cost and marginal cost.

The cost sheet answers a different question: how does a total cost build up from materials and wages to the full cost of selling the goods? We take the two unit costs first, then the cost sheet.

## Average cost
<!-- bite: 2b6798ef-2f50-4930-aa8a-19715ea5c8af -->

Average cost is the total cost shared equally over every unit made:

$$\text{Average cost} = \frac{\text{total cost}}{\text{output}}$$

It equals average fixed cost plus average variable cost. Example: total cost of 1,000 for 100 units gives an average cost of 10.

Notice that the fixed part gets spread thinner as output grows. Rent of 500 shared over 100 units is 5 a unit; shared over 500 units it's 1 a unit. That's why average cost usually falls at first as a factory makes more.

## Marginal cost
<!-- bite: 66c99557-c752-475b-8cf8-1f21b4bc2e7f -->

Marginal cost is the extra cost of making one more unit. You find it by taking the total cost at n units and subtracting the total cost at one unit fewer:

$$MC = TC(n) - TC(n-1)$$

It depends on variable cost only, because producing one more unit adds nothing to fixed cost. The rent is the same whether you make 100 units or 101.

**Example:** making 100 units costs 1,000 and making 101 units costs 1,008. The marginal cost of the 101st unit is 1,008 − 1,000 = 8.

Average and marginal cost come back in lesson 32, where you'll see that marginal cost cuts average cost at its lowest point.

## Elements of cost and the cost sheet
<!-- bite: 4fdeed72-9d1b-4a7d-b1ea-af57f055f8d5 -->

The total cost is built up in layers. Each layer adds to the one before.

| Layer | Formula |
| --- | --- |
| Prime cost | Direct material + direct labour (+ direct expenses) |
| Works (factory) cost | Prime cost + works (factory) overhead |
| Cost of production | Works cost + administrative overhead |
| Total cost of sales | Cost of production + selling and distribution overhead |
| Profit or loss | Sales − total cost |

The full list of costs laid out like this, step by step, is called a **cost sheet**.

Notice the order: the direct costs come first (prime cost), then the overheads are added one at a time, from the factory floor outwards to the office and then to selling.

## Worked example: a cost sheet
<!-- bite: a421a1c8-eec7-47bb-91f2-eb8a0dbab1c0 -->

**Textbook example:** direct material 7,000; direct labour 2,800; factory expenses 2,600; administrative expenses 1,000; selling expenses 900; sales 20,000.

- Prime cost = 7,000 + 2,800 = 9,800
- Works cost = 9,800 + 2,600 = 12,400
- Cost of production = 12,400 + 1,000 = 13,400
- Total cost = 13,400 + 900 = 14,300
- Profit = 20,000 − 14,300 = 5,700

> **Correction:** the 2019 material writes the second line as "Rs. 9,000 + 2,600 = 12,400". Prime cost is 9,800, so it should read 9,800 + 2,600 = 12,400. The final answers are right.

## Common pitfalls
<!-- bite: 1c2f37b7-4f76-4d66-b850-196827b0afcd -->

1. **Putting fixed cost into marginal cost.** One more unit adds no rent, so marginal cost is variable cost only.
2. **Skipping a layer in the cost sheet.** Each layer adds one overhead to the layer before. Write every line, so a slip is easy to find.
3. **Taking profit from the works cost.** Profit is sales minus the *total* cost of sales, after administration and selling are added.

That's cost covered. But a project's costs and benefits don't all happen at once: you pay for the machine today and get savings for years. Part 2 starts with why that timing matters.

## Check your understanding
<!-- bite: 5e88c741-4354-4e4f-b0dc-c7846768137e -->

Try each one before you open the answer.

1. <!-- q: exact id="8dfcb9a5" answer="15" -->
   A bakery's total cost for one day is ₦4,500 and it bakes 300 loaves. What is the average cost per loaf, in naira?

   <details><summary>Answer</summary>

   4,500 ÷ 300 = ₦15 a loaf.

   </details>

2. <!-- q: exact id="c6199c0d" answer="30" -->
   A workshop's total cost of making 50 tables is ₦2,400, and of making 51 tables is ₦2,430. What is the marginal cost of the 51st table, in naira?

   <details><summary>Answer</summary>

   MC = TC(51) − TC(50) = 2,430 − 2,400 = ₦30.

   </details>

3. <!-- q: mcq id="7f42ac40" -->
   Why does marginal cost depend on variable cost only?

   - [ ] Because fixed cost is a sunk cost
   - [x] Because producing one more unit adds nothing to fixed cost
   - [ ] Because variable cost is always larger than fixed cost
   - [ ] Because marginal cost ignores overheads by definition

   <details><summary>Answer</summary>

   Producing one more unit adds nothing to fixed cost. The rent and insurance are the same at 100 units or 101.

   </details>

4. <!-- q: gap id="f4d3543d" answers="17000;20500;24000;6000" -->
   A firm has these figures: direct material 12,000; direct labour 5,000; factory overhead 3,500; administrative overhead 2,000; selling and distribution overhead 1,500; sales 30,000. Fill in the gaps. Prime cost = ___, works cost = ___, total cost of sales = ___, profit = ___.

   <details><summary>Answer</summary>

   - Prime cost = 12,000 + 5,000 = 17,000
   - Works cost = 17,000 + 3,500 = 20,500
   - Cost of production = 20,500 + 2,000 = 22,500
   - Total cost of sales = 22,500 + 1,500 = 24,000
   - Profit = 30,000 − 24,000 = 6,000

   </details>

5. <!-- q: mcq id="010fb6de" -->
   In a cost sheet, which layer is prime cost plus works (factory) overhead?

   - [ ] Cost of production
   - [x] Works (factory) cost
   - [ ] Total cost of sales
   - [ ] Direct cost

   <details><summary>Answer</summary>

   Works (factory) cost. Adding administrative overhead to it gives the cost of production, and adding selling and distribution overhead gives the total cost of sales.

   </details>

## Before moving on
<!-- bite: f5222e2e-133d-4d9c-bc7d-34781293a0f5 -->

You can work out average and marginal cost, and build and check a cost sheet. **Next:** [[engineering-economics/04-time-value-of-money-1|Time Value of Money 1]]: why a naira today is worth more than a naira next year.

## Related
<!-- bite: 88375cb2-986e-4b5a-adb3-702945d9e2a1 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 499b9aa4-1953-4f40-b77d-6860be6c7f23 -->

**Level:** Beginner. **Covers:** average cost, marginal cost, the layers of the cost sheet and the textbook's cost sheet example, with a correction to the 2019 material.

**Where it sits:** lesson 03 of 38, part 2 of 2 on cost concepts.

**Source:** the author's own GEG 501 note, section 2. The marginal cost example (100 and 101 units) was added for this lesson.
