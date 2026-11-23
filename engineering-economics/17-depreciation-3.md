---
id: d8d1bbda-6540-462d-8b70-8fe3beec80af
---

# Depreciation 3: Sum-of-the-Years Digits, Units of Production and Others

Sum-of-the-years digits charges a shrinking fraction each year, and units of production charges by how much the asset is used.

## Before you start
<!-- bite: 9fc271c0-ee4e-4075-8789-8a2df1ff8ef4 -->

You should know straight line and double declining balance from [[engineering-economics/16-depreciation-2|Depreciation 2]].

After this lesson you will be able to:

1. depreciate an asset by sum-of-the-years digits (SYD) and check the total;
2. depreciate an asset by units of production;
3. describe ACRS, MACRS and sinking-fund depreciation, use the accumulated depreciation and book value relationships, and compare how fast the methods write an asset off.

## What sum-of-the-years digits is
<!-- bite: 34a193b5-0e0d-46d5-901e-803f23f9a362 -->

Remember that declining balance is accelerated: it charges most in the early years. SYD is another accelerated method, but it reaches the salvage value exactly, with no floor rule needed.

Write the digits of the life, add them, and charge each year a fraction using the remaining life. For a 4-year life, the digits are 4, 3, 2, 1, which add to 10. So year 1 gets 4/10 of the depreciable amount, year 2 gets 3/10, and so on.

## The sum-of-the-years digits formula
<!-- bite: 25324d2d-9355-4be8-b631-747addaf828f -->

The sum of the digits from 1 to n is n(n + 1)/2. Each year's charge is the remaining life over that sum, times the depreciable amount:

$$SYD = \frac{n(n+1)}{2} \qquad D_t = \frac{RF}{SYD}\,(FC - SV)$$

RF is the remaining life at the start of the year (n for year 1, n−1 for year 2, and so on).

## Example: the generator by SYD
<!-- bite: cbc0c85f-e94b-48b2-9324-293fcd6c4f97 -->

**Example (lecture 6):** a generator costs ₦6,000,000, salvage ₦600,000, life 4 years. The depreciable base is 5,400,000 and SYD = 4 × 5/2 = 10.

| Year | RF | Fraction | Depreciation |
| --- | --- | --- | --- |
| 1 | 4 | 4/10 | 2,160,000 |
| 2 | 3 | 3/10 | 1,620,000 |
| 3 | 2 | 2/10 | 1,080,000 |
| 4 | 1 | 1/10 | 540,000 |

The total is 5,400,000, which equals FC − SV. Always use this as your check.

## Units of production (usage-based)
<!-- bite: e1cef63f-3145-42d4-aba4-1b323008a580 -->

Depreciation follows how much the asset is used, not time. A machine that sits idle all year hardly wears out, so why charge it the same as a machine that ran day and night?

You find the depreciation for each unit of output, then multiply by the units produced that year:

$$\text{Depreciation per unit} = \frac{FC - SV}{\text{total expected units}} \qquad D_t = \text{per unit} \times \text{units produced in year } t$$

## Example: units of production
<!-- bite: e795178b-159d-4c7e-8500-bf1c648515fb -->

**Class exercise (lecture 6):** a machine costs ₦15,000,000, salvage ₦3,000,000, expected output 120,000 units. Actual output is 20,000 (year 1), 30,000 (year 2) and 25,000 (year 3). Find the depreciation each year and the book value after year 3.

- Per unit = 12,000,000 ÷ 120,000 = ₦100
- Year 1: 20,000 × 100 = ₦2,000,000
- Year 2: 30,000 × 100 = ₦3,000,000
- Year 3: 25,000 × 100 = ₦2,500,000
- Book value after year 3 = 15,000,000 − 7,500,000 = **₦7,500,000**

