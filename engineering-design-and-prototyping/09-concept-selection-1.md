---
id: 0613f9d6-8639-4e9c-bcfc-8bd0373b0e67
---

# Concept Selection 1: The Pugh Matrix

Concept selection is the third phase of engineering design, where we select the best design concept that meets the criteria for success.

## Before you start
<!-- bite: c2227fc5-105a-400e-87b6-4618c15205db -->

You should know how concepts are generated and the factors for evaluating them ([[engineering-design-and-prototyping/08-concept-generation-3|Concept Generation 3]]).

After this lesson you will be able to:

1. name the four skills used to select the best design concept;
2. build a Pugh matrix and calculate its weighted totals;
3. give the benefits of the Pugh matrix and its limits.

## What concept selection is
<!-- bite: edf1018c-85f4-4731-84d0-6ae75386c6a5 -->

By now concept generation has given us many ideas. Selection (phase 3) picks the best one, and refinement (phase 4) improves the one we picked.

The danger here is picking the concept you *like*, not the one that's *best*. Maybe it was your idea, or it looks nice. The methods in the next three lessons stop that from happening, by scoring every concept against the same criteria.

## How to select the best design concept
<!-- bite: 8ede1fbf-b930-489f-8d83-ee592e123b70 -->

To select the best design concept, apply and combine these skills:

1. **Evaluation**: the ability to measure and assess the performance and outcomes of the design concepts using various methods and tools.
2. **Comparison**: the ability to identify and analyse the similarities and differences of the design concepts.
3. **Decision-making**: the ability to make a rational and justified choice among the design concepts.
4. **Trade-off analysis**: the ability to balance and optimise the conflicting objectives, requirements and constraints of the design solution.

There are four methods that are the tools for doing this: the Pugh matrix, the Kano model, the decision matrix and AHP. We start with the Pugh matrix.

## The Pugh matrix
<!-- bite: 7c158627-c49d-4e3d-9085-11997d18da40 -->

A Pugh matrix is a method of evaluating and comparing design concepts by using a table that lists the criteria for success and the design concepts, and assigns scores to each design concept based on how well it meets or exceeds the criteria **compared to a reference design concept**.

That last part is the key. You don't ask "how good is this bag out of 10?" You ask "is this bag better, the same, or worse than the reference bag?" Comparing is easier than scoring from nothing.

## Steps of the Pugh matrix
<!-- bite: 4a4c5a58-2859-4ce3-81a9-57b581359b32 -->

1. Define your evaluation criteria (and assign weights to each criterion based on its importance).
2. Identify your design concepts (ideas, basically).
3. Create the matrix: criteria go in the rows, design concepts in the columns. You can add a column for a reference design.
4. Score each concept by comparing it to the reference design for each criterion: **+1** is better, **0** is the same, **−1** is worse.
5. Analyse the scores.

The reference design scores 0 everywhere, because it's the same as itself. It's usually the current product or the most obvious concept.

## Lecture example: a new student backpack
<!-- bite: f0c0735b-ac32-41c3-ad48-87d9ef2db382 -->

Here are three backpack concepts compared with a reference backpack. The weighted total is weight × score, added up.

| Criteria | Weight | Minimalist roll-top | Padded backpack | Convertible bag |
| --- | --- | --- | --- | --- |
| Comfort | 2 | +1 | −1 | 0 |
| Capacity | 1 | −1 | +1 | +1 |
| Organisation | 1 | −1 | +1 | +1 |
| Durability | 1 | 0 | +1 | 0 |
| Cost | 0.5 | −1 | +1 | 0 |
| Style | 0.5 | +1 | 0 | +1 |
| **Weighted total** |  | **0** | **1.5** | **2.5** |

## Working out the totals
<!-- bite: 1e39ed18-4d49-4ce8-8675-edc928517bb1 -->

Let's check the convertible bag, row by row:

- Comfort: 2 × 0 = 0
- Capacity: 1 × (+1) = 1
- Organisation: 1 × (+1) = 1
- Durability: 1 × 0 = 0
- Cost: 0.5 × 0 = 0
- Style: 0.5 × (+1) = 0.5

Total: 0 + 1 + 1 + 0 + 0 + 0.5 = **2.5**.

Now the roll-top: 2(+1) + 1(−1) + 1(−1) + 1(0) + 0.5(−1) + 0.5(+1) = 2 − 1 − 1 + 0 − 0.5 + 0.5 = **0**. It's better on comfort, which has the biggest weight, but loses on almost everything else.

