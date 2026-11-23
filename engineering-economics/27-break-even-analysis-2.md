---
id: ead69028-6ece-4a7c-904a-9a3aecfb4e20
---

# Break-Even Analysis 2: Worked Examples and Operating Leverage

Operating leverage is how much a firm's profit swings when its sales change, and this lesson works it out alongside the lectures' break-even problems.

## Before you start
<!-- bite: ebfa755c-5f97-4420-aecc-d1f30b2771cd -->

You should know contribution, the break-even point and target profit from [[engineering-economics/26-break-even-analysis-1|Break-Even Analysis 1]].

After this lesson you will be able to:

1. work a single-product break-even problem from raw cost data, including splitting a mixed cost;
2. find the break-even quantity between two options with different fixed and variable costs;
3. calculate the degree of operating leverage and explain what it says about risk.

## What this lesson does
<!-- bite: 30374ba1-0041-4b8b-9a15-baa46db88ed5 -->

Lesson 26 gave the formulas. Exam questions rarely hand you "contribution = 40" on a plate, though. They give you a list of costs and you have to sort them into fixed and variable first. That sorting is where marks are lost, so we take the lecture's exercise slowly.

## Single product: sorting the costs
<!-- bite: 33f33082-a754-487a-97ac-dcfa507a398c -->

**Lecture 9, exercise 1:** budget 10,000 units. Materials 12, direct labour 35, variable production overhead 5 hours × 8 = 40, distribution 2 a unit. Fixed factory cost 120,000, selling and distribution cost 160,000 in total, administration 80,000. Selling price 129.

**Variable cost per unit:**
- materials 12 + labour 35 + variable overhead 40 + distribution 2 = **89**.
- So unit contribution = 129 − 89 = **40**.

**Fixed cost:** the 160,000 selling and distribution figure is a mixed cost. It includes the 2-a-unit distribution, which is variable, so take that out: 160,000 − 2 × 10,000 = 140,000 is fixed.
- Fixed costs = 120,000 + 140,000 + 80,000 = **340,000**.

## Single product: the answers
<!-- bite: 5a2c5539-1dc8-4238-8cdd-ea6696d3ae03 -->

- (a) Break-even = 340,000 ÷ 40 = **8,500 units**.
- (b) For a profit of 40,000: (340,000 + 40,000) ÷ 40 = 9,500 units, so sales of 9,500 × 129 = **1,225,500**.

And the margin of safety at the 10,000-unit budget: 10,000 − 8,500 = 1,500 units, or 15%. That's the shaded gap on the break-even chart in lesson 26.

## Break-even between two options
<!-- bite: 8afbdb3f-1329-4a1e-91a6-afb3a57f968c -->

Break-even also compares two ways of doing a job: one with a high fixed cost and low variable cost (a machine), one with the opposite (hand work).

**Example (FE review):** hand tools cost $1,000 plus $1.50 per unit. An automated process costs $15,000 plus $0.50 per unit.

1. Set the total costs equal: 1,000 + 1.5x = 15,000 + 0.5x.
2. So x = 14,000 units.
3. At 5,000 units a year that is 2.8 years.

Beyond that quantity the automated process is cheaper. (This ignores interest. The lease-or-buy example in lesson 12 includes it.)

## Operating leverage
<!-- bite: cc07abc8-b00c-47b2-b2c6-87d783642ee8 -->

**Cost structure** is the proportion of fixed to variable cost in a business. The **degree of operating leverage (DOL)** measures what that structure does to profit:

$$DOL = \frac{\text{contribution margin}}{\text{net operating income}}$$

It tells you how much profit changes for a 1% change in sales. A 10% rise in sales with a DOL of 4 raises profit by about 40%.

DOL is not constant (it is infinite at break-even because profit is zero), so recompute it at each sales level.

## Operating leverage: the lecture exercise
<!-- bite: f5a00850-eade-4e32-8c27-fef018779b0c -->

At the 10,000-unit budget in exercise 1:

- Total contribution = 10,000 × 40 = 400,000.
- Profit = 400,000 − 340,000 = 60,000.
- DOL = 400,000 ÷ 60,000 = **6.67**.

