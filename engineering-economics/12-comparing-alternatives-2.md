---
id: 754d128b-f43d-45fe-940d-575722413e4a
---

# Comparing Alternatives 2: Annual Worth and Future Worth

The annual worth method turns every cash flow into an equal amount per year, and the future worth method moves every cash flow to the end of the project.

## Before you start
<!-- bite: d9eb59a9-27c7-47e5-9d74-49ebaa5dbe58 -->

You should know the present worth method from [[engineering-economics/11-comparing-alternatives-1|Comparing Alternatives 1]], and the A/P and A/F factors from [[engineering-economics/06-interest-factors-1|Interest Factors 1]].

After this lesson you will be able to:

1. calculate annual worth (AW), also called equivalent annual cost (EAC), from a project's cash flows or from its PW;
2. compare alternatives with different lives using annual worth;
3. solve a lease-or-buy break-even, and calculate future worth.

## What annual worth is
<!-- bite: 27bf4d28-db77-4d83-b13f-239b0931175d -->

Remember the limit of present worth? It only compares fairly when the alternatives have the same life. Annual worth fixes that.

Convert everything to an equal yearly amount over the project life. It is handy when lives differ, because you compare cost per year.

Think of it like comparing two phone plans: one is ₦30,000 for 3 months, the other ₦100,000 for a year. You don't compare 30,000 with 100,000. You compare the cost per month. Annual worth does the same for projects.

## The annual worth formula
<!-- bite: 631b6a0e-b0a8-4a60-8684-b04b0e6b9a4b -->

You can get annual worth two ways. Spread the PW over the life with the capital recovery factor, or convert each part straight to a yearly amount:

$$AW = PW\,(A/P,i,n) \qquad AW = -C_0\,(A/P,i,n) + A + S\,(A/F,i,n)$$

The first cost is spread back over the life with A/P, the yearly amount stays as it is, and the salvage is turned into a yearly saving with A/F.

AW > 0 means a yearly profit over the life of the machine.

## Example: Machine A or Machine B again
<!-- bite: 274aa9ca-e25b-4651-8022-3a74603b3b0d -->

Same example as lesson 11: Machine A costs ₦3,000,000 and gives ₦1,200,000 a year, Machine B costs ₦4,200,000 and gives ₦1,700,000 a year, both for 4 years at 10%. A/P at 10% for 4 years = 0.3155.

- AW(A) = −3,000,000 × 0.3155 + 1,200,000 = **₦253,500**
- AW(B) = −4,200,000 × 0.3155 + 1,700,000 = **₦374,900**

B is still preferred. This agrees with PW, as it should.

## Example: from PW to AW
<!-- bite: 1ce36395-a6ea-4ce9-ae92-cfe9652716d7 -->

**Example (textbook):** a machine costs 40,000, gives 10,000 a year for 10 years and has a salvage value of 5,000 at 15%.

- PW = −40,000 + 10,000 × 5.0188 + 5,000 × 0.2472 = 11,424.
- AW = 11,424 × 0.1993 = 2,277 per year.

AW is positive, so accept. This is the same machine as question 6 in the practice booklet, so you've now seen the method for it.

## Different lives: where annual worth wins
<!-- bite: 72379da3-d59e-4d42-82ba-0c0b395a3e69 -->

Here is the case PW can't handle. Pump X costs ₦10,000, lasts 3 years and costs ₦2,000 a year to run. Pump Y costs ₦16,000, lasts 6 years and costs ₦1,500 a year to run. MARR is 10%. Neither has salvage value.

- EAC(X) = 10,000 × (A/P, 10%, 3) + 2,000 = 10,000 × 0.4021 + 2,000 = **₦6,021 a year**.
- EAC(Y) = 16,000 × (A/P, 10%, 6) + 1,500 = 16,000 × 0.2296 + 1,500 = **₦5,174 a year**.

Y costs less per year, so choose Y. (This assumes X would be replaced by an identical pump after 3 years, which is the usual assumption.) This example was added for this lesson.

## Lease or buy: a break-even with interest
<!-- bite: 6c0f66c0-1319-4b87-8c4b-77b8e70c009d -->

**Lease vs buy (FE review, EAC):** leasing costs $0.15 per km. Buying costs $5,000, 3-year life, $1,200 salvage, $0.04 per km running cost and $500 a year insurance, at 10%.

1. EAC(buy) = 0.04x + 500 + 5,000(0.4021) − 1,200(0.3021) = 0.04x + 2,148, where x is km driven a year.
2. EAC(lease) = 0.15x.
3. Set 0.15x = 0.04x + 2,148, so x = **19,527 km** a year to break even.

