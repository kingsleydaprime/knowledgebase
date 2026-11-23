---
id: 4c0031d1-263f-44d4-bc8d-96bfb086fb3f
---

# Interest Factors 1: The Six Factors

An interest factor is a ready-made number that converts money from one point in time to another, so you don't redo the compound interest sum every time.

## Before you start
<!-- bite: f3ef2267-e8fc-48fc-9142-5c6b1065e6ef -->

You should know compound interest, F = P(1 + i)^n, from [[engineering-economics/05-time-value-of-money-2|Time Value of Money 2]].

After this lesson you will be able to:

1. read and write factor notation like F = P(F/P, i, n);
2. give the formula and use of each of the six main factors, and spot the three inverse pairs;
3. work all six kinds of problem, and say what each answer means.

## What interest factors are
<!-- bite: 2cf8129b-f44c-456d-a886-ad7821785b66 -->

Remember the two-plan example at the end of the last lesson? To find the present value of ₦1,000 a year for 5 years you had to add five separate present values. The formulas from the last lesson get repeated in almost every problem, so engineers turn them into **factors** you can read from a table or compute once.

Each factor converts money from one point in time to another. The name reads "find the first, given the second": P/F means present given future.

## The notation
<!-- bite: 8d499630-60e8-4b04-bf14-0b7a04fe996a -->

F = P(F/P, i, n) means F equals P times the F/P factor at interest rate i for n periods.

The letters always mean the same things:

1. **P** is a present sum, at time 0.
2. **F** is a future sum, at the end of period n.
3. **A** is an equal payment at the end of each period, from period 1 to period n. A string of equal payments like this is called an **annuity**.
4. **i** is the interest rate per period.
5. **n** is the number of periods.

## The six main factors
<!-- bite: 1eb6aae1-87c1-48da-8adf-dc4f338e37d0 -->

| Factor | Name | Formula | Use it to find |
| --- | --- | --- | --- |
| P/F | Present worth (single payment) | 1/(1+i)^n | Today's value of one future amount |
| F/P | Future worth (compound amount) | (1+i)^n | Future value of one present amount |
| P/A | Present worth of annuity | [(1+i)^n − 1] / [i(1+i)^n] | Today's value of equal yearly amounts |
| A/P | Capital recovery | i(1+i)^n / [(1+i)^n − 1] | Equal yearly amount from a present sum |
| F/A | Future worth of annuity | [(1+i)^n − 1] / i | Future value of equal yearly deposits |
| A/F | Sinking fund | i / [(1+i)^n − 1] | Equal yearly amount needed to reach a future sum |

## The three pairs
<!-- bite: e5af3e35-e315-410a-80ae-eefaac682a0c -->

Notice the pairs. P/F and F/P are inverses of each other. P/A and A/P are inverses. F/A and A/F are inverses. So if you know one, the other is 1 divided by it.

Also, A/P = A/F + i, which is a useful check. At 10% for 5 years, A/P = 0.2638 and A/F = 0.1638, and 0.1638 + 0.10 = 0.2638.

> **Correction:** the 2019 material writes the capital recovery factor once with (1 − i)^n − 1. It should be (1 + i)^n − 1, as in the table.

## Worked examples 1 to 3 (from your lectures)
<!-- bite: 7fe3a3c5-50a0-4a73-b8b1-ad1595e73725 -->

Always say what the answer means. Your lecturer stressed that interpretation is the most important part.

**1. P/F:** what is ₦500,000 payable in 3 years worth today at 10%? P/F = 1/1.1^3 = 0.7513, so P = 500,000 × 0.7513 = **₦375,650**. Meaning: ₦375,650 invested today grows to ₦500,000 in 3 years.

**2. F/P:** what does ₦500,000 grow to at 8% in 5 years? F/P = 1.08^5 = 1.4693, so F = 500,000 × 1.4693 = **₦734,650** (the exact figure is ₦734,664, because 1.4693 is rounded).

**3. P/A:** a project saves ₦200,000 a year for 4 years at 10%. What are the savings worth today? P/A = 3.1699, so P = 200,000 × 3.1699 = **₦633,980**. Meaning: 4 years of savings are worth ₦633,980 today.

## Worked examples 4 to 6 (from your lectures)
<!-- bite: 7427ac29-5ad2-4696-ab90-1688f68fc0f4 -->

**4. A/P:** a ₦1,000,000 loan over 5 years at 10%. What is the yearly repayment? A/P = 0.2638, so A = 1,000,000 × 0.2638 = **₦263,800 a year** for 5 years (exact: ₦263,797.48). The total repaid is more than ₦1,000,000 because of interest on the balance.

**5. F/A:** you save ₦100,000 a year at 10% for 4 years. What do you have at the end? F/A = 4.641, so F = **₦464,100**.

