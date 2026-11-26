---
id: 3eec5625-1a15-4511-8072-c8fd0f4553f3
---

# Nominal and Effective Interest

The nominal interest rate is the yearly rate a bank states, and the effective rate is what you really earn or pay once interest is compounded more than once a year.

## Before you start
<!-- bite: 74f75a0f-abbe-4981-adff-cfaa5b93dd43 -->

You should know compound interest and the P/A factor from [[engineering-economics/06-interest-factors-1|Interest Factors 1]].

After this lesson you will be able to:

1. convert a nominal rate to an effective rate, for monthly, daily and continuous compounding;
2. use the factors when the compounding period isn't a year;
3. work out the capitalized cost of a project with no end, including one whose equipment is replaced every few years.

## What nominal and effective interest are
<!-- bite: b547f4ea-aeff-48f1-807c-073eda7da878 -->

The factors in lessons 06 and 07 assume the interest rate matches the period (a yearly rate for yearly payments). This lesson fixes that assumption.

When interest is compounded more than once a year, the stated yearly rate (the **nominal rate**, r) is not what you really earn. The **effective rate** is.

Why? Say a bank quotes 12% a year, compounded monthly. It adds 1% every month. By February you're earning interest on January's interest. So by December you've earned a bit more than 12%.

## The effective rate formula
<!-- bite: 6bea94fd-f099-410f-9ce0-2567fc81505d -->

The rate per period is r/m, and it is compounded m times in the year. The effective rate is what that grows to in a year, minus the 1 you started with:

$$i_{eff} = \left(1 + \frac{r}{m}\right)^{m} - 1$$

m is the number of compounding periods per year.

- **Example (textbook):** 5.25% a year compounded daily ($m = 365$). $i_{\text{eff}} = (1 + 0.0525/365)^{365} - 1 = 0.0539$, so about **5.39%**.
- **Example:** 12% a year compounded monthly gives (1.01)^12 − 1 = 12.68%.

If n is counted in the same periods as the rate per period, you can use the normal factors with i = r/m and n = number of periods. A 3-year loan at 12% compounded monthly uses i = 1% and n = 36.

## Continuous compounding
<!-- bite: f75a6b8e-7a00-4878-8b47-4f7fcd9efde5 -->

What if the bank compounds every day, every hour, every second? As m becomes very large, compounding is continuous. The formulas become:

$$i_{eff} = e^{r} - 1 \qquad F = Pe^{rn} \qquad P = Fe^{-rn}$$

e is the number 2.71828… (the $e^x$ key on your calculator). For 10% compounded continuously, $i_{\text{eff}} = e^{0.1} - 1 = 10.52\%$, only a little more than monthly compounding would give.

## Capitalized cost: a project with no end
<!-- bite: 2ec0784a-cb8e-4024-bdb0-f3ffbda2d4b4 -->

Some things are meant to last forever: a bridge, a dam, a cemetery. For these, the P/A factor tends to 1/i as n grows. So the present sum that pays an annual cost A for ever without touching the principal is:

$$P = \frac{A}{i}$$

It makes sense: if you put P in the bank, the interest every year is P × i. Set that equal to A, and the interest pays the cost forever while P stays untouched.

**Example (FE review):** a cemetery plot costs $75 a year to maintain. At 6%, you must set aside 75 ÷ 0.06 = **$1,250**.

Capitalized cost = first cost + A/i.

## Capitalized cost with replacement
<!-- bite: d67fa663-857d-4921-844c-a89d1ad9cb1f -->

For equipment that must be replaced every n years forever, you need the original cost plus enough money to fund every future replacement:

$$\text{Capitalized cost} = C_o + \frac{C_R}{(1+i)^n - 1}$$

**Example:** a pump costs ₦10,000, lasts 5 years, no salvage, i = 10%. Capitalized cost $= 10{,}000 + 10{,}000 \div (1.1^5 - 1) = 10{,}000 + 16{,}380 =$ **₦26,380**.

- If the operating cost is $R_{\text{op}}$ a year forever, add $R_{\text{op}} \div i$.
- If the item has salvage value, the replacement cost $C_R$ is the original cost minus salvage.

So ₦26,380 set aside today buys the first pump and pays for a new one every 5 years, forever.

## Common pitfalls
<!-- bite: 13319fba-5df6-4e8d-abc8-b6d654d6b62a -->

