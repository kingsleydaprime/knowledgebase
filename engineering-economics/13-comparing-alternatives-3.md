---
id: be7b5f8b-407a-448d-be09-8bac63c6d89d
---

# Comparing Alternatives 3: Rate of Return

The internal rate of return (IRR) is the interest rate that makes a project's present worth exactly zero, so it tells you the percentage return the project earns.

## Before you start
<!-- bite: 10dcce36-6e37-41de-ae2b-abe6d3c9bc76 -->

You should know present worth from [[engineering-economics/11-comparing-alternatives-1|Comparing Alternatives 1]].

After this lesson you will be able to:

1. define the MARR, IRR and ERR, and state the IRR decision rule;
2. find an IRR by trial and error, and close in on it with linear interpolation;
3. explain why IRR can disagree with PW for mutually exclusive projects, and use incremental IRR instead.

## What the rate of return is
<!-- bite: 4b5c5649-3a46-4e7d-8e48-0b63d33eadae -->

PW, AW and FW give the answer in naira. Managers often want a percentage instead: "this project earns 18%". That's the rate of return.

Three rates appear in these problems:

- **MARR:** the minimum acceptable rate (lesson 11).
- **Internal rate of return (IRR):** the interest rate that makes the present worth of the project equal to zero. It is the return earned on the money still unrecovered in the project.
- **External rate of return (ERR):** the return you could realistically earn on money outside the project. It is usually set equal to the MARR.

Rule: **accept if IRR ≥ MARR**.

## Why PW = 0 gives the project's own rate
<!-- bite: 4af074c9-f817-45f8-834d-4314679705f7 -->

Think about what PW = 0 means. Discount the cash flows at some rate and the benefits exactly pay back the cost, with nothing left over. So that rate is precisely what the project earns.

The higher the rate you discount at, the smaller the PW. So PW falls as the rate rises, and crosses zero at the IRR.

![Present worth of a 500 naira investment returning 300, 300 and 200 plotted against the interest rate from 0 to 40 percent: the curve falls from 300 at 0 percent and crosses zero at about 30 percent, which is the internal rate of return, with the 15 percent target rate marked to its left](images/ee-irr-pw-curve.svg)

## Finding IRR by trial and error
<!-- bite: 356e3935-7903-4b63-a2ca-08aa9f142e81 -->

You normally find IRR by trial and error: try rates until the benefits equal the costs.

**Example (slides):** invest ₦500, receive ₦300 in year 1, ₦300 in year 2 and ₦200 in year 3. The desired return is 15%.

| Trial rate | PW of the returns | Compare with 500 |
| --- | --- | --- |
| 10% | 273 + 248 + 150 = 671 | too high, try a bigger rate |
| 20% | 250 + 208 + 116 = 574 | too high |
| 30% | 231 + 178 + 91 = 500 | equal, so IRR = 30% |

IRR of 30% is above the 15% target, so accept. That's the point where the curve in the picture crosses zero.

> **Correction:** the slide shows 272 + 247 + 156 = 669 for the 10% row, but the third term should be about 150 and the sum is 671. The IRR of 30% does not change. At 30% the sum is 499, which rounds to 500.

## Closing in: linear interpolation
<!-- bite: 21f0f5b4-c52e-4319-a143-8352666e0f0d -->

The slide example lands exactly on a round number. Most don't. When one trial rate gives a positive PW and the next gives a negative PW, the IRR lies between them, and you estimate it by drawing a straight line between the two points:

$$IRR \approx i_1 + (i_2 - i_1)\frac{PW_1}{PW_1 - PW_2}$$

**Example:** invest ₦1,000, receive ₦400 a year for 3 years.

1. At 9%: PW = −1,000 + 400 × 2.53129 = +12.5.
2. At 10%: PW = −1,000 + 400 × 2.48685 = −5.3.
3. IRR ≈ 9 + (10 − 9) × 12.5 / (12.5 + 5.3) = 9 + 0.70 = **9.70%**.

Keep the two trial rates close (1 or 2 points apart), because the real curve bends and the straight line is only an estimate. This interpolation example was added for this lesson; the 2025/2026 exam asks for exactly this.

## Caution 1: IRR can rank projects wrongly
<!-- bite: d987aa28-1f12-46d1-8a50-d52fbe76cb99 -->

Ranking mutually exclusive projects by IRR alone can disagree with PW, FW and AW. The consistent method is **incremental IRR**: start with the cheaper acceptable project, then check the extra investment (the difference in cash flows) against the MARR. If the extra return is above the MARR, the bigger project is better.

Why do they disagree? IRR is a percentage, so it ignores *size*. Earning 30% on ₦1,000 gives you less money than earning 25% on ₦2,000.

## Example: incremental IRR
<!-- bite: af38d8b5-e4df-4b45-80e6-180bc8ab8cfe -->

MARR is 10%. Project A costs ₦1,000 and returns ₦1,300 after one year (IRR 30%). Project B costs ₦2,000 and returns ₦2,500 after one year (IRR 25%).

