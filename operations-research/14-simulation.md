---
id: 90fbf1ce-3bc6-4113-a0d5-ebd9628c086b
---

# Simulation

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The code below was run and its output checked.

## Before you start
<!-- bite: 97766f77-95de-40cf-afd2-f0eb5f101fbd -->

You should know the M/M/1 formulas → [[operations-research/12-queueing-theory|note 12]], what a standard deviation and a confidence interval are → [[mathematics/05-probability-statistics/05-inference-and-estimation|inference and estimation]], and write a Python loop with functions.

After this lesson you will be able to:

1. Write a Monte Carlo simulation to estimate a probability or an expected value, with a confidence interval.
2. Write a discrete-event simulation of a queue, and check it against the theory.
3. Name the main ways a simulation gives misleading answers — warm-up, too few runs, a wrong model — and guard against each.

**Study route:** sections 1–3 (Monte Carlo), then run the queue simulation (section 4) and compare with note 12. Then sections 5–6.

## The kid version
<!-- bite: 469b31cb-cbc5-441f-b9fe-619bc06b008a -->

You want to know how often you'd get at least one six when rolling four dice. You could work it out with fractions — or you could just roll four dice a thousand times, count how often a six shows up, and divide. **Simulation is answering a question about chance by acting it out many times, on a computer, very fast.** The more times you act it out, the closer your answer gets to the truth.

**Where the analogy stops working.** Dice are simple and you know their rules exactly. A simulated hospital or factory is only as good as the rules you programmed into it — if your pretend hospital's patients behave differently from real ones, a million runs will give you a very precise wrong answer.

## 1. Why this exists
<!-- bite: 19ce968c-96d3-491a-9f6d-6efd9e9dd8fc -->

Note 12's formulas need assumptions: Poisson arrivals, a constant arrival rate, one class of customer, no breakdowns. A real A&E department has a morning lull and an evening surge, patients of different urgency who jump the queue, doctors who go on break, and beds that block when the wards are full. No formula covers that.

A simulation can. You describe what happens — arrivals, services, priorities, breakdowns — as rules in code, and let the computer play it out. It's the most flexible tool in operations research, and the easiest to get wrong, because it'll always produce a number.

## Terms used in simulation
<!-- bite: 1360f9bb-a580-4057-8294-a429ae926357 -->

1. **Monte Carlo simulation**: This is estimating a quantity by drawing many random samples and averaging. Named after the casino.
2. **Discrete-event simulation**: This is simulating a system as a sequence of events — an arrival, a service finishing — that each happen at a moment in time and change the system's state. Nothing is computed between events.
3. **Replication**: This is one complete independent run of a simulation. Results are averaged across replications.
4. **Pseudo-random number generator**: This is an algorithm that produces numbers that look random but are completely determined by a starting value, the **seed**. The same seed gives the same "random" run, which makes simulations reproducible.
5. **Warm-up period**: This is also known as the **initial transient**. This is the early part of a run, before the system has settled into typical behaviour, which is usually thrown away. A queue that starts empty is unusually short at first.
6. **Confidence interval**: This is a range that, by a stated procedure, contains the true value with a stated probability, such as 95%. It's how a simulation reports its uncertainty.
7. **Verification**: This is checking that the code does what you meant — the model is *built right*.
8. **Validation**: This is checking that what you meant matches reality — you *built the right model*.

## 2. Monte Carlo: estimate by sampling
<!-- bite: 1195a66f-f4e0-43cd-ac2b-c09d43e06ca1 -->

**The method states that the average of many independent random samples of a quantity approaches its true expected value, and the error shrinks with the square root of the number of samples.**

That's the law of large numbers, plus the central limit theorem for the error. Concretely, with $n$ samples of standard deviation $s$:

$$\text{95\% confidence interval} \approx \bar{x} \pm 1.96\,\frac{s}{\sqrt{n}}$$

**The square root is the catch.** To halve the error, you need four times as many samples. To get one more decimal digit, a hundred times as many.

### Example: a project with uncertain durations

Take the project from [[operations-research/06-network-models|note 06, section 6]]: A (3 days) then B (5) and C (6), D (2) after B, E (3) after C and D. CPM said 13 days. But suppose each duration is really uncertain — say uniformly within ±1 day of the estimate. What's the chance the project takes longer than 14 days?

The Monte Carlo recipe:

1. Draw a random duration for each activity.
2. Compute the project length with the forward pass (the longest path).
3. Repeat many times; the answer is the fraction of runs over 14.

A key effect appears that CPM can't show: **the expected project length is more than 13 days**, even though every activity's expected duration is unchanged. E has to wait for the *later* of C and D, and the maximum of two random things is, on average, more than the maximum of their averages. Path C (3 + 6 = 9 before E) and path B–D (3 + 5 + 2 = 10) are close, so sometimes C is the late one. Every merge point in a project adds expected delay — one reason projects run late more often than early.

