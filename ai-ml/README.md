# AI & ML

A map of this folder, in reading order, across three phases: get oriented first (what these systems are, the math underneath them, how to use what already exists), then go deeper into building things with code (data, training, computer vision), then get into designing and shipping your own models.

Tags mark roughly where each note sits on a Beginner → Advanced curve — the three phases already move in that direction at a coarse level; the tags add the same signal within each phase.

## Phase 1 — Orientation & foundations

**Foundations**
1. [[01-what-is-ai|what-is-ai]] — **[Beginner]** — AI vs ML vs deep learning, narrow vs general
2. [[02-what-is-a-model|what-is-a-model]] — **[Beginner]** — parameters, training vs inference, generalization

**Maths** (each of these three is deep enough to be its own folder of atomic notes, not one flat file)
3. [[ai-ml/02-maths/01-linear-algebra/README|linear-algebra/]] — **[Beginner → Intermediate]** — vectors, matrices, dot products — why weights and embeddings are what they are
4. [[ai-ml/02-maths/02-calculus/README|calculus/]] — **[Intermediate]** — derivatives, gradients, chain rule — why backpropagation works
5. [[ai-ml/02-maths/03-probability-and-statistics/README|probability-and-statistics/]] — **[Beginner → Intermediate]** — distributions, Bayes, why loss functions and LLM sampling look the way they do
6. [[04-optimization|optimization]] — **[Intermediate]** — gradient descent, learning rate, batches — how training actually runs

**Using what already exists**
7. [[03-llms|llms]] — **[Intermediate]** — tokens, context windows, transformers/attention, autoregressive generation
8. [[04-other-model-types|other-model-types]] — **[Beginner]** — classic ML, computer vision, diffusion, embeddings, speech, RL
9. [[05-open-source-models|open-source-models]] — **[Intermediate]** — Hugging Face, Ollama/llama.cpp, quantization, self-host vs API
10. [[06-agents|agents]] — **[Intermediate]** — the agentic loop, tool calling, MCP
11. [[07-prompting|prompting]] — **[Beginner]** — system vs user prompts, few-shot, chain-of-thought, failure modes
12. [[08-ai-tools-landscape|ai-tools-landscape]] — **[Beginner]** — the categories of AI products and where each one fits
13. [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]] — **[Intermediate]** — turning all of the above into an actual decision process

## Phase 2 — Building with code **[Intermediate]**

**ML engineering** ([[ai-ml/03-ml-engineering/README|ml-engineering/]]) — the general workflow: cleaning and splitting data, running a real PyTorch training loop, evaluating honestly, fine-tuning an existing model instead of starting from zero.

**Computer vision** ([[ai-ml/04-computer-vision/README|computer-vision/]]) — the same workflow specialized for images: CNNs, image data/augmentation, transfer learning.

## Phase 3 — Building your own models **[Advanced]**

[[ai-ml/05-building-your-own-models/README|building-your-own-models/]] — designing an architecture instead of reusing one, deciding when training from scratch is actually worth it over fine-tuning, and what happens after training: serving, monitoring for drift, versioning, retraining pipelines.

## Related
- [[foundations/dsa/README|DSA fundamentals]] — different domain, same "orientation → patterns/practice → build" approach
