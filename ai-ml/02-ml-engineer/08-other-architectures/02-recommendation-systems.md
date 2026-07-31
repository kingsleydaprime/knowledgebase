# Recommendation Systems

**[reference]** — from the roadmap.sh `machine-learning` roadmap. One of the highest-business-value ML applications — the engine behind "recommended for you," feeds, and product suggestions.

## The problem

Given a user and a catalog of items (products, videos, songs), predict which items the user will want. The scale is huge (millions of users × items) and the data is sparse (each user has interacted with a tiny fraction of items).

## Collaborative filtering — "users like you also liked"

The classic approach uses only the **interaction matrix** (who interacted with what), no knowledge of the items themselves:

- **User-based** — find users similar to you, recommend what they liked.
- **Item-based** — find items similar to ones you liked (similarity measured by *who* liked them, not their content).

The scalable version is **matrix factorization**: decompose the sparse user×item matrix into learned **embeddings** — a vector for each user and each item — such that a user's predicted rating for an item is the [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot product]] of their vectors. Users and items that "go together" end up with aligned vectors. This is the same [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/03-nlp-and-embeddings|embedding]] idea as everywhere else: represent things as vectors so similarity is geometry.

## Content-based filtering — "similar to what you liked"

Recommend items whose *features* resemble items the user liked (genre, tags, text description embeddings). Doesn't need other users' data — good when you have rich item metadata.

## The cold-start problem

The defining challenge: a **new user** has no interaction history, and a **new item** has no interactions, so collaborative filtering has nothing to work with. Fixes: fall back to content-based (uses item features), use popularity as a default, or ask for initial preferences. Real systems are **hybrid** — blending collaborative + content-based to cover each other's weaknesses.

## Modern approaches

Production recommenders (YouTube, Netflix, TikTok) use **deep learning**: neural networks that learn user and item embeddings from many signals (watch time, context, sequence of recent actions), often a two-stage *candidate generation → ranking* pipeline. **Sequence models** ([[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/README|transformers]]) increasingly model the *order* of a user's actions to predict the next one.

## The feedback-loop caveat

A subtle, important issue: recommenders **shape the behavior they then learn from**. Recommending an item makes it more likely to be clicked, which reinforces recommending it — creating filter bubbles and popularity bias, and making offline [[ai-ml/02-ml-engineer/04-model-evaluation/README|evaluation]] deceptive (you only observe outcomes for items you *chose* to show). This is a real [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]]/monitoring concern, and a reason [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|A/B testing on live traffic]] matters more here than offline metrics.

## Related
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/03-nlp-and-embeddings|NLP & Embeddings]] — the embedding idea recommenders rely on
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — the same similarity-search machinery, applied
- [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|Serving & Operations]] — A/B testing and feedback loops
