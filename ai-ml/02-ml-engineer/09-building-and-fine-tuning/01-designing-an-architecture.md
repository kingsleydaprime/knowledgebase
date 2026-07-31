# Designing an Architecture

Everything so far in this vault has been about using an existing architecture — a pretrained LLM, a standard CNN. Designing your own means deciding the shape of the function itself (see [[ai-ml/00-foundations/02-what-is-a-model|what-is-a-model]]): how many layers, what type, how they connect — before any training happens at all. This is a genuinely different skill from using existing models well, and a much rarer one to actually need.

## Start from the data's structure, not from a blank page

The type of data almost always dictates the broad architecture family, echoing [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|choosing-the-right-ai-tool]] but one level more specific:
- Grid-structured data (images) → convolutional layers (see [[01-cnns|cnns]]) or vision transformers.
- Sequential data (text, time series, audio) → transformers (attention-based, see [[ai-ml/03-ai-engineer/02-how-llms-work|llms]]) or, for smaller-scale sequence tasks, recurrent architectures.
- Unordered, tabular data → plain fully-connected layers are often sufficient, or classic ML entirely (see [[ai-ml/03-ai-engineer/03-the-model-landscape|other-model-types]]) — a custom deep architecture is frequently the wrong tool here.
- Graph-structured data (molecules, social networks) → graph neural networks, a more specialized architecture family not covered elsewhere in this vault yet.

## Depth and width — the basic levers

- **Depth** (number of layers) — more depth lets the network represent more complex, hierarchical patterns (as seen in CNNs progressing from edges to objects, [[01-cnns|cnns]]), but increases training difficulty (vanishing/exploding gradients, see [[03-chain-rule|chain-rule]]) and compute cost.
- **Width** (size of each layer) — more width increases a layer's capacity to represent patterns at that stage, at a direct parameter-count and compute cost (see [[02-matrices|matrices]] for why layer shape determines parameter count).

There's no formula that hands you the right depth/width for a new problem — the practical approach is starting from an existing, well-tested architecture in the same general family and adjusting from there, rather than designing from first principles.

## Building blocks worth knowing by name

- **Residual/skip connections** — let a layer's input bypass straight to a later layer in addition to going through the normal path, directly counteracting the vanishing-gradient problem in very deep networks by giving gradients a shorter path back during backpropagation.
- **Normalization layers** (batch norm, layer norm) — rescale activations partway through the network, stabilizing training and often allowing higher learning rates than would otherwise be usable.
- **Attention** (see [[ai-ml/03-ai-engineer/02-how-llms-work|llms]]) — lets a layer weigh how much every part of its input should influence every other part, rather than only processing local neighborhoods (convolution) or a fixed sequential order (older recurrent architectures).

Most modern successful architectures are combinations of these well-understood building blocks arranged for a specific data shape, rather than a wholly novel mechanism invented from scratch — genuinely new building blocks are rare, research-level contributions.

## Prototyping small before scaling up

Test a new architecture idea on a small version of the real problem first — fewer layers, a smaller dataset subset, fewer training steps — to catch basic bugs (shape mismatches, a loss that won't decrease at all) cheaply, before committing to a full-scale, expensive training run. A architecture that can't overfit a tiny handful of examples almost certainly has a bug, not a genuine capacity limitation — that's a useful, cheap sanity check before scaling up.

## Gotchas

- A model too small to represent the underlying pattern at all will underfit no matter how it's trained (see [[ai-ml/02-ml-engineer/04-model-evaluation/02-overfitting-and-regularization|overfitting-and-regularization]]) — increasing depth/width is diagnostic here, not just a performance knob.
- Designing an elaborate, novel architecture before confirming a much simpler, standard one genuinely fails on your problem is a common overengineering trap — always establish a simple baseline first.

## Related
- [[ai-ml/00-foundations/02-what-is-a-model|what-is-a-model]]
- [[02-training-from-scratch-vs-fine-tuning|training-from-scratch-vs-fine-tuning]]
- [[02-matrices|matrices]]