- By IRR alone, A looks better (30% against 25%).
- By PW at 10%: PW(A) = 1,300/1.1 − 1,000 = ₦182, PW(B) = 2,500/1.1 − 2,000 = ₦273. B is better.
- Incremental: B − A costs an extra ₦1,000 and returns an extra ₦1,200, an IRR of 20%. That's above the 10% MARR, so the extra investment is worth it, and B wins.

Incremental IRR agrees with PW. This example was added for this lesson.

## Caution 2: more than one sign change
<!-- bite: 500914f2-3f85-4fd0-9987-732e3776b7cd -->

Cash flows with more than one sign change can give several rates that make PW zero. A simple investment has just one sign change (minus to plus), so it has one true IRR.

A project that costs money at the start, earns for years, then costs a lot again at the end (say, to clean up a mine) changes sign twice and can have two IRRs. Use PW for those.

IRR is a percentage. The next lesson's main method, the benefit-cost ratio, is a ratio, and it's the one governments use for roads and bridges.

## Check your understanding
<!-- bite: 7eda51d8-2d73-40ac-90fd-3435433f3a92 -->

Try each one before you open the answer.

1. <!-- q: gap id="8dfcb9a6" answers="zero|0;MARR|minimum attractive rate of return" -->
   Fill in the gaps. The internal rate of return is the interest rate that makes the present worth of a project equal to ___. A project is accepted if its IRR is at least the ___.

   <details><summary>Answer</summary>

   Zero; the MARR. Accept if IRR ≥ MARR.

   </details>

2. <!-- q: exact id="c6199c0e" answer="13.08" sigfigs="3" tolerance="0.05" accept="13.08%|13.1%" -->
   A project's PW is +₦28.06 at 12% and −₦24.01 at 14%. Estimate its IRR by linear interpolation, in percent.

   <details><summary>Answer</summary>

   IRR ≈ 12 + (14 − 12) × 28.06 / (28.06 + 24.01) = 12 + 2 × 0.539 = 13.08%.

   </details>

3. <!-- q: mcq id="7f42ac41" -->
   A project costs ₦800 and returns ₦400, ₦400 and ₦400 over three years. At 20%, the PW of the returns is ₦843. At 25% it is ₦781. What can you say about the IRR?

   - [ ] It is below 20%
   - [x] It is between 20% and 25%
   - [ ] It is above 25%
   - [ ] It is exactly 25%

   <details><summary>Answer</summary>

   Between 20% and 25%. At 20% the returns are worth more than the ₦800 cost (PW positive), and at 25% they are worth less (PW negative), so PW crosses zero in between.

   </details>

4. <!-- q: mcq id="f4d3543e" -->
   MARR is 12%. Project X costs ₦1,000 with IRR 28%. Project Y costs ₦3,000 with IRR 22%. The extra ₦2,000 of investment in Y has an incremental IRR of 19%. Which project should be chosen if they are mutually exclusive?

   - [ ] X, because its IRR is higher
   - [x] Y, because the incremental IRR is above the MARR
   - [ ] Neither

   <details><summary>Answer</summary>

   Y. Both are acceptable, and the extra ₦2,000 earns 19%, which beats the 12% MARR, so the bigger project adds value. Ranking by IRR alone would wrongly pick X.

   </details>

5. <!-- q: open id="010fb6df" -->
   Briefly explain why IRR and PW may sometimes give conflicting rankings for mutually exclusive projects. (A 3-mark part of the 2025/2026 exam.)

   <details><summary>Answer</summary>

   IRR is a percentage, so it ignores the size of the investment: a small project can have a high IRR but add less money than a bigger project with a lower IRR. PW measures the actual naira value added at the MARR, so it can rank them the other way. The timing of cash flows also matters, because IRR assumes money is reinvested at the IRR, while PW assumes the MARR. Cash flows with more than one sign change can give several IRRs. The consistent method is incremental IRR: check the extra investment against the MARR, which agrees with PW.

   </details>

## Before moving on
<!-- bite: 95b0e226-e6c2-4b7f-81df-5822c53ccdb7 -->

You can define IRR, find it by trial and interpolation, and use incremental IRR to choose between projects. **Next:** [[engineering-economics/14-comparing-alternatives-4|Comparing Alternatives 4]]: benefit-cost ratio, payback, and choosing a method.

## Related
<!-- bite: d3408f04-add1-4b48-b65b-7ddc29fab5d6 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 19bdd4b5-8e9e-4de8-b6bc-cdc73bc7c2ee -->

**Level:** Beginner to intermediate. **Covers:** MARR, IRR and ERR, the IRR rule, trial and error with the slides' example (and a correction), linear interpolation, incremental IRR, and multiple sign changes.

**Where it sits:** lesson 13 of 38, part 3 of 4 on comparing alternatives.

**Source:** the author's own GEG 501 note, section 6. The interpolation and incremental IRR examples were added for this lesson, and the curve comes from `scripts/diagrams/engineering_economics.py`.
