---
id: 6f3f5f8a-61f2-416e-8d1d-a03571e3bbe7
---

# Matrices

A matrix is a grid of numbers in rows and columns.

## What a matrix is
<!-- bite: 3a7cd51c-a075-4306-a1dc-d3fc69f8c825 -->

A matrix is a 2D grid of numbers — rows and columns. Mechanically simple; what matters in ML is that a matrix can be read two different ways, and both readings are used constantly.

The next two bites show the two readings.

## Reading 1 — a table of data
<!-- bite: 2d711280-bab2-4112-af70-05bf86217cfb -->

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
<!-- bite: fbc5c7e2-46c2-4f72-84ca-04fd3cf85511 -->

A matrix, multiplied against a vector, maps that vector to a new vector — it rotates it, scales it, projects it into a different space, or some combination. This is the reading that matters for understanding what a neural network layer actually does.

```python
W = np.array([[1, 0], [0, -1]])   # a transformation: flips the y-component
x = np.array([2, 3])
W @ x                              # -> [2, -3]
```

Every layer of a neural network is, at its core, exactly this: take the incoming vector, multiply it by a weight matrix (learned during training — see [[04-optimization|optimization]]), producing a new vector that gets passed to the next layer. "The network has many layers" means "there's a chain of matrices, each transforming the output of the one before it" (see [[04-matrix-multiplication|matrix-multiplication]] for how that chaining works).

## Shape — the dimensions that have to line up
<!-- bite: 4058e4a6-b7d0-4e34-897f-39f2fd52cb93 -->

A matrix's shape is `rows × columns`. For matrix-vector multiplication to be valid, the number of columns in the matrix must match the number of entries in the vector — this is the single most common source of runtime errors when building anything with neural network code, and it's worth being able to eyeball shapes as a debugging first step.

```text
W: 3 x 2 matrix   x: vector of length 2   ->  W @ x: vector of length 3
(W's columns must match x's length; the result's length matches W's row count)
```

## Why matrix shape tells you about model size
<!-- bite: 27fa4939-3f5b-4a75-af1d-1818cc0af231 -->

A weight matrix connecting a layer of size `m` to a layer of size `n` has shape `n × m`, meaning `n * m` individual parameters. This is literally where the "billions of parameters" in a large model come from — stacking many large matrices, each contributing `rows × columns` worth of learnable numbers. Reading "a 4096 → 4096 layer" as "a matrix with about 16.8 million parameters" is a direct, useful translation once shape clicks.

## Gotchas
<!-- bite: 9add48fc-13bd-4ec6-96da-2dc8060360cd -->

- Matrix multiplication is **not commutative** — `A @ B` is generally not the same as `B @ A` (and one of the two orderings may not even be a valid shape match at all). Order matters, unlike ordinary number multiplication.
- Confusing "a matrix as a data table" with "a matrix as a transformation" is easy when reading ML code, since the same object type (a 2D array) is used for both — context (is this the input data, or a layer's weights?) is what tells you which reading applies.

## Check your understanding
<!-- bite: fb9ab85e-e7a0-4f82-ad48-20322e33996c -->

Try each one before you open the answer.

1. <!-- q: exact id="35e5262b" answer="1000" -->
   A dataset holds 1000 houses with 3 features each, as a matrix with one house per row. How many rows does the matrix have?

   <details><summary>Answer</summary>

   1000. Rows are examples and columns are features, so the matrix is 1000 × 3.

   </details>

2. <!-- q: mcq id="737d714a" -->
   Inside a neural network layer, the weight matrix is being used as which reading?

   - [ ] A table of data
   - [x] A transformation that maps one vector to a new vector

   <details><summary>Answer</summary>

   A transformation. The layer multiplies the incoming vector by its weight matrix to produce a new vector for the next layer. The same 2D array type is used for data tables, so context tells you which reading applies.

   </details>

3. <!-- q: gap id="646689bc" answers="2;-3" -->
   Fill in the gaps. `W = [[1, 0], [0, -1]]` and `x = [2, 3]`. Then `W @ x` is `[___, ___]`.

   <details><summary>Answer</summary>

   `[2, -3]`. This W keeps the first part and flips the sign of the second.

   </details>

4. <!-- q: exact id="45ef9e59" answer="3" accept="three" -->
   W is a 3 × 2 matrix and x is a vector of length 2. How long is the vector `W @ x`?

   <details><summary>Answer</summary>

   3. W's columns (2) must match x's length (2), and the result has one entry per row of W.

   </details>

5. <!-- q: exact id="c7249fe9" answer="16777216" accept="16.8 million|16,777,216|4096*4096" sigfigs="2" -->
   A layer connects 4096 inputs to 4096 outputs. Roughly how many parameters are in its weight matrix?

   <details><summary>Answer</summary>

   4096 × 4096 = 16,777,216, about 16.8 million. A weight matrix from a layer of size m to one of size n has n × m parameters, which is where the "billions of parameters" come from.

   </details>

## Related
<!-- bite: 59d2ae56-cca9-4502-9579-b7f69944f8db -->
- [[01-vectors|vectors]]
- [[04-matrix-multiplication|matrix-multiplication]]
- [[machine-learning/00-foundations/02-what-is-a-model|what-is-a-model]] — weight matrices are the parameters
