# Chain Rule (and Backpropagation)

A neural network is a chain of functions — layer 1's output feeds layer 2, which feeds layer 3, and so on. The chain rule is the calculus fact that lets you compute the derivative of a *chain* of functions by multiplying the derivatives of each individual link. It's the one piece of calculus that makes training a deep network computationally tractable at all.

## The rule itself

```
if y = f(g(x)), then dy/dx = f'(g(x)) * g'(x)
```

In words: the rate of change of the whole chain is the product of the rates of change of each link in the chain, evaluated at the right point.

## Backpropagation — the chain rule, applied layer by layer

Training needs the [[02-gradients|gradient]] of the loss with respect to *every* parameter in the network — including parameters buried in the very first layer, far from where the loss is actually computed at the output. Backpropagation is nothing more than the chain rule applied repeatedly, working backward from the loss at the output toward each parameter:

```
loss depends on layer3 depends on layer2 depends on layer1 depends on parameter W

d(loss)/dW = d(loss)/d(layer3) * d(layer3)/d(layer2) * d(layer2)/d(layer1) * d(layer1)/dW
             <- backprop computes exactly this product, working backward from the loss
```

Without the chain rule, there'd be no tractable way to figure out how a parameter buried deep inside a 100-layer network affects the final loss; with it, that effect is just a product of local derivatives along the path connecting that parameter to the output. "Back" in backpropagation refers to this direction — computing derivatives starting from the output and working backward toward the input, which turns out to be far more efficient than computing them starting from the input and working forward.

## Why you don't compute any of this by hand

Every deep learning framework (PyTorch, TensorFlow, JAX) implements **automatic differentiation** ("autodiff"): given the forward computation — how inputs turn into outputs, expressed as ordinary code — the framework automatically derives the chain-rule computation needed to get gradients, without a human deriving any formula by hand. In practice, you write the forward pass, call something like `.backward()` (PyTorch's term), and the framework handles applying the chain rule through every operation used, all the way back to every parameter. Knowing that this is what's happening underneath is what matters for reading about how models are trained; deriving gradients by hand is a rare, specialized skill even among ML practitioners, mostly useful for understanding a new architecture's internals rather than day-to-day model building.

## Gotchas

- A very deep network can suffer from **vanishing or exploding gradients** — since backpropagation multiplies many local derivatives together across layers, if those local derivatives are consistently small (< 1) the product shrinks toward zero across many layers (vanishing), and if consistently large (> 1) it grows explosively (exploding). This is a direct, structural consequence of the chain rule being a product across many layers, not a bug in any single layer — architectural choices (residual connections, careful initialization, normalization layers) exist specifically to counteract it.
- "Backpropagation" and "gradient descent" are often mentioned together but are different things: backpropagation is *how the gradient gets computed*; gradient descent (see [[04-optimization|optimization]]) is *what you do with that gradient once you have it*.

## Related
- [[02-gradients|gradients]]
- [[01-derivatives|derivatives]]
- [[04-optimization|optimization]]
