---
id: cafa38db-1d7f-4164-8cfd-177ede563bf9
---

# Output Analysis

A simulation's output is random, so it is summarised with replications, descriptive statistics and confidence intervals before any conclusion is drawn.

## Before you start
<!-- bite: b8fe9498-a916-4195-a0cc-5b30c815bdd2 -->

You should have read [[systems-simulation/33-verification-and-validation-3|33 — Verification and Validation 3]] and [[systems-simulation/22-monte-carlo-simulation|22 — Monte Carlo Simulation]].

After this lesson you will be able to:

1. explain why one run proves nothing and what a replication is;
2. compute a confidence interval for a performance measure from replications;
3. tell a terminating simulation from a steady-state one, and use hypothesis tests to compare designs.

## What output analysis is
<!-- bite: 5ed31239-d78d-4e39-8a45-9eabf5f76dd7 -->

**Output analysis** is the statistical reading of a simulation's results. Lesson 02 named the problem: random inputs give random outputs, so a long queue in one run might be the system or just bad luck. Output analysis separates the two.

This lesson covers the four techniques from the class notes (descriptive statistics, confidence intervals, hypothesis tests and optimisation), plus how long and how many runs to do.

## Replications
<!-- bite: aff6f114-fc78-4db4-938c-2302c43a366b -->

A **replication** is one independent run of the model, with its own random numbers. Each replication gives one value of each performance measure, such as one average wait. Across replications those values form a **random sample**, and ordinary statistics works on it.

Ten to thirty replications is a typical minimum. More replications give a narrower confidence interval.

## Descriptive statistics
<!-- bite: c84fab10-18b5-40dc-a9ba-34982a540d4c -->

Summarise the sample with measures of **central tendency** (mean, median, mode) and **dispersion** (range, standard deviation, variance). The mean says what typically happens; the spread says how much it varies from run to run.

## Confidence intervals
<!-- bite: 44bb78e1-0a26-4e9f-a35b-911a7d789cb7 -->

A **confidence interval** is a range that contains the true long-run value with a stated confidence, such as 95%. For n replications with mean $\bar{x}$ and standard deviation s:

$$\bar{x} \pm t_{n-1,\,0.025}\,\frac{s}{\sqrt{n}}$$

The part after ± is the **half-width**, which is what Arena reports beside each average.

**Example:** 10 replications of a bank model give a mean wait of 6.2 minutes with s = 1.5. The t value for 9 degrees of freedom at 95% is 2.262. Half-width = 2.262 × 1.5 ÷ √10 = 1.07. So the true mean wait is between about 5.13 and 7.27 minutes, with 95% confidence.

## Hypothesis testing and optimisation
<!-- bite: 2ab0064d-d8d3-44ff-8d53-795f466ad809 -->

1. **Hypothesis testing:** test a claim about a parameter with the output data, at a significance level such as 0.05 or 0.01. For example: "a second teller cuts the average wait". Compare the two designs' replications with a t-test, ideally using **common random numbers** (the same streams, lesson 18) so the difference comes from the design.
2. **Optimisation:** find the values of the decision variables that maximise or minimise an objective (profit, cost, throughput) within constraints (capacity, budget, quality). Arena's OptQuest does this (lesson 38).

## How long to run
<!-- bite: afede51f-ebf1-47f6-a1fc-e99db02daf3a -->

1. **Terminating simulation:** the system has a natural end, such as a bank that closes at 4 pm. Run each replication for the real opening hours, starting empty, as the real bank does.
2. **Steady-state simulation:** you want long-run behaviour, such as a factory that runs non-stop. Use a very long run (the textbook pharmacy used 10,000 hours) and a **warm-up period**: throw away the early results, so the artificial empty start doesn't bias the averages.

## The challenges
<!-- bite: ce042956-a634-4056-be09-4835e6d4f37a -->

