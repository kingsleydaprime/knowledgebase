---
id: 7a7a3803-f19e-4e68-b53e-606eeda7346b
---

# Random Numbers 2: The Linear Congruential Method

The linear congruential method makes each new number from the last one with one multiply, one add and a remainder.

## Before you start
<!-- bite: 67a72d40-02b3-491d-aac7-a76061a3e6be -->

You should have read [[systems-simulation/16-random-numbers-1|16 — Random Numbers 1]].

After this lesson you will be able to:

1. write the linear congruential formula and name its four constants;
2. tell the mixed method from the multiplicative one;
3. generate a sequence of random numbers by hand.

## What the linear congruential method is
<!-- bite: 440387c4-0206-49ea-90ee-ea1b98cf4019 -->

The **linear congruential method (LCM)** is the most widely used way to make pseudo-random numbers. It produces a sequence of whole numbers, each worked out from the one before, and then divides each by a fixed number to scale it into [0, 1].

It needs only a multiply, an add and a "mod" (the remainder after division), so it is very fast. This lesson gives the formula and works it by hand twice. Lesson 18 then shows how to choose the constants so the sequence runs as long as possible before repeating.

## The formula
<!-- bite: 6404cc24-0c4e-4924-8fd6-0e777d8af710 -->

$$X_{i+1} = (aX_i + c) \bmod m, \quad i = 0, 1, 2, \ldots \qquad R_i = \frac{X_i}{m}$$

1. **X0** is the **seed**, the starting value.
2. **a** is the **constant multiplier**.
3. **c** is the **increment**.
4. **m** is the **modulus**.

"mod m" means the remainder after dividing by m: 158 mod 100 = 58. So every X is a whole number from 0 to m − 1, and every R is between 0 and 1.

The choice of a, c, m and X0 strongly affects the mean, the variance and how long before the sequence repeats.

## Mixed and multiplicative
<!-- bite: 421f9fcc-622e-475e-9587-74dc9a46d14e -->

1. If **c is not zero**, it is the **mixed** congruential method.
2. If **c = 0**, it is the **multiplicative** congruential method.

## Worked example: the class exercise
<!-- bite: 00ce7847-ae67-43ab-834e-6b0411d0f8a8 -->

Generate the first six numbers with X0 = 37, a = 17, c = 29, m = 100.

| $i$ | Calculation | $X_i$ | $R_i = X_i/100$ |
| --- | --- | --- | --- |
| 1 | (17 × 37 + 29) mod 100 = 658 mod 100 | 58 | 0.58 |
| 2 | (17 × 58 + 29) mod 100 = 1,015 mod 100 | 15 | 0.15 |
| 3 | (17 × 15 + 29) mod 100 = 284 mod 100 | 84 | 0.84 |
| 4 | (17 × 84 + 29) mod 100 = 1,457 mod 100 | 57 | 0.57 |
| 5 | (17 × 57 + 29) mod 100 = 998 mod 100 | 98 | 0.98 |
| 6 | (17 × 98 + 29) mod 100 = 1,695 mod 100 | 95 | 0.95 |

Each X feeds the next. With m = 100, "mod 100" just means "keep the last two digits", which makes it easy by hand.

## Worked example: the textbook
<!-- bite: 07e2a33c-ba32-4564-968b-b5cd0640b858 -->

With X0 = 27, a = 17, c = 43, m = 100:

1. X1 = (17 × 27 + 43) mod 100 = 502 mod 100 = 2, so R1 = 0.02.
2. X2 = (17 × 2 + 43) mod 100 = 77, so R2 = 0.77.
3. X3 = (17 × 77 + 43) mod 100 = 1,352 mod 100 = 52, so R3 = 0.52.

## Common pitfalls
<!-- bite: 6369eabd-19f3-4c4f-86c6-e1809f80652d -->

1. **Forgetting to feed X forward.** X2 uses X1, not the seed.
2. **Dividing X by the wrong number.** R = X/m, using the modulus.
3. **Forgetting c in the multiplicative case.** With c = 0, it is just $aX_i \bmod m$.
4. **Arithmetic slips.** Write the full product before taking the remainder.

A sequence like this must eventually repeat, because there are only m possible values. Next lesson shows how long it can run first, and how to choose constants that make it run as long as possible.

## Check your understanding
<!-- bite: 7e50a6ad-3ec4-41e3-9f4a-cff984a4b0b8 -->

Try each one before you open the answer.

1. <!-- q: exact id="66482d29" answer="6" -->
   Use the linear congruential method with X0 = 7, a = 5, c = 3 and m = 16. What is X1?

   <details><summary>Answer</summary>

   6: (5 × 7 + 3) mod 16 = 38 mod 16 = 6, since 38 = 2 × 16 + 6.

   </details>

2. <!-- q: exact id="a6a376a6" answer="0.375" accept="3/8|6/16" -->
   With X0 = 7, a = 5, c = 3 and m = 16, X1 = 6. What is the random number R1?

   <details><summary>Answer</summary>

   0.375: R1 = X1/m = 6/16.

   </details>

3. <!-- q: exact id="b59a9364" answer="1" -->
   Continue the generator with a = 5, c = 3 and m = 16, starting from X1 = 6. What is X2?

   <details><summary>Answer</summary>

   1: (5 × 6 + 3) mod 16 = 33 mod 16 = 1.

   </details>

4. <!-- q: exact id="09b5f3b4" answer="0.88" -->
   Use X0 = 12, a = 13, c = 32 and m = 100. What is R1?

   <details><summary>Answer</summary>

   0.88: 13 × 12 + 32 = 188, and 188 mod 100 = 88, so X1 = 88 and R1 = 88/100.

   </details>

5. <!-- q: mcq id="156c9e51" -->
   A generator uses $X_{i+1} = 21X_i \bmod 256$. Which kind is it?

   - [ ] Mixed congruential
   - [x] Multiplicative congruential
   - [ ] Not a congruential generator
   - [ ] Combined generator

   <details><summary>Answer</summary>

   Multiplicative: the increment c is 0.

   </details>

## Before moving on
<!-- bite: eba5bec1-de0e-41ab-a5ec-973f6b15009a -->

You can run the linear congruential method by hand and name its constants. **Next:** [[systems-simulation/18-random-numbers-3|18 — Random Numbers 3]]: period, combined generators and streams.

## Related
<!-- bite: 5c09be04-9941-4223-a79c-176035e6ae3b -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 94b1529f-29de-420f-8127-444bfff04c85 -->

**Level:** Beginner. **Covers:** the linear congruential formula, its four constants, mixed and multiplicative versions, and two worked sequences.

**Where it sits:** lesson 17 of 38, in part 4 (random numbers and Monte Carlo).

**Source:** the author's own SSG 517 study notes, section 4. The quiz generators are added for this lesson and checked in `scripts/diagrams/systems_simulation.py`.
