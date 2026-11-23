---
id: a0183ca2-3cb3-47a6-aa25-d066986e9efd
---

# Chain Rule (and Backpropagation)

The chain rule finds the derivative of functions chained one after another.

## What the chain rule is
<!-- bite: 77323afe-56df-49e6-8178-1b882aa474cc -->

A neural network is a chain of functions — layer 1's output feeds layer 2, which feeds layer 3, and so on. The chain rule is the calculus fact that lets you compute the derivative of a *chain* of functions by multiplying the derivatives of each individual link. It's the one piece of calculus that makes training a deep network computationally tractable at all.

Next: the rule itself, then backpropagation, which is the chain rule applied layer by layer.

## The rule itself
<!-- bite: 43295460-1767-4d38-ae4d-046ac8030877 -->

```text
if y = f(g(x)), then dy/dx = f'(g(x)) * g'(x)
```

In words: the rate of change of the whole chain is the product of the rates of change of each link in the chain, evaluated at the right point.

## Backpropagation — the chain rule, applied layer by layer
<!-- bite: 8c131f3d-0708-4eb6-b0a8-448911de9c83 -->

Training needs the [[02-gradients|gradient]] of the loss with respect to *every* parameter in the network — including parameters buried in the very first layer, far from where the loss is actually computed at the output. Backpropagation is nothing more than the chain rule applied repeatedly, working backward from the loss at the output toward each parameter:

```text
loss depends on layer3 depends on layer2 depends on layer1 depends on parameter W

d(loss)/dW = d(loss)/d(layer3) * d(layer3)/d(layer2) * d(layer2)/d(layer1) * d(layer1)/dW
             <- backprop computes exactly this product, working backward from the loss
```

Without the chain rule, there'd be no tractable way to figure out how a parameter buried deep inside a 100-layer network affects the final loss; with it, that effect is just a product of local derivatives along the path connecting that parameter to the output. "Back" in backpropagation refers to this direction — computing derivatives starting from the output and working backward toward the input, which turns out to be far more efficient than computing them starting from the input and working forward.

## Why you don't compute any of this by hand
<!-- bite: 75139717-8ca9-4f69-992b-c8f89000f375 -->

Every deep learning framework (PyTorch, TensorFlow, JAX) implements **automatic differentiation** ("autodiff"): given the forward computation — how inputs turn into outputs, expressed as ordinary code — the framework automatically derives the chain-rule computation needed to get gradients, without a human deriving any formula by hand. In practice, you write the forward pass, call something like `.backward()` (PyTorch's term), and the framework handles applying the chain rule through every operation used, all the way back to every parameter. Knowing that this is what's happening underneath is what matters for reading about how models are trained; deriving gradients by hand is a rare, specialized skill even among ML practitioners, mostly useful for understanding a new architecture's internals rather than day-to-day model building.

## Gotchas
<!-- bite: a972800b-2492-4680-aabe-ee5f62ec6d36 -->

- A very deep network can suffer from **vanishing or exploding gradients** — since backpropagation multiplies many local derivatives together across layers, if those local derivatives are consistently small (< 1) the product shrinks toward zero across many layers (vanishing), and if consistently large (> 1) it grows explosively (exploding). This is a direct, structural consequence of the chain rule being a product across many layers, not a bug in any single layer — architectural choices (residual connections, careful initialization, normalization layers) exist specifically to counteract it.
- "Backpropagation" and "gradient descent" are often mentioned together but are different things: backpropagation is *how the gradient gets computed*; gradient descent (see [[04-optimization|optimization]]) is *what you do with that gradient once you have it*.

## Check your understanding
<!-- bite: c7897dcd-99cb-4fbc-9103-0470bb02ccf6 -->

Try each one before you open the answer.

1. <!-- q: gap id="3db8699b" answers="multiplying|multiply|product" -->
   Fill in the gap. If y = f(g(x)), the chain rule finds dy/dx by ___ the derivatives of each link: f'(g(x)) × g'(x).

   <details><summary>Answer</summary>

   Multiplying. The rate of change of the whole chain is the product of the rates of change of each link.

   </details>

2. <!-- q: mcq id="d7af9aba" -->
   Why is it called backpropagation?

   - [ ] Because it undoes the last training step
   - [x] Because it computes the derivatives starting from the loss at the output and works back toward the input
   - [ ] Because it runs the data through the network in reverse

   <details><summary>Answer</summary>

   It works backward from the loss toward each parameter. That turns out to be far more efficient than starting at the input.

   </details>

3. <!-- q: mcq id="5eb2f857" -->
   Local derivatives across many layers are all a bit smaller than 1. What happens to the gradient for the early layers?

   - [x] It shrinks toward zero (vanishing gradients)
   - [ ] It grows very large (exploding gradients)
   - [ ] Nothing, the size of the local derivatives doesn't matter

   <details><summary>Answer</summary>

   It vanishes. Backprop multiplies many local derivatives together, and multiplying many numbers below 1 shrinks the product toward zero. Numbers consistently above 1 make it explode.

   </details>

4. <!-- q: mcq id="4b4ce8d8" -->
   In PyTorch, who works out the chain-rule computation for the gradients?

   - [ ] You derive each formula by hand
   - [x] The framework, through automatic differentiation, when you call `.backward()`

   <details><summary>Answer</summary>

   The framework. You write the forward pass as ordinary code, and autodiff applies the chain rule through every operation back to every parameter.

   </details>

5. <!-- q: open id="93cca19b" -->
   Backpropagation and gradient descent are often mentioned together. What does each one do?

   <details><summary>Answer</summary>

   Backpropagation computes the gradient. Gradient descent uses that gradient to update the parameters, by taking a small step in the opposite direction.

   </details>

## Related
<!-- bite: e9cb5934-9f64-4fab-b54e-5313b1869f06 -->
- [[02-gradients|gradients]]
- [[01-derivatives|derivatives]]
- [[04-optimization|optimization]]
