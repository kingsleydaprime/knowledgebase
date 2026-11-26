---
id: efa7ed65-3d80-4da0-a3fe-0e82e206eaf5
---

# Depreciation 4: Depreciation, Tax and Cash Flow

Depreciation changes cash flow through tax: it is deducted before tax is worked out, so the firm pays less tax.

## Before you start
<!-- bite: be80b4e3-3275-4689-b4b8-78484c02362c -->

You should know the four depreciation methods from [[engineering-economics/16-depreciation-2|Depreciation 2]] and [[engineering-economics/17-depreciation-3|Depreciation 3]], and present worth from [[engineering-economics/11-comparing-alternatives-1|Comparing Alternatives 1]].

After this lesson you will be able to:

1. calculate the yearly tax saving from depreciation;
2. work out a project's annual after-tax cash flow from sales, expenses, depreciation and the tax rate;
3. explain how the depreciation method affects the timing of cash flow, the NPV and the tax liability.

## What depreciation does to tax
<!-- bite: a9f60f66-99fa-4b1b-8366-0431b7766d12 -->

Remember that depreciation is not a cash outflow (lesson 15)? It's a bookkeeping entry. So how can it change cash? Through tax.

- Expenses and depreciation are tax-deductible, revenues are taxed.
- So the yearly **tax saving from depreciation** = D × tax rate.

If a firm charges ₦1,000,000 of depreciation and the tax rate is 30%, its taxable profit is ₦1,000,000 lower, so it pays ₦300,000 less tax. That ₦300,000 is real money that stays in the firm.

## Other tax points
<!-- bite: 09e82ae4-a38c-4c7a-919c-cbfee9c5e383 -->

- If you sell an asset for more than its book value, the difference is taxed.
- A tax credit is a one-time benefit that is subtracted from income tax.
- In inflation, depreciation on historical cost is understated, which overstates profit and tax (lesson 10).

## The annual cash flow formula
<!-- bite: 317753d8-e228-4bfd-94bd-133c23ed4812 -->

Here's how depreciation enters a project's cash flow. Gross profit is sales minus expenses. Depreciation reduces tax but is not a cash cost. So you subtract depreciation to work out the tax, then add it back to get the cash:

$$GP = S - E, \quad NP = (GP - D)(1 - t), \quad CF = NP + D = GP(1-t) + D\,t$$

S is sales, E expenses, D depreciation, t the tax rate, NP net profit and CF the cash flow.

The last form says it neatly: the cash flow is the after-tax gross profit plus the tax saving from depreciation, D × t.

## Example: the annual cash flow
<!-- bite: c09641c3-d2f9-4bee-88ca-f7425184af17 -->

Sales 500, expenses 300, so GP = 200. Depreciation D = 50, tax rate 30%.

1. Tax = (200 − 50) × 0.3 = 45.
2. NP = 200 − 50 − 45 = 105.
3. CF = 105 + 50 = 155.
4. Check: 200 × 0.7 + 50 × 0.3 = 140 + 15 = 155.

The cash flow is higher when depreciation is claimed, because of the tax it saves. Without depreciation the firm would pay 60 in tax and keep only 140.

## Why the method matters: timing
<!-- bite: 675af0be-10b7-478d-9fee-43821294cf55 -->

Every method writes off the same total, so every method saves the same total tax. But an accelerated method (DDB, SYD) brings the tax saving earlier, which has a higher present value.

**Example:** an asset costs ₦1,000,000, no salvage, 4-year life. The tax rate is 30% and the MARR is 10%.

- **Straight line:** D = 250,000 a year, so the tax saving is 75,000 a year. PV = 75,000 × 3.1699 = **₦237,740**.
- **SYD:** D = 400,000, 300,000, 200,000, 100,000, so the tax savings are 120,000, 90,000, 60,000, 30,000. PV = 120,000/1.1 + 90,000/1.1² + 60,000/1.1³ + 30,000/1.1⁴ = **₦249,040**.

Both save ₦300,000 in total, but SYD's savings are worth about ₦11,300 more today. This example was added for this lesson.

## How the method affects cash flow, NPV and tax
<!-- bite: a86a3134-4dce-443a-964e-15d52644447b -->

This is a 3-mark part of the 2025/2026 exam, so here it is in one place.