**6. A/F:** you need ₦1,000,000 in 5 years at 10%. How much do you save each year? A/F = 0.1638, so A = **₦163,800 a year**. This is how a sinking fund or a replacement reserve works.

## When to use each one
<!-- bite: 1cb9edd3-5333-4b40-affc-a844db38e94e -->

- **P/A and A/P** go together when you work with loans, mortgage payments, installments, lease payments, subscriptions or yearly maintenance fees. Engineers use annuities to compare projects that have yearly costs.
- **F/A and A/F** are for saving up to a future cost: replacement funds, reserve funds, sinking funds.
- **P/F and F/P** are for single amounts.

A quick way to pick: ask "what do I have, and what do I want?" Have a loan today and want the yearly payment? That's A given P, so A/P.

## Common pitfalls
<!-- bite: 64855d30-5378-4f85-8b97-c047c3c84924 -->

1. **Using P/F for an annuity.** A string of equal payments needs P/A. The 2019 material makes this slip once in its notation.
2. **Putting the first payment at time 0.** The A in these factors starts at the end of period 1. If a payment is at time 0, handle it separately.
3. **Stopping at the number.** Say what it means: "₦375,650 invested today grows to ₦500,000 in 3 years."

These six factors handle payments that stay the same every year. But maintenance usually rises as a machine gets older. The next lesson handles costs that grow by the same amount each year.

## Check your understanding
<!-- bite: 1094ed77-59d2-4015-8a8b-a14e813237db -->

Try each one before you open the answer.

1. <!-- q: mcq id="4cf9ef9d" -->
   A company must replace a facility in 15 years and wants to put away an equal amount at the end of each year to pay for it. Which factor gives the yearly amount?

   - [ ] P/A
   - [ ] A/P
   - [x] A/F
   - [ ] F/P

   <details><summary>Answer</summary>

   A/F, the sinking fund factor: an equal yearly amount (A) needed to reach a future sum (F).

   </details>

2. <!-- q: exact id="47e4878d" answer="190655.42" sigfigs="4" tolerance="30" -->
   What is ₦300,000 payable in 4 years worth today, at 12% compounded annually? Give your answer in naira.

   <details><summary>Answer</summary>

   P/F = 1/1.12^4 = 0.6355, so P = 300,000 × 0.6355 ≈ ₦190,655. Meaning: about ₦190,655 invested today at 12% grows to ₦300,000 in 4 years.

   </details>

3. <!-- q: exact id="2bc31109" answer="554819.46" sigfigs="4" tolerance="60" -->
   A firm borrows ₦2,000,000 at 12%, to be repaid in 5 equal end-of-year payments. What is each payment, in naira?

   <details><summary>Answer</summary>

   A/P at 12% for 5 years = 0.12(1.12)^5 / [(1.12)^5 − 1] = 0.2774. A = 2,000,000 × 0.2774 ≈ ₦554,819 a year.

   </details>

4. <!-- q: exact id="75bea45a" answer="366796.45" sigfigs="4" tolerance="30" -->
   You save ₦50,000 at the end of every year for 6 years at 8% compounded annually. How much do you have at the end of year 6, in naira?

   <details><summary>Answer</summary>

   F/A at 8% for 6 years = (1.08^6 − 1)/0.08 = 7.3359. F = 50,000 × 7.3359 ≈ ₦366,796.

   </details>

5. <!-- q: exact id="f4cae847" answer="0.1638" sigfigs="3" -->
   At 10% for 5 years, the capital recovery factor A/P is 0.2638. Use the relationship between A/P and A/F to find the sinking fund factor A/F.

   <details><summary>Answer</summary>

   A/P = A/F + i, so A/F = 0.2638 − 0.10 = 0.1638.

   </details>

6. <!-- q: gap id="e4740875" answers="P/A;F/A;F/P" -->
   Fill in the gaps with the inverse of each factor. A/P is the inverse of ___. A/F is the inverse of ___. P/F is the inverse of ___.

   <details><summary>Answer</summary>

   A/P and P/A, A/F and F/A, P/F and F/P.

   </details>

## Before moving on
<!-- bite: 92610006-20c4-43bb-8768-8a1c92e0d1a4 -->

You can write factor notation, pick the right factor for a problem, and interpret the answer. **Next:** [[engineering-economics/07-interest-factors-2|Interest Factors 2]]: gradient series, and the practical side of using factors.

## Related
<!-- bite: 20f87f53-8a22-474e-8169-4c85e378fc54 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: bdf425b6-78d8-4469-b47c-c59d4e91ad9e -->

**Level:** Beginner. **Covers:** factor notation, the six factors and their formulas, the inverse pairs and the A/P = A/F + i check, the lecture's six worked examples, and when to use each factor.

**Where it sits:** lesson 06 of 38, part 1 of 2 on interest factors.

**Source:** the author's own GEG 501 note, section 4 (lecture 4), with corrections from section 15 of the note.
