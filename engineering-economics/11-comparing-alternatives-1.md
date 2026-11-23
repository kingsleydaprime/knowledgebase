---
id: 0647795f-4a46-429e-908e-a61e1b469747
---

# Comparing Alternatives 1: Ground Rules, MARR and Present Worth

Comparing alternatives means bringing every option's cash flows to the same point in time, at the same interest rate, so you can see which option is worth the most.

## Before you start
<!-- bite: 6718b370-7e31-4382-b239-df11bbb0bc04 -->

You should know the P/A and P/F factors from [[engineering-economics/06-interest-factors-1|Interest Factors 1]], and sunk cost from [[engineering-economics/02-cost-concepts-1|Cost Concepts 1]].

After this lesson you will be able to:

1. tell independent, mutually exclusive and contingent alternatives apart;
2. state the four ground rules for a fair comparison, and what the MARR is and what it depends on;
3. work out the present worth of a project and use it to accept, reject or choose.

## What comparing alternatives is
<!-- bite: 2edc102d-0ccb-4876-9607-6939de0ce110 -->

Now that every cash flow can be moved to one point in time, you can compare projects. This is step 4 of the seven decision steps in lesson 01.

There are several methods, and the next four lessons cover them: present worth, annual worth, future worth, rate of return, benefit-cost ratio and payback. The methods differ in how they put the answer (a naira value today, a naira value per year, or a percentage), but a correct analysis should lead to the same decision.

Before any method, you need to know what kind of choice you're making, the rules of a fair comparison, and the interest rate to use.

## Types of alternatives
<!-- bite: 07ad9495-e764-4cd8-a202-af12b772eb23 -->

- **Independent:** each can be accepted or rejected on its own, for example buying a house and buying a car.
- **Mutually exclusive:** choosing one rules out the others, for example solar power or a diesel generator, machine A or machine B.
- **Contingent:** acceptance depends on another project going ahead first, for example battery storage depends on a solar installation.

## Ground rules before any comparison
<!-- bite: 35f9b05b-6a52-4157-bc90-5d8419378eb7 -->

1. Compare mutually exclusive alternatives with each other.
2. Use the **same planning horizon** (the same useful life, or a common period).
3. Use one consistent interest rate, the MARR.
4. Use **relevant cash flows only**: future costs and benefits. Sunk costs are ignored (lesson 02).

Rule 2 is the one people forget. A machine that lasts 3 years and one that lasts 6 years can't be compared on present worth as they stand. Lesson 12 shows how annual worth gets round it.

## MARR (minimum attractive rate of return)
<!-- bite: 1448a86c-8c42-4eda-a9f5-d5692b56817d -->

MARR is the lowest rate of return you will accept on an investment. It is the benchmark every project is measured against. Other names: hurdle rate, cut-off rate, required rate of return. It depends on:

1. **Cost of capital:** what you pay for the money you borrow or use.
2. **Expected inflation:** the loss of purchasing power.
3. **Risk of the project:** higher risk means a higher MARR.
4. **Opportunity cost:** the return from the next best alternative.

Organisations set different MARRs. Government bodies and regulated utilities usually accept lower rates than competitive industrial firms. A cost-reduction proposal may need a lower rate than a research project, because its cash flows are more certain.

A one-sentence version for an exam: the MARR is the minimum rate of return an organisation will accept on an investment, set from its cost of capital, expected inflation, the project's risk and its opportunity cost, and every project is judged against it.

## The present worth (PW) method
<!-- bite: a4be292c-b8d5-47a6-a3a9-e9c36ccf7463 -->

Convert every cash flow to time 0 and add them up. The difference between the present worth of inflows and outflows is the **net present worth (NPW)**.

Each cash flow is divided by (1 + i) once for every year it is away, then everything is added. For a project with a first cost, equal yearly benefits and a salvage value, that becomes:

$$PW = \sum_{t=0}^{n} \frac{CF_t}{(1+i)^t} \qquad PW = -C_0 + A\,(P/A,i,n) + S\,(P/F,i,n)$$

C0 is the first cost, A the yearly net benefit (or cost), S the salvage value and n the life.

> **Correction:** your lecture 5 writes the salvage term as S(F/P, i, n). Salvage comes at the end and you want its present value, so it is S(P/F, i, n).

## The PW decision rules
<!-- bite: 990e6dc4-84c3-4aa4-9570-dd2dbf7f819d -->

- **One project:** PW > 0 accept (it earns more than the MARR), PW < 0 reject, PW = 0 you are indifferent.
- **Several mutually exclusive projects:** if you measure benefits, pick the highest PW. If you measure only costs, pick the least negative PW (the lowest cost).

Why does PW > 0 mean it beats the MARR? Because you discounted at the MARR. A positive PW means the project gives back everything the MARR asks for, plus that much extra in today's money.

## Example: Machine A or Machine B
<!-- bite: af7aa656-95a7-4368-a1bd-fb1d478a3eca -->

**Example (lecture 5):** Machine A costs ₦3,000,000 and gives ₦1,200,000 a year for 4 years. Machine B costs ₦4,200,000 and gives ₦1,700,000 a year for 4 years. MARR = 10%, so P/A = 3.1699.

- PW(A) = −3,000,000 + 1,200,000 × 3.1699 = **₦803,880**
- PW(B) = −4,200,000 + 1,700,000 × 3.1699 = **₦1,188,830**

PW(B) is bigger, so Machine B is preferred. Both lives are 4 years, so the comparison is fair.

