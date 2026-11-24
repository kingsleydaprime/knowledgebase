---
id: d5c158a6-a0a4-4b5f-99b0-2f4db50d4b3b
---

# Testing Random Numbers 2: Chi-Square and Autocorrelation

The chi-square test checks uniformity in large samples by counting numbers in classes, and the autocorrelation test checks independence.

## Before you start
<!-- bite: f6b69e31-4b8c-43f9-b501-5b2315afcb5d -->

You should have read [[systems-simulation/19-testing-random-numbers-1|19 — Testing Random Numbers 1]].

After this lesson you will be able to:

1. carry out the chi-square test for uniformity;
2. set up the autocorrelation test and decide from its Z statistic;
3. explain why one failed test doesn't prove a generator is bad.

## What the chi-square and autocorrelation tests are
<!-- bite: 661d489a-df38-4c69-bee5-e89c064d96f2 -->

Lesson 19 tested uniformity with Kolmogorov-Smirnov, which suits small samples. This lesson finishes the toolkit. **Chi-square** tests uniformity when you have many numbers. **Autocorrelation** tests the other property, independence: whether numbers a fixed distance apart move together. The same hypothesis set-up from lesson 19 applies to both.

## The chi-square test
<!-- bite: af118a74-4682-4c82-80df-306aaa9fa488 -->

Split [0, 1] into n equal classes and count how many numbers fall in each. Call the observed count in class i **O_i**. If the numbers are uniform, each class expects **E_i = N/n**.

$$\chi_0^2 = \sum_{i=1}^{n} \frac{(O_i - E_i)^2}{E_i}, \qquad E_i = \frac{N}{n}$$

Compare $\chi_0^2$ with the chi-square table value for **n − 1 degrees of freedom** at your α. If $\chi_0^2$ is larger, reject uniformity.

It needs a large sample: each E_i should be at least 5.

**Example from the notes:** 100 numbers in 10 classes gave $\chi_0^2$ = 3.4. The critical value for 9 degrees of freedom at α = 0.05 is 16.9. Since 3.4 < 16.9, uniformity is not rejected.

## A chi-square worked out
<!-- bite: 470c2baa-6482-490b-9ad0-8828e3b09dd0 -->

50 numbers, 5 classes, so E_i = 10. The observed counts are 8, 12, 10, 7 and 13.

| Class | O_i | O_i − E_i | (O_i − E_i)²/E_i |
| --- | --- | --- | --- |
| 0.0–0.2 | 8 | −2 | 0.4 |
| 0.2–0.4 | 12 | 2 | 0.4 |
| 0.4–0.6 | 10 | 0 | 0.0 |
| 0.6–0.8 | 7 | −3 | 0.9 |
| 0.8–1.0 | 13 | 3 | 0.9 |

$\chi_0^2$ = 2.6. With 4 degrees of freedom the critical value at α = 0.05 is 9.49, so uniformity is not rejected.

## The autocorrelation test
<!-- bite: 1084a8f3-3621-4faf-a760-75a51662efa7 -->

This checks whether numbers a fixed distance apart, the **lag** m, are correlated. Start at the i-th number and take every m-th number after it: R_i, R_(i+m), R_(i+2m), ...

1. **H0:** the autocorrelation is 0. **H1:** it isn't.
2. **M** is the largest whole number with i + (M + 1)m ≤ N.
3. The estimate is $\hat\rho = \dfrac{1}{M+1}\sum_{k=0}^{M} R_{i+km}R_{i+(k+1)m} - 0.25$, and its standard deviation is $\sigma = \dfrac{\sqrt{13M+7}}{12(M+1)}$.
4. The statistic is $Z_0 = \hat\rho / \sigma$.
5. **Do not reject** if Z0 lies between −z(α/2) and +z(α/2). For α = 0.05 that is ±1.96.

If the estimate is positive, high numbers tend to be followed by high ones. If negative, high ones tend to be followed by low ones.

**Example from the notes:** N = 30, i = 3, m = 5. Then 3 + (M + 1) × 5 ≤ 30 gives M + 1 ≤ 5.4, so M = 4. The test gave Z0 = −1.516, inside ±1.96, so there is no evidence of autocorrelation.

## Runs tests
<!-- bite: 24e5242e-e406-4e3b-a2ae-a6123c5475ae -->

**Runs tests** are another way to check independence. A run is a stretch of numbers that keep going up, or keep going down, or stay on one side of the mean. Too few or too many runs suggests a pattern. The textbook names runs up and down, and runs above and below the mean; the course focuses on the three tests above.

