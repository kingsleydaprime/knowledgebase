---
id: 7e77fff1-fcbc-497e-8a96-19175d551264
---

# Priority Rules 2: Scaling and the Composite Allocation Factor

The composite allocation factor (CAF) blends scaled RAF and scaled SAF into one priority score out of 100.

## Before you start
<!-- bite: fb3d6383-bc13-42e7-a06b-399b7db984a8 -->

You should have read [[planning-and-scheduling/28-priority-rules-1|28 — Priority Rules 1]].

After this lesson you will be able to:

1. scale RAF and SAF to a range out of 100;
2. combine them into CAF with a weight, and scale CAF;
3. rank a set of activities by priority, as in the 2019/20 exam question.

## What scaling does
<!-- bite: d9c93a59-8541-44da-b749-f0df86ba3f1c -->

Last lesson ended with a problem: RAF is a small decimal, SAF is a number of weeks. Scaling fixes it by turning each into "how big is this compared with the biggest one", on the same 0 to 100 range. Then a weight decides how much each matters.

## The scaling formulas
<!-- bite: dcce19c5-0278-4567-9db4-87b05a1ebfe9 -->

**Scaled RAF: divide each RAF by the largest RAF, times 100.** The activity with the biggest RAF scores 100.

$$\text{Scaled RAF}_i = \frac{RAF_i}{\max RAF} \times 100$$

**Scaled SAF: SAF has two parts, so each part is scaled to 50.** The duration is divided by the longest duration, and s/t by the largest s/t.

$$\text{Scaled SAF}_i = \frac{t_i}{\max t} \times 50 + \frac{s_i / t_i}{\max (s/t)} \times 50$$

**CAF: a weighted blend, with the weight w on RAF.** Then **scaled CAF** divides by the largest CAF, times 100.

$$CAF_i = w \times \text{Scaled RAF}_i + (1 - w) \times \text{Scaled SAF}_i, \qquad \text{Scaled CAF}_i = \frac{CAF_i}{\max CAF} \times 100$$

A higher scaled CAF means a higher priority.

## The worked example: the data
<!-- bite: 4a62c3a2-6c13-44ba-bbba-4ea825df90dd -->

The 2019/20 paper (Question 1c) gives eight development tasks with PERT times in weeks and two types of staff: Type 1 technical (8 available) and Type 2 supportive (10 available). The weight is w = 0.6 on RAF.

| Task | After | a, m, b | t | s | Type 1 | Type 2 |
| --- | --- | --- | --- | --- | --- | --- |
| A Hardware selection | - | 4, 6, 7 | 5.83 | 0.50 | 4 | 5 |
| B Software design | - | 3, 4, 7 | 4.33 | 0.67 | 6 | 3 |
| C Install hardware | A | 2, 3, 4 | 3.00 | 0.33 | 4 | 5 |
| D Code and test | B | 1, 2, 4 | 2.17 | 0.50 | 5 | 4 |
| E File take-on | B | 1, 3, 4 | 2.83 | 0.50 | 3 | 5 |
| F Write user manual | - | 8, 10, 14 | 10.33 | 1.00 | 6 | 6 |
| G User training | E, F | 3, 3, 3 | 3.00 | 0.00 | 5 | 4 |
| H Install and test | C, D | 1, 2, 4 | 2.17 | 0.50 | 5 | 4 |

## Following task A through
<!-- bite: bd04af65-9ed3-454a-8550-d4ea01601ee1 -->

1. **RAF**: (1/5.83) × (4/8 + 5/10) = 1/5.83 = **0.171**. The largest RAF is 0.473 (D and H), so scaled RAF = 0.171 / 0.473 × 100 = **36.2**.
2. **Scaled SAF**: the duration part is 5.83 / 10.33 × 50 = 28.2 (F is longest at 10.33). s/t = 0.50 / 5.83 = 0.086; the largest s/t is 0.231 (D and H), so the second part is 0.086 / 0.231 × 50 = 18.6. Together: 28.2 + 18.6 = **46.8**.
3. **CAF**: 0.6 × 36.2 + 0.4 × 46.8 = **40.5**.
4. **Scaled CAF**: the largest CAF is 84.2 (D and H), so 40.5 / 84.2 × 100 = **48.1**.

## All eight tasks
<!-- bite: ec360dde-4abd-4021-ad37-02daa8a5a79e -->

