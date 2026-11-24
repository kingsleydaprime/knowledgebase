---
id: 649e5286-1a21-4cac-88af-5af664bd061e
---

# Earned Value

Earned value analysis measures progress in money, to show whether a project is behind schedule, over budget, or both.

## Before you start
<!-- bite: 5daac9a2-c8fd-498f-aae1-7437f87f218b -->

You should have read [[planning-and-scheduling/34-the-master-schedule|34 — The Master Schedule]].

After this lesson you will be able to:

1. define planned value, earned value and actual cost;
2. compute the schedule and cost variances and say what their signs mean;
3. compute and read the schedule and cost performance indices.

## What earned value is
<!-- bite: fa5cc423-88f7-4ce9-8859-389a38c103f8 -->

On day 6 of the fence the owner asks, "How are we doing?" The builder says, "We've spent N54,000." Is that good? You can't tell. Spending exactly what was planned could mean the work is on track, or that you've done half the work for the full money. Spending alone mixes up two questions: are we on time, and are we on budget?

Earned value separates them. The trick is to measure the work done in the same unit as the money: **what that work was budgeted to cost**. Your slides name earned value analysis (EVA) as a technique; the measures below are the standard ones. If your lecturer covered it, expect it to be tested.

## The three measures
<!-- bite: 89cc0eac-af13-4137-bbe8-a746c6447677 -->

1. **Planned value (PV)**: This is the budgeted cost of the work **scheduled** to be done by now. It is what you planned to have done, in money.
2. **Earned value (EV)**: This is the budgeted cost of the work **actually done** by now. It is what you really achieved, valued at the budget's prices.
3. **Actual cost (AC)**: This is what you have **actually spent** by now.

For the fence, budgeted at N120,000 over 12 days: by day 6 the plan said N60,000 of work should be done (**PV = 60,000**). The work actually finished was budgeted at N48,000 (**EV = 48,000**). The builder has spent N54,000 (**AC = 54,000**).

## The two variances
<!-- bite: b8747192-1463-4d6d-8ddb-2498f423318d -->

**Schedule variance is earned value minus planned value: how much work, in money, you are ahead of or behind the plan.**

**Cost variance is earned value minus actual cost: how much more or less the work done cost than its budget.**

$$SV = EV - PV, \qquad CV = EV - AC$$

For the fence: SV = 48,000 − 60,000 = **−12,000**, and CV = 48,000 − 54,000 = **−6,000**.

Remember this one: both start with EV, and **negative is bad**. Negative SV means behind schedule; negative CV means over budget. The fence is both.

## The two indices
<!-- bite: 6428e008-6d44-4485-b036-96969aa10a5d -->

Variances are in naira, so a N12,000 shortfall means different things on a N120,000 fence and a N12 billion refinery. The indices turn them into ratios.

**The schedule performance index is earned value divided by planned value; the cost performance index is earned value divided by actual cost.**

$$SPI = \frac{EV}{PV}, \qquad CPI = \frac{EV}{AC}$$

For the fence: SPI = 48,000 / 60,000 = **0.80**, and CPI = 48,000 / 54,000 = **0.89**.

Read them as "kobo of value per naira": the fence is getting 80% of the planned progress, and 89 kobo of work for every naira spent. **Below 1 is bad; above 1 is good; exactly 1 is on plan.**

## Reading all four together
<!-- bite: d4325d2b-c495-4950-a041-c64dff7f4a25 -->

1. **SV < 0, SPI < 1**: behind schedule.
2. **SV > 0, SPI > 1**: ahead of schedule.
3. **CV < 0, CPI < 1**: over budget.
4. **CV > 0, CPI > 1**: under budget.

The two questions are independent. A project can be ahead of schedule and over budget (paying overtime to race ahead), or behind and under budget (a crew is missing, so less is being spent and less done).

For the fence, both are below 1. The builder should find out why: the late wood from lesson 10's external dependency, perhaps. That's the Monitoring and Controlling loop from lesson 04, closed: measure, compare with the plan, correct.

## Common pitfalls
<!-- bite: e31137a6-ada7-4c05-964c-c83be2fc5694 -->

1. **Using AC − EV.** Both variances are EV minus something, so negative always means bad.
2. **Comparing PV with AC.** That mixes schedule and cost, which is exactly the confusion earned value exists to avoid.
3. **Reading an index of 1.1 as bad.** Above 1 is good.

## Check your understanding
<!-- bite: 21e6c2bb-8221-4c74-973b-f070ad71f72a -->

Try each one before you open the answer.

1. <!-- q: exact id="3d7f0a92" answer="10" accept="+10|10k|N10k" -->
   A project has PV = N80k, EV = N90k and AC = N100k. What is the schedule variance, in thousands of naira?

   <details><summary>Answer</summary>

   +10: SV = 90 − 80. Positive, so it is ahead of schedule.

   </details>

2. <!-- q: exact id="b84e2c15" answer="-10" accept="−10|-10k" -->
   A project has PV = N80k, EV = N90k and AC = N100k. What is the cost variance, in thousands of naira?

   <details><summary>Answer</summary>

   −10: CV = 90 − 100. Negative, so it is over budget.

   </details>

3. <!-- q: exact id="6a1c9e58" answer="0.9" -->
   A project has PV = N80k, EV = N90k and AC = N100k. What is its CPI?

   <details><summary>Answer</summary>

   0.9: 90 / 100. It gets 90 kobo of work for each naira spent.

   </details>

4. <!-- q: mcq id="e5f20d73" -->
   A project's SPI is 1.2 and its CPI is 0.85. What is happening?

   - [ ] Behind schedule and under budget
   - [x] Ahead of schedule but over budget
   - [ ] On schedule and on budget
   - [ ] Behind schedule and over budget

   <details><summary>Answer</summary>

   SPI above 1 means ahead; CPI below 1 means over budget, as when overtime is paid to race ahead.

   </details>

5. <!-- q: open id="0c4d8b61" -->
   Why can't you tell whether a project is on budget just by comparing what has been spent with what was planned to be spent by now?

   <details><summary>Answer</summary>

   Because the amount of work done may differ from the plan. Spending matching the plan could mean on-track work, or less work done at a higher cost. Earned value values the work actually done at budget prices, so comparing it with actual cost shows the cost position, and comparing it with planned value shows the schedule position, separately.

   </details>

## Before moving on
<!-- bite: b0391cdf-ffb0-4a2b-aa9c-a7534f2fc92a -->

You can compute and read PV, EV, AC, SV, CV, SPI and CPI. That completes the subject: from defining the project, through the network, critical path, PERT, crashing and resources, to measuring progress. Test yourself on the [[planning-and-scheduling/ssg-513-question-bank|SSG 513 question bank]].

## Related
<!-- bite: 54c9d685-9b04-4744-bb8a-7497d988e0d1 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[engineering-economics/index|Engineering Economics]]: cost estimation and budgeting.

## About this lesson
<!-- bite: eeaa4236-0f74-4b2c-af54-b465f6a167f1 -->

**Level:** Intermediate. **Covers:** PV, EV and AC, schedule and cost variance, SPI and CPI, and how to read them together.

**Where it sits:** lesson 35 of 35, in part 8 (other planning tools).

**Source:** the author's own SSG 513 study notes, section 8. The slides only name earned value analysis, so the measures are standard project-management material; the fence figures are added for this lesson.
