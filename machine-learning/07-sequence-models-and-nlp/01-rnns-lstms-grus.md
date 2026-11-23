---
id: b226890c-5d71-4f48-80ae-bb8a3959a939
---

# RNNs, LSTMs & GRUs

RNNs, LSTMs and GRUs read data in order, remembering what came before.

## What RNNs, LSTMs and GRUs are
<!-- bite: fd391935-0d0a-4060-a352-186c7b6d30a0 -->

RNNs, LSTMs and GRUs are kinds of neural network built to read data in order, one step at a time, while remembering what came before. Order matters in things like sentences, speech and stock prices: "dog bites man" is not the same as "man bites dog". These networks powered early phone keyboard suggestions and voice typing before transformers took over.

Next: why order needs a special kind of network.

## Why sequences need special architectures
<!-- bite: 65da6871-16b2-4f87-bb2a-ae2683450321 -->

A plain [[machine-learning/05-deep-learning/01-neural-network-fundamentals|MLP]] or [[machine-learning/06-computer-vision/01-cnns|CNN]] takes a fixed-size input with no notion of order. But text, time series, speech, and DNA are **sequences** — variable length, and order matters ("dog bites man" ≠ "man bites dog"). Sequence models process elements one at a time while carrying information forward.

## Recurrent Neural Networks (RNNs)
<!-- bite: 3793fea9-833a-4dac-a034-241ca8923539 -->

An RNN processes a sequence step by step, maintaining a **hidden state** that acts as memory: at each step it combines the current input with the hidden state from the previous step to produce a new hidden state (and optionally an output). The same weights are reused at every step — the "recurrence."

```text
h₁ → h₂ → h₃ → h₄        (hidden state carried forward)
↑    ↑    ↑    ↑
x₁   x₂   x₃   x₄         (sequence elements in order)
```

This lets earlier context influence later predictions. Trained by **backpropagation through time** (unroll the sequence, then ordinary [[machine-learning/05-deep-learning/01-neural-network-fundamentals|backprop]]).

## The problem: long-range memory
<!-- bite: ea8cf29e-f0b5-419d-a374-df4d1ebb54f0 -->

Plain RNNs fail on **long-range dependencies** because of vanishing/exploding gradients ([[machine-learning/05-deep-learning/01-neural-network-fundamentals|vanishing gradients]]) — as information (and gradient) propagates across many steps, it decays away. So an RNN struggles to connect "The **cat**, which … [30 words] … , **was** hungry" — by the time it reaches "was," it's effectively forgotten "cat."

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

[[machine-learning/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers]] process the whole sequence *at once* via attention, are massively parallelizable, and connect any two positions directly regardless of distance — which is why they took over. RNNs/LSTMs still appear in resource-constrained or streaming settings and are foundational to understand, but transformers are the default for anything sequence-shaped now.

## Check your understanding
<!-- bite: daeb6d1e-055a-4fe3-b76c-dcca5925cd62 -->

Try each one before you open the answer.

1. <!-- q: gap id="5c8ae016" answers="hidden state|hidden" -->
   Fill in the gap. An RNN carries memory from step to step in its ___, which combines the current input with the previous step's value.

   <details><summary>Answer</summary>

   The hidden state. The same weights are reused at every step, which is the "recurrence".

   </details>

2. <!-- q: mcq id="a54a18a6" -->
   Why do plain RNNs struggle to connect "The cat, which … [30 words] …, was hungry"?

   - [ ] They can't read long sentences at all
   - [x] Vanishing gradients: information from early steps decays away over many steps
   - [ ] They read the sentence backward

   <details><summary>Answer</summary>

   Vanishing gradients. By the time the RNN reaches "was", the signal from "cat" has effectively faded.

   </details>

3. <!-- q: mcq id="36e83471" -->
   What does an LSTM add to fix long-range memory?

   - [x] A separate cell state controlled by learned gates
   - [ ] More training data
   - [ ] Attention over the whole sequence

   <details><summary>Answer</summary>

   A cell state with gates that decide what to forget, store and output, so gradients can flow across many steps. Attention is the transformer's idea.

   </details>

4. <!-- q: mcq id="37999ab3" -->
   Which two limits of RNNs did transformers fix? Choose all that apply.

   - [x] Step-by-step processing can't be parallelized during training
   - [x] Very long dependencies are still hard
   - [ ] RNNs can't use GPUs at all

   <details><summary>Answer</summary>

   The first two. RNNs can run on GPUs, but each step waits for the one before, which wastes the GPU's parallelism.

   </details>

5. <!-- q: open id="9a7bb3f9" -->
   What is a GRU, and why might you pick it over an LSTM?

   <details><summary>Answer</summary>

   A GRU (Gated Recurrent Unit) is a streamlined LSTM with fewer gates. It is often just as good and faster to train.

   </details>

## Related
<!-- bite: a2d6bdf8-c566-4288-ac94-d3d12be3f3b4 -->
- [[machine-learning/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers & Attention]] — what replaced these and why
- [[machine-learning/05-deep-learning/01-neural-network-fundamentals|Neural Network Fundamentals]] — vanishing gradients, the core problem here
- [[machine-learning/07-sequence-models-and-nlp/03-nlp-and-embeddings|NLP & Embeddings]] — how text becomes model input

## About this lesson
<!-- bite: 7dade1fa-b8b3-47b9-9fd5-e591acbe718e -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. The pre-transformer approach to sequences — still worth understanding, both historically and because the problems they solved explain *why* [[machine-learning/07-sequence-models-and-nlp/02-transformers-and-attention|transformers]] look the way they do.
