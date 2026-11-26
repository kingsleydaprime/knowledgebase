---
id: 34f83494-722a-499e-a7a8-cb3d2da11eb7
---

# Time Value of Money 2: Simple Interest, Compound Interest and Equivalence

Simple and compound interest are the two ways of working out how money grows over time, and equivalence uses them to compare sums paid at different times.

## Before you start
<!-- bite: 08720254-6840-4346-ba49-eb5e24ff81e7 -->

You should know present value, future value, discounting and compounding from [[engineering-economics/04-time-value-of-money-1|Time Value of Money 1]].

After this lesson you will be able to:

1. calculate simple interest and the amount it grows to;
2. calculate a future value and a present value with compound interest;
3. explain economic equivalence, and use it to compare two payment plans.

## What simple and compound interest are
<!-- bite: b2aa73c1-986b-4ea2-a14f-eeac153d9b63 -->

Remember that interest is the rent paid for using someone's money? The question now is what the rent is charged *on*.

- With **simple interest**, it is charged on the original sum only.
- With **compound interest**, it is charged on the original sum and on the interest already earned.

That small difference grows big over many years. We do simple interest first because it's easier, then compound interest, which is the one engineers actually use.

## Simple interest
<!-- bite: 04ab67d3-1214-4ccf-a0c2-862b499065ef -->

Interest is worked out on the original principal only. The interest is the principal times the rate times the number of periods, and the amount at the end is the principal plus that interest:

$$I = P \times i \times n \qquad F = P(1 + in)$$

P is the principal, i the rate per period, n the number of periods.

**Example:** ₦200,000 at 5% simple interest for 4 years. I = 200,000 × 0.05 × 4 = ₦40,000, so the total is ₦240,000.

Simple interest is rarely used in engineering economics because real investments do not behave this way. For example, bonds pay more than keeping money in the bank, so people do not leave money idle.

## Compound interest
<!-- bite: 55aab284-f6bd-4bfa-a1dc-d0b9634d87dd -->

Interest is earned on the principal **and** on interest already earned. This is how money grows in reality, so almost every analysis uses it. It is used for loans, mortgages, equipment leasing, and for how savings and costs grow.

Each year the amount is multiplied by (1 + i). After n years it has been multiplied n times. Going the other way, you divide:

$$F = P(1+i)^n \qquad P = \frac{F}{(1+i)^n}$$

## Compound interest examples
<!-- bite: 8409f0d1-e5da-47f4-bd60-1d6760bac9ba -->

- ₦500,000 at 8% for 5 years: F = 500,000 × (1.08)^5 = ₦734,664.04.
- $100 at 9% for 2 years: F = 100 × (1.09)^2 = $118.81, so the interest earned is $18.81 (simple interest would give only $18).
- A loan of ₦1,000,000 at 10% for 5 years: if nothing is repaid until the end, you owe $1{,}000{,}000 \times 1.1^5 =$ ₦1,610,510.

Look at the $100 example. The extra 81 cents is interest earned on the first year's interest. Over 2 years it's small, but over 20 years it's most of the money.

## Economic equivalence
<!-- bite: e6e4cda3-8441-4942-a386-f8f288823241 -->

Cash flows at different times are equivalent if they have the same value once converted to a common time. For example, ₦100k today may be equivalent to ₦140k in 4 years, depending on the interest rate. Equivalence depends on the interest rate.

How you use it to compare two plans:

1. Convert plan 1 to one value at one point in time.
2. Convert plan 2 to one value at the same point, with the same interest rate.
3. Compare the two values.

## Example: two payment plans
<!-- bite: 5b0da66e-e928-40b7-a685-b2ee58203e4b -->

**Example (slides):** Plan 1 pays ₦1,000 a year for 5 years (total 5,000). Plan 2 pays ₦5,000 now (total 5,000).

At 10%, the first plan has a present value of 1,000 × 3.791 = 3,791. Plan 2 is worth 5,000 today, so it is better, even though the totals are equal.

Where did 3.791 come from? It's the sum of five present values: 1,000/1.1 + 1,000/1.1² + … + 1,000/1.1⁵. Working that out every time is slow, so engineers pack it into a single number called a factor. That is exactly what the next lesson is about.

