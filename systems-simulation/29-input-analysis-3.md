---
id: 0bb2f54a-9661-40fc-a526-296afe991a96
---

# Input Analysis 3: Four Common Data Challenges

Real input data is often thin, lumpy, changing over time or correlated, and each of these four problems has its own fix.

## Before you start
<!-- bite: a192deb3-3ce9-4186-85de-be8a3f082cdf -->

You should have read [[systems-simulation/28-input-analysis-2|28 — Input Analysis 2]].

After this lesson you will be able to:

1. model an input when there is little or no data;
2. handle mixture distributions and nonstationary arrivals;
3. explain what goes wrong when correlated data is treated as independent, and how to model it.

## What the four challenges are
<!-- bite: 6c3ee994-b884-4647-aa40-ea51ffbc5d85 -->

Lesson 28 assumed plenty of clean, steady, independent data. Real data rarely is. The four challenges here are the heart of the exam's input-modelling and data-challenges questions: (1) little or no data, (2) mixtures, (3) nonstationary data and (4) correlated data. For each one: what it looks like, and what to do.

## 1. Little or no data
<!-- bite: 6b560b9c-a2d4-4d39-9fcd-92f30f41221e -->

This turns up more often than you'd expect: there may be no data, or the data is awful, full of odd values and never cleaned. There are no great options, but you can:

1. **Ask experts** for the minimum, maximum and most likely values, and use a **uniform** or **triangular** distribution. Quantiles from the expert ("90% of jobs take under 12 minutes") are even better.
2. **Decide discrete or continuous,** then use the process: success or failure observations suggest Bernoulli, binomial, geometric or negative binomial; counts of arrivals suggest Poisson, and the gaps exponential; averages or sums suggest normal; bounded values suggest beta; reliability or job times suggest gamma, Weibull or lognormal.
3. **Think about the physical process** behind the variable.
4. Use **sensitivity analysis** (lesson 32) to see how much the guess matters.

## 2. Nonstandard or mixture distributions
<!-- bite: 0d7b3d67-5f05-4173-8b29-0cca4b1135cf -->

Some data looks like two normal curves pushed together: two humps. A hospital's treatment times might mix quick check-ups and long procedures. Most fitting software can't fit that. Options:

1. **Model it as a mixture,** piece by piece: with probability 0.7 draw from the check-up distribution, otherwise from the procedure one.
2. **Sample from the empirical distribution,** or a smoothed version of it. Sampling straight from the data is a form of **bootstrapping**.

## 3. Nonstationary data
<!-- bite: 163c53fa-c5b1-4ed8-85aa-182566a018d8 -->

The arrival rate changes over time: restaurants, highway traffic, call centres, seasonal demand. Ignore it and you get GIGO, because the peaks vanish into the average.

The fix is a **nonhomogeneous Poisson process (NHPP)**: a Poisson process whose rate is a function of time. A practical way is a **constant rate within each period**, such as each hour: 10 per hour from 8 to 9, 25 per hour from 12 to 1, and so on.

## 4. Multivariate or correlated data
<!-- bite: 0fa13be6-af6f-4ef6-90df-f142ec750265 -->

Data doesn't have to be independent and identically distributed. Examples:

1. a person's height and weight are correlated;
2. monthly unemployment rates are serially correlated, each month like the last;
3. arrivals to a website jump when something goes viral;
4. a badly damaged part may need longer service at several stations in a row;
5. a tired server gives longer service times.

What to do:

1. Identify the kind of correlation and propose a model: **multivariate normal** for related variables like height and weight, **time series models** such as ARMA(p, q) or EAR(1) for serial correlation.
2. Estimate the parameters. For a multivariate normal: the means, variances and covariances.
3. Validate that the fitted model is actually good.
4. Or, with enough data, **bootstrap** from the empirical data.

## Why ignoring correlation is dangerous
<!-- bite: 310cdf79-c6dd-43f2-9d67-119617ed4368 -->

If busy periods also bring longer service, the two effects pile on top of each other: more customers *and* each taking longer. Model them as independent and the model loses that pile-up. It produces **too little variability**: queues look shorter and delays smaller than reality, and staffing decisions built on it are over-optimistic.

