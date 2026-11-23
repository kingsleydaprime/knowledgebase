---
id: bcb8a60e-4b6e-45d9-a6ad-9aa7c9675685
---

# Derivatives

A derivative is the slope of a function at a point.

## What a derivative is
<!-- bite: 1c07b078-a823-42c8-b15a-d0cbe49811d3 -->

The derivative of a function at a point tells you the slope there — if you nudge the input slightly, how much (and in which direction) does the output move? A positive derivative means "increasing the input increases the output"; negative means the opposite; zero means flat, no immediate change either way.

Next: the idea in more detail, then why ML needs it.

## The idea
<!-- bite: 4d929ccb-83b2-40ee-a14b-654619151239 -->

```text
f(x) = x²
f'(x) = 2x        <- the derivative (slope) at any point x

at x=3: f'(3) = 6  -> increasing x here increases f(x) steeply
at x=1: f'(1) = 2  -> increasing x here increases f(x) more gently
at x=0: f'(0) = 0  -> flat — this is the minimum of f(x) = x²
```

```text
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
<!-- bite: c98878e5-5ade-4e29-8977-04bdedb5019c -->

Training a model comes down to finding parameter values that make a **loss function** (a measure of how wrong the model currently is) as small as possible. The derivative of the loss with respect to a parameter tells you exactly which direction to nudge that parameter to make the loss smaller — and the minimum of the loss (the best-fitting parameters, at least locally) is where that derivative is zero. This is the entire conceptual bridge from "derivative" to "how a model learns," fleshed out fully in [[04-optimization|optimization]].

## Partial derivatives — one variable at a time
<!-- bite: 45c4cfb8-8715-4214-a5db-0c7dcb26fbea -->

A function with multiple inputs (like a loss function that depends on millions of parameters) has a **partial derivative** with respect to each one — "if I nudge just this one parameter, holding all the others fixed, how does the output change?" Collecting all of these partial derivatives together into one vector is exactly what a [[02-gradients|gradient]] is.

## Gotchas
<!-- bite: 4a7e2f9e-8800-4a5e-a3d4-32165775eba2 -->

- A derivative of zero doesn't always mean "the best possible value" — it can mean a true minimum, a maximum, or a saddle point (flat in some directions, sloped in others). Distinguishing these matters more once you're past a simple 1D picture like the one above — see [[04-optimization|optimization]] for how this plays out in practice with many parameters.
- The derivative describes the slope *at a single point* — it says nothing directly about the function's overall shape far away from that point, which is why optimization takes many small steps rather than jumping straight to wherever the local slope points.

## Check your understanding
<!-- bite: 8556231e-8cf4-4713-974c-b0ebec0ca589 -->

Try each one before you open the answer.

1. <!-- q: exact id="9a844345" answer="6" accept="six" -->
   For f(x) = x², the derivative is f'(x) = 2x. What is the slope at x = 3?

   <details><summary>Answer</summary>

   6. f'(3) = 2 × 3 = 6, so increasing x here increases f(x) steeply.

   </details>

2. <!-- q: mcq id="fd4864fd" -->
   The derivative of a function at a point is negative. What happens if you increase the input a little?

   - [ ] The output goes up
   - [x] The output goes down
   - [ ] The output stays the same

   <details><summary>Answer</summary>

   The output goes down. Positive means the output rises with the input, negative means it falls, and zero means it is flat.

   </details>

3. <!-- q: mcq id="1f4b8a5c" -->
   The derivative is zero at a point. Which of these could that point be? Choose all that apply.

   - [x] A minimum
   - [x] A maximum
   - [x] A saddle point

   <details><summary>Answer</summary>

   All three. A zero derivative only means "flat here". It does not by itself mean you found the best value.

   </details>

4. <!-- q: gap id="2e89592a" answers="partial derivative|partial;gradient" -->
   Fill in the gaps. Nudging just one input while holding the others fixed gives a ___. Collecting one of these per input into a vector gives the ___.

   <details><summary>Answer</summary>

   Partial derivative, then gradient. A loss with millions of parameters has one partial derivative per parameter, and together they form the gradient.

   </details>

5. <!-- q: open id="a73efe23" -->
   Why does a model care about derivatives at all? Connect the derivative to training.

   <details><summary>Answer</summary>

   Training is about making the loss as small as possible. The derivative of the loss with respect to a parameter tells you which way to nudge that parameter so the loss goes down. The minimum is where the derivative is zero.

   </details>

## Check your understanding: worked problems
<!-- bite: 062a8522-bd93-4fff-b1bc-d0217209b134 -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="2beb1e29" answer="14" -->
   f(x) = 3x² + 2x. What is f'(2)?

   <details><summary>Answer</summary>

   14. f'(x) = 6x + 2, so f'(2) = 12 + 2 = 14.

   </details>

2. <!-- q: exact id="0957d527" answer="3" accept="three" -->
   f(x) = x³. What is the slope at x = 1?

   <details><summary>Answer</summary>

   3. f'(x) = 3x², so f'(1) = 3.

   </details>

3. <!-- q: exact id="5bceddb2" answer="2" accept="x=2|x = 2" -->
   f(x) = x² − 4x. At what x is the derivative zero (the minimum)?

   <details><summary>Answer</summary>

   x = 2. f'(x) = 2x − 4, which is 0 when x = 2.

   </details>

## Related
<!-- bite: a0987138-8e0d-4d60-950a-4d74529051be -->
- [[02-gradients|gradients]]
- [[03-chain-rule|chain-rule]]
- [[04-optimization|optimization]]