1. **Cash flow timing:** an accelerated method gives bigger deductions early, so tax is lower and cash flow is higher in the early years, and lower in the later years.
2. **Net present value:** the total tax saved is the same, but money received earlier is worth more, so an accelerated method gives a higher NPV.
3. **Tax liability:** total tax over the life is the same (if the tax rate doesn't change), but tax is deferred: less is paid early and more later. In effect the firm gets an interest-free loan from the government.

## Inflation in project cash flows
<!-- bite: c3f859a7-2215-4892-9a1f-eb3e0cc8d4ca -->

If a project's revenues and expenses both rise with inflation, you discount with the combined rate $(1 + i_{\text{comb}}) = (1 + i)(1 + f)$ (lesson 09). Depreciation is **not** inflated, because it is based on the original cost.

That's why mixing real and nominal values is dangerous. Use real cash flows with a real rate, or nominal cash flows with a nominal rate, and remember that depreciation's tax saving is fixed in nominal naira, so in real terms it shrinks each year.

That finishes depreciation. All of parts 3 and 4 assumed you already *had* numbers for first cost, yearly cost and salvage value. Part 5 is about where those numbers come from: cost estimation.

## Check your understanding
<!-- bite: 71599502-989c-48d1-b7b2-40f7c930b813 -->

Try each one before you open the answer.

1. <!-- q: exact id="0ea93ea4" answer="600000" accept="600,000|₦600,000" -->
   A firm charges ₦2,000,000 of straight line depreciation a year, and the tax rate is 30%. What is the yearly tax saving from depreciation, in naira?

   <details><summary>Answer</summary>

   Tax saving = D × t = 2,000,000 × 0.30 = ₦600,000 a year.

   </details>

2. <!-- q: exact id="ee1fb51f" answer="275" -->
   A project has sales of 800, expenses of 450 and depreciation of 100 in a year. The tax rate is 30%. What is its after-tax cash flow for the year?

   <details><summary>Answer</summary>

   GP = 800 − 450 = 350. CF = GP(1 − t) + D × t = 350 × 0.7 + 100 × 0.3 = 245 + 30 = 275.

   </details>

3. <!-- q: exact id="d1031a04" answer="175" -->
   A project has sales of 800, expenses of 450 and depreciation of 100 in a year. The tax rate is 30%. What is its net profit after tax?

   <details><summary>Answer</summary>

   NP = (GP − D)(1 − t) = (350 − 100) × 0.7 = 175. Adding back depreciation gives the cash flow, 275.

   </details>

4. <!-- q: mcq id="0864f292" -->
   An asset costs ₦600,000 with a 3-year life and no salvage. The tax rate is 30% and the MARR is 12%. Straight line gives tax savings of ₦60,000 a year (PV ₦144,110). SYD gives ₦90,000, ₦60,000 and ₦30,000 (PV ₦149,542). Which statement is true?

   - [ ] SYD saves more tax in total
   - [x] Both save ₦180,000 in total, but SYD's savings have a higher present value
   - [ ] Straight line gives the higher NPV
   - [ ] The method makes no difference to NPV

   <details><summary>Answer</summary>

   Both save 600,000 × 0.3 = ₦180,000 in total. SYD saves more in the early years, and money earlier is worth more, so its PV is higher and the project's NPV is higher.

   </details>

5. <!-- q: mcq id="895d4fda" -->
   A project's revenues and expenses are forecast in nominal naira, rising with inflation. Which of these should NOT be inflated?

   - [ ] Revenues
   - [ ] Operating expenses
   - [x] Depreciation
   - [ ] Maintenance cost

   <details><summary>Answer</summary>

   Depreciation. It is based on the original cost, so it stays fixed in nominal naira.

   </details>

6. <!-- q: open id="b67854a7" -->
   Under inflation, why is consistency between real and nominal cash flows critical in project evaluation?

   <details><summary>Answer</summary>

   Nominal cash flows include inflation and real cash flows don't. If you discount nominal cash flows with a real rate, you count inflation as if it were real gain and overstate the NPV. If you discount real cash flows with a nominal rate, you take inflation off twice and understate the NPV. So real cash flows must go with a real rate and nominal cash flows with a nominal rate (linked by the Fisher equation). Depreciation needs care: it is fixed in nominal terms, so its tax saving loses real value as prices rise.

   </details>

## Before moving on
<!-- bite: 173b79d0-f7df-49c8-ba0b-bde82f9d89dc -->

You can work out the tax saving from depreciation, build an after-tax cash flow, and explain how the method changes cash flow timing, NPV and tax. **Next:** [[engineering-economics/19-cost-estimation-1|Cost Estimation 1]]: where the numbers come from.

## Related
<!-- bite: 18e36e43-9b1d-4d20-8864-88fe02339dca -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: b6e3a9db-e1a8-4194-8c98-d7eebd49cdce -->

**Level:** Beginner to intermediate. **Covers:** the tax saving from depreciation, other tax points, the annual cash flow formula and example, the present value of tax savings under straight line and SYD, how the method affects cash flow, NPV and tax, and inflation in project cash flows.

**Where it sits:** lesson 18 of 38, part 4 of 4 on depreciation, and the end of part 4.

**Source:** the author's own GEG 501 note, sections 7 and 14.5. The straight line and SYD tax-saving comparison, and the three-point answer on cash flow, NPV and tax, were added for this lesson.