## 3. Discrete-event simulation
<!-- bite: 50c251a1-2900-4ddc-bb38-e5a950af9db7 -->

For queues and other systems that evolve over time, you don't simulate every second. You jump from event to event.

**For a single-server queue, each customer needs three numbers:**

1. **Arrival time**: the previous arrival plus a random gap.
2. **Start of service**: the later of their arrival and the moment the server becomes free.
3. **End of service**: start plus a random service time.

Their time in the system is end minus arrival. That's the whole simulation for first-come first-served with one server — about ten lines.

For more complex systems (several servers, priorities, breakdowns), you keep a **future event list** — a priority queue of upcoming events sorted by time — and repeatedly pop the earliest, update the state, and schedule any events it causes → [[dsa/02-data-structures/07-heaps|DSA: heaps]]. Libraries like SimPy handle that bookkeeping.

## 4. Worked example — simulating M/M/1 against the formula
<!-- bite: 08e452f2-f6a8-4c23-88f8-b0015c3a74fb -->

**Runnable**, standard library only. Takes a few seconds.

```python
# mm1_sim.py — note 14: simulate an M/M/1 queue and compare with the formula
import random

def simulate(lam, mu, customers=200_000, seed=1):
    rng = random.Random(seed)
    arrival = server_free_at = total_time_in_system = 0.0
    for _ in range(customers):
        arrival += rng.expovariate(lam)            # next customer turns up
        start = max(arrival, server_free_at)        # waits if the server is busy
        server_free_at = start + rng.expovariate(mu)
        total_time_in_system += server_free_at - arrival
    return total_time_in_system / customers

for lam in (5, 8, 9, 9.5):
    print(f"lambda={lam:>4}: simulated W = {simulate(lam, 10):.3f} h, formula 1/(mu-lambda) = {1/(10-lam):.3f} h")
```

```bash
python3 mm1_sim.py
```

Expected output (with seed 1; other seeds give slightly different numbers):

```
lambda=   5: simulated W = 0.200 h, formula 1/(mu-lambda) = 0.200 h
lambda=   8: simulated W = 0.497 h, formula 1/(mu-lambda) = 0.500 h
lambda=   9: simulated W = 0.986 h, formula 1/(mu-lambda) = 1.000 h
lambda= 9.5: simulated W = 2.204 h, formula 1/(mu-lambda) = 2.000 h
```

**Read it carefully, because it teaches two things.**

1. **The simulation verifies against theory.** At low and moderate load, it matches the formula closely. That's the first test any simulation should pass: on a case with a known answer, does it get it right? If not, the code is wrong.
2. **At high load, it's 10% off — even with 200,000 customers.** That isn't a bug. Near $\rho = 1$, waiting times are hugely variable and strongly correlated from one customer to the next (if one waits a long time, the next one probably does too). The effective number of independent samples is far smaller than 200,000, and the error shrinks slowly. **Heavily loaded systems need much longer runs, or many replications, to estimate well.** Try a few different seeds at $\lambda = 9.5$ and watch the answer move.

## 5. Making simulation results trustworthy
<!-- bite: 95fbee78-f2aa-4268-b1ab-f25817b8e5e0 -->

A simulation always prints a number. These habits decide whether the number means anything.

1. **Verify on a case with a known answer.** As in section 4. Then add complications one at a time.
2. **Run several independent replications** (different seeds), and report a confidence interval, not a single number. Averaging *within* one long run underestimates the error, because successive customers are correlated.
3. **Discard a warm-up period.** A queue that starts empty spends its early period unusually uncrowded. Plot the running average against time and cut where it flattens.
4. **Use the same random numbers to compare designs.** When comparing "2 servers vs 3", feed both the same arrival sequence (common random numbers). Then differences come from the design, not from luck, and far fewer runs are needed.
5. **Validate against reality.** Run the simulation on last month's actual arrivals and compare its predicted waits with the waits that actually happened. If they disagree, the model is missing something, and that's the most useful thing you can learn.
6. **Fix the seed for debugging, vary it for results.** Reproducible runs make bugs findable; multiple seeds make conclusions robust.

## 6. Simulation and optimisation together
<!-- bite: 751c9c4f-ebbe-4496-9a15-f5c3a2d96386 -->

Simulation evaluates one design at a time. To *choose* a design, you combine it with search:

1. **Compare a few options.** Simulate each candidate with common random numbers and pick the best, with confidence intervals on the differences. Often enough.
2. **Simulation-optimisation.** Wrap the simulation inside a search — a grid, a heuristic from note 10, or Bayesian optimisation — that proposes designs and uses simulated performance as the objective. Expensive, because each evaluation is a whole simulation, and noisy, because each evaluation is random.
3. **Optimise, then simulate.** Solve a simplified optimisation model (an LP or MILP with average values), then check its plan in a detailed simulation. This is very common in practice: the optimiser handles the combinatorics, the simulation checks the plan survives randomness.

**That last pattern summarises the whole track.** Optimisation models (notes 02–10) choose; stochastic models and simulation (notes 11–14) test the choice against uncertainty.

