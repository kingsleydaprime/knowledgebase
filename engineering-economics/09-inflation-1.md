---
id: f0d3de4f-78a0-46c3-8dfc-e1271500ef5f
---

# Inflation 1: Inflation, Real Values and the Fisher Equation

Inflation is a sustained increase in the general price level of goods and services over time, which reduces the purchasing power of money.

## Before you start
<!-- bite: 2bf67398-2db0-4050-892f-52a63551ca94 -->

You should know nominal and effective interest from [[engineering-economics/08-nominal-and-effective-interest|Nominal and Effective Interest]].

After this lesson you will be able to:

1. define inflation, work out an inflation rate, and name the three price indices and the types of inflation;
2. tell nominal values from real values, and convert one to the other;
3. use the Fisher equation to find a real interest rate, and know when the quick approximation is good enough.

## What inflation is
<!-- bite: 47f3b7d9-9742-4e5c-9270-72ffd7f7f452 -->

The factors so far assume prices stay steady. They don't. Remember that inflation is one of the four reasons money loses value over time (lesson 04)? This lesson gives it numbers.

**Inflation** is a **sustained increase** in the general price level of goods and services **over time**, which reduces the purchasing power of money. Both words matter: a one-off jump in one price is not inflation.

If the price of tomatoes doubles after a bad harvest, that's not inflation. If the price of almost everything rises month after month, that is.

## Measuring inflation
<!-- bite: 5de034fb-9aa1-441f-9e6f-72cc314b0ca4 -->

- **Price level (P)** is the absolute level of prices in an economy.
- **Inflation rate** is the percentage change in the price level from one period to the next:

$$\pi_t = \frac{P_t - P_{t-1}}{P_{t-1}} \times 100$$

- It is measured with three indices: the **consumer price index (CPI)**, the **GDP deflator** and the **producer price index (PPI)**.

**Example:** the CPI was 120 last year and is 132 this year. Inflation = (132 − 120)/120 × 100 = 10%.

## Types of inflation
<!-- bite: 595c095f-b362-43cd-b544-a6f1f278093b -->

1. **Demand-pull:** demand is greater than supply.
2. **Cost-push:** rising production costs push prices up.
3. **Built-in:** a wage-price spiral, where higher wages raise prices and higher prices raise wages.
4. **By speed** (slowest to fastest): creeping, walking, galloping, hyperinflation.

You'll see demand-pull again in lesson 33: when demand grows faster than supply, the equilibrium price rises.

## Nominal and real values
<!-- bite: 4692000b-7147-45f0-a156-b2f9a48277b2 -->

Once prices are rising, a bigger number isn't always more. So we need two kinds of value.

- **Nominal value** is measured in current prices and ignores inflation (nominal wage, nominal interest rate).
- **Real value** is measured in constant prices and accounts for inflation.

To get a real value, divide the nominal value by the price index (written as a ratio to the base year, so 1.2 means prices are 20% higher):

$$\text{Real value} = \frac{\text{Nominal value}}{\text{Price index}}$$

**Example:** your salary rose from ₦50,000 to ₦60,000, but prices rose 20% (index 1.2). Your real salary is 60,000 ÷ 1.2 = ₦50,000. You earn more naira but can buy exactly the same things.

## The real interest rate (Fisher equation)
<!-- bite: 4b732b34-5b37-425d-bee7-360baf912dca -->

The same idea applies to interest. The nominal rate has two parts: the real return and compensation for inflation. Growing by the nominal rate is the same as growing by the real rate and then by inflation:

$$1 + i_{nominal} = (1 + i_{real})(1 + f)$$

f is the inflation rate.

**Example (lecture 3):** nominal 12%, inflation 4%. 1.12 = (1 + i_real)(1.04), so i_real = 1.12/1.04 − 1 = 0.0769, which is **7.69%**.

## The quick approximation
<!-- bite: b97d03d2-1ae4-4bc9-9493-48ae2fad8df5 -->

**Quick approximation:** i_real ≈ i_nominal − f, and i_nominal ≈ i_real + f.

With 15% nominal and 10% inflation, i_real ≈ 5% (the exact answer is 4.55%). The approximation is fine when rates are small. With Nigerian inflation rates it can be well off, so in an exam use the exact form unless told otherwise.

## Going the other way: the combined rate
<!-- bite: 8ccd71a2-fcc5-4622-a068-9bb57c24a628 -->

If a question asks for the combined rate going the other way (real plus inflation), multiply out the Fisher equation. The combined rate d is:

$$d = i + f + if$$