So a 10% rise in sales (to 11,000 units) would raise profit by about 67%, to 100,000. And a 10% fall would cut profit by 67%, to 20,000. (This DOL working was added for this lesson.)

A firm with a high share of fixed cost has high operating leverage: more profit when sales rise, and more risk when they fall. Close to break-even, DOL is huge, so small changes in sales swing profit wildly.

So far there's been one product. Most firms sell several, and that's the last break-even lesson.

## Check your understanding
<!-- bite: 9744be1d-9936-4d8d-9cf9-23c433a59c8a -->

Try each one before you open the answer.

1. <!-- q: exact id="c6199c10" answer="12000" accept="12,000" -->
   Process A costs ₦20,000 to set up plus ₦4 per unit. Process B costs ₦50,000 to set up plus ₦1.50 per unit. At what quantity do they cost the same?

   <details><summary>Answer</summary>

   20,000 + 4x = 50,000 + 1.5x, so 2.5x = 30,000 and x = 12,000 units. Above that, process B is cheaper.

   </details>

2. <!-- q: exact id="7f42ac43" answer="4" -->
   A firm's total contribution margin is ₦200,000 and its net operating income is ₦50,000. What is its degree of operating leverage?

   <details><summary>Answer</summary>

   DOL = 200,000 ÷ 50,000 = 4. A 1% change in sales changes profit by about 4%.

   </details>

3. <!-- q: exact id="f4d35440" answer="20" accept="20%" -->
   A firm's degree of operating leverage is 4. Sales rise by 5%. By about what percentage does profit rise?

   <details><summary>Answer</summary>

   5% × 4 = about 20%.

   </details>

4. <!-- q: gap id="010fb6e1" answers="60;100000|100,000" -->
   A product sells for ₦150. Its variable costs per unit are materials ₦40, labour ₦30, variable overhead ₦15 and delivery ₦5. Fixed costs are ₦6,000,000. Fill in the gaps. The contribution per unit is ₦___ and the break-even point is ___ units.

   <details><summary>Answer</summary>

   Variable cost = 40 + 30 + 15 + 5 = ₦90, so contribution = 150 − 90 = ₦60. BEP = 6,000,000 ÷ 60 = 100,000 units.

   </details>

5. <!-- q: exact id="a2ac4afa" answer="300000" accept="300,000|₦300,000" -->
   A firm's selling and distribution cost is ₦500,000 in total at its budget of 50,000 units. That total includes delivery at ₦4 per unit. What is the fixed part of the selling and distribution cost, in naira?

   <details><summary>Answer</summary>

   Variable part = 4 × 50,000 = ₦200,000. Fixed part = 500,000 − 200,000 = ₦300,000.

   </details>

6. <!-- q: mcq id="6e38e15d" -->
   Firm H has high fixed costs and low variable costs. Firm L has low fixed costs and high variable costs. Both have the same profit today. Sales fall 10%. Which statement is true?

   - [x] Firm H's profit falls by a bigger percentage, because it has higher operating leverage
   - [ ] Firm L's profit falls more, because its variable costs are higher
   - [ ] Both profits fall by 10%

   <details><summary>Answer</summary>

   Firm H. A high share of fixed cost means high operating leverage: more profit when sales rise, and a bigger fall when they drop.

   </details>

## Before moving on
<!-- bite: 5aab27a7-1c7f-488e-924e-baf28af1a893 -->

You can sort raw costs into fixed and variable, find break-even and target-profit sales, find the break-even between two processes, and use the DOL. **Next:** [[engineering-economics/28-break-even-analysis-3|Break-Even Analysis 3]]: several products.

## Related
<!-- bite: b1e68999-47fd-4f4c-9055-ce935ace972a -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: e2ef57af-c7e7-44bb-aed3-e4ffc36bdc9c -->

**Level:** Beginner. **Covers:** lecture 9 exercise 1 in full (including the mixed selling cost), break-even between hand tools and automation, cost structure and operating leverage.

**Where it sits:** lesson 27 of 38, part 2 of 3 on break-even analysis.

**Source:** the author's own GEG 501 note, section 10 (lecture 9 and the FE review slides). The margin of safety and DOL for exercise 1 were added for this lesson.
