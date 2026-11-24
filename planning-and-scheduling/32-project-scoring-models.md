---
id: 8f30cf1c-7fca-49b9-89be-4d889f52f180
---

# Project Scoring Models

A project scoring model turns each candidate project's cost, chance of success and payoff into one number, so a manager can rank projects and choose which ones to run.

## Before you start
<!-- bite: d6db16be-87f5-4cb9-8ceb-e39ad65318d4 -->

You should have read [[planning-and-scheduling/02-the-project-environment|02 — The Project Environment and Key Terms]] (portfolio).

After this lesson you will be able to:

1. compute a project's score with the formula from the 2024/25 paper;
2. rank a set of projects and choose the best ones;
3. comment, as a project manager would, on close calls and odd data.

## What a scoring model is
<!-- bite: 00711a7f-9378-4a52-922e-dc4041c89f30 -->

Everything so far assumed the project had already been chosen. But before anyone draws a network, an organisation with limited money must decide *which* projects to do at all. Should the fence company take the estate contract or the school contract? Both look good in different ways: one pays more, the other is more certain.

A scoring model puts those different strengths on one scale. You pick the factors that matter, combine them in a formula, and rank the projects by the result. It is a tool of portfolio management: choosing the set of projects that best serves the organisation.

## The formula from the paper
<!-- bite: f9cbec42-c75f-4237-8acb-f4483f321f6c -->

The 2024/25 paper (Question 1d) gives this model:

**A project's score is its probability of success plus twice its payoff, all divided by its cost.**

$$\text{Score} = \frac{P(\text{success}) + 2 \times \text{Payoff}}{\text{Cost}}$$

A higher score is better. Payoff counts double, and dividing by cost rewards projects that give more for less money.

## A worked example
<!-- bite: df160b63-ca1e-4364-a457-d10cb646245a -->

Four contracts the fence company is weighing, with payoff and cost in millions of naira:

1. **Estate**: P = 0.8, payoff 10, cost 5. Score = (0.8 + 20) / 5 = **4.16**.
2. **Hospital**: P = 0.6, payoff 12, cost 6. Score = (0.6 + 24) / 6 = **4.10**.
3. **School**: P = 0.9, payoff 6, cost 3. Score = (0.9 + 12) / 3 = **4.30**.
4. **Factory**: P = 0.5, payoff 15, cost 8. Score = (0.5 + 30) / 8 = **3.81**.

Ranked: School 4.30, Estate 4.16, Hospital 4.10, Factory 3.81. If the company can take two, it picks **School and Estate**.

## Thinking like a project manager
<!-- bite: 1d3d949e-e5d1-47d6-b31e-120cc6a6ef5b -->

The paper asks you to comment "as the project manager", and the numbers alone don't earn those marks. Three things to say:

1. **Close calls.** Estate (4.16) and Hospital (4.10) are nearly tied. A gap that small is inside the error of the estimates, so the choice could be settled by something outside the score, such as risk, strategic fit or the client relationship.
2. **What the formula really rewards.** P(success) is at most 1, while payoff is doubled, so the score is driven almost entirely by payoff divided by cost. The chance of success barely moves it. A manager might want a model that multiplies payoff by the probability instead.
3. **Odd data.** In the 2024/25 paper several P(success) values are above 1, which a real probability can't be. Score them as given, but say so, and treat them as scores on a larger scale.

## The 2024/25 answer
<!-- bite: 033c7fc7-2394-4bad-978f-7c21b76e9549 -->

For the record, the paper's twelve projects score: project 4 at 4.96, 6 at 4.22, 3 at 4.13, 5 at 4.10, 8 and 1 at 3.43, 10 at 3.35, 9 at 2.78, 2 at 2.57, 7 at 2.55, 11 at 2.45 and 12 at 2.40. The three best are **projects 4, 6 and 3**, with 5 a very close fourth (4.10 against 4.13), the same kind of near-tie as Estate and Hospital above.

Choosing the project comes first in real life, and planning it follows. The next lesson goes back to planning with three more ways to draw a schedule.

## Common pitfalls
<!-- bite: 8d879900-13be-4022-ba1f-3e4c104003f6 -->

1. **Forgetting to double the payoff.**
2. **Dividing only the payoff by cost.** The whole top line is divided.
3. **Ranking without comment** when the question says "as the project manager".

## Check your understanding
<!-- bite: 68273c7d-0373-400d-a6dc-627f24810294 -->

Try each one before you open the answer.

1. <!-- q: exact id="1a6f3c9e" answer="4.675" sigfigs="3" -->
   A project has P(success) = 0.7, payoff N9 million and cost N4 million. What is its score with Score = (P + 2 × Payoff) / Cost?

   <details><summary>Answer</summary>

   4.675: (0.7 + 18) / 4.

   </details>

2. <!-- q: mcq id="d8e20b47" -->
   Scores: Q 3.9, R 4.4, S 4.2, T 4.19. A firm can take two projects. Which two, and what should the manager add?

   - [ ] Q and R; nothing more
   - [x] R and S; note that S and T are almost tied, so another factor could decide
   - [ ] R and T; S is too risky
   - [ ] S and T; they are closest

   <details><summary>Answer</summary>

   R (4.4) and S (4.2) score highest, but S and T differ by only 0.01, well inside estimating error, so risk or strategy could decide between them.

   </details>

3. <!-- q: open id="6c4b9f12" -->
   In the model Score = (P(success) + 2 × Payoff) / Cost, why does the probability of success hardly affect the ranking?

   <details><summary>Answer</summary>

   P(success) can add at most 1 to the top line, while the payoff is doubled and usually much larger, so the score is driven almost entirely by payoff divided by cost. Two projects with the same payoff and cost but very different chances of success score almost the same.

   </details>

4. <!-- q: open id="e3a07d85" -->
   A table lists a project's P(success) as 1.4. What should you do and say?

   <details><summary>Answer</summary>

   A probability can't exceed 1, so the figure must be a score on some larger scale or a mistake. Use it as given so the answer matches the question, but state the problem in the answer.

   </details>

## Before moving on
<!-- bite: 3eaef8d7-3668-4ca1-b3f4-48eec577261e -->

You can score and rank projects and comment on the result as a manager. **Next:** [[planning-and-scheduling/33-bar-charts-line-of-balance-and-time-location-charts|33 — Bar Charts, Line of Balance and Time-Location Charts]].

## Related
<!-- bite: 7f0ffdef-a348-46f9-a29d-b7b699557521 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[engineering-economics/index|Engineering Economics]]: comparing projects with present worth and benefit-cost ratios.

## About this lesson
<!-- bite: 2d9f202b-0544-449d-a51d-7ea5c68f8acf -->

**Level:** Beginner to intermediate. **Covers:** the 2024/25 scoring formula, ranking, and how to comment as a project manager.

**Where it sits:** lesson 32 of 35, in part 8 (other planning tools).

**Source:** the author's own SSG 513 study notes, section 8. The four-contract example is added for this lesson; its scores are checked in `scripts/diagrams/planning_scheduling.py`.
