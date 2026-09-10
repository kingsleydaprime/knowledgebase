# Inference and Estimation

**[Advanced]** — reasoning from a sample back to the population, and what a confidence interval actually promises.

## Before you start

- You know expectation, variance and the normal distribution — [[04-random-variables-and-distributions/01-distributions|distributions]].
- You know why sample variance divides by $n-1$ — [[02-dispersion-and-cumulative-frequency/01-dispersion|dispersion]].
- You can apply Bayes' theorem — [[03-probability/01-probability|probability]].

**What you will be able to do after this lesson:**

1. State the **Central Limit Theorem** and demonstrate it on a distribution that looks nothing like a normal.
2. Explain why the standard error is $\sigma/\sqrt{n}$, and what that implies about the cost of precision.
3. Construct a **confidence interval**, and state precisely what the $95\%$ refers to — and what it does not.
4. Run a hypothesis test, interpret a $p$-value correctly, and name the two error types.

**Study route:** read 1–5, attempt the prediction in section 3, then run the lab. Block 3 measures whether the intervals do what they claim.

---

## 1. Why this exists

You cannot measure the population. You measure a sample and want to say something about the whole.

That step is not arithmetic; it is an **inference**, and it can be wrong. The discipline of statistics is largely about quantifying *how* wrong it might be — not eliminating uncertainty, which is impossible, but bounding it and stating the bound honestly.

Two things make this lesson worth doing slowly. First, one theorem — the Central Limit Theorem — does almost all the work, and it is genuinely surprising. Second, the standard summary of the result, the $p$-value, is the most widely misinterpreted number in science, including by people who use it daily.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Parameter** | A number describing the **population** | $\mu$, $\sigma$ — fixed and unknown |
| **Statistic** | A number computed from the **sample** | $\bar{x}$, $s$ — known and random |
| **Estimator** | A recipe for guessing a parameter | $\bar{x}$ estimates $\mu$ |
| **Unbiased** | Right *on average* over many samples | The $n-1$ variance is unbiased |
| **Sampling distribution** | The distribution of a statistic across samples | The central idea of the lesson |
| **Standard error** | The standard deviation of a **statistic** | $\sigma/\sqrt{n}$ for a mean |
| **Confidence interval** | A range built by a procedure with a stated hit rate | Not "probability the parameter is inside" |
| **Null hypothesis** $H_0$ | The default, no-effect claim | You reject it or fail to |
| **$p$-value** | $P(\text{data this extreme} \mid H_0 \text{ true})$ | **Not** $P(H_0 \mid \text{data})$ |

The distinction between **parameter** and **statistic** carries the whole lesson. $\mu$ is fixed and unknown. $\bar{x}$ is known and varies from sample to sample. Inference is about that variation.

## 3. The Central Limit Theorem

> Take samples of size $n$ from **any** distribution with finite mean $\mu$ and variance $\sigma^2$. As $n$ grows, the distribution of the **sample mean** approaches a normal distribution with mean $\mu$ and standard deviation $\sigma/\sqrt{n}$.

Three things deserve emphasis:

- **"Any distribution."** Skewed, bimodal, discrete, ugly — it does not matter, provided the variance is finite. The lab starts from a violently skewed distribution and from a two-spike bimodal one, and both produce a normal sampling distribution.
- **It is about the *mean*, not the data.** Individual measurements do not become normal. Averages of them do. Confusing these is the most common misuse.
- **The $\sqrt{n}$ is the whole economics of sampling.** Variances add for independent variables, so the variance of a sum of $n$ is $n\sigma^2$; dividing by $n$ to make a mean gives variance $\sigma^2/n$, and a standard deviation of $\sigma/\sqrt{n}$.

That square root is expensive. To halve your uncertainty you need **four times** the data; for one more decimal place, a hundred times. Every survey, every A/B test and every physics experiment is priced by this.

