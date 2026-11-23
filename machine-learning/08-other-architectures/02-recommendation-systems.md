---
id: 09576e26-78b2-466a-a884-7d0482669284
---

# Recommendation Systems

A recommendation system guesses what a person will want next.

## What a recommendation system is
<!-- bite: b84f779f-387f-4c48-b2d5-0f9d5ba77fcd -->

A recommendation system is software that guesses which items a person will want next, out of a huge catalogue. It uses what you and people like you have watched, bought or liked. The "recommended for you" lists on Netflix, YouTube, Spotify and Jumia are all recommendation systems.

Next: the problem it solves, then the two main approaches.

## The problem
<!-- bite: f5283a55-3935-4bdd-951d-11689a3b7602 -->

Given a user and a catalog of items (products, videos, songs), predict which items the user will want. The scale is huge (millions of users × items) and the data is sparse (each user has interacted with a tiny fraction of items).

## Collaborative filtering — "users like you also liked"
<!-- bite: 65f3806a-5390-49ae-b5df-ea56ad3ee6f9 -->

The classic approach uses only the **interaction matrix** (who interacted with what), no knowledge of the items themselves:

- **User-based** — find users similar to you, recommend what they liked.
- **Item-based** — find items similar to ones you liked (similarity measured by *who* liked them, not their content).

The scalable version is **matrix factorization**: decompose the sparse user×item matrix into learned **embeddings** — a vector for each user and each item — such that a user's predicted rating for an item is the [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot product]] of their vectors. Users and items that "go together" end up with aligned vectors. This is the same [[machine-learning/07-sequence-models-and-nlp/03-nlp-and-embeddings|embedding]] idea as everywhere else: represent things as vectors so similarity is geometry.

## Content-based filtering — "similar to what you liked"
<!-- bite: 7ef1f7f6-053e-4ef2-8f5d-87ea15a764ec -->

Recommend items whose *features* resemble items the user liked (genre, tags, text description embeddings). Doesn't need other users' data — good when you have rich item metadata.

## The cold-start problem
<!-- bite: 735923e1-24b5-4092-8c2b-50f0fd2798c7 -->

The defining challenge: a **new user** has no interaction history, and a **new item** has no interactions, so collaborative filtering has nothing to work with. Fixes: fall back to content-based (uses item features), use popularity as a default, or ask for initial preferences. Real systems are **hybrid** — blending collaborative + content-based to cover each other's weaknesses.

## Modern approaches
<!-- bite: b08dc06c-b355-4db0-9a88-4bed5a984647 -->

Production recommenders (YouTube, Netflix, TikTok) use **deep learning**: neural networks that learn user and item embeddings from many signals (watch time, context, sequence of recent actions), often a two-stage *candidate generation → ranking* pipeline. **Sequence models** ([[machine-learning/07-sequence-models-and-nlp/index|transformers]]) increasingly model the *order* of a user's actions to predict the next one.

## The feedback-loop caveat
<!-- bite: 77b5405f-7961-4817-b4fd-45a17e9f0ad5 -->

A subtle, important issue: recommenders **shape the behavior they then learn from**. Recommending an item makes it more likely to be clicked, which reinforces recommending it — creating filter bubbles and popularity bias, and making offline [[machine-learning/04-model-evaluation/index|evaluation]] deceptive (you only observe outcomes for items you *chose* to show). This is a real [[machine-learning/10-mlops/index|MLOps]]/monitoring concern, and a reason [[machine-learning/10-mlops/04-serving-and-monitoring|A/B testing on live traffic]] matters more here than offline metrics.

## Related
<!-- bite: bfc2e49b-efed-4c77-86dc-92aff435fbea -->
- [[machine-learning/07-sequence-models-and-nlp/03-nlp-and-embeddings|NLP & Embeddings]] — the embedding idea recommenders rely on
- [[ai-engineering/06-rag-and-embeddings/index|RAG & Embeddings]] — the same similarity-search machinery, applied
- [[machine-learning/10-mlops/04-serving-and-monitoring|Serving & Operations]] — A/B testing and feedback loops

## About this lesson
<!-- bite: 469b37ef-c617-452e-8b8f-aa89c92fe2f5 -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. One of the highest-business-value ML applications — the engine behind "recommended for you," feeds, and product suggestions.
