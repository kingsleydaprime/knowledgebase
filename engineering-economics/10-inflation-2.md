---
id: 2aa3ef98-3f35-4712-8667-2fbfccd5ebd7
---

# Inflation 2: Inflation and Tax

Inflation and tax interact because taxes are charged on nominal values, while what you can actually buy depends on real values.

## Before you start
<!-- bite: 443156d6-5ece-4148-b28c-137928a22a40 -->

You should know nominal and real values from [[engineering-economics/09-inflation-1|Inflation 1]].

After this lesson you will be able to:

1. explain bracket creep and money illusion with a worked example;
2. explain how indexation of tax brackets fixes bracket creep;
3. show how inflation raises company tax through depreciation and FIFO inventory, and why firms prefer LIFO during inflation.

## What inflation does to tax
<!-- bite: 1c845971-5a63-4f1c-b88d-8efd78651fcc -->

Taxes are charged on **nominal** values, but your welfare depends on **real** values. So inflation can raise your tax without raising your real income.

- If nominal income rises 12% and inflation is 10%, real income rises only about 2%.
- In a progressive tax system (higher income, higher tax), inflation pushes you into a higher bracket, you pay more tax, and your real disposable income falls. This is **bracket creep**.

We look at people first (bracket creep and indexation), then at companies (depreciation and inventory).

## Bracket creep: an example
<!-- bite: 585ee1b9-2f68-4df4-943b-9ce9f3895951 -->

**Example:** the tax threshold is ₦1,000,000 and your income is ₦950,000. After 10% inflation your income is 950,000 × 1.1 = ₦1,045,000, now over the threshold, yet your purchasing power has not changed.

Income rising by the same percentage as prices means no real gain. Mistaking the bigger number for a real gain is **money illusion**.

So the government collects more tax from you, and you're not one kobo richer.

## Indexation of tax brackets
<!-- bite: 095b0a6f-0b73-4c0c-87e7-95f27303271c -->

**Indexation of tax brackets** fixes this by adjusting thresholds each year using a price index, usually the CPI. With 10% inflation, the ₦1,000,000 threshold becomes 1,000,000 × 1.1 = ₦1,100,000, so 10% tax applies up to ₦1,100,000 and 20% above it.

Now your ₦1,045,000 is still under the threshold, as it should be, since your real income hasn't changed.

Without indexation: brackets stay in nominal terms, inflation raises nominal wages even if real wages are unchanged, taxpayers cross thresholds because of inflation, government revenue rises automatically, and bracket creep occurs. Indexation is designed to solve exactly these problems.

## Inflation and company tax: depreciation
<!-- bite: c4f15be8-1d29-4dfd-abf2-2630f8022dd7 -->

Companies get a hidden tax rise too, through depreciation. (Depreciation, spreading an asset's cost over its life, has its own lessons from lesson 15. For now, it's a yearly amount a firm subtracts before tax.)

1. **Depreciation** is based on historical cost, not replacement cost. During inflation the allowance is understated in real terms.
2. So taxable profit is overstated.
3. So the effective tax rate goes up.

## Inventory valuation: FIFO and LIFO
<!-- bite: 94cebcab-4e08-4156-906c-4e7ece97d4cb -->

The second route is how a firm values the stock it sells.

- **FIFO** means first in, first out: the oldest stock is sold first.
- **LIFO** means last in, first out: the newest stock is sold first.

When prices are rising, the oldest stock is the cheapest. So the method changes the cost the firm reports, and with it the profit and the tax.

## Worked example: FIFO in inflation
<!-- bite: c0abc109-ac07-4d2b-99a7-addeaa37595b -->

A firm buys 100 units at ₦10 (January), 100 at ₦12 (March) and 100 at ₦14 (May). It sells 150 units at ₦20 each, so revenue is ₦3,000.

- FIFO cost of goods sold = (100 × 10) + (50 × 12) = ₦1,600. Profit = 3,000 − 1,600 = ₦1,400.
- Replacing the stock at today's price costs 150 × 14 = ₦2,100. Profit at current cost = 3,000 − 2,100 = ₦900.
- So FIFO overstates profit by ₦500. Why: FIFO uses old, low costs while revenue reflects today's higher prices.

