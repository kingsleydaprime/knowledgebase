# Descriptive Statistics

**[Beginner]** — summarising a dataset in a few numbers, and the datasets that prove why you must also look at it.

## Before you start

- You can compute a mean and read a table — [[01-number-systems|number systems]].
- You can plot points on axes — [[03-coordinate-geometry/01-coordinate-geometry|coordinate geometry]].

**What you will be able to do after this lesson:**

1. Compute and choose between **mean, median and mode**, and say which one a given situation calls for.
2. Estimate the mean of **grouped data**, and state the assumption that makes it an estimate rather than a fact.
3. Read and build the standard displays — bar chart, histogram, pie chart — and explain why a histogram's **area**, not its height, carries the frequency.
4. Demonstrate that identical summary statistics can describe completely different data.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 is the one that changes how you use the rest.

---

## 1. Why this exists

A dataset of ten thousand salaries is unreadable. You need a handful of numbers that stand in for it — a *centre*, a *spread*, a *shape*.

That compression is useful and it is lossy, and the whole discipline lives in the gap. The mean of ten thousand salaries hides whether everyone earns roughly the same or nine thousand earn very little while a hundred earn enormously. Both give the same mean.

So this lesson does two things: it gives you the summaries, and it shows you exactly how much they can hide. Section 5's lab is the demonstration, and it is worth more than the formulas.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Population** | Every member of the group you care about | Usually unavailable |
| **Sample** | The subset you actually measured | What you really have |
| **Datum / data** | One observation / many | Data is the plural |
| **Frequency** | How many times a value occurs | — |
| **Class interval** | A range values are grouped into, e.g. $20\text{–}29$ | Used when there are too many distinct values |
| **Mean** $\bar{x}$ | The arithmetic average, $\frac{\sum x}{n}$ | Uses every value; sensitive to extremes |
| **Median** | The middle value when sorted | Ignores how extreme the extremes are |
| **Mode** | The most frequent value | The only one that works for categories |
| **Skew** | Asymmetry of the distribution | Pulls the mean away from the median |
| **Outlier** | A value far from the rest | May be an error, or the most important point |

## 3. The three averages

**Mean** — add and divide:

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$

It uses every value, which is its strength and its weakness. One billionaire in a room of a hundred people raises the mean wealth to millions while the median stays where it was.

**Median** — sort and take the middle. With an even count, average the middle two. It is **resistant**: changing the largest value to a hundred times its size does not move it at all.

**Mode** — the most common value. The only average that works on **categorical** data: there is no mean favourite colour, but there is a modal one. A dataset can have no mode, one, or several.

### Which to use

| Situation | Use | Because |
| :--- | :--- | :--- |
| Roughly symmetric, no extremes | **Mean** | Uses all the information |
| Skewed — incomes, house prices, response times | **Median** | The tail would drag the mean somewhere unrepresentative |
| Categories — colours, brands, error types | **Mode** | The others are undefined |
| You will do further mathematics with it | **Mean** | It is the only one with clean algebra |

That last row matters more than it looks. The mean is what variance, the normal distribution and least-squares fitting are all built on, because $\sum(x_i - \bar{x}) = 0$ exactly. The median has no comparable algebra, which is why it is *reported* often and *computed with* rarely.

**On skew:** for a right-skewed distribution (a long tail of large values, like incomes) the mean sits **above** the median. That relationship is a quick diagnostic — if a report gives you both and they differ a lot, the data is skewed and the mean alone will mislead.

## 4. Grouped data

Once data is grouped into class intervals, the individual values are gone. To estimate the mean, assume every value in a class sits at the **midpoint**:

$$
\bar{x} \approx \frac{\sum f_i m_i}{\sum f_i}
$$

with $f_i$ the frequency and $m_i$ the midpoint of class $i$.

This is an **estimate**, and the assumption is explicit: values are spread evenly within each class. If they cluster at one end, the estimate is biased in that direction. The lab computes both the true mean and the grouped estimate on the same data so you can see the size of the error.

