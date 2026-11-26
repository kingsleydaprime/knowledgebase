---
id: d4b5169f-c406-482d-ad83-d367c54dd2cc
---

# Cryptarithmetic 2: The Exam Puzzles and the Search Tree

The exams set cryptarithms two ways: solve one, or draw its search tree without solving it.

## Before you start
<!-- bite: 2aaac6a8-86bb-4251-9245-7d8fcf3efdeb -->

Read [[artificial-intelligence/05-constraint-satisfaction/02-cryptarithmetic-1|Cryptarithmetic 1]] first. You need the rules, the column equations and how to split cases on carries.

After this lesson you will be able to:

1. solve `BASE + BALL = GAMES` with a short chain of reasoning, including a parity argument;
2. draw the search tree for `RED + ROE = DEER`, explaining the basis for the branching at each level;
3. solve `CROSS + ROADS = DANGER` on your own.

## What this lesson covers
<!-- bite: 3e6308d9-1900-4188-a104-c19d95db855e -->

Cryptarithmetic 1 solved `SEND + MORE = MONEY`. The past papers ask for two more, and in two different styles:

1. **2019/20:** "Solve `BASE + BALL = GAMES`." (8 marks)
2. **2012/13, 2014/15, 2016/17:** "Without necessarily solving the problem, draw a search tree for the solution of `RED + ROE = DEER`, explaining in detail the basis for the branching at each level." (Part of a 22-mark question)

The second style is the one that surprises people. The examiner wants to see the *search*, not just the answer. The trick is knowing what to branch on.

## The kid version
<!-- bite: bba674b8-7c87-424b-a219-53176e134715 -->

Think of a "choose your own adventure" book. At each page you pick one of two paths. Some paths end quickly ("you fall in the river, the end"). One path goes all the way to the treasure. Drawing the search tree is drawing that book's map: every choice point, every dead end, and the one path that works.

**Where the analogy stops working.** In the book, the choices are given. In a cryptarithm, *you* decide what the choices are, and the smart choice is "is there a carry here or not?", which gives just two branches at each column.

## `BASE + BALL = GAMES`: setting up
<!-- bite: 13bbc072-156e-4aec-be52-33c1228f72db -->

```
    B A S E
  + B A L L
  ---------
  G A M E S
```

Number the columns 1 (units) to 5, with carries $c_1$ to $c_4$:

1. Column 1: E + L = S + 10$c_1$
2. Column 2: S + L + $c_1$ = E + 10$c_2$
3. Column 3: A + A + $c_2$ = M + 10$c_3$
4. Column 4: B + B + $c_3$ = A + 10$c_4$
5. Column 5: $c_4$ = G

**G = 1**, because `GAMES` has one more digit than the numbers added, and $c_4$ = 1. So column 4 is 2B + $c_3$ = A + 10.

## `BASE + BALL`: the units and tens
<!-- bite: 01982156-8ef2-4e0a-a3d2-e5145b86108b -->

Columns 1 and 2 share E, S and L, so combine them. From column 1, S = E + L − 10$c_1$. Put that into column 2:

(E + L − 10$c_1$) + L + $c_1$ = E + 10$c_2$, which simplifies to **2L − 9$c_1$ = 10$c_2$**.

Now a **parity** (odd or even) argument. The right side, 10$c_2$, is even. If $c_1$ = 1, the left side is 2L − 9, which is odd. An odd number can't equal an even one, so **$c_1$ = 0**. Then 2L = 10$c_2$:

1. $c_2$ = 0 gives L = 0. But then column 1 says S = E + 0 = E, and S ≠ E. Fails.
2. $c_2$ = 1 gives **L = 5**. Then column 1 gives **S = E + 5**.

## `BASE + BALL`: the hundreds and thousands
<!-- bite: a7d96d71-ea0d-45ed-bc31-ee599f82a40a -->

Now columns 3 and 4, with $c_2$ = 1: 2A + 1 = M + 10$c_3$, and 2B + $c_3$ = A + 10.

**Case $c_3$ = 0:** A = 2B − 10 and M = 2A + 1. B must be at least 5 so that A isn't negative.

1. B = 5 gives A = 0, M = 1, but G is 1. Fails.
1. B = 6 gives A = 2, M = 5, but L is 5. Fails.
2. **B = 7 gives A = 4, M = 9.** Keep it.
3. B = 8 gives A = 6, M = 13. Not a digit. Fails.
4. B = 9 gives A = 8, M = 17. Fails.

