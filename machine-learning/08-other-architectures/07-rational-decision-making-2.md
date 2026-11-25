---
id: 424dc7e1-3f2f-4b52-bd05-31b45326bb11
---

# Rational Decision Making 2: The Six-Step Model

The rational decision making model is a six-step recipe for choosing well when you care about several things at once.

## Before you start
<!-- bite: eb322eac-6dbb-40ad-a29b-453a7c618ded -->

You should have read [[machine-learning/08-other-architectures/06-rational-decision-making-1|Rational Decision Making 1]]: net benefit, marginal analysis and the five lessons. You should be able to multiply decimals.

After this lesson you will be able to:

- list the six steps of the rational decision making model in order;
- weight criteria using absolute and relative comparison;
- rank alternatives, multiply by the weights and pick the best one;
- say what the model can and can't tell you.

## What the rational decision making model is
<!-- bite: 8768a2d9-f51c-4810-bd15-f11712581e05 -->

Remember the car from part 1? Each car had one number for its benefit, so choosing was easy. Real decisions are messier. When a family runs out of space at home, they care about the cost, how long the fix takes, and whether it will still work in five years. No single number covers all three.

The **rational decision making model** is a linear process, a fixed order of steps, that helps you make a more rational decision in a case like this. It has six steps:

1. Define the problem.
2. Identify the decision criteria.
3. Allocate weights to the criteria.
4. Develop the alternatives.
5. Evaluate the alternatives.
6. Select the best alternative.

We'll follow one problem through all six: **a family that has run out of space at home.**

## Step 1: define the problem
<!-- bite: e032d1e7-9313-4e3d-93ed-819076fcb3f4 -->

The problem is **space**: the family doesn't have enough room. Two rules for this step:

1. **Address the cause, not a symptom.** "The hallway is always cluttered" is a symptom. The cause is not enough space for the things and people in the house.
2. **Don't define the problem and the solution together.** "We need a bigger house" is not a problem statement, it is a solution sneaking in early. If you write it as the problem, you've already thrown away every other fix.

## Step 2: identify the decision criteria
<!-- bite: 9ba3412f-782d-4702-8b58-fd892b27dc49 -->

The criteria are the standards that will guide the decision, the things the family cares about. Here there are three:

1. **Cost (C)**: how much the fix costs.
2. **Time (T)**: how long the fix takes.
3. **Long-term solution (LS)**: whether the fix will still work years from now.

But the family doesn't care about all three equally. That's the next step.

## Step 3: allocate weights, absolute comparison
<!-- bite: 4d7d1e36-b036-46d6-b67f-c8fe544c8714 -->

