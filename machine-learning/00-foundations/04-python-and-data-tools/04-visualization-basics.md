---
id: 1127611c-c297-4469-b535-5eac9c8db5cd
---

# Visualization Basics

Data visualization is turning numbers into pictures.

## What data visualization is
<!-- bite: cef4b3bb-c4cc-41e5-be68-aec3a0575611 -->

Data visualization is turning numbers into pictures, like line charts, bar charts and histograms, so you can see patterns at a glance. This lesson covers the two main Python charting libraries, matplotlib and seaborn. The spending chart in a bank app or the step graph in a fitness app is the same idea.

Next: matplotlib, then seaborn.

## matplotlib — the foundation
<!-- bite: 86759e1a-770d-49a2-a012-2c9c86968b90 -->

Everything sits on matplotlib. The one concept to internalize is the **Figure / Axes** model: a `Figure` is the whole canvas; an `Axes` is a single plot on it (confusingly, "axes" = one plot, not the x/y axis lines). Learn the explicit object API, not the implicit `plt.plot()` global state — it scales to multi-panel figures:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 5))     # one Figure, one Axes
ax.plot(x, y, label="revenue")
ax.set_xlabel("month"); ax.set_ylabel("$"); ax.set_title("Revenue over time")
ax.legend()
plt.show()                                   # or plt.savefig("chart.png", dpi=150)

# multiple panels (small multiples)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].hist(data); axes[1].scatter(x, y)
```

The core chart methods on an `Axes`: `.plot` (line), `.scatter`, `.bar`/`.barh`, `.hist`, `.boxplot`, `.imshow` (heatmap/image). In a Jupyter notebook plots render inline automatically.

## seaborn — statistical plots, beautifully, in one line
<!-- bite: 3c92c33d-4b1d-415c-bafb-f934cad7606c -->

seaborn wraps matplotlib with sane defaults and works directly with [[machine-learning/00-foundations/04-python-and-data-tools/03-pandas|pandas DataFrames]] — pass the frame and column *names*. It's the everyday [[data-science/04-exploratory-data-analysis|EDA]] tool:

```python
import seaborn as sns

sns.histplot(data=df, x="income")                       # distribution
sns.boxplot(data=df, x="plan", y="income")              # distribution per category
sns.scatterplot(data=df, x="age", y="spend", hue="city")# relationship, colored by group
sns.heatmap(df.corr(numeric_only=True), annot=True)     # correlation matrix
sns.pairplot(df[["age", "income", "spend"]])            # every pairwise scatter — 1-line EDA
```

The `hue=` parameter (color by a category) is the fast way to add a third dimension, and `sns.pairplot`/`sns.FacetGrid` give you small-multiples almost free — matching the "map variables to visual channels" idea in the [[data-science/05-data-visualization|grammar of graphics]].

## The EDA plotting loop
<!-- bite: 4092722c-f895-4b70-a7f9-dc8a4f23d981 -->

In practice you cycle through a handful of plots per dataset:

- **`histplot` / `kdeplot`** — the shape of one variable (skew, outliers, modes).
- **`boxplot` / `violinplot`** — one variable's distribution *across categories*.
- **`scatterplot`** — two numerics; add `hue`/`size` for more.
- **`heatmap` of `.corr()`** — spot correlated features at a glance.
- **`countplot` / `value_counts().plot.bar()`** — category frequencies.

That set answers most "what does this data look like" questions ([[data-science/04-exploratory-data-analysis|EDA]]).

## Interactive and the rest
<!-- bite: 9b76cfb3-f514-4044-8895-41105898afc3 -->

For dashboards or notebook interactivity (hover, zoom), **Plotly** and **Altair** produce interactive charts from similar one-liners. For non-technical stakeholders, the output usually moves to a BI tool (Tableau/Power BI) — see the [[data-science/05-data-visualization|visualization principles]] note. But matplotlib + seaborn cover essentially all *exploratory* and most *report* needs.

## Check your understanding
<!-- bite: d98d1bbf-a2cd-4dad-84fd-b1f0ae5eed4f -->

Try each one before you open the answer.

1. <!-- q: mcq id="f521079f" -->
   In matplotlib, what is an `Axes`?

   - [ ] The x and y axis lines
   - [x] One single plot on the figure
   - [ ] The whole canvas

   <details><summary>Answer</summary>

   One plot. The `Figure` is the whole canvas, and each `Axes` is one plot on it.

   </details>

2. <!-- q: gap id="4d3292d9" answers="hue" -->
   Fill in the gap. In seaborn, the ___ parameter colours the points by a category, such as city.

   <details><summary>Answer</summary>

   `hue`. It adds a third dimension to the plot by colouring by group.

   </details>

3. <!-- q: mcq id="92317a21" -->
   You want to see how income is spread for each subscription plan. Which plot fits best?

   - [ ] `histplot` of income alone
   - [x] `boxplot` with `x="plan"`, `y="income"`
   - [ ] `heatmap` of `.corr()`

   <details><summary>Answer</summary>

   The boxplot. It shows one variable's distribution across categories. A histplot shows one variable alone, and a correlation heatmap compares numeric columns.

   </details>

4. <!-- q: mcq id="aede969c" -->
   Which plot shows every pairwise scatter between a few columns in one line of code?

   - [x] `sns.pairplot`
   - [ ] `sns.countplot`
   - [ ] `ax.imshow`

   <details><summary>Answer</summary>

   `sns.pairplot`. It draws every pair of columns against each other, which makes it a fast first look at a dataset.

   </details>

5. <!-- q: open id="914a6ed3" -->
   Why learn matplotlib's explicit `fig, ax = plt.subplots()` style instead of the global `plt.plot()` style?

   <details><summary>Answer</summary>

   With the explicit style you always know which plot you are drawing on, so it scales to figures with several panels. The global style relies on hidden state about the "current" plot, which gets confusing once there is more than one.

   </details>

## Practice
<!-- bite: b9878e64-0518-4d32-913b-1f6b89109cd1 -->

- Take the dataset you cleaned in the [[machine-learning/00-foundations/04-python-and-data-tools/03-pandas|pandas]] note and produce: a distribution plot, a grouped box plot, a correlation heatmap, and one scatter with a `hue`. Then rewrite one of them to be *honest and clear* per the [[data-science/05-data-visualization|principles]] (zero-based axis, direct labels, takeaway title).

## Related
<!-- bite: 6b2492b5-2286-4cea-8820-ee23e8855e16 -->
- [[data-science/05-data-visualization|Data Visualization]] — the principles: which chart, and honesty
- [[machine-learning/00-foundations/04-python-and-data-tools/03-pandas|pandas]] — where the data comes from
- [[data-science/04-exploratory-data-analysis|Exploratory Data Analysis]] — plots as an exploration tool

## About this lesson
<!-- bite: 0c011d32-8ee3-436f-bb7f-01ad6c50a034 -->

**Level:** reference / practice. **Covers:** the *how-to* for making charts in Python. This is the hands-on companion to [[data-science/05-data-visualization|Data Visualization]] (which covers *which* chart and how to be honest) — read that for the principles, this for the code.