The class notes list four challenges for verifying, validating and analysing: data availability and quality; model complexity and scalability; model uncertainty and variability; and communicating the results. That last one is ticked in the notes: managers want one number, and the honest answer is a range.

## Common pitfalls
<!-- bite: 22338854-5f9f-49a1-a4dc-f97f6f18dbd3 -->

1. **Trusting one run.** Report a mean and a confidence interval from several replications.
2. **No warm-up in a steady-state model.** The empty start makes averages look too good.
3. **Using z instead of t for few replications.** With 10 runs, use t with 9 degrees of freedom.
4. **Comparing designs with different random numbers.** Use common random numbers.

That completes the method. The last part shows it in the tool the exam uses: Arena, starting with its building blocks.

## Check your understanding
<!-- bite: e597b9cd-9e29-4e72-8f80-56c3ab3d419a -->

Try each one before you open the answer.

1. <!-- q: exact id="c07dbd85" answer="1.0655" sigfigs="2" -->
   16 replications give a mean time in system of 12.4 minutes, with standard deviation 2.0. The t value for 15 degrees of freedom at 95% is 2.131. What is the 95% half-width, in minutes?

   <details><summary>Answer</summary>

   About 1.07: 2.131 × 2.0 ÷ √16 = 2.131 × 0.5. So the true mean is roughly 11.3 to 13.5 minutes.

   </details>

2. <!-- q: exact id="44f54861" answer="4" -->
   A confidence interval from 10 replications is too wide. About how many times as many replications are needed to halve its half-width?

   <details><summary>Answer</summary>

   About 4 times: the half-width shrinks with 1/√n, so halving it needs four times the replications (roughly 40 runs).

   </details>

3. <!-- q: mcq id="3ad23708" -->
   A model of a factory that runs 24 hours a day starts each run with every machine idle and every buffer empty. What should you do?

   - [ ] Nothing; the start doesn't matter
   - [x] Use a warm-up period and discard the early results before computing averages
   - [ ] Stop each run after one hour
   - [ ] Use only one long replication with no statistics

   <details><summary>Answer</summary>

   Use a warm-up period. The empty start isn't typical of a non-stop factory, and would make averages like queue length look too good.

   </details>

4. <!-- q: mcq id="7e2cd17a" -->
   A bank opens at 8 am and closes at 4 pm, starting each day empty. What kind of simulation is this?

   - [x] Terminating: run each replication for the 8 hours of opening
   - [ ] Steady-state: run for 10,000 hours
   - [ ] Monte Carlo with no clock
   - [ ] Continuous

   <details><summary>Answer</summary>

   Terminating. The system has a natural start and end, so each replication covers one real day.

   </details>

5. <!-- q: open id="1a69a436" -->
   A manager sees one run where the new layout cut the average wait from 9 to 7 minutes and wants to adopt it. What should you say?

   <details><summary>Answer</summary>

   One run is one random sample, so the 2-minute gap might be luck. Run several replications of both layouts with common random numbers, compute confidence intervals or a t-test on the difference, and adopt the layout only if the improvement is statistically clear.

   </details>

## Before moving on
<!-- bite: ca5a2636-f563-4dcc-ab14-bf9bb3741bae -->

You can explain replications, compute a confidence interval, choose run length and compare designs fairly. **Next:** [[systems-simulation/35-arena-1|35 — Arena 1]].

## Related
<!-- bite: a7e22950-2d64-4f50-b252-d6c068399d93 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 85e68a88-712c-46f3-9d93-e2c9c03d7dea -->

**Level:** Intermediate. **Covers:** replications, descriptive statistics, confidence intervals and the half-width, hypothesis tests and optimisation, terminating and steady-state runs with warm-up, and the challenges.

**Where it sits:** lesson 34 of 38, the end of part 8 (verification, validation and output analysis).

**Source:** the author's own SSG 517 study notes, sections 1 and 8. The t-based confidence interval formula and both worked numbers are added for this lesson; check the formula against your lecturer's notes.
