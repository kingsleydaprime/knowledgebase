---
id: c1e2b9ad-f5b8-4c1b-8604-d592e6c16e91
---

# Priority Rules 1: ACTRES, ROT, TIMRES, GENRES, RAF and SAF

A priority rule gives each activity a score that decides which one gets scarce resources first.

## Before you start
<!-- bite: 579b087a-a400-46f1-8b3d-50cc957c4f0c -->

You should have read [[planning-and-scheduling/26-resources-2|26 — Resources 2]] and [[planning-and-scheduling/17-pert-1|17 — PERT 1]] (for the standard deviation).

After this lesson you will be able to:

1. define ACTRES, ROT, TIMRES, GENRES, RAF and SAF and write each formula;
2. compute each one for a given activity;
3. explain what each rule is trying to favour.

## What a priority rule is
<!-- bite: aad2f4ee-f14e-4a68-ab99-88350026ac52 -->

On day 3 of the fence, with only 3 workers, B (2 workers) and C (2 workers) both want to start. Only one can. Which? Smoothing solved the fence because C had float. In a bigger, resource-constrained project, float runs out, and you need a rule that decides, every time there's a clash, who gets the workers.

These rules are called **heuristics**: rules of thumb that give a good schedule quickly, but not always the best one. All the ones below come from the 2019/20 and 2020/21 papers, and the 2019/20 paper asks you to define them for 10 marks.

## The symbols
<!-- bite: 17457d19-f2ee-4107-860e-06c9685732f2 -->

1. **t**: This is the activity's duration (for a PERT activity, its expected time).
2. **$x_{ij}$**: This is how much of resource $j$ activity $i$ needs. "Task A needs 4 Type 1 workers" means $x$ for A and Type 1 is 4.
3. **$y_j$**: This is the most of resource $j$ available at any time.
4. **s**: This is the activity's standard deviation, (b − a)/6 from PERT.
5. **w**: This is a weight between 0 and 1, chosen by the planner.

The running example is one activity: t = 4 weeks, needing 3 workers in total, 2 of the 4 available Type 1 workers and 3 of the 6 available Type 2 workers, with s = 4/3.

## The simple rules
<!-- bite: 099549d1-d64b-4020-a3d2-e8e38e5c3693 -->

1. **ACTRES** (activity times resources): t × (resources required). It favours long activities that need a lot. Example: 4 × 3 = **12**.
2. **ROT** (resource over time): (resources required) / t. It favours activities that need a lot of resource for a short time. Example: 3 / 4 = **0.75**.
3. **TIMRES** (time and resources): 0.5 × t + 0.5 × ACTRES, an equal mix of duration and ACTRES. Example: 0.5 × 4 + 0.5 × 12 = **8**.
4. **GENRES** (general resources): w × t + (1 − w) × ACTRES. It is the general form, and TIMRES is GENRES with w = 0.5. Example with w = 0.3: 0.3 × 4 + 0.7 × 12 = **9.6**.

## RAF: the resource allocation factor
<!-- bite: 4b40bf9d-71d5-4235-aa61-c8b7ee32e573 -->

**RAF measures what share of the available resources an activity uses, per unit of its time.** For each resource, divide what the activity needs by what is available, add the shares up, and divide by the duration.

$$RAF_i = \frac{1}{t_i} \sum_j \frac{x_{ij}}{y_j}$$

Example: the activity needs 2 of 4 Type 1 (a share of 0.5) and 3 of 6 Type 2 (also 0.5). RAF = (1/4) × (0.5 + 0.5) = **0.25**.

A high RAF means a short activity that grabs a big share of what's available: it blocks others, so it's worth getting out of the way.

## SAF: the stochastic allocation factor
<!-- bite: 7e0570dc-716f-418f-9c12-049a005cc386 -->

**SAF adds a measure of how uncertain an activity is to its duration.** "Stochastic" means random: the rule cares about the spread, not just the length.

$$SAF_i = t_i + \frac{s_i}{t_i}$$

