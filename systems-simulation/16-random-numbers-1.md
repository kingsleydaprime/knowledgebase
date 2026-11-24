---
id: f46baa65-947b-4fa1-9e4c-74546ea4019d
---

# Random Numbers 1: What Makes a Number Random

Every random thing in a simulation starts from a stream of numbers between 0 and 1 that must be uniform and independent.

## Before you start
<!-- bite: 66e468ea-5339-4c2a-8254-283863ff8f5c -->

You should have read [[systems-simulation/15-the-mmc-queue|15 — The M/M/c Queue]].

After this lesson you will be able to:

1. state the two properties a random number sequence must have;
2. give the mean and variance of a uniform random number on [0, 1];
3. explain what pseudo-random means, how it can go wrong, and what a good generator needs.

## What a random number is
<!-- bite: 8ecd8381-96e0-4cb1-959f-dde70d9be313 -->

In a simulation, every random event, such as the gap between arrivals, a service time or a breakdown, starts as a **random number**: a value between 0 and 1. That number is then turned into whatever distribution you need (lesson 21).

So the whole simulation rests on these numbers. If they are biased or patterned, every queue and every Monte Carlo result inherits the problem. This lesson says what "random" means precisely. Lessons 17 and 18 then make the numbers, and lessons 19 and 20 test them.

## The two properties
<!-- bite: 0b6f052e-f527-4553-8019-41a8fc0514a5 -->

A sequence R1, R2, R3, ... must have:

1. **Uniformity:** each number is equally likely to fall anywhere in [0, 1].
2. **Independence:** knowing one number tells you nothing about the next.

A practical way to see uniformity: divide [0, 1] into n equal classes. With N numbers, each class should hold about N/n of them. Independence means the chance of landing in a class doesn't depend on where the previous numbers fell.

## Mean and variance of a uniform number
<!-- bite: f257a0dc-e8d6-4630-b9c5-24735b2de810 -->

For a continuous uniform variable R on [0, 1]:

$$E(R) = \frac{1}{2}, \qquad V(R) = \frac{1}{3} - \left(\frac{1}{2}\right)^2 = \frac{1}{12}$$

The mean is the middle of the interval. The variance comes from $E(R^2) - E(R)^2$: $E(R^2) = \int_0^1 x^2\,dx = 1/3$, and $(1/2)^2 = 1/4$, so the variance is 1/3 − 1/4 = 1/12 ≈ 0.0833.

These two numbers are a quick check on a generator. If a thousand of its outputs average 0.62, something is wrong.

## Pseudo-random numbers
<!-- bite: eda3de57-6864-47b8-8f54-ab118eba93d4 -->

A computer can't produce truly random numbers. It uses a known formula, so the numbers are called **pseudo-random**, "pseudo" meaning false. The goal is numbers that *behave as if* they were uniform and independent.

Ways pseudo-random numbers can depart from the ideal:

1. not uniformly distributed, or discrete (only a few possible values) instead of continuous;
2. a mean or variance too high or too low;
3. dependence: correlation between numbers, runs above or below the mean, or runs of high and low values.

## What a good generator needs
<!-- bite: fc03ce57-35d3-4780-9fa4-b10b64453c1c -->

1. **Fast:** a simulation may need millions of numbers.
2. **Portable:** the same results on different computers.
3. **A long cycle:** a long sequence before the numbers repeat.
4. **Replicable:** the same starting value (the **seed**) gives the same numbers. This helps debugging, and lets you compare two designs fairly with identical randomness.
5. **Close to ideal:** the numbers closely match uniformity and independence.

Replicable can sound like a weakness. It is a strength: being able to rerun exactly the same "random" day is what lets you tell a real improvement from luck.

## Common pitfalls
<!-- bite: f72ef815-9e54-486c-b9f1-12c913ed2197 -->

1. **Thinking uniform means evenly spaced.** 0.1, 0.2, 0.3, ... is uniform but not independent at all.
2. **Treating pseudo-random as a flaw.** Replicability is why it is used.
3. **Getting the variance wrong.** It is 1/12, not 1/4 or 1/2.

Next lesson builds the most widely used generator, the linear congruential method, and runs it by hand.

## Check your understanding
<!-- bite: 38b653a9-1aae-4792-a3ae-3e7c571dda7b -->

Try each one before you open the answer.

1. <!-- q: gap id="db219c20" answers="uniformity|uniform;independence|independent" -->
   A random number sequence must have two properties: ___ (equally likely anywhere in [0, 1]) and ___ (one number tells you nothing about the next).

   <details><summary>Answer</summary>

   Uniformity and independence.

   </details>

2. <!-- q: exact id="d2a928f4" answer="0.0833333" sigfigs="2" accept="1/12" -->
   What is the variance of a uniform random number on [0, 1]?

   <details><summary>Answer</summary>

   1/12 ≈ 0.083: E(R²) − E(R)² = 1/3 − 1/4.

   </details>

3. <!-- q: exact id="aca55f0f" answer="50" -->
   You generate 500 random numbers and split [0, 1] into 10 equal classes. If the numbers are uniform, about how many should fall in each class?

   <details><summary>Answer</summary>

   50: N/n = 500/10.

   </details>

4. <!-- q: mcq id="cb7992ae" -->
   A generator produces 0.11, 0.12, 0.13, 0.14, ... and so on up to 0.99. Over the whole run, the numbers spread evenly across [0, 1]. Which property fails?

   - [ ] Uniformity
   - [x] Independence
   - [ ] Both
   - [ ] Neither

   <details><summary>Answer</summary>

   Independence. The spread is even, but each number tells you exactly what the next one will be.

   </details>

5. <!-- q: open id="dc676dc3" -->
   Why is it useful that a pseudo-random generator gives the same numbers from the same seed?

   <details><summary>Answer</summary>

   You can rerun a run exactly, which helps find bugs. And you can feed two designs, such as two and three tellers, the identical stream of arrivals and service times, so any difference in their results comes from the design, not from luck.

   </details>

## Before moving on
<!-- bite: 5196d8c8-46f9-4390-b014-7be6738589ab -->

You can state what random numbers need, their mean and variance, and what makes a good generator. **Next:** [[systems-simulation/17-random-numbers-2|17 — Random Numbers 2]]: the linear congruential method.

## Related
<!-- bite: a88d4fb6-79d1-4d7c-af60-44518b2f5748 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 451a9bb9-5ae1-40a1-8d14-95a9aa492658 -->

**Level:** Beginner. **Covers:** uniformity and independence, the mean and variance of a uniform number, pseudo-random numbers and how they fail, and what a good generator needs.

**Where it sits:** lesson 16 of 38, the start of part 4 (random numbers and Monte Carlo).

**Source:** the author's own SSG 517 study notes, section 4.
