---
id: f3c0091d-ad7d-4be3-85f8-068857bb013b
---

# Collecting and Preparing Data

Good input data comes from the right sources, collected the right way, and cleaned before any distribution is fitted.

## Before you start
<!-- bite: 46cc982c-f5cd-4bdf-b8e1-8180705827d3 -->

You should have read [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3]].

After this lesson you will be able to:

1. list the data a hospital model needs, and where it comes from;
2. compare three ways of collecting queue data, with a strength and weakness of each;
3. describe the five-stage data preprocessing framework and the harm done by missing data.

## What good input data is
<!-- bite: 2a2844f3-506e-44bc-b2a5-eceefc349fc8 -->

Lessons 27 to 29 assumed you already had data. This lesson is about getting it and preparing it. It follows the 2024/25 paper's hospital and kiosk questions, using the author's own handwritten answers, so it doubles as exam practice.

## What a hospital model needs
<!-- bite: 0e9ea7b0-ce01-41b5-b0b3-695f448e2a7d -->

1. **Arrival data:** inter-arrival times, broken down by hour (because arrivals are nonstationary).
2. **Service times** at each station: triage, consultation, lab, pharmacy.
3. **Resource data:** beds, doctors, nurses, lab capacity.
4. **Routing logic:** the path each patient follows. It matters because it catches circular bottlenecks, such as a patient holding an emergency bed while waiting for lab results.

**Sources:** hospital databases (large samples), **time studies** (watching the flow and timing each station), and **interviews** with doctors, nurses and technicians where data is missing.

## Three ways to collect queue data
<!-- bite: 546e07cd-16cb-445a-9234-7cd6fd196cc6 -->

For a kiosk or service queue:

| Method | How | Strength | Weakness |
| --- | --- | --- | --- |
| Manual observation (time study) | Stopwatch or phone app, record each customer's times | The most reliable way to capture people who walk away or jump the line | Labour-intensive |
| Automated queue system | Pull timestamps from kiosks and logs | A huge cleaned dataset over long periods, good for spotting nonstationary trends | Only records customers who actually take a ticket |
| Expert interviews | Staff describe boundaries and typical behaviour | Works when no hard data exists | Subjective; the last resort |

Notice how the methods cover each other's gaps: the automated system misses the people who balk, and manual observation catches exactly them.

## The challenges
<!-- bite: a8cfa3a4-727a-4cd5-b736-09f6ecfb0890 -->

The usual problems: no or little data, poor data quality, **observation bias** (people work differently when watched), mixture distributions, nonstationary data and correlated data.

## The harm missing or inconsistent data does
<!-- bite: 9fc6faad-6750-4c0c-a854-1ac997d8dfa7 -->

1. **GIGO:** flawed input data gives wrong output, however good the model.
2. **Underestimated queues:** missing peak-hour data makes the model show less stress than the real system has.
3. **Wrong resource decisions:** inconsistent data can make a busy teller look idle, so management cuts the wrong staff.
4. **Validation failure:** the model won't match the real system, so it can't pass its checks.

## Fixing it
<!-- bite: 0980e299-f05d-4c25-af99-2a77e7c9dd9b -->

1. **Expert interviews** to fill gaps.
2. **Data cleaning:** remove outliers that don't represent typical operations, such as a day the system was down.
3. **Homogeneity testing:** if data came from different days, test statistically whether it comes from the same population before merging.
4. **Different rates for different times** of day, for nonstationary arrivals.
5. **An empirical distribution** when the data fits no standard curve.
6. **Validation:** face validity, input-output comparison, and a **Turing test**: give the administrator one model-generated report and one real one; if they can't tell which is which, the model is credible.

## The preprocessing framework
<!-- bite: f1e8d007-1f83-47db-a00c-853378ac6817 -->

Five stages, in order:

1. **Data cleaning and filtering.**
2. **Stationarity analysis:** split the data into periods if it changes over time.
3. **Exploratory data analysis:** histograms for the general shape; stem-and-leaf diagrams to see the detail.
4. **Independence testing:** check the observations are independent and identically distributed.
5. **Distribution fitting and parameter estimation:** hypothesise a distribution from the physical process, fit it, test it.

Why it matters: it prevents GIGO, builds the model's credibility, captures real variability, and avoids wrong conclusions.

## Common pitfalls
<!-- bite: da4d8220-b826-43df-bf1b-190f6e19c714 -->

1. **Relying on one source.** Each method misses something; combine them.
2. **Fitting before cleaning.** One bad day can distort a whole distribution.
3. **Merging data from different conditions** without a homogeneity test.

The inputs are ready. Now the model itself must earn trust. The next part is verification and validation: was it built right, and is it the right model?

## Check your understanding
<!-- bite: 71c9434b-44ca-40cb-b6ba-668eccd88e2e -->

Try each one before you open the answer.

1. <!-- q: mcq id="569b1305" -->
   A bank's ticket machine records every customer who takes a ticket. Which customers does this data miss?

   - [ ] Customers served by the second teller
   - [x] Customers who see the queue and leave without taking a ticket
   - [ ] Customers who arrive in the afternoon
   - [ ] None; it records everyone

   <details><summary>Answer</summary>

   The ones who balk. Manual observation is needed to capture them.

   </details>

2. <!-- q: open id="df4ccf94" -->
   For a hospital model, name the four kinds of data to collect and one source for them.

   <details><summary>Answer</summary>

   Arrival data (inter-arrival times by hour), service times at each station, resource data (beds, doctors, nurses, labs) and routing logic (each patient's path). Sources: hospital databases, time studies, and interviews with staff.

   </details>

3. <!-- q: mcq id="20b9f118" -->
   What is the Turing test in model validation?

   - [ ] A test of the random number generator
   - [x] Experts are shown a real report and a model-generated one; if they can't tell them apart, the model is credible
   - [ ] A chi-square test on output
   - [ ] A test of the computer's speed

   <details><summary>Answer</summary>

   An expert tries to tell model output from real output. Failing to tell them apart is evidence the model is credible.

   </details>

4. <!-- q: open id="75c00cdc" -->
   Put the five stages of the preprocessing framework in order.

   <details><summary>Answer</summary>

   (1) Data cleaning and filtering, (2) stationarity analysis, (3) exploratory data analysis, (4) independence testing, (5) distribution fitting and parameter estimation.

   </details>

5. <!-- q: open id="5d03485e" -->
   A model of a post office was built without peak-hour data. Explain two consequences.

   <details><summary>Answer</summary>

   Queues are underestimated, because the model never sees the busiest hour's stress. And resources are mis-sized: management may conclude fewer counters are needed than the peak really requires, so customers wait far longer than the model says. The model would also likely fail validation against real peak-hour queues.

   </details>

## Before moving on
<!-- bite: 3f30f322-dfbb-40d5-a9d4-47d0e745b853 -->

You can plan data collection, compare methods, and prepare data with the five-stage framework. **Next:** [[systems-simulation/31-verification-and-validation-1|31 — Verification and Validation 1]].

## Related
<!-- bite: 86945957-1554-4b9d-a9a6-817d402986e5 -->

- [[systems-simulation/index|Systems simulation map]]
- [[data-engineering/index|Data Engineering]]: cleaning and preparing data at scale.

## About this lesson
<!-- bite: ba8bf155-d3c1-4510-9bfb-acaeca5d3bdb -->

**Level:** Beginner to intermediate. **Covers:** data for a hospital model, three collection methods, the challenges, the harm of missing data, the fixes, and the five-stage preprocessing framework.

**Where it sits:** lesson 30 of 38, the end of part 7 (input analysis and data).

**Source:** the author's own SSG 517 study notes, section 10 (his handwritten 2024/25 answers).
