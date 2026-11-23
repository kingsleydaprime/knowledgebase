---
id: 3c00e2a7-07c0-4de2-8dc4-abb2842aa51e
---

# Concept Selection 3: The Decision Matrix and AHP

The decision matrix and AHP are concept selection methods that score every concept with weighted numbers.

## Before you start
<!-- bite: 48a1763c-fec8-416b-bd3a-83e3215b2f01 -->

You should know the Pugh matrix ([[engineering-design-and-prototyping/09-concept-selection-1|Concept Selection 1]]) and the Kano model ([[engineering-design-and-prototyping/10-concept-selection-2|Concept Selection 2]]).

After this lesson you will be able to:

1. build a decision matrix and calculate each option's total score;
2. describe the five steps of AHP and when to use it;
3. say how the decision matrix differs from the Pugh matrix.

## What the decision matrix and AHP are
<!-- bite: 008f6864-580e-491f-917f-77d57342a500 -->

Remember the Pugh matrix's weakness? +1 said "better" but not *how much* better. The decision matrix fixes that: each concept gets a real score, say 1 to 5, on each criterion.

AHP goes further, for decisions that are big and complicated, with many criteria and many people to satisfy. It breaks the decision into levels and compares things two at a time.

We start with the decision matrix, because it's the one you'll use most (and the one lesson 20 uses for the study desk).

## The decision matrix
<!-- bite: 956c1735-965f-44cf-bcf3-6f081772c6fc -->

A decision matrix is a method of evaluating and comparing design concepts by using a table that lists the criteria for success and the design concepts. It assigns weights to each criterion and scores to each design concept based on how well it meets or exceeds the criterion, and calculates the total score for each design concept by multiplying the weights and the scores.

**Steps:**

1. Define criteria and weights (weights indicate relative importance, 5 being most important).
2. List options.
3. Score each option.
4. Calculate total scores (weight × score, added up).
5. Analyse results.

## Lecture example: choosing an office location
<!-- bite: 4f90d919-3274-40c8-a627-39436c49bfcd -->

| Criteria | Weight | A: Downtown | B: Suburban park | C: Coworking |
| --- | --- | --- | --- | --- |
| Rent cost | 5 | 2 | 4 | 5 |
| Accessibility | 4 | 5 | 3 | 4 |
| Space | 3 | 4 | 5 | 3 |
| Amenities | 2 | 3 | 2 | 5 |
| Neighbourhood | 4 | 4 | 3 | 2 |
| **Total** |  | **64** | **63** | **68** |

Here a higher score is always better, so for rent cost, 5 means cheapest.

## Working out the totals
<!-- bite: 291044ba-d759-4aae-bb6f-e7e542994b8f -->

Multiply each score by its weight, then add down the column:

- **A:** 5(2) + 4(5) + 3(4) + 2(3) + 4(4) = 10 + 20 + 12 + 6 + 16 = **64**
- **B:** 5(4) + 4(3) + 3(5) + 2(2) + 4(3) = 20 + 12 + 15 + 4 + 12 = **63**
- **C:** 5(5) + 4(4) + 3(3) + 2(5) + 4(2) = 25 + 16 + 9 + 10 + 8 = **68**

So C (coworking) wins.

> **Correction:** the lecture gives totals of 58, 55 and 58, which would make A and C a tie. Working it out with the lecture's own scores gives 64, 63 and 68, so C wins outright. If an exam uses this table, show the working so the examiner can follow your numbers.

## Benefits of the decision matrix
<!-- bite: 59223173-4cf9-4598-a2ed-240ab9d11f2a -->

1. Forces systematic evaluation of multiple factors.
2. Makes the decision-making process clear and understandable.
3. Facilitates discussion and consensus-building among stakeholders.
4. Allows objective comparison of design concepts.
5. Acknowledges the importance of different criteria and their relative weights.

**Pugh matrix versus decision matrix:** the Pugh matrix scores each concept as better (+1), same (0) or worse (−1) than a reference. The decision matrix gives each concept its own score on a scale, with no reference. So the decision matrix shows *how much* better.

## The Analytical Hierarchy Process (AHP)
<!-- bite: 1098b9ff-3803-4a05-9bb5-71ab07e8e2e9 -->

AHP is a method that uses a hierarchical structure to break the decision problem down into levels of objectives, criteria and alternatives. It assigns priorities to each element using pairwise comparisons and consistency checks, then calculates the overall ranking of the alternatives by combining the priorities.

It is best when decisions are complex, with many criteria and perspectives.

**Pairwise** means two at a time. Instead of asking "how important is price, out of 5?", you ask "is price more important than design, and by how much?" People are better at comparing two things than at scoring one thing alone.

## Steps of AHP
<!-- bite: 58cf43c5-5e3c-4fd3-9b6c-c281d5724692 -->

