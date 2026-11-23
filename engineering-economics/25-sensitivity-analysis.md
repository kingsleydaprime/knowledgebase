---
id: cadce37d-e138-480c-8afc-f41c268b5cb5
---

# Sensitivity Analysis

Sensitivity analysis asks: if one estimate turns out different, does my decision change?

## Before you start
<!-- bite: 1ed0a280-72e0-4bb5-ad41-5d81bb3dc1f0 -->

You should know present worth from [[engineering-economics/11-comparing-alternatives-1|Comparing Alternatives 1]] and the idea of risk from [[engineering-economics/22-risk-and-uncertainty-1|Risk and Uncertainty 1]].

After this lesson you will be able to:

1. carry out a sensitivity analysis on a project's present worth, one variable at a time;
2. find a break-even (switching) value, and read a spider diagram;
3. give the advantages and limits of sensitivity analysis, and say how scenario analysis differs.

## What sensitivity analysis is
<!-- bite: 16926caf-0439-42aa-a7b0-2ccfab1f6b22 -->

Every estimate in a project (cost, sales, life, interest rate) can be wrong. **Sensitivity analysis** asks: if one estimate turns out different, does my decision change? It is the simplest way to test risk (lesson 22) without needing probabilities.

Think of planning a trip to Lagos on ₦50,000. What if fuel costs 20% more? What if the bus fare doubles? If the trip still works under either, your plan is safe. If a 10% rise in fuel ruins it, you know fuel is the number to watch. That's sensitivity analysis.

## How to do it
<!-- bite: e35d22dd-6c80-40f9-bc00-3dd0d66bafb7 -->

1. Work out the base case, for example the PW using your best estimates.
2. Change **one** variable at a time (say by −20%, −10%, +10%, +20%) and keep the others fixed.
3. Recalculate PW (or IRR, or AW) each time.
4. Find which variable moves the result most. That is the variable you must estimate most carefully.
5. Find the **break-even (switching) value**: how far a variable can move before PW hits zero and the decision flips.

## Example: changing the annual benefit
<!-- bite: fdaef46f-3c23-4120-a020-7d28ae926ecc -->

Invest ₦100 million now, receive ₦30 million a year for 5 years, MARR 10%. The P/A factor is 3.7908.

| Annual benefit | PW (₦ million) | Decision |
| --- | --- | --- |
| 24 (−20%) | −9.02 | Reject |
| 30 (base) | +13.72 | Accept |
| 36 (+20%) | +36.47 | Accept |

The break-even annual benefit is 100 ÷ 3.7908 = ₦26.38 million. So the benefit can fall about 12% before the project stops being worth doing. The decision is sensitive to the annual benefit.

## The spider diagram
<!-- bite: 4c3dcd62-d560-4a8e-9ee1-e5639195762c -->

Results are often shown as a table like the one above, or as a **spider diagram**: a line for each variable, plotting PW against % change. The steepest line is the most sensitive variable.

Here is the same project with three variables changed in turn: the annual benefit, the first cost and the MARR.

![Spider diagram for a 100 million naira project returning 30 million a year for 5 years at 10 percent: present worth against percentage change from minus 20 to plus 20 percent, with a steep rising line for annual benefit that crosses zero near minus 12 percent, a falling line for first cost that crosses zero near plus 14 percent, and a gentle falling line for the interest rate that stays positive](images/ee-spider-diagram.svg)

## Reading the spider diagram
<!-- bite: 015f3645-e5ed-4228-9466-4d4a89c004ba -->

What does the picture say? The benefit line is steepest, so the annual benefit matters most. The first cost is close behind: a 14% overrun wipes out the PW. The MARR line is flattest, so even a 20% change in the rate leaves the project worth doing. (The first cost and MARR lines were added for this lesson.)

## Scenario analysis
<!-- bite: 026ec5fd-0285-454a-bf1f-14af57d9b2ef -->

A **scenario analysis** goes a step further and changes several variables together (best case, base case, worst case).

For example, a worst case might be benefit −20%, first cost +10% and MARR +20%, all at once. Real problems often come in groups (a recession lowers sales *and* raises borrowing cost), and scenario analysis captures that.

## Advantages and limits
<!-- bite: f239c4d1-63b4-41ed-819d-3a151dab2c01 -->

**Advantages:** simple, needs no probabilities, shows which estimates matter, and shows where to collect more data.

**Limits:** it changes one variable at a time, although in real life variables move together; it does not say how likely a change is; and the ranges chosen (±20%) are arbitrary.

