# NumPy

**[reference / practice]** — the foundation of the entire Python numeric stack (pandas, scikit-learn, PyTorch all build on it). The core skill is a **mental shift: stop writing loops, start operating on whole arrays**. Type these out and run them.

## The ndarray

NumPy's one data structure is the **ndarray** — an n-dimensional grid of a *single* dtype, stored in a contiguous block of memory (which is why it's fast — the [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|vectors and matrices]] of linear algebra, in code):

```python
import numpy as np
a = np.array([1, 2, 3])              # 1-D, shape (3,)
b = np.array([[1, 2, 3], [4, 5, 6]]) # 2-D, shape (2, 3)
b.shape      # (2, 3) — rows, cols
b.dtype      # int64
b.ndim       # 2
np.zeros((2, 3)); np.ones(5); np.arange(0, 10, 2); np.linspace(0, 1, 5)
np.random.rand(3, 3)                  # random, for quick experiments
```

Unlike a Python list, an ndarray is fixed-dtype and fixed-size, stored raw — that's the tradeoff that buys speed.

## Vectorization — the whole point

The mental shift: operations apply to the **entire array at once**, element-wise, in compiled C — no Python loop. Compare:

```python
# The way you'd do it in Java/JS — slow in Python
result = []
for x in data:
    result.append(x * 2 + 1)

# The NumPy way — fast, and reads like math
result = data * 2 + 1
```

Everything vectorizes: arithmetic (`a + b`, `a * b`), comparisons (`a > 5`), math functions (`np.sqrt(a)`, `np.exp(a)`, `np.log(a)`). A rule to live by: **if you're writing a `for` loop over a NumPy array, you're probably doing it wrong** — there's almost always a vectorized form that's shorter *and* 10–100× faster. This is the same "push work into the library" principle from [[ai-ml/00-foundations/04-python-and-data-tools/01-python-for-data|Python for data]].

## Indexing, slicing, and boolean masks

Slicing extends Python's, per dimension:

```python
b[0, 2]       # single element (row 0, col 2)
b[0]          # first row
b[:, 1]       # second column (all rows)
b[0:2, 1:3]   # sub-block
```

**Boolean masking** is the killer feature — select/modify by condition, no loop:

```python
a = np.array([1, -2, 3, -4, 5])
a[a > 0]           # array([1, 3, 5]) — keep positives
a[a < 0] = 0       # clamp negatives to zero, in place
mask = (a > 0) & (a < 4)   # combine conditions with & | ~ (not and/or)
```

This "filter and transform by condition" pattern is everywhere in data cleaning ([[ai-ml/02-ml-engineer/02-working-with-data/README|working with data]]) and carries directly into [[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]].

## Broadcasting — operating on mismatched shapes

The concept people find magic at first: NumPy automatically "stretches" smaller arrays to match bigger ones in element-wise ops, *without copying*, when shapes are compatible:

```python
prices = np.array([[10], [20], [30]])   # shape (3, 1)
taxes  = np.array([0.05, 0.10])          # shape (2,)  -> broadcast to (3, 2)
prices * taxes    # (3, 2) — every price × every tax rate

matrix - matrix.mean(axis=0)   # center each column: (n,m) - (m,) broadcasts
```

The rule: dimensions are compatible when they're equal or one of them is 1. Broadcasting is *why* you rarely need loops — normalizing data (`(x - mean) / std`), applying weights, batch operations all rely on it. It's also exactly how neural-network layers apply the same operation across a batch ([[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|deep learning]]).

## Axis operations

Aggregations take an `axis` — the dimension to collapse *along*. This trips everyone up, so anchor it: `axis=0` collapses rows → per-**column** result; `axis=1` collapses columns → per-**row** result:

```python
m = np.array([[1, 2, 3], [4, 5, 6]])
m.sum()            # 21 — everything
m.sum(axis=0)      # [5, 7, 9] — one value per column
m.sum(axis=1)      # [6, 15]  — one value per row
m.mean(axis=0); m.max(axis=1); m.std()
```

## Why it's fast (and the one gotcha)

Speed comes from contiguous typed memory + vectorized C loops + SIMD, plus **views**: slicing returns a *view* into the same memory, not a copy — efficient, but it means **modifying a slice modifies the original**:

```python
sub = a[1:3]
sub[0] = 999      # also changes a[1]!  use a[1:3].copy() if you need independence
```

Knowing view-vs-copy avoids a whole class of "why did my data change" bugs.

## Practice

- Reimplement a small numeric loop you'd write in Java (e.g. normalize a list, compute a moving average) as one vectorized expression.
- Implement `k-means` or `linear regression` using *only* NumPy (no scikit-learn) — the fastest way to make [[ai-ml/00-foundations/03-mathematics/README|the math]] and vectorization click. (These are in [[project-ideas|PROJECTS]].)

## Related
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — what arrays represent
- [[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]] — labeled tables built on ndarrays
- [[ai-ml/02-ml-engineer/05-deep-learning/01-neural-network-fundamentals|Neural Network Fundamentals]] — broadcasting is how layers process batches
