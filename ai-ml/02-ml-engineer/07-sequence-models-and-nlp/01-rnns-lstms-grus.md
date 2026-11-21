---
id: b226890c-5d71-4f48-80ae-bb8a3959a939
---

# RNNs, LSTMs & GRUs

RNNs, LSTMs and GRUs are kinds of neural network built to read data in order, one step at a time, while remembering what came before. Order matters in things like sentences, speech and stock prices: "dog bites man" is not the same as "man bites dog". These networks powered early phone keyboard suggestions and voice typing before transformers took over.

## Why sequences need special architectures
<!-- bite: 65da6871-16b2-4f87-bb2a-ae2683450321 -->

A plain [[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|MLP]] or [[ai-ml/02-ml-engineer/06-computer-vision/01-cnns|CNN]] takes a fixed-size input with no notion of order. But text, time series, speech, and DNA are **sequences** — variable length, and order matters ("dog bites man" ≠ "man bites dog"). Sequence models process elements one at a time while carrying information forward.

## Recurrent Neural Networks (RNNs)
<!-- bite: 3793fea9-833a-4dac-a034-241ca8923539 -->

An RNN processes a sequence step by step, maintaining a **hidden state** that acts as memory: at each step it combines the current input with the hidden state from the previous step to produce a new hidden state (and optionally an output). The same weights are reused at every step — the "recurrence."

```text
h₁ → h₂ → h₃ → h₄        (hidden state carried forward)
↑    ↑    ↑    ↑
x₁   x₂   x₃   x₄         (sequence elements in order)
```

This lets earlier context influence later predictions. Trained by **backpropagation through time** (unroll the sequence, then ordinary [[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|backprop]]).

## The problem: long-range memory
<!-- bite: ea8cf29e-f0b5-419d-a374-df4d1ebb54f0 -->

Plain RNNs fail on **long-range dependencies** because of vanishing/exploding gradients ([[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|vanishing gradients]]) — as information (and gradient) propagates across many steps, it decays away. So an RNN struggles to connect "The **cat**, which … [30 words] … , **was** hungry" — by the time it reaches "was," it's effectively forgotten "cat."

## LSTMs and GRUs — gating fixes memory
<!-- bite: 6d06e7bf-f273-4eb2-91f4-f6799d100c35 -->

**LSTM** (Long Short-Term Memory) adds a separate **cell state** — a memory highway — controlled by learned **gates** that decide what to forget, what to store, and what to output at each step. The gates let gradients flow across many steps without vanishing, so LSTMs capture much longer dependencies. **GRU** (Gated Recurrent Unit) is a streamlined version with fewer gates — often as good, faster to train.

```python
import torch.nn as nn
lstm = nn.LSTM(input_size=128, hidden_size=256, num_layers=2, batch_first=True)
```

For years, LSTMs were the state of the art for translation, speech recognition, and text generation.

## Why transformers replaced them
<!-- bite: d28849eb-4661-4b75-b48c-e62fbae09071 -->

RNNs/LSTMs have two structural limits transformers fixed:

- **Sequential = slow** — processing step by step can't be parallelized across the sequence during training (each step needs the previous one), wasting modern GPU parallelism.
- **Long-range still hard** — gating helps but very long dependencies remain difficult.

[[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers]] process the whole sequence *at once* via attention, are massively parallelizable, and connect any two positions directly regardless of distance — which is why they took over. RNNs/LSTMs still appear in resource-constrained or streaming settings and are foundational to understand, but transformers are the default for anything sequence-shaped now.

## Related
<!-- bite: a2d6bdf8-c566-4288-ac94-d3d12be3f3b4 -->
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers & Attention]] — what replaced these and why
- [[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|Neural Network Fundamentals]] — vanishing gradients, the core problem here
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/03-nlp-and-embeddings|NLP & Embeddings]] — how text becomes model input

## About this lesson
<!-- bite: 7dade1fa-b8b3-47b9-9fd5-e591acbe718e -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. The pre-transformer approach to sequences — still worth understanding, both historically and because the problems they solved explain *why* [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|transformers]] look the way they do.
