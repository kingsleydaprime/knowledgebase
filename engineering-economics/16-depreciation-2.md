---
id: 85158af1-98dc-4d2b-8593-7543f0a030b4
---

# Depreciation 2: Straight Line and Declining Balance

Straight line depreciation writes off the same amount every year, while declining balance charges most in the early years.

## Before you start
<!-- bite: 8ea77d79-0522-4008-86a5-9399ff2ef0b1 -->

You should know first cost, salvage value and book value from [[engineering-economics/15-depreciation-1|Depreciation 1]].

After this lesson you will be able to:

1. calculate straight line depreciation and build its book value table;
2. calculate declining balance and double declining balance depreciation year by year;
3. apply the rule that book value never falls below salvage value.

## What the depreciation methods are
<!-- bite: b534459f-e4b5-483c-8770-003f6fc99698 -->

There are three groups: **time-based** (straight line), **usage-based** (units of production) and **accelerated** (declining balance, sum-of-years digits). Every method writes off the same total, FC − SV, but at a different pace.

Think of eating a pot of jollof over five days. You can eat the same amount each day (straight line), or eat a lot on day 1 and less each day after (accelerated). Either way the pot is empty on day 5. The total doesn't change, only the pace.

This lesson covers straight line and declining balance. Lesson 17 covers the rest.

## 1. Straight line (SL)
<!-- bite: 7cdcb3e2-88d6-4e48-9b32-f8a15dc9a79c -->

Equal depreciation every year. You take the depreciable amount and share it equally over the life:

$$D = \frac{FC - SV}{n}$$

- **Example (lecture 6):** FC = ₦5,000,000, SV = ₦500,000, n = 5. D = 4,500,000 ÷ 5 = **₦900,000 a year**.
- **Lecture 3 example:** P = ₦2,000,000, S = ₦200,000, n = 5. D = (2,000,000 − 200,000)/5 = ₦360,000 a year.
- **FE review:** cost $9,000, life 10 years, salvage $200. D = 8,800/10 = $880 a year, so book value after 3 years is 9,000 − 3 × 880 = $6,360.

> **Correction:** the FE review slides type "9000 − (3)($800) = $6,360". The yearly depreciation is $880, so it is 9,000 − 3 × 880. The answer is right; the typed number is wrong.

## Straight line: the book value table
<!-- bite: cfaae56c-9ad7-4556-a63b-a996c6c286ef -->

**Example (lecture 6 class work):** installed cost ₦12,000,000, salvage ₦2,000,000, 5 years. D = **₦2,000,000 a year**.

| Year | Depreciation | Accumulated | Book value |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 12,000,000 |
| 1 | 2,000,000 | 2,000,000 | 10,000,000 |
| 2 | 2,000,000 | 4,000,000 | 8,000,000 |
| 3 | 2,000,000 | 6,000,000 | 6,000,000 |
| 4 | 2,000,000 | 8,000,000 | 4,000,000 |
| 5 | 2,000,000 | 10,000,000 | 2,000,000 |

Notice the book value ends exactly at the salvage value.

## 2. Declining balance (DB) and double declining balance (DDB)
<!-- bite: 424199ab-08a8-420c-8626-0888719e7b1d -->

Depreciation is highest in the early years and falls over time, because each year you take a fixed percentage of the **book value** at the start of the year. The new book value is the old one minus that year's charge:

$$D_t = k \times BV_{t-1} \qquad BV_t = BV_{t-1} - D_t$$

- For plain declining balance, k is the rate given in the question.
- For **double declining balance**, k = 2/n (double the straight-line rate). If a question says "use the double declining rate", use k = 2/n.
- It is popular for tax purposes because it gives bigger deductions early.

> **Correction:** one page of your lecture 6 writes k = 1/n. For double declining balance k = 2/n, and your own later page and example (k = 0.4 for n = 5) use 2/n.

## The salvage value floor
<!-- bite: 9598358d-78bf-4df1-9134-2b8eca8c64a3 -->

Salvage value is not used in the declining balance formula, but book value must **never fall below salvage value**. In the year it would, only depreciate down to the salvage value.

This is the rule students forget, so keep it in front of you while you work the next two examples.

## Example: double declining balance
<!-- bite: 89e7e144-a00a-4641-93e7-6f35ba1a2925 -->

**Example (lecture 6, DDB):** an asset costs ₦8,500,000, life 5 years, salvage ₦500,000. k = 2/5 = 0.4 (40%).

| Year | Depreciation (0.4 × opening BV) | Closing book value |
| --- | --- | --- |
| 1 | 3,400,000 | 5,100,000 |
| 2 | 2,040,000 | 3,060,000 |
| 3 | 1,224,000 | 1,836,000 |
| 4 | 734,400 | 1,101,600 |
| 5 | 440,640 | 660,960 |

Book value after year 5 (660,960) is still above salvage value (500,000), so no adjustment is needed.

## Example: when the floor bites
<!-- bite: 49ac32f4-c9f1-4d19-acb4-5565076b8093 -->

