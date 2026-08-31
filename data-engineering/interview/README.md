# Data Engineering — Interview Prep

From the [[data-engineering/README|data engineering course]].

## Files
1. [[data-engineering/interview/01-the-data-engineering-round|The Data Engineering Round]] — fundamentals, data movement (CDC, Kafka), processing (Spark and when *not* to), practice (idempotency, dbt, dimensional modelling), and the stack-sizing judgement question. 🔥 marks what comes up constantly

## The scope note — read this first

**[[INTERVIEW|INTERVIEW.md]] states a principle this bank sits against:** *"an interview bank for a subject you haven't practised would be memorisation, not preparation."*

That holds, and this bank exists anyway — **written from the course, not from having sat these interviews, and honestly labelled.** A map of what the round asks, not a substitute for reps.

**What actually prepares you is a pipeline you built and operated** — because the questions that separate candidates (idempotency, backfills, stale-but-green failures) are ones you only internalise by having a re-run double-count your data → [[data-engineering/projects|data engineering projects]]. The end-to-end DuckDB + dbt mini-pipeline is a weekend and covers most of the fundamentals questions.

## What this round tests differently

**The practical questions are the filter.** Anyone can define ETL; the people who've built pipelines are the ones who immediately reach for CDC over watermark queries, insist on idempotency, and know that "the pipeline succeeded" doesn't mean "the data is right."

Two failure modes this bank is written against:

1. **Naming tools without understanding why they exist.** "We use Kafka and Spark and Airflow" is table stakes. *Why* columnar storage is fast, *why* CDC beats a watermark query, *why* idempotency is non-negotiable — that's the signal
2. **Over-engineering as a reflex.** A candidate who designs a ten-tool platform for every problem reads as someone who's read the blog posts, not run the systems. **The senior answer reaches for the simplest thing that works**

## Related
- [[data-engineering/README|the course]] · [[databases/interview/README|databases interview bank]]
- [[ai-ml/interview/README|ai-ml interview bank]] — the layer above
- [[INTERVIEW|Interview Prep Index]]
