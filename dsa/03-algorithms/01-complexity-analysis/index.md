# Complexity Analysis

**The measuring system.** Every other note in this course is written in the vocabulary this folder establishes, which is why it is numbered `01` and why it should be read second, immediately after [[01-loops-and-what-they-cost|loops and what they cost]].

> **The one idea:** you are never measuring *how long* an algorithm takes — that depends on the machine, the language, the compiler and what else is running. You are measuring **how the time changes when the input grows**. That number is a property of the algorithm itself, it survives being moved to different hardware, and it is the only one worth arguing about.

## Why this is a folder and not one note

Two genuinely different questions hide under the word "complexity", and conflating them is where most confusion comes from:

1. **How does the cost of one operation grow with input size?** — asymptotic notation, $O$, $\Omega$, $\Theta$, best/average/worst case. Lesson 01.
2. **How do I cost a *sequence* of operations when individual ones vary wildly?** — amortised analysis: the aggregate, accounting and potential methods. Lesson 02.

The second is the one that gets skipped, and it is the one interviews reach for when they want to go past "what is $O(n)$?". A dynamic array append is $O(n)$ in the worst case and $O(1)$ amortised, and being able to say *why*, with a method rather than a hand-wave, is a different skill from reading a nested loop.

**The third question — "how do I get a growth rate when the algorithm calls itself?" — is recurrences, and it lives next door in [[02-recursion/index|02-recursion]]**, because you cannot read a recursion tree before you understand recursion. Read this folder, then that one.

## The lessons

1. [[01-growth-and-asymptotic-notation|Growth and Asymptotic Notation]] — **[Beginner → Intermediate]** — what an algorithm is; growth rate instead of wall-clock time; $O$, $\Omega$ and $\Theta$ and why they are not interchangeable; best, average and worst case as a *separate axis* from the notation; space complexity including the call stack; reading a constraint to guess the intended complexity.
2. [[02-amortized-analysis|Amortised Analysis]] — **[Intermediate → Advanced]** — the aggregate, accounting and potential methods, each applied to the same structure; **why amortised is not average-case**, and why a hash map gets one and a dynamic array gets the other; the catalogue — array append, multipop, two-stack queue, binary counter, union-find; and **the drill of turning a table of operation costs into an amortised cost**.

## Question banks

One bank per lesson: micro-questions with the answers hidden behind toggles, for closed-book recall rather than reading. Method explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

- [[01-growth-and-asymptotic-notation-qb|Growth & Asymptotic Notation]]
- [[02-amortized-analysis-qb|Amortized Analysis]]

---

## Related

- [[01-loops-and-what-they-cost|Loops and What They Cost]] — the on-ramp: counting iterations before naming the growth
- [[03-algorithms/index|03-algorithms]] — the parent folder
- [[02-dynamic-arrays|Dynamic Arrays]] — where amortised analysis first earns its keep
- [[10-union-find|Union-Find]] — the $O(\alpha(n))$ result that only amortised analysis can prove
- [[02-recursion/index|Recursion]] — recurrences and the Master Theorem, the third question
- [[05-induction-and-recursion|Discrete maths: induction and recursion]] — the proof machinery behind the Master Theorem
