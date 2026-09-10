# Random Variables and Distributions

**[Intermediate]** — attaching numbers to outcomes, and the handful of distributions that describe most of what you will meet.

## Before you start

- You know the probability rules and conditional probability — [[03-probability/01-probability|probability]].
- You can compute a mean and a variance — [[02-dispersion-and-cumulative-frequency/01-dispersion|dispersion]].
- Helpful: the binomial coefficient — [[02-discrete-math/06-combinatorics-and-counting|combinatorics]].

**What you will be able to do after this lesson:**

1. Distinguish **discrete** from **continuous** random variables, and say why a continuous variable has zero probability at every single point.
2. Compute **expectation** and **variance** from a distribution, and use the linearity of expectation.
3. Recognise when a situation is **Bernoulli, binomial, Poisson, geometric** or **normal**, and state the assumptions each one needs.
4. Explain the $68$–$95$–$99.7$ rule and use standardisation ($z$-scores).

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 shows one distribution turning into another.

---

## 1. Why this exists

Probability so far has been about events — "it rained", "the test was positive". Most questions are about **quantities**: how many defects, how long until failure, how much traffic.

A **random variable** attaches a number to each outcome, which lets you do arithmetic: add them, average them, ask what happens in the long run. And once you have numbers, a small number of shapes turn out to describe an enormous amount of reality — not by coincidence, but because each shape follows from a specific mechanism. Knowing the mechanism tells you which distribution applies, and, more importantly, when none of them does.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Random variable** | A function from outcomes to numbers | Written $X$; a *function*, not a variable |
| **Discrete** | Takes countable values | Counts: $0, 1, 2, \dots$ |
| **Continuous** | Takes any value in a range | Measurements: time, length |
| **PMF** $P(X=x)$ | Probability mass function — discrete | Sums to $1$ |
| **PDF** $f(x)$ | Probability **density** function — continuous | **Integrates** to $1$ |
| **CDF** $F(x) = P(X \le x)$ | Cumulative distribution function | Non-decreasing, $0 \to 1$ |
| **Expectation** $E[X]$ | The long-run average | Also written $\mu$ |
| **Variance** $\operatorname{Var}(X)$ | $E[(X-\mu)^2]$ | Spread, in squared units |
| **i.i.d.** | Independent and identically distributed | The assumption most results need |

**Density is not probability.** For a continuous variable, $P(X = 3.7)$ is exactly $0$ — there are infinitely many values and no single one carries positive mass. Only *intervals* have probability, given by the area under the curve. A density can exceed $1$; a probability cannot.

## 3. Expectation and variance

$$
E[X] = \sum_x x\,P(X=x) \qquad\text{or}\qquad \int x f(x)\,dx
$$

$$
\operatorname{Var}(X) = E[(X-\mu)^2] = E[X^2] - (E[X])^2
$$

That second form is usually the easier one to compute, and the identity is worth remembering.

**Linearity of expectation** is the most useful fact here:

$$
E[X + Y] = E[X] + E[Y]
$$

**for any $X$ and $Y$, independent or not.** This is unusual and extremely powerful — it lets you break a complicated quantity into simple pieces without worrying about how they interact.

Variance is **not** linear in general. It adds only when the variables are independent:

$$
\operatorname{Var}(X+Y) = \operatorname{Var}(X) + \operatorname{Var}(Y) \quad\text{if independent}
$$

That single condition is what makes the $\sqrt{n}$ appear everywhere in statistics.

## 4. The distributions worth knowing

| Distribution | The mechanism | $E[X]$ | $\operatorname{Var}(X)$ |
| :--- | :--- | :--- | :--- |
| **Bernoulli**$(p)$ | One trial, success or failure | $p$ | $p(1-p)$ |
| **Binomial**$(n,p)$ | $n$ **independent** trials, count the successes | $np$ | $np(1-p)$ |
| **Geometric**$(p)$ | Trials until the first success | $1/p$ | $(1-p)/p^2$ |
| **Poisson**$(\lambda)$ | Events at a constant average rate, independently | $\lambda$ | $\lambda$ |
| **Normal**$(\mu,\sigma^2)$ | A sum of many small independent effects | $\mu$ | $\sigma^2$ |

**Binomial:** $P(X=k) = \binom{n}{k}p^k(1-p)^{n-k}$. The assumptions are fixed $n$, constant $p$, and independence. Sampling *without* replacement breaks the third — that is the hypergeometric distribution, though for a small sample from a large population the difference is negligible.

