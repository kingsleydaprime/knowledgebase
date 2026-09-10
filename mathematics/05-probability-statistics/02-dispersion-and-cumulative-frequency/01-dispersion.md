# Dispersion and Cumulative Frequency

**[Beginner]** — how spread out the data is, and why the variance formula divides by $n-1$ rather than $n$.

## Before you start

- You can compute a mean and a median — [[01-descriptive-statistics/01-descriptive-statistics|descriptive statistics]].
- You can read a graph and interpolate between points — [[03-coordinate-geometry/01-coordinate-geometry|coordinate geometry]].

**What you will be able to do after this lesson:**

1. Compute range, quartiles, **interquartile range**, variance and standard deviation, and say what each is resistant to.
2. Explain **why the sample variance divides by $n-1$**, and demonstrate the bias that appears if you use $n$.
3. Build and read a **cumulative frequency curve**, and get the median and quartiles off it.
4. Apply the $1.5 \times \text{IQR}$ rule for outliers, and say what it does and does not claim.

**Study route:** read 1–5, attempt the prediction in section 3, then run the lab. Block 3 settles the $n-1$ question with numbers rather than assertion.

---

## 1. Why this exists

Two production servers both average $100$ ms response time. On the first, almost every request takes between $95$ and $105$ ms. On the second, most take $20$ ms and a few take $2$ seconds.

Same centre. Completely different service. The difference is **dispersion**, and it is often the thing that actually matters — an average that is right on average and wrong in both directions is not a useful promise to make to a user.

Centre tells you where the data sits. Spread tells you how much you should trust the centre.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Range** | Largest minus smallest | Uses only two values; destroyed by one outlier |
| **Quartile** | The values cutting the sorted data into four | $Q_1$, $Q_2$ (the median), $Q_3$ |
| **IQR** | $Q_3 - Q_1$ — the spread of the middle half | Resistant to outliers |
| **Percentile** | The value below which a given percentage falls | The 90th percentile is the $p90$ of latency dashboards |
| **Deviation** | $x_i - \bar{x}$, how far one value is from the mean | These always sum to exactly zero |
| **Variance** | The mean of the **squared** deviations | In squared units |
| **Standard deviation** | The square root of the variance | Back in the original units |
| **Cumulative frequency** | Running total of frequencies | Plotted as an *ogive* |
| **Ogive** | The cumulative frequency curve | Plotted at class **upper bounds** |

## 3. Variance, and the $n-1$

Deviations from the mean sum to zero by construction:

$$
\sum (x_i - \bar{x}) = \sum x_i - n\bar{x} = n\bar{x} - n\bar{x} = 0
$$

So you cannot average them directly. **Squaring** them fixes the sign problem, and gives the variance:

$$
s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2
$$

Standard deviation is $s = \sqrt{s^2}$, which puts the answer back in the original units — metres rather than square metres.

### Why $n-1$ and not $n$

The intuition first, then the demonstration.

When you compute the variance of a **sample**, you do not know the population mean $\mu$. You use the sample mean $\bar{x}$ instead — and $\bar{x}$ is, by construction, the number that makes $\sum(x_i - \bar{x})^2$ as small as it can possibly be. It is fitted *to this sample*.

So the sum of squared deviations about $\bar{x}$ is systematically **smaller** than it would have been about the true $\mu$. Dividing by $n$ inherits that shortfall and underestimates the population variance, every time. Not sometimes — on average, always.

The correction is to divide by $n - 1$: you spent one **degree of freedom** estimating the mean, so only $n-1$ of the deviations are free to vary. Once you know $n-1$ of them, the last is determined, because they must sum to zero.

The factor works out exactly: dividing by $n$ gives, on average, $\frac{n-1}{n}$ of the true variance. For $n = 5$ that is $80\%$ — a $20\%$ underestimate, which is not a rounding detail.

> [!TIP]
> **Predict before running the lab.** A population has variance exactly $4.0$. You take thousands of samples of size $5$, computing the variance of each with $\div n$ and with $\div(n-1)$, then average each over all the samples. What two numbers do you expect? Commit before opening the answers.

