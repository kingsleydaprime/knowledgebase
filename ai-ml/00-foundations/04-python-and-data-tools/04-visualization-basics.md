# Visualization Basics

**[reference / practice]** — the *how-to* for making charts in Python. This is the hands-on companion to [[ai-ml/01-data-scientist/05-data-visualization|Data Visualization]] (which covers *which* chart and how to be honest) — read that for the principles, this for the code.

## matplotlib — the foundation

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

seaborn wraps matplotlib with sane defaults and works directly with [[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas DataFrames]] — pass the frame and column *names*. It's the everyday [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]] tool:

```python
import seaborn as sns

sns.histplot(data=df, x="income")                       # distribution
sns.boxplot(data=df, x="plan", y="income")              # distribution per category
sns.scatterplot(data=df, x="age", y="spend", hue="city")# relationship, colored by group
sns.heatmap(df.corr(numeric_only=True), annot=True)     # correlation matrix
sns.pairplot(df[["age", "income", "spend"]])            # every pairwise scatter — 1-line EDA
```

The `hue=` parameter (color by a category) is the fast way to add a third dimension, and `sns.pairplot`/`sns.FacetGrid` give you small-multiples almost free — matching the "map variables to visual channels" idea in the [[ai-ml/01-data-scientist/05-data-visualization|grammar of graphics]].

## The EDA plotting loop

In practice you cycle through a handful of plots per dataset:

- **`histplot` / `kdeplot`** — the shape of one variable (skew, outliers, modes).
- **`boxplot` / `violinplot`** — one variable's distribution *across categories*.
- **`scatterplot`** — two numerics; add `hue`/`size` for more.
- **`heatmap` of `.corr()`** — spot correlated features at a glance.
- **`countplot` / `value_counts().plot.bar()`** — category frequencies.

That set answers most "what does this data look like" questions ([[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]]).

## Interactive and the rest

For dashboards or notebook interactivity (hover, zoom), **Plotly** and **Altair** produce interactive charts from similar one-liners. For non-technical stakeholders, the output usually moves to a BI tool (Tableau/Power BI) — see the [[ai-ml/01-data-scientist/05-data-visualization|visualization principles]] note. But matplotlib + seaborn cover essentially all *exploratory* and most *report* needs.

## Practice

- Take the dataset you cleaned in the [[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]] note and produce: a distribution plot, a grouped box plot, a correlation heatmap, and one scatter with a `hue`. Then rewrite one of them to be *honest and clear* per the [[ai-ml/01-data-scientist/05-data-visualization|principles]] (zero-based axis, direct labels, takeaway title).

## Related
- [[ai-ml/01-data-scientist/05-data-visualization|Data Visualization]] — the principles: which chart, and honesty
- [[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]] — where the data comes from
- [[ai-ml/01-data-scientist/04-exploratory-data-analysis|Exploratory Data Analysis]] — plots as an exploration tool