## Common pitfalls and traps
<!-- bite: b1e6e89e-7fa8-420e-914a-2b85e38a3dad -->

1. **One run, one number.** No confidence interval, no idea whether a difference is real.
2. **Same seed everywhere.** Every "replication" is identical, and the confidence interval collapses to zero.
3. **No warm-up deletion.** Starting empty biases waits low.
4. **Wrong distributions.** Using exponential service when real service times have a heavy tail underestimates queues badly (note 12, section 6). Fit distributions to data where you can.
5. **Mistaking precision for accuracy.** A million runs of a wrong model give a tight confidence interval around the wrong answer. Validation, not replication count, is what protects you.
6. **Building the simulation before asking whether a formula would do.** Note 12's formulas answer many questions in a line. Simulate when they can't.

## Check your understanding
<!-- bite: cff697c4-9383-406b-a807-1a196447072a -->

1. A Monte Carlo estimate from 1,000 samples has a 95% confidence interval of ±4. Roughly how many samples would you need for ±1?
2. Why is the high-load simulation in section 4 less accurate than the low-load one, even with the same number of customers?
3. Why does the project in section 2 take longer on average than its CPM length, even though no activity's average duration changed?
4. You're comparing 2 and 3 cashiers by simulation. Why should both designs see the same random arrival sequence?

<details>
<summary>After your attempt — answers</summary>

1. The error shrinks with $1/\sqrt{n}$. To divide it by 4, multiply $n$ by 16: about 16,000 samples.
2. At high load, waiting times are much more variable and successive customers' waits are strongly correlated, so 200,000 customers carry much less independent information. The estimate converges slowly.
3. E starts at the later of C's and D's finish. Taking the maximum of two random times gives, on average, more than the maximum of their averages: whenever C runs late, the project waits for C, but D finishing early never helps. Merge points convert variability into delay.
4. So that the difference between the designs reflects the designs, not luck. With independent arrivals, one design might happen to get a quiet day. Common random numbers cancel that noise and need far fewer replications.

</details>

## Practice — independent task
<!-- bite: 2928b266-3770-47f4-9a01-0b83caf2e9af -->

1. **Monte Carlo the project.** Write `project_mc.py`: draw each activity's duration uniformly within ±1 day of note 06's estimates, compute the project length by the forward pass, and run 100,000 times. Report the mean length with a 95% confidence interval, and $P(\text{length} > 14)$.
2. **Extend the queue.** Modify `mm1_sim.py` to (a) run 20 replications with different seeds at $\lambda = 9$ and report a confidence interval for $W$; (b) use *fixed* service times of 0.1 h (M/D/1), and check against note 12's Pollaczek–Khinchine result that $W_q$ halves.
3. **Something the formulas can't do.** Simulate a 12-hour day where arrivals are 6 per hour for the first 4 hours, 12 per hour for the next 4, and 6 per hour for the last 4, with 1 server at $\mu = 10$. Plot or print the average wait by hour. What happens in the busy period, and when does the queue recover?

**Done when:** part 1 reports a mean above 13 with its interval; part 2's confidence interval contains the formula's 1.0 and the M/D/1 wait is about half; part 3 shows (in numbers) the queue growing during the rush, when $\rho > 1$, and draining afterwards — a behaviour steady-state formulas can't describe.

## Before moving on
<!-- bite: 3be6c6d1-ea80-4da7-9195-566ed8035dfc -->

You're ready when you can write a Monte Carlo estimate with a confidence interval, write a single-server queue simulation from memory, verify it against M/M/1, and list the habits that make a simulation's answer trustworthy.

**Recap:**

1. Monte Carlo averages random samples; the error shrinks with $1/\sqrt{n}$.
2. Discrete-event simulation jumps from event to event; a single-server queue is ten lines.
3. Verify on known cases, replicate with different seeds, delete warm-up, use common random numbers, validate against reality.
4. Optimise to choose, simulate to check — the pattern that ties the track together.

**Next:** this is the last core note. Go to the [[operations-research/projects|projects]] — the rest of the learning happens there.

## Related
<!-- bite: aef2aa70-c881-45ac-9c72-408337e72459 -->

- [[operations-research/12-queueing-theory|Queueing Theory]] — the formulas to verify against
- [[operations-research/06-network-models|Network Models]] — the project being simulated
- [[mathematics/05-probability-statistics/05-inference-and-estimation|Inference and estimation]] — confidence intervals
- [[dsa/02-data-structures/07-heaps|DSA: heaps]] — the future event list
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: ac0e50ca-1fee-4f90-8b0b-e4ed0a00825e -->

**Level:** Intermediate. **Covers:** When a system is too messy for formulas — rush hours, breakdowns, priorities, odd distributions — build it in code, run it thousands of times, and measure. This note covers Monte Carlo and discrete-event simulation, how to tell whether a simulation's answer can be trusted, and how simulation and optimisation fit together.