> [!TIP]
> **Predict before section 4.** You build a $95\%$ confidence interval from each of $10{,}000$ samples drawn from a population whose true mean you know. What fraction of those intervals should contain the true mean — and what happens to that fraction if you use $z = 1.96$ when the population $\sigma$ is unknown and $n$ is small? Decide before opening the answers.

## 4. Confidence intervals

For a mean, with known $\sigma$:

$$
\bar{x} \pm z^{*}\frac{\sigma}{\sqrt{n}}
$$

with $z^{*} = 1.96$ for $95\%$. When $\sigma$ is unknown — nearly always — you use $s$ and the **$t$-distribution**, whose critical values exceed $z$ for small $n$, widening the interval to pay for the extra uncertainty in estimating $\sigma$.

### What the 95% means

**It is a property of the procedure, not of any one interval.**

The correct statement: *if you repeat the whole process many times, about $95\%$ of the intervals produced will contain the true parameter.*

The incorrect statement: *there is a $95\%$ probability that the true value lies inside this particular interval.* Once computed, the interval either contains $\mu$ or it does not — there is no probability left, because $\mu$ is not random.

That distinction sounds pedantic and is not. It is why block 3 of the lab does the only honest check available: build ten thousand intervals from a known population and **count how many contain the truth**. If the procedure is right, that count lands on $95\%$.

## 5. Hypothesis testing

1. State $H_0$ (no effect) and $H_1$.
2. Choose $\alpha$, the false-positive rate you will tolerate — conventionally $0.05$.
3. Compute a test statistic and its $p$-value.
4. If $p < \alpha$, reject $H_0$; otherwise fail to reject.

**What a $p$-value is:** the probability of data *at least this extreme* **if $H_0$ were true**.

**What it is not:**

- the probability that $H_0$ is true — that is $P(H_0\mid\text{data})$, requires a prior, and needs [[03-probability/01-probability|Bayes]];
- the probability the result was a fluke;
- a measure of effect **size** — with a large enough $n$, a trivial difference gets a tiny $p$.

| | $H_0$ true | $H_0$ false |
| :--- | :--- | :--- |
| **Reject** | Type I error (rate $\alpha$) | Correct |
| **Fail to reject** | Correct | Type II error (rate $\beta$) |

**Power** is $1-\beta$: the chance of detecting a real effect. Lowering $\alpha$ reduces false positives and raises $\beta$ — you cannot reduce both without more data.

**The multiple-comparisons problem** follows directly. Test twenty independent true nulls at $\alpha = 0.05$ and the chance of at least one false positive is $1 - 0.95^{20} \approx 64\%$. This is the same complement calculation from probability, and it is why running many tests and reporting the significant one is not a valid procedure.

## Worked example — runnable

**Runnable example:** save as `inference.py` in any empty directory and run `python3 inference.py`. Standard library only; writes no files.

