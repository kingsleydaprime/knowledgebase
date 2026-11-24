---
id: dbfb137a-30c9-463e-a5c6-b40e112a9256
---

# PERT 3: All Paths and Deadlines for a Given Confidence

When another path is nearly critical, the chance of finishing on time is the chance that every path finishes on time.

## Before you start
<!-- bite: 6ba5a20c-7e28-4a16-896b-2298ff2e7024 -->

You should have read [[planning-and-scheduling/18-pert-2|18 — PERT 2]].

After this lesson you will be able to:

1. explain why a near-critical path can matter as much as the critical one;
2. find the probability that all paths finish by a date;
3. find the time that gives a stated level of confidence.

## What goes wrong with "critical path only"
<!-- bite: 65209a84-c37c-423b-be80-10233b0f6fc2 -->

Last lesson we used only the critical path. That assumes the other paths have so much float they can never be late. Usually true. But picture two paths, one expected at 23 days with a small spread, and one at 22 days with a big spread. The second is "non-critical", yet it can easily run past 25 days. The project is only done when **every** path is done.

So the careful answer is: find each path's chance of finishing in time, using that path's own mean and variance, and **multiply** them. Multiplying is right if the paths are treated as independent, meaning one path running late tells you nothing about another.

## The worked example: e-library
<!-- bite: 911567e7-37e1-46d6-bdb4-d46915888f0a -->

The 2024/25 paper (Question 3b) gives this project, already turned into expected times and variances (days):

| Activity | A | B | C | D | E | F | G | H | I | J | K |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| After | - | - | A | A | B | C, D | E | G | F, G | H | I, J |
| t_e | 5 | 6 | 3 | 5 | 4 | 2 | 1 | 4 | 3 | 1 | 7 |
| V | 1.778 | 0.111 | 0.111 | 1.000 | 1.000 | 0.111 | 0 | 0.111 | 0.444 | 0 | 2.778 |

The critical path is **B-E-G-H-J-K**, with T_e = 6 + 4 + 1 + 4 + 1 + 7 = **23 days** and V_p = 4.0. The question asks: what is the chance the project is done by T_e + 2 = **25 days**?

## Every path on its own
<!-- bite: 3007dd7c-514e-485b-9222-dbf73b582772 -->

There are four paths. For each, add its own t_e values and its own variances, then find Z for 25 days.

| Path | Mean | Variance | Z | Probability |
| --- | --- | --- | --- | --- |
| A-C-F-I-K | 20 | 5.222 | 2.19 | 0.9857 |
| A-D-F-I-K | 22 | 6.111 | 1.21 | 0.8875 |
| B-E-G-H-J-K | 23 | 4.000 | 1.00 | 0.8413 |
| B-E-G-I-K | 21 | 4.333 | 1.92 | 0.9727 |

Look at A-D-F-I-K. It is a day shorter than the critical path, but its variance is bigger, so its chance (0.8875) is not far above the critical path's (0.8413).

## Multiplying them
<!-- bite: a412b168-72f3-4d20-9551-5e3df1f35cca -->

All four paths must be done by day 25:

P = 0.9857 × 0.8875 × 0.8413 × 0.9727 = **0.716**, about 71.6%.

The critical path alone said 84%. The true chance is lower, because there are four ways to be late, not one. Using only the critical path makes a manager overconfident, and the overconfidence grows with the number of near-critical paths.

## The deadline for a given confidence
<!-- bite: 1077ccd4-e36e-418e-b65b-860522887d72 -->

The other common twist runs the Z formula backwards. Instead of "what is the chance of finishing by T?" the client asks "what date can you promise with 95% confidence?"

**Start from the expected time and add as many standard deviations as the confidence requires.**

$$T = T_e + Z \times \sigma$$

For 95% confidence, Z = 1.64 (the table value giving 0.9495; 1.645 is more exact). Using the A to J project of lesson 18, with T_e = 20 and σ = 2.357:

T = 20 + 1.64 × 2.357 = 23.9, so promise **24 days**.

Round up, not down: rounding down drops you below the confidence you promised.

## Common pitfalls
<!-- bite: da0f4d16-d0c1-462a-bd63-5d21c3bf27f7 -->

1. **Using the critical path's variance for every path.** Each path has its own variance.
2. **Adding path probabilities.** Paths must *all* finish, so multiply.
3. **Rounding a promised date down.** It lowers the confidence.
4. **Forgetting the independence assumption.** Paths that share activities are not truly independent; state that you treat them as independent.

Next lesson takes PERT into two more exam twists: using it on costs, and three estimates written as algebra.

## Check your understanding
<!-- bite: d7d2cfb0-7e3d-4445-9123-9e59f17b7284 -->

Try each one before you open the answer.

1. <!-- q: exact id="a7f3b2c1" answer="0.912" sigfigs="2" -->
   A project has two independent paths. Path 1: mean 22 days, variance 4. Path 2: mean 23 days, variance 1. What is the probability both finish within 25 days? (Φ(1.5) = 0.9332, Φ(2) = 0.9772.)

   <details><summary>Answer</summary>

   0.912. Path 1: Z = (25 − 22)/2 = 1.5, P = 0.9332. Path 2: Z = (25 − 23)/1 = 2, P = 0.9772. Both: 0.9332 × 0.9772 = 0.912.

   </details>

2. <!-- q: exact id="4e09d6a8" answer="44.92" sigfigs="3" accept="44.935|45" -->
   A project has expected time 40 weeks and standard deviation 3 weeks. Using Z = 1.64, what completion time gives 95% confidence?

   <details><summary>Answer</summary>

   44.92 weeks: 40 + 1.64 × 3. Promise 45 weeks.

   </details>

3. <!-- q: mcq id="c2d18e5f" -->
   The critical path alone gives an 84% chance of finishing on time. With all paths included the answer is 72%. Why is it lower?

   - [ ] The critical path was calculated wrong
   - [x] Every path must finish in time, so each extra path that might run late lowers the joint chance
   - [ ] Adding paths increases the expected time
   - [ ] The variances were added instead of multiplied

   <details><summary>Answer</summary>

   The project needs all paths done. Each extra path is another way to be late, so the product of the probabilities is lower than any one of them.

   </details>

4. <!-- q: open id="6b85f0e3" -->
   A path is two days shorter than the critical path but has a much bigger variance. Explain why a manager should not ignore it.

   <details><summary>Answer</summary>

   Its large spread means it has a real chance of running past the deadline, possibly as large as the critical path's. Since the project finishes only when every path finishes, a high-variance near-critical path can delay the project, and ignoring it overstates the chance of finishing on time.

   </details>

## Before moving on
<!-- bite: 9eba0dd0-af0a-47f0-8295-edef7f1628c1 -->

You can find the all-paths probability and the deadline for a stated confidence. **Next:** [[planning-and-scheduling/20-pert-4|20 — PERT 4: PERT on Costs and Estimates With a Parameter]].

## Related
<!-- bite: f2f5e126-4f5c-461c-b2a0-ef0fa92b6955 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 8ea79f67-1b25-4152-acdc-a6143ed52e85 -->

**Level:** Intermediate. **Covers:** the all-paths probability with the 2024/25 e-library question, and the deadline for a given confidence.

**Where it sits:** lesson 19 of 35, in part 5 (PERT). Part 3 of 4 on PERT.

**Source:** the author's own SSG 513 study notes, sections 5 and 9.3. The e-library paths were recomputed in `scripts/diagrams/planning_scheduling.py`. The column labels on that paper read a, b, C; they are read here by size as optimistic, most likely and pessimistic.
