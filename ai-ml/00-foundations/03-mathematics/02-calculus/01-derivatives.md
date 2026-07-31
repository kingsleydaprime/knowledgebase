# Derivatives

The derivative of a function at a point tells you the slope there — if you nudge the input slightly, how much (and in which direction) does the output move? A positive derivative means "increasing the input increases the output"; negative means the opposite; zero means flat, no immediate change either way.

## The idea

```
f(x) = x²
f'(x) = 2x        <- the derivative (slope) at any point x

at x=3: f'(3) = 6  -> increasing x here increases f(x) steeply
at x=1: f'(1) = 2  -> increasing x here increases f(x) more gently
at x=0: f'(0) = 0  -> flat — this is the minimum of f(x) = x²
```

```
f(x)
 |    \                    /
 |     \                  /
 |      \                /
 |       \______________/
 +-----------------------> x
              ^
         derivative = 0 here (the minimum)
```

## Why this matters for ML: finding the minimum of a loss function

Training a model comes down to finding parameter values that make a **loss function** (a measure of how wrong the model currently is) as small as possible. The derivative of the loss with respect to a parameter tells you exactly which direction to nudge that parameter to make the loss smaller — and the minimum of the loss (the best-fitting parameters, at least locally) is where that derivative is zero. This is the entire conceptual bridge from "derivative" to "how a model learns," fleshed out fully in [[04-optimization|optimization]].

## Partial derivatives — one variable at a time

A function with multiple inputs (like a loss function that depends on millions of parameters) has a **partial derivative** with respect to each one — "if I nudge just this one parameter, holding all the others fixed, how does the output change?" Collecting all of these partial derivatives together into one vector is exactly what a [[02-gradients|gradient]] is.

## Gotchas

- A derivative of zero doesn't always mean "the best possible value" — it can mean a true minimum, a maximum, or a saddle point (flat in some directions, sloped in others). Distinguishing these matters more once you're past a simple 1D picture like the one above — see [[04-optimization|optimization]] for how this plays out in practice with many parameters.
- The derivative describes the slope *at a single point* — it says nothing directly about the function's overall shape far away from that point, which is why optimization takes many small steps rather than jumping straight to wherever the local slope points.

## Related
- [[02-gradients|gradients]]
- [[03-chain-rule|chain-rule]]
- [[04-optimization|optimization]]