Here the salvage floor does matter. A generator costs ₦6,000,000, life 4 years, salvage ₦600,000. k = 2/4 = 0.5.

| Year | Opening BV | 0.5 × opening BV | Depreciation charged | Closing BV |
| --- | --- | --- | --- | --- |
| 1 | 6,000,000 | 3,000,000 | 3,000,000 | 3,000,000 |
| 2 | 3,000,000 | 1,500,000 | 1,500,000 | 1,500,000 |
| 3 | 1,500,000 | 750,000 | 750,000 | 750,000 |
| 4 | 750,000 | 375,000 | **150,000** | 600,000 |

In year 4 the formula says 375,000, which would leave 375,000, below the salvage value. So you only charge 750,000 − 600,000 = 150,000. The total is 5,400,000 = FC − SV, as it must be. This example was added for this lesson; lesson 17 uses the same generator for the other methods.

## Common pitfalls
<!-- bite: 6509bbca-b77d-4991-a4d4-c35798aeb7c3 -->

1. **Subtracting salvage in DDB.** The DDB charge is k × opening book value. Salvage is only the floor.
2. **Applying k to the first cost every year.** That's straight line in disguise. DDB applies k to the *opening book value* of each year.
3. **Using k = 1/n for DDB.** Double declining is 2/n.

## Check your understanding
<!-- bite: bfbe7763-add4-4949-b420-6d38521ac5ad -->

Try each one before you open the answer.

1. <!-- q: exact id="f2c30902" answer="1000000" accept="1,000,000|₦1,000,000" -->
   A machine costs ₦9,000,000, has a salvage value of ₦1,000,000 and a life of 8 years. What is its straight line depreciation each year, in naira?

   <details><summary>Answer</summary>

   D = (9,000,000 − 1,000,000) ÷ 8 = ₦1,000,000 a year.

   </details>

2. <!-- q: exact id="55d176db" answer="6000000" accept="6,000,000|₦6,000,000" -->
   A machine costs ₦9,000,000, has a salvage value of ₦1,000,000 and a life of 8 years, depreciated by straight line. What is its book value after 3 years, in naira?

   <details><summary>Answer</summary>

   D = 1,000,000 a year, so BV = 9,000,000 − 3 × 1,000,000 = ₦6,000,000.

   </details>

3. <!-- q: gap id="399ef903" answers="4000000|4,000,000;2400000|2,400,000;2160000|2,160,000" -->
   An asset costs ₦10,000,000 with a 5-year life and is depreciated by double declining balance. Fill in the gaps, in naira. Depreciation in year 1 is ___, depreciation in year 2 is ___, and the book value at the end of year 3 is ___.

   <details><summary>Answer</summary>

   k = 2/5 = 0.4.
   - Year 1: 0.4 × 10,000,000 = 4,000,000, BV 6,000,000.
   - Year 2: 0.4 × 6,000,000 = 2,400,000, BV 3,600,000.
   - Year 3: 0.4 × 3,600,000 = 1,440,000, BV 2,160,000.

   </details>

4. <!-- q: exact id="323658d6" answer="200000" accept="200,000|₦200,000" -->
   An asset costs ₦4,000,000, has a 4-year life and a salvage value of ₦800,000, and is depreciated by double declining balance. After year 2 its book value is ₦1,000,000. How much depreciation is charged in year 3, in naira?

   <details><summary>Answer</summary>

   k = 0.5, so the formula gives 0.5 × 1,000,000 = 500,000, which would leave 500,000, below the ₦800,000 salvage value. So only 1,000,000 − 800,000 = ₦200,000 is charged, and nothing in year 4.

   </details>

5. <!-- q: mcq id="df9fde28" -->
   Why is double declining balance popular for tax purposes?

   - [ ] It writes off more in total than straight line
   - [x] It gives bigger deductions in the early years
   - [ ] It ignores the salvage value completely
   - [ ] It doesn't need the asset's life

   <details><summary>Answer</summary>

   It gives bigger deductions early. The total written off is the same (FC − SV), but bigger early deductions mean the tax saving comes sooner, which is worth more today.

   </details>

## Before moving on
<!-- bite: b28eea0b-4cd0-49b1-be7c-63f1243e6ad0 -->

You can depreciate by straight line and by declining balance, and you can apply the salvage floor. **Next:** [[engineering-economics/17-depreciation-3|Depreciation 3]]: sum-of-the-years digits, units of production and the other methods.

## Related
<!-- bite: 668b14b3-c6bf-4ad0-8ff7-92d3d0792faa -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: d9605132-f318-4955-afed-aa373145adc3 -->

**Level:** Beginner. **Covers:** the three groups of method, straight line with four examples and a book value table, declining and double declining balance, the salvage value floor, and two worked DDB tables.

**Where it sits:** lesson 16 of 38, part 2 of 4 on depreciation.

**Source:** the author's own GEG 501 note, section 7 (lectures 3 and 6 and the FE review slides). The generator DDB example was added for this lesson and is checked by `scripts/diagrams/engineering_economics.py`.
