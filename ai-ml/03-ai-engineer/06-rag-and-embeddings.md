# RAG & Embeddings

**Source:** new for the track, from the [roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer) RAG branch. RAG is the single most important applied-AI pattern after prompting — it's how you make an LLM answer from *your* data.

## Embeddings — meaning as vectors

An **embedding** is a [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/01-vectors|vector]] (a list of numbers) that captures the *meaning* of a piece of text (or image/audio), produced by an embedding model, such that **similar meanings produce nearby vectors**. "How do I reset my password?" and "I forgot my login" land close together even with no shared words.

Closeness is measured by **cosine similarity** (or [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot product]]) — the angle between vectors, not keyword overlap. This is **semantic search**: embed a query, find the nearest document vectors, and you've retrieved by meaning rather than exact match.

## Why RAG exists

An LLM only knows its training data and what's in the [[ai-ml/03-ai-engineer/02-how-llms-work|context window]]. It doesn't know your company's docs, and it [[ai-ml/03-ai-engineer/02-how-llms-work|hallucinates]] confidently when it doesn't know. **Retrieval-Augmented Generation (RAG)** fixes both: fetch the relevant slice of *your* data and put it in the prompt, so the model answers *from provided sources* instead of from memory. It's the standard cure for hallucination and the way to give a model private/current knowledge without training.

## The RAG pipeline

```
INDEXING (once, offline):
  documents → split into chunks → embed each chunk → store vectors in a vector DB

QUERYING (per request):
  user question → embed it → find nearest chunks (semantic search)
                → stuff those chunks into the prompt as context
                → LLM generates an answer grounded in them (often with citations)
```

Each stage has real decisions:

- **Chunking** — documents are split into passages small enough to embed and to fit several into a prompt. Too big → noisy, few fit; too small → context lost across the split. Chunk on semantic boundaries (paragraphs/sections) with some overlap so meaning isn't severed mid-thought. Chunking quality quietly determines RAG quality more than model choice does.
- **Indexing** — chunk vectors go into a vector database supporting fast nearest-neighbor search (approximate, at scale).
- **Retrieval** — embed the query, fetch the top-k nearest chunks. **Hybrid search** (combine semantic similarity with keyword/BM25) often beats pure vector search, catching exact terms (names, codes) that embeddings blur. A **reranker** can reorder retrieved candidates for relevance before they hit the prompt.
- **Generation** — the LLM answers using the retrieved chunks, ideally citing which chunk each claim came from so the answer is auditable.

## Vector databases

Purpose-built stores for embeddings + nearest-neighbor search:

| Option | Note |
|---|---|
| **pgvector** | a Postgres extension — vectors in the database you already run; the pragmatic default when you're already on Postgres/Supabase |
| **Pinecone** | managed, popular, scales without ops |
| **Chroma** | lightweight, developer-friendly, great for local/prototyping |
| **Qdrant / Weaviate / Milvus** | open-source, feature-rich, self-hostable |
| **FAISS** | a library (not a server) for in-process similarity search |

For most apps starting out, `pgvector` or a managed service is plenty — reach for a dedicated distributed store when scale demands it, the same "do you actually need it yet?" judgment as everywhere else.

## RAG vs fine-tuning — a key AI-engineer decision

Both specialize a model to your needs, differently:

| | RAG | Fine-tuning |
|---|---|---|
| Adds | *knowledge* (facts, docs) | *behavior/style/format* |
| Updates | instant — change the data, no retraining | requires retraining |
| Sources | can cite retrieved chunks | opaque, baked into weights |
| Best for | Q&A over changing/private knowledge | consistent tone, format, a narrow task |

Rule of thumb: **RAG for knowledge, fine-tuning for behavior** — and you can combine them. For "answer questions about our docs," RAG is almost always the right first move; reach for fine-tuning when you need the model to reliably *behave* a certain way, not to *know* new facts.

## Advanced RAG — where the real quality lives

The basic pipeline above gets you a demo. Production RAG is mostly a set of upgrades to *retrieval*, because retrieval quality — not the LLM — is what caps a RAG system. In rough order of payoff:

- **Chunking strategy is decision #1.** Beyond "split into passages": size chunks to your content (a few hundred tokens is a common start), split on **semantic boundaries** (paragraphs, sections, code blocks) not blind character counts, and add **overlap** so meaning isn't severed at a boundary. **Contextual retrieval** — prepend a one-line summary of the *document* to each chunk before embedding — fixes the classic failure where a chunk says "it increased 30%" with no idea what "it" is. Chunking quietly determines RAG quality more than model choice.
- **Query transformation** — the user's raw question is often a poor search query. Rewrite it: **query rewriting** (clean up a messy question), **multi-query** (generate several phrasings, retrieve for each, merge), and **HyDE** (Hypothetical Document Embeddings — have the LLM draft a *fake ideal answer* and embed *that* to search, since a hypothetical answer sits closer in vector space to the real passages than the question does).
- **Hybrid search** — combine semantic (vector) similarity with **keyword/BM25** search and fuse the rankings (e.g. reciprocal rank fusion). Vectors blur exact terms (names, codes, error IDs, acronyms); keyword search nails them. Hybrid reliably beats pure vector search in production.
- **Reranking** — retrieve a *generous* candidate set (say top-50) cheaply, then run a **cross-encoder reranker** that scores each candidate against the query far more accurately than the initial vector similarity, and keep the top few for the prompt. Retrieve wide, rerank precise. This is one of the highest-ROI additions.
- **GraphRAG** — when answers require connecting facts across documents ("how does X relate to Y?"), build a knowledge graph of entities/relationships and retrieve over *that* structure, not just isolated chunks. Heavier to build; shines on multi-hop questions plain chunk retrieval can't answer.
- **Agentic RAG** — let an [[ai-ml/03-ai-engineer/08-agents|agent]] drive retrieval: decide *whether* to search, reformulate the query, search again if the first results were thin, and reason over multiple retrieval rounds — instead of a single fixed fetch. More capable, more expensive/slower.

**And measure it.** Retrieval and generation are separately evaluable — context precision/recall for "did the right chunk come back?", faithfulness/answer-relevance for "did the model use it correctly?". Don't tune RAG by vibes; see [[ai-ml/03-ai-engineer/12-evals|evals]] (the RAG-evaluation section). Reach for these upgrades in response to *measured* failures — start simple, add the piece that fixes the retrieval miss you actually observe.

## Gotchas

- **RAG is only as good as its retrieval** — if the right chunk isn't retrieved, the model can't use it, and may hallucinate instead. Debug retrieval (what got fetched?) before blaming the model.
- **Garbage chunks → garbage answers** — messy source data and bad chunking are the usual culprits behind a disappointing RAG system, not the LLM.
- **More retrieved context isn't always better** — irrelevant chunks dilute attention and cost tokens; precise retrieval beats dumping everything in.

## Related
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — embedding models as a model type
- [[ai-ml/03-ai-engineer/05-prompt-engineering|Prompt Engineering]] — context engineering, the broader discipline RAG feeds
- [[ai-ml/03-ai-engineer/12-evals|Evals]] — evaluating retrieval vs. generation separately
- [[ai-ml/03-ai-engineer/08-agents|Agents]] — agentic RAG, where the model drives retrieval
- [[ai-ml/03-ai-engineer/15-fine-tuning-applied|Fine-Tuning (Applied)]] — the other side of the RAG-vs-fine-tuning decision
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|Dot Product]] — the similarity math underneath