## The hidden tax increase
<!-- bite: 5bd7968d-92da-4f11-9b2c-dd0ea6b98c0e -->

Part of that ₦1,400 profit is only due to inflation, not real productive profit. It is called an **inventory holding gain** or paper gain.

Because accounting profit is higher, the firm pays more company tax although real profit did not rise. So **inflation + FIFO = a hidden tax increase**, and the reverse happens under LIFO. That is why firms prefer LIFO during inflation.

That finishes part 2: you can now move money through time and allow for inflation. Part 3 uses all of it to answer the question the course is for: which project should we pick?

## Check your understanding
<!-- bite: 4d80e10f-486b-48f1-a36c-7c2444d84246 -->

Try each one before you open the answer.

1. <!-- q: mcq id="895d4fd9" -->
   Your income rises from ₦800,000 to ₦880,000 in a year when prices also rise 10%. You feel richer and spend more. What is this called?

   - [ ] Bracket creep
   - [x] Money illusion
   - [ ] Indexation
   - [ ] An inventory holding gain

   <details><summary>Answer</summary>

   Money illusion: mistaking a bigger nominal number for a real gain. Income rose by the same percentage as prices, so there is no real gain.

   </details>

2. <!-- q: exact id="b67854a6" answer="2300000" accept="2,300,000|₦2,300,000" -->
   A tax threshold is ₦2,000,000 and inflation this year is 15%. With indexation of tax brackets, what is next year's threshold, in naira?

   <details><summary>Answer</summary>

   2,000,000 × 1.15 = ₦2,300,000.

   </details>

3. <!-- q: gap id="950e5b93" answers="16000;14000;2000" -->
   A shop buys 200 units at ₦50, then 200 units at ₦60. It sells 300 units at ₦100 each (revenue ₦30,000). Today's price to replace stock is ₦60. Fill in the gaps. FIFO cost of goods sold is ₦___, FIFO profit is ₦___, and FIFO overstates profit compared with current cost by ₦___.

   <details><summary>Answer</summary>

   - FIFO cost of goods sold = 200 × 50 + 100 × 60 = ₦16,000, so profit = 30,000 − 16,000 = ₦14,000.
   - At current cost: 300 × 60 = ₦18,000, so profit = ₦12,000.
   - FIFO overstates profit by 14,000 − 12,000 = ₦2,000, a paper gain.

   </details>

4. <!-- q: mcq id="57a3ce7a" -->
   During inflation, why is a firm's depreciation allowance understated in real terms?

   - [ ] Because depreciation is based on replacement cost
   - [x] Because depreciation is based on historical cost
   - [ ] Because depreciation is not tax-deductible
   - [ ] Because LIFO is used

   <details><summary>Answer</summary>

   Depreciation is based on historical cost, not replacement cost. So it is too small in real terms, taxable profit is overstated, and the effective tax rate goes up.

   </details>

5. <!-- q: open id="c8fcd473" -->
   Why do firms prefer LIFO to FIFO during inflation?

   <details><summary>Answer</summary>

   During inflation the oldest stock is the cheapest. FIFO charges that old, low cost against revenue at today's higher prices, so it reports a higher profit. Part of that profit is only an inventory holding (paper) gain caused by inflation, but the firm still pays company tax on it. LIFO charges the newest, dearer stock, so reported profit is closer to real profit and the firm pays less tax.

   </details>

## Before moving on
<!-- bite: be899c24-1db1-4983-a8a1-6160d0c632bc -->

You can explain bracket creep, money illusion and indexation, and show how depreciation and FIFO raise company tax during inflation. **Next:** [[engineering-economics/11-comparing-alternatives-1|Comparing Alternatives 1]]: the ground rules, the MARR, and the present worth method.

## Related
<!-- bite: cf016ae4-c5c1-47ae-aafb-9f493046484b -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 26612949-b66f-4a13-a280-c58cc6223ec5 -->

**Level:** Beginner. **Covers:** inflation and personal tax (bracket creep, money illusion, indexation), and inflation and company tax (depreciation and FIFO and LIFO inventory valuation).

**Where it sits:** lesson 10 of 38, part 2 of 2 on inflation, and the end of part 2 (time value of money).

**Source:** the author's own GEG 501 note, section 5.