**Poisson:** $P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$. Note $E[X] = \operatorname{Var}(X) = \lambda$ — a genuinely useful diagnostic. If your count data has variance much larger than its mean it is *overdispersed*, and Poisson is the wrong model.

**Normal:** the bell curve, and the reason it appears so often is not that nature likes bells. It is the [[05-inference-and-estimation/01-inference|Central Limit Theorem]]: anything that is a sum of many small independent contributions tends towards it, whatever the pieces look like.

**The $68$–$95$–$99.7$ rule:** about $68\%$ of a normal distribution lies within one standard deviation of the mean, $95\%$ within two, $99.7\%$ within three. Standardising with

$$
z = \frac{x - \mu}{\sigma}
$$

converts any normal to the standard one, which is why a single table ever sufficed.

> [!TIP]
> **Predict before running the lab.** A binomial with $n = 1000$ trials and $p = 0.003$ has mean $np = 3$. A Poisson with $\lambda = 3$ has the same mean. How close are the two distributions — same to one decimal place, two, three? And what is it about $n$ and $p$ that makes them close? Decide before opening the answers.

## 5. Poisson as a limit of binomial

Poisson is what binomial becomes when trials are many and success is rare, with $np$ held fixed at $\lambda$.

The mechanism makes this obvious. A binomial counts successes in $n$ fixed slots. Let the slots become finer and more numerous — seconds, then milliseconds — while the expected total stays the same. In the limit there are no slots left, just a **rate**, and that is Poisson.

This is why Poisson describes arrivals: requests hitting a server, calls reaching an exchange, decays in a sample. There is no natural $n$; there is a rate and a window.

The variance check comes along too: $\operatorname{Var} = np(1-p) \to np = \lambda$ as $p \to 0$, which is exactly the Poisson property that mean equals variance.

## Worked example — runnable

**Runnable example:** save as `distributions.py` in any empty directory and run `python3 distributions.py`. Standard library only; writes no files.

