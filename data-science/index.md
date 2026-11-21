# Data Science

## What data science is

**Data science is using data, statistics and simple models to answer real questions, so people can make better decisions.** A data scientist asks a question, explores the data, runs experiments, and explains what the answer is and how sure we can be.

This subject is about **extracting insight and drawing sound conclusions from data** — framing questions, exploring and understanding data, running experiments, and using statistics and models to answer questions that inform decisions. Where the [[machine-learning/index|ML Engineer]] ships a model as software and the [[ai-engineering/index|AI Engineer]] builds on pre-trained models, the Data Scientist's deliverable is usually an *answer, a recommendation, or a communicated finding*. The maths it stands on is in [[machine-learning/00-foundations/index|Machine Learning's foundations]], and so is the Python data stack (NumPy, pandas).

## What this track covers (and what it borrows)

roadmap.sh's [`ai-data-scientist`](https://roadmap.sh/ai-data-scientist) roadmap is deliberately high-level, and much of it — machine learning, deep learning, MLOps, mathematics — is already built in the [[machine-learning/index|ML Engineer track]] and [[machine-learning/00-foundations/index|foundations]]. So this track focuses on the **distinctive DS pillars** (statistics, EDA, visualization, experimentation, causal inference) and cross-links the shared modeling rather than duplicating it.

## Three subjects, three jobs

Data science, machine learning and AI engineering used to be one subject called "AI & ML". They are three jobs that share some basics, so each is its own subject now.

| Subject | The question it answers | What you produce | Do you train models? |
|---|---|---|---|
| [[data-science/index\|Data Science]] | "What does the data tell us?" | an answer or insight, often a report | sometimes, mostly simpler models |
| [[machine-learning/index\|Machine Learning]] | "How do we build a model and run it reliably in a real product?" | a trained model running as software | **yes** |
| [[ai-engineering/index\|AI Engineering]] | "How do we build a product on top of models others have trained?" | an app that uses models like Claude or GPT | **no**, you use existing ones |

## Reading order

1. [[data-science/01-the-data-scientist-role|The Data Scientist Role]] — **[Beginner]** — DS vs ML engineer vs analyst, the analytics spectrum (descriptive→prescriptive), the DS workflow, and why communication is half the job
2. [[data-science/02-descriptive-statistics|Descriptive Statistics]] — **[Beginner → Intermediate]** — central tendency, dispersion, distribution shape, and correlation — summarizing data honestly
3. [[data-science/03-inferential-statistics|Inferential Statistics]] — **[Intermediate]** — sampling, the CLT, confidence intervals, hypothesis testing, p-values, and the common tests
4. [[data-science/04-exploratory-data-analysis|Exploratory Data Analysis]] — **[Intermediate]** — the systematic "understand before you model" process
5. [[data-science/05-data-visualization|Data Visualization]] — **[Intermediate]** — choosing the right chart, the libraries and BI tools, and communicating without misleading
6. [[data-science/06-experimentation-and-ab-testing|Experimentation & A/B Testing]] — **[Intermediate → Advanced]** — designing experiments that give trustworthy answers
7. [[data-science/07-causal-inference-and-econometrics|Causal Inference & Econometrics]] — **[Advanced]** — correlation vs causation, confounders, regression for *inference*, and time series

## What it draws on elsewhere

- [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/index|Probability & Statistics (foundations)]] — the probability basis these build on
- [[machine-learning/02-working-with-data/index|Working with Data (ML-engineer)]] — cleaning/wrangling, shared with this path
- [[machine-learning/03-classical-ml/index|Classical ML (ML-engineer)]] — the models a data scientist uses, here for *insight* over deployment
- [[machine-learning/01-foundations-of-ml/02-the-ml-toolkit|The ML Toolkit]] — Python/pandas/scikit-learn (a data scientist also often uses **R** for statistics)

## Related
- [[machine-learning/index|Machine Learning]] · [[ai-engineering/index|AI Engineering]] — the two sibling subjects
- [[machine-learning/00-foundations/index|Foundations]] — the maths and Python tools this subject uses
- [[data-science/projects|Projects]]