Drive more than that and buying is cheaper. The same idea, without interest, comes back in break-even analysis (lesson 27).

## Future worth (FW)
<!-- bite: df5b559c-adab-47ac-8634-ebbb751bdd21 -->

Same idea as PW, but every cash flow is moved to the **end** of the project:

$$FW = PW\,(F/P, i, n)$$

The decision rule is the same: FW > 0 accept, and the highest FW wins. Use it when you care about the value at the end, for example how much a savings plan will be worth at retirement.

For Machine B: FW = 1,188,830 × (F/P, 10%, 4) = 1,188,830 × 1.4641 ≈ ₦1,740,566.

PW, AW and FW all give the same ranking because each is the others multiplied by a positive factor. The next method is different: it gives the answer as a percentage, and that brings a few traps.

## Check your understanding
<!-- bite: bb79d846-9caa-4a44-9840-811327f7cbab -->

Try each one before you open the answer.

1. <!-- q: exact id="9f1ab858" answer="76662.48" sigfigs="4" tolerance="60" -->
   A machine costs ₦2,000,000, gives a net benefit of ₦600,000 a year for 5 years, and has a salvage value of ₦200,000 at the end of year 5. The MARR is 12%, so (A/P, 12%, 5) = 0.2774 and (A/F, 12%, 5) = 0.1574. What is its annual worth, in naira?

   <details><summary>Answer</summary>

   AW = −2,000,000 × 0.2774 + 600,000 + 200,000 × 0.1574 = −554,800 + 600,000 + 31,480 ≈ ₦76,680 a year (₦76,662 with exact factors). Positive, so accept.

   </details>

2. <!-- q: exact id="b14cb3ab" answer="5400" accept="5,400|₦5,400" tolerance="5" -->
   A project has a present worth of ₦20,000 over a 5-year life. At the MARR, (A/P, i, 5) = 0.2700. What is its annual worth, in naira?

   <details><summary>Answer</summary>

   AW = PW × (A/P) = 20,000 × 0.2700 = ₦5,400 a year.

   </details>

3. <!-- q: mcq id="e94ccd4a" -->
   Machine P lasts 4 years and Machine Q lasts 7 years. Both do the same job. Which method compares them most directly?

   - [ ] Present worth over each machine's own life
   - [x] Annual worth (equivalent annual cost)
   - [ ] Payback period
   - [ ] Adding up each machine's costs

   <details><summary>Answer</summary>

   Annual worth. It compares cost per year, so different lives don't matter. Present worth over different lives is not a fair comparison.

   </details>

4. <!-- q: exact id="9751df9c" answer="19386.67" sigfigs="3" tolerance="20" -->
   Leasing a van costs ₦0.20 per km. Buying one gives an equivalent annual cost of 0.05x + 2,908, where x is km a year. How many km a year make the two equal?

   <details><summary>Answer</summary>

   0.20x = 0.05x + 2,908, so 0.15x = 2,908 and x ≈ 19,387 km a year. Drive more than that and buying is cheaper.

   </details>

5. <!-- q: mcq id="12ec1dc6" -->
   At 10%, Project S has PW = ₦500,000 and Project T has PW = ₦650,000, both over 4 years. Which has the higher future worth at the end of year 4?

   - [ ] Project S
   - [x] Project T
   - [ ] You can't tell without the cash flows

   <details><summary>Answer</summary>

   Project T. FW = PW × (F/P, 10%, 4), the same positive factor for both, so the ranking doesn't change.

   </details>

## Before moving on
<!-- bite: d60d6448-299f-440d-afc6-42ad6669063b -->

You can calculate annual worth and future worth, compare machines with different lives, and solve a lease-or-buy break-even. **Next:** [[engineering-economics/13-comparing-alternatives-3|Comparing Alternatives 3]]: the internal rate of return.

## Related
<!-- bite: bb3660b6-6666-4113-bc19-322bfb905a76 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 04d3b441-d431-4424-8eb9-afbfb824c169 -->

**Level:** Beginner. **Covers:** annual worth (equivalent annual cost), the Machine A and B example again, the textbook machine, alternatives with different lives, the FE review lease-or-buy break-even, and future worth.

**Where it sits:** lesson 12 of 38, part 2 of 4 on comparing alternatives.

**Source:** the author's own GEG 501 note, section 6. The different-lives pump example and the Machine B future worth were added for this lesson.
