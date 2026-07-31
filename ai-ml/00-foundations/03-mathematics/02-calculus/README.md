# Calculus for AI/ML

The one idea from calculus that actually matters for ML: a derivative tells you which direction to nudge a number to make some other number (usually a loss/error) go down. Training a model is, mechanically, computing a lot of derivatives and using them to adjust parameters — that's the entire connection between calculus and ML, and the three notes below cover it without requiring a full calculus course.

## Reading order
1. [[01-derivatives|derivatives]] — **[Beginner]** — rate of change; why the minimum of a function is where the derivative is zero
2. [[02-gradients|gradients]] — **[Intermediate]** — derivatives for every parameter at once, collected into a vector
3. [[03-chain-rule|chain-rule]] — **[Advanced]** — how to get a gradient through a *chain* of functions — i.e. backpropagation

## Why you don't need to compute any of this by hand

Every deep learning framework (PyTorch, TensorFlow, JAX) implements automatic differentiation — given the forward computation, the framework derives the chain-rule gradient computation for you. What matters is understanding *what's happening conceptually* (covered in [[03-chain-rule|chain-rule]]), not deriving gradients manually.

## Related
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|linear algebra]] — gradients are vectors, and layers are matrix multiplications
- [[04-optimization|optimization]] — where all three of these notes get put to use in an actual training loop