### Displays

| Display | For | The rule people get wrong |
| :--- | :--- | :--- |
| **Bar chart** | Categories | Bars are separated, because categories have no order |
| **Histogram** | Continuous data in classes | Bars touch, and **area** represents frequency |
| **Pie chart** | Parts of one whole | Only valid if the parts genuinely sum to the whole |

**The histogram rule.** With equal class widths, height is proportional to frequency and nobody notices the distinction. With **unequal** widths you must plot **frequency density**:

$$
\text{frequency density} = \frac{\text{frequency}}{\text{class width}}
$$

Otherwise a wide class looks far more common than it is, purely because it is wide. This is the single most common chart error in published statistics.

> [!TIP]
> **Predict before running the lab.** Four datasets each have eleven $(x, y)$ points. All four agree on mean $x$, mean $y$, both variances, the correlation and the best-fit line, every one of them to within $0.006$. How different can the four actually be? Commit to an answer before opening the answers.

## 5. What summaries hide

In 1973 the statistician Frank Anscombe constructed four datasets with essentially identical summary statistics and utterly different shapes. One is a clean linear relationship; one is a perfect curve; one is a straight line with a single outlier; one is a vertical stack with a single point far to the right that drags the whole regression line.

Every number you would normally report is the same. The only thing that separates them is **looking at the data**.

The lab reproduces Anscombe's quartet, prints the statistics, and draws all four as text plots.

## Worked example — runnable

**Runnable example:** save as `descriptive.py` in any empty directory and run `python3 descriptive.py`. Standard library only; writes no files.