**When $n$ is right.** If you have the **entire population**, there is no estimation and no lost degree of freedom: divide by $n$. The distinction is not about sample size, it is about whether the mean you subtracted was estimated from the same data.

## 4. Quartiles, ogives and outliers

**Quartiles** cut the sorted data into four equal parts. Conventions for the exact positions differ between textbooks and software — the lab states which one it uses, and that is the honest way to handle it.

**Cumulative frequency curves.** Plot the running total against the **upper bound** of each class, and join the points. Read off:

- the **median** at $\tfrac{n}{2}$ up the vertical axis,
- $Q_1$ at $\tfrac{n}{4}$, $Q_3$ at $\tfrac{3n}{4}$,
- any percentile at the corresponding height.

Plotting at class *midpoints* instead of upper bounds is the standard error: cumulative frequency counts everything *up to and including* the class, so the point belongs at its top.

**The $1.5 \times \text{IQR}$ rule.** A value is flagged as an outlier if it lies below $Q_1 - 1.5\,\text{IQR}$ or above $Q_3 + 1.5\,\text{IQR}$.

This is a **convention**, not a test. It flags roughly $0.7\%$ of data drawn from a perfectly normal distribution — so on a large clean dataset it will flag points that are not errors at all. It is a prompt to look, not a verdict.

## 5. Which measure to use

| Measure | Resistant to outliers? | Uses all data? | Use when |
| :--- | :---: | :---: | :--- |
| Range | No — worst possible | No | Quick sanity check only |
| IQR | **Yes** | No | Skewed data, or outliers present |
| Standard deviation | No | **Yes** | Roughly symmetric data, and further mathematics |

The pairing matters: report **median with IQR**, or **mean with standard deviation**. Mixing them — a mean with an IQR — signals that the choice was not deliberate.

## Worked example — runnable

**Runnable example:** save as `dispersion.py` in any empty directory and run `python3 dispersion.py`. Standard library only; writes no files.

