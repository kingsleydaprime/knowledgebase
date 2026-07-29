# What is a Model

A model is a function with a huge number of adjustable numbers ("parameters" or "weights") whose values were set by feeding it examples, rather than hand-written by a programmer. That's it, mechanically — everything else (LLMs, image classifiers, recommendation engines) is a variation on "a big adjustable function plus a way of adjusting it."

## Parameters / weights

Every parameter is just a number the model multiplies or adds somewhere internally while turning an input into an output. A model with "7 billion parameters" has 7 billion of these numbers. Before training, they're random noise; training's entire job is nudging them toward values that make the model's outputs match reality (see [[04-optimization|optimization]] for the mechanism). Nothing about a parameter is inherently meaningful on its own — the meaning is distributed across all of them together, which is exactly why individual weights inside a trained model are notoriously hard to interpret.

## Training vs inference — two completely different phases

- **Training**: showing the model many (input, correct-output) examples, computing how wrong its guess is, and adjusting parameters to reduce that error. Expensive — can take days to months of GPU time for large models — and happens once (or occasionally, to update the model).
- **Inference**: using an already-trained model to produce output for a new input. Cheap and fast relative to training, no parameter updates happen — this is what's running every time you chat with an LLM or run an image classifier on a new photo.

Confusing these two is a common source of misunderstanding — "training a model" and "using a model" (inference) are different operations with wildly different cost profiles, and a deployed product almost never trains live on your input (though some products do collect your input to potentially retrain a *future* version).

## Architecture — the shape of the function

"Architecture" describes how the parameters are organized and connected — not their values, but the structure they sit in. A linear regression's architecture is a single weighted sum. A neural network's architecture is layers of weighted sums each followed by a nonlinear function, stacked on top of each other. A transformer (what LLMs are built from) is a specific architecture built around an "attention" mechanism that lets the model weigh how much every part of the input should influence every other part — enough of its own topic to warrant its own note in [[03-llms|llms]] rather than covered fully here.

## Why "bigger model" isn't automatically "better model"

More parameters mean more capacity to represent complex patterns, but also:
- More data needed to set all those parameters meaningfully (an under-trained large model can underperform a smaller, well-trained one).
- More compute for both training and inference.
- More risk of **overfitting** — memorizing the training examples' quirks instead of learning the general pattern, which shows up as great performance on training data and poor performance on new data.

## Generalization — the actual goal

The entire point of training isn't to get the right answer on the training examples (that's almost trivial to achieve by memorizing them) — it's to produce a model that performs well on inputs it has **never seen**. This is called generalization, and it's evaluated by holding back a chunk of data (the "test set") that the model never trains on, then checking performance there. Any time you hear "accuracy" or "loss" quoted for a model, the honest version of that number is measured on held-out data, not training data.

## Gotchas

- "The model has learned X" usually means "the model's parameters, after training, produce outputs correlated with X across the examples it saw" — not that it has an explicit, inspectable rule for X anywhere inside it.
- A model performing perfectly on its training data and poorly on new data is the textbook overfitting signature — not a sign of a "smart" model, the opposite.
- Inference isn't free of quirks either — the same trained model can give different-feeling answers depending on decoding settings (temperature, sampling strategy — see [[03-llms|llms]]), which is a separate axis from anything learned during training.

## Related
- [[04-optimization|optimization]]
- [[03-llms|llms]]
- [[04-other-model-types|other-model-types]]
