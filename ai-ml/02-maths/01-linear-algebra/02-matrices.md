# Matrices

A matrix is a 2D grid of numbers — rows and columns. Mechanically simple; what matters in ML is that a matrix can be read two different ways, and both readings are used constantly.

## Reading 1 — a table of data

Rows are examples, columns are features — a spreadsheet, essentially. A dataset of 1000 houses with 3 features each is naturally a 1000×3 matrix: each row is one house's [[01-vectors|feature vector]].

```python
import numpy as np
houses = np.array([
    [1800, 15, 2],
    [2400, 5,  8],
    [1200, 30, 1],
])   # 3 houses (rows) x 3 features (columns)
```

## Reading 2 — a transformation

A matrix, multiplied against a vector, maps that vector to a new vector — it rotates it, scales it, projects it into a different space, or some combination. This is the reading that matters for understanding what a neural network layer actually does.

```python
W = np.array([[1, 0], [0, -1]])   # a transformation: flips the y-component
x = np.array([2, 3])
W @ x                              # -> [2, -3]
```

Every layer of a neural network is, at its core, exactly this: take the incoming vector, multiply it by a weight matrix (learned during training — see [[04-optimization|optimization]]), producing a new vector that gets passed to the next layer. "The network has many layers" means "there's a chain of matrices, each transforming the output of the one before it" (see [[04-matrix-multiplication|matrix-multiplication]] for how that chaining works).

## Shape — the dimensions that have to line up

A matrix's shape is `rows × columns`. For matrix-vector multiplication to be valid, the number of columns in the matrix must match the number of entries in the vector — this is the single most common source of runtime errors when building anything with neural network code, and it's worth being able to eyeball shapes as a debugging first step.

```
W: 3 x 2 matrix   x: vector of length 2   ->  W @ x: vector of length 3
(W's columns must match x's length; the result's length matches W's row count)
```

## Why matrix shape tells you about model size

A weight matrix connecting a layer of size `m` to a layer of size `n` has shape `n × m`, meaning `n * m` individual parameters. This is literally where the "billions of parameters" in a large model come from — stacking many large matrices, each contributing `rows × columns` worth of learnable numbers. Reading "a 4096 → 4096 layer" as "a matrix with about 16.7 million parameters" is a direct, useful translation once shape clicks.

## Gotchas

- Matrix multiplication is **not commutative** — `A @ B` is generally not the same as `B @ A` (and one of the two orderings may not even be a valid shape match at all). Order matters, unlike ordinary number multiplication.
- Confusing "a matrix as a data table" with "a matrix as a transformation" is easy when reading ML code, since the same object type (a 2D array) is used for both — context (is this the input data, or a layer's weights?) is what tells you which reading applies.

## Related
- [[01-vectors|vectors]]
- [[04-matrix-multiplication|matrix-multiplication]]
- [[02-what-is-a-model|what-is-a-model]] — weight matrices are the parameters