```python
"""Random variables: expectation, variance, and the standard distributions."""
import math
import random
from collections import Counter

TRIALS = 200000


def expectation(pmf):
    return sum(x * p for x, p in pmf.items())


def variance_of(pmf):
    mu = expectation(pmf)
    return sum(p * (x - mu) ** 2 for x, p in pmf.items())


def binomial_pmf(n, p, kmax=None):
    """kmax bounds the range: comb(100000, 50000) overflows a float, and for a
    large-n small-p comparison only the small k matter anyway."""
    top = n if kmax is None else min(n, kmax)
    return {k: math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(top + 1)}


def poisson_pmf(lam, kmax):
    return {k: lam ** k * math.exp(-lam) / math.factorial(k) for k in range(kmax + 1)}


def geometric_pmf(p, kmax):
    return {k: (1 - p) ** (k - 1) * p for k in range(1, kmax + 1)}


def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def bar(p, scale=280):
    return "#" * int(round(p * scale))


if __name__ == "__main__":
    print("Block 1 - a die as a random variable")
    die = {k: 1 / 6 for k in range(1, 7)}
    mu, var = expectation(die), variance_of(die)
    print(f"  E[X] = {mu:.4f}   Var(X) = {var:.4f}   sd = {math.sqrt(var):.4f}")
    assert abs(mu - 3.5) < 1e-9
    # E[X^2] - (E[X])^2 must agree with the definition
    ex2 = sum(p * x * x for x, p in die.items())
    print(f"  E[X^2] - (E[X])^2 = {ex2:.4f} - {mu**2:.4f} = {ex2 - mu**2:.4f}")
    assert abs((ex2 - mu ** 2) - var) < 1e-9
    print("  note E[X] = 3.5, a value the die can never show")

    print()
    print("Block 2 - linearity of expectation holds even when NOT independent")
    rng = random.Random(20260910)
    # X = first die, Y = X itself (maximally dependent). E[X+Y] must still be E[X]+E[Y].
    tot = 0
    for _ in range(TRIALS):
        x = rng.randint(1, 6)
        tot += x + x
    print(f"  E[X + X] simulated = {tot/TRIALS:.4f}, and E[X] + E[X] = {2*mu:.4f}")
    assert abs(tot / TRIALS - 2 * mu) < 0.02
    print("  variance is NOT linear the same way:")
    print(f"    Var(X + X) = Var(2X) = 4Var(X) = {4*var:.4f}, not 2Var(X) = {2*var:.4f}")

    print()
    print("Block 3 - binomial: assumptions, mean and variance")
    n, p = 20, 0.3
    pmf = binomial_pmf(n, p)
    print(f"  Binomial(n={n}, p={p}):  sum of pmf = {sum(pmf.values()):.12f}")
    print(f"    E[X] = {expectation(pmf):.4f}  (np = {n*p})")
    print(f"    Var  = {variance_of(pmf):.4f}  (np(1-p) = {n*p*(1-p)})")
    assert abs(expectation(pmf) - n * p) < 1e-9
    assert abs(variance_of(pmf) - n * p * (1 - p)) < 1e-9
    for k in range(0, 13, 2):
        print(f"    P(X={k:2}) = {pmf[k]:.5f}  {bar(pmf[k])}")

    print()
    print("Block 4 - Poisson is the limit of binomial when n is large and p small")
    LAM = 3.0
    pois = poisson_pmf(LAM, 12)
    print(f"     n        max |binomial(n, 3/n) - Poisson(3)| over k=0..12")
    prev = None
    for n_i in (10, 100, 1000, 10000, 100000):
        b = binomial_pmf(n_i, LAM / n_i, kmax=12)
        gap = max(abs(b.get(k, 0.0) - pois[k]) for k in range(13))
        arrow = "" if prev is None else f"   ({prev/gap:.1f}x closer)"
        print(f"  {n_i:7}        {gap:.8f}{arrow}")
        prev = gap
    b1000 = binomial_pmf(1000, 0.003, kmax=12)
    assert max(abs(b1000.get(k, 0.0) - pois[k]) for k in range(13)) < 0.001
    print("  side by side at n=1000, p=0.003:")
    print("     k   binomial    Poisson")
    for k in range(7):
        print(f"    {k:2}   {b1000[k]:.6f}   {pois[k]:.6f}")
    # the moments need the tail, so compute them on a wider range than the table
    pois_full = poisson_pmf(LAM, 60)
    print(f"  Poisson has mean = variance = {LAM}: "
          f"E={expectation(pois_full):.6f}, Var={variance_of(pois_full):.6f}")
    assert abs(expectation(pois_full) - LAM) < 1e-9
    assert abs(variance_of(pois_full) - LAM) < 1e-9
    print(f"  (truncating at k=12 loses {1 - sum(pois.values()):.2e} of the mass,")
    print(f"   which is why the moments are computed over k=0..60 instead)")

    print()
    print("Block 5 - geometric: waiting for the first success")
    p_succ = 1 / 6
    geo = geometric_pmf(p_succ, 200)
    print(f"  rolling until the first 6:  E[X] = {expectation(geo):.4f}  (1/p = {1/p_succ:.4f})")
    assert abs(expectation(geo) - 1 / p_succ) < 0.01
    rng = random.Random(777)
    total = 0
    for _ in range(50000):
        c = 1
        while rng.randint(1, 6) != 6:
            c += 1
        total += c
    print(f"  simulated over 50,000 runs: {total/50000:.4f}")
    assert abs(total / 50000 - 6) < 0.15

    print()
    print("Block 6 - the normal distribution and the 68-95-99.7 rule")
    for k in (1, 2, 3):
        inside = normal_cdf(k) - normal_cdf(-k)
        print(f"  within {k} sd of the mean: {inside:.6f}  ({100*inside:.2f}%)")
    assert abs((normal_cdf(1) - normal_cdf(-1)) - 0.6827) < 0.001
    assert abs((normal_cdf(2) - normal_cdf(-2)) - 0.9545) < 0.001
    assert abs((normal_cdf(3) - normal_cdf(-3)) - 0.9973) < 0.001
    print("  standardising: exam mean 62, sd 11. A mark of 80 is")
    z = (80 - 62) / 11
    print(f"    z = (80 - 62)/11 = {z:.4f}, so better than {100*normal_cdf(z):.2f}% of candidates")
    print("  a continuous variable has ZERO probability at any single point:")
    print(f"    P(X = 80) = 0 exactly;  P(79.5 < X < 80.5) = "
          f"{normal_cdf(80.5,62,11) - normal_cdf(79.5,62,11):.6f}")

    print()
    print("distributions: passed")
```

Expected output:

```
Block 1 - a die as a random variable
  E[X] = 3.5000   Var(X) = 2.9167   sd = 1.7078
  E[X^2] - (E[X])^2 = 15.1667 - 12.2500 = 2.9167
  note E[X] = 3.5, a value the die can never show

Block 2 - linearity of expectation holds even when NOT independent
  E[X + X] simulated = 6.9997, and E[X] + E[X] = 7.0000
  variance is NOT linear the same way:
    Var(X + X) = Var(2X) = 4Var(X) = 11.6667, not 2Var(X) = 5.8333

Block 3 - binomial: assumptions, mean and variance
  Binomial(n=20, p=0.3):  sum of pmf = 1.000000000000
    E[X] = 6.0000  (np = 6.0)
    Var  = 4.2000  (np(1-p) = 4.199999999999999)
    P(X= 0) = 0.00080  
    P(X= 2) = 0.02785  ########
    P(X= 4) = 0.13042  #####################################
    P(X= 6) = 0.19164  ######################################################
    P(X= 8) = 0.11440  ################################
    P(X=10) = 0.03082  #########
    P(X=12) = 0.00386  #

Block 4 - Poisson is the limit of binomial when n is large and p small
     n        max |binomial(n, 3/n) - Poisson(3)| over k=0..12
       10        0.04278612
      100        0.00343232   (12.5x closer)
     1000        0.00033676   (10.2x closer)
    10000        0.00003361   (10.0x closer)
   100000        0.00000336   (10.0x closer)
  side by side at n=1000, p=0.003:
     k   binomial    Poisson
     0   0.049563   0.049787
     1   0.149137   0.149361
     2   0.224154   0.224042
     3   0.224379   0.224042
     4   0.168284   0.168031
     5   0.100869   0.100819
     6   0.050333   0.050409
  Poisson has mean = variance = 3.0: E=3.000000, Var=3.000000
  (truncating at k=12 loses 1.61e-05 of the mass,
   which is why the moments are computed over k=0..60 instead)

Block 5 - geometric: waiting for the first success
  rolling until the first 6:  E[X] = 6.0000  (1/p = 6.0000)
  simulated over 50,000 runs: 6.0150

Block 6 - the normal distribution and the 68-95-99.7 rule
  within 1 sd of the mean: 0.682689  (68.27%)
  within 2 sd of the mean: 0.954500  (95.45%)
  within 3 sd of the mean: 0.997300  (99.73%)
  standardising: exam mean 62, sd 11. A mark of 80 is
    z = (80 - 62)/11 = 1.6364, so better than 94.91% of candidates
  a continuous variable has ZERO probability at any single point:
    P(X = 80) = 0 exactly;  P(79.5 < X < 80.5) = 0.009513

distributions: passed
```

Block 4 is the one to study. As $n$ grows with $np$ held at $3$, the binomial converges on the Poisson, and the largest gap falls by a factor of ten for every tenfold increase in $n$ — reaching $3.4\times10^{-4}$ at $n=1000$ and $3.4\times10^{-6}$ at $n=100{,}000$. The Poisson is not a separate invention; it is what binomial *becomes*.

## Common pitfalls and traps

- **Treating a density as a probability.** $f(x)$ can exceed $1$. Only areas are probabilities, and $P(X = c) = 0$ for any single $c$.
- **Using binomial when trials are not independent.** Sampling without replacement from a small population is hypergeometric. Independence is an assumption to check, not a formality.
- **Using Poisson on overdispersed counts.** If the sample variance is much larger than the mean, the constant-rate assumption has failed. The negative binomial is the usual repair.
- **Assuming variance adds without independence.** $\operatorname{Var}(X+Y) = \operatorname{Var}(X)+\operatorname{Var}(Y)$ needs independence; **expectation never does**.
- **Assuming normality because the data is "natural".** Incomes, file sizes, city populations and word frequencies are all heavy-tailed. The $68$–$95$–$99.7$ rule applied to them is badly wrong in the tail — precisely where it matters.
- **Forgetting $E[X]$ can be impossible.** The mean roll of a die is $3.5$. An expectation is a long-run average, not a prediction of any single outcome.

## Check your understanding

1. A fair coin is flipped $10$ times. Find $E[\text{heads}]$ and $\operatorname{Var}(\text{heads})$.
2. Why is $P(X = 5)$ zero for a continuous random variable?
3. Calls arrive at $4$ per hour on average. What is $P(\text{exactly } 2 \text{ in an hour})$?
4. A distribution has mean $10$ and variance $40$. Is Poisson plausible?
5. Heights are normal with mean $170$ cm and sd $8$ cm. What proportion are between $162$ and $186$ cm?

<details><summary>Answers — open only after an attempt</summary>

