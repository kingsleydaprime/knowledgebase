---
id: 4dfadb52-100f-480a-bdf5-e089dcbc3201
---

# Random Numbers 3: Period, Combined Generators and Streams

A generator's period is how many numbers it gives before repeating, and the right constants make that period as long as possible.

## Before you start
<!-- bite: 2d3e114e-f500-4b1b-bf6e-27428fb317d2 -->

You should have read [[systems-simulation/17-random-numbers-2|17 — Random Numbers 2]].

After this lesson you will be able to:

1. state the longest possible period for mixed and multiplicative generators, and the conditions that reach it;
2. show how a bad seed shortens the period;
3. explain combined generators and random number streams.

## What the period is
<!-- bite: bbe69967-6227-4fa9-969c-3141efa79725 -->

A linear congruential generator only has m possible values, 0 to m − 1. As soon as it produces a value it has produced before, the whole sequence from there repeats, because each X depends only on the one before. The number of values before the repeat is the **period**, P.

A long period matters: once the sequence repeats, the simulation is reusing the same randomness and its results stop being independent. A large modulus also helps in a second way: it gives a fine spacing between possible values (maximum density), so the numbers cover [0, 1] smoothly instead of in coarse steps.

## The three rules for the longest period
<!-- bite: 580aeb2f-3c34-41b4-89df-3961a9981223 -->

| Generator | Longest period | When it is reached |
| --- | --- | --- |
| Mixed, m = 2^b | P = m | c is relatively prime to m (no common factor), and a = 1 + 4k |
| Multiplicative, m = 2^b | P = m/4 | the seed is odd, and a = 3 + 8k or 5 + 8k |
| Multiplicative, m prime | P = m − 1 | the smallest k for which a^k − 1 is divisible by m is k = m − 1 |

Here k is any whole number, so "a = 1 + 4k" means a is one of 1, 5, 9, 13, ...

## Example: a bad seed
<!-- bite: a4fb85a4-4f3f-4fb6-88a0-bdc422a4429a -->

Take the multiplicative generator a = 13, m = 64, c = 0. Here m = 2⁶ and 13 = 5 + 8 × 1, so the rule promises P = 64/4 = 16, but only with an odd seed.

1. **Seed 1 or seed 3:** period 16, the maximum.
2. **Seed 2:** period 8.
3. **Seed 4:** period 4.

An even seed throws away part of the cycle. The constants were fine; the seed spoiled them.

## Example: a full mixed period
<!-- bite: 9c47e5f7-35a4-42be-9c53-9afe258e30b7 -->

The mixed generator a = 5, c = 3, m = 16 meets both conditions: 3 has no common factor with 16, and 5 = 1 + 4 × 1. So it reaches the full period P = m = 16, visiting every value 0 to 15 exactly once before repeating, whatever the seed.

## Combined generators
<!-- bite: c40bf01f-8a75-4c3a-8bea-9fcd077dfbe8 -->

With modern computing, a single generator with a period of around 2 billion (about 2³¹) is too short: a big simulation can use that many numbers in minutes. **Combined generators** join two or more multiplicative generators. L'Ecuyer's method gives periods of order 10¹⁸, far longer than any simulation needs.

## Streams
<!-- bite: d834c3b2-f9b6-437b-98d8-3ea2fc865e9c -->

A **stream** is a separate piece of the generator's sequence, starting from its own seed. Give each source of randomness its own stream: one for arrivals, one for service times, one for breakdowns.

The point is fair comparison. If you add a teller and rerun, the arrivals stream is untouched, so both designs see exactly the same customers. The difference in waiting time then comes from the extra teller, not from a luckier day.

## Common pitfalls
<!-- bite: 456da6f1-401c-428c-8038-5b14e622df58 -->

1. **Using an even seed with a multiplicative 2^b generator.** It shortens the period.
2. **Forgetting the c condition.** For the full mixed period, c must have no common factor with m.
3. **One stream for everything.** Changing one part of the model then reshuffles all the randomness, and comparisons get noisy.

We can now make good-looking numbers. But looking good isn't proof. Next lesson tests them, starting with the Kolmogorov-Smirnov test for uniformity.

## Check your understanding
<!-- bite: 4ec50c3f-5fd4-4bb2-bf06-7e1671a304a0 -->

Try each one before you open the answer.

1. <!-- q: exact id="6464ab26" answer="256" -->
   A multiplicative generator has m = 1,024 (that is 2¹⁰), a = 5 + 8k and an odd seed. What is its period?

   <details><summary>Answer</summary>

   256: for a multiplicative generator with m = 2^b, the longest period is m/4 = 1,024/4.

   </details>

2. <!-- q: exact id="3f4bda2d" answer="1024" accept="1,024" -->
   A mixed generator has m = 1,024, c = 7 and a = 1 + 4k. What is its longest period?

   <details><summary>Answer</summary>

   1,024: a mixed generator with m = 2^b reaches P = m when c is relatively prime to m (7 is odd, so it shares no factor with 1,024) and a = 1 + 4k.

   </details>

3. <!-- q: exact id="e22568c0" answer="100" -->
   A multiplicative generator has a prime modulus m = 101, with a chosen to give the longest period. What is that period?

   <details><summary>Answer</summary>

   100: with m prime, the longest period is m − 1.

   </details>

4. <!-- q: mcq id="26f14c60" -->
   The multiplicative generator a = 13, m = 64 is run from seed 4. What goes wrong?

   - [ ] Nothing; every seed gives period 16
   - [x] The period drops to 4, because the seed is even
   - [ ] The numbers all come out as 0
   - [ ] The generator becomes mixed

   <details><summary>Answer</summary>

   The period drops to 4. The full period of m/4 = 16 needs an odd seed; seed 2 gives 8 and seed 4 gives 4.

   </details>

5. <!-- q: open id="515f2341" -->
   A model compares two and three cashiers. Why should arrivals, service times and breakdowns each use their own random number stream?

   <details><summary>Answer</summary>

   So that changing the design doesn't change the randomness. With separate streams, both designs see the same arrival times and the same service times, so any difference in waiting comes from the extra cashier and not from a different, luckier sequence of customers.

   </details>

## Before moving on
<!-- bite: 07ee82dc-b1b8-4739-9628-baeeca1fc72d -->

You can find a generator's longest period and explain combined generators and streams. **Next:** [[systems-simulation/19-testing-random-numbers-1|19 — Testing Random Numbers 1]].

## Related
<!-- bite: 12ad07a3-3364-4455-be54-66fee9ca3f67 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: a0fcdcbf-fff8-4be5-8be8-90d6662381a7 -->

**Level:** Intermediate. **Covers:** the period, the three longest-period rules, the bad-seed example, a full mixed period, combined generators and streams.

**Where it sits:** lesson 18 of 38, in part 4 (random numbers and Monte Carlo).

**Source:** the author's own SSG 517 study notes, section 4. The full mixed period example is added for this lesson; every period here is checked in `scripts/diagrams/systems_simulation.py`.
