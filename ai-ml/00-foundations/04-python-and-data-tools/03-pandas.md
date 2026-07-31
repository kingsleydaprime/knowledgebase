# pandas

**[reference / practice]** — the library you'll spend the most *time* in. pandas is spreadsheets-as-code: labeled, mixed-type tables with powerful selection, grouping, and joining. Built on [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]], so vectorization and boolean masking carry over. Type these out against a real CSV.

## Series and DataFrame

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

Real data is full of holes ([[ai-ml/02-ml-engineer/02-working-with-data/01-missing-data-and-cleaning|handling missing data]] is the ML view):

```python
df.isna().sum()                    # count missing per column — always check this early
df.dropna(subset=["income"])       # drop rows missing income
df["income"].fillna(df["income"].median())   # impute (median is robust to outliers)
```

## groupby — split, apply, combine

The single most powerful pattern: split rows into groups, compute per group, combine the results. This is SQL's `GROUP BY`, and it answers most analytical questions:

```python
df.groupby("city")["income"].mean()                        # avg income per city
df.groupby("city").agg(avg_income=("income","mean"),
                       n=("income","size"))                 # multiple aggregations, named
df.groupby(["city", "senior"])["income"].median()          # multi-key
```

Related reshaping: `pivot_table` (spreadsheet pivots), `value_counts()` (frequency of each value — you'll use it constantly), `crosstab` (categorical vs categorical).

## Combining tables

```python
pd.concat([df1, df2])                          # stack rows (or axis=1 for columns)
df.merge(other, on="user_id", how="left")      # SQL-style join: inner/left/right/outer
```

`merge` is a database join — same mental model (keys, join types). Getting `how=` wrong (dropping rows with an inner join when you meant left) is a classic silent bug; check row counts before and after.

## Sorting, and the index

```python
df.sort_values("income", ascending=False)
df["city"].unique(); df["city"].nunique()
df.set_index("user_id"); df.reset_index()
```

The **index** (row labels) is pandas-specific and powerful (fast lookups, alignment on operations) but a source of confusion — when things behave oddly after a merge or groupby, a stray index is often why; `reset_index()` is the reset button.

## The performance mindset

pandas is fast when you use vectorized/`groupby`/`merge` operations and slow when you loop (`for i, row in df.iterrows()` is an anti-pattern — avoid it). For data too big for memory, **Polars** (a faster DataFrame library) and Dask/Spark ([[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|data pipelines]]) are the escalation path.

## Practice

- Load a real dataset (a Kaggle CSV, your own export), and answer 10 questions about it using only `groupby`/`value_counts`/boolean selection — no loops.
- Do a full clean-up pass: check `.isna()`, fix dtypes, handle duplicates, standardize a messy categorical column. (This is the core of the [[project-ideas|EDA project]].)

## Related
- [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — the array engine underneath
- [[ai-ml/02-ml-engineer/02-working-with-data/README|Working with Data]] — cleaning/feature-engineering with these tools
- [[ai-ml/01-data-scientist/04-exploratory-data-analysis|Exploratory Data Analysis]] — pandas as an exploration tool
