---
id: be90db6b-61ab-4e57-9b4b-40cdeb44862f
---

# Comparing Alternatives 4: Benefit-Cost Ratio, Payback and Choosing a Method

The benefit-cost ratio divides a project's discounted benefits by its discounted costs, and the payback period counts the years it takes to get the first cost back.

## Before you start
<!-- bite: f299e406-2a56-4065-a131-2037fb7a80b8 -->

You should know present worth and IRR from [[engineering-economics/11-comparing-alternatives-1|Comparing Alternatives 1]] and [[engineering-economics/13-comparing-alternatives-3|Comparing Alternatives 3]].

After this lesson you will be able to:

1. calculate a benefit-cost ratio (BCR) and use it to accept a project or choose between two;
2. calculate simple and discounted payback, return on investment and payout time, and say what each ignores;
3. pick the right comparison method for a question.

## What the benefit-cost ratio is
<!-- bite: af1870e4-ee76-4abb-a587-53df859cfce1 -->

The BCR is common for public projects such as roads, bridges and water supply. A government doesn't sell a road, so it doesn't earn a "return" in the usual sense. Instead it asks: for every naira we spend, how many naira of benefit do citizens get?

You divide the present value of the benefits by the present value of the costs:

$$BCR = \frac{PV(B)}{PV(C)}$$

- BCR > 1: accept. BCR < 1: reject. BCR = 1: break even, neither profit nor loss.
- Equivalent test: B − C ≥ 0.

## Benefit-cost examples
<!-- bite: e2b86d16-d6ea-4fff-80f8-a772daf8d199 -->

**Example:** a road project has PV(B) = ₦18bn and PV(C) = ₦12bn. BCR = 1.5, so accept. Meaning: every ₦1 spent returns ₦1.50 in benefits.

> **Correction:** your lecture 5 writes this as "₦1.50k". It is a ratio: ₦1.50 of benefit per ₦1 of cost.

**Example (FE review):** first cost $40M, capitalized perpetual annual cost $12M, capitalized benefit $49M, no residual value. B − C = 49 − 52 = −$3M, so do not undertake it. (Capitalized cost is the A/i idea from lesson 08.)

## Choosing between projects by BCR
<!-- bite: b24192b9-c785-4eda-8699-5df130a1c056 -->

**Mutually exclusive projects (lecture 5):** A has PV(B) = 15 and PV(C) = 10, so BCR = 1.50. B has PV(B) = 20 and PV(C) = 14, so BCR = 1.43. Both are acceptable. Your lecture picks A because it has the highest BCR.

> **Caution (general knowledge, not from your notes):** choosing by the highest BCR alone can mislead, for the same reason as IRR in lesson 13. The extra step from A to B costs 4 more and brings 5 more benefit, an incremental BCR of 5/4 = 1.25. That is above 1, so B adds value if money is not limited. If your exam asks you to pick "the highest BCR", follow the lecture. If it asks for the best use of money, check the incremental BCR too.

## Payback period
<!-- bite: aec11e0e-ed07-4c67-8e02-3ba3fc001422 -->

The payback period is the time needed for the cash inflows to recover the first cost. With equal yearly inflows it is just a division:

$$\text{Payback} = \frac{\text{first cost}}{\text{yearly inflow}}$$

It is simple and shows how fast you get your money back, but it ignores what happens after payback.

The **discounted payback** does the same after discounting each inflow, so it is always longer. Example from the SFPE chapter: undiscounted, sprinklers were said to pay back in 4 to 7 years, but after discounting at 10% the payback was 5 to 11 years.

The **discounted break-even period** is the same idea: the time for the cumulative *discounted* cash flow to reach zero.

## More profitability measures
<!-- bite: 48b349d0-f723-480a-b64c-a6b187310124 -->

These come from your "TVM and other stuff" note.

- **Return on investment (ROI)** = annual profit ÷ fixed capital × 100. For example, a profit of ₦20 million a year on ₦100 million is 20%. It ignores the time value of money.
- **Payout (payback) time** = (fixed capital + start-up cost) ÷ annual cash flow. It ignores interest and anything after the payback point.
- **Discounted cash flow rate of return (DCFROR)** is the same as IRR: the rate that makes NPV zero. It is not the bank rate. Compare it with a required return that is higher than the bank rate, because a business carries risk and effort.
- **NPV** = present value of the cash flows minus the investment. A positive NPV means the project earns more than leaving the money in the bank at the chosen rate.

The two criteria that fully recognise the timing of cash flows are NPV and IRR. ROI (the accounting rate of return) and payback do not.