```python
"""Averages, grouped estimates, and Anscombe's quartet."""
import math
from collections import Counter

EPS = 1e-9


def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def mode(xs):
    counts = Counter(xs)
    top = max(counts.values())
    return sorted(v for v, c in counts.items() if c == top)


def variance(xs, sample=True):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - (1 if sample else 0))


def correlation(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den


def least_squares(xs, ys):
    mx, my = mean(xs), mean(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return slope, my - slope * mx


def grouped_mean(classes):
    """classes: list of (low, high, frequency). Assumes values sit at midpoints."""
    total_f = sum(f for _, _, f in classes)
    return sum(((lo + hi) / 2) * f for lo, hi, f in classes) / total_f


def scatter(xs, ys, width=34, height=11):
    """A small text scatter plot, so the shape is visible without a library."""
    lo_x, hi_x = min(xs), max(xs)
    lo_y, hi_y = min(ys), max(ys)
    grid = [[" "] * width for _ in range(height)]
    for x, y in zip(xs, ys):
        cx = int((x - lo_x) / (hi_x - lo_x) * (width - 1))
        cy = int((y - lo_y) / (hi_y - lo_y) * (height - 1))
        grid[height - 1 - cy][cx] = "*"
    return ["|" + "".join(row) + "|" for row in grid]


if __name__ == "__main__":
    print("Block 1 - the three averages, and when they disagree")
    room = [21000, 23000, 24000, 25000, 27000, 28000, 30000, 31000, 33000, 35000]
    print(f"  ten salaries: mean {mean(room):,.0f}  median {median(room):,.0f}")
    with_founder = room + [4000000]
    print(f"  add one founder on 4,000,000:")
    print(f"    mean   {mean(with_founder):>12,.0f}   (moved by {mean(with_founder)-mean(room):+,.0f})")
    print(f"    median {median(with_founder):>12,.0f}   (moved by {median(with_founder)-median(room):+,.0f})")
    assert mean(with_founder) > 300000, "one value dragged the mean into the hundreds of thousands"
    assert abs(median(with_founder) - 28000) < EPS
    print("  the median barely moves: it counts positions, not magnitudes")
    print(f"  mean > median by {mean(with_founder) - median(with_founder):,.0f}: right-skewed, as expected")

    print()
    print("  the mode is the only average that works on categories:")
    colours = ["blue", "red", "blue", "green", "blue", "red"]
    print(f"    {colours} -> mode {mode(colours)}")
    assert mode(colours) == ["blue"]

    print()
    print("Block 2 - grouped data loses information")
    raw = ([22] * 3 + [25] * 5 + [28] * 4 + [31] * 6 + [34] * 2
           + [37] * 5 + [41] * 3 + [44] * 2)
    classes = [(20, 29, 12), (30, 39, 13), (40, 49, 5)]
    assert sum(f for _, _, f in classes) == len(raw)
    true_mean = mean(raw)
    est = grouped_mean(classes)
    print(f"  {len(raw)} values.  true mean {true_mean:.4f},  grouped estimate {est:.4f}")
    print(f"  error {abs(est - true_mean):.4f} - because the midpoint assumption is only an assumption")
    assert abs(est - true_mean) > 0.1

    print()
    print("Block 3 - histograms: with unequal widths, height lies")
    hist = [(0, 10, 20), (10, 20, 30), (20, 50, 45)]   # last class is 3x as wide
    print("     class      freq   width   frequency density")
    for lo, hi, f in hist:
        w = hi - lo
        print(f"   {lo:3}-{hi:<3}    {f:5}   {w:5}   {f / w:16.2f}")
    print("  by raw frequency the last class looks biggest (45 vs 30)")
    print("  by density it is the SMALLEST (1.50 vs 3.00) - it is just three times wider")
    assert 45 > 30 and (45 / 30) < (30 / 10)

    print()
    print("Block 4 - Anscombe's quartet: identical statistics, different data")
    x1 = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
    quartet = {
        "I":   (x1, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
        "II":  (x1, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
        "III": (x1, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
        "IV":  ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
                [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
    }
    print("   set   mean x    mean y    var x     var y     corr    slope  intercept")
    stats = []
    for name, (xs, ys) in quartet.items():
        m, c = least_squares(xs, ys)
        row = (mean(xs), mean(ys), variance(xs), variance(ys), correlation(xs, ys), m, c)
        stats.append(row)
        print(f"   {name:4} {row[0]:8.4f} {row[1]:9.4f} {row[2]:8.3f} {row[3]:9.5f}"
              f" {row[4]:8.5f} {row[5]:8.5f} {row[6]:9.5f}")
    labels = ["mean x", "mean y", "var x", "var y", "corr", "slope", "intercept"]
    print("   spread across the four sets:")
    for i, label in enumerate(labels):
        col = [r[i] for r in stats]
        spread = max(col) - min(col)
        same2dp = len({round(v, 2) for v in col}) == 1
        print(f"     {label:10} range {spread:.5f}   identical to 2 d.p.: {same2dp}")
        assert spread < 0.006, (label, spread)
    # six of the seven are identical at 2 d.p.; var y straddles a rounding boundary
    assert sum(len({round(r[i], 2) for r in stats}) == 1 for i in range(7)) == 6

    print()
    names = list(quartet)
    plots = {n: scatter(*quartet[n]) for n in names}
    for i in range(len(plots["I"])):
        print("   " + "  ".join(plots[n][i] for n in names))
    print("    " + "  ".join(f"{'set ' + n:<36}" for n in names))

    print()
    print("descriptive: passed")
```

Expected output:

```
Block 1 - the three averages, and when they disagree
  ten salaries: mean 27,700  median 27,500
  add one founder on 4,000,000:
    mean        388,818   (moved by +361,118)
    median       28,000   (moved by +500)
  the median barely moves: it counts positions, not magnitudes
  mean > median by 360,818: right-skewed, as expected

  the mode is the only average that works on categories:
    ['blue', 'red', 'blue', 'green', 'blue', 'red'] -> mode ['blue']

Block 2 - grouped data loses information
  30 values.  true mean 31.7667,  grouped estimate 32.1667
  error 0.4000 - because the midpoint assumption is only an assumption

Block 3 - histograms: with unequal widths, height lies
     class      freq   width   frequency density
     0-10        20      10               2.00
    10-20        30      10               3.00
    20-50        45      30               1.50
  by raw frequency the last class looks biggest (45 vs 30)
  by density it is the SMALLEST (1.50 vs 3.00) - it is just three times wider

Block 4 - Anscombe's quartet: identical statistics, different data
   set   mean x    mean y    var x     var y     corr    slope  intercept
   I      9.0000    7.5009   11.000   4.12727  0.81642  0.50009   3.00009
   II     9.0000    7.5009   11.000   4.12763  0.81624  0.50000   3.00091
   III    9.0000    7.5000   11.000   4.12262  0.81629  0.49973   3.00245
   IV     9.0000    7.5009   11.000   4.12325  0.81652  0.49991   3.00173
   spread across the four sets:
     mean x     range 0.00000   identical to 2 d.p.: True
     mean y     range 0.00091   identical to 2 d.p.: True
     var x      range 0.00000   identical to 2 d.p.: True
     var y      range 0.00501   identical to 2 d.p.: False
     corr       range 0.00028   identical to 2 d.p.: True
     slope      range 0.00036   identical to 2 d.p.: True
     intercept  range 0.00236   identical to 2 d.p.: True

   |                          *       |  |                       *          |  |                             *    |  |                                 *|
   |                                  |  |                *  *      *  *    |  |                                  |  |                                  |
   |                                 *|  |             *                   *|  |                                  |  |                                  |
   |                                  |  |                                  |  |                                  |  |                                  |
   |                *      *          |  |         *                        |  |                                  |  |                                  |
   |                   *         *    |  |                                  |  |                                  |  |                                  |
   |      *      *                    |  |      *                           |  |                                 *|  |*                                 |
   |                                  |  |                                  |  |                       *  *       |  |*                                 |
   |   *                              |  |   *                              |  |                *  *              |  |*                                 |
   |                                  |  |                                  |  |         *   *                    |  |*                                 |
   |*        *                        |  |*                                 |  |*  *  *                           |  |*                                 |
    set I                                 set II                                set III                               set IV                              

descriptive: passed
```

Block 4 is the lesson. Seven statistics, four datasets — and every statistic agrees across all four to within $0.006$. Six of the seven are identical to two decimal places; the variance of $y$ is the exception only because it straddles a rounding boundary at $4.1226$–$4.1276$. Yet one dataset is a line, one is a curve, one is a line with an outlier, and one is a vertical stack. **Summaries are a starting point, not a conclusion.**

## Common pitfalls and traps

- **Reporting a mean for skewed data.** Incomes, house prices, response times and wait times are all right-skewed. The mean of a latency distribution is routinely a value that almost no request experienced.
- **Plotting unequal-width histogram classes by frequency.** Use frequency density, or the widest class will always look the most common.
- **Treating the grouped mean as exact.** It assumes even spread within classes. Say "estimate", and know which way the bias runs if the data clusters.
- **Using a pie chart for things that overlap.** If respondents could pick more than one option, the slices do not sum to a whole and the chart is meaningless.
- **Deleting outliers because they are inconvenient.** An outlier may be a typo, or it may be the fraud, the failure or the discovery. Investigate before removing, and say in your write-up that you did.
- **Concluding from statistics alone.** Anscombe's quartet is the counterexample to that entire habit.

## Check your understanding

1. Find the mean, median and mode of $3, 7, 7, 8, 9, 12, 40$.
2. Which average would you report for house prices in a city, and why?
3. A histogram has classes $0\text{–}5$ (frequency 10) and $5\text{–}25$ (frequency 20). Which bar should be taller?
4. In a right-skewed distribution, which is larger — the mean or the median?
5. Two datasets have the same mean and the same standard deviation. What can you conclude about them?

<details><summary>Answers — open only after an attempt</summary>

