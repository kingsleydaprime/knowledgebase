# Data Analysis

## What data analysis is

**Data analysis is using data to answer a business question, so that someone can make a better decision.**

A shop owner asks: "Sales dropped last month. Why?" A data analyst pulls the sales records, breaks them down by product, by city and by week, and finds that one popular item ran out of stock in Lagos for ten days. That's the answer, and it leads to a decision: order more stock earlier. The answer is the point. A correct number that nobody acts on hasn't done its job.

Analysts mostly use **SQL** to pull data from databases, spreadsheets and dashboards to explore it, and clear writing and charts to explain what they found. It's the most common data job, and a good way into the field.

It sits between two neighbouring jobs. [[data-engineering/index|Data engineers]] build the systems that collect and store the data. [[ai-ml/01-data-scientist/index|Data scientists]] build statistical models and run careful experiments. Analysts turn the stored data into decisions.

## What you'll be able to do

By the end you will be able to:
- turn a vague request into a clear question tied to a decision;
- write the SQL analysts use every day, including running totals and comparisons across groups;
- choose what's worth measuring, and spot numbers that look good but mean nothing;
- find out why a number changed, step by step;
- analyse how customers move through a sign-up process and how many keep coming back;
- tell a real change apart from the normal ups and downs of the week or season;
- build a useful dashboard, and present findings so people act on them.

## Where to start

**Before you start:** you should be able to write basic SQL; [[databases/00-your-first-sql|Your First SQL Queries]] teaches it.

Read in order. Note 01 sets the frame, note 02 is the main skill, and notes 04 and 05 are the daily job.

1. [[data-analysis/01-what-data-analysis-is|What Data Analysis Is]]: how analysts differ from engineers and scientists, the steps of an analysis, and why the result is a decision, not a number.
2. [[data-analysis/02-sql-for-analysis|SQL for Analysis]]: the SQL analysts rely on: window functions (calculations across related rows, like running totals) and named sub-queries, plus common patterns and traps.
3. [[data-analysis/03-metrics-and-kpis|Metrics and KPIs]]: choosing what to measure, numbers that predict versus numbers that report, and why a number stops being useful once people are judged on it.
4. [[data-analysis/04-exploratory-and-diagnostic-analysis|Exploratory and Diagnostic Analysis]]: checking you can trust a dataset, and a step-by-step method for "why did this number change?".
5. [[data-analysis/05-product-and-business-analytics|Product and Business Analytics]]: the analyses that are the job: where people drop out of a process, how many come back, and whether each customer earns more than they cost to win.
6. [[data-analysis/06-time-series-analysis|Time Series Analysis]]: data over time: separating the long-term trend, regular seasonal patterns and random noise, and simple forecasts.
7. [[data-analysis/07-dashboards-and-bi|Dashboards and BI]]: dashboard tools, keeping one agreed definition of every number, and why most dashboards go unused.
8. [[data-analysis/08-communicating-analysis|Communicating Analysis]]: the half of the job that isn't technical: lead with the answer, say why it matters, and turn findings into action.

## Practice

- [[data-analysis/09-practice-exercises|Practice Exercises]]: twelve drills, mostly the SQL questions interviews use, plus a full "why did this change?" investigation and a one-page write-up.
- [[data-analysis/10-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- [[data-analysis/projects|Projects]]: hands-on tasks with a clear "done when". Start by investigating a real change in a public dataset.
- [[data-analysis/interview/index|Data analysis interview prep]]: the SQL test, defining a metric, investigating a drop, and the standard product questions.

## Key ideas to remember

1. **The result is a decision.** Start from "what would we do differently?", not from the data. → [[data-analysis/01-what-data-analysis-is|01]]
2. **Learn window functions.** They're the line between pulling data out of a database and analysing it. → [[data-analysis/02-sql-for-analysis|02]]
3. **Most "the number changed!" alarms are just the season or the day of the week.** Compare like with like before investigating. → [[data-analysis/06-time-series-analysis|06]]
4. **Lead with the answer** when you present, then the evidence. → [[data-analysis/08-communicating-analysis|08]]

## Related

- [[databases/index|Databases]]: the engine your SQL runs on.
- [[data-engineering/index|Data Engineering]]: the layer that collects and stores the data.
- [[ai-ml/01-data-scientist/index|Data Scientist]]: careful statistics, experiments, and telling cause from coincidence.
- [[ai-ml/01-data-scientist/05-data-visualization|Data Visualisation]]: choosing charts that don't mislead.
- [[ai-ml/00-foundations/04-python-and-data-tools/index|Python data tools]]: the analyst's second tool after SQL.

---

## About this course

- **Size:** 8 notes plus practice, written in September 2026. Before that, the vault covered building data systems and data science, but not the analyst work in between.
- **Where it came from:** reference sources. It links to the data scientist course for statistics, testing and cause-and-effect instead of repeating them.
