---
id: c663eb58-0e2a-4eb3-a0f7-0c1b476fa3bf
---

# Crashing 2: The Crashing Algorithm

The crashing algorithm shortens a project one day at a time, always buying the cheapest day on the critical path.

## Before you start
<!-- bite: cbcad4fd-c0be-47c9-8e2f-f123e706e0f5 -->

You should have read [[planning-and-scheduling/22-crashing-1|22 — Crashing 1]].

After this lesson you will be able to:

1. follow the six steps of the crashing algorithm;
2. handle the moment a second path becomes critical;
3. find the normal cost, the cost slopes and the cheapest duration for a small table.

## What the algorithm does
<!-- bite: a467289d-5dad-47d0-af6a-72ca74d99133 -->

Lesson 22 gave two rules: crash only critical activities, and only while the slope is below the daily overhead. The algorithm is those rules in order, applied one day at a time, because each day you cut can change which path is critical.

## The six steps
<!-- bite: d8ef56bb-e559-420c-ab97-5c995920c4b2 -->

1. **Draw the network** and find the normal critical path and duration.
2. **Compute the cost slope** of every activity that can still be crashed (one with Tn = Tc can't).
3. **Among the critical activities, crash the one with the lowest slope** by one day.
4. **Recompute all path lengths.** If two or more paths are now critical, the next day must come off all of them: crash one activity on each, or one activity they share.
5. **Stop** when the cheapest available day costs more than the indirect cost saved, or when no critical activity can be crashed any more.
6. **Total cost = direct cost + indirect cost per day × duration.** Compare it at each duration to find the minimum.

Step 4 is the one people miss. Once two paths tie, shortening only one of them saves nothing, because the other still sets the finish.

## The worked table
<!-- bite: 23d8e58a-8551-40ea-b5fb-6b2c8f7fcd20 -->

This table appears in 2019/20, 2023/24 and 2024/25. Four activities: A starts, B and C follow A, D follows C. The 2023/24 and 2024/25 numbers:

| Activity | After | Tn | Tc | Cn (N) | Cc (N) | Slope (N/day) |
| --- | --- | --- | --- | --- | --- | --- |
| A | - | 4 | 2 | 4,000 | 14,000 | 5,000 |
| B | A | 8 | 5 | 1,000 | 11,000 | 3,333 |
| C | A | 5 | 4 | 4,000 | 18,000 | 14,000 |
| D | C | 5 | 3 | 2,000 | 13,000 | 5,500 |

Check B's slope: (11,000 − 1,000) / (8 − 5) = 10,000 / 3 = 3,333.

## Normal duration and normal cost
<!-- bite: e77e874f-8558-405b-9b76-b311d9fe812d -->

The two paths are A-B = 4 + 8 = 12 days and A-C-D = 4 + 5 + 5 = **14 days**. So the normal duration is **14 days**, critical path A-C-D.

The normal direct cost is the sum of the normal costs: 4,000 + 1,000 + 4,000 + 2,000 = **N11,000**. With a fixed cost of N3,500 per day, the normal total cost is 11,000 + 3,500 × 14 = **N60,000**.

## Should we crash it?
<!-- bite: 6d55e211-e948-4229-a61a-d005a47b2f38 -->

Run step 3. The critical activities are A, C and D, with slopes 5,000, 14,000 and 5,500. The cheapest is A at N5,000 a day. But a day of overhead saves only N3,500. Every critical day costs more than it saves, so **crashing never pays here**: the cheapest plan is the normal 14 days at N60,000.

B has the cheapest slope of all (3,333), and it would pay, but B isn't critical. Crashing it would only add float to A-B.

If the owner insisted on 13 days anyway, you'd crash A by one day (the cheapest critical), and the total would be 60,000 + 5,000 − 3,500 = N61,500.

## The 2019/20 version: crashing pays
<!-- bite: eb0f0897-a0ad-45ba-ab98-3e55d0006f73 -->

The 2019/20 paper uses the same four activities with different numbers: A 3 to 1, B 7 to 3, C 4 to 2, D 5 to 2, the same normal and crash costs, and a fixed cost of **N4,500** per day.

1. **Slopes**: A 10,000/2 = 5,000; B 10,000/4 = 2,500; C 14,000/2 = 7,000; D 11,000/3 = 3,667.
2. **Normal**: A-B = 10, A-C-D = **12 days**. Total = 11,000 + 4,500 × 12 = **N65,000**.
3. **Day 1**: the cheapest critical slope is D at 3,667, below 4,500. Crash D: 11 days, A-C-D = 11, A-B = 10. Total = 65,000 + 3,667 − 4,500 = N64,167.
4. **Day 2**: crash D again: 10 days, and now both paths are 10. Total = **N63,333**.
5. **Day 3**: both paths must shorten. The cheapest way is A (on both) at 5,000, above 4,500. **Stop.**

The cheapest plan is **10 days at N63,333**, N1,667 less than doing nothing. Same table shape, different overhead, opposite answer. That's why the comparison between slope and overhead is the heart of the method.

## Common pitfalls
<!-- bite: 36f519aa-eb97-4b70-a4f4-ef6775446bfd -->

1. **Crashing the cheapest activity overall instead of the cheapest critical one.** B in the first table is the trap.
2. **Forgetting to recheck the paths after each day.** Ties appear, and step 4 then changes the cost of a day.
3. **Stopping at the normal total cost when asked for the optimum.** Run the algorithm and show the total at each duration.

The next lesson runs the algorithm on a bigger network, where three paths end up tied, and builds the full cost table.

## Check your understanding
<!-- bite: 78c2197f-1b9b-48f0-a6d0-1edc138c39e1 -->

Try each one before you open the answer.

1. <!-- q: exact id="3c8e5a17" answer="6250" accept="6,250" -->
   X (5 days, N1,000; crash 3 days, N1,600) starts the project. Y (4 days, N500; crash 3 days, N700) and Z (6 days, N900; crash 4 days, N1,700) both follow X. Indirect cost is N350 per day. What is the normal total cost, in naira?

   <details><summary>Answer</summary>

   6,250. Normal duration is X-Z = 11 days (X-Y is 9). Direct cost 1,000 + 500 + 900 = 2,400. Total = 2,400 + 350 × 11 = 6,250.

   </details>

2. <!-- q: exact id="a1f704d9" answer="300" -->
   X (5 days, N1,000; crash 3 days, N1,600) starts the project. Y and Z both follow X; Z is on the critical path. What is X's cost slope, in naira per day?

   <details><summary>Answer</summary>

   300: (1,600 − 1,000) / (5 − 3).

   </details>

3. <!-- q: exact id="e0b9c362" answer="9" -->
   X (5 days, N1,000; crash 3 days, N1,600) starts the project. Y (4 days, N500; crash 3 days, N700) and Z (6 days, N900; crash 4 days, N1,700) both follow X. Indirect cost is N350 per day. What duration gives the lowest total cost?

   <details><summary>Answer</summary>

   9 days. Slopes: X 300, Y 200, Z 400. Critical path X-Z. Crash X (300 < 350) twice: 11 → 9 days, total 6,250 − 2 × 50 = 6,150. Next, only Z can shorten X-Z, at 400 > 350, so stop. (Y is never critical, so its cheap slope doesn't matter.)

   </details>

4. <!-- q: mcq id="7e2d5f80" -->
   After crashing, two paths are both critical at 15 days. You want 14 days. What must you do?

   - [ ] Crash the cheapest activity on either path by one day
   - [x] Shorten both paths by a day: one activity on each, or one activity they share, whichever is cheaper
   - [ ] Stop, because a tie can't be crashed
   - [ ] Crash a non-critical activity

   <details><summary>Answer</summary>

   Both paths must come down, or the other still sets 15 days. Compare the cost of one shared activity against the sum of one on each.

   </details>

5. <!-- q: open id="4b6c9e1f" -->
   In a crash table, the activity with the lowest cost slope of all is not on the critical path. Why shouldn't you crash it?

   <details><summary>Answer</summary>

   The project's duration is set by the critical path. Shortening a non-critical activity only increases its float; the project still takes as long as before, so the extra money buys nothing.

   </details>

## Before moving on
<!-- bite: 78a857b2-4917-4c45-8787-fc166afbf728 -->

You can run the algorithm, handle ties and find the cheapest duration. **Next:** [[planning-and-scheduling/24-crashing-3|24 — Crashing 3: A Software Project, Step by Step]].

## Related
<!-- bite: 245d1df2-9f4f-4512-bb8e-ea6f16f9320c -->

- [[planning-and-scheduling/index|Planning and scheduling map]]

## About this lesson
<!-- bite: 0692ba9b-3c92-4766-9c30-7cb7ba510cd1 -->

**Level:** Intermediate. **Covers:** the six-step algorithm, ties between paths, and the A to D crash table in both versions.

**Where it sits:** lesson 23 of 35, in part 6 (crashing). Part 2 of 3 on crashing.

**Source:** the author's own SSG 513 study notes, section 6. The full crashing run on the 2019/20 numbers (10 days, N63,333) is added for this lesson; the notes stop at the normal cost. Every figure is checked in `scripts/diagrams/planning_scheduling.py`.
