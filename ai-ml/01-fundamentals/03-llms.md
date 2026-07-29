# LLMs (Large Language Models)

An LLM is a [[02-what-is-a-model|model]] trained on huge amounts of text to do one core thing: given a sequence of text so far, predict what comes next. Everything an LLM does — answering questions, writing code, holding a conversation — is this same next-token-prediction mechanism, applied repeatedly, dressed up by training and prompting to look like task completion.

## Tokens — the actual unit of input/output

LLMs don't see text as characters or whole words — they see **tokens**, chunks of text (often sub-word pieces) mapped to numbers via a fixed vocabulary. "Understanding" is a single token for common words; a rare word might be split into several tokens (`under` + `stand` + `ing`). This matters practically: API pricing and context limits are measured in tokens, not characters or words, and roughly 1 token ≈ 4 characters of English text as a rule of thumb.

```
"I love transformers" -> tokens: ["I", " love", " transform", "ers"]  (illustrative — actual splits vary by tokenizer)
```

## Context window — the model's working memory

The context window is the maximum number of tokens (input + output combined) the model can attend to at once. Anything outside that window simply doesn't exist to the model in that request — it's not "forgotten" in a human sense, it was never in view. This is why long conversations eventually need summarization or truncation, and why techniques like RAG (retrieval-augmented generation — fetching only the relevant snippet of a large document instead of feeding the whole thing) exist: to work around a fixed context window rather than needing an infinite one.

## Transformers and attention — the architecture, at a conceptual level

The transformer architecture (introduced in the 2017 paper "Attention Is All You Need") is what almost every modern LLM is built from. Its key idea is **self-attention**: for every token, the model computes how much every *other* token in the context should influence it, then blends their information accordingly. This is what lets a model correctly resolve something like "it" in "the trophy didn't fit in the suitcase because it was too big" — attention lets "it" pull information from "trophy" (or "suitcase," in the version where "big" flips the referent) based on learned patterns, rather than reading strictly left to right without context.

Mechanically, attention comes down to the [[03-dot-product|dot products]] covered in that note: each token is turned into vectors, and dot products between them measure how relevant each pair of tokens is to each other — the "attention weights" are just normalized versions of these dot products.

## Autoregressive generation — how output is actually produced

An LLM generates one token at a time: predict the most likely next token (or sample from the probability distribution over possible next tokens — see [[01-distributions|distributions]]), append it to the sequence, then repeat, feeding the whole sequence-so-far back in to predict the *next* next token. This is why LLMs stream output token by token, and why generation cost roughly scales with output length — each new token is a full pass through the model.

## Pretraining vs fine-tuning vs instruction-tuning (briefly)

- **Pretraining**: training on massive amounts of general text to learn language patterns broadly — this is the expensive, foundational phase.
- **Fine-tuning**: further training a pretrained model on a smaller, specific dataset to specialize it.
- **Instruction-tuning / RLHF**: additional training specifically to make the model follow instructions and prefer helpful, safe responses over just "statistically likely next text" — this is a large part of why a raw pretrained model feels very different from a chat-ready one like the assistant you're talking to right now.

## Why LLMs sometimes state wrong things confidently ("hallucination")

An LLM is fundamentally predicting plausible-sounding text, not looking up verified facts (unless it's explicitly given a tool to do so, like search or code execution — see [[06-agents|agents]]). When the training data doesn't clearly cover something, the model can still produce fluent, confident-sounding text that's simply wrong, because fluency and correctness are optimized somewhat separately during training. This isn't a bug that gets patched out entirely — it's a structural consequence of the underlying mechanism, which is why grounding an LLM's answers in retrieved, verifiable sources (RAG) or tool use matters for anything where correctness is critical.

## Gotchas

- "The model remembers our earlier conversation" is only true within the current context window of a single session — across separate sessions, there's no memory unless the product layer explicitly stores and re-feeds prior context.
- More parameters or a longer context window doesn't automatically mean a better answer to a specific question — task fit, prompt quality (see [[07-prompting|prompting]]), and whether the model has relevant training data all matter more for a given task than raw scale.

## Related
- [[02-what-is-a-model|what-is-a-model]]
- [[07-prompting|prompting]]
- [[06-agents|agents]]
- [[04-other-model-types|other-model-types]]
