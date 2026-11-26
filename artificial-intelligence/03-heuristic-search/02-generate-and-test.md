---
id: 599fc080-1dce-40a0-b4e7-bc9ef059fdb8
---

# Generate and Test

Generate and test is the simplest search method: generate a possible solution, test whether it really is a solution, and if not, generate another.

## Before you start
<!-- bite: 7edfa783-75a8-4035-87fc-1a4d09423c2d -->

Read [[artificial-intelligence/03-heuristic-search/01-heuristics-and-heuristic-search|Heuristics and Heuristic Search]] first.

After this lesson you will be able to:

1. write the three steps of the generate-and-test algorithm from your class notes;
2. run generate-and-test by hand on a small problem and count the tests;
3. explain why the generator decides whether the method is blind or heuristic;
4. say how hill climbing grows out of generate-and-test.

## What generate and test is
<!-- bite: a69dabd8-c1a2-4f54-b270-8efbd5e74800 -->

Your notes put generate-and-test in the heuristic search lecture, and give it as three steps:

1. **Generate** a possible solution. This can be either a point in the problem space or a path from the initial state.
2. **Test** whether the possible solution is a real solution, by comparing the state reached with the set of goal states.
3. **If it's a real solution, return it.** Otherwise, repeat from generate.

That's the whole algorithm. It's how you'd open a combination padlock if you'd forgotten the code: try a number, pull the shackle, try the next number.

## The kid version
<!-- bite: 47a24900-5103-4e46-ba78-49b94daef9ae -->

You've lost the cap of your pen and you have a box of twenty caps. You pick one up, try it on the pen. Doesn't fit? Put it aside and pick up the next. Eventually one clicks on. That's generate (pick a cap) and test (does it fit?). If you're clever, you try the blue caps first, because your pen is blue. That's a heuristic generator.

**Where the analogy stops working.** A box of twenty caps is small. Many real problems have millions or billions of possible solutions, so trying them one by one in any order can take longer than you have. How cleverly you generate decides whether the method is usable at all.

## Trying it by hand
<!-- bite: 1f7b1427-84c0-4995-9584-3278756b1c8c -->

Here's a small problem. Find a two-digit number whose digits add up to 10 and multiply to 21.

**Generate** the numbers in order: 10, 11, 12, … **Test** each one: do the digits sum to 10 and multiply to 21?

1. 10: 1 + 0 = 1. No.
2. 11: 1 + 1 = 2. No.
3. …
4. 19: 1 + 9 = 10, but 1 × 9 = 9. No.
5. 28: 2 + 8 = 10, but 2 × 8 = 16. No.
6. 37: 3 + 7 = 10, and 3 × 7 = 21. **Yes!** Return 37.

Counting from 10 to 37 is 28 tests. (73 also works, but we stop at the first solution.)

## A smarter generator
<!-- bite: bf6217fb-4e15-4b4c-ae1a-3f4d05d71740 -->

Now use a little knowledge. The digits must add up to 10, so the second digit is always 10 minus the first. Generate only numbers like that: 19, 28, 37, … Now you test 19, 28, then 37: three tests instead of 28.

Nothing changed in the test. Only the generator got smarter. That's the main lesson of generate-and-test:

1. **An exhaustive generator** tries every possibility in a fixed order. It's a blind, brute-force search, and it will always find a solution if one exists, given enough time.
2. **A heuristic generator** uses knowledge of the problem to try the likely candidates first, or to skip ones that can't work. It's much faster, but if the knowledge is wrong it might skip the answer.

## Where generate-and-test fits
<!-- bite: f4d5cc47-228d-48e4-8fd4-bb3e58c27d48 -->

Generate-and-test works best when:

1. **The test is cheap** and easy to check, like "do the digits sum to 10?".
2. **The space is small**, or the generator is smart enough to cut it down.

It works badly on big problems with a blind generator. The 8-puzzle has 181,440 arrangements; trying them in order would be hopeless.

## From generate-and-test to hill climbing
<!-- bite: 0e15285c-e2bf-405a-aeb9-b42fe49eb7f2 -->

Plain generate-and-test only learns "yes" or "no" from each test. Suppose the test also said how *close* the guess was, like "warmer" or "colder". Then you could use that to decide what to generate next: change the guess in the direction that made it better.