## Passing isn't everything
<!-- bite: 24f7305c-0706-4a29-b5f3-e5c59263e8b3 -->

Test a generator many times and it will fail an occasional test purely by chance: at α = 0.05, about 5 tests in 100. So **one failure isn't proof of a bad generator.** Repeat the test with fresh numbers, or add other tests. A generator that fails again and again, or fails far more than 5% of the time, is the one to worry about.

## Common pitfalls
<!-- bite: ecdbd4c7-6708-4045-994c-cd1258cdbcbf -->

1. **Using n degrees of freedom.** Chi-square uses n − 1.
2. **Running chi-square on tiny samples.** Every E_i should be at least 5; for small N, use KS.
3. **Getting M wrong.** It is the largest whole number with i + (M + 1)m ≤ N.
4. **Treating one failure as the verdict.** Repeat before blaming the generator.

The numbers are made and tested. But a simulation needs exponential gaps and normal service times, not just numbers between 0 and 1. Next lesson turns uniform numbers into any distribution you need.

## Check your understanding
<!-- bite: bbc9d2f5-e90f-4550-b2eb-d313b07d02dc -->

Try each one before you open the answer.

1. <!-- q: exact id="f5f862ce" answer="2.6" -->
   50 random numbers are split into 5 equal classes, with observed counts 8, 12, 10, 7 and 13. What is the chi-square statistic?

   <details><summary>Answer</summary>

   2.6. Each class expects 50/5 = 10. The terms (O − E)²/E are 0.4, 0.4, 0, 0.9 and 0.9.

   </details>

2. <!-- q: exact id="ed5cd304" answer="4" -->
   60 random numbers are split into 6 equal classes, with observed counts 12, 7, 9, 11, 14 and 7. What is the chi-square statistic?

   <details><summary>Answer</summary>

   4.0. Each class expects 60/6 = 10. The squared differences (O − E)² are 4, 9, 1, 1, 16 and 9, which add to 40, and 40/10 = 4.0. With 5 degrees of freedom the critical value at α = 0.05 is 11.07, so uniformity is not rejected.

   </details>

3. <!-- q: exact id="4cde4be1" answer="5" -->
   In an autocorrelation test with N = 40 numbers, starting at i = 2 with lag m = 6, what is M?

   <details><summary>Answer</summary>

   5. You need the largest whole M with 2 + (M + 1) × 6 ≤ 40, so (M + 1) ≤ 6.33, giving M + 1 = 6 and M = 5.

   </details>

4. <!-- q: mcq id="d4d0fe30" -->
   An autocorrelation test at α = 0.05 gives Z0 = 2.31. What do you conclude?

   - [ ] Do not reject: the numbers are independent
   - [x] Reject H0: there is evidence of autocorrelation, with high numbers tending to follow high ones
   - [ ] Reject H0: the numbers aren't uniform
   - [ ] The test is invalid

   <details><summary>Answer</summary>

   Reject, because 2.31 is outside ±1.96. The positive sign means high numbers tend to be followed by high ones. Autocorrelation is about independence, not uniformity.

   </details>

5. <!-- q: open id="c515cfab" -->
   You run 100 chi-square tests on a generator at α = 0.05 and it fails 4 of them. Is the generator bad?

   <details><summary>Answer</summary>

   Not on this evidence. At α = 0.05, a perfect generator is expected to fail about 5 tests in 100 just by chance, so 4 failures is normal. Worry if it fails far more often than α predicts, or keeps failing the same test on fresh numbers.

   </details>

## Before moving on
<!-- bite: f5cdbab4-f284-48dd-88a5-d35cc29e6510 -->

You can carry out chi-square and autocorrelation tests and interpret a failure sensibly. **Next:** [[systems-simulation/21-generating-random-variates|21 — Generating Random Variates]].

## Related
<!-- bite: 40f9dec8-b4d9-4090-a407-5ec98d8e8e4b -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 77dd79e7-1cd4-45a2-b47e-2999f1c8ec85 -->

**Level:** Intermediate. **Covers:** the chi-square test, a worked example, the autocorrelation test with its formulas, runs tests, and why one failure isn't proof.

**Where it sits:** lesson 20 of 38, part 2 of 2 on testing random numbers.

**Source:** the author's own SSG 517 study notes, section 4. The autocorrelation formulas are the standard textbook ones (Banks, Carson, Nelson and Nicol), added because the notes name the steps without them; the worked chi-square and quiz numbers are added for this lesson.
