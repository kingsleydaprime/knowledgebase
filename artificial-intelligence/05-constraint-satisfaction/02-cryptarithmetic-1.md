---
id: 28352167-6de5-4413-a54d-bf3a27cba8a2
---

# Cryptarithmetic 1: The Rules and a Worked Sum

A cryptarithmetic puzzle is a sum written in letters, where each letter stands for a different digit, and you solve it as a constraint satisfaction problem, column by column.

## Before you start
<!-- bite: d4d82237-5554-4dab-af48-91abfc992501 -->

Read [[artificial-intelligence/05-constraint-satisfaction/01-constraint-satisfaction-problems|Constraint Satisfaction Problems]] first. You need variables, domains, constraints and backtracking. You should be comfortable with column addition and carries.

After this lesson you will be able to:

1. state the rules of cryptarithmetic;
2. formulate a cryptarithmetic puzzle as a CSP, including the carries;
3. solve `SEND + MORE = MONEY` by reasoning about each column, backtracking where a guess fails;
4. explain why reasoning beats trying every assignment.

## What cryptarithmetic is
<!-- bite: 21393a86-4b72-44f4-a0a6-573ebc6edc23 -->

Here's a famous one:

```
    S E N D
  + M O R E
  ---------
  M O N E Y
```

Each letter stands for one digit, different letters stand for different digits, and the sum has to work. Your SSG 503 notes say cryptarithmetic is used to test people's analytical skill. In AI it's a classic constraint satisfaction problem, and the SSG 503 exams ask one almost every year.

## The kid version
<!-- bite: df27393f-05d6-4e25-8ed9-584bccd4f7c7 -->

Imagine a secret code where every letter hides a digit, and someone has written a sum in code. You can't see the numbers, but you know the sum adds up. So you play detective: "the answer has one more digit than the numbers being added, so the first letter must be a carried 1". Each clue rules things out, until only one answer is left.

**Where the analogy stops working.** A detective follows hunches. Cryptarithmetic needs care: a guess must be followed to the end, and if it leads to a contradiction, you go back and try the next possibility. That's backtracking.

## The rules
<!-- bite: dd85ef4d-090f-4220-8773-4cef0432b91e -->

Your SSG 503 notes list them:

1. Digits range from **0 to 9** only.
2. Each letter has a **unique value**: different letters, different digits.
3. Each letter stands for **only one digit** throughout the problem.
4. You need to find the value of **every letter**.
5. The number base is **10** unless stated otherwise.
6. Numbers **must not begin with 0**.
7. After replacing the letters with digits, **normal arithmetic must hold**.

## Cryptarithmetic as a CSP
<!-- bite: 828ec884-936a-4d78-8cde-583a79a04850 -->

