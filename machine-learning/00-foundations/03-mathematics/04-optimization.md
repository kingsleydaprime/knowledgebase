---
id: 3fcc187b-8223-48f5-8b9a-ab52fd835264
---

# Optimization for AI/ML

Optimization is the piece that actually connects [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|linear algebra]] (how a model is represented), [[machine-learning/00-foundations/03-mathematics/02-calculus/index|calculus]] (how to compute which direction reduces error), and [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/index|probability and statistics]] (how error/loss is defined) into an actual training loop. If [[machine-learning/00-foundations/02-what-is-a-model|what-is-a-model]] describes "a big adjustable function," optimization is the description of *how the adjusting happens*.

## The loss function — defining "wrong"
<!-- bite: 73b4a140-ad29-4d8d-9fe8-38bcfde03d6e -->

Before you can improve a model, you need a single number that measures how wrong its current output is — the **loss** (or cost). Simple example for predicting a number: squared error, `(prediction - actual)²`. For classification, it's typically cross-entropy loss (see [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/index|probability and statistics]]). Whatever the specific formula, the training process only ever does one thing: try to make this number smaller.

## Gradient descent — the core algorithm
<!-- bite: 88c14522-fd38-452c-85d5-48c59867d517 -->

1. Compute the loss for the current parameters.
2. Compute the gradient of the loss with respect to every parameter — i.e. "if I nudge this parameter slightly, does the loss go up or down, and how fast" (this is where [[03-chain-rule|the chain rule / backpropagation]] does its work).
3. Nudge every parameter a small step in the direction that *decreases* the loss (opposite the gradient).
4. Repeat, using new batches of data, until the loss stops meaningfully improving.

```python
# conceptual, not a real framework's API
for step in range(num_steps):
    predictions = model(inputs, params)
    loss = loss_function(predictions, targets)
    gradients = compute_gradients(loss, params)     # backpropagation
    params = params - learning_rate * gradients      # the actual "learning" step
```

```text
loss
 ^
 |  \
 |   \
 |    \___
 |        \___
 |            \________  <- gradient descent walks downhill, step by step
 +-----------------------> parameter value
```

## Learning rate — the size of each step
<!-- bite: 7cfe69b1-166d-4597-8af3-aede681c6799 -->

The learning rate controls how big a step each update takes. Too large, and updates overshoot the minimum, bouncing around or diverging entirely (loss gets worse, not better). Too small, and training crawls, taking an impractically long time to converge, or gets stuck in a shallow dip that a bigger step would have escaped. Picking (and often dynamically adjusting) the learning rate is one of the most impactful, least glamorous parts of getting a model to train well.

## Batches — why training doesn't use the whole dataset every step
<!-- bite: 2d56a35c-e602-4472-aa2b-ed92b57190ed -->

Computing the exact gradient over an entire dataset before each update is accurate but slow, especially with millions of examples. Instead, training almost always uses **mini-batches** — a small random subset of the data — to estimate the gradient at each step. This is **stochastic gradient descent (SGD)**: noisier gradient estimates, but many more update steps per unit of time, which in practice converges faster and can even help escape shallow local minima (the noise itself acts like a small kick).

## Local minima and why training isn't guaranteed to find "the best" model
<!-- bite: 4e53f41d-b27c-4a8a-a3a3-fb1b1ccd1ce6 -->

Gradient descent only guarantees it'll walk downhill — it has no way of knowing whether it's approaching the best possible minimum (global) or has settled into a worse but locally flat spot (local minimum) or a flat saddle region. In practice, for the huge, high-dimensional parameter spaces of deep learning, this turns out to matter less than the simple 2D picture above suggests — most local minima found in practice are "good enough," which is more an empirical observation about deep networks than a guarantee.

## Common optimizer variants you'll see named
<!-- bite: 6e7c1f2e-e0d3-4a1e-be00-e88c9ea962df -->

Plain gradient descent is rarely used directly in practice — variants that adapt the step size per parameter and incorporate momentum (carrying some of the previous step's direction forward, to smooth out noisy updates) train faster and more reliably. **Adam** is the most commonly used default across deep learning today; **SGD with momentum** is still used, particularly in some computer vision training setups. Knowing these names exist and roughly why they help (adaptive step sizes, momentum smoothing) is enough at this level — the derivations are a deeper rabbit hole than needed here.

## Gotchas
<!-- bite: d9b871a4-4469-418c-a70d-8db6201d24fc -->

- A loss that's decreasing on training data but flat or rising on held-out validation data is the numeric signature of overfitting (see [[machine-learning/00-foundations/02-what-is-a-model|what-is-a-model]]) — optimization is happily doing its job of reducing training loss, which isn't the same as the model actually getting better.
- Learning rate is usually the single highest-leverage setting to tune when a model trains badly — "loss is exploding to NaN" is very often "learning rate too high," and "loss barely moves" is very often "learning rate too low."

## Related
<!-- bite: 9d4f37b1-4c90-435e-879b-c8800ddec41e -->
- [[machine-learning/00-foundations/03-mathematics/02-calculus/index|calculus]] — where gradients come from
- [[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/index|probability and statistics]] — where loss functions come from
- [[machine-learning/00-foundations/02-what-is-a-model|what-is-a-model]]
