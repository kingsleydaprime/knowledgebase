# The Data Scientist Role

**[reference]** — from the roadmap.sh `ai-data-scientist` and `data-analyst` roadmaps. Orientation for the whole track.

## What a data scientist does

A data scientist turns data into **decisions**. The job is less "build a model that ships" and more "answer a question well enough that someone acts on it": *Is this new feature actually working? Why did churn spike? Which customers should we target? Will this change help or hurt?* The deliverable is usually an analysis, an experiment result, or a model *used for insight* — often a notebook and a presentation, not a production service.

## DS vs ML Engineer vs Data Analyst

The three blur in practice, but the emphasis differs:

| Role | Optimizes for | Typical output | Depth of stats | Ships production software? |
|---|---|---|---|---|
| **Data Analyst** | describing what happened | dashboards, reports | descriptive | no |
| **Data Scientist** | explaining *why* & predicting | experiments, models, recommendations | deep (inferential + causal) | sometimes |
| **[[ai-ml/02-ml-engineer/README\|ML Engineer]]** | a reliable model in production | a deployed, monitored model | applied | yes |

The Data Scientist sits between the analyst (who reports) and the ML engineer (who ships), leaning hardest on **statistics and experimental rigor** — the skills that let you say "this result is real, not noise" and "this actually *caused* that." Many real jobs are a blend; the split is about where the weight sits.

## The analytics spectrum

A useful frame for what kind of question you're answering — each level is harder and more valuable:

1. **Descriptive** — *what happened?* Summaries, dashboards, [[ai-ml/01-data-scientist/02-descriptive-statistics|descriptive stats]]. ("Sales fell 12% last quarter.")
2. **Diagnostic** — *why did it happen?* Drilling in, correlation, segmentation, [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]]. ("Because churn rose in one region.")
3. **Predictive** — *what will happen?* Models forecasting the future ([[ai-ml/02-ml-engineer/03-classical-ml/README|classical ML]]). ("These accounts are likely to churn.")
4. **Prescriptive** — *what should we do?* Recommending actions, optimization, [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|experiments]] to test them. ("Offer this segment a discount — we A/B tested it.")

Most business value is unlocked by moving up this ladder — and the higher rungs need the statistical and causal rigor this track is about.

## The data science workflow

Real DS work is a loop, and (like ML engineering) it's mostly *not* modeling:

```
frame the question → get & clean data → explore (EDA) → analyze / model
   → validate (is this real? is it causal?) → communicate → inform a decision
```

- **Framing** is underrated — a precisely stated question ("does X *cause* a lift in Y, for whom?") determines everything downstream. A vague question yields a useless answer.
- **Data cleaning & EDA** are most of the time ([[ai-ml/02-ml-engineer/02-working-with-data/README|working with data]], [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]]).
- **Validation** is what separates a data scientist from someone who found a pattern in noise — [[ai-ml/01-data-scientist/03-inferential-statistics|inferential statistics]] and [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal reasoning]].

## Communication is half the job

The best analysis is worthless if no one acts on it. A data scientist must translate a statistical finding into a decision-maker's language — a clear [[ai-ml/01-data-scientist/05-data-visualization|visualization]], an honest statement of uncertainty ("we're 95% confident the lift is 2–5%"), and a recommendation. Two failure modes to avoid: **false certainty** (presenting a noisy estimate as fact) and **drowning the signal** (a 40-slide deck when one chart would do). This "storytelling with data" skill is genuinely part of the role, not a soft add-on.

## The toolkit

Python (pandas, [[ai-ml/02-ml-engineer/01-foundations-of-ml/02-the-ml-toolkit|the ML stack]]) and increasingly notebooks are standard, but data science leans on **R** more than the other paths — it's built for statistics and has unmatched packages for inference, modeling, and visualization (ggplot2). SQL is essential (the data usually lives in a database), and analysts/DS often use **BI tools** (Tableau, Power BI) and even Excel for reporting ([[ai-ml/01-data-scientist/05-data-visualization|visualization]]).

## Related
- [[ai-ml/01-data-scientist/02-descriptive-statistics|Descriptive Statistics]] — the first analytical tool
- [[ai-ml/01-data-scientist/03-inferential-statistics|Inferential Statistics]] — the "is it real?" toolkit
- [[ai-ml/README|AI/ML course map]] — the three paths compared