Here s/t is the standard deviation as a fraction of the duration, called the coefficient of variation. Example: SAF = 4 + (4/3)/4 = 4 + 0.333 = **4.333**.

A high SAF means a long or unpredictable activity, one that could cause trouble late if it's left to the end.

RAF is a small decimal (0.25) while SAF is a number of weeks (4.333). Put them in one formula as they are, and SAF would swamp RAF. The next lesson scales them to the same range and combines them into the CAF, the score used in the exam's big question.

## Common pitfalls
<!-- bite: 76beaacd-bd28-4dbc-96b4-d1c1e98cae53 -->

1. **Mixing up ROT and ACTRES.** ACTRES multiplies by t; ROT divides by t.
2. **Forgetting to divide by $y_j$ in RAF.** RAF uses shares of what's available, not raw counts.
3. **Using variance instead of s in SAF.** SAF uses the standard deviation.
4. **Calling the rules optimal.** They are heuristics: quick and usually good, not guaranteed best.

## Check your understanding
<!-- bite: 5500814b-c969-4099-922d-1c78335fdc7e -->

Try each one before you open the answer.

1. <!-- q: exact id="6f1c8a3e" answer="15" -->
   An activity takes 5 days and needs 3 workers. What is its ACTRES?

   <details><summary>Answer</summary>

   15: 5 × 3.

   </details>

2. <!-- q: exact id="0b9e4d27" answer="0.6" accept="3/5" -->
   An activity takes 5 days and needs 3 workers. What is its ROT?

   <details><summary>Answer</summary>

   0.6: 3 / 5.

   </details>

3. <!-- q: exact id="e2d75a90" answer="10" -->
   An activity takes 5 days and needs 3 workers. What is its TIMRES?

   <details><summary>Answer</summary>

   10: 0.5 × 5 + 0.5 × 15, where ACTRES = 15.

   </details>

4. <!-- q: exact id="8a3f61c4" answer="0.2" accept="1/5" -->
   An activity takes 5 weeks and needs 4 of the 8 available Type 1 workers and 5 of the 10 available Type 2 workers. What is its RAF?

   <details><summary>Answer</summary>

   0.2: (1/5) × (4/8 + 5/10) = (1/5) × 1.

   </details>

5. <!-- q: exact id="c5b0e819" answer="6.1" -->
   An activity has expected time 6 weeks and standard deviation 0.6 weeks. What is its SAF?

   <details><summary>Answer</summary>

   6.1: 6 + 0.6 / 6 = 6 + 0.1.

   </details>

6. <!-- q: open id="1d47f3b6" -->
   Why can't RAF and SAF be combined into one score without scaling?

   <details><summary>Answer</summary>

   They are on very different scales: RAF is a small decimal (a fraction of resources per unit time), while SAF is roughly a number of weeks. Added or weighted directly, SAF would dominate and RAF would hardly affect the result. Scaling both to a common range, such as 0 to 100, lets each count as intended.

   </details>

## Before moving on
<!-- bite: acb91161-9102-4e93-8fdc-4d127a971249 -->

You can define and compute the six rules. **Next:** [[planning-and-scheduling/29-priority-rules-2|29 — Priority Rules 2: Scaling and the Composite Allocation Factor]].

## Related
<!-- bite: 0e69bf18-43d4-40e6-b47b-b67c0f608228 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[operations-research/10-heuristics-and-metaheuristics|Heuristics and Metaheuristics]]: why rules of thumb are used when the best answer is too hard to find.

## About this lesson
<!-- bite: 2aeb3c9d-938c-442b-9105-b499a793506e -->

**Level:** Intermediate. **Covers:** ACTRES, ROT, TIMRES, GENRES, RAF and SAF, with their formulas and what each favours.

**Where it sits:** lesson 28 of 35, in part 7 (resources). Part 4 of 7 on resources; part 1 of 2 on priority rules.

**Source:** the author's own SSG 513 study notes, section 7 (the 2019/20 and 2020/21 papers). The running example and the "what it favours" lines are added for this lesson.