## Common pitfalls
<!-- bite: 128ba45b-3ba9-4e3c-8447-1e43bc31a867 -->

1. **Giving up when there is no data.** Experts and the physical process still give a defensible distribution.
2. **Forcing one distribution onto two humps.** Use a mixture or the empirical data.
3. **One rate for the whole day.** Use a rate per period.
4. **Assuming independence because it's easier.** It biases the model towards optimism.

Every challenge here starts with how the data was collected in the first place. Next lesson covers collecting and preparing data in practice, using the 2024/25 paper's hospital and kiosk questions.

## Check your understanding
<!-- bite: 2aeda242-3fa3-4dbe-a269-80ecc390b533 -->

Try each one before you open the answer.

1. <!-- q: mcq id="a3191802" -->
   A new clinic has no records. A nurse says a consultation takes between 5 and 25 minutes, most often 10. What should you do?

   - [ ] Wait until a year of data has been collected
   - [x] Use Triangular(5, 10, 25) from the nurse's estimate, and test how sensitive the results are to it
   - [ ] Assume every consultation takes 10 minutes
   - [ ] Leave consultation time out of the model

   <details><summary>Answer</summary>

   Use the expert's minimum, most likely and maximum in a triangular distribution, then check with sensitivity analysis how much the guess affects the answer.

   </details>

2. <!-- q: mcq id="52ced077" -->
   A call centre receives 40 calls an hour in the morning and 120 an hour after lunch. How should arrivals be modelled?

   - [ ] A Poisson process with the daily average of 80 per hour
   - [x] A nonhomogeneous Poisson process, with a separate rate for each period
   - [ ] A constant gap of 45 seconds
   - [ ] A normal distribution

   <details><summary>Answer</summary>

   A nonhomogeneous Poisson process: a constant rate within each period, changing between periods. The daily average would hide the afternoon peak.

   </details>

3. <!-- q: open id="10d7b3e2" -->
   A hospital's treatment-time histogram has two clear humps, one around 10 minutes and one around 60. Give two ways to model it.

   <details><summary>Answer</summary>

   Model it as a mixture: with some probability draw from a short-treatment distribution, otherwise from a long one, with the probabilities and the two distributions fitted from the data. Or sample directly from the empirical (or smoothed empirical) distribution, a form of bootstrapping.

   </details>

4. <!-- q: open id="b8fe72bf" -->
   In an emergency department, busy nights also bring sicker patients who need longer treatment. What goes wrong if the model treats arrivals and treatment times as independent?

   <details><summary>Answer</summary>

   It misses the pile-up of more patients each needing more time, so it produces too little variability. Queues and waits come out shorter than in reality, and decisions on staff and beds are over-optimistic. Model the correlation, for example with a multivariate distribution, or bootstrap from the real data.

   </details>

5. <!-- q: gap id="99c02815" answers="multivariate normal;time series|time-series" -->
   For correlated variables like height and weight, use a ___ distribution. For serial correlation, like monthly unemployment, use ___ models such as ARMA or EAR(1).

   <details><summary>Answer</summary>

   Multivariate normal, then time series models.

   </details>

## Before moving on
<!-- bite: 2bb6ee85-d07f-4489-b927-3f9b26221395 -->

You can handle the four data challenges and explain the danger of ignoring correlation. **Next:** [[systems-simulation/30-collecting-and-preparing-data|30 — Collecting and Preparing Data]].

## Related
<!-- bite: d3a397bf-23fb-421c-9817-19f190f60f93 -->

- [[systems-simulation/index|Systems simulation map]]

## About this lesson
<!-- bite: 9849d234-6f14-478c-a3d1-ec73475eeb41 -->

**Level:** Intermediate. **Covers:** little or no data, mixtures, nonstationary data and the nonhomogeneous Poisson process, correlated data, and why ignoring correlation biases the model.

**Where it sits:** lesson 29 of 38, part 3 of 3 on input analysis.

**Source:** the author's own SSG 517 study notes, sections 6 and 9 (Q4). The sensitivity-analysis tip for little data comes from the Q4 answer outline.