1. Binomial with $n=10$, $p=0.5$: $E = np = 5$, $\operatorname{Var} = np(1-p) = 10(0.5)(0.5) = 2.5$.
2. Because there are uncountably many possible values, and assigning positive probability to each would make the total infinite. Probability lives in *areas* under the density, and a single point has zero width.
3. Poisson with $\lambda = 4$: $P(X=2) = \frac{4^2 e^{-4}}{2!} = \frac{16 e^{-4}}{2} = 8e^{-4} \approx 0.1465$.
4. **No.** Poisson requires mean $=$ variance. Here the variance is four times the mean — the data is overdispersed, so the constant-rate assumption fails. Consider a negative binomial.
5. $162$ is $z = -1$ and $186$ is $z = +2$. So the proportion is $P(-1 < Z < 2) \approx 0.8413 - 0.1587 = 0.6826$... more precisely $0.9772 - 0.1587 = 0.8185$, about $82\%$.

**And the prediction from section 4:** at $n = 1000$, $p = 0.003$ the largest discrepancy is about $3.4\times10^{-4}$ — agreement to **three decimal places**. What makes them close is $n$ large *and* $p$ small with $np$ fixed, and the lab shows the gap shrinking by a factor of ten for each tenfold increase in $n$.
</details>

## Practice — independent task

Implement `fit_and_check(counts)`: given observed count data, fit both a Poisson and a binomial, and decide which — if either — is defensible.

1. Compute the sample mean and variance. Report the **index of dispersion**, $\text{variance}/\text{mean}$: near $1$ suggests Poisson, well above $1$ means overdispersed, well below means underdispersed.
2. Fit Poisson by setting $\lambda = \bar{x}$, and produce the expected frequency of each count.
3. Compare observed and expected with a chi-square statistic, $\sum \frac{(O-E)^2}{E}$. Pool any categories with expected count below $5$ and say why that pooling is necessary.
4. Test on data you generate yourself: genuinely Poisson data (via `random.poisson`-equivalent — write your own by summing exponential waits, or by the inverse-CDF method), and deliberately overdispersed data (a Poisson whose $\lambda$ itself varies randomly).
5. **The point of step 4:** show your dispersion index correctly separates the two, and state the smallest sample size at which it reliably does so, based on your own runs.

**Edge cases:** all counts identical (variance zero); a single observation; counts including large values where `math.factorial` gets slow — use a recurrence for the Poisson PMF instead.

**Done when:** your index of dispersion cleanly separates the two generated datasets, your chi-square pooling rule is implemented and explained, and you can say what "the model fits" does and does not establish.

## Tradeoffs, limits and extensions

**These five are a starting kit, not a complete set.** Real data is frequently heavy-tailed — file sizes, incomes, city sizes and network degrees follow power laws, where the variance may be infinite and the sample mean does not converge usefully. Applying normal reasoning there is not slightly wrong, it is meaningless.

**The distributions come from mechanisms.** Binomial from fixed independent trials; Poisson from a constant rate; normal from summing many small effects; geometric from waiting. Choosing a distribution by which curve the histogram resembles is backwards — choose by which mechanism the data-generating process actually has, then check the fit.

**The normal's dominance is a theorem, not an aesthetic.** The Central Limit Theorem explains why sums and averages tend to normality regardless of the underlying shape, which is why it governs measurement error and sample means. It says nothing about individual raw measurements, which is where it is most often misapplied — the subject of [[05-inference-and-estimation/01-inference|inference]].

## Before moving on

You are done with this lesson when you can:

- Compute expectation and variance from a PMF, and use $E[X^2] - (E[X])^2$.
- Apply linearity of expectation without checking independence, and know that variance is different.
- Pick the right distribution from the mechanism, and name the assumption each requires.
- Use $z$-scores and the $68$–$95$–$99.7$ rule.

**Recap for later lookup:** $E[X] = \sum xP(x)$; $\operatorname{Var}(X) = E[X^2]-(E[X])^2$; expectation is **always** linear, variance adds only under independence; Bernoulli $p$, $p(1-p)$; binomial $np$, $np(1-p)$; geometric $1/p$; Poisson $\lambda$, $\lambda$ — mean equals variance; normal $\mu$, $\sigma^2$ with $68$–$95$–$99.7$ and $z = \frac{x-\mu}{\sigma}$; Poisson is the $n\to\infty$, $p\to0$, $np=\lambda$ limit of binomial.

**Next:** [[05-inference-and-estimation/01-inference|Inference and Estimation]] — going from a sample back to the population, and what a confidence interval actually promises.

## Related

- [[03-probability/01-probability|Probability]] — the rules these are built on
- [[02-dispersion-and-cumulative-frequency/01-dispersion|Dispersion]] — where mean and variance came from
- [[06-error-correcting-codes|Error-Correcting Codes]] — binomial reasoning about bit errors
- [[05-inference-and-estimation/01-inference|Inference]] — the Central Limit Theorem in full
