---
id: 8a521a85-fcab-4fb7-87bc-fc4d88628a73
---

# Interest Factors 2: Gradient Series and Using the Factors

A gradient series is a cash flow that grows by the same amount every period, like a maintenance bill that rises ₦10,000 a year as a machine ages.

## Before you start
<!-- bite: 55417c12-3285-4ed0-bb12-f599357e9c8b -->

You should know the six factors, especially P/A, from [[engineering-economics/06-interest-factors-1|Interest Factors 1]].

After this lesson you will be able to:

1. recognise a gradient series and find its G;
2. convert a gradient into an equal yearly amount with A/G, and into a present value with P/G;
3. use tables, calculators and spreadsheets for factors, combine factors, and handle payments at the start of a period.

## What a gradient series is
<!-- bite: e792fa27-ea64-4ddb-9421-469fee777b3d -->

The six factors in the last lesson all assume the payment A is the same every year. Real costs often aren't. A generator's maintenance might be ₦50,000 in year 1, ₦60,000 in year 2, ₦70,000 in year 3, because old machines need more care.

In a gradient series the cash flow **increases by a constant amount G every period**, starting from the second year (for example maintenance cost rising ₦10k, ₦20k, ₦30k, so G = ₦10k). It suits rising maintenance, labour or utility cost.

So a rising cost is split into two parts: a **base amount** that stays the same every year (₦50,000 here), plus the **gradient** that starts at zero in year 1 and grows by G each year after.

## The gradient factors
<!-- bite: 45ae5e93-fecf-4207-8c6d-a5b1429b710d -->

There are two gradient factors. A/G turns the gradient into an equal yearly amount, and P/G turns it into a present value:

$$(A/G, i, n) = \frac{1}{i} - \frac{n}{(1+i)^n - 1} \qquad (P/G, i, n) = \frac{(1+i)^n - 1 - ni}{i^2 (1+i)^n}$$

If there is also a base amount, handle it as an ordinary annuity and add the gradient part:

- equal yearly amount = base + G × (A/G, i, n);
- present value = base × (P/A, i, n) + G × (P/G, i, n).

## Worked example: rising maintenance
<!-- bite: 5fd176f1-b4ae-484c-b67b-612091fe18ea -->

A generator's maintenance is ₦50,000 in year 1 and rises by ₦10,000 every year for 5 years (50k, 60k, 70k, 80k, 90k). The interest rate is 10%.

1. Split it: the base is ₦50,000 a year and G = ₦10,000.
2. Factors at 10% for 5 years: A/G = 1.8101, P/A = 3.7908, P/G = 6.8618.
3. Equal yearly amount = 50,000 + 10,000 × 1.8101 = **₦68,101 a year**.
4. Present value = 50,000 × 3.7908 + 10,000 × 6.8618 = 189,539 + 68,618 = **₦258,157**.

Meaning: paying the rising bills is the same, at 10%, as paying a flat ₦68,101 every year, or setting aside ₦258,157 today. Adding up the five bills one by one with P/F gives the same ₦258,157, which is a good check.

This example was added for this lesson. It is the method you need for the practice booklet's bridge question, where fuel savings rise by a fixed amount each year.

## Using the factors
<!-- bite: a646946d-f46d-4f60-b00b-50a26b3919f2 -->

- You can use an interest table, a calculator or a spreadsheet. In a spreadsheet: `P = PV(i, n, A, F)`, `F = FV(i, n, A, P)`, `i = RATE(n, A, P, F)`.
- Small differences between table and formula answers are normal. Do not worry about exact digits.
- Factors can be combined. For example (F/G) = (P/G)(F/P): move the gradient to time 0, then forward to the end.

Combining works because each factor is just a step in time. P/G takes the gradient to time 0, and F/P takes that single amount to the end.

## Payments at the start or end of a period
<!-- bite: 1973cc45-5a55-443e-8906-e6da3eec2de8 -->

Unless the question says otherwise, payments are made at the **end** of each period (even if the bill arrives on the first of the month). If the first payment is made at the start, the payments are different, so check the question.

Interest and payment periods are assumed annual, and the interest rate is assumed constant.

