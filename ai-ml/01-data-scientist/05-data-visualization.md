# Data Visualization

**[reference]** — from the roadmap.sh `data-analyst`/`ai-data-scientist` roadmaps. Two jobs: **exploring** data (charts for yourself, during [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]]) and **communicating** findings (charts for others, the [[ai-ml/01-data-scientist/01-the-data-scientist-role|deliverable]]). Getting these right is a large part of a data scientist's actual impact.

## Choosing the right chart

The most common mistake is picking a chart type by habit rather than by what you're trying to show. Match the chart to the **question**:

| You want to show… | Use |
|---|---|
| **Comparison** across categories | bar chart (horizontal if many/long labels) |
| **Trend** over time | line chart |
| **Distribution** of one variable | histogram, box plot, violin plot |
| **Relationship** between two numerics | scatter plot |
| **Correlation** across many variables | heatmap |
| **Composition** (parts of a whole) | stacked bar — **rarely** a pie chart |
| **Drop-off through stages** | funnel chart |

Some hard-won specifics: **pie charts are usually a bad choice** (humans compare angles poorly — a bar chart almost always reads better); **dual y-axes mislead** (they let you imply a relationship by arbitrary scaling); and for distributions, a **box or violin plot** shows spread and outliers a bar-of-averages hides.

## The libraries and tools

- **Matplotlib** — the Python foundation; total control, verbose. Everything else sits on it.
- **Seaborn** — statistical plotting on top of Matplotlib; beautiful defaults, one-liners for common EDA charts. The everyday EDA tool.
- **Plotly / Bokeh / Altair** — interactive charts (hover, zoom), good for dashboards and notebooks.
- **ggplot2** (R) — the "grammar of graphics" reference implementation; many data scientists prefer R specifically for it.
- **BI tools** — **Tableau**, **Power BI**, Looker: drag-and-drop dashboards for business stakeholders, no code. Even **Excel** (pivot tables, charts) is a real reporting tool for analysts. These are how findings reach non-technical decision-makers.

```python
import seaborn as sns
sns.histplot(df["income"])                  # distribution
sns.scatterplot(data=df, x="age", y="spend") # relationship
sns.heatmap(df.corr(), annot=True)           # correlation matrix
```

## The grammar of graphics

The idea (from Leland Wilkinson, realized in ggplot2 and Altair) that any chart decomposes into layers: **data** → **mappings** of variables to visual channels (x, y, color, size, shape) → **geometry** (points, bars, lines) → scales and facets. Thinking this way — "which variable maps to which channel?" — is more powerful than memorizing chart types, and it's why faceting (small multiples: the same chart repeated per subgroup) is often clearer than cramming everything into one busy plot.

## Communicating honestly

Visualization is uniquely easy to mislead with — sometimes accidentally, sometimes not. The integrity rules:

- **Don't truncate the y-axis** to exaggerate a difference (start bar charts at zero). A tiny change made to look huge is the most common deceptive chart.
- **Avoid chartjunk** — 3D effects, heavy gridlines, decoration. Maximize the "data-ink ratio" (Tufte): every mark should carry information.
- **Label directly, minimize legends**, and let the title state the *takeaway* ("Conversion rose 3% after launch"), not just the variables ("Conversion over time").
- **Use color intentionally** — for meaning, not decoration; keep palettes **colorblind-safe** (~8% of men are red-green colorblind), and use sequential/diverging palettes appropriately (never a rainbow for ordered data).
- **Show uncertainty** — error bars / confidence bands, so a [[ai-ml/01-data-scientist/03-inferential-statistics|noisy estimate]] isn't read as exact.

The goal is the same as the whole role: help someone reach a *correct* conclusion quickly. A chart that's pretty but misleading is worse than no chart.

## Related
- [[ai-ml/01-data-scientist/04-exploratory-data-analysis|Exploratory Data Analysis]] — visualization as an exploration tool
- [[ai-ml/01-data-scientist/01-the-data-scientist-role|The Data Scientist Role]] — communication as half the job
- [[ai-ml/01-data-scientist/02-descriptive-statistics|Descriptive Statistics]] — Anscombe's quartet, why you must plot, not just summarize