```python
"""The CLT, confidence-interval coverage, and what a p-value is not."""
import math
import random

Z95 = 1.959964


def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs, ddof=1):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - ddof))


def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def histogram(values, bins=21, width=46):
    lo, hi = min(values), max(values)
    counts = [0] * bins
    for v in values:
        idx = min(bins - 1, int((v - lo) / (hi - lo) * bins))
        counts[idx] += 1
    peak = max(counts)
    rows = []
    for i, c in enumerate(counts):
        edge = lo + (i + 0.5) * (hi - lo) / bins
        rows.append(f"   {edge:8.3f} | {'#' * int(width * c / peak)}")
    return rows


def ci_for_mean(sample, z=Z95):
    m, s, n = mean(sample), stdev(sample), len(sample)
    half = z * s / math.sqrt(n)
    return m - half, m + half


if __name__ == "__main__":
    rng = random.Random(20260910)

    print("Block 1 - the CLT starting from distributions that are not remotely normal")
    populations = {
        "exponential (very skewed)": lambda: rng.expovariate(1.0),
        "bimodal (two spikes)":      lambda: rng.gauss(0, 0.4) + (5 if rng.random() < 0.5 else -5),
        "uniform (flat)":            lambda: rng.uniform(0, 1),
    }
    for name, draw in populations.items():
        raw = [draw() for _ in range(4000)]
        print(f"\n  {name}: the RAW data")
        for row in histogram(raw, bins=13, width=40):
            print(row)
        for n in (30,):
            means = [mean([draw() for _ in range(n)]) for _ in range(4000)]
            print(f"  the same population, means of samples of {n}")
            for row in histogram(means, bins=13, width=40):
                print(row)

    print()
    print("Block 2 - the standard error really is sigma/sqrt(n)")
    SIGMA = 1.0
    print("       n    observed sd of the mean    sigma/sqrt(n)   ratio")
    for n in (1, 4, 16, 64, 256):
        means = [mean([rng.gauss(0, SIGMA) for _ in range(n)]) for _ in range(20000)]
        obs = stdev(means)
        pred = SIGMA / math.sqrt(n)
        print(f"  {n:6}    {obs:22.5f}    {pred:13.5f}   {obs/pred:.4f}")
        assert abs(obs / pred - 1) < 0.05
    print("  quadruple n, halve the error: that is the price of every extra digit")

    print()
    print("Block 3 - do 95% confidence intervals actually contain the truth 95% of the time?")
    TRUE_MU, TRUE_SD = 50.0, 12.0
    for n in (5, 15, 30, 100):
        hits = 0
        TRIALS = 10000
        for _ in range(TRIALS):
            sample = [rng.gauss(TRUE_MU, TRUE_SD) for _ in range(n)]
            lo, hi = ci_for_mean(sample)
            hits += lo <= TRUE_MU <= hi
        print(f"  n={n:4}: {hits/TRIALS:.4f} of {TRIALS:,} intervals contained the true mean")
    # with n=100 the z-interval is essentially correct
    hits = 0
    for _ in range(10000):
        sample = [rng.gauss(TRUE_MU, TRUE_SD) for _ in range(100)]
        lo, hi = ci_for_mean(sample)
        hits += lo <= TRUE_MU <= hi
    assert 0.94 < hits / 10000 < 0.96, hits / 10000
    print("  coverage climbs towards 95% as n grows, but even at n=100 it is a")
    print("  little under - using z with an ESTIMATED sigma is anti-conservative.")
    print("  at n=5 it is visibly SHORT of 95% - because using z with an estimated")
    print("  sigma ignores the extra uncertainty. That is what the t-distribution fixes.")

    print()
    print("Block 4 - a p-value is not the probability the null is true")
    # Two groups drawn from the SAME distribution: the null is true by construction.
    def two_sample_z(a, b):
        diff = mean(a) - mean(b)
        se = math.sqrt(stdev(a) ** 2 / len(a) + stdev(b) ** 2 / len(b))
        z = diff / se
        return 2 * (1 - normal_cdf(abs(z)))

    TRIALS = 20000
    ps = []
    for _ in range(TRIALS):
        a = [rng.gauss(0, 1) for _ in range(40)]
        b = [rng.gauss(0, 1) for _ in range(40)]
        ps.append(two_sample_z(a, b))
    below = sum(1 for p in ps if p < 0.05)
    print(f"  {TRIALS:,} experiments where the null is TRUE by construction")
    print(f"    significant at p < 0.05: {below} ({below/TRIALS:.4f})")
    assert 0.04 < below / TRIALS < 0.06
    print("  a little ABOVE the 5% you chose: the two-sample z-test with estimated")
    print("  variances at n=40 is mildly anti-conservative, for the same reason.")
    print("  under the null, p-values are UNIFORM. Deciles of the observed p-values:")
    ps.sort()
    for d in range(1, 10):
        print(f"    {10*d:3}th percentile: {ps[int(len(ps)*d/10)]:.4f}")

    print()
    print("Block 5 - multiple comparisons")
    print("   tests   P(at least one false positive at alpha=0.05)")
    for k in (1, 5, 10, 20, 100):
        print(f"  {k:6}   {1 - 0.95 ** k:.4f}")
    assert abs((1 - 0.95 ** 20) - 0.6415) < 0.001
    rng2 = random.Random(555)
    caught = 0
    for _ in range(5000):
        pvals = [two_sample_z([rng2.gauss(0, 1) for _ in range(40)],
                              [rng2.gauss(0, 1) for _ in range(40)]) for _ in range(20)]
        caught += any(p < 0.05 for p in pvals)
    print(f"  simulated, 20 tests per experiment: {caught/5000:.4f} had at least one 'hit'")
    assert abs(caught / 5000 - 0.64) < 0.03
    print("  running 20 tests and reporting the significant one is not a procedure,")
    print("  it is a 64% chance of finding nothing at all")

    print()
    print("inference: passed")
```

