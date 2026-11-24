---
id: 026023f6-920c-47b0-9614-caba6bc6bd43
---

# Input Analysis 2: Choosing a Distribution

The right distribution for an input depends on whether the data is discrete or continuous, what is known about it, and the physical process behind it.

## Before you start
<!-- bite: 6444fa9d-ce7c-4f2c-a81d-f25cf46b86e9 -->

You should have read [[systems-simulation/27-input-analysis-1|27 — Input Analysis 1]].

After this lesson you will be able to:

1. ask the five questions that guide the choice of a distribution;
2. match common discrete and continuous distributions to their typical uses;
3. explain the link between Poisson counts and exponential gaps.

## What choosing a distribution means
<!-- bite: f968e3e4-ac6c-4b43-b855-e4b16fc224f7 -->

Step 2 of input analysis is choosing the distribution that describes the data. There are dozens of distributions, but a short list covers nearly every simulation input. This lesson gives that list, the questions that narrow it down, and one link between two distributions that the whole of queueing rests on.

## The five questions
<!-- bite: 3d338452-2d81-489d-b163-0739e7cf299b -->

1. Is the data **discrete** (separate values, such as a count) or **continuous** (any value in a range, such as a time)?
2. Is it **univariate** (one variable) or **multivariate** (several that move together)?
3. How much data is there?
4. Are there experts you can ask about its nature?
5. If there is very little data, can you still guess a reasonable distribution from what you know about the process?

## Discrete distributions
<!-- bite: e350acba-2b75-4031-b1a6-d9367ad3ba49 -->

| Distribution | Typical use |
| --- | --- |
| Bernoulli(p) | One trial: success or failure. Does this part pass inspection? |
| Binomial(n, p) | Number of successes in n trials. How many of 20 parts pass? |
| Geometric(p) | Number of trials until the first success. How many calls until one answers? |
| Negative binomial | Number of trials until a fixed number of successes |
| Poisson(λ) | Count of arrivals in a time interval. How many cars per minute? |
| Empirical | The sample distribution taken from the data itself |

## Continuous distributions
<!-- bite: d554c9de-09f8-4f78-b09c-9c746f4e130b -->

| Distribution | Typical use |
| --- | --- |
| Uniform | Only the minimum and maximum are known |
| Triangular | Minimum, maximum and most likely value are known |
| Exponential(λ) | Inter-arrival times of a Poisson process; time between failures |
| Normal | Heights, weights, sample means, averages and sums |
| Beta | Data bounded between two limits, such as a fraction |
| Gamma, Weibull, Gumbel, lognormal | Reliability data, and job or repair times |
| Empirical | The sample distribution taken from the data itself |

## The Poisson–exponential link
<!-- bite: 24bf9a88-8f9a-4dc8-a881-52177388bf6a -->

**If the number of arrivals in an interval is Poisson, then the time between arrivals is exponential.** They are two descriptions of the same random process: one counts, one measures gaps. With λ = 12 arrivals per hour, the count per hour is Poisson(12) and the gap between arrivals is exponential with mean 1/12 hour = 5 minutes.

That is why M in Kendall's notation (lesson 11) means both "Poisson arrivals" and "exponential inter-arrival times".

## Matching data to a distribution
<!-- bite: 4c4b875e-c2cc-4e73-84e5-2977059bcec1 -->

Some examples of the thinking:

1. **Vehicles arriving per minute at a junction:** a count, so discrete; arrivals happen independently, so **Poisson**.
2. **Passengers per vehicle:** a small count with a fixed maximum, so **binomial** or **empirical**.
3. **Travel speed:** continuous and roughly symmetric, so **normal**, or **lognormal** if it can't go below zero.
4. **Trip duration or repair time:** continuous, positive and skewed, so **gamma**, **Weibull** or **lognormal**.
5. **A brand-new process with no data:** ask an expert for the minimum, maximum and most likely time, and use **triangular**.

## Common pitfalls
<!-- bite: 3a60c219-d8ae-4a0a-9d37-6aca2ea6479b -->

1. **Using a continuous distribution for counts.** Customers per hour are whole numbers.
2. **Normal for times that must be positive.** A normal can go negative; lognormal or gamma can't.
3. **Forgetting the empirical option.** If nothing fits, sample from the data itself.

This lesson assumed tidy data. Real data is often thin, lumpy, changing over time or correlated. Next lesson handles those four problems.

## Check your understanding
<!-- bite: 07f213d6-b5f6-468b-8078-dce8d1f635fd -->

Try each one before you open the answer.

1. <!-- q: mcq id="564ae751" -->
   Calls arrive at a help desk as a Poisson process, averaging 20 per hour. What is the distribution of the time between calls?

   - [ ] Poisson with mean 20
   - [x] Exponential with mean 3 minutes
   - [ ] Normal with mean 3 minutes
   - [ ] Uniform from 0 to 6 minutes

   <details><summary>Answer</summary>

   Exponential with mean 60/20 = 3 minutes. Poisson counts go with exponential gaps.

   </details>

2. <!-- q: mcq id="7a8f2d21" -->
   A new machine has never run. An engineer says it will take at least 4 minutes per part, at most 10, and most likely 6. Which distribution should you use?

   - [ ] Uniform(4, 10)
   - [x] Triangular(4, 6, 10)
   - [ ] Exponential with mean 6
   - [ ] Poisson(6)

   <details><summary>Answer</summary>

   Triangular, since you know the minimum, the most likely value and the maximum. Uniform throws away the "most likely 6".

   </details>

3. <!-- q: mcq id="b2498875" -->
   Which distribution fits "the number of defective parts in a box of 25, when each part is defective with probability 0.04"?

   - [ ] Geometric
   - [x] Binomial(25, 0.04)
   - [ ] Exponential
   - [ ] Normal

   <details><summary>Answer</summary>

   Binomial: the number of successes (here, defects) in a fixed number of independent trials.

   </details>

4. <!-- q: open id="d8fd3d30" -->
   For an urban traffic model, name one discrete and one continuous input, and suggest a distribution for each.

   <details><summary>Answer</summary>

   For example. Discrete: vehicles arriving per minute, Poisson. Continuous: trip duration, gamma or lognormal (or the time between vehicles, exponential; or speed, normal).

   </details>

5. <!-- q: mcq id="cfc5c74e" -->
   Which of these is NOT one of the questions that guide the choice of a distribution?

   - [ ] Is the data discrete or continuous?
   - [ ] How much data is available?
   - [ ] Are there experts to ask?
   - [x] Which simulation software will be used?

   <details><summary>Answer</summary>

   The software doesn't decide the distribution; the data and the process do.

   </details>

## Before moving on
<!-- bite: 1fd0e2db-d4a4-4b95-82e8-82e8a4eb5a3f -->

You can choose a distribution from the questions and the two tables, and explain the Poisson–exponential link. **Next:** [[systems-simulation/29-input-analysis-3|29 — Input Analysis 3]]: four common data challenges.

## Related
<!-- bite: 0c774457-8be0-4399-aa54-fa8c1bf456eb -->

- [[systems-simulation/index|Systems simulation map]]
- [[mathematics/index|Mathematics]]: probability distributions in depth.

## About this lesson
<!-- bite: 075a5b41-eab1-44ca-84c1-0001bce9ecc4 -->

**Level:** Beginner to intermediate. **Covers:** the five questions, common discrete and continuous distributions, the Poisson–exponential link, and examples of matching data to a distribution.

**Where it sits:** lesson 28 of 38, part 2 of 3 on input analysis.

**Source:** the author's own SSG 517 study notes, sections 6 and 9 (Q3).