1. **Variables**: the letters S, E, N, D, M, O, R, Y. We also add the **carries** $c_1, c_2, c_3, c_4$ out of each column, counting from the right.
2. **Domains**: each letter takes 0 to 9 (leading letters S and M take 1 to 9); each carry takes 0 or 1 (two digits plus a carry can't reach 20).
3. **Constraints**: all the letters are different, and each column adds up. Number the columns from the right:
   1. Column 1: D + E = Y + 10$c_1$
   2. Column 2: N + R + $c_1$ = E + 10$c_2$
   3. Column 3: E + O + $c_2$ = N + 10$c_3$
   4. Column 4: S + M + $c_3$ = O + 10$c_4$
   5. Column 5: $c_4$ = M

Trying every assignment blindly means placing 8 letters among 10 digits: 1,814,400 possibilities. Reasoning column by column cuts that to a handful.

## Steps 1 and 2: the left-hand columns
<!-- bite: d22aa552-9fca-4843-8fbe-9937131973b3 -->

**Step 1: M.** `MONEY` has five digits, and `SEND` and `MORE` have four. The fifth digit can only come from a carry, so **M = 1**.

**Step 2: S and O.** Column 4: S + M + $c_3$ = O + 10. With M = 1: S + 1 + $c_3$ = O + 10, so S + $c_3$ = O + 9. S is at most 9, so O is at most 1. M already has 1, so **O = 0**. Then S + $c_3$ = 9: either S = 9 with $c_3$ = 0, or S = 8 with $c_3$ = 1. Keep both possibilities for now.

## Step 3: N and E
<!-- bite: c44275ce-fd65-4e7d-9aef-df7ec0631a47 -->

Column 3: E + O + $c_2$ = N + 10$c_3$. With O = 0: E + $c_2$ = N + 10$c_3$.

1. If $c_3$ = 1, then E + $c_2$ = N + 10. The largest E + $c_2$ can be is 10 (E = 9, $c_2$ = 1), which would make N = 0, but O is already 0. Contradiction. So $c_3$ = 0, and from step 2, **S = 9**.
2. With $c_3$ = 0: E + $c_2$ = N. Since N ≠ E, $c_2$ must be 1, so **N = E + 1**.

## Step 4: R
<!-- bite: 27103c1a-9f16-463d-affd-9ff0fa3ca298 -->

Column 2: N + R + $c_1$ = E + 10$c_2$ = E + 10. Put in N = E + 1:

(E + 1) + R + $c_1$ = E + 10, so R + $c_1$ = 9.

If $c_1$ = 0, R = 9, but S is already 9. So $c_1$ = 1 and **R = 8**.

## Step 5: D, E and Y
<!-- bite: 8314b427-4522-4838-b00b-39a55d70a81d -->

Column 1: D + E = Y + 10$c_1$ = Y + 10. The digits left are 2, 3, 4, 5, 6 and 7 (0, 1, 8 and 9 are taken). Y is at least 2, so D + E is at least 12. Try values of E, remembering N = E + 1 must also be free:

1. **E = 2**, N = 3: D = Y + 8, so D is at least 10. Impossible.
2. **E = 3**, N = 4: D = Y + 7; with Y = 2, D = 9, taken. Fails.
3. **E = 4**, N = 5: D = Y + 6; Y = 2 gives D = 8 and Y = 3 gives D = 9, both taken. Fails.
4. **E = 5**, N = 6: D = Y + 5; Y = 2 gives **D = 7**. All free. ✓
5. **E = 6**, N = 7: D = Y + 4; Y = 2 gives D = 6 (that's E) and Y = 3 gives D = 7 (that's N). Fails.
6. **E = 7**, N = 8: 8 is R. Fails.

Only E = 5 works: **E = 5, N = 6, D = 7, Y = 2**.

## The answer
<!-- bite: f4333b8e-8e39-4ad5-b250-28725607ee73 -->

S = 9, E = 5, N = 6, D = 7, M = 1, O = 0, R = 8, Y = 2.

```
    9 5 6 7
  + 1 0 8 5
  ---------
  1 0 6 5 2
```

Check every column: 7 + 5 = 12 (Y = 2, carry 1); 6 + 8 + 1 = 15 (E = 5, carry 1); 5 + 0 + 1 = 6 (N = 6); 9 + 1 = 10 (O = 0, carry 1 = M). ✓ It's the only solution.

Notice the method. Each step picked the column with the fewest unknowns, used the carries to split into cases, and backtracked out of cases that hit a contradiction (S = 8, R = 9 and E = 2, 3, 4, 6, 7). That's backtracking search with constraint propagation, done by hand.

## Terms used in this lesson
<!-- bite: 13dda63b-971b-40e6-a5e3-b81f2f599139 -->

1. **Cryptarithmetic**: This is also known as a **cryptarithm** or **alphametic**. It's a sum written in letters, where each letter stands for a different digit.
2. **Carry**: This is the 1 passed from one column to the next when a column's sum is 10 or more. In a CSP formulation, each carry is a variable with domain {0, 1}.
3. **Leading letter**: This is the first letter of a number, which can't stand for 0.

## Common pitfalls and traps
<!-- bite: 4f4a79b6-1eef-4962-88cd-a2e5e7d57c26 -->

- **Forgetting the carries.** Every column equation needs its incoming carry. Most wrong answers come from a missing carry.
- **Giving two letters the same digit.** Check every new value against all the letters already placed.
- **Stopping at the first answer that fits one column.** Check every column before writing the answer.

## Check your understanding
<!-- bite: 03a4d6e7-f55d-4035-a41c-8109b23c2afb -->

Try each one before you open the answer.

1. <!-- q: mcq id="f3a32428" -->
   Which of these is **not** a rule of cryptarithmetic?

   - [ ] Each letter stands for one digit
   - [ ] Different letters stand for different digits
   - [ ] A number can't begin with 0
   - [x] Every letter must be odd

   <details><summary>Answer</summary>

   There's no rule that letters must be odd. The other three are rules from your notes.

   </details>

2. <!-- q: exact id="2d036739" answer="1" -->
   In `AB + CD = EFG`, where every letter is a different digit, what must E be?

   <details><summary>Answer</summary>

   1. The answer has one more digit than the numbers added, so its first digit is a carry, and two 2-digit numbers can't sum to more than 198.

   </details>

3. <!-- q: gap id="92dded24" answers="0;1" -->
   In a cryptarithmetic CSP, each carry variable has the domain {___, ___}.

   <details><summary>Answer</summary>

   {0, 1}. Two digits plus a carry is at most 9 + 9 + 1 = 19, so the carry out is never more than 1.

   </details>

4. <!-- q: exact id="63bd76d8" answer="2" -->
   Solve `TO + GO = OUT`. What digit is T?

   <details><summary>Answer</summary>

   2. O = 1 (the carry into the third column). Column 1: 1 + 1 = T + 10$c_1$, so T = 2, $c_1$ = 0. Column 2: T + G = U + 10, so 2 + G = U + 10. G = 8 gives U = 0 (G = 9 would give U = 1, but O is 1). So 21 + 81 = 102.

   </details>

5. <!-- q: open id="b7430c26" -->
   In `SEND + MORE = MONEY`, explain why $c_3$ (the carry out of the third column) must be 0.

   <details><summary>Answer</summary>

   Column 3 says E + O + $c_2$ = N + 10$c_3$, and O = 0. If $c_3$ were 1, E + $c_2$ would equal N + 10; the most E + $c_2$ can be is 9 + 1 = 10, which forces N = 0. But O is already 0, and different letters need different digits. So $c_3$ = 0.

   </details>

## Before moving on
<!-- bite: 3220f487-c911-4407-afeb-81df7a58e17e -->

You're done when you can state the rules, formulate a cryptarithm as a CSP with carries, and solve `SEND + MORE = MONEY` column by column, explaining each backtrack.

Recap: a cryptarithm is a CSP with the letters and carries as variables, digits 0–9 (and carries 0–1) as domains, and "all different" plus one equation per column as constraints. Start from the leftmost column (a carry out means the leading letter is 1), split into cases on the carries, and backtrack from contradictions. `SEND + MORE = MONEY` gives 9567 + 1085 = 10652.

Next, [[artificial-intelligence/05-constraint-satisfaction/03-cryptarithmetic-2|Cryptarithmetic 2]] solves the two puzzles the SSG 503 exams set, and shows how to draw the search tree without solving the puzzle.

## Related
<!-- bite: 2bb70a4c-496a-4bbd-a957-27225122e2ed -->

- [[artificial-intelligence/ssg-518-question-bank|SSG 518 question bank]]: every cryptarithm from the past papers.

## About this lesson
<!-- bite: e225301b-e9e6-4ca6-a193-d9e5f9518dd4 -->

**Level:** intermediate. Lesson 2 of section 05 (constraint satisfaction), part 1 of 2 on cryptarithmetic. It covers the rules, the CSP formulation with carries, and a full step-by-step solution of `SEND + MORE = MONEY`.

**Source:** University of Lagos SSG 503 class notes (the rules of cryptarithmetic and the `SEND + MORE = MONEY` example) and the SSG 503 past papers. The solution's uniqueness, the 1,814,400 blind assignments and the quiz answer are checked by `scripts/diagrams/ai_gaps.py`.
