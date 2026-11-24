---
id: 56b399d3-f39c-454f-8279-454afdd25517
---

# Brooks' Algorithm 2: The 2019/20 Exam Question

This lesson runs Brooks' algorithm on the 2019/20 exam question and shows the resource limit more than doubling the project time.

## Before you start
<!-- bite: df833e9e-3a08-4bb6-8757-8b83810b5530 -->

You should have read [[planning-and-scheduling/30-brooks-algorithm-1|30 — Brooks' Algorithm 1]] and [[planning-and-scheduling/29-priority-rules-2|29 — Priority Rules 2]].

After this lesson you will be able to:

1. schedule a two-resource project with Brooks' algorithm;
2. compare the result with the unconstrained CPM time;
3. explain which task causes the delay and why.

## What we're scheduling
<!-- bite: 7c6ea725-92c3-45fc-8562-93dfb5b106f2 -->

Here are the eight tasks again, now with what matters for scheduling: duration (weeks), predecessors, staff needed (Type 1, Type 2), and the priority from lesson 29. Available: **Type 1 = 8, Type 2 = 10**.

| Task | t | After | Needs (T1, T2) | Scaled CAF |
| --- | --- | --- | --- | --- |
| A | 5.83 | - | 4, 5 | 48.1 |
| B | 4.33 | - | 6, 3 | 62.3 |
| C | 3.00 | A | 4, 5 | 68.6 |
| D | 2.17 | B | 5, 4 | 100.0 |
| E | 2.83 | B | 3, 5 | 71.2 |
| F | 10.33 | - | 6, 6 | 53.4 |
| G | 3.00 | E, F | 5, 4 | 58.4 |
| H | 2.17 | C, D | 5, 4 | 100.0 |

## The first three steps
<!-- bite: 989a060c-9f32-4a92-a081-d3550d5f1fd0 -->

**TNOW = 0.** Ready: A, B, F. In priority order: B (62.3), F (53.4), A (48.1). Free: (8, 10).
1. B needs (6, 3): fits. Start B, 0 to 4.33. Free: (2, 7).
2. F needs (6, 6): only 2 Type 1 left. Hold.
3. A needs (4, 5): only 2 Type 1 left. Hold.

**TNOW = 4.33** (B finishes). Free: (8, 10). Ready: D, E, F, A.
1. D (100) needs (5, 4): fits. Start D, 4.33 to 6.50. Free: (3, 6).
2. E (71.2) needs (3, 5): fits. Start E, 4.33 to 7.17. Free: (0, 1).
3. F and A: no Type 1 left. Hold.

**TNOW = 6.50** (D finishes). Free: (5, 5). Ready: F, A.
1. F needs 6 Type 1: hold.
2. A needs (4, 5): fits. Start A, 6.50 to 12.33. Free: (1, 0).

## The rest of the run
<!-- bite: 92cf8a87-1c96-4672-b1a6-2c6640523c67 -->

**TNOW = 7.17** (E finishes). Free: (4, 5). F needs 6 Type 1: hold.

**TNOW = 12.33** (A finishes). Free: (8, 10). Ready: C, F. C (68.6) needs (4, 5): start C, 12.33 to 15.33. Free: (4, 5). F: hold.

**TNOW = 15.33** (C finishes). Free: (8, 10). Ready: H, F. H (100) needs (5, 4): start H, 15.33 to 17.50. Free: (3, 6). F: hold.

**TNOW = 17.50** (H finishes). Free: (8, 10). F finally fits: start F, 17.50 to 27.83.

**TNOW = 27.83** (F finishes). G is ready (E and F done): start G, 27.83 to 30.83.

## The final schedule
<!-- bite: 5ee4451c-1da5-403a-bf2b-c8e2be9d00c0 -->

| Task | Start | Finish |
| --- | --- | --- |
| B | 0 | 4.33 |
| D | 4.33 | 6.50 |
| E | 4.33 | 7.17 |
| A | 6.50 | 12.33 |
| C | 12.33 | 15.33 |
| H | 15.33 | 17.50 |
| F | 17.50 | 27.83 |
| G | 27.83 | 30.83 |

The project takes **30.83 weeks** with the staff limits.

## Seeing where the time went
<!-- bite: 4f21d9a9-2037-45a6-b6a9-9a7ba54dc609 -->

![A bar chart of the resource-constrained 2019/20 schedule from week 0 to about 31: B 0 to 4.33, D 4.33 to 6.5, E 4.33 to 7.17, A 6.5 to 12.33, C 12.33 to 15.33, H 15.33 to 17.5, F 17.5 to 27.83 and G 27.83 to 30.83, with a marker at 13.33 weeks for the unconstrained finish](images/ps-brooks-2019.svg)

Without resource limits the same network needs only **13.33 weeks**: the longest path is F-G = 10.33 + 3. The limit costs about **17.5 weeks**.

The culprit is F. It is long (10.33 weeks) and hungry (6 Type 1 and 6 Type 2), so it can't run alongside anything that needs more than 2 Type 1 staff. Every time the clock stops, something else of higher priority, or smaller, fits first. F ends up at the very end, and G waits behind it. In the exam, saying *why* the time grew earns the last marks.

## The 2020/21 version
<!-- bite: ddb5547e-a08a-4891-890d-e8e410b50eb9 -->

The 2020/21 paper (Question 4) asks the same thing with w = 0.4 and limits of 10 and 12. Its marking scheme's table ends at 31.34 weeks; running the algorithm with the question's own figures gives 29.33 weeks. The scheme gives activity S a Type 1 need of 7 where the question says 0, which probably explains the gap. Use the lecturer's layout, and if your figure differs, say why. Either way the conclusion is the one the scheme wants: **limiting resources doesn't shorten a project; it usually lengthens it**, because activities have to wait for each other.

## Common pitfalls
<!-- bite: d56586df-ea3f-4014-9ad4-e722952c1e13 -->

1. **Releasing resources at the wrong time.** D releases at 6.50, E at 7.17: handle them as separate clock stops.
2. **Letting F start at 17.50 alongside nothing.** Check it really fits: (6, 6) against (8, 10), yes.
3. **Forgetting G needs both E and F.** E was done long before; G waits for F.

## Check your understanding
<!-- bite: a363da56-d4e2-45de-8f09-db404ef3edb4 -->

Try each one before you open the answer.

1. <!-- q: exact id="8c2f5a07" answer="5" -->
   Two resources, limits (8, 10). Running: D needs (5, 4) and E needs (3, 5). D finishes first. How many Type 1 staff are free right after D finishes?

   <details><summary>Answer</summary>

   5. While both ran, Type 1 free was 8 − 5 − 3 = 0. D releases its 5.

   </details>

2. <!-- q: exact id="3b97e4d1" answer="17.5" accept="17.50" -->
   A project takes 13.33 weeks without resource limits and 30.83 weeks with them. How many weeks does the resource limit cost?

   <details><summary>Answer</summary>

   17.5 weeks: 30.83 − 13.33.

   </details>

3. <!-- q: mcq id="e06d1c58" -->
   A long task needs 6 of the 8 available Type 1 staff. What usually happens to it under Brooks' algorithm?

   - [ ] It always starts first
   - [x] It keeps getting held back, because almost anything else running leaves too few Type 1 staff
   - [ ] It is split into smaller tasks
   - [ ] Its priority is raised automatically

   <details><summary>Answer</summary>

   It can only start when almost nothing else is using Type 1 staff, so smaller or higher-priority tasks keep fitting first.

   </details>

4. <!-- q: open id="5f1a9b3c" -->
   State the general conclusion about resource-constrained scheduling that the 2019/20 and 2020/21 results both show.

   <details><summary>Answer</summary>

   Limiting resources never shortens a project and usually lengthens it, because activities that could run in parallel by logic must wait for each other to free the resources they share. The CPM duration is a lower bound; the resource-constrained schedule is the realistic one.

   </details>

## Before moving on
<!-- bite: 97b9aa29-fe9e-46b0-989e-15f2447678ac -->

You can run Brooks' algorithm on a two-resource exam question and explain the delay. **Next:** [[planning-and-scheduling/32-project-scoring-models|32 — Project Scoring Models]].

## Related
<!-- bite: ac6ebfb1-6501-4c47-a671-b10cb03024ed -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 2685949e-ab41-4d4f-8b13-f5e9dd656e33 -->

**Level:** Advanced. **Covers:** the 2019/20 Brooks question run in full, the unconstrained comparison, and the 2020/21 version's discrepancy.

**Where it sits:** lesson 31 of 35, in part 7 (resources). Part 7 of 7 on resources; part 2 of 2 on Brooks' algorithm.

**Source:** the author's own SSG 513 study notes, sections 7 and 9.4. The schedule is rerun in `scripts/diagrams/planning_scheduling.py`, which also draws the chart.