| Task | RAF | Scaled RAF | Scaled SAF | CAF | Scaled CAF |
| --- | --- | --- | --- | --- | --- |
| A | 0.171 | 36.2 | 46.8 | 40.5 | 48.1 |
| B | 0.242 | 51.2 | 54.3 | 52.5 | 62.3 |
| C | 0.333 | 70.5 | 38.6 | 57.7 | 68.6 |
| D | 0.473 | 100.0 | 60.5 | 84.2 | 100.0 |
| E | 0.309 | 65.3 | 51.9 | 60.0 | 71.2 |
| F | 0.131 | 27.6 | 71.0 | 45.0 | 53.4 |
| G | 0.342 | 72.2 | 14.5 | 49.1 | 58.4 |
| H | 0.473 | 100.0 | 60.5 | 84.2 | 100.0 |

The priority order is **D and H (tied at 100), E, C, B, G, F, A**. The tie doesn't matter: H can't start until C and D are both done, so they never compete.

## Reading the ranking
<!-- bite: 1b4d73fa-540b-4b5a-a76e-538496dcf709 -->

Look at what the score rewards. D and H are short tasks that grab a big share of the staff and are fairly uncertain: get them done and out of the way. F, the 10-week manual, has the highest scaled SAF (71.0) but the lowest RAF, so with w = 0.6 favouring RAF it ranks near the bottom. Change w and the order changes: that's the planner's choice.

The scores are ready. Next lesson uses them to build the actual schedule with Brooks' algorithm.

## Common pitfalls
<!-- bite: 1600cd4e-e66b-4cae-9587-84b1745f1d4a -->

1. **Scaling SAF in one piece.** It is two parts, each scaled to 50.
2. **Putting w on the wrong term.** Read the question: here w = 0.6 is on RAF.
3. **Forgetting the final scaling of CAF.** The exam asks for scaled CAF.
4. **Rounding too early.** Keep three decimals until the end.

## Check your understanding
<!-- bite: 22ce187b-356c-40f4-b88e-92f3525af041 -->

Try each one before you open the answer.

1. <!-- q: exact id="4c7e9b21" answer="85.7143" sigfigs="3" -->
   Two activities have RAF 0.25 and 0.2917. What is the scaled RAF of the first?

   <details><summary>Answer</summary>

   85.7: 0.25 / 0.2917 × 100.

   </details>

2. <!-- q: exact id="a90d3f65" answer="100" -->
   Two activities, each 4 weeks long. P has s/t = 0.333; Q has s/t = 0. What is P's scaled SAF?

   <details><summary>Answer</summary>

   100: (4/4) × 50 + (0.333/0.333) × 50. P has both the longest time and the largest s/t.

   </details>

3. <!-- q: exact id="2e58c1b7" answer="92.8571" sigfigs="3" -->
   An activity has scaled RAF 85.71 and scaled SAF 100. With w = 0.5 on RAF, what is its CAF?

   <details><summary>Answer</summary>

   92.9: 0.5 × 85.71 + 0.5 × 100.

   </details>

4. <!-- q: exact id="f6a14e08" answer="80.7692" sigfigs="3" -->
   Two activities have CAF 92.86 and 75.0. What is the scaled CAF of the second?

   <details><summary>Answer</summary>

   80.8: 75.0 / 92.86 × 100.

   </details>

5. <!-- q: open id="7b3d0c92" -->
   Two tasks tie at a scaled CAF of 100, but one of them has the other's predecessor among its own predecessors. Why doesn't the tie matter when scheduling?

   <details><summary>Answer</summary>

   Priority only matters when two activities are ready at the same moment and compete for resources. If one can't start until the other's chain is finished, they are never ready together, so they never compete, and the tie never has to be broken.

   </details>

## Before moving on
<!-- bite: 290514c7-33cb-4bbe-b119-ac1f137d5238 -->

You can scale RAF and SAF, build CAF and rank activities. **Next:** [[planning-and-scheduling/30-brooks-algorithm-1|30 — Brooks' Algorithm 1: Serial Priority Scheduling]].

## Related
<!-- bite: 8619225d-e4fe-4278-ac1e-91707ce4ba0c -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 2ab88a48-c2e5-44a4-bb18-1db9d06ea967 -->

**Level:** Intermediate to advanced. **Covers:** scaled RAF, scaled SAF, CAF and scaled CAF, worked in full for the 2019/20 question.

**Where it sits:** lesson 29 of 35, in part 7 (resources). Part 5 of 7 on resources; part 2 of 2 on priority rules.

**Source:** the author's own SSG 513 study notes, section 7. Every value in the table is recomputed in `scripts/diagrams/planning_scheduling.py`.
