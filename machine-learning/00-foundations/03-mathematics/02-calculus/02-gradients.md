---
id: 3c50cbce-1b3b-44f2-87c4-31c1aa5ac001
---

# Gradients

A gradient is the derivative for a function with many inputs.

## What a gradient is
<!-- bite: 6156df7c-7a84-4e18-890a-88f83191aef5 -->

A model doesn't have one parameter — it has millions or billions. The gradient is the multi-parameter generalization of a [[01-derivatives|derivative]]: the collection of partial derivatives, one per parameter, each telling you how nudging *that specific parameter* (holding all others fixed) would change the loss.

Next: what the gradient looks like, and which way it points.

## What a gradient actually is
<!-- bite: 34da6182-b195-418f-a27b-1839e69e3b9f -->

Just a [[01-vectors|vector]] — one entry per parameter, where entry `i` is the partial derivative of the loss with respect to parameter `i`.

```text
loss depends on 3 parameters: w1, w2, w3

gradient = [ d(loss)/d(w1), d(loss)/d(w2), d(loss)/d(w3) ]
         = [     0.4,            -1.2,           0.05    ]
```

Reading this example: increasing `w1` would increase the loss (bad — should decrease `w1`); increasing `w2` would *decrease* the loss (good — should increase `w2`); `w3` barely matters right now (very small effect either way).

## The gradient points toward steepest increase
<!-- bite: fcd3f048-ac33-4446-9b51-c15d56d04dc7 -->

As a whole vector, the gradient points in the direction that increases the loss fastest. Since the goal of training is to *decrease* the loss, every training step moves parameters in the **opposite** direction of the gradient — this is the entire idea behind the name "gradient descent" (see [[04-optimization|optimization]] for the full training loop built on this).

```python
# conceptual
params = params - learning_rate * gradient   # step opposite the gradient
```

## Why "the gradient" is really "a gradient at this specific point"
<!-- bite: 1ffe9eba-be5a-43a4-bf5d-3200a415645c -->

The gradient is recomputed at every single training step, because it depends on the current parameter values — as parameters change, the slope of the loss with respect to each of them changes too. This is why training is iterative rather than a single computation: compute the gradient here, take a small step, recompute the gradient at the new position, repeat.

## Gotchas
<!-- bite: 42b7a85b-a297-4370-9e84-bace12154aeb -->

- A gradient entry near zero for a given parameter doesn't necessarily mean that parameter is unimportant overall — it can mean the loss is currently insensitive to it *at this specific point* in training, which can change as other parameters update.
- "The gradient" is sometimes loosely used to mean "the whole process of computing it across a deep network" — that specific computation (applying the [[03-chain-rule|chain-rule]] backward through every layer) is called backpropagation, a distinct concept from the gradient itself, which is just the resulting vector.

## Check your understanding
<!-- bite: cc69d5d8-9e30-414e-a190-f1a1d3ee2100 -->

Try each one before you open the answer.

1. <!-- q: mcq id="52c4efa1" -->
   The gradient is `[0.4, -1.2, 0.05]` for parameters w1, w2, w3. To reduce the loss, what should happen to w2?

   - [x] Increase it
   - [ ] Decrease it
   - [ ] Leave it alone

   <details><summary>Answer</summary>

   Increase it. Its entry is negative, so increasing w2 would decrease the loss. w1 should go down, and w3 barely matters right now.

   </details>

2. <!-- q: gap id="44ae73be" answers="increase|increases;opposite" -->
   Fill in the gaps. The gradient points in the direction that makes the loss ___ fastest, so each training step moves the parameters in the ___ direction.

   <details><summary>Answer</summary>

   Increase, then opposite. That is why it's called gradient descent: `params = params - learning_rate * gradient`.

   </details>

3. <!-- q: exact id="e3c6baf6" answer="1000000" accept="one million|1 million|1,000,000" -->
   A model has 1,000,000 parameters. How many entries does its gradient have?

   <details><summary>Answer</summary>

   1,000,000. There is one partial derivative per parameter.

   </details>

4. <!-- q: mcq id="2ecb3496" -->
   Why is the gradient recomputed at every training step?

   - [ ] Because the training data changes its labels
   - [x] Because it depends on the current parameter values, and those change every step
   - [ ] Because computers forget it between steps

   <details><summary>Answer</summary>

   It depends on where the parameters currently are. After a step, the slope of the loss is different, so you compute it again at the new spot.

   </details>

5. <!-- q: open id="71381eba" -->
   What is the difference between the gradient and backpropagation?

   <details><summary>Answer</summary>

   The gradient is the result: a vector with one partial derivative per parameter. Backpropagation is the method for computing it in a deep network, by applying the chain rule backward through every layer.

   </details>

## Related
<!-- bite: f25e6b36-af38-4e7a-94d7-be671bb75e0c -->
- [[01-derivatives|derivatives]]
- [[03-chain-rule|chain-rule]]
- [[04-optimization|optimization]]
