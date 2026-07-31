# How LLMs Work

**Source:** re-homed from the old `01-fundamentals/03-llms.md`, deepened with the sampling/decoding parameters ([roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer): tokens, temperature, top-k/top-p, penalties) that an AI engineer actually sets in every API call.

An LLM is a [[ai-ml/00-foundations/02-what-is-a-model|model]] trained on huge amounts of text to do one thing: given the text so far, predict the next token. Everything it does — answering, coding, conversing — is that single next-token-prediction mechanism applied repeatedly. Understanding this is what lets you reason about *why* it behaves as it does instead of treating it as magic.

## Tokens — the unit of everything

LLMs don't see characters or words; they see **tokens** — chunks of text (often sub-word) mapped to numbers via a fixed vocabulary. A common word is one token; a rare word splits into several (`under` + `stand` + `ing`).

```
"I love transformers" → ["I", " love", " transform", "ers"]   (splits vary by tokenizer)
```

This is not trivia — **tokens are the unit of pricing and of context limits**, and roughly 1 token ≈ 4 characters of English. Every cost estimate and context-budget decision you make is in tokens.

## Context window — the working memory

The **context window** is the max tokens (input + output combined) the model can attend to at once. Anything outside it doesn't exist to the model for that request — not "forgotten," never in view. This is why long conversations need summarization/truncation, and why [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]] exists: to feed only the relevant slice of a large corpus instead of needing an infinite window. Modern context windows are large (hundreds of thousands of tokens) but not free — more context means more cost and, past a point, degraded attention to any single detail ("lost in the middle").

## Transformers and attention

Almost every modern LLM is a **transformer** (2017, "Attention Is All You Need"). Its key mechanism is **self-attention**: for each token, the model computes how much every *other* token should influence it, then blends their information. This is what resolves "it" in "the trophy didn't fit in the suitcase because it was too big" — attention lets "it" pull from "trophy" based on learned patterns rather than reading strictly left to right. Mechanically it's [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot products]] between token vectors, normalized into attention weights.

## Autoregressive generation

An LLM generates **one token at a time**: predict a probability distribution over the next token, pick one, append it, feed the whole sequence back, repeat. This is why output streams token by token, and why generation cost scales with output length — each token is a full forward pass.

## The decoding knobs you actually control

Because generation *samples* from a probability distribution, the API exposes parameters that shape that sampling — the AI engineer's direct control surface:

| Parameter | What it does |
|---|---|
| **temperature** | scales randomness. `0` ≈ deterministic (always the most likely token) → good for extraction/classification; higher (`0.7–1.0`) → more varied/creative, more risk of drift |
| **top-p (nucleus)** | sample only from the smallest set of tokens whose probabilities sum to `p` (e.g. `0.9`) — a dynamic cutoff |
| **top-k** | sample only from the `k` most likely tokens — a fixed cutoff |
| **max tokens** | hard cap on output length (and cost) |
| **frequency / presence penalty** | discourage repeating tokens (frequency) or reusing already-seen tokens at all (presence) — reduce repetition/looping |
| **stop sequences** | strings that halt generation when produced |

The single most useful instinct: **lower temperature for anything where you want one correct, consistent answer** (structured output, classification, extraction); raise it for brainstorming/creative variation. Inconsistent output across runs is expected sampling behavior, not a bug — lower temperature (or a fixed seed, where supported) to tighten it.

## Pretraining vs fine-tuning vs instruction-tuning

- **Pretraining** — training on massive general text to learn language broadly. The expensive, foundational phase.
- **Fine-tuning** — further training a pretrained model on a smaller, specific dataset to specialize it ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG vs fine-tuning]] is a key AI-engineer decision).
- **Instruction-tuning / RLHF** — additional training to make the model follow instructions and prefer helpful, safe responses over merely "statistically likely" text. This is why a chat model feels so different from a raw pretrained one.

## Why LLMs confidently state wrong things ("hallucination")

An LLM predicts *plausible* text, not *verified* facts (unless given a tool like search — see [[ai-ml/03-ai-engineer/08-agents|agents]]). When training data doesn't clearly cover something, it still produces fluent, confident, wrong text — because fluency and correctness are optimized somewhat separately. **This is structural, not a bug that gets patched out**, which is exactly why grounding answers in retrieved sources ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]]) or tools matters for anything correctness-critical, and why [[ai-ml/03-ai-engineer/10-safety-and-production|evals and guardrails]] exist.

## Gotchas

- "The model remembers our earlier conversation" is only true within one context window — across separate sessions there's no memory unless the product explicitly stores and re-feeds it (see [[ai-ml/03-ai-engineer/08-agents|agent memory]]).
- More parameters or a longer context doesn't automatically mean a better answer — task fit, [[ai-ml/03-ai-engineer/05-prompt-engineering|prompt quality]], and whether the model has the relevant knowledge matter more for a given task than raw scale.

## Related
- [[ai-ml/00-foundations/02-what-is-a-model|What is a Model]] — the general "adjustable function" this specializes
- [[ai-ml/03-ai-engineer/05-prompt-engineering|Prompt Engineering]] — shaping the input to this mechanism
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — where you set these parameters in practice
