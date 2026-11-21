---
id: 567c52f1-3a2c-4970-a4ba-a9188effcf5a
---

# Training From Scratch vs. Fine-Tuning

[[03-fine-tuning|Fine-tuning]] and [[03-transfer-learning|transfer learning]] both start from an existing pretrained model. This note is about the remaining question: when is it actually worth training an architecture completely from scratch — random initial weights, no pretrained starting point — instead?

## Why "from scratch" is the expensive, rare default
<!-- bite: e8d031e8-7712-45fc-9334-f90ebc1cbdd4 -->

Training from scratch means the model has to learn everything — including the broadly useful low-level patterns (edges, grammar, general world structure) that a pretrained model already has — using only your own dataset and compute budget. For almost any task where a relevant pretrained model exists, starting from scratch is strictly more expensive for typically worse results than fine-tuning or transfer learning, which is exactly why those are the default reach in [[ai-engineering/01-the-ai-engineer-role|choosing-the-right-ai-tool]] and throughout the rest of this vault's practical notes.

## When training from scratch is actually justified
<!-- bite: 9e965d6e-75be-425d-ba03-c4b148fe42db -->

- **No relevant pretrained model exists** — a genuinely novel data modality or domain where nothing resembling your data was in any available pretrained model's training set (a highly specialized sensor format, for instance).
- **Licensing or provenance requirements** — some applications require full knowledge and control of everything the model was trained on, which pretrained models (with opaque or restrictively licensed training data) can't satisfy.
- **The task is fundamentally different from anything pretraining covers** — not just a new domain, but a different *kind* of prediction problem than the architecture's pretraining objective was built around.
- **You have enough data and compute that the benefit of pretraining is genuinely marginal** — rare in practice; this threshold is usually far higher than it initially seems, especially for text and image tasks where strong pretrained models are abundant.

For the vast majority of applied projects, at least one of these doesn't hold, which is why fine-tuning/transfer learning is the practical default rather than a shortcut.

## What training from scratch actually requires beyond fine-tuning
<!-- bite: 3b470a13-3492-4750-b1d7-6d8466a4fe92 -->

Everything from [[01-designing-an-architecture|designing-an-architecture]] (there's no existing architecture to lean on, or an existing architecture is being used with genuinely random initial weights) plus a training dataset large enough to teach the model everything, not just specialize it — often orders of magnitude more data than a fine-tuning dataset needs, following directly from the "learning everything vs. adapting existing structure" distinction in [[03-fine-tuning|fine-tuning]].

## A middle ground — training from scratch on a smaller, well-understood architecture
<!-- bite: 473c98bd-f88d-4a80-9d44-7de73ac70489 -->

Not every from-scratch project needs to be frontier-model-scale. Training a small CNN from scratch (see [[01-cnns|cnns]]) on a moderately sized, domain-specific image dataset is a completely reasonable, common thing to do — "from scratch" doesn't inherently mean "as expensive as training a frontier LLM," it means "no pretrained starting point for this specific model," which is a much lower bar when the architecture and dataset are modest in scale.

## Gotchas
<!-- bite: 952e2f9b-5f15-441a-b522-e0c3e8404fab -->

- Assuming a custom problem "must" need training from scratch without first checking whether a pretrained model, prompted or fine-tuned appropriately, already handles it — this checking step (see [[ai-engineering/01-the-ai-engineer-role|choosing-the-right-ai-tool]]) should always come first, since it's far cheaper to disprove than to discover after an expensive training run.
- Underestimating how much data training from scratch actually requires relative to fine-tuning — a dataset that would fine-tune a model well can be wildly insufficient to train a comparable architecture from random initialization.

## Related
<!-- bite: 6c86b4ab-fb22-41c3-a4de-2aabac0119e6 -->
- [[01-designing-an-architecture|designing-an-architecture]]
- [[03-fine-tuning|fine-tuning]]
- [[ai-engineering/01-the-ai-engineer-role|choosing-the-right-ai-tool]]