## Quick guide: which method?
<!-- bite: f2a2b7b4-a50d-4e9d-be94-eadbc3622ee2 -->

| Method | Answer is | Accept if | Best when |
| --- | --- | --- | --- |
| PW or NPW | A naira value today | PW > 0, pick the highest | Same lives |
| AW or EAC | A naira value per year | AW > 0, pick the highest (or the lowest cost) | Different lives |
| FW | A naira value at the end | FW > 0 | You care about value at the end |
| IRR | A percentage | IRR ≥ MARR | You want a rate (use incremental IRR to rank) |
| BCR | A ratio | BCR > 1 | Public projects |
| Payback | Years | Short enough | A quick screen only |

That finishes comparing alternatives. All these methods used cash flows. Part 4 is about something that isn't a cash flow at all, but still changes the cash: depreciation.

## Check your understanding
<!-- bite: 7a1ce664-e26a-4892-b7a6-732810f3a913 -->

Try each one before you open the answer.

1. <!-- q: exact id="a2ac4af7" answer="0.75" accept="3/4" -->
   A water supply scheme has a present value of benefits of ₦9 billion and a present value of costs of ₦12 billion. What is its benefit-cost ratio?

   <details><summary>Answer</summary>

   BCR = 9 ÷ 12 = 0.75. It is below 1, so reject: each ₦1 spent returns only 75 kobo of benefit.

   </details>

2. <!-- q: exact id="6e38e15a" answer="1.5" accept="1.50" -->
   Two bridge designs are mutually exclusive. Design P has PV(B) = 30 and PV(C) = 20. Design Q has PV(B) = 39 and PV(C) = 26. What is the incremental BCR of moving from P to Q?

   <details><summary>Answer</summary>

   Extra benefit = 39 − 30 = 9. Extra cost = 26 − 20 = 6. Incremental BCR = 9 ÷ 6 = 1.5. It is above 1, so the extra spending on Q adds value. (Both designs have a BCR of exactly 1.5 on their own.)

   </details>

3. <!-- q: exact id="1b13256f" answer="5" accept="5 years" -->
   A machine costs ₦300,000 and brings in ₦60,000 a year. What is its simple payback period, in years?

   <details><summary>Answer</summary>

   300,000 ÷ 60,000 = 5 years.

   </details>

4. <!-- q: mcq id="ef1f6726" -->
   A project costs ₦200,000 and brings in ₦50,000 at the end of each year. Its simple payback is 4 years. At 10%, the cumulative discounted cash flow is −₦10,461 after year 5 and +₦17,763 after year 6. What is its discounted payback?

   - [ ] 4 years
   - [ ] Between 4 and 5 years
   - [x] Between 5 and 6 years
   - [ ] More than 6 years

   <details><summary>Answer</summary>

   Between 5 and 6 years: the cumulative discounted cash flow turns positive during year 6. Discounted payback is always longer than simple payback.

   </details>

5. <!-- q: mcq id="5308a1b8" -->
   Which two criteria fully recognise the timing of cash flows?

   - [ ] Payback period and accounting rate of return
   - [x] Net present value and internal rate of return
   - [ ] Return on investment and payback period
   - [ ] Accounting rate of return and net present value

   <details><summary>Answer</summary>

   NPV and IRR. Payback and the accounting rate of return (ROI) ignore the time value of money.

   </details>

6. <!-- q: exact id="78f8cef7" answer="15" accept="15%" -->
   A plant needs ₦80 million of fixed capital and makes an annual profit of ₦12 million. What is its return on investment, in percent?

   <details><summary>Answer</summary>

   ROI = 12 ÷ 80 × 100 = 15%. It ignores the time value of money.

   </details>

## Before moving on
<!-- bite: 6c8f1e8e-d0ca-4723-90d5-e77bc50581ed -->

You can use the BCR (and its incremental form), payback, discounted payback, ROI and payout time, and pick the right method. **Next:** [[engineering-economics/15-depreciation-1|Depreciation 1]]: what depreciation is and why we calculate it.

## Related
<!-- bite: 52dd4a4a-2d2c-442f-a3eb-fe295e3f0180 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: b17001e6-8a40-4f94-bc10-96e3e4608eff -->

**Level:** Beginner. **Covers:** the benefit-cost ratio with three examples, incremental BCR, payback and discounted payback, ROI, payout time, DCFROR, NPV, and the quick guide to the six methods.

**Where it sits:** lesson 14 of 38, part 4 of 4 on comparing alternatives.

**Source:** the author's own GEG 501 note, sections 6 and 14.5. The incremental BCR caution is general knowledge, not from the lecture materials.
