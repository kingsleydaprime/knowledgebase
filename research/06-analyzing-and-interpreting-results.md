---
id: 400169e4-a093-4a76-8e3f-ea8f171a669e
---

# Analysing and Interpreting Results

Analysing results means working out what your data really shows, separating real differences from luck, and saying exactly that much and no more.

## Before you start
<!-- bite: 7891c267-3445-4a6f-bfee-e5a3e503b59f -->

Read [[research/05-methodology-and-experiment-design|Methodology and Experiment Design]] first. You can read this lesson while your four weeks of data are coming in, but do its steps once `data.csv` is complete. You'll need Python 3 to run the analysis script (any version from the last few years).

After this lesson you will be able to:

1. score your data and compare every result with its baselines;
2. test whether a difference is bigger than luck, using the days that disagree;
3. say what a p-value means, and what it doesn't;
4. tell a difference that's real from one that's big enough to matter;
5. write the narrowest claim your data supports, after hunting for boring explanations;
6. spot the ways analysis fools people: p-hacking, testing many things, and cherry-picking.

## What analysing results is
<!-- bite: 4e53ec1b-9d1a-4edc-ad9d-50eb0330b2bf -->

You've collected the data. Now: what does it actually mean? Numbers don't tell you whether they're a real difference or luck, and the pull to believe the ones that flatter you is strong. This is the easiest place in research to fool yourself.

So analysis has two jobs. First, decide whether each difference is **real or luck**. Second, **say exactly what the numbers show, and nothing more**. Both are honesty, done carefully.

## Where we stopped
<!-- bite: f624fad9-2f29-447d-820f-74d29cc0b340 -->

Your study ran for four weeks, following the method in `plan.md`. `data.csv` has a row for every app on every day, and `plan.md` says, dated, what you predicted: each app is right about rain more often than "tomorrow will be like today". Now you'll find out whether it was.

## The kid version
<!-- bite: df205aa7-be27-4b0f-8ce8-0b402cf10232 -->

You and your friend each flip a coin 10 times. You get 6 heads, your friend gets 4. Are you better at flipping heads? No: that's luck. Flip again and it might reverse.

Research results are like that. App B was right 22 times and the guess 17 times. Is app B really better, or did it have a lucky month? The numbers won't say. You have to work it out, and the trick is to ask: *how often would a difference this big happen if it were only coin flips?*

**Where the analogy stops working.** Everyone knows a coin is 50–50, so 6 heads is obviously luck. With apps, you don't know the true accuracy; that's the thing you're trying to find out. So you need a test.

## First, the plain numbers
<!-- bite: 1791d07e-78f0-4ed6-afe4-08c9273292df -->

Start by scoring everything with the rules in `plan.md`. Here's what the analysis script in Step 1 prints for an example four weeks (made up, the same example as the last lesson):

```text
28 days scored

                   right  hit rate  avg error
A                  18/28       64%      1.2°C
B                  22/28       79%      0.7°C
C                  15/28       54%      2.0°C
always "rain"      16/28       57%
"like today"       17/28       61%
```

Read it against the baselines first. App B beats both guesses by a clear margin. App A barely does. App C loses to "always rain". For temperature, app B is also closest, off by 0.7 °C on an average day; app C is off by 2.0 °C.

Every app was scored on the **same 28 days**. If one app is missing a reading, the script drops that day for all of them, so nobody gets an easier month.

## Only the days that disagree count
<!-- bite: 9dc30a8c-5310-4ca0-b31b-a52239c156d3 -->

Is app B's 22 against 17 real? Split the days four ways:

![The 28 days of the example split four ways, comparing app B with the guess that tomorrow will be like today. On 15 days both were right and on 4 days both were wrong; those 19 days say nothing about which is better, so they are greyed out. On 7 days only app B was right, and on 2 days only the guess was right. Only these 9 days where they disagree count: app B won 7 of them](images/rs-paired-days.svg)

On 19 days they agreed (both right or both wrong), so those days can't tell you which is better. Everything comes down to the **9 days they disagreed**: app B won 7 and the guess won 2. Now the question is sharp: *if the two were really equally good, how often would one of them win 7 or more out of 9 just by luck?*

## The coin-flip test
<!-- bite: cb8d0ee2-e9a9-473c-8e17-ab6d112ed061 -->

If app B and the guess were equally good, each disagreement day would be a coin flip. So count how often a fair coin gives 7 or more heads in 9 flips:

![The coin-flip test. If app B and the guess were really equally good, each disagreement day would be a coin flip. Left, 4 weeks: the bars show how often each number of wins out of 9 would happen by luck; the orange bars, 7 or more wins, add up to 46 in 512, about 0.09, so 7 out of 9 happens by luck about 9 times in 100. Right, 8 weeks with the same pattern, 14 wins out of 18: the orange tail, 14 or more, adds up to about 0.015, under 2 times in 100, so luck is a much poorer explanation](images/rs-coin-flip-test.svg)

Nine flips can land 2⁹ = 512 ways. The ways with 7, 8 or 9 heads are $\binom{9}{7} + \binom{9}{8} + \binom{9}{9} = 36 + 9 + 1 = 46$, where $\binom{9}{7}$ ("9 choose 7") is the number of ways to pick which 7 flips are heads. So:

$$p = \frac{46}{512} \approx 0.09$$

## What p ≈ 0.09 means
<!-- bite: fa65a0ef-ee70-487e-b689-2f88b3b862fb -->

That number is the **p-value**: the chance of a result at least this strong if there were really no difference. This test is called the **sign test** (with two methods on the same days, it's also known as McNemar's test).

Luck alone would give app B a result this good about 9 times in 100. That's not very often, but it's not rare either. Most fields use 0.05 (5 times in 100) as the line, and 0.09 is above it. So the honest conclusion is: **we can't rule out luck. Four weeks wasn't enough to show app B beats the guess.**

That's not "app B is no better". It's "this study couldn't tell". Look at the right-hand picture: with eight weeks and the same pattern (14 wins out of 18), p drops to about 0.015, and luck becomes a poor explanation. More days shrink the luck, as the last lesson said.

You tested the direction you predicted in `plan.md` (app B *better*), which is why only the right-hand tail counts. Choosing the direction before the data is part of what makes the test honest.

## What a p-value is not
<!-- bite: 2178b466-a42b-4111-b9f9-0fd595294d2b -->

The p-value is the most used and most misread number in science. It is **not**:

1. **The chance the null hypothesis is true.** It's the chance of your data *if* the null were true, which is a different thing.
2. **A law at 0.05.** The 0.05 line is a habit, not a law of nature. A p of 0.049 and a p of 0.051 are practically the same evidence.
3. **A measure of importance.** With enough data, a tiny, useless difference can get a very small p-value.

That last one matters so much it gets its own section.

## Big enough to matter?
<!-- bite: cf24199b-a098-431b-9af3-abf090fa0f33 -->

"Is the difference real?" and "is the difference big?" are separate questions. The size of a difference is its **effect size**, and you should always report it in plain units, not only the p-value.

For the weather study: app B was right on 79% of days and the guess on 61%, a gap of 18 percentage points. That's about **five more right days a month**. For someone deciding whether to carry an umbrella, five days a month matters. A gap of 1 percentage point (one day in about three months) wouldn't matter to anyone, even if a year of data made it "significant".

This is the difference between **statistical significance** (bigger than luck) and **practical significance** (big enough to care about). A good results section gives both.

## Say only what you showed
<!-- bite: 6a290116-b88d-47f9-b088-c1055606f281 -->

The most common mistake in interpreting results is jumping from *"A scored higher than B in my study"* to *"A is better than B"*. The data only supports the first. Write the **narrowest claim** your evidence supports, with its scope attached:

1. Too big: *"App B is the most accurate weather app."*
2. Honest: *"Over 28 days of June 2026 in Yaba, Lagos, app B was right about next-day rain on 22 days, against 17 for the 'tomorrow will be like today' guess. The difference was not statistically significant (sign test, one-sided, p ≈ 0.09); a longer study is needed."*

The honest version says where, when, how much, compared with what, and how sure. It's the version that survives review.

## Hunt the boring explanation
<!-- bite: d198ddd8-1d3a-449d-8776-37788712bd53 -->

Before you believe a result, try to kill it. Assume it's an accident, and look for the dull reason:

1. **One event.** Did a single storm week decide everything? Score each week separately and see whether the pattern holds.
2. **A confound.** Did something else change along with the app? An app update mid-study, a change in your reading time? Check the `notes` column.
3. **Measurement.** Could the gauge's 7 am reading, which mixes two days, favour one app? (Here, no: every app is scored on the same readings.)
4. **Luck.** That's what the test is for.

If a result looks too good, be suspicious first. The results that survive your own hardest attempts to explain them away are the ones worth reporting.

## A null result is a result
<!-- bite: 582c68df-7dfe-4ba3-b796-2fae0d8dda2d -->

