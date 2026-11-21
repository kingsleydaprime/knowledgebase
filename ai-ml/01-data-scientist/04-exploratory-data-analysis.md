---
id: 552141b9-0e0c-4ebc-8e2a-27369020e094
---

# Exploratory Data Analysis

## What EDA is and why it's non-negotiable
<!-- bite: 6fa22de7-0202-4691-b5f7-1168898931bc -->

**Exploratory Data Analysis** is investigating a dataset to understand its structure, spot problems, find patterns, and form hypotheses — *before* formal modeling or testing. Coined by John Tukey, its spirit is "let the data speak first." Skipping it is how people build models on broken data, test the wrong hypothesis, or get fooled by an artifact. It combines [[ai-ml/01-data-scientist/02-descriptive-statistics|descriptive statistics]] with [[ai-ml/01-data-scientist/05-data-visualization|visualization]] as an iterative loop: look, question, look again.

## The EDA checklist
<!-- bite: 4a368327-2ee4-4624-a755-299ea22e9509 -->

A rough order that generalizes across datasets:

### 1. Understand the structure

```python
df.shape            # rows × columns
df.info()           # types, non-null counts
df.head()           # actually look at the rows
df.describe()       # summary stats per numeric column
```

How many rows/columns? What's the type of each column (numeric, categorical, date, text)? What does one row *represent* (the unit of analysis)? Getting the grain wrong invalidates everything after.

### 2. Assess data quality

- **Missing data** — how much, and *where*? Is it random, or systematically missing (which biases everything)? ([[ai-ml/02-ml-engineer/02-working-with-data/01-missing-data-and-cleaning|handling missing data]].)
- **Duplicates** — real, or an artifact of a bad join?
- **Errors / impossible values** — negative ages, future dates, placeholder codes (`-999`, `"N/A"` as a string).
- **Consistency** — mismatched units, categories spelled differently (`"USA"` vs `"U.S."`).

### 3. Examine each variable (univariate)

For each column: its distribution ([[ai-ml/01-data-scientist/05-data-visualization|histogram]] for numeric, bar chart for categorical), its center and spread, its **skew** and **outliers**. This is where you decide a variable needs a log transform, or that "revenue" has a suspicious spike at zero.

### 4. Examine relationships (bivariate / multivariate)

- Numeric vs numeric → **scatter plots** and a **correlation matrix / heatmap**.
- Categorical vs numeric → grouped box plots.
- Categorical vs categorical → cross-tabs.

This is where hypotheses form ("churn seems higher for the annual plan — worth testing") and where you spot [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|confounders]] and multicollinearity.

## Outliers — investigate, don't reflexively delete
<!-- bite: 7ec86149-0142-4009-bf83-0b9816221d41 -->

An outlier might be an **error** (delete/fix it) or the **most interesting point in the dataset** (the fraud, the breakthrough, the bug). The [[ai-ml/01-data-scientist/02-descriptive-statistics|IQR]] rule and box plots flag candidates, but the right response is to *investigate why* — silently dropping outliers to make a model look better is a common way to hide the truth.

## The mindset
<!-- bite: 2fa46913-6e8b-41a5-9689-9dfabfbe49a7 -->

EDA is skeptical curiosity, not a checklist to rush. The goals:

- **Catch problems early** — bad data caught in EDA is cheap; caught after modeling, it's a wasted week (or a wrong decision shipped).
- **Generate hypotheses** — EDA *suggests* what to test; it doesn't *confirm* it. A pattern you find by looking must then be validated on fresh data or with a proper [[ai-ml/01-data-scientist/03-inferential-statistics|test]] — otherwise you're just describing noise you happened to notice.
- **Avoid the trap:** if you explore exhaustively and then run a hypothesis test on the most striking pattern you found, the p-value is meaningless (you implicitly ran hundreds of tests — [[ai-ml/01-data-scientist/03-inferential-statistics|p-hacking]]). Explore to *form* hypotheses; confirm them on data you didn't explore.

## Tooling
<!-- bite: 2569a645-9e9f-45e8-9ac2-344e17ff4b91 -->

pandas for the manipulation, [[ai-ml/01-data-scientist/05-data-visualization|matplotlib/seaborn]] for the plots. Automated EDA tools (`ydata-profiling`/pandas-profiling, Sweetviz) generate a full report in one line — a great starting scan, though never a substitute for asking your own questions of the data.

## Related
<!-- bite: fcd265c3-e91e-4c18-8e0c-cadcf95dae90 -->
- [[ai-ml/01-data-scientist/02-descriptive-statistics|Descriptive Statistics]] — the summaries EDA computes
- [[ai-ml/01-data-scientist/05-data-visualization|Data Visualization]] — EDA's other half
- [[ai-ml/02-ml-engineer/02-working-with-data/index|Working with Data]] — the cleaning EDA reveals the need for

## About this lesson
<!-- bite: fbdb0604-daed-4e76-9b02-4630e6bf5f11 -->

**Level:** reference. **Covers:** from the roadmap.sh `ai-data-scientist`/`data-analyst` roadmaps. The systematic "understand the data before you model or conclude" process — where a data scientist actually spends much of their time, and where the real insights usually come from.
