# Probability and Statistics

**Describing data you have, and reasoning about data you do not.** Written to [[COURSE-STANDARD|the course standard]]: prerequisites, observable outcomes, worked derivations, a runnable lab whose output was generated from an actual run, practice with hidden answers, and a demonstrable finish line.

This umbrella merges both curricula — SS1–SS3 statistics and probability from the [[ss1-ss3-course-outline|NERDC outline]], and the university probability and mathematical statistics course from the [[uni-math-course-outline|university track]] — so each subject appears once, secondary treatment first.

> **The one idea:** every summary is a compression, and compression loses information. A mean hides a bimodal split; a $p$-value hides an effect size; a $95\%$ confidence interval hides that the $95\%$ describes the *procedure* rather than the interval. This course teaches the tools and, in the same breath, exactly what each one throws away.

## Reading order

Strictly sequential. Inference needs distributions, which need probability, which needs the descriptive vocabulary.

1. [[01-descriptive-statistics/01-descriptive-statistics|Descriptive Statistics]] — **[Beginner]** — mean, median, mode, grouped data, and **Anscombe's quartet**: four datasets agreeing on every statistic and looking nothing alike
2. [[02-dispersion-and-cumulative-frequency/01-dispersion|Dispersion and Cumulative Frequency]] — **[Beginner]** — range, IQR, variance, ogives, outliers, and **why the variance formula divides by $n-1$**, demonstrated rather than asserted
3. [[03-probability/01-probability|Probability]] — **[Beginner → Intermediate]** — sample spaces, the rules, conditional probability, Bayes, and why a **99%-accurate test is wrong 91% of the time it fires**
4. [[04-random-variables-and-distributions/01-distributions|Random Variables and Distributions]] — **[Intermediate]** — expectation, variance, and the five distributions worth knowing, each tied to the mechanism that produces it
5. [[05-inference-and-estimation/01-inference|Inference and Estimation]] — **[Advanced]** — the Central Limit Theorem, standard error, confidence intervals, hypothesis tests, and what a $p$-value is not
6. [[06-stochastic-processes/01-markov-chains|Stochastic Processes]] — **[Advanced]** — Markov chains, random walks, queues, and **why the last 10% of capacity is unusable**

## Where the two curricula meet

| Lesson | Secondary source | University source |
| :--- | :--- | :--- |
| Descriptive statistics | SS1 T3 — frequency tables, charts, mean/median/mode | assumed |
| Dispersion, cumulative frequency | SS2 T3 — ogives, range, variance, standard deviation | assumed |
| Probability | SS2 T3 basic; SS3 T2 mutually exclusive, independent, tree diagrams | Y3S2 probability spaces |
| Distributions | — | Y3S2 — random variables, Normal, Binomial, Poisson |
| Inference | — | Y3S2 — central limit theorem, parameter estimation |
| Stochastic processes | — | Y4S2 — Markov chains, Poisson processes |

## What is verified

Every lab was executed and its expected output generated from that run. Several exist to test a claim rather than illustrate one:

- **Anscombe's quartet** — seven statistics agreeing across four datasets to within $0.006$, and text scatter plots showing a line, a parabola, an outlier and a vertical stack.
- **The $n-1$ correction** — 200,000 samples of size 5: dividing by $n$ lands at exactly $80\%$ of the true variance, which is $\frac{n-1}{n}$.
- **The base rate fallacy** — counted out over 100,000 people: 99 true positives against 999 false ones.
- **Monty Hall with a control** — a *knowing* host gives $\tfrac13$ / $\tfrac23$; a host opening at random gives no advantage at all, isolating knowledge as the mechanism.
- **Poisson as a binomial limit** — the gap shrinking by a factor of ten for every tenfold increase in $n$.
- **Confidence interval coverage** — 10,000 intervals per sample size, showing $z$-intervals cover only $87.7\%$ at $n=5$ and still fall marginally short at $n=100$.
- **$p$-values under a true null** — uniform to the decile, with $5.6\%$ falling below $0.05$.
- **M/M/1 queueing** — a $10\%$ traffic rise multiplying the queue eleven-fold.

## How to study this

1. **Attempt the prediction before reading on.** Every lesson stops once and asks you to commit. The answers sit at the end of *Check your understanding*, never beside the question.
2. **Trust the count over the formula.** Bayes is easier as a table of 100,000 people than as an equation, and the lessons do it that way first.
3. **Simulate to check, derive to claim.** Every simulation here carries $1/\sqrt{N}$ error; it confirms arithmetic, it does not establish results.
4. **Watch what each tool discards.** That is the thread through all six lessons, and the reason the labs are built the way they are.

## Related

- [[mathematics/index|mathematics/]] — the parent course and the full topic map
- [[02-discrete-math/06-combinatorics-and-counting|Combinatorics]] — the counting probability is built on
- [[04-linear-algebra/06-eigenvalues/01-eigenvalues-and-eigenvectors|Eigenvalues]] — the steady state of lesson 6, algebraically
- [[ai-ml/index|ai-ml/]] — where distributions, inference and the CLT are used daily
- [[COURSE-STANDARD|Course standard]] — the teaching shape these lessons follow