## Example: the dump truck
<!-- bite: b5f36138-723a-4f74-8650-bc1e5fcd39b0 -->

**Example (slides):** at 9%, first cost $50,000, operating cost $2,000 a year, income $9,000 a year, salvage $10,000, life 10 years. The factors are P/A = 6.418 and P/F = 0.4224.

- PW of benefits = 9,000 × 6.418 = $57,762.
- PW of costs = 50,000 + 2,000 × 6.418 − 10,000 × 0.4224 = $58,612.
- NPW = −$850, so do **not** invest.

The minimum yearly benefit that makes it worthwhile is 58,612 ÷ 6.418 = $9,132.

> **Correction:** the slides give $9,312.44. 58,612 ÷ 6.418 = $9,132.44 (two digits swapped).

## The limit of present worth
<!-- bite: 14d9bdb4-07f6-4244-95f8-e73780e5f9ce -->

**Limit of PW:** it only compares fairly when the alternatives have the same life. For different lives, use annual worth.

That's the next lesson: annual worth turns everything into a naira amount per year, so a 3-year machine and a 6-year machine can finally be compared.

## Check your understanding
<!-- bite: fcc98eef-ad46-44c6-8660-917363fadad1 -->

Try each one before you open the answer.

1. <!-- q: mcq id="642a4ffa" -->
   A firm can install either a solar system or a diesel generator to power its site, but not both. What type of alternatives are these?

   - [ ] Independent
   - [x] Mutually exclusive
   - [ ] Contingent

   <details><summary>Answer</summary>

   Mutually exclusive: choosing one rules out the other.

   </details>

2. <!-- q: mcq id="a4a0a761" -->
   Which of these does the MARR NOT depend on?

   - [ ] The cost of capital
   - [ ] The project's risk
   - [ ] Expected inflation
   - [x] Money already spent on a feasibility study

   <details><summary>Answer</summary>

   Money already spent is a sunk cost and affects nothing. The MARR depends on the cost of capital, expected inflation, the project's risk and the opportunity cost.

   </details>

3. <!-- q: exact id="719109da" answer="276351.09" sigfigs="4" tolerance="60" -->
   A machine costs ₦2,000,000, gives a net benefit of ₦600,000 a year for 5 years, and has a salvage value of ₦200,000 at the end of year 5. The MARR is 12%, so (P/A, 12%, 5) = 3.6048 and (P/F, 12%, 5) = 0.5674. What is its present worth, in naira?

   <details><summary>Answer</summary>

   PW = −2,000,000 + 600,000 × 3.6048 + 200,000 × 0.5674 = −2,000,000 + 2,162,880 + 113,480 ≈ ₦276,350. It is positive, so accept: it earns more than 12%.

   </details>

4. <!-- q: mcq id="2e6e28dd" -->
   Two pumps do the same job for 4 years, and only their costs are known. At 10%, PW(pump X) = −₦1,475,480 and PW(pump Y) = −₦1,553,589. Which should be chosen?

   - [x] Pump X, the least negative PW
   - [ ] Pump Y, the bigger number
   - [ ] Neither, because both PWs are negative

   <details><summary>Answer</summary>

   Pump X. When you measure only costs, every PW is negative, and you pick the least negative one: the lowest cost. A negative PW doesn't mean reject here, because the job must be done anyway.

   </details>

5. <!-- q: exact id="8b578306" answer="12000" accept="12,000|₦12,000" tolerance="5" -->
   A project costs ₦50,000 and its yearly benefits run for 6 years. At the MARR, (P/A, i, 6) = 4.1667. What is the minimum yearly benefit that makes it worthwhile, in naira?

   <details><summary>Answer</summary>

   Set PW = 0: A × 4.1667 = 50,000, so A = 50,000 ÷ 4.1667 ≈ ₦12,000 a year.

   </details>

6. <!-- q: open id="a19dc9b4" -->
   Write a short note on the minimum attractive rate of return (MARR).

   <details><summary>Answer</summary>

   The MARR is the lowest rate of return an organisation will accept on an investment, and every project is judged against it. It is also called the hurdle rate, cut-off rate or required rate of return. It depends on the cost of capital, expected inflation, the risk of the project (higher risk, higher MARR) and the opportunity cost of the next best alternative. Organisations set different MARRs: government bodies and regulated utilities usually accept lower rates than competitive firms, and a more certain project (cost reduction) may need a lower rate than a risky one (research). A project is accepted when its PW at the MARR is positive, or its IRR is at least the MARR.

   </details>

## Before moving on
<!-- bite: b90f7f4f-5854-42f5-b572-df7a76f12f65 -->

You can classify alternatives, state the ground rules, explain the MARR, and accept or choose projects with present worth. **Next:** [[engineering-economics/12-comparing-alternatives-2|Comparing Alternatives 2]]: annual worth and future worth.

## Related
<!-- bite: 33b1fa41-94b7-4aae-8f9d-4247c7421783 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 01ad0ce9-170e-4f82-b216-eaa050d2bf6e -->

**Level:** Beginner. **Covers:** types of alternatives, the four ground rules, the MARR, the present worth method and its decision rules, the lecture's Machine A and B example, and the slides' dump truck example, with two corrections.

**Where it sits:** lesson 11 of 38, part 1 of 4 on comparing alternatives.

**Source:** the author's own GEG 501 note, section 6 (lecture 5 and the present worth slides).
