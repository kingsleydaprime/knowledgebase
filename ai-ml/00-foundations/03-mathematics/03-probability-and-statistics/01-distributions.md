# Probability Distributions

A probability distribution assigns a likelihood to every possible outcome of some random process. Almost nothing a model outputs is a single certain answer — it's a distribution over possibilities — so this is the vocabulary for talking about that precisely.

## The normal (Gaussian) distribution

The one that shows up constantly in ML — the familiar bell curve, where outcomes cluster around a mean and become rarer the further out you go.

```
       ___
      /   \
     /     \
____/       \____
    mean
```

Model weights are frequently **initialized** by sampling from a normal distribution before training even starts (see [[04-optimization|optimization]]) — starting from small random values distributed this way, rather than all zeros or an arbitrary pattern, turns out to make training behave far better in practice. Many statistical assumptions baked into ML methods (errors being roughly normal, for instance) trace back to this distribution's convenient mathematical properties.

## Discrete vs continuous distributions

- **Discrete**: outcomes are countable/distinct — the result of a dice roll, which of several classes an image belongs to. A model's classification output ("80% cat, 15% dog, 5% other") is a discrete probability distribution over class labels.
- **Continuous**: outcomes form a continuum — a person's height, a predicted house price. The normal distribution above is a continuous distribution.

This distinction matters directly for what a model's final layer looks like: a classifier's output layer is built to produce a discrete distribution over classes (summing to 1), while a regression model's output is a single continuous value, sometimes accompanied by an estimate of uncertainty around it.

## Where distributions show up in an LLM specifically

Every token an LLM generates comes from a probability distribution over its entire vocabulary — given everything so far, the model computes how likely each possible next token is. A **sampling strategy** then picks one: greedy (always the most likely), top-k (sample from the k most likely), or temperature-based (a setting that flattens or sharpens the distribution before sampling). This is why the same prompt can produce different output across runs, and why "temperature" changes how random vs. predictable a model's output feels — it's literally reshaping this distribution before a token gets drawn from it (see [[ai-ml/03-ai-engineer/02-how-llms-work|llms]] for the generation mechanism this plugs into).

## Gotchas

- A model reporting a confidence score is reporting where its *own* output distribution places its mass — that's a genuinely different thing from the model being right that percentage of the time in reality (see the calibration gotcha in [[02-expectation-and-variance|expectation-and-variance]] / [[ai-ml/03-ai-engineer/02-how-llms-work|llms]]).
- "Randomness" in model output isn't arbitrary — it's structured sampling from a specific, learned distribution, which is why adjusting temperature/sampling settings has a predictable effect rather than just turning noise up or down uniformly.

## Related
- [[02-expectation-and-variance|expectation-and-variance]]
- [[03-bayes-theorem|bayes-theorem]]
- [[ai-ml/03-ai-engineer/02-how-llms-work|llms]]