A weight says how much a criterion matters. There are two methods for choosing weights. The first is **absolute comparison**: you rate each criterion on its own scale, from 0 (doesn't matter) to 10 (matters most), without looking at the others.

| Criterion | Scale |
| --- | --- |
| Cost (C) | 0 1 2 3 4 5 6 7 8 9 10 |
| Time (T) | 0 1 2 3 4 5 6 7 8 9 10 |
| Long-term solution (LS) | 0 1 2 3 4 5 6 7 8 9 10 |

It is quick, but it has a weakness: it is easy to rate everything 8 or 9, and then the weights don't separate anything.

## Step 3: allocate weights, relative comparison
<!-- bite: d89e33c2-aa1c-4829-8efc-7219b59c7a65 -->

The second method, **relative comparison**, fixes that. You compare each criterion against each other one, in pairs. In this table, each cell compares the row's criterion with the column's: **+1 means the column criterion matters more**, −1 means it matters less. Add up each column.

| | C | T | LS |
| --- | --- | --- | --- |
| **C** | | +1 | +1 |
| **T** | −1 | | +1 |
| **LS** | −1 | −1 | |
| **Total** | **−2** | **0** | **+2** |

Long-term solution scores highest (+2), then time (0), then cost (−2). The family turned this order into weights that add up to 1: **LS = 0.6, T = 0.3, C = 0.1**. The exact numbers are the family's choice; the comparison only fixes their order.

## Step 4: develop the alternatives
<!-- bite: 5c4ebfd7-02bc-4cd6-9cd0-ad314db1eaf8 -->

Now list every possible fix. The rule here: **generate as many alternatives as possible, but don't evaluate them yet.** Judging too early kills ideas before they're heard.

1. **Bigger home (BH)**: move to a bigger house.
2. **Better storage (S)**: use a better storage system in the current house.
3. **Increase size (IS)**: extend the existing house.
4. **Reduce family size (R)**: probably wouldn't be the choice, but it goes on the list.

Yes, "reduce family size" is on the list. At this step, nothing gets thrown out.

## Step 5: evaluate the alternatives
<!-- bite: ab9437ff-14a2-418e-afdb-654f0b45138a -->

Now rank each alternative against each criterion, where **1 is the best and 4 is the worst**:

| Alternative | LS (0.6) | T (0.3) | C (0.1) |
| --- | --- | --- | --- |
| BH | 1 | 4 | 4 |
| S | 4 | 1 | 1 |
| IS | 2 | 3 | 2 |
| R | 3 | 2 | 3 |

Read the BH row: a bigger home is the best long-term solution (1), but it takes the longest (4) and costs the most (4). Better storage is the opposite: fastest and cheapest (1 and 1), but the worst long-term (4). Every option wins somewhere and loses somewhere. That's exactly why we need the weights.

## Step 6: select the best alternative
<!-- bite: 516c8e90-75a7-4d06-a76d-16479605154a -->

Multiply each rank by its criterion's weight, then add across the row. Because rank 1 is best, **the lowest total wins**.

| Alternative | LS (0.6) | T (0.3) | C (0.1) | Total |
| --- | --- | --- | --- | --- |
| BH | 1 × 0.6 = 0.6 | 4 × 0.3 = 1.2 | 4 × 0.1 = 0.4 | **2.2** |
| S | 4 × 0.6 = 2.4 | 1 × 0.3 = 0.3 | 1 × 0.1 = 0.1 | 2.8 |
| IS | 2 × 0.6 = 1.2 | 3 × 0.3 = 0.9 | 2 × 0.1 = 0.2 | 2.3 |
| R | 3 × 0.6 = 1.8 | 2 × 0.3 = 0.6 | 3 × 0.1 = 0.3 | 2.7 |

**A bigger home (2.2) is the preferred option.** It loses on time and cost, but it wins on the long-term solution, and the family said that matters most (0.6).

## What the numbers can't see
<!-- bite: cfdb767f-d449-4be2-a7b9-32f6aa9a6e13 -->

Look at R, reducing family size. It scores 2.7, which is *not* the worst of the four: better storage (2.8) is worse. On these numbers, sending someone away beats buying shelves!

That isn't the model being wrong. It's the model doing exactly what it was told. Nobody added a criterion like "acceptable to the family", so the model can't see why R is unthinkable. **The model is only as good as its criteria and weights.** If a result looks crazy, check step 2 and step 3 before you trust step 6.

Also, watch the direction of the scale. Here rank 1 is best, so the lowest total wins. If you score with points where higher is better, as in [[engineering-design-and-prototyping/11-concept-selection-1|concept selection]], the highest total wins. Mixing the two up picks the worst option.

## How this connects to AI
<!-- bite: a7329f96-a6a9-451a-9fa8-5646f56fb190 -->

An AI agent faces the same job every time it acts: several options, several things it cares about, pick one. A **rational agent** in AI is one that always chooses the action expected to give the best outcome, the way our family picked the lowest total.

The difference is where the numbers come from. Here, the family wrote down the weights and ranks themselves. In [[machine-learning/08-other-architectures/03-reinforcement-learning|reinforcement learning]], the agent learns those values from reward, by trial and error.

## Check your understanding
<!-- bite: b7d1206c-2b27-445e-93c3-6604cdce072c -->

Try each one before you open the answer.

1. <!-- q: open id="758bfa99" -->
   List the six steps of the rational decision making model in order.

   <details><summary>Answer</summary>

   1. Define the problem. 2. Identify the decision criteria. 3. Allocate weights to the criteria. 4. Develop the alternatives. 5. Evaluate the alternatives. 6. Select the best alternative.

   </details>

2. <!-- q: mcq id="7635cfb1" -->
   A team writes its problem as "We need to hire two more developers." What is wrong with it?

   - [ ] It addresses the cause
   - [x] It puts a solution into the problem statement
   - [ ] It has no criteria

   <details><summary>Answer</summary>

   It defines the problem and a solution together. The real problem might be "releases are late", and hiring is only one possible fix.

   </details>

3. <!-- q: mcq id="49395bd6" -->
   In step 4, a teammate suggests an odd alternative. What does the model say to do?

   - [x] Add it to the list and don't evaluate it yet
   - [ ] Reject it straight away if it seems unlikely
   - [ ] Rank it before listing any others

   <details><summary>Answer</summary>

   Add it. Generate as many alternatives as possible and don't evaluate them until step 5.

   </details>

4. <!-- q: mcq id="744d68c2" -->
   A relative comparison gives these column totals: Price −2, Battery +2, Weight 0. Which criterion matters most?

   - [ ] Price
   - [x] Battery
   - [ ] Weight

   <details><summary>Answer</summary>

   Battery, with the highest total. Then weight, then price.

   </details>

## Check your understanding: worked problems
<!-- bite: 21717a41-9f32-4593-b41b-9416627a4d4f -->

5. <!-- q: exact id="bbecebbf" answer="1.8" tolerance="0.001" -->
   Ranks go from 1 (best) to 3 (worst), and the weights are Battery 0.5, Price 0.3 and Weight 0.2. Laptop A ranks 1 on battery, 3 on price and 2 on weight. What is its weighted total?

   <details><summary>Answer</summary>

   1 × 0.5 + 3 × 0.3 + 2 × 0.2 = 0.5 + 0.9 + 0.4 = 1.8.

   </details>

6. <!-- q: mcq id="92a57297" -->
   Ranks go from 1 (best) to 3 (worst). Which laptop should be chosen?

   | Laptop | Battery (0.5) | Price (0.3) | Weight (0.2) |
   | --- | --- | --- | --- |
   | A | 1 | 3 | 2 |
   | B | 2 | 1 | 3 |
   | C | 3 | 2 | 1 |

   - [x] A
   - [ ] B
   - [ ] C

   <details><summary>Answer</summary>

   A. Totals: A = 0.5 + 0.9 + 0.4 = 1.8, B = 1.0 + 0.3 + 0.6 = 1.9, C = 1.5 + 0.6 + 0.2 = 2.3. Rank 1 is best, so the lowest total, 1.8, wins.

   </details>

7. <!-- q: open id="a4c73dcd" -->
   The model gives a result that everyone agrees is unacceptable. What should you check, and why?

   <details><summary>Answer</summary>

   Check the criteria (step 2) and the weights (step 3). The model only sees what it is told to care about, so an unacceptable winner usually means a criterion is missing or a weight is wrong. Also check the direction of the scale, lowest wins or highest wins.

   </details>

## Before moving on
<!-- bite: f8b6a84c-77ff-4372-9ed8-cd27a0c3e31e -->

You're done when you can take a problem, list criteria, weight them, rank the alternatives and compute the weighted totals to pick a winner.

The short version: define the problem, pick criteria, weight them (absolute or relative comparison), list alternatives without judging, rank them, multiply by the weights and add. With rank 1 as best, the lowest total wins, and the result is only as good as the criteria and weights.

**Next:** this is the last lesson in [[machine-learning/08-other-architectures/index|Other Architectures]]. Carry on to [[machine-learning/09-building-and-fine-tuning/index|Building and Fine-Tuning]].

## About this lesson
<!-- bite: 6e8be802-6b4d-42f9-bd3a-de9972d69639 -->

**Level:** Beginner. Part 2 of 2 on rational decision making. **Covers:** the six-step rational decision making model, absolute and relative comparison of criteria, ranking alternatives and computing weighted totals, the limits of the model, and the link to rational agents in AI. **Source:** SSG 518 (Introduction to Artificial Intelligence), Module 4: Rational Decision Making (RDM), class slides, with the family-space example and its tables. The slides don't say how the column totals became the weights 0.6, 0.3 and 0.1, so this lesson says the comparison fixes the order and the family picks the numbers. The same weighted-matrix idea is taught in [[engineering-design-and-prototyping/index|Engineering Design and Prototyping]].