1. **Using the nominal rate as if it were effective.** 12% compounded monthly is 12.68% a year, not 12%.
2. **Mixing periods.** If i is per month, n must be in months.
3. **Forgetting the first cost.** A/i only covers the yearly cost. Capitalized cost adds the first cost on top.

The rates in this lesson are all about interest. But there's another reason money loses value over time, and it's one every Nigerian already knows too well: prices keep rising. That's inflation, and it's next.

## Check your understanding
<!-- bite: 337c570e-b534-4c36-9f29-90978d6018c3 -->

Try each one before you open the answer.

1. <!-- q: exact id="323658d5" answer="0.195618" sigfigs="3" accept="19.56%|19.6%|19.56" -->
   A loan has a nominal rate of 18% a year, compounded monthly. What is the effective annual rate, as a decimal?

   <details><summary>Answer</summary>

   $i_{\text{eff}} = (1 + 0.18/12)^{12} - 1 = 1.015^{12} - 1 = 0.1956$, about 19.56%.

   </details>

2. <!-- q: exact id="df9fde27" answer="0.0824322" sigfigs="3" accept="8.24%|8.24" -->
   A savings account pays 8% a year compounded quarterly. What is the effective annual rate, as a decimal?

   <details><summary>Answer</summary>

   $i_{\text{eff}} = (1 + 0.08/4)^4 - 1 = 1.02^4 - 1 = 0.0824$, about 8.24%.

   </details>

3. <!-- q: exact id="72693226" answer="14918.25" sigfigs="4" tolerance="5" -->
   ₦10,000 is invested at 8% a year compounded continuously for 5 years. What does it grow to, in naira?

   <details><summary>Answer</summary>

   $F = Pe^{rn} = 10{,}000 \times e^{0.08 \times 5} = 10{,}000 \times e^{0.4} = 10{,}000 \times 1.4918 \approx$ ₦14,918.

   </details>

4. <!-- q: exact id="9d4152bd" answer="2500000" accept="2,500,000|₦2,500,000" -->
   A town wants a fund that pays a bridge's maintenance of ₦200,000 a year forever, without touching the fund itself. At 8%, how much must it set aside, in naira?

   <details><summary>Answer</summary>

   P = A/i = 200,000 ÷ 0.08 = ₦2,500,000. The interest each year, 8% of 2,500,000, is exactly 200,000.

   </details>

5. <!-- q: exact id="8c070062" answer="81372.70" sigfigs="4" tolerance="5" -->
   A machine costs ₦50,000, lasts 10 years with no salvage, and must be replaced every 10 years forever. At 10%, what is its capitalized cost, in naira?

   <details><summary>Answer</summary>

   Capitalized cost $= 50{,}000 + 50{,}000 \div (1.1^{10} - 1) = 50{,}000 + 50{,}000 \div 1.5937 = 50{,}000 + 31{,}373 \approx$ ₦81,373.

   </details>

6. <!-- q: mcq id="04020a90" -->
   A 2-year loan is at 12% a year compounded monthly, with monthly payments. Which i and n should you use in the P/A factor?

   - [ ] i = 12%, n = 2
   - [ ] i = 12%, n = 24
   - [x] i = 1%, n = 24
   - [ ] i = 1%, n = 2

   <details><summary>Answer</summary>

   i = r/m = 12%/12 = 1% per month, and n = 24 months. The rate and n must be counted in the same periods.

   </details>

## Before moving on
<!-- bite: d2128052-1b83-46e1-bf62-c4860a4383fa -->

You can convert nominal to effective rates, handle continuous compounding, and work out capitalized cost with and without replacement. **Next:** [[engineering-economics/09-inflation-1|Inflation 1]]: what inflation is, and how to separate real values from nominal ones.

## Related
<!-- bite: fa6a7c9b-6d43-4a74-9dc0-6b93eb254de0 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: b5379d6c-1986-4be8-bad7-98d9691bebb4 -->

**Level:** Beginner. **Covers:** nominal and effective interest, using factors with non-yearly periods, continuous compounding, capitalized cost, and capitalized cost with replacement.

**Where it sits:** lesson 08 of 38, the last lesson on interest before inflation.

**Source:** the author's own GEG 501 note, sections 5 and 14.5.
