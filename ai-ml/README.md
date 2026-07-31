# AI & ML

This domain is organized around a distinction that matters for how you actually learn and work: **"AI/ML" is three different career paths, not one.** roadmap.sh treats them as separate roadmaps (and even has explicit `ml-engineer-vs-ai-engineer` nodes) — so this domain is split the same way, over a shared foundation.

## The three paths — and how they differ

| Path | Core question | Deliverable | Builds/trains models? |
|---|---|---|---|
| **[[ai-ml/01-data-scientist/README\|Data Scientist]]** | "what does the data tell us?" | an answer, analysis, or insight (often a notebook + report) | sometimes — usually classical ML, interpreted |
| **[[ai-ml/02-ml-engineer/README\|ML Engineer]]** | "how do we build and ship a model that works in production?" | a trained model running reliably as software | **yes** — trains models, then operationalizes them (MLOps) |
| **[[ai-ml/03-ai-engineer/README\|AI Engineer]]** | "how do we build a product on top of existing models?" | an application using pre-trained models (LLMs) via APIs | **no** — uses pre-trained models; RAG/prompting/agents, not training |

The sharpest line is between **ML Engineer** (trains models, needs the math and the algorithm zoo) and **AI Engineer** (uses someone else's trained models, needs prompting/RAG/agents/APIs). The Data Scientist sits closer to the ML Engineer on the math/stats side but optimizes for *insight* over *shipping software*. Many real jobs blend two of these — the split is about emphasis, not walls.

## Shared foundation

- [[ai-ml/00-foundations/README|00-foundations/]] — the common ground: **core concepts** (what AI/a model is) and **[[ai-ml/00-foundations/03-mathematics/README|mathematics]]** (linear algebra, calculus, probability/statistics, optimization). The Data Scientist and ML Engineer paths lean on this heavily; the AI Engineer path needs far less of it.

## The three tracks

1. [[ai-ml/01-data-scientist/README|01-data-scientist/]] — **[skeleton]** — statistics, EDA, experimentation, econometrics, classical ML for insight. The emptiest track; to be built out.
2. [[ai-ml/02-ml-engineer/README|02-ml-engineer/]] — **[Intermediate → Advanced]** — the ML workflow, deep learning, computer vision, building your own models, and (to come) the algorithm zoo, RL, NLP, and MLOps. The most-built track — its current content was re-homed here from the old flat structure.
3. [[ai-ml/03-ai-engineer/README|03-ai-engineer/]] — **[Beginner → Advanced]** — the applied-LLM track: how LLMs work, the model landscape, calling models (APIs/SDKs), prompt engineering, RAG & embeddings, tools & MCP, agents, multimodal, and safety. **The deep-built track** — it matches the applied AI work (AI SDK, MCP, agents) done elsewhere in these projects.

## Where the content comes from

Restructured (2026-07-31) by cross-referencing against roadmap.sh's `ai-data-scientist`, `machine-learning`, `mlops`, and `ai-engineer` roadmaps. The old single linear course ("fundamentals → maths → ml-engineering → CV → build your own") conflated all three paths; its content was re-homed into the path it actually belonged to, nothing dropped. The AI Engineer track was built out deeply this pass (folding in the old `01-fundamentals/` notes + roadmap gaps); Data Scientist and ML Engineer keep their existing content with gaps documented for later passes.

## Related
- [[foundations/dsa/README|DSA fundamentals]] — different domain, same "orientation → build" approach
- [[devops/README|DevOps]] — the MLOps half of the ML Engineer path cross-links here
- [[ai-automation/README|ai-automation/]] — the no-code/automation-tooling angle on applied AI
