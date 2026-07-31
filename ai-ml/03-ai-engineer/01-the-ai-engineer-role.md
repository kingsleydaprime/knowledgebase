# The AI Engineer Role

**Source:** folds in the old `01-fundamentals/09-choosing-the-right-ai-tool.md` (the decision process below) and frames the track. The applied-AI work this maps to (AI SDK, MCP, agent-building) is where this track is genuinely grounded rather than reference.

## What an AI Engineer is (and isn't)

An **AI Engineer builds products on top of pre-trained models** — almost always LLMs — accessed through APIs or run locally. They do **not** train models from scratch or need the deep math the [[ai-ml/02-ml-engineer/README|ML Engineer]] does. Their toolkit is prompting, retrieval (RAG), tool/function calling, agents, and the surrounding production concerns (evals, cost, safety) — software engineering with a model as a component, not model research.

roadmap.sh draws the line explicitly (it has `ai-engineer-vs-ml-engineer` nodes on both roadmaps):

| | ML Engineer | AI Engineer |
|---|---|---|
| Works with | models they train | pre-trained models (someone else's) |
| Core skills | math, algorithms, training, MLOps | prompting, RAG, agents, APIs, product |
| Question | "how do I train a model that works?" | "how do I build a product with existing models?" |
| Math needed | a lot | conceptual understanding, not derivations |

If you're building a chatbot, a RAG system over your docs, an agent, or an LLM feature in an app, you're doing AI engineering. If you're training a fraud-detection model or fine-tuning a vision network, that's ML engineering.

## The paradigm shift

The reason this role exists as something distinct is recent: **pre-trained frontier models made "intelligence" an API call.** You no longer need a dataset, GPUs, and weeks of training to get a capable model — you send text to an endpoint and get capable text back. The engineering problem moved from *building the model* to *building reliably around a model you don't control* — one that's non-deterministic, occasionally wrong ([[ai-ml/03-ai-engineer/02-how-llms-work|hallucination]]), and priced per token. That's a genuinely different discipline from classical ML.

## Choosing the right tool — the decision process

The most common mistake is reaching for the flashiest option (a big general LLM) by default without checking whether something cheaper, simpler, or more reliable fits. A decision process:

### Step 1 — does this even need a model?

If the logic is well-understood and doesn't vary, a hand-written rule beats any model: cheaper, instant, predictable, debuggable, no training data. Reach for ML/AI only when the pattern is too complex, variable, or poorly-understood to hand-specify.

### Step 2 — what shape is the input/output?

This narrows the field fast (see [[ai-ml/00-foundations/02-what-is-a-model|what a model is]] and the wider model map in [[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]]):

| Input/output | Reach for |
|---|---|
| Structured/tabular data | classic ML (regression, gradient-boosted trees) — an [[ai-ml/02-ml-engineer/README|ML-engineer]] job |
| Free-form text in, text/answer out | an LLM |
| Images in, classification/detection out | a vision model |
| Text in, new image/audio out | a diffusion / generation model |
| "Find similar things" / semantic search | [[ai-ml/03-ai-engineer/06-rag-and-embeddings|embeddings]] |

### Step 3 — for language tasks, how much capability does it need?

- **Simple, narrow, high-volume** (classify a ticket, extract a field) → a small/cheap model, or even classic ML. Matters once volume makes per-request cost add up.
- **Complex reasoning, ambiguous, multi-step** → a larger frontier model earns its cost; small models degrade faster on genuinely hard reasoning.
- **Needs to act, not just answer** → this is an [[ai-ml/03-ai-engineer/08-agents|agent]] question (tools + a loop), not a "bigger model" question.
- **Needs to be current or cite sources** → grounding via [[ai-ml/03-ai-engineer/06-rag-and-embeddings|retrieval]] matters more than model size.

### Step 4 — hosted API or self-hosted open model?

Covered in [[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]] — short version: hosted API for best capability with no infra (the common default); self-hosted open model when privacy/offline is a hard requirement, volume makes per-token cost dominate, or you need to fine-tune on private data.

## The through-line

"Can an LLM technically do this?" is almost always yes — the real question is whether it's the *most appropriate* tool given cost, reliability, and latency. And don't reach for an [[ai-ml/03-ai-engineer/08-agents|agent]] when a single good [[ai-ml/03-ai-engineer/05-prompt-engineering|prompt]] would do; agents add latency, cost, and failure surface for the ability to take multiple steps — only worth it when the task needs them.

## Related
- [[ai-ml/00-foundations/01-what-is-ai|What is AI]] — the AI/ML/DL nesting this role sits inside
- [[ai-ml/02-ml-engineer/README|ML Engineer path]] — the "train the model" sibling
- [[ai-ml/03-ai-engineer/README|AI Engineer track map]]