```python
"""Spread, quartiles, ogives, and a demonstration of why variance uses n-1."""
import math
import random


def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs); n = len(s); m = n // 2
    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2


def quartiles(xs):
    """Tukey's hinges: split at the median, EXCLUDING it when n is odd."""
    s = sorted(xs); n = len(s); m = n // 2
    lower, upper = s[:m], s[m + 1:] if n % 2 else s[m:]
    return median(lower), median(s), median(upper)


def variance(xs, ddof=1):
    """ddof=1 divides by n-1 (a sample); ddof=0 divides by n (a population)."""
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def stdev(xs, ddof=1):
    return math.sqrt(variance(xs, ddof))


def outliers(xs):
    q1, _, q3 = quartiles(xs)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [x for x in xs if x < lo or x > hi], (lo, hi)


def ogive(classes):
    """classes: (low, high, frequency). Returns cumulative points at UPPER bounds."""
    total = 0
    pts = []
    for lo, hi, f in classes:
        total += f
        pts.append((hi, total))
    return pts


def read_from_ogive(points, target):
    """Linear interpolation between plotted points - what you do by eye on paper."""
    prev_x, prev_y = points[0][0], 0
    for x, y in points:
        if y >= target:
            if y == prev_y:
                return x
            return prev_x + (target - prev_y) * (x - prev_x) / (y - prev_y)
        prev_x, prev_y = x, y
    return points[-1][0]


if __name__ == "__main__":
    print("Block 1 - two servers with the same mean")
    steady = [95, 98, 99, 100, 100, 101, 102, 103, 104, 98]
    spiky = [20, 21, 22, 20, 23, 21, 19, 22, 80, 752]   # same total, so the same mean
    for name, data in [("steady", steady), ("spiky ", spiky)]:
        q1, q2, q3 = quartiles(data)
        print(f"  {name}: mean {mean(data):7.2f}  median {q2:6.1f}  sd {stdev(data):8.2f}"
              f"  IQR {q3 - q1:6.1f}  range {max(data) - min(data):6}")
    assert abs(mean(steady) - mean(spiky)) < 1.0, "the two means are close"
    assert stdev(spiky) > 10 * stdev(steady)
    print("  near-identical means; the standard deviations differ by more than 10x")

    print()
    print("Block 2 - deviations from the mean always sum to zero")
    for data in (steady, spiky, [1, 2, 3]):
        total = sum(x - mean(data) for x in data)
        print(f"  n={len(data):2}: sum of deviations = {total:.12f}")
        assert abs(total) < 1e-9
    print("  which is why they must be squared before averaging")

    print()
    print("Block 3 - why n-1: the bias, measured")
    # A population we know everything about.
    population = [2, 4, 4, 4, 5, 5, 7, 9]
    mu = mean(population)
    true_var = variance(population, ddof=0)          # a real population: divide by n
    print(f"  population {population}")
    print(f"  true mean {mu}, true variance {true_var}")

    random.seed(20260910)
    TRIALS, N = 200000, 5
    tot_n = tot_n1 = 0.0
    for _ in range(TRIALS):
        sample = [random.choice(population) for _ in range(N)]
        tot_n += variance(sample, ddof=0)
        tot_n1 += variance(sample, ddof=1)
    avg_n, avg_n1 = tot_n / TRIALS, tot_n1 / TRIALS
    print(f"  {TRIALS:,} samples of size {N}:")
    print(f"    average of (divide by n)   = {avg_n:.4f}   vs true {true_var:.4f}"
          f"   -> {100 * avg_n / true_var:.1f}% of the truth")
    print(f"    average of (divide by n-1) = {avg_n1:.4f}   vs true {true_var:.4f}"
          f"   -> {100 * avg_n1 / true_var:.1f}% of the truth")
    print(f"  theory says dividing by n gives (n-1)/n = {(N-1)/N:.3f} of the variance")
    assert abs(avg_n / true_var - (N - 1) / N) < 0.01, "the n version is biased low"
    assert abs(avg_n1 / true_var - 1.0) < 0.01, "the n-1 version is unbiased"
    print("  the n-1 version lands on the truth; the n version is short by exactly 1/n")

    print()
    print("Block 4 - quartiles, the IQR rule, and what it flags")
    marks = [12, 15, 18, 22, 25, 27, 28, 30, 31, 33, 35, 38, 41, 44, 91]
    q1, q2, q3 = quartiles(marks)
    found, (lo, hi) = outliers(marks)
    print(f"  data: {marks}")
    print(f"  Q1={q1}  median={q2}  Q3={q3}  IQR={q3-q1}")
    print(f"  fences: below {lo} or above {hi}  ->  flagged: {found}")
    assert found == [91]
    print("  91 is flagged. That is a prompt to investigate, not a verdict:")
    print("  the rule flags about 0.7% of perfectly normal data as well")

    print()
    print("Block 5 - a cumulative frequency curve, read by interpolation")
    classes = [(0, 10, 4), (10, 20, 11), (20, 30, 19), (30, 40, 12), (40, 50, 4)]
    pts = ogive(classes)
    n = pts[-1][1]
    print("   upper bound   cumulative")
    for x, y in pts:
        bar = "#" * int(40 * y / n)
        print(f"   {x:11}   {y:10}  {bar}")
    for label, frac in [("Q1", 0.25), ("median", 0.50), ("Q3", 0.75), ("90th pct", 0.90)]:
        print(f"   {label:9} at height {frac * n:5.1f}  ->  {read_from_ogive(pts, frac * n):.3f}")
    med = read_from_ogive(pts, n / 2)
    assert 20 < med < 30, "the median class is 20-30"
    q1o, q3o = read_from_ogive(pts, n / 4), read_from_ogive(pts, 3 * n / 4)
    print(f"   IQR from the curve: {q3o - q1o:.3f}")
    assert q3o > med > q1o

    print()
    print("dispersion: passed")
```

Expected output:

```
Block 1 - two servers with the same mean
  steady: mean  100.00  median  100.0  sd     2.67  IQR    4.0  range      9
  spiky : mean  100.00  median   21.5  sd   229.84  IQR    3.0  range    733
  near-identical means; the standard deviations differ by more than 10x

Block 2 - deviations from the mean always sum to zero
  n=10: sum of deviations = 0.000000000000
  n=10: sum of deviations = 0.000000000000
  n= 3: sum of deviations = 0.000000000000
  which is why they must be squared before averaging

Block 3 - why n-1: the bias, measured
  population [2, 4, 4, 4, 5, 5, 7, 9]
  true mean 5.0, true variance 4.0
  200,000 samples of size 5:
    average of (divide by n)   = 3.2012   vs true 4.0000   -> 80.0% of the truth
    average of (divide by n-1) = 4.0015   vs true 4.0000   -> 100.0% of the truth
  theory says dividing by n gives (n-1)/n = 0.800 of the variance
  the n-1 version lands on the truth; the n version is short by exactly 1/n

Block 4 - quartiles, the IQR rule, and what it flags
  data: [12, 15, 18, 22, 25, 27, 28, 30, 31, 33, 35, 38, 41, 44, 91]
  Q1=22  median=30  Q3=38  IQR=16
  fences: below -2.0 or above 62.0  ->  flagged: [91]
  91 is flagged. That is a prompt to investigate, not a verdict:
  the rule flags about 0.7% of perfectly normal data as well

Block 5 - a cumulative frequency curve, read by interpolation
   upper bound   cumulative
            10            4  ###
            20           15  ############
            30           34  ###########################
            40           46  ####################################
            50           50  ########################################
   Q1        at height  12.5  ->  17.727
   median    at height  25.0  ->  25.263
   Q3        at height  37.5  ->  32.917
   90th pct  at height  45.0  ->  39.167
   IQR from the curve: 15.189

dispersion: passed
```

Block 3 is the argument. Two hundred thousand samples, and dividing by $n$ lands at exactly $80\%$ of the true variance — which is $\frac{n-1}{n} = \frac{4}{5}$, as predicted. The correction is not a convention; it is the size of a measurable bias.

## Common pitfalls and traps

- **Using $n$ for a sample.** It underestimates, systematically, by a factor of $\frac{n-1}{n}$. The smaller the sample, the worse — and small samples are exactly when you are most likely to be doing this by hand.
- **Using $n-1$ for a full population.** There is no estimation, so there is no correction. Dividing by $n-1$ then *over*estimates.
- **Reporting variance in the write-up.** It is in squared units — "the variance of the delay was $9$ seconds squared" is not a sentence anyone can act on. Report the standard deviation.
- **Plotting an ogive at class midpoints.** Cumulative frequency counts everything up to the top of the class, so the point goes at the **upper bound**.
- **Treating the $1.5\,\text{IQR}$ rule as a test for errors.** It is a screening convention. On a large clean dataset it will flag genuine data.
- **Mixing centre and spread measures.** Median with IQR, or mean with standard deviation. A mean reported with an IQR usually means neither was chosen on purpose.
- **Assuming quartile values are universal.** Textbooks and libraries use different interpolation conventions and give slightly different answers on small datasets. Say which you used.

## Check your understanding

1. Find the range, $Q_1$, median, $Q_3$ and IQR of $4, 7, 8, 11, 13, 15, 18, 21$.
2. A dataset has variance $16$ cm². What is its standard deviation, and in what units?
3. Why can you not simply average the deviations from the mean?
4. When is dividing by $n$ the correct choice?
5. A cumulative frequency curve for $80$ students reaches $20$ at mark $35$ and $60$ at mark $58$. Estimate the interquartile range.

<details><summary>Answers — open only after an attempt</summary>

1. Range $= 21 - 4 = 17$. With eight values the median is $\frac{11+13}{2} = 12$. Lower half $4,7,8,11$ gives $Q_1 = \frac{7+8}{2} = 7.5$; upper half $13,15,18,21$ gives $Q_3 = \frac{15+18}{2} = 16.5$. IQR $= 9$.
2. $s = \sqrt{16} = 4$ **cm** — the square root returns it to the original units, which is the entire reason standard deviation is reported instead of variance.
3. Because they always sum to exactly zero: $\sum(x_i - \bar{x}) = 0$ by construction. Their average is therefore $0$ for every dataset, carrying no information. Squaring removes the cancellation.
4. When you have the **whole population**, so the mean you subtracted is the true mean rather than one estimated from the same data. No degree of freedom was spent, so no correction is needed.
5. $Q_1$ is at height $20$, which the curve reaches at $35$. $Q_3$ is at height $60$, reached at $58$. So IQR $\approx 58 - 35 = 23$.