Expected output:

```
Block 1 - the CLT starting from distributions that are not remotely normal

  exponential (very skewed): the RAW data
      0.294 | ########################################
      0.880 | ######################
      1.466 | ############
      2.052 | ######
      2.638 | ###
      3.225 | #
      3.811 | #
      4.397 | 
      4.983 | 
      5.569 | 
      6.156 | 
      6.742 | 
      7.328 | 
  the same population, means of samples of 30
      0.513 | 
      0.613 | ###
      0.714 | #############
      0.814 | ##########################
      0.914 | ########################################
      1.015 | #######################################
      1.115 | ##############################
      1.215 | #################
      1.316 | ########
      1.416 | ####
      1.516 | #
      1.617 | 
      1.717 | 

  bimodal (two spikes): the RAW data
     -5.970 | #####
     -4.980 | ########################################
     -3.990 | #####
     -3.000 | 
     -2.010 | 
     -1.020 | 
     -0.030 | 
      0.960 | 
      1.950 | 
      2.940 | 
      3.930 | ####
      4.920 | #######################################
      5.909 | #######
  the same population, means of samples of 30
     -2.978 | 
     -2.498 | #
     -2.018 | ##
     -1.538 | ###########
     -1.058 | ##################
     -0.578 | ###############################
     -0.098 | ########################################
      0.382 | ###############################
      0.862 | ##############################
      1.342 | ##########
      1.822 | #####
      2.302 | #
      2.782 | 

  uniform (flat): the RAW data
      0.038 | ######################################
      0.115 | #####################################
      0.192 | ######################################
      0.269 | ####################################
      0.346 | #####################################
      0.423 | #####################################
      0.500 | #####################################
      0.577 | #######################################
      0.654 | #################################
      0.731 | ########################################
      0.808 | ####################################
      0.885 | ###################################
      0.961 | #####################################
  the same population, means of samples of 30
      0.336 | 
      0.364 | #
      0.392 | #####
      0.420 | #############
      0.447 | ##########################
      0.475 | ########################################
      0.503 | #######################################
      0.531 | ###################################
      0.559 | #######################
      0.587 | ############
      0.615 | #####
      0.642 | 
      0.670 | 

Block 2 - the standard error really is sigma/sqrt(n)
       n    observed sd of the mean    sigma/sqrt(n)   ratio
       1                   1.00899          1.00000   1.0090
       4                   0.49826          0.50000   0.9965
      16                   0.24914          0.25000   0.9966
      64                   0.12473          0.12500   0.9979
     256                   0.06231          0.06250   0.9969
  quadruple n, halve the error: that is the price of every extra digit

Block 3 - do 95% confidence intervals actually contain the truth 95% of the time?
  n=   5: 0.8772 of 10,000 intervals contained the true mean
  n=  15: 0.9258 of 10,000 intervals contained the true mean
  n=  30: 0.9422 of 10,000 intervals contained the true mean
  n= 100: 0.9453 of 10,000 intervals contained the true mean
  coverage climbs towards 95% as n grows, but even at n=100 it is a
  little under - using z with an ESTIMATED sigma is anti-conservative.
  at n=5 it is visibly SHORT of 95% - because using z with an estimated
  sigma ignores the extra uncertainty. That is what the t-distribution fixes.

Block 4 - a p-value is not the probability the null is true
  20,000 experiments where the null is TRUE by construction
    significant at p < 0.05: 1114 (0.0557)
  a little ABOVE the 5% you chose: the two-sample z-test with estimated
  variances at n=40 is mildly anti-conservative, for the same reason.
  under the null, p-values are UNIFORM. Deciles of the observed p-values:
     10th percentile: 0.0956
     20th percentile: 0.1924
     30th percentile: 0.2938
     40th percentile: 0.4008
     50th percentile: 0.5023
     60th percentile: 0.6024
     70th percentile: 0.7021
     80th percentile: 0.8020
     90th percentile: 0.8994

Block 5 - multiple comparisons
   tests   P(at least one false positive at alpha=0.05)
       1   0.0500
       5   0.2262
      10   0.4013
      20   0.6415
     100   0.9941
  simulated, 20 tests per experiment: 0.6646 had at least one 'hit'
  running 20 tests and reporting the significant one is not a procedure,
  it is a 64% chance of finding nothing at all

inference: passed
```

