---
id: 0288fc02-c972-4d6f-8d49-153cceb373d7
---

# pandas

pandas is a Python library for working with tables of data.

## What pandas is
<!-- bite: 471c46f5-011c-4af0-93e2-6be45b3de81b -->

pandas is a Python library for working with tables of data, the kind of rows and columns you see in a spreadsheet. You use it to load a file, pick out the rows and columns you need, fix missing values and add things up by group. If you have ever sorted or filtered a school result sheet in Excel, pandas does the same jobs in code.

Next: the two pandas objects, the Series and the DataFrame.

## Series and DataFrame
<!-- bite: 5c482fe0-e385-407e-b19b-c3e93840aad3 -->

- **Series** — a 1-D labeled array (one column, with an index).
- **DataFrame** — a 2-D labeled table (columns of possibly different dtypes, sharing a row index). This is the object.

```python
import pandas as pd
df = pd.read_csv("data.csv")     # also read_excel, read_json, read_parquet, read_sql
df.head(); df.tail(); df.sample(5)
df.shape          # (rows, cols)
df.info()         # dtypes + non-null counts — your first look
df.describe()     # summary stats for numeric columns
df.columns; df.dtypes
```

`read_*` / `to_*` cover CSV, Excel, JSON, Parquet, SQL — pandas is also your data-loading layer.

## Selecting data — the part to get fluent
<!-- bite: 198fc421-8ef5-431f-b852-730f9badf206 -->

Three ways, and mixing them up is the #1 beginner confusion:

```python
df["age"]                 # one column (a Series)
df[["age", "city"]]       # multiple columns (a DataFrame)

# .loc = label-based, .iloc = integer-position-based
df.loc[0, "age"]          # by row label + column name
df.iloc[0, 2]             # by row/col integer position
df.loc[df["age"] > 30]    # boolean selection — the workhorse

# boolean masking (same idea as NumPy), combine with & | ~ and parentheses
df.loc[(df["age"] > 30) & (df["city"] == "Lagos"), ["name", "age"]]
```

**Rule: use `.loc` for label/boolean selection and `.iloc` for positional.** Chained indexing like `df[df.age > 30]["city"] = ...` triggers the famous `SettingWithCopyWarning` and may silently not work — do the assignment through a single `.loc`.

## Creating and transforming columns
<!-- bite: 277a5706-6191-4ff7-aa4f-c43252d89303 -->

Vectorized, like NumPy — avoid row loops:

```python
df["age_months"] = df["age"] * 12                 # vectorized arithmetic
df["senior"] = df["age"] > 60                      # boolean column
df["city"] = df["city"].str.strip().str.title()    # vectorized string ops via .str
df["bucket"] = pd.cut(df["age"], bins=[0, 18, 65, 120], labels=["minor","adult","senior"])
df["log_income"] = np.log1p(df["income"])
```