**Example (FE review):** the uninflated present worth of $2,000 in 2 years at i = 10% and f = 6% uses d = 0.10 + 0.06 + 0.006 = 0.166, so P = 2,000 × (1.166)^−2 = $1,471.

This matters because it lets you compare equipment cost across years, judge salaries, project fuel cost, and assess how maintenance cost grows.

Inflation doesn't only change what money buys. It also changes how much tax you pay, even when you're no richer. That's the next lesson.

## Common pitfalls
<!-- bite: 39aa56f4-cc5e-4f0c-b440-c61954cfbfc2 -->

1. **Subtracting when rates are large.** 25% nominal with 20% inflation is a real rate of 1.25/1.20 − 1 = 4.17%, not 5%.
2. **Calling a one-off price rise inflation.** Inflation is sustained and general.
3. **Mixing real and nominal.** Discount real cash flows with a real rate and nominal cash flows with a nominal rate, never one with the other.

## Check your understanding
<!-- bite: dd2aef45-8245-4091-ac38-abf356a0d3ad -->

Try each one before you open the answer.

1. <!-- q: exact id="ab5e584f" answer="10" accept="10%|0.1|0.10" -->
   A country's consumer price index was 250 last year and is 275 this year. What is the inflation rate, in percent?

   <details><summary>Answer</summary>

   (275 − 250)/250 × 100 = 25/250 × 100 = 10%.

   </details>

2. <!-- q: exact id="35ed42b8" answer="0.0550459" sigfigs="3" accept="5.50%|5.5%|5.50|5.5" -->
   A bank pays a nominal rate of 15% and inflation is 9%. Use the Fisher equation to find the real interest rate, as a decimal.

   <details><summary>Answer</summary>

   1 + i_real = 1.15/1.09 = 1.0550, so i_real = 0.0550, about 5.50%. (The quick approximation, 15% − 9% = 6%, is a little high.)

   </details>

3. <!-- q: exact id="0ea93ea3" answer="0.134" sigfigs="3" accept="13.4%|13.4" -->
   A firm wants a real return of 8%, and inflation is expected to be 5%. What nominal rate should it use, as a decimal?

   <details><summary>Answer</summary>

   1 + i_nominal = 1.08 × 1.05 = 1.134, so i_nominal = 0.134, which is 13.4%. (Or d = 0.08 + 0.05 + 0.08 × 0.05 = 0.134.)

   </details>

4. <!-- q: exact id="ee1fb51e" answer="80000" accept="80,000|₦80,000" -->
   A worker's nominal wage is ₦100,000 a month. The price index is 1.25 (prices are 25% above the base year). What is the real wage, in base-year naira?

   <details><summary>Answer</summary>

   Real value = nominal ÷ price index = 100,000 ÷ 1.25 = ₦80,000.

   </details>

5. <!-- q: mcq id="d1031a03" -->
   Workers win a big pay rise, firms raise prices to cover it, and workers then demand another pay rise. What type of inflation is this?

   - [ ] Demand-pull
   - [ ] Cost-push
   - [x] Built-in (wage-price spiral)
   - [ ] Hyperinflation

   <details><summary>Answer</summary>

   Built-in inflation: higher wages raise prices and higher prices raise wages, in a spiral.

   </details>

6. <!-- q: open id="0864f291" -->
   Why are both the words "sustained" and "general" needed in the definition of inflation?

   <details><summary>Answer</summary>

   "Sustained" means the rise continues over time, so a one-off jump is not inflation. "General" means it covers the price level of goods and services as a whole, so a rise in one price (like tomatoes after a bad harvest) is not inflation either. Inflation reduces the purchasing power of money only when most prices keep rising.

   </details>

## Before moving on
<!-- bite: f0f96b5d-c8a2-41fc-803f-47e1704210a7 -->

You can measure inflation, convert between nominal and real values, and use the Fisher equation both ways. **Next:** [[engineering-economics/10-inflation-2|Inflation 2]]: how inflation raises tax for people and companies.

## Related
<!-- bite: 73bd5509-1231-4901-af17-04787236a147 -->

- [[engineering-economics/index|Engineering economics map]]

## About this lesson
<!-- bite: 844048a6-f638-4d8e-9435-0f2259dde900 -->

**Level:** Beginner. **Covers:** the definition and measurement of inflation, the three price indices, the types of inflation, nominal and real values, the Fisher equation, its approximation, and the combined rate.

**Where it sits:** lesson 09 of 38, part 1 of 2 on inflation.

**Source:** the author's own GEG 501 note, section 5 (lecture 3 and the FE review slides). The CPI and salary examples were added for this lesson.
