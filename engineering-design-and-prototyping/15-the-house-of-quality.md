---
id: d09e4212-f2a8-4357-a800-5459b85f5fd0
---

# The House of Quality

The House of Quality is the chart used to carry out quality function deployment (QFD): it links what customers want to what engineers must measure.

## Before you start
<!-- bite: 113b90e8-c901-4504-b58d-cf8d5390a409 -->

You should know what QFD is and how it was used on the water bottle ([[engineering-design-and-prototyping/14-concept-refinement|lesson 14]]), and how weights work in a decision matrix ([[engineering-design-and-prototyping/13-concept-selection-3|lesson 13]]).

After this lesson you will be able to:

1. name the parts of a House of Quality and say what each one holds;
2. fill in the relationship grid and calculate the technical importance of each requirement;
3. read the roof to spot requirements that conflict.

## What the House of Quality is
<!-- bite: bc8e2378-e3fb-405b-a099-c26560006155 -->

In lesson 14, QFD turned customer needs into design requirements: "leakproof" became "a tight seal between body and cap". But how do you decide which requirement matters *most* when there are many needs and many requirements, all pulling on each other?

The House of Quality answers that. It's one big chart, shaped like a house, with the customer's needs on one side and the engineering requirements on the other. When it's filled in, it ranks the engineering requirements by how much the customer cares about them.

It's called a house because of its shape: rooms in the middle, a triangle roof on top.

## The parts of the house
<!-- bite: 06ae79af-47de-41be-b479-d8805e3835b1 -->

1. **Customer needs (the left wall)**: what customers say they want, in their own words, each with a **weight** for how important it is (for example 1 to 5).
2. **Engineering requirements (the ceiling)**: things engineers can measure, like a force in newtons or a size in millimetres.
3. **The relationship grid (the rooms)**: for each need and requirement, how strongly that requirement affects that need.
4. **The roof**: which engineering requirements help or hurt each other.
5. **Technical importance (the floor)**: a score for each requirement, telling you where to focus.

## Customer needs become engineering requirements
<!-- bite: 150731f7-97c6-4a3e-8644-e6d4530b7c0d -->

The first job is translating. A customer says "easy to clean". An engineer can't measure "easy", so we ask: what measurable thing makes a bottle easy to clean? The size of the opening, in millimetres.

Here's the water bottle:

| Customer need (weight) | Engineering requirement that affects it |
| --- | --- |
| Leakproof (5) | Seal force: how hard the cap presses on the seal |
| Easy to clean (3) | Opening size: the diameter of the mouth |
| Collapses small (4) | Folded height: how short it gets when collapsed |
| Durable (4) | Fold cycles: how many folds before it fails |
| Attractive (1) | Colours: how many colour options |

The weights come from user research. Leakproof gets 5 because a bottle that leaks in a bag is a disaster; attractive gets 1, as QFD found in lesson 14.

## Filling in the rooms
<!-- bite: 0cd074ab-d8e6-4134-8b39-66071e523db7 -->

Now, for every pair of need and requirement, ask: does this requirement affect this need? Score it:

- **9**: strong relationship.
- **3**: medium relationship.
- **1**: weak relationship.
- Blank: no relationship.

Some examples from the bottle:

- Seal force and leakproof: **9**. The seal is what stops leaks.
- Opening size and leakproof: **3**. A bigger opening is harder to seal.
- Fold cycles and collapses small: **3**. A bottle that fails after a few folds stops collapsing.
- Folded height and attractive: **1**. A neat fold looks a little better.

The 9, 3, 1 scale is spread out on purpose, so a strong link counts far more than a weak one.

## The whole house
<!-- bite: 73b6a26a-55b9-4899-b43b-5c27f9b58db2 -->

Here is the finished House of Quality for the bottle:

![A House of Quality for a collapsible water bottle: five customer needs with weights down the left, five engineering requirements across the top, 9, 3 and 1 relationships in the grid, a roof marking two conflicts, and technical importance totals of 60, 42, 37, 53 and 9 along the bottom.](images/ed-house-of-quality.svg)

Look at the bottom row. Those are the technical importance scores, worked out in the next section.

## Calculating technical importance
<!-- bite: fc6b68b7-e6f8-4ebf-be62-3a5d434dc7ec -->

The technical importance of a requirement is found by multiplying each customer need's weight by its relationship score in that column, then adding down the column. It's the decision matrix idea again: weight × score, added up.

For **seal force**: leakproof 5 × 9, easy to clean 3 × 1, durable 4 × 3.

5 × 9 + 3 × 1 + 4 × 3 = 45 + 3 + 12 = **60**

For **fold cycles**: leakproof 5 × 1, collapses small 4 × 3, durable 4 × 9.

5 × 1 + 4 × 3 + 4 × 9 = 5 + 12 + 36 = **53**

The rest: opening size 42, folded height 37, colours 9.

## Reading the result
<!-- bite: e45ff69b-45d4-4461-9340-52c21ad4d199 -->

Ranked: seal force (60), fold cycles (53), opening size (42), folded height (37), colours (9).