(The cost was hard to read in your lecture note. A classmate's note shows ₦15,000,000, which is what I used. If your question paper says another figure, change the first cost and redo the per-unit depreciation.)

## Other methods: ACRS, MACRS and sinking fund
<!-- bite: 849b0b06-06bd-4bd7-b229-bcdfbef823db -->

- **ACRS:** the Accelerated Cost Recovery System (used in the FE review slides) takes the depreciation each year as cost times a table factor, and ignores salvage value. Example: cost $9,000 with factors 0.10, 0.18, 0.144 gives $900, $1,620 and $1,296, so book value after 3 years is $5,184. Compare with $6,360 under straight line (lesson 16).
- **MACRS:** a legal depreciation method used in the USA. It starts with double declining balance and switches to straight line, uses the half-year rule, and does not subtract salvage. In your course the main methods are straight line, double declining balance, sum-of-the-years digits and units of production.
- **Sinking-fund depreciation:** the yearly charge is the amount you would deposit each year to build up (original value − salvage value) by the end of the life. It uses the A/F factor from lesson 06: D = (FC − SV)(A/F, i, n).

## Handy relationships
<!-- bite: 3cc318f3-cb26-4803-ad61-ff56289cc09d -->

Two lines that hold for every method:

- Accumulated depreciation (AD) at year t = AD(t−1) + D(t).
- Book value at year t = BV(t−1) − D(t) = FC − AD(t).

## Comparing the methods on one asset
<!-- bite: e078558d-8d41-4cfb-8e4b-1a2acf1ab9c3 -->

Here is the same generator (₦6,000,000, salvage ₦600,000, 4 years) by three methods. Straight line charges ₦1,350,000 every year. SYD's book values are 3.84, 2.22, 1.14 and 0.6 million. DDB's are 3.0, 1.5, 0.75 and 0.6 million (from lesson 16).

![Book value of a 6 million naira generator over 4 years under straight line, sum-of-the-years digits and double declining balance: all three start at 6 million and end at the 600,000 salvage value, but double declining balance falls fastest, sum-of-the-years digits next, and straight line falls in a straight line](images/ee-book-value-methods.svg)

All three end at the same place, ₦600,000. The accelerated methods just get there faster. Why would a firm want that? Because depreciation cuts tax, and a tax saving today is worth more than one later. That's the next lesson.

## Check your understanding
<!-- bite: 6ffaaaa5-d77a-42ea-8351-44cedd11af87 -->

Try each one before you open the answer.

1. <!-- q: exact id="72693227" answer="15" -->
   An asset has a useful life of 5 years. What is the sum of the years' digits?

   <details><summary>Answer</summary>

   SYD = n(n + 1)/2 = 5 × 6/2 = 15 (or 5 + 4 + 3 + 2 + 1).

   </details>

2. <!-- q: gap id="9d4152be" answers="500000|500,000;300000|300,000" -->
   A machine costs ₦1,600,000, has a salvage value of ₦100,000 and a life of 5 years. It is depreciated by sum-of-the-years digits. Fill in the gaps, in naira. Depreciation in year 1 is ___ and in year 3 is ___.

   <details><summary>Answer</summary>

   Depreciable base = 1,500,000 and SYD = 15.
   - Year 1: 5/15 × 1,500,000 = 500,000.
   - Year 3: remaining life at the start of year 3 is 3, so 3/15 × 1,500,000 = 300,000.

   </details>

3. <!-- q: exact id="8c070063" answer="1500000" accept="1,500,000|₦1,500,000" -->
   A compressor costs ₦8,000,000, has a salvage value of ₦500,000 and is expected to run 150,000 hours in its life. This year it ran 30,000 hours. What is this year's units-of-production depreciation, in naira?

   <details><summary>Answer</summary>

   Per hour = (8,000,000 − 500,000) ÷ 150,000 = ₦50. This year: 30,000 × 50 = ₦1,500,000.

   </details>

4. <!-- q: mcq id="04020a91" -->
   Which depreciation method ignores salvage value and uses a factor from a table each year?

   - [ ] Straight line
   - [ ] Sum-of-the-years digits
   - [x] ACRS
   - [ ] Units of production

   <details><summary>Answer</summary>

   ACRS (the Accelerated Cost Recovery System). MACRS, its US successor, also ignores salvage.

   </details>

5. <!-- q: exact id="ab5e584e" answer="163797.48" sigfigs="4" tolerance="100" -->
   An asset costs ₦1,000,000 with no salvage value and a 5-year life. Using sinking-fund depreciation at 10%, with (A/F, 10%, 5) = 0.1638, what is the yearly charge, in naira?

   <details><summary>Answer</summary>

   D = (FC − SV)(A/F) = 1,000,000 × 0.1638 = ₦163,800 a year (₦163,797 with the exact factor). Deposited every year at 10%, it builds up exactly ₦1,000,000 by year 5.

   </details>

6. <!-- q: mcq id="35ed42b9" -->
   Two firms buy identical machines. One uses straight line, the other sum-of-the-years digits, with the same life and salvage value. Which statement is true?

   - [ ] SYD writes off more in total
   - [x] Both write off the same total, but SYD writes off more in the early years
   - [ ] Straight line writes off more in the early years
   - [ ] SYD ends below the salvage value

   <details><summary>Answer</summary>

   Both write off FC − SV in total. SYD is accelerated, so more of it comes in the early years.

   </details>

## Before moving on
<!-- bite: 40d3e7fe-047b-495d-ba5b-f2088d05d8ed -->

You can depreciate by SYD and units of production, describe ACRS, MACRS and sinking-fund depreciation, and compare the pace of the methods. **Next:** [[engineering-economics/18-depreciation-4|Depreciation 4]]: depreciation, tax and cash flow.

## Related
<!-- bite: 6659c3db-20d5-4f9c-92ce-87eb8b8c2389 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: c8a4ca13-28fd-4a83-b4a6-355f1b4f9469 -->

**Level:** Beginner. **Covers:** sum-of-the-years digits with the lecture's generator, units of production with the lecture's class exercise, ACRS, MACRS, sinking-fund depreciation, the accumulated depreciation and book value relationships, and a picture comparing three methods.

**Where it sits:** lesson 17 of 38, part 3 of 4 on depreciation.

**Source:** the author's own GEG 501 note, sections 7 and 14.5. The picture and its numbers come from `scripts/diagrams/engineering_economics.py`.
