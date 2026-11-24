---
id: 5b3de2cb-bac0-4447-83ef-41a0b8d6420f
---

# Critical Path Method 4: A Past-Paper Network From Start to Finish

This lesson solves one full past-paper network question the way an exam answer should be laid out: the diagram, the paths, both passes, the table and the critical path.

## Before you start
<!-- bite: 63958285-50d5-4cd8-a64b-d2aa0f747d13 -->

You should have read [[planning-and-scheduling/14-critical-path-method-2|14 — Critical Path Method 2]].

After this lesson you will be able to:

1. lay out a full CPM answer in the order examiners expect;
2. check your answer three ways;
3. solve a new network of ten activities without help.

## What this lesson does
<!-- bite: 471d141f-6139-4bec-b35b-40db0ed81d23 -->

You have the pieces: draw the network (lesson 08), forward pass (13), backward pass and float (14). In the exam they come as one question worth 10 to 15 marks, and the marks are spread over the diagram, the times table, the critical path and the duration. A good layout makes sure you collect every one.

## The question
<!-- bite: 0065b34c-92e8-445f-a534-42ee64362c61 -->

This is the network you'll solve, step by step.

The question is 2024/25 Question 4b, a software development project, in weeks:

1. **A**: 3 weeks, no predecessor.
2. **B**: 5 weeks, no predecessor.
3. **C**: 7 weeks, no predecessor.
4. **D**: 8 weeks, after A.
5. **E**: 5 weeks, after B.
6. **F**: 5 weeks, after C.
7. **G**: 4 weeks, after E.
8. **H**: 5 weeks, after F.
9. **I**: 6 weeks, after D.
10. **J**: 4 weeks, after G and H.

## Step 1: draw the network
<!-- bite: a91fa512-c8cd-46b7-ae96-af39b916c018 -->

Three activities start the project, so they all hang off a Start node. I and J are the two activities nothing waits for, so both lead to End.

![The software project as an activity-on-node diagram: Start leads to A 3, B 5 and C 7; A leads to D 8 and then I 6; B leads to E 5 and then G 4; C leads to F 5 and then H 5; G and H both lead to J 4; I and J lead to End. The critical path C, F, H, J is drawn in orange](images/ps-software-network.svg)

## Step 2: list the paths
<!-- bite: 7e63e250-371f-4b09-a568-590e0f8d3f4d -->

This is a fast check that the passes will confirm. There are three ways through:

1. A-D-I = 3 + 8 + 6 = 17
2. B-E-G-J = 5 + 5 + 4 + 4 = 18
3. C-F-H-J = 7 + 5 + 5 + 4 = **21**

So expect a project time of **21 weeks**, along C-F-H-J. On a big network listing paths takes too long (the 2024/25 refinery has eight), but on ten activities it is quick and catches mistakes.

## Step 3: both passes in one table
<!-- bite: 682398af-500d-467c-a6b9-caa5c3373bad -->

Forward pass for ES and EF (take the maximum at a merge, such as J: max(G's 14, H's 17) = 17). Then backward pass for LF and LS from 21 (take the minimum).

| Task | t | After | ES | EF | LS | LF | Float |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 3 | - | 0 | 3 | 4 | 7 | 4 |
| B | 5 | - | 0 | 5 | 3 | 8 | 3 |
| C | 7 | - | 0 | 7 | 0 | 7 | 0 |
| D | 8 | A | 3 | 11 | 7 | 15 | 4 |
| E | 5 | B | 5 | 10 | 8 | 13 | 3 |
| F | 5 | C | 7 | 12 | 7 | 12 | 0 |
| G | 4 | E | 10 | 14 | 13 | 17 | 3 |
| H | 5 | F | 12 | 17 | 12 | 17 | 0 |
| I | 6 | D | 11 | 17 | 15 | 21 | 4 |
| J | 4 | G, H | 17 | 21 | 17 | 21 | 0 |

## Step 4: state the answer, then check it
<!-- bite: 1fa84298-8bdf-4595-b442-76ed82445d6c -->

Write the answer in a sentence: the project takes **21 weeks**, and the critical path is **C-F-H-J**.

Then check it three ways before moving on:

1. **The path list agrees.** C-F-H-J was the longest path at 21.
2. **Float is the same both ways.** For every row, LS − ES equals LF − EF. For D: 7 − 3 = 4 and 15 − 11 = 4.
3. **Floats along a side path make sense.** A, D and I all have float 4, because their path is 21 − 17 = 4 weeks short. B, E and G have 3, because theirs is 21 − 18 = 3 short.

The third check is worth knowing: on a simple side path, every activity's float equals how much shorter that path is than the critical one.

## How to lay out an exam answer
<!-- bite: 4396e6aa-d642-4d78-ab95-88811e9a7b26 -->

1. Draw the network, neat and labelled with durations.
2. If it's small, list the paths and their lengths.
3. Give one table with ES, EF, LS, LF and float.
4. State the duration and critical path in words.
5. If asked, mark the critical path on the diagram (a double line or a colour).

That completes deterministic CPM. Its weakness is the one number per activity: real durations are uncertain. Part 5 brings in PERT, which uses three numbers and answers a question CPM can't: what is the chance we finish on time?

## Common pitfalls
<!-- bite: a341078b-6e47-4771-8ef7-0240f682fbdb -->

1. **Forgetting a Start or End node** when several activities start or finish the project.
2. **Rounding or skipping the table.** The table carries most of the marks.
3. **Stating the duration without the path**, or the path without the duration. Both are asked.

## Check your understanding
<!-- bite: b1ea15cc-81cf-4aaf-9e89-4e22257c2c32 -->

Try each one before you open the answer.

1. <!-- q: exact id="4b1c8e37" answer="16" -->
   A project in days: K 4 (no predecessor), L 6 (no predecessor), M 5 (after K), N 3 (after L), O 7 (after M and N), P 2 (after N). How long does it take?

   <details><summary>Answer</summary>

   16 days. Paths: K-M-O = 16, L-N-O = 16, L-N-P = 11. Two paths tie at 16, so both are critical.

   </details>

2. <!-- q: exact id="e7a20f5c" answer="5" -->
   A project in days: K 4 (no predecessor), L 6 (no predecessor), M 5 (after K), N 3 (after L), O 7 (after M and N), P 2 (after N). What is P's float?

   <details><summary>Answer</summary>

   5. P's path L-N-P is 11 days, 16 − 11 = 5 short. Check: P's ES = 9, LF = 16, LS = 14, float = 14 − 9 = 5.

   </details>

3. <!-- q: mcq id="0d6e93a1" -->
   A network's paths are 22, 25, 19 and 25 days long. Which is true?

   - [ ] The project takes 22 days
   - [ ] The project takes 91 days
   - [x] The project takes 25 days and has two critical paths
   - [ ] There is no critical path because two paths tie

   <details><summary>Answer</summary>

   The longest path sets the duration, and both 25-day paths are critical. A network can have more than one critical path.

   </details>

4. <!-- q: open id="8f4b2d96" -->
   On a simple side path that joins the critical path only at the end, every activity has a float of 4. What does that tell you about the path's length?

   <details><summary>Answer</summary>

   The path is 4 time units shorter than the critical path. On a side path like that, each activity's total float equals the gap between the critical path's length and the side path's length, and the activities share it: using it on one uses it up for the others.

   </details>

## Before moving on
<!-- bite: 8a35f7aa-f7ac-45e2-a19b-885242644a42 -->

You can solve and check a full network question. **Next:** [[planning-and-scheduling/17-pert-1|17 — PERT 1: The Three-Point Estimate]].

## Related
<!-- bite: 2b4ad80a-72f2-45b5-bb11-52d6b598b1ad -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[planning-and-scheduling/ssg-513-question-bank|SSG 513 question bank]]: the Laralek, Craneburg, refinery and large construction networks to practise on.

## About this lesson
<!-- bite: 8cd154f3-f9d6-4ce1-befc-2b24b6dcca03 -->

**Level:** Intermediate. **Covers:** a full CPM answer for 2024/25 Question 4b, three checks, and the exam layout.

**Where it sits:** lesson 16 of 35, in part 4 (the critical path method). Part 4 of 4 on CPM.

**Source:** the author's own SSG 513 study notes, section 9.2. The diagram comes from `scripts/diagrams/planning_scheduling.py`, which also checks the table.