1. **Define the hierarchy**: objective, then criteria, then alternatives.
2. **Make pairwise comparisons**, i.e. compare each criterion pair within each level, on a 1 to 9 scale (1 = equal importance, 9 = much more important).
3. **Check for consistency** in your judgements by comparing ratios across different comparisons (a consistency ratio and an eigenvector, by software or by hand). If you said price beats design and design beats brand, then price had better beat brand too.
4. **Priority calculation**: calculate the relative importance of each element.
5. **Perform the overall ranking**: combine the priorities of the criteria with the performance score of the alternatives for every criterion, calculate the overall score of each alternative, then choose the alternative with the highest overall score.

## Lecture example: a fitness tracker
<!-- bite: d0c38014-3568-4393-af39-d1d1ad4daf5c -->

- **Objective:** the most popular fitness tracker.
- **Criteria:** functionality, design, price, brand.
- **Alternatives:** minimalist wristband, multi-feature smartwatch, hybrid analog/digital watch.

If functionality is 2 times more important than design, and the smartwatch is much better on functionality, the smartwatch can come out highest overall even though it costs more. AHP lets you justify that with evidence.

**Benefits of AHP:**

1. Makes complex decisions easier to understand and communicate.
2. Reduces bias and ensures logical decision-making.
3. Provides numerical scores for comparison and ranking.
4. Accommodates multiple stakeholders.

We've now picked a concept. Phase 4 is about making it better, and that's the next lesson.

## Common pitfalls
<!-- bite: 6d86abcd-daa8-4fd9-b168-e0ed25cffebc -->

1. **Adding the scores without the weights.** The total is weight × score, added up.
2. **Mixing up which way the scale runs.** For a cost criterion, a high score must mean *cheap*, so that higher is always better.
3. **Inconsistent AHP judgements.** If A beats B and B beats C, A must beat C. The consistency check catches this.

## Check your understanding
<!-- bite: 350a080c-1134-42ca-9c4b-720fe9c5e8f0 -->

Try each one before you open the answer.

1. <!-- q: exact id="5c0e9a83" answer="44" -->
   A decision matrix for a water pump has three criteria. Flow rate has weight 5, Cost has weight 4, Ease of repair has weight 2. Pump X scores 4 on flow rate, 5 on cost and 2 on ease of repair. What is Pump X's total score?

   <details><summary>Answer</summary>

   5(4) + 4(5) + 2(2) = 20 + 20 + 4 = 44.

   </details>

2. <!-- q: mcq id="d2b71f4e" -->
   A decision matrix has these totals: Concept P = 52, Concept Q = 61, Concept R = 58. Which concept is chosen?

   - [ ] P
   - [x] Q
   - [ ] R

   <details><summary>Answer</summary>

   Q, the highest total. You'd still check feasibility and other factors before the final decision.

   </details>

3. <!-- q: gap id="1e9f6c42" answers="1;9" -->
   Fill in the gaps. In AHP, pairwise comparisons use a scale from ___ (equal importance) to ___ (much more important).

   <details><summary>Answer</summary>

   1 to 9.

   </details>

4. <!-- q: mcq id="8f3a0d5b" -->
   A city must choose a site for a new power station. There are 8 criteria, 3 levels of decision, and engineers, residents and the government all have a say. Which method fits best?

   - [ ] Pugh matrix
   - [ ] Kano model
   - [x] AHP

   <details><summary>Answer</summary>

   AHP. It is best when decisions are complex, with many criteria and perspectives, and it accommodates multiple stakeholders.

   </details>

5. <!-- q: open id="6a7d2c19" -->
   How does a decision matrix differ from a Pugh matrix?

   <details><summary>Answer</summary>

   A Pugh matrix scores each concept against a reference design: +1 better, 0 the same, −1 worse. A decision matrix gives each concept its own score on a scale (for example 1 to 5) with no reference, multiplies by the weights and adds up. So the decision matrix shows how much better a concept is, not just whether it is better.

   </details>

## Before moving on
<!-- bite: 2e9e16f9-821f-4cdd-9da6-0b7dbe27748d -->

You can build a decision matrix and total it, describe AHP's five steps, and choose the right selection method for a problem. **Next:** [[engineering-design-and-prototyping/12-concept-refinement|Concept Refinement]]: improving the concept you picked.

## Related
<!-- bite: af0c306b-abb4-4987-8114-7e88eaaee3ee -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]
- [[operations-research/index|Operations Research]]: the wider field of making decisions with numbers.

## About this lesson
<!-- bite: 869e256e-66f3-4368-98f7-07c1a06df2fd -->

**Level:** Beginner. **Covers:** the decision matrix with the lecture's office location example (and a correction to its totals), how it differs from the Pugh matrix, and AHP with the fitness tracker example.

**Where it sits:** lesson 11 of 21, part 3 of 3 on concept selection.

**Source:** the author's own SSG 532 notes (lecture 3). The office totals are checked by `scripts/diagrams/engineering_design.py`.