**How reliable are the inputs?** Forecasts of sales volume, product price, tax rate, inflation and risk are the least reliable and have the biggest effect on profitability. Installed cost, working capital and operating costs are better known but still matter a lot. This is why sensitivity analysis is used.

That finishes part 6. Break-even analysis in part 7 is a close cousin: it finds the one sales level where profit switches from loss to gain.

## Check your understanding
<!-- bite: 028ecba1-7389-4824-b742-c656e926acc9 -->

Try each one before you open the answer.

1. <!-- q: exact id="c6199c0f" answer="4.0716" sigfigs="3" tolerance="0.02" -->
   A project costs ₦50 million and returns ₦15 million a year for 5 years. The MARR is 12%, so (P/A, 12%, 5) = 3.6048. What is its base-case PW, in millions of naira?

   <details><summary>Answer</summary>

   PW = −50 + 15 × 3.6048 = −50 + 54.07 = ₦4.07 million. Positive, so accept.

   </details>

2. <!-- q: exact id="7f42ac42" answer="13.870" sigfigs="3" tolerance="0.02" -->
   A project costs ₦50 million and returns an equal benefit each year for 5 years. The MARR is 12%, so (P/A, 12%, 5) = 3.6048. What is the break-even annual benefit, in millions of naira?

   <details><summary>Answer</summary>

   Set PW = 0: A × 3.6048 = 50, so A = 50 ÷ 3.6048 ≈ ₦13.87 million a year.

   </details>

3. <!-- q: exact id="f4d3543f" answer="7.53" sigfigs="2" tolerance="0.1" accept="7.5%|7.53%|7.5" -->
   A project's expected annual benefit is ₦15 million and its break-even annual benefit is ₦13.87 million. By what percentage can the benefit fall before the project stops being worth doing?

   <details><summary>Answer</summary>

   (15 − 13.87) ÷ 15 × 100 ≈ 7.5%. A small margin, so the decision is very sensitive to the benefit.

   </details>

4. <!-- q: mcq id="010fb6e0" -->
   On a spider diagram, the line for "selling price" is the steepest and the line for "maintenance cost" is almost flat. What does this tell you?

   - [x] The decision is most sensitive to selling price, so it must be estimated most carefully
   - [ ] Maintenance cost is the most important variable
   - [ ] Selling price is the most likely to change
   - [ ] The project should be rejected

   <details><summary>Answer</summary>

   The steepest line is the most sensitive variable. A small error in selling price moves the PW a lot. The diagram doesn't say how likely a change is.

   </details>

5. <!-- q: mcq id="a2ac4af8" -->
   How does scenario analysis differ from sensitivity analysis?

   - [ ] It uses probabilities for every variable
   - [x] It changes several variables together, as best, base and worst cases
   - [ ] It only changes the interest rate
   - [ ] It needs no base case

   <details><summary>Answer</summary>

   Scenario analysis changes several variables together. Sensitivity analysis changes one at a time.

   </details>

6. <!-- q: open id="6e38e15b" -->
   Write a short note on sensitivity analysis in engineering economic evaluation.

   <details><summary>Answer</summary>

   Sensitivity analysis tests whether a decision changes if one estimate turns out different. You work out a base case (for example PW with best estimates), change one variable at a time (say ±10% and ±20%) while holding the others fixed, recalculate, and see which variable moves the result most. You also find the break-even (switching) value where PW reaches zero and the decision flips. Results are shown in a table or a spider diagram, where the steepest line is the most sensitive variable. It is simple, needs no probabilities, shows which estimates matter and where to collect more data. Its limits: it changes one variable at a time though real variables move together, it says nothing about how likely a change is, and the ranges are arbitrary. Scenario analysis changes several variables together.

   </details>

## Before moving on
<!-- bite: 3cf05a2d-3529-4d12-95fd-308a580cd3e2 -->

You can run a sensitivity analysis, find a switching value, read a spider diagram, and give the method's strengths and limits. **Next:** [[engineering-economics/26-break-even-analysis-1|Break-Even Analysis 1]]: contribution and the break-even point.

## Related
<!-- bite: a5862323-9896-43cd-a41d-e1c6a349fcb7 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 334eccc1-a38b-4369-b3d2-6c24a5f4f7a8 -->

**Level:** Beginner. **Covers:** the steps of sensitivity analysis, the annual benefit example, the break-even (switching) value, the spider diagram, scenario analysis, advantages and limits, and which inputs are least reliable.

**Where it sits:** lesson 25 of 38, the end of part 6 (risk and uncertainty).

**Source:** the author's own GEG 501 note, sections 14.1 and 14.5. The spider diagram comes from `scripts/diagrams/engineering_economics.py`, which also checks the table.