That's **hill climbing**, lesson 07. It's generate-and-test where the test gives feedback, and the generator uses that feedback to choose the next guess.

## Terms used in this lesson
<!-- bite: 6e9a4361-ac61-4278-9497-6be129d16594 -->

1. **Generate and test**: This is a search method that repeatedly generates a possible solution and tests whether it is a real solution, stopping at the first one that passes.
2. **Generator**: This is the part that produces candidate solutions. It can be exhaustive (every candidate in order) or heuristic (likely candidates first).
3. **Exhaustive search**: This is also known as **brute-force search**. It tries every possibility.

## Common pitfalls and traps
<!-- bite: a9249f6e-0910-4d6f-8cb7-c3fca78c01df -->

- **Thinking generate-and-test is always blind.** With an exhaustive generator it is; with a heuristic generator it isn't. The generator decides.
- **Forgetting it can generate paths, not only states.** Your notes say a candidate can be a point in the problem space *or* a path from the initial state, such as a whole route to test against the goal.
- **Using it on a huge space with a blind generator.** It's complete in theory but too slow in practice.

## Check your understanding
<!-- bite: e2197e43-1e0b-4efb-a178-9e0cb368b011 -->

Try each one before you open the answer.

1. <!-- q: mcq id="3f567908" -->
   Put the steps of generate-and-test in order.

   - [x] Generate a candidate; test it against the goal states; return it if it passes, otherwise repeat
   - [ ] Test all candidates; generate the best one; return it
   - [ ] Generate every candidate first; then test them all at the end
   - [ ] Test the goal state; generate its predecessors; repeat

   <details><summary>Answer</summary>

   Generate one candidate, test it, and either return it or go back to generate.

   </details>

2. <!-- q: exact id="27c7e2f2" answer="15" -->
   You generate two-digit numbers in order from 10 upward, testing whether the digits multiply to 8 and add up to 6. How many tests do you make before finding the first solution, counting the successful test?

   <details><summary>Answer</summary>

   15. The first number whose digits add to 6 and multiply to 8 is 24 (2 + 4 = 6, 2 × 4 = 8). From 10 to 24 is 15 numbers.

   </details>

3. <!-- q: gap id="9d66a7f8" answers="generator|generate step;heuristic" -->
   Generate-and-test is blind or informed depending on its ___. If it uses knowledge to try likely candidates first, it is a ___ method.

   <details><summary>Answer</summary>

   The generator. With knowledge of the problem, it becomes a heuristic method.

   </details>

4. <!-- q: open id="8e0e7a4e" -->
   Explain how hill climbing can be seen as a form of generate-and-test.

   <details><summary>Answer</summary>

   In plain generate-and-test, the test only says yes or no. In hill climbing, the test also measures how good the candidate is, and the generator uses that measure to choose the next candidate, a small change in the direction that improves it. So it's generate-and-test with feedback guiding the generator.

   </details>

## Before moving on
<!-- bite: a26b68a0-b862-45a2-bac5-d4ea7dcb2df4 -->

You're done when you can write the three steps, run the method by hand and count the tests, and explain the difference between an exhaustive and a heuristic generator.

Recap: generate a candidate, test it against the goal, return it or repeat. With an exhaustive generator it's brute force; with a heuristic generator it's far faster. It suits small spaces with cheap tests. Hill climbing is generate-and-test with feedback.

Next, [[artificial-intelligence/03-heuristic-search/03-greedy-best-first-search|Greedy Best-First Search]] puts the heuristic into the search loop: always expand whichever node looks closest to the goal.

## Related
<!-- bite: 8045ffa4-a037-4d1b-8bea-e1001393e0d7 -->

- [[artificial-intelligence/03-heuristic-search/07-hill-climbing-1|Hill Climbing]]: generate-and-test with feedback.

## About this lesson
<!-- bite: 2a0041aa-f4b7-46db-a433-6fb7014953d4 -->

**Level:** introductory. Lesson 2 of section 03 (heuristic search). It covers the generate-and-test algorithm, a worked example, exhaustive versus heuristic generators, and the link to hill climbing.

**Source:** University of Lagos SSG 518 class notes, *Generate and Test Algorithm* (10/02/26). The digit example and its test counts are computed and asserted by `scripts/diagrams/ai_heuristic.py`.
