# Missing Data & Cleaning

Real datasets are messy — missing values, duplicate rows, inconsistent formatting, outright errors. A model trained on dirty data learns the mess along with (or instead of) the real pattern, so cleaning is usually the least glamorous, highest-leverage step in the whole pipeline — before any [[04-optimization|training]] happens at all.

## Why missing data breaks things by default

Most ML code assumes every feature has a value for every row — a matrix with a gap in it isn't a valid input to the [[04-matrix-multiplication|matrix multiplications]] that a model runs on. Missing values have to be explicitly handled before training, not just ignored and hoped away.

## Strategies for handling missing values

```python
import pandas as pd
df = pd.DataFrame({"age": [25, None, 31, 40], "income": [50000, 60000, None, 80000]})

df.isna().sum()          # count missing values per column — always check this first
df.dropna()               # drop any row with a missing value — simplest, loses data
df["age"].fillna(df["age"].mean())     # fill with the column mean — simple, works for numeric data
df["age"].fillna(df["age"].median())   # median — more robust to outliers than mean
df["age"].fillna(method="ffill")       # forward-fill — carries the last known value forward, common for time series
```

- **Drop rows/columns** — simplest, but wastes data, and can bias the dataset if missingness isn't random (e.g. if higher earners are more likely to skip the income question, dropping those rows skews the remaining data).
- **Impute with mean/median** — fast and reasonable for numeric data missing at random; median is more robust when the column has outliers.
- **Impute with a model** — predict the missing value from the other features using a separate small model; more accurate, more complex, usually only worth it when missingness is substantial and important.
- **Add a "was this missing" indicator column** — sometimes the fact that a value was missing is itself informative (a skipped survey question can correlate with the answer), and a plain imputed value throws that signal away.

## Duplicates and inconsistent formatting

```python
df.duplicated().sum()        # count exact duplicate rows
df.drop_duplicates()

df["country"].unique()       # eyeball inconsistent categories: "USA", "U.S.A.", "usa" all meaning the same thing
df["country"] = df["country"].str.strip().str.lower()   # basic normalization
```

Duplicate rows silently give some data points more influence than others during training (the model effectively sees them more than once); inconsistent category spellings silently fragment what should be one category into several, diluting the signal for all of them.

## Outliers

An outlier is a value far outside the normal range for a feature — sometimes a genuine rare event, sometimes a data entry error (an age of 200, a negative price). Deciding which it is matters: a genuine outlier might be exactly the case the model needs to learn about; an entry error should be fixed or removed. Visualizing a feature's distribution (a histogram, a box plot) before training is the fastest way to catch entry errors early, rather than discovering them as unexplained bad predictions later.

## Gotchas

- **Never clean the test/validation set using statistics computed on the test set itself** — imputing a missing value in the test set using the test set's own mean, for instance, leaks information about the test set into evaluation. Always compute cleaning statistics (mean, median, category lists) on the training set only, then apply them unchanged to validation/test data (see [[03-train-val-test-splits|train-val-test-splits]]).
- Dropping rows with missing data can silently bias a dataset if the missingness isn't random — always check whether missing values correlate with other features before defaulting to dropping them.
- "The model performs badly" is very often actually "the data going in is messier than assumed" — checking data quality is usually a faster diagnostic step than immediately suspecting the model or training setup.

## Related
- [[02-feature-engineering-and-scaling|feature-engineering-and-scaling]]
- [[03-train-val-test-splits|train-val-test-splits]]