Block 3 is the honest check nobody usually performs, and the result is more interesting than a clean pass. At $n = 5$ the intervals contain the true mean only **87.7%** of the time — nowhere near the advertised $95\%$. Coverage climbs with $n$, but even at $n = 100$ it reaches $94.5\%$, still a little short. Using $z$ with a $\sigma$ estimated from the same sample ignores the uncertainty in that estimate, and the intervals come out too narrow. That is exactly the gap the $t$-distribution closes, and the practice task asks you to measure the repair.

## Common pitfalls and traps

- **"There is a 95% chance $\mu$ is in this interval."** Wrong. $\mu$ is fixed; the interval is random. The $95\%$ describes the long-run hit rate of the *procedure*.
- **Reading a $p$-value as $P(H_0)$.** It is the reverse conditional. Getting this backwards is the base rate fallacy again, in new clothing.
- **"$p > 0.05$, so there is no effect."** Failing to reject is not evidence of absence — it may just be low power. Report the confidence interval, which shows what effect sizes remain plausible.
- **Confusing significance with importance.** With $n = 10^6$, a difference of $0.001\%$ can be highly significant and completely irrelevant.
- **Applying the CLT to individual observations.** It is about the sampling distribution of the *mean*. Raw data does not become normal.
- **Assuming the CLT always applies.** It needs finite variance. For heavy-tailed data — power laws — sample means may not converge usefully at any $n$.
- **Running many tests and reporting the winner.** Block 5 quantifies it: twenty tests give a $64\%$ chance of at least one false positive.

## Check your understanding

1. A sample of $64$ has mean $70$ and the population sd is known to be $16$. Give a $95\%$ confidence interval for $\mu$.
2. To halve the width of that interval, what sample size do you need?
3. A study reports $p = 0.03$. What exactly does that number say?
4. Why does failing to reject $H_0$ not prove $H_0$?
5. Why does the CLT let you use normal-based methods on decidedly non-normal data?

<details><summary>Answers — open only after an attempt</summary>

1. Standard error $= 16/\sqrt{64} = 2$. Interval $= 70 \pm 1.96(2) = 70 \pm 3.92$, so $(66.08,\ 73.92)$.
2. Width scales as $1/\sqrt{n}$, so halving it needs **four times** the data: $n = 256$.
3. If the null hypothesis were true, the probability of observing data at least this extreme is $0.03$. It says nothing directly about whether the null *is* true, and nothing about the size of the effect.
4. Because absence of evidence is not evidence of absence. A small sample has low power and may fail to detect a real effect. The confidence interval is more informative: it shows which effect sizes are still consistent with the data.
5. Because the methods apply to the **sampling distribution of the mean**, not to the raw data — and the CLT says that distribution tends to normal regardless of the population's shape, provided the variance is finite and $n$ is reasonably large.