"We couldn't show a difference" is real knowledge. App C losing to "always rain" is a finding that would save someone from trusting it. But studies like that often go unpublished: journals and authors prefer exciting positive results. Negative results end up in a drawer, and the published literature makes things look better than they are. This is called **publication bias**, or the **file-drawer problem**.

The fix starts with you: report what you found, including what didn't work.

## Ways analysis fools people
<!-- bite: 6a98a415-cd53-4365-b09f-c4ea36bf02f4 -->

These are usually done without meaning to, which is why you need to know them:

1. **p-hacking**: trying different thresholds, subsets or metrics until something drops below 0.05, then reporting only that one.
2. **Testing many things**: run 20 tests and, by luck alone, about one will come in under 0.05. You're testing three apps, so you're running three tests. A simple, strict fix is to divide the line by the number of tests (0.05 ÷ 3 ≈ 0.017); this is called the **Bonferroni correction**.
3. **Cherry-picking**: showing the best week, or the best app, and hiding the rest.
4. **HARKing**: presenting a pattern you found as though you'd predicted it.

The cures are the ones you already have: the dated plan, reporting everything you tried, and labelling anything new as exploratory.

## From numbers to meaning
<!-- bite: 169ed856-991a-4801-8f9b-fa80b1546a1b -->

Last, connect the numbers back to the question. What did you learn? Why might it have come out this way: does app B use a local weather service, or a newer model? (That's a guess about a cause, so label it as one; it's a question for a future study.) And where does the result stop: one season, one part of Lagos, three apps.

Not every study is numbers. In **qualitative** research, such as interviews, analysis means sorting what people said into themes (called **coding**), checking them against other sources, and having a second person code the same material to see if they agree.

## Step 1: run the analysis
<!-- bite: b63f61a7-b694-4d9b-a047-83b3c1c376c2 -->

Save this script as `analyse.py` in your study folder. Check the two rules at the top match your `plan.md`, then run `python3 analyse.py data.csv`.

```python
"""Score the weather study.   python3 analyse.py data.csv"""
import csv
import sys
from math import comb

RAIN_CHANCE = 50   # the app "said rain" at this % or more (from plan.md)
RAIN_MM = 1.0      # "it rained" at this many mm or more (from plan.md)

rows = [r for r in csv.DictReader(open(sys.argv[1])) if all(r[c].strip() for c in
        ('date', 'app', 'rain_chance', 'forecast_high', 'rain_mm', 'actual_high'))]
apps = sorted({r['app'] for r in rows})
rained = {r['date']: float(r['rain_mm']) >= RAIN_MM for r in rows}
said = {(r['app'], r['date']): float(r['rain_chance']) >= RAIN_CHANCE for r in rows}
error = {(r['app'], r['date']): abs(float(r['forecast_high']) - float(r['actual_high'])) for r in rows}

# Score every app on the same days: days where every app has a reading and yesterday's rain is known.
dates = sorted(rained)
days = [d for prev, d in zip(dates, dates[1:]) if all((a, d) in said for a in apps)]
yesterday = dict(zip(dates[1:], dates))

right = {a: {d: said[a, d] == rained[d] for d in days} for a in apps}
right['always "rain"'] = {d: rained[d] for d in days}
right['"like today"'] = {d: rained[yesterday[d]] == rained[d] for d in days}

print(f'{len(days)} days scored\n')
print(f'{"":16}{"right":>8}{"hit rate":>10}{"avg error":>11}')
for name, r in right.items():
    hits = sum(r.values())
    err = f'{sum(error[name, d] for d in days) / len(days):.1f}°C' if name in apps else ''
    print(f'{name:16}{hits:>5}/{len(days):<3}{100 * hits / len(days):>8.0f}%{err:>11}')

print('\nEach app against "like today", on the days they disagree:')
for a in apps:
    wins = sum(right[a][d] and not right['"like today"'][d] for d in days)
    losses = sum(right['"like today"'][d] and not right[a][d] for d in days)
    n = wins + losses
    p = sum(comb(n, k) for k in range(wins, n + 1)) / 2 ** n if n else 1.0
    print(f'{a:16}won {wins}, lost {losses}   chance of {wins}+ wins out of {n} by luck: p = {p:.3f}')
```

Before you trust it on your data, **predict** one number by hand: count app A's right days for the first week yourself, and check the script agrees when you run it on just that week.

