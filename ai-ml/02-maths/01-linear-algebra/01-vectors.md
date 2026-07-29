# Vectors

A vector is an ordered list of numbers: `[0.2, -1.4, 3.0]`. That's the entire mechanical definition — what makes vectors matter for ML is what they're used to *represent*.

## What a vector represents in ML

Almost everything a model touches gets turned into a vector first:

- **A data point** — a row of features (a house's square footage, age, location, price → one vector per house).
- **A word, sentence, or document** — an "embedding," a vector positioned so that similar meanings sit close together in the space (see [[03-dot-product|dot-product]] for how "close" is measured, and [[03-llms|llms]] for embeddings in context).
- **A direction to move in** — during training, the update applied to a model's parameters at each step is itself a vector (see [[02-gradients|gradients]]).
- **An image, flattened** — a grid of pixel values reshaped into one long vector (or, more commonly today, processed through a structure that preserves the 2D layout — but the underlying representation is still numeric and vector-like at each stage).

```python
import numpy as np
house = np.array([1800, 15, 2])   # [sqft, age_years, distance_to_city_km]
```

## Geometric intuition — a vector is a point, and a direction

A vector can be read two ways, both useful: as a **point** in space (this specific house sits at this coordinate in feature-space), or as an **arrow** from the origin to that point (a direction and a magnitude). The second reading is what makes "vectors that point in similar directions represent similar things" a meaningful statement rather than just a numerical coincidence — see [[03-dot-product|dot-product]] for how that similarity is actually computed.

## Dimensionality

The number of entries in a vector is its dimensionality. A house-price vector might have 3-10 dimensions (a handful of features); a modern LLM's embedding vectors commonly have hundreds to low thousands of dimensions — far too many to visualize directly, but the same arithmetic (addition, scaling, dot products) applies regardless of how many dimensions there are.

## Basic operations

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

a + b        # [5, 7, 9]   — element-wise addition
a * 2        # [2, 4, 6]   — scaling
np.linalg.norm(a)   # 3.74 — magnitude/length of the vector
```

Vector addition and scaling are what make "move the parameters a little in this direction" (training) and "combine two embeddings" (some retrieval/averaging techniques) well-defined operations rather than hand-wavy ideas.

## Gotchas

- Two vectors need to be the **same dimensionality** to be added, subtracted, or dot-producted — a common source of shape-mismatch errors when working with real ML code, since it's easy to lose track of a vector's exact size several transformations later.
- A vector's raw magnitude can be misleading on its own — two embeddings can point in very similar directions (semantically similar) while having different lengths, which is exactly why similarity is usually measured via the *angle* between vectors (cosine similarity, built on the dot product) rather than raw distance.

## Related
- [[03-dot-product|dot-product]]
- [[02-matrices|matrices]]
- [[03-llms|llms]] — embeddings are vectors