**And the prediction from section 3:** the $\div(n-1)$ average lands on $4.0$ — it is **unbiased**. The $\div n$ average lands on $\frac{n-1}{n} \times 4.0 = \frac{4}{5}\times 4.0 = 3.2$ — short by exactly $20\%$. The lab confirms both to within $1\%$ over 200,000 samples.
</details>

## Practice — independent task

Implement `box_plot_summary(data)` returning the five-number summary and a text box plot, then investigate what the $1.5\,\text{IQR}$ rule actually flags.

1. Return minimum, $Q_1$, median, $Q_3$, maximum, the IQR, the fences, and the flagged outliers. State which quartile convention you used and why.
2. Draw the box plot as text: whiskers to the most extreme values **inside** the fences, outliers marked individually beyond them.
3. **Measure the false-positive rate.** Generate many samples of size $n$ from a normal distribution (`random.gauss`) with a fixed seed, and count what fraction of *points* get flagged. Compare against the theoretical $\approx 0.7\%$.
4. Then vary $n$ from $10$ to $10{,}000$ and report the fraction of **samples** containing at least one flagged point. Explain the trend — it is not the same question as step 3, and the answer surprises people.
5. Finally, run the same experiment on data from a genuinely skewed distribution (an exponential, say `random.expovariate(1)`), and report how the flagging rate changes. Say what that means for using the rule on latency data.

**Edge cases:** fewer than four data points; all values identical (IQR of zero — what do the fences become, and what does the rule then flag?); exactly one outlier at the fence boundary.

**Done when:** your step-3 rate is close to $0.7\%$, your step-4 answer explains the trend rather than just reporting it, and you can say in one sentence why applying this rule to response-time data flags things that are not errors.

## Tradeoffs, limits and extensions

**Standard deviation assumes symmetry to be interpretable.** "Mean $\pm$ one standard deviation" suggests a symmetric band. On skewed data that band can extend below zero for a quantity that cannot be negative — a sign the summary does not fit the shape. Percentiles do not have this problem, which is why latency is reported as $p50/p95/p99$ rather than mean $\pm$ sd.

**Squaring is a choice with consequences.** Squaring makes the algebra work — it gives the mean its special status, and makes variances of independent quantities add. It also means one point twice as far from the centre contributes **four** times as much, so the standard deviation is strongly influenced by extremes. The mean absolute deviation avoids that and is barely used, because it has no comparable algebra.

**Where this goes next.** Variance is what makes the normal distribution's parameters meaningful, and the fact that variances *add* for independent quantities is the engine of the Central Limit Theorem — the reason the standard error of a mean is $\sigma/\sqrt{n}$, which is the whole basis of [[05-inference-and-estimation/01-inference|inference]].

## Before moving on

You are done with this lesson when you can:

- Compute all five of range, IQR, variance, standard deviation and any percentile.
- Explain the $n-1$ correction from degrees of freedom, and state the size of the bias without it.
- Build an ogive with the points in the right places and read quartiles off it.
- Apply the IQR outlier rule and describe its limits.

**Recap for later lookup:** range is worst-case fragile; IQR $= Q_3 - Q_1$ is resistant; $s^2 = \frac{1}{n-1}\sum(x-\bar{x})^2$ for a **sample**, $\div n$ for a **population**; dividing by $n$ on a sample underestimates by $\frac{n-1}{n}$; standard deviation restores the original units; ogives are plotted at class **upper bounds**; outlier fences at $Q_1 - 1.5\,\text{IQR}$ and $Q_3 + 1.5\,\text{IQR}$.

**Next:** [[03-probability/01-probability|Probability]] — from describing data you have to reasoning about data you have not seen yet.

## Related

- [[01-descriptive-statistics/01-descriptive-statistics|Descriptive Statistics]] — centre, of which this is the other half
- [[04-random-variables-and-distributions/01-distributions|Distributions]] — where mean and variance become parameters
- [[05-inference-and-estimation/01-inference|Inference and Estimation]] — where $\sigma/\sqrt{n}$ comes from