1. Mean $= \frac{86}{7} \approx 12.29$; median $= 8$; mode $= 7$. The mean is above every value except $40$ — that single value drags it.
2. The **median**. House prices are strongly right-skewed: a small number of very expensive properties pull the mean well above what a typical buyer faces.
3. The **first**. Densities are $10/5 = 2$ and $20/20 = 1$, so the $0\text{–}5$ bar is twice as tall despite half the frequency. Plotting raw frequency would show the opposite and mislead.
4. The **mean**. The long right tail pulls it above the median, which only counts positions.
5. **Almost nothing.** Anscombe's quartet has four datasets agreeing on mean, variance, correlation and regression line, and they look entirely different. Equal summaries are consistent with wildly different data.

**And the prediction from section 4:** completely different. Set I is a roughly linear scatter; set II is a clean downward **parabola**; set III is a perfect straight line with one point knocked far off it; set IV has every $x$ equal to 8 except one at 19, which single-handedly determines the regression line. The lab's text plots show all four.
</details>

## Practice — independent task

Implement `summarise(data)` returning a full descriptive summary, then use it to detect what a mean alone would hide.

1. Return mean, median, mode(s), range, and the count. Handle an empty input and a single value explicitly.
2. Add a **skew indicator**: report `mean - median` and its sign, and classify as left-skewed, symmetric, or right-skewed using a threshold you choose and justify in a comment.
3. Add a text histogram of the data, choosing the number of classes with a stated rule (Sturges' rule, $k = \lceil\log_2 n\rceil + 1$, is a reasonable one — say why you did or did not use it).
4. Test it on: a symmetric dataset; a right-skewed one; one with a single extreme outlier; and one with two distinct clusters.
5. **The interesting case is the last one.** A bimodal dataset — say exam marks from two very different classes combined — has a mean sitting in the gap where *nobody scored*. Construct such a dataset, show that your summary reports a mean no student achieved, and say what your histogram reveals that the summary does not.

**Edge cases:** all values identical (zero range, what is the mode?); an even number of values (median interpolation); non-numeric categorical data (which statistics are still defined?).

**Done when:** your bimodal example produces a mean that no data point is near, your histogram makes the two clusters obvious, and you can state in one sentence why reporting only the mean there would be actively misleading.

## Tradeoffs, limits and extensions

**Resistance versus efficiency.** The median resists outliers; the mean uses all the data. When the data really is symmetric and clean, the mean is a *more efficient* estimator — it extracts more information from the same sample. The choice is a trade, not a ranking, and it depends on what you believe about the data's shape.

**Every summary is a model.** Reporting a mean implies the data has a meaningful centre. For a bimodal distribution it does not, and no amount of extra decimal places fixes that. The right response is to report the two groups separately, which means understanding the data well enough to know they exist.

**Where this goes next.** Centre is half the story; [[02-dispersion-and-cumulative-frequency/01-dispersion|dispersion]] is the other half, and the two together are what [[04-random-variables-and-distributions/01-distributions|distributions]] are parametrised by. Correlation and the regression line appear here as summary numbers; what they mean, and when they are safe to trust, is [[05-inference-and-estimation/01-inference|inference]].

## Before moving on

You are done with this lesson when you can:

- Choose among mean, median and mode with a reason rather than a habit.
- Estimate a grouped mean and name the assumption it rests on.
- Explain why histogram area, not height, carries the frequency.
- Say what Anscombe's quartet demonstrates, without looking it up.

**Recap for later lookup:** mean $\frac{\sum x}{n}$ uses everything and is dragged by extremes; median is resistant; mode is the only one valid for categories; right skew puts mean above median; grouped mean $\frac{\sum fm}{\sum f}$ assumes midpoints; histograms with unequal classes need **frequency density**; identical summary statistics do not mean identical data.

**Next:** [[02-dispersion-and-cumulative-frequency/01-dispersion|Dispersion and Cumulative Frequency]] — how spread out the data is, and why the variance formula divides by $n-1$.

## Related

- [[02-dispersion-and-cumulative-frequency/01-dispersion|Dispersion]] — the other half of a summary
- [[03-probability/01-probability|Probability]] — from describing data to reasoning about chance
- [[01-plane-shapes|Plane Shapes]] — the area reasoning a histogram depends on
