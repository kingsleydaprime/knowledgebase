---
id: 05ae479f-82ee-42d4-8c2c-8fe83c184f68
---

# Missing Data & Cleaning

Cleaning is fixing messy data before a model learns from it.

## What data cleaning is
<!-- bite: bd6ff2ba-afa7-433a-bbd7-db1ec0178589 -->

Real datasets are messy — missing values, duplicate rows, inconsistent formatting, outright errors. A model trained on dirty data learns the mess along with (or instead of) the real pattern, so cleaning is usually the least glamorous, highest-leverage step in the whole pipeline — before any [[04-optimization|training]] happens at all.

Next: why missing values break things, then the ways to handle them.

## Why missing data breaks things by default
<!-- bite: 81f9504d-d20e-42fc-9251-fea6a1fee63d -->

Most ML code assumes every feature has a value for every row — a matrix with a gap in it isn't a valid input to the [[04-matrix-multiplication|matrix multiplications]] that a model runs on. Missing values have to be explicitly handled before training, not just ignored and hoped away.

## Strategies for handling missing values
<!-- bite: 31264723-6cac-45fb-ab68-a52a60491044 -->

```python
import pandas as pd
df = pd.DataFrame({"age": [25, None, 31, 40], "income": [50000, 60000, None, 80000]})

df.isna().sum()          # count missing values per column — always check this first
df.dropna()               # drop any row with a missing value — simplest, loses data
df["age"].fillna(df["age"].mean())     # fill with the column mean — simple, works for numeric data
df["age"].fillna(df["age"].median())   # median — more robust to outliers than mean
df["age"].fillna(method="ffill")       # forward-fill — carries the last known value forward, common for time series
```

## Choosing a strategy for missing values
<!-- bite: a32293b7-7970-4db2-8470-6ebed5f749fe -->

Each way of handling missing values has a cost. Here is when to use which.

- **Drop rows/columns** — simplest, but wastes data, and can bias the dataset if missingness isn't random (e.g. if higher earners are more likely to skip the income question, dropping those rows skews the remaining data).
- **Impute with mean/median** — fast and reasonable for numeric data missing at random; median is more robust when the column has outliers.
- **Impute with a model** — predict the missing value from the other features using a separate small model; more accurate, more complex, usually only worth it when missingness is substantial and important.
- **Add a "was this missing" indicator column** — sometimes the fact that a value was missing is itself informative (a skipped survey question can correlate with the answer), and a plain imputed value throws that signal away.

## Duplicates and inconsistent formatting
<!-- bite: 93fe3b17-8a2c-49bc-bed9-5a1a34a44bee -->

```python
df.duplicated().sum()        # count exact duplicate rows
df.drop_duplicates()

df["country"].unique()       # eyeball inconsistent categories: "USA", "U.S.A.", "usa" all meaning the same thing
df["country"] = df["country"].str.strip().str.lower()   # basic normalization
```

Duplicate rows silently give some data points more influence than others during training (the model effectively sees them more than once); inconsistent category spellings silently fragment what should be one category into several, diluting the signal for all of them.

## Outliers
<!-- bite: f92256fa-1491-4fbd-b8f4-21247f1faf92 -->

An outlier is a value far outside the normal range for a feature — sometimes a genuine rare event, sometimes a data entry error (an age of 200, a negative price). Deciding which it is matters: a genuine outlier might be exactly the case the model needs to learn about; an entry error should be fixed or removed. Visualizing a feature's distribution (a histogram, a box plot) before training is the fastest way to catch entry errors early, rather than discovering them as unexplained bad predictions later.

## Gotchas
<!-- bite: 6bd34db8-a55b-4585-86b0-3f62a9324f13 -->

- **Never clean the test/validation set using statistics computed on the test set itself** — imputing a missing value in the test set using the test set's own mean, for instance, leaks information about the test set into evaluation. Always compute cleaning statistics (mean, median, category lists) on the training set only, then apply them unchanged to validation/test data (see [[03-train-val-test-splits|train-val-test-splits]]).
- Dropping rows with missing data can silently bias a dataset if the missingness isn't random — always check whether missing values correlate with other features before defaulting to dropping them.
- "The model performs badly" is very often actually "the data going in is messier than assumed" — checking data quality is usually a faster diagnostic step than immediately suspecting the model or training setup.

## Check your understanding
<!-- bite: 18e995d4-63f2-4806-842f-d83496d926c4 -->

Try each one before you open the answer.

1. <!-- q: mcq id="7d802617" -->
   The income column has a few huge values (outliers) and some missing ones. Which fill value is the safer choice?

   - [ ] The mean
   - [x] The median
   - [ ] Zero

   <details><summary>Answer</summary>

   The median. A few huge values drag the mean up, but they barely move the median. Zero would invent a fake income.

   </details>

2. <!-- q: exact id="eb67ec92" answer="2" accept="two" -->
   `df = pd.DataFrame({"age": [25, None, 31, 40], "income": [50000, 60000, None, 80000]})`. How many rows are left after `df.dropna()`?

   <details><summary>Answer</summary>

   2. Row 2 is missing an age and row 3 is missing an income, so both are dropped. Half the data is gone, which is the cost of dropping.

   </details>

3. <!-- q: mcq id="e994beb1" -->
   The country column holds "USA", "U.S.A." and "usa". What problem does this cause?

   - [ ] None, the model reads them as the same
   - [x] One real category gets split into several, which dilutes the signal
   - [ ] It creates duplicate rows

   <details><summary>Answer</summary>

   It fragments one category into several. Normalize them, for example with `.str.strip().str.lower()`, and map the spellings to one value.

   </details>

4. <!-- q: mcq id="82ea1ab8" -->
   Where should the mean used to fill missing test-set values come from?

   - [x] The training set only
   - [ ] The test set itself
   - [ ] The whole dataset, before splitting

   <details><summary>Answer</summary>

   The training set only. Using the test set's own statistics leaks information about it into evaluation, which makes the score look better than it really is.

   </details>

5. <!-- q: open id="a082189f" -->
   Higher earners are more likely to skip the income question. Why is dropping the rows with missing income a bad idea here, and what could you do instead?

   <details><summary>Answer</summary>

   The missingness isn't random, so dropping those rows removes mostly high earners and skews the data that's left. Instead, impute the value (or predict it with a small model), and add a "was missing" indicator column, because skipping the question is itself informative.

   </details>

## Related
<!-- bite: e0d8b5c2-c66f-4c9b-b884-7532156967d9 -->
- [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]]
- [[03-train-val-test-splits|train-val-test-splits]]