The factors in lessons 06 and 07 also assume the interest is compounded once per period, matching the payments. When a bank compounds monthly but quotes a yearly rate, that assumption breaks, and that's the next lesson.

## Common pitfalls
<!-- bite: f0631b68-03ae-40e6-b55f-3e08964a1790 -->

1. **Starting the gradient in year 1.** The gradient is zero in year 1, G in year 2, 2G in year 3. The year-1 amount is the base.
2. **Forgetting the base.** A/G and P/G only handle the growing part. Add the base as an ordinary annuity.
3. **Mixing table and formula values in one answer.** Pick one and stay with it. Small differences are fine, but say which you used.

## Check your understanding
<!-- bite: b79ab06f-b0de-4848-8be2-ad006944a39f -->

Try each one before you open the answer.

1. <!-- q: exact id="0646e875" answer="5000" accept="5,000|₦5,000" -->
   A pump's repair cost is ₦20,000 in year 1, ₦25,000 in year 2, ₦30,000 in year 3 and ₦35,000 in year 4. What is the gradient G, in naira?

   <details><summary>Answer</summary>

   G = ₦5,000, the constant amount the cost rises by each year. The base is ₦20,000.

   </details>

2. <!-- q: exact id="2ef1eec4" answer="27019.8" sigfigs="4" tolerance="5" -->
   A pump's repair cost is ₦20,000 in year 1 and rises by ₦5,000 every year for 4 years. At 8%, (A/G, 8%, 4) = 1.4040. What equal yearly amount is the same as these rising costs, in naira?

   <details><summary>Answer</summary>

   Equal yearly amount = base + G × (A/G) = 20,000 + 5,000 × 1.4040 ≈ ₦27,020 a year.

   </details>

3. <!-- q: exact id="f2c30901" answer="23250.46" sigfigs="4" tolerance="5" -->
   A cost has no base amount: it is ₦0 in year 1, ₦5,000 in year 2, ₦10,000 in year 3 and ₦15,000 in year 4. At 8%, (P/G, 8%, 4) = 4.6501. What is its present value, in naira?

   <details><summary>Answer</summary>

   P = G × (P/G) = 5,000 × 4.6501 ≈ ₦23,250. You can check it with P/F: 5,000/1.08² + 10,000/1.08³ + 15,000/1.08⁴ ≈ 23,250.

   </details>

4. <!-- q: mcq id="55d176da" -->
   In a gradient series with a base of ₦40,000 and G = ₦8,000, what is the cash flow in year 3?

   - [ ] ₦48,000
   - [x] ₦56,000
   - [ ] ₦64,000
   - [ ] ₦24,000

   <details><summary>Answer</summary>

   ₦56,000. The gradient is 0 in year 1, G in year 2 and 2G in year 3, so year 3 is 40,000 + 2 × 8,000 = ₦56,000.

   </details>

5. <!-- q: mcq id="399ef902" -->
   A question says "a maintenance fee of ₦100,000 is paid every year for 5 years" and says nothing about timing. When should you assume each payment is made?

   - [ ] At the start of each year
   - [x] At the end of each year
   - [ ] In the middle of each year

   <details><summary>Answer</summary>

   At the end of each year, unless the question says otherwise. Maintenance is an end-of-period flow, and the factors assume end-of-period payments.

   </details>

## Before moving on
<!-- bite: 7f003454-c878-4b8a-b151-ee626967452a -->

You can split a rising cost into a base and a gradient, convert it with A/G and P/G, and use factors from tables or a spreadsheet. **Next:** [[engineering-economics/08-nominal-and-effective-interest|Nominal and Effective Interest]]: when interest is compounded more than once a year.

## Related
<!-- bite: 4b9a0257-ee1c-40d2-bab7-1ba2fc19e4d2 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 7c5fabe9-1814-4ec2-95af-935e4881648b -->

**Level:** Beginner. **Covers:** gradient series, the A/G and P/G factors, a worked rising-maintenance example, tables and spreadsheets, combining factors, and payments at the start or end of a period.

**Where it sits:** lesson 07 of 38, part 2 of 2 on interest factors.

**Source:** the author's own GEG 501 note, sections 4 and 14.5. The rising-maintenance example was added for this lesson, and its numbers are checked by `scripts/diagrams/engineering_economics.py`.
