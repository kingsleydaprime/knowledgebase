# Gradients

A model doesn't have one parameter — it has millions or billions. The gradient is the multi-parameter generalization of a [[01-derivatives|derivative]]: the collection of partial derivatives, one per parameter, each telling you how nudging *that specific parameter* (holding all others fixed) would change the loss.

## What a gradient actually is

Just a [[01-vectors|vector]] — one entry per parameter, where entry `i` is the partial derivative of the loss with respect to parameter `i`.

```
loss depends on 3 parameters: w1, w2, w3

gradient = [ d(loss)/d(w1), d(loss)/d(w2), d(loss)/d(w3) ]
         = [     0.4,            -1.2,           0.05    ]
```

Reading this example: increasing `w1` would increase the loss (bad — should decrease `w1`); increasing `w2` would *decrease* the loss (good — should increase `w2`); `w3` barely matters right now (very small effect either way).

## The gradient points toward steepest increase

As a whole vector, the gradient points in the direction that increases the loss fastest. Since the goal of training is to *decrease* the loss, every training step moves parameters in the **opposite** direction of the gradient — this is the entire idea behind the name "gradient descent" (see [[04-optimization|optimization]] for the full training loop built on this).

```python
# conceptual
params = params - learning_rate * gradient   # step opposite the gradient
```

## Why "the gradient" is really "a gradient at this specific point"

The gradient is recomputed at every single training step, because it depends on the current parameter values — as parameters change, the slope of the loss with respect to each of them changes too. This is why training is iterative rather than a single computation: compute the gradient here, take a small step, recompute the gradient at the new position, repeat.

## Gotchas

- A gradient entry near zero for a given parameter doesn't necessarily mean that parameter is unimportant overall — it can mean the loss is currently insensitive to it *at this specific point* in training, which can change as other parameters update.
- "The gradient" is sometimes loosely used to mean "the whole process of computing it across a deep network" — that specific computation (applying the [[03-chain-rule|chain-rule]] backward through every layer) is called backpropagation, a distinct concept from the gradient itself, which is just the resulting vector.

## Related
- [[01-derivatives|derivatives]]
- [[03-chain-rule|chain-rule]]
- [[04-optimization|optimization]]