## Step 2: the coin-flip test by hand, once
<!-- bite: 0dd97b67-fdd4-4482-bcdc-b26786e3947f -->

Take one app's wins and losses from the script's last lines. Work out its p-value by hand, the way the coin-flip section did (count the ways to get that many wins or more, and divide by 2 to the power of the number of disagreement days), and check it matches the script. You only need to do this once, so the script's number means something to you.

## Step 3: write your results
<!-- bite: 82b7eed6-ce48-4010-9873-c2596663118a -->

Create `results.md` with four parts:

1. **The table**: paste the script's output.
2. **The test**: for each app, wins, losses and p, and whether it passes your line (use the Bonferroni line if you're testing more than one app).
3. **The claims**: one narrowest-claim sentence per app, with where, when, how much, compared with what, and how sure; plus the effect size in plain units ("about N more right days a month").
4. **Boring explanations checked**: score each week separately, read your `notes`, and write what you found.

Anything you tried that wasn't in `plan.md` goes under a heading **Exploratory**.

## Your project so far
<!-- bite: 6c680e13-5cd8-459e-9e79-3698d11d44b3 -->

```text
my-study/
├── journal.md
├── reading-log.md
├── lit-review.md
├── plan.md
├── data.csv         ← complete: four weeks
├── analyse.py       ← scores every app and baseline, and runs the coin-flip test
└── results.md       ← table, tests, narrowest claims with effect sizes, boring explanations checked
```

**Done when** `results.md` gives every app's hit rate and average error next to both baselines, a coin-flip test with its p-value for each app against your planned baseline, one narrowest-claim sentence per app with its effect size, a week-by-week check, and anything unplanned labelled exploratory.

## Terms used in this lesson
<!-- bite: 8c6021fe-9a48-40b6-a48a-9eb911d31882 -->

1. A **p-value** is the chance of a result at least this strong if there were really no difference.
2. The **sign test** compares two methods on the same days, counting only the days they disagree, as if each were a coin flip.
3. **Effect size** is how big a difference is, in plain units.
4. **Statistical significance** means a difference is bigger than luck; **practical significance** means it's big enough to care about.
5. **p-hacking** is trying analyses until one gives a small p-value and reporting only that one.
6. The **Bonferroni correction** divides the 0.05 line by the number of tests you run.
7. **Publication bias** (the file-drawer problem) is when negative results go unpublished, so the literature looks better than the truth.

## Common pitfalls and traps
<!-- bite: c14bd62e-fcfa-4f22-acb9-df29922576e1 -->

1. **"Higher" read as "better".** A higher score in one small study can be luck.
2. **Reading p as the chance you're wrong.** It isn't; it assumes the null is true.
3. **Reporting p without effect size.** A real difference can be too small to matter.
4. **Claiming more than you tested.** One month in one place isn't "the best app".
5. **Hiding what didn't work.** Null and negative results are findings.
6. **Running many tests and reporting the lucky one.** Correct for the number of tests, and report them all.

## Check your understanding
<!-- bite: 7250e72d-f031-4487-b879-48a9102dcebb -->

Try each one before you open the answer.

1. <!-- q: mcq id="2c7e0b95" -->
   Two phone chargers are tested on the same 20 phones. Charger X filled 12 phones faster, charger Y filled 6 faster, and on 2 phones they tied. How many phones count in a sign test?

   - [ ] 20
   - [x] 18
   - [ ] 12
   - [ ] 2

   <details><summary>Answer</summary>

   18: only the phones where they differ count. The 2 ties say nothing about which is faster.

   </details>

2. <!-- q: gap id="b80f4d16" answers="1;8;0.125" -->
   Two methods disagree on 3 days, and method X wins all 3. Treat each day as a coin flip.

   Number of ways to get 3 heads: ___. Total ways three flips can land: ___. So p = ___.

   <details><summary>Answer</summary>

   1 way (all heads) out of 8, so p = 1 ÷ 8 = 0.125. Even winning every disagreement can be luck when there are only 3 of them.

   </details>

3. <!-- q: mcq id="e41a7c58" -->
   A study reports p = 0.03 for the difference between two teaching methods. Which statement is correct?

   - [ ] There's a 3% chance the methods are equally good
   - [x] If the methods were really equally good, a difference this big would happen about 3 times in 100
   - [ ] There's a 97% chance the new method is better
   - [ ] The difference is big enough to matter

   <details><summary>Answer</summary>

   The p-value is the chance of data like this *if* there were no difference. It isn't the chance the null is true, and it says nothing about whether the difference is big.

   </details>

4. <!-- q: mcq id="7f3b9e20" -->
   A study of 2 million online shoppers finds a new checkout button raises sales by 0.01%, with p = 0.001. What's the best summary?

   - [ ] A large, important effect
   - [x] Almost certainly real, but too small to matter for most shops
   - [ ] Probably luck
   - [ ] Proof the button is better in every shop

   <details><summary>Answer</summary>

   Statistically significant (a huge sample makes even tiny effects show up), but the effect size, 0.01%, is practically nothing.

   </details>

5. <!-- q: mcq id="c95d2a07" -->
   Over one month in Ibadan, pump brand P used less fuel than brand Q on 21 of 30 days. Which is the most honest claim?

   - [ ] "Brand P is more fuel-efficient than brand Q."
   - [ ] "Brand P is the best pump in Nigeria."
   - [x] "Over 30 days in Ibadan, brand P used less fuel than brand Q on 21 days."
   - [ ] "Brand Q should not be sold."

   <details><summary>Answer</summary>

   The third states exactly what was measured, where and when. A full version would add the test's p-value and how much less fuel.

   </details>

6. <!-- q: mcq id="6a0e8f31" -->
   A researcher tests 20 different foods to see if any affects exam scores, and finds one with p = 0.04. What's the most likely explanation?

   - [ ] That food improves exam scores
   - [x] With 20 tests, about one is expected under 0.05 by luck alone
   - [ ] The other 19 foods were tested wrongly
   - [ ] 0.04 is too close to 0.05

   <details><summary>Answer</summary>

   Testing many things. With the Bonferroni correction the line is 0.05 ÷ 20 = 0.0025, and 0.04 is nowhere near it.

   </details>

7. <!-- q: open id="d3f61b84" -->
   A student's new spam filter catches more spam than the old one on a test week, and she's delighted. Name three boring explanations she should check before believing it.

   <details><summary>Answer</summary>

   For example: that week had unusually easy spam (one event: test other weeks); she tuned the new filter on the same emails she tested it on (leakage); the old filter ran with default settings while the new one was tuned (unequal effort); or it's luck (run a sign test on the emails where they disagree).

   </details>

## Before moving on
<!-- bite: b15afa41-12c1-49f3-9f96-2c35b614828e -->

You're done when you can compare results with baselines, run and explain the coin-flip test, read a p-value correctly, report effect size alongside it, write the narrowest honest claim, and name the ways analysis fools people; and your own `results.md` exists.

Recap: score everything on the same days and read it against the baselines. To ask "real or luck?", count only the days two methods disagree and ask how often a coin would do as well: that's the p-value. A small p means "probably not luck", not "important": report the effect size in plain units. Claim only what you tested, with its scope. Hunt the boring explanation, report what didn't work, and correct for running many tests.

Next: [[research/07-research-ethics-and-integrity|Research Ethics and Integrity]], where honest analysis meets the rules of the research community.

## Related
<!-- bite: 35ea588f-b793-455e-8481-c0718fb5227f -->

- [[research/05-methodology-and-experiment-design|Methodology and Experiment Design]]: the design that makes the analysis trustworthy.
- [[research/04-research-questions-and-hypotheses|Research Questions and Hypotheses]]: the null and alternative hypotheses being tested.
- [[research/07-research-ethics-and-integrity|Research Ethics and Integrity]]: where p-hacking crosses into misconduct.
- [[data-science/03-inferential-statistics|Inferential Statistics]]: significance tests and confidence intervals in depth.
- [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/index|Probability and Statistics]]: the foundations underneath.

## About this lesson
<!-- bite: c3e8e07b-e2e4-4c7d-9b53-722fec71cf6d -->

**Level:** intermediate. Lesson 06 of the research subject, part A (doing the research). It covers scoring against baselines, the sign test on disagreement days, reading p-values, effect size and practical significance, narrow claims, boring explanations, null results and publication bias, p-hacking, multiple tests and the Bonferroni correction, and qualitative analysis in brief. It moves the running study forward to `results.md`.

**Source:** standard statistical practice (the sign test, and McNemar's test for paired methods), *The Craft of Research*, and the reproducibility literature (Ioannidis, "Why Most Published Research Findings Are False"). Rewritten to the course standard, as a hands-on lesson, on 2026-11-26. The pictures come from `scripts/diagrams/research.py`, which asserts their numbers; the script and its example output are checked by the lab in `research/labs/weather-analysis/` (`python3 labs/run.py research/weather-analysis`).