So the engineering effort goes first into the seal, then into making the fold survive many cycles. That's the same conclusion lesson 14 reached in words (leakproof is high priority, customers care about durability), but now it's backed by numbers you can show.

Colours scored 9: worth doing, but not where the money goes first.

## The roof: requirements that fight each other
<!-- bite: b09028d5-f623-4fea-a65f-5fa419f6c8cb -->

The roof compares every engineering requirement with every other one. Where two meet in the roof, you mark whether improving one helps or hurts the other. The bottle has two conflicts (the − marks):

1. **Seal force and opening size.** A bigger opening is easier to clean but harder to seal tightly.
2. **Folded height and fold cycles.** Folding flatter bends the material more sharply, so it wears out sooner.

The roof doesn't solve these. It warns you, so you make the trade-off on purpose. And remember TRIZ from lesson 8: a contradiction like "bigger opening but still tight seal" is exactly what the contradiction matrix is for.

With the House of Quality done, we know what to build and what matters most. Next, the product is broken into its subsystems and the interfaces between them: its architecture.

## Common pitfalls
<!-- bite: 49c48336-939a-4e15-88b2-24c4a8068140 -->

1. **Writing customer needs as engineering terms.** "Leakproof" goes on the left in the customer's words. "Seal force in newtons" goes on top.
2. **Forgetting the weights.** Technical importance is weight × relationship, added down the column, not just the relationships added.
3. **Using 1, 2, 3 instead of 1, 3, 9.** The spread-out scale is what makes strong links stand out.
4. **Ignoring the roof.** Two top-ranked requirements that conflict will cause trouble later if nobody decides the trade-off now.

## Check your understanding
<!-- bite: 6e108665-8e0a-4bb7-890a-be0083d003cf -->

Try each one before you open the answer.

1. <!-- q: exact id="4f2a9c61" answer="57" -->
   In a House of Quality for a school bag, the engineering requirement "strap padding thickness" has these relationships: Comfortable (weight 5) = 9, Light (weight 4) = 3, Cheap (weight 3) = 0. What is its technical importance?

   <details><summary>Answer</summary>

   5 × 9 + 4 × 3 + 3 × 0 = 45 + 12 + 0 = 57.

   </details>

2. <!-- q: mcq id="b8e1d047" -->
   Which part of the House of Quality shows that two engineering requirements conflict?

   - [ ] The left wall
   - [ ] The relationship grid
   - [x] The roof
   - [ ] The technical importance row

   <details><summary>Answer</summary>

   The roof compares every engineering requirement with every other, and marks where they help or hurt each other.

   </details>

3. <!-- q: mcq id="2c7f0e93" -->
   A customer says a kettle should "boil fast". Which of these belongs on the ceiling of the House of Quality as the engineering requirement?

   - [ ] Boils fast
   - [x] Heating element power in watts
   - [ ] Customers are happy

   <details><summary>Answer</summary>

   Heating element power in watts: it is measurable. "Boils fast" is the customer need and goes on the left wall.

   </details>

4. <!-- q: gap id="9d3b6a20" answers="9;3;1" -->
   Fill in the gaps. In the relationship grid, a strong relationship scores ___, a medium one scores ___ and a weak one scores ___.

   <details><summary>Answer</summary>

   9, 3 and 1.

   </details>

5. <!-- q: mcq id="e05c4b18" -->
   A House of Quality for a torch gives these technical importance scores: battery capacity 72, lens size 30, case thickness 45, switch type 18. Where should the team focus first?

   - [x] Battery capacity
   - [ ] Case thickness
   - [ ] Switch type

   <details><summary>Answer</summary>

   Battery capacity, the highest score. It is the requirement the customers' most important needs depend on most.

   </details>

6. <!-- q: open id="71a8f3d5" -->
   Give one pair of engineering requirements for a mobile phone that would get a conflict mark in the roof, and explain why.

   <details><summary>Answer</summary>

   For example, battery capacity and phone thickness: a bigger battery needs more space, so a thinner phone means a smaller battery. Another: screen brightness and battery life. Any pair works if improving one makes the other worse.

   </details>

## Before moving on
<!-- bite: ea96b14b-0cad-475f-8f34-2fea552dbd56 -->

You can name the parts of a House of Quality, fill in the relationships, calculate technical importance, and read conflicts from the roof. **Next:** [[engineering-design-and-prototyping/16-system-architecture-and-mbse|16 — System Architecture and MBSE]]: breaking a product into subsystems and interfaces, and keeping it all in one model.

## Related
<!-- bite: fb1a287a-156c-4903-92d0-603c096a8efd -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]

## About this lesson
<!-- bite: f3aad3eb-fde8-457b-be08-fa55d024891d -->

**Level:** Intermediate. **Covers:** the parts of the House of Quality, translating customer needs into engineering requirements, the 9, 3, 1 relationship scale, technical importance, and the roof.

**Where it sits:** lesson 15 of 36, in part 4 (choosing and shaping an idea).

**Source:** written from general engineering knowledge; it is not in the SSG 532 lecture notes. The bottle's numbers are an example built on lesson 14, and are checked by `scripts/diagrams/engineering_design.py`.
