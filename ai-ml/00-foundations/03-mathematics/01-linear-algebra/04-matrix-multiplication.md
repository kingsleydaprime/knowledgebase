# Matrix Multiplication

Matrix multiplication is [[03-dot-product|dot products]], batched. Multiplying a matrix by a vector means taking the dot product of the vector with *each row* of the matrix, producing one output number per row. Multiplying two matrices together means doing that once for every row of the first matrix against every column of the second. It sounds like a lot of separate operations because it is — and that's exactly why this is the operation GPUs are built around accelerating.

## The mechanics

```python
import numpy as np
X = np.array([[1, 2], [3, 4]])
Y = np.array([[5, 6], [7, 8]])
X @ Y
# result[0][0] = row0 of X . col0 of Y = 1*5 + 2*7 = 19
# result[0][1] = row0 of X . col1 of Y = 1*6 + 2*8 = 22
# result[1][0] = row1 of X . col0 of Y = 3*5 + 4*7 = 43
# result[1][1] = row1 of X . col1 of Y = 3*6 + 4*8 = 50
```

For a matrix-vector product (the more common case in a neural network's forward pass), it's the same idea with the second "matrix" being a single column:

```python
W = np.array([[1, 0], [0, -1], [2, 1]])   # shape 3x2
x = np.array([2, 3])                       # shape 2
W @ x                                        # shape 3 -> [2, -3, 7]
```

## Why this is what "running a neural network" actually is

A layer's forward pass is: take the incoming vector, multiply by the layer's weight matrix, add a bias vector, apply a nonlinearity — then hand the result to the next layer as its input. "The model has 40 layers" means this operation repeats 40 times in sequence, each time with a different weight [[02-matrices|matrix]]. There's no separate, more exotic mechanism underneath a neural network's forward pass beyond this chain of matrix multiplications plus nonlinear functions between them — the nonlinearities (ReLU, GELU, and similar) are what stop the whole chain from mathematically collapsing into a single equivalent matrix multiplication, which is what would happen if every layer were purely linear.

## Why GPUs matter specifically for this

A GPU's core strength is doing huge numbers of independent arithmetic operations in parallel — and computing every entry of a matrix product is exactly that: independent multiply-and-sum operations that don't depend on each other's results. Training or running a large model means doing an enormous number of these matrix multiplications, which is the direct, mechanical reason GPU (or specialized AI accelerator) hardware is central to modern ML rather than an implementation detail.

## Complexity

Multiplying an `n×m` matrix by an `m×p` matrix takes O(n·m·p) time using the standard algorithm — the cost grows with all three dimensions involved. This is why layer width (the `m`/`p` dimensions) directly drives compute cost, not just parameter count in the abstract — a wider layer costs more per forward pass, not just more memory to store.

## Gotchas

- Shapes must be compatible — the number of columns in the first matrix must equal the number of rows (or length, for a vector) in the second. A shape mismatch here is one of the most common errors when building or debugging model code by hand.
- Matrix multiplication is associative but **not commutative** — `(A @ B) @ C` equals `A @ (B @ C)`, but `A @ B` does not equal `B @ A` in general (and one order may not even be a valid shape). Order matters when chaining multiple transformations.

## Related
- [[03-dot-product|dot-product]]
- [[02-matrices|matrices]]
- [[01-vectors|vectors]]