## Common pitfalls
<!-- bite: 931b35c3-39c2-4f81-b1c6-35190f8a036a -->

1. **Using simple interest when the question says compounded.** "Compounded annually" means F = P(1 + i)^n.
2. **Comparing totals instead of values.** Plan 1 and plan 2 both total ₦5,000, but they are not worth the same. Always convert to one time first.
3. **Forgetting the interest rate.** Two sums are only equivalent at a stated rate. Change the rate and they stop being equivalent.

## Check your understanding
<!-- bite: 01573908-b3a3-41a0-8c3e-12fc7ccd9a89 -->

Try each one before you open the answer.

1. <!-- q: exact id="8ca86501" answer="27000" accept="27,000" -->
   ₦150,000 is invested at 6% simple interest for 3 years. How much interest is earned, in naira?

   <details><summary>Answer</summary>

   I = P × i × n = 150,000 × 0.06 × 3 = ₦27,000.

   </details>

2. <!-- q: exact id="1a457f0e" answer="280985.6" sigfigs="5" tolerance="1" -->
   ₦200,000 is invested at 12% compounded annually for 3 years. What does it grow to, in naira?

   <details><summary>Answer</summary>

   F = 200,000 × (1.12)^3 = 200,000 × 1.404928 = ₦280,985.60.

   </details>

3. <!-- q: exact id="39f5a41d" answer="500" -->
   ₦50,000 is invested at 10% for 2 years. How much more interest does compound interest earn than simple interest, in naira?

   <details><summary>Answer</summary>

   Compound: 50,000 × 1.1² − 50,000 = 60,500 − 50,000 = 10,500. Simple: 50,000 × 0.1 × 2 = 10,000. The difference is ₦500, which is the interest earned on the first year's ₦5,000 of interest.

   </details>

4. <!-- q: exact id="cc6cb019" answer="661157.02" sigfigs="5" tolerance="1" -->
   You will receive ₦800,000 in 2 years. At 10% compounded annually, what is it worth today, in naira?

   <details><summary>Answer</summary>

   P = F/(1 + i)^n = 800,000 / 1.1² = 800,000 / 1.21 = ₦661,157.02.

   </details>

5. <!-- q: mcq id="f1aacb5a" -->
   At 10%, the present value of ₦2,000 a year for 3 years is ₦4,973.70. Plan A pays ₦2,000 a year for 3 years. Plan B pays ₦5,000 now. Which plan is worth more to the person receiving it?

   - [ ] Plan A, because it pays ₦6,000 in total
   - [x] Plan B, because ₦5,000 now is more than Plan A's present value of ₦4,973.70
   - [ ] They are equivalent, because both are about ₦5,000

   <details><summary>Answer</summary>

   Plan B. Compare values at one time, not totals. At time 0 Plan A is worth ₦4,973.70 and Plan B is worth ₦5,000.

   </details>

6. <!-- q: open id="73445924" -->
   Why is compound interest used almost everywhere in engineering economics instead of simple interest?

   <details><summary>Answer</summary>

   Because compound interest is how money really grows: interest is earned on the principal and on the interest already earned. Real investments don't behave like simple interest, because people don't leave earned interest idle; they reinvest it (for example in bonds, which pay more than a bank account). Loans, mortgages, leasing, savings and growing costs all follow compound interest.

   </details>

## Before moving on
<!-- bite: c79b880c-c431-44f5-a007-712775311b81 -->

You can work out simple and compound interest, move a sum forward and back in time, and compare two plans by converting them to one time. **Next:** [[engineering-economics/06-interest-factors-1|Interest Factors 1]]: the six factors that do these conversions in one step.

## Related
<!-- bite: 99f97407-80da-4457-9455-42ea5a478080 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: dbb564ae-eb77-4e53-b94a-af9f02ba9f28 -->

**Level:** Beginner. **Covers:** simple interest, compound interest with three examples, economic equivalence and the slides' two-plan example.

**Where it sits:** lesson 05 of 38, part 2 of 2 on the time value of money.

**Source:** the author's own GEG 501 note, section 3.
