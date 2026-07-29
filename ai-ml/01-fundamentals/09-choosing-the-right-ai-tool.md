# Choosing the Right AI Tool

The most common mistake in applying AI to a problem is reaching for the flashiest available option (usually a large general-purpose LLM) by default, without checking whether a cheaper, simpler, more reliable tool already fits. This note is a decision process, built directly on the earlier maps in this folder ([[01-what-is-ai|what-is-ai]], [[04-other-model-types|other-model-types]], [[08-ai-tools-landscape|ai-tools-landscape]]).

## Step 1 — does this even need to be learned from data?

If the logic is well-understood and doesn't actually vary across cases, a hand-written rule/algorithm beats any model: cheaper, instant, perfectly predictable, no training data needed, no risk of the wrong answer for reasons no one can debug. Reach for ML/AI specifically when the pattern is too complex, too variable, or too poorly understood to hand-specify — not by default.

## Step 2 — what shape is the input/output?

This narrows the field fast, straight from [[04-other-model-types|other-model-types]]:

| Input/output shape | Reach for |
|---|---|
| Structured/tabular data, clear numeric features | Classic ML (regression, gradient-boosted trees) |
| Free-form text in, text/answer out | An LLM |
| Images in, classification/detection out | A vision model (CNN/ViT) |
| Text/description in, new image/audio out | A diffusion model |
| "Find similar things" / semantic search | Embeddings |
| Sequential decisions with a reward signal | Reinforcement learning |

## Step 3 — for language-shaped tasks, how much capability does it actually need?

Not every text task needs the largest, most expensive model:

- **Simple, narrow, high-volume tasks** (classify this ticket into one of 5 categories, extract a phone number from text) — a small/cheap model, or even classic ML, is often plenty, and matters a lot once volume is high enough that cost per request adds up.
- **Complex reasoning, ambiguous instructions, multi-step problems** — a larger frontier model earns its cost here; smaller models degrade faster on genuinely hard reasoning than on simple pattern-matching.
- **Needs to act, not just answer** (edit files, run code, check its own work across steps) — this isn't a "bigger model" question, it's an [[06-agents|agent]] question — you need tool access and a loop, not just more capable text generation.
- **Needs to be current or cite a source** — grounding via retrieval/search (see [[08-ai-tools-landscape|ai-tools-landscape]]) matters more here than raw model size; even the best model can't know something outside its training data without being given it.

## Step 4 — hosted API or self-hosted open model?

Covered in full in [[05-open-source-models|open-source-models]] — short version: hosted API for best available capability with no infrastructure burden (the common default); self-hosted open model when data privacy/offline operation is a hard requirement, or volume is high enough that per-token cost dominates, or you need to fine-tune on private data.

## A worked example

"We want to automatically tag support tickets by category." Walking the steps: this is learnable from data (categories aren't perfectly rule-based) → text in, label out → likely high volume, so cost matters → this is a narrow, well-defined classification task, not open-ended reasoning. Conclusion: this is very plausibly a case for a small fine-tuned classifier (classic ML or a small LLM), not a frontier general-purpose model — reaching for the biggest available LLM here would work, but be needlessly expensive per request at any real volume.

## Gotchas

- "Can an LLM technically do this" is almost always yes — the actual question is whether it's the *most appropriate* tool given cost, reliability, and the shape of the task, not whether it's capable in principle.
- Don't reach for an agent when a single well-crafted prompt (see [[07-prompting|prompting]]) would do — agents add latency, cost, and failure surface for the added ability to take multiple steps/actions; only worth it when the task genuinely needs that.

## Related
- [[01-what-is-ai|what-is-ai]]
- [[04-other-model-types|other-model-types]]
- [[08-ai-tools-landscape|ai-tools-landscape]]
- [[05-open-source-models|open-source-models]]
- [[06-agents|agents]]