`.apply(func)` runs a Python function per row/element — flexible but *slow* (it's a loop in disguise). Reach for it only when there's no vectorized alternative.

## Missing data
<!-- bite: 17b0590f-1f95-4f4f-b7d7-006af0205a33 -->

Real data is full of holes ([[machine-learning/02-working-with-data/01-missing-data-and-cleaning|handling missing data]] is the ML view):

```python
df.isna().sum()                    # count missing per column — always check this early
df.dropna(subset=["income"])       # drop rows missing income
df["income"].fillna(df["income"].median())   # impute (median is robust to outliers)
```

## groupby — split, apply, combine
<!-- bite: 71bd977d-1e39-4973-bac2-75e64a3770d6 -->

The single most powerful pattern: split rows into groups, compute per group, combine the results. This is SQL's `GROUP BY`, and it answers most analytical questions:

```python
df.groupby("city")["income"].mean()                        # avg income per city
df.groupby("city").agg(avg_income=("income","mean"),
                       n=("income","size"))                 # multiple aggregations, named
df.groupby(["city", "senior"])["income"].median()          # multi-key
```

Related reshaping: `pivot_table` (spreadsheet pivots), `value_counts()` (frequency of each value — you'll use it constantly), `crosstab` (categorical vs categorical).

## Combining tables
<!-- bite: 4ed75329-e992-47b5-9d23-15e2c0182cd8 -->

```python
pd.concat([df1, df2])                          # stack rows (or axis=1 for columns)
df.merge(other, on="user_id", how="left")      # SQL-style join: inner/left/right/outer
```

`merge` is a database join — same mental model (keys, join types). Getting `how=` wrong (dropping rows with an inner join when you meant left) is a classic silent bug; check row counts before and after.

## Sorting, and the index
<!-- bite: 46e95cb4-8a69-45de-b2e2-5e3a3c5b499e -->

```python
df.sort_values("income", ascending=False)
df["city"].unique(); df["city"].nunique()
df.set_index("user_id"); df.reset_index()
```

The **index** (row labels) is pandas-specific and powerful (fast lookups, alignment on operations) but a source of confusion — when things behave oddly after a merge or groupby, a stray index is often why; `reset_index()` is the reset button.

## The performance mindset
<!-- bite: 06395db9-2c07-4f41-8c86-c3be1681c51d -->

pandas is fast when you use vectorized/`groupby`/`merge` operations and slow when you loop (`for i, row in df.iterrows()` is an anti-pattern — avoid it). For data too big for memory, **Polars** (a faster DataFrame library) and Dask/Spark ([[machine-learning/10-mlops/02-experiment-tracking-and-pipelines|data pipelines]]) are the escalation path.

## Check your understanding
<!-- bite: 7b7fc3fc-bf2c-481d-b78f-e7777fb59616 -->

Try each one before you open the answer.

1. <!-- q: mcq id="15c5d071" -->
   Which selector picks rows and columns by their integer position?

   - [ ] `.loc`
   - [x] `.iloc`

   <details><summary>Answer</summary>

   `.iloc`. Use `.loc` for labels and boolean selection, and `.iloc` for positions.

   </details>

2. <!-- q: gap id="9cd33a09" answers="isna|isnull" -->
   Fill in the gap. To count the missing values in every column, run `df.___().sum()`.

   <details><summary>Answer</summary>

   `isna`. `df.isna().sum()` gives the missing count per column. Check it early on every dataset.

   </details>

3. <!-- q: mcq id="a530d2e1" -->
   Which line gives the average income in each city?

   - [x] `df.groupby("city")["income"].mean()`
   - [ ] `df["income"].mean()`
   - [ ] `df.sort_values("city")`
   - [ ] `df["city"].value_counts()`

   <details><summary>Answer</summary>

   The groupby line. It splits the rows by city, takes the mean income per group and combines the results. It is SQL's GROUP BY.

   </details>

4. <!-- q: mcq id="a6c33c96" -->
   Which of these are slow, loop-like habits to avoid in pandas? Choose all that apply.

   - [x] `for i, row in df.iterrows():`
   - [x] `.apply()` when a vectorized option exists
   - [ ] `df["age"] * 12`
   - [ ] `df.groupby("city")`

   <details><summary>Answer</summary>

   `iterrows` and needless `.apply`. Both run a Python loop under the hood. Vectorized arithmetic and groupby run in fast compiled code.

   </details>

5. <!-- q: open id="cfd61fd4" -->
   You merge two tables and the result has fewer rows than you expected. What is a likely cause, and how do you catch it?

   <details><summary>Answer</summary>

   The `how=` was probably wrong, like an inner join where you meant a left join. Rows with no match in the other table get dropped. Check the row counts before and after every merge.

   </details>

## Practice
<!-- bite: 31ca19f9-b69f-411c-a25b-9ba7b6a6a9b3 -->

- Load a real dataset (a Kaggle CSV, your own export), and answer 10 questions about it using only `groupby`/`value_counts`/boolean selection — no loops.
- Do a full clean-up pass: check `.isna()`, fix dtypes, handle duplicates, standardize a messy categorical column. (This is the core of the [[project-ideas|EDA project]].)

## Related
<!-- bite: ee1942cb-a49f-446b-97ab-2ba91ddc8020 -->
- [[machine-learning/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — the array engine underneath
- [[machine-learning/02-working-with-data/index|Working with Data]] — cleaning/feature-engineering with these tools
- [[data-science/04-exploratory-data-analysis|Exploratory Data Analysis]] — pandas as an exploration tool

## About this lesson
<!-- bite: 0a733c40-2c2e-40b8-a4db-a322b9dfc228 -->

**Level:** reference / practice. **Covers:** the library you'll spend the most *time* in. pandas is spreadsheets-as-code: labeled, mixed-type tables with powerful selection, grouping, and joining. Built on [[machine-learning/00-foundations/04-python-and-data-tools/02-numpy|NumPy]], so vectorization and boolean masking carry over. Type these out against a real CSV.
