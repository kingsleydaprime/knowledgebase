---
id: 08b1c504-8983-4b26-ab48-b2960723afa1
---

# Transformers & Attention

## The core idea: attention
<!-- bite: d7c31ee8-7b9f-4c9b-8739-98caf5bb6e7e -->

The 2017 paper "Attention Is All You Need" replaced recurrence entirely with **self-attention**. Instead of carrying a hidden state step by step ([[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/01-rnns-lstms-grus|RNNs]]), a transformer looks at the **whole sequence at once** and, for each element, computes how much every *other* element should influence it.

Mechanically, each token is projected into three vectors — a **query**, a **key**, and a **value**. Attention scores how well a token's query matches every other token's key (via [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot products]]), normalizes those scores into weights (softmax), and produces a weighted blend of the values:

```
attention(Q, K, V) = softmax( Q·Kᵀ / √d ) · V
```

That's the whole mechanism: **"for each token, gather information from the tokens most relevant to it."** It's what lets a model resolve "it" to the right noun, or connect a verb to a subject 40 words back — any two positions interact *directly*, no matter the distance.

## Multi-head attention
<!-- bite: 70b73111-49d5-4d5c-bb0b-fa955f5e0611 -->

One attention computation captures one kind of relationship. **Multi-head attention** runs several in parallel, each learning to attend to different aspects (syntax, coreference, topic), then combines them. More heads = more relationship types the model can track at once.

## The full transformer block
<!-- bite: 1c169d28-3f4a-4aa2-9176-a1234aa2b5f6 -->

Stack these pieces into a block, then stack many blocks:

- **Self-attention** — mix information across positions (above).
- **Feed-forward network** — an [[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|MLP]] applied to each position, for per-token processing.
- **Residual connections + layer normalization** — let gradients flow through many layers, making very deep stacks trainable.
- **Positional encoding** — since attention has no inherent notion of order (it sees a *set*, not a sequence), position information is added to the inputs so the model knows word order.

## Why transformers won
<!-- bite: 87dbcaaa-23ff-4aed-9416-6c17fc449bf1 -->

- **Parallelism** — the whole sequence is processed at once, not step by step, so training uses GPUs fully (the [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/01-rnns-lstms-grus|RNN bottleneck]]).
- **Long-range dependencies** — any two positions connect directly; no decay over distance.
- **Scale** — they keep improving with more data and parameters, which (with [[ai-ml/02-ml-engineer/01-foundations-of-ml/01-what-is-ml-and-types|self-supervised]] pretraining on internet-scale text) is exactly what produced LLMs.

The one cost: attention is **O(n²)** in sequence length (every token attends to every other), which is why context windows have limits and why efficient-attention variants (FlashAttention, sparse/linear attention) are active work.

## The families
<!-- bite: c19451a2-7cdd-4d49-a493-36957b214247 -->

- **Encoder-only** (BERT) — bidirectional, good for understanding/classification/embeddings.
- **Decoder-only** (GPT, most LLMs) — autoregressive next-token prediction, good for generation ([[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]]).
- **Encoder-decoder** (T5, original translation model) — for sequence-to-sequence tasks.

Transformers also crossed over into [[ai-ml/02-ml-engineer/06-computer-vision/index|vision]] (Vision Transformers) and other modalities — the architecture generalized far beyond text.

## Related
<!-- bite: cb0be1f0-fb23-4bde-8f73-5350c94ee044 -->
- [[ai-ml/03-ai-engineer/02-how-llms-work/index|How LLMs Work]] — the applied view of what these enable
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/01-rnns-lstms-grus|RNNs/LSTMs]] — what transformers replaced
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|Dot Product]] — the similarity operation attention is built on
- [[build-your-own-shit/24-your-own-llm|Your Own LLM]] — **this note as running code**: attention built up in four stages, then blocks, training and sampling

## About this lesson
<!-- bite: b89084fa-e94e-4cfd-aacc-0e232064e889 -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. The architecture behind every modern LLM ([[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]] is the applied view; this is the modeling view).