The padded backpack and the convertible bag come out ahead of the roll-top. The lecture says you may need more analysis or prototyping before the final decision.

## Benefits and limits
<!-- bite: a11bba4d-03e8-4d8d-aa8b-483278ad3e72 -->

**Benefits:**

1. Ensures you evaluate designs based on what truly matters.
2. Reduces bias and emotional decision-making.
3. Makes the selection process transparent and easy to communicate.
4. Encourages discussion and consensus building.

**Note:** you may need to consider other factors like feasibility, manufacturability and market research to take the final decision.

And notice its weakness: +1 says "better", but not *how much* better. A bag that is a little more comfortable and a bag that is far more comfortable both get +1. The next methods fix that in different ways. The Kano model, next, looks at how users *feel* about each feature.

## Common pitfalls
<!-- bite: 882557c8-bc48-4caa-95af-07ef1a59ee38 -->

1. **Forgetting the weights.** Add up weight × score, not just the scores. Without weights, the roll-top's comfort advantage counts the same as style.
2. **Scoring against the wrong thing.** Each concept is compared with the reference, not with each other.
3. **Treating the total as the final answer.** It guides the decision; feasibility, manufacturability and market research can still change it.

## Check your understanding
<!-- bite: 0b38fd14-650e-4c71-bd12-2ed59a1e5ef7 -->

Try each one before you open the answer.

1. <!-- q: gap id="7e0c2b15" answers="+1|1|plus one;0|zero;-1|minus one" -->
   Fill in the gaps. In a Pugh matrix, a concept that is better than the reference scores ___, the same scores ___, and worse scores ___.

   <details><summary>Answer</summary>

   +1, 0 and −1.

   </details>

2. <!-- q: exact id="a4f9d360" answer="2" -->
   A Pugh matrix for a water bottle has these criteria and weights: Leakproof (weight 3), Weight (weight 2), Cost (weight 1). Concept X scores +1 on Leakproof, −1 on Weight and +1 on Cost. What is Concept X's weighted total?

   <details><summary>Answer</summary>

   3(+1) + 2(−1) + 1(+1) = 3 − 2 + 1 = 2.

   </details>

3. <!-- q: exact id="c1b85e27" answer="-0.5" accept="-1/2" -->
   A Pugh matrix for a desk fan has these criteria and weights: Airflow (weight 2), Noise (weight 1.5), Price (weight 1). Concept Y scores −1 on Airflow, +1 on Noise and 0 on Price. What is its weighted total?

   <details><summary>Answer</summary>

   2(−1) + 1.5(+1) + 1(0) = −2 + 1.5 + 0 = −0.5. It comes out slightly worse than the reference.

   </details>

4. <!-- q: mcq id="58d2e4a0" -->
   What does the reference design score on every criterion?

   - [x] 0
   - [ ] +1
   - [ ] It depends on the weights

   <details><summary>Answer</summary>

   0, because it is the same as itself.

   </details>

5. <!-- q: open id="0f6b3a9c" -->
   Give two benefits of the Pugh matrix, and one weakness.

   <details><summary>Answer</summary>

   Benefits (any two): it evaluates designs on what truly matters; it reduces bias and emotional decisions; it makes the selection transparent and easy to communicate; it encourages discussion and consensus. Weakness: +1 only says "better", not how much better, and the total may still need feasibility, manufacturability and market research before the final decision.

   </details>

## Before moving on
<!-- bite: 1fe477b7-d53f-4d6f-9178-50d75205043f -->

You can name the four selection skills, build a Pugh matrix, and calculate its weighted totals. **Next:** [[engineering-design-and-prototyping/10-concept-selection-2|Concept Selection 2: The Kano Model]]: choosing features by how they make users feel.

## Related
<!-- bite: 68b83153-a63f-45cf-8b0d-d9dc8dfba493 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[systems-engineering/05-trade-studies|Trade Studies]]: comparing design options fairly, from the systems engineering side.

## About this lesson
<!-- bite: e756b4b6-8bf2-4ff2-b4ee-f0178a5bae08 -->

**Level:** Beginner. **Covers:** the four skills for selecting a concept (evaluation, comparison, decision-making, trade-off analysis), and the Pugh matrix with the lecture's student backpack example.

**Where it sits:** lesson 9 of 21, part 1 of 3 on concept selection (phase 3).

**Source:** the author's own SSG 532 notes (lecture 3). The totals are checked by `scripts/diagrams/engineering_design.py`.