**And the prediction from section 3:** about **95%** should contain the true mean — and the lab confirms it at $n = 100$. At small $n$ with $\sigma$ estimated from the sample, using $z = 1.96$ **under-covers**: the intervals are too narrow because they ignore the uncertainty in $s$ itself. The $t$-distribution's wider critical values are the fix.
</details>

## Practice — independent task

Implement `t_interval(sample, confidence)` using the $t$-distribution, and show it fixes the under-coverage block 3 exposes.

1. Implement or approximate the $t$ critical value for $n-1$ degrees of freedom. You may compute it by numerically inverting the $t$ CDF; say which method you used and how you validated it (the $t$ value for large $df$ must approach $z$).
2. Re-run block 3's coverage experiment with your $t$ intervals at $n = 5, 10, 15, 30, 100$, and tabulate coverage for both $z$ and $t$ side by side.
3. **Assert that $t$ achieves close to nominal coverage at every $n$**, while $z$ does not at small $n$. State the smallest $n$ at which the difference stops mattering, from your own numbers.
4. Report the average interval **width** for both. The $t$ interval is wider — quantify by how much at each $n$, and explain what you are buying with that width.
5. Then break it: run the same coverage experiment sampling from a **heavily skewed** population (exponential) at $n = 5$ and $n = 100$. Report coverage. Explain which assumption failed and why larger $n$ helps.

**Edge cases:** $n = 1$ (no variance estimate — what should the function do?); a sample with zero variance; confidence levels of $0$ and $1$.

**Done when:** your $t$ coverage lands within simulation error of nominal at every $n$, your width table shows the price paid, and your step-5 result is explained by the CLT rather than described.

## Tradeoffs, limits and extensions

**Frequentist and Bayesian answer different questions.** A confidence interval is a statement about the procedure's long-run behaviour. A Bayesian **credible** interval genuinely does say "there is a $95\%$ probability the parameter lies here" — but only relative to a stated prior. Neither is free: one requires care in interpretation, the other requires justifying a prior.

**The replication crisis is largely this lesson.** $p < 0.05$ as a publication threshold, combined with many tested hypotheses and selective reporting, guarantees a literature full of false positives. Pre-registration, effect sizes with intervals, and correction for multiple comparisons are the structural fixes.

**Assumptions do fail.** The CLT needs finite variance; heavy-tailed data violates it. Standard tests assume independent observations; time series and clustered data violate that badly, and the resulting intervals can be far too narrow. Checking assumptions is not a formality that precedes the real work — it *is* the work.

## Before moving on

You are done with this lesson when you can:

- State the CLT precisely, including what it does not say.
- Derive $\sigma/\sqrt{n}$ from variance addition, and say what it costs to double precision.
- State what $95\%$ confidence means as a property of the procedure.
- Interpret a $p$-value correctly and explain the multiple-comparisons problem.

**Recap for later lookup:** parameters are fixed and unknown, statistics are known and random; CLT — sample means tend to $N(\mu, \sigma^2/n)$ for **any** finite-variance population; standard error $\sigma/\sqrt{n}$, so precision costs quadratically; a $95\%$ CI is $\bar{x} \pm z^*\frac{s}{\sqrt{n}}$, or $t^*$ when $\sigma$ is estimated, and the $95\%$ is the procedure's hit rate; $p = P(\text{data this extreme}\mid H_0)$, never $P(H_0\mid\text{data})$; Type I rate $\alpha$, Type II rate $\beta$, power $1-\beta$; $k$ independent tests give $1-(1-\alpha)^k$ chance of a false positive.

**Next:** [[06-stochastic-processes/01-markov-chains|Stochastic Processes]] — probability that evolves over time.

## Related

- [[04-random-variables-and-distributions/01-distributions|Distributions]] — the normal the CLT delivers
- [[03-probability/01-probability|Probability]] — Bayes, and the conditional that $p$-values reverse
- [[06-eigenvalues/01-eigenvalues-and-eigenvectors|Eigenvalues]] — the steady state the next lesson needs