**Case $c_3$ = 1:** A = 2B − 9, and 2A + 1 = M + 10 needs A ≥ 5. B = 5 or 6 gives A = 1 or 3, too small; B = 7 gives A = 5 (that's L); B = 8 gives A = 7, M = 5 (that's L); B = 9 gives A = 9 (that's B). All fail.

So **B = 7, A = 4, M = 9**.

## `BASE + BALL`: the answer
<!-- bite: dbdf7abb-a0a4-4ae3-8670-98a0efd9d765 -->

Last, S = E + 5, using the digits still free: 0, 2, 3, 6, 8. E = 0 gives S = 5 (taken); E = 2 gives S = 7 (taken); **E = 3 gives S = 8**. ✓

B = 7, A = 4, S = 8, E = 3, L = 5, M = 9, G = 1.

```
    7 4 8 3
  + 7 4 5 5
  ---------
  1 4 9 3 8
```

Check: 3 + 5 = 8 (S); 8 + 5 = 13 (E = 3, carry 1); 4 + 4 + 1 = 9 (M); 7 + 7 = 14 (A = 4, carry 1 = G). ✓ It's the only solution.

## `RED + ROE = DEER`: what to branch on
<!-- bite: f0c9e801-afd3-4f08-a7b4-a68dd4c97000 -->

```
    R E D
  + R O E
  -------
  D E E R
```

The question says "without necessarily solving". So the examiner wants a tree whose levels are the **columns**, right to left, and whose two branches at each level are the possible **carries out** of that column: **no carry (c = 0)** and **carry (c = 1)**. That's the "basis for the branching at each level". At each node, write the column equation for that branch, and either the deduction it gives or the contradiction that kills it.

Start at the root with what's certain: `DEER` has one more digit than the addends, so **D = 1**.

## `RED + ROE = DEER`: the tree
<!-- bite: e61e7ae0-78e0-48b1-98fd-5ca03e61e765 -->

![The search tree for `RED` plus `ROE` equals `DEER`, branching on the carry out of each column: D is 1; the units column with a carry fails because R would be 0; with no carry R is E plus 1; the tens column with a carry fails because O would be 10; with no carry O is 0; the hundreds column then gives E equals 8 and R equals 9.](../images/gp-red-roe-tree.svg)

## Reading the tree level by level
<!-- bite: 18af4eb1-dc28-4cd7-a1b9-4f958e938b9a -->

Here's each level of that tree:

1. **Level 1, units:** D + E = R + 10$c_1$, that is 1 + E = R + 10$c_1$.
   1. $c_1$ = 1: 1 + E = R + 10, so E = 9 and R = 0. But R leads a number and can't be 0. **Dead end.**
   2. $c_1$ = 0: **R = E + 1**. Keep going.
2. **Level 2, tens:** E + O + $c_1$ = E + 10$c_2$, so O = 10$c_2$ (since $c_1$ = 0).
   1. $c_2$ = 1: O = 10, not a digit. **Dead end.**
   2. $c_2$ = 0: **O = 0**. Keep going.
3. **Level 3, hundreds:** R + R + $c_2$ = E + 10$c_3$, and $c_3$ must equal D = 1. So 2R = E + 10. With R = E + 1: 2E + 2 = E + 10, giving **E = 8, R = 9**.

**Answer:** R = 9, E = 8, D = 1, O = 0. Check: 981 + 908 = 1889. ✓

## Drawing it in the exam
<!-- bite: 8fa09561-e0df-4734-87cf-14f5fc298d49 -->

For full marks, in your drawing:

1. Put the whole puzzle, and the certain deduction (D = 1), in the root box.
2. Label each level with the column it handles.
3. Label each branch "no carry" or "carry" (or $c = 0$, $c = 1$).
4. Write each branch's equation and its result inside the box.
5. Mark dead ends clearly, with the reason ("R = 0 not allowed", "O = 10 not a digit").
6. Say in one sentence why you branch on carries: each column's sum depends only on its two digits and the carry coming in, so the carry is the one unknown that links the columns, and it can only be 0 or 1.

## Practice: `CROSS + ROADS = DANGER`
<!-- bite: b153fc70-760a-4f4d-a79f-6e1cdde63da6 -->

This one came up as an SSG 503 class assignment. Solve it yourself before opening the answer.

```
    C R O S S
  + R O A D S
  -----------
  D A N G E R
```

Hint: start from the left (what must D be?), then the units column (S + S).

<details><summary>Check your answer</summary>

D = 1 (the carry into the sixth column). The unique solution is C = 9, R = 6, O = 2, S = 3, A = 5, N = 8, G = 7, E = 4: 96233 + 62513 = 158746.

</details>

## Terms used in this lesson
<!-- bite: ef578d71-5443-4826-9a57-deee7a52c174 -->

1. **Parity**: This is whether a number is odd or even. A parity argument rules out a case because one side of an equation is odd and the other even.
2. **Branching on carries**: This means building the cryptarithm search tree one column per level, with two branches at each level: carry 0 and carry 1.

## Common pitfalls and traps
<!-- bite: ceacc419-32de-4ebb-9051-7085126ca8ac -->

- **Drawing a tree that branches on digits.** Branching on each possible digit gives up to 10 branches per level and a huge tree. Branch on carries: 2 per level.
- **Forgetting to explain the dead ends.** The marks are for the reasoning at each node, not only the final answer.
- **Skipping the check.** Always add the numbers back up at the end.

## Check your understanding
<!-- bite: 7092ef47-8e62-44a2-9cee-9bc45e70dc63 -->

Try each one before you open the answer.

1. <!-- q: exact id="92429a89" answer="7" -->
   In `BASE + BALL = GAMES`, what digit is B?

   <details><summary>Answer</summary>

   7. The solution is 7483 + 7455 = 14938.

   </details>

2. <!-- q: mcq id="7a16d86b" -->
   When drawing the search tree for a cryptarithm "without necessarily solving it", what should each level branch on?

   - [ ] Each possible digit (0 to 9) for one letter
   - [x] Whether the column produces a carry (0 or 1)
   - [ ] Each letter in alphabetical order
   - [ ] Whether the answer is odd or even

   <details><summary>Answer</summary>

   The carry out of each column. It's the one unknown linking each column to the next, and it can only be 0 or 1, so the tree branches two ways per level.

   </details>

3. <!-- q: open id="25d4e2c3" -->
   In `BASE + BALL = GAMES`, combining columns 1 and 2 gives 2L − 9$c_1$ = 10$c_2$. Explain why this forces $c_1$ = 0.

   <details><summary>Answer</summary>

   10$c_2$ is always even. If $c_1$ = 1, the left side is 2L − 9, which is odd for every L (2L is even, and even minus 9 is odd). An odd number can't equal an even number, so $c_1$ = 1 is impossible, and $c_1$ = 0.

   </details>

4. <!-- q: exact id="f07dbec7" answer="8" -->
   In `RED + ROE = DEER`, what digit is E?

   <details><summary>Answer</summary>

   8. The solution is 981 + 908 = 1889.

   </details>

## Before moving on
<!-- bite: dc5645f0-90d2-4b12-9038-09754089b7be -->

You're done when you can solve `BASE + BALL = GAMES` with the parity argument, draw and explain the `RED + ROE = DEER` search tree, and solve `CROSS + ROADS = DANGER` unaided.

Recap: `BASE + BALL = GAMES` is 7483 + 7455 = 14938, found by combining the first two columns and a parity argument, then splitting on one carry. For "draw a search tree", make one level per column, branch on the carry (0 or 1), and write each branch's equation and its result or contradiction. `RED + ROE = DEER` is 981 + 908 = 1889.

This section will grow with more constraint satisfaction methods. For now, test yourself with the cryptarithms in the [[artificial-intelligence/ssg-503-revision|SSG 503 revision questions]].

## Related
<!-- bite: 55b97b3d-1c3f-4e56-8a4e-152af0acd81b -->

- [[artificial-intelligence/05-constraint-satisfaction/01-constraint-satisfaction-problems|Constraint Satisfaction Problems]]: backtracking and forward checking in general.

## About this lesson
<!-- bite: 23e97ccb-b809-49db-a492-7f33f4cd2e4b -->

**Level:** intermediate. Lesson 3 of section 05 (constraint satisfaction), part 2 of 2 on cryptarithmetic. It covers solving `BASE + BALL = GAMES`, drawing the search tree for `RED + ROE = DEER`, and practice with `CROSS + ROADS = DANGER`.

**Source:** University of Lagos SSG 503 past papers (2019/20 question 3: `BASE + BALL`; 2012/13, 2014/15, 2016/17: `RED + ROE`) and the SSG 503 class notes (the `CROSS + ROADS` assignment). Every solution, and that each is the only one, is checked by brute force in `scripts/diagrams/ai_gaps.py`.
