---
id: 182bac82-4bd3-4c3e-b2ac-773822661071
---

# Vectors

A vector is an ordered list of numbers.

## What a vector is
<!-- bite: 5d7b26d8-c899-47b7-9156-6001c6d4efe1 -->

A vector is an ordered list of numbers: `[0.2, -1.4, 3.0]`. That's the entire mechanical definition — what makes vectors matter for ML is what they're used to *represent*.

Next: the things a vector stands for in ML.

## What a vector represents in ML
<!-- bite: 50551e3f-7dd0-44da-9edb-7a28a471bc0d -->

Almost everything a model touches gets turned into a vector first:

- **A data point** — a row of features (a house's square footage, age, location, price → one vector per house).
- **A word, sentence, or document** — an "embedding," a vector positioned so that similar meanings sit close together in the space (see [[03-dot-product|dot-product]] for how "close" is measured, and [[ai-engineering/02-how-llms-work/index|llms]] for embeddings in context).
- **A direction to move in** — during training, the update applied to a model's parameters at each step is itself a vector (see [[02-gradients|gradients]]).
- **An image, flattened** — a grid of pixel values reshaped into one long vector (or, more commonly today, processed through a structure that preserves the 2D layout — but the underlying representation is still numeric and vector-like at each stage).

```python
import numpy as np
house = np.array([1800, 15, 2])   # [sqft, age_years, distance_to_city_km]
```

## Geometric intuition — a vector is a point, and a direction
<!-- bite: 32bcb658-16b2-4f90-991b-6726d413ff66 -->

A vector can be read two ways, both useful: as a **point** in space (this specific house sits at this coordinate in feature-space), or as an **arrow** from the origin to that point (a direction and a magnitude). The second reading is what makes "vectors that point in similar directions represent similar things" a meaningful statement rather than just a numerical coincidence — see [[03-dot-product|dot-product]] for how that similarity is actually computed.

## Dimensionality
<!-- bite: e9fb8022-2334-4b6a-8b10-4c20aeb5e444 -->

The number of entries in a vector is its dimensionality. A house-price vector might have 3-10 dimensions (a handful of features); a modern LLM's embedding vectors commonly have hundreds to low thousands of dimensions — far too many to visualize directly, but the same arithmetic (addition, scaling, dot products) applies regardless of how many dimensions there are.

## Basic operations
<!-- bite: f6337c6f-dd5f-4eeb-be53-5f1621c8f1c3 -->

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

a + b        # [5, 7, 9]   — element-wise addition
a * 2        # [2, 4, 6]   — scaling
np.linalg.norm(a)   # 3.74 — magnitude/length of the vector
```

Vector addition and scaling are what make "move the parameters a little in this direction" (training) and "combine two embeddings" (some retrieval/averaging techniques) well-defined operations rather than hand-wavy ideas.

## Gotchas
<!-- bite: d8f81e70-ddb5-4716-8761-3b2ba417a214 -->

- Two vectors need to be the **same dimensionality** to be added, subtracted, or dot-producted — a common source of shape-mismatch errors when working with real ML code, since it's easy to lose track of a vector's exact size several transformations later.
- A vector's raw magnitude can be misleading on its own — two embeddings can point in very similar directions (semantically similar) while having different lengths, which is exactly why similarity is usually measured via the *angle* between vectors (cosine similarity, built on the dot product) rather than raw distance.

## Check your understanding
<!-- bite: 63365538-2bec-43d6-9663-635676668291 -->

Try each one before you open the answer.

1. <!-- q: mcq id="2c3c8853" -->
   Which of these does ML turn into a vector? Choose all that apply.

   - [x] One house's features (square footage, age, distance)
   - [x] A word or sentence (an embedding)
   - [x] The update applied to the parameters in one training step
   - [x] An image, flattened into one long list of pixel values

   <details><summary>Answer</summary>

   All four. Almost everything a model touches becomes a vector first: a data point, an embedding, a direction to move in, or a flattened image.

   </details>

2. <!-- q: exact id="f99ef63b" answer="3" accept="three" -->
   What is the dimensionality of the vector `[1800, 15, 2]`?

   <details><summary>Answer</summary>

   3. The dimensionality is the number of entries in the vector.

   </details>

3. <!-- q: gap id="0c4bc9a8" answers="5;7;9" -->
   Fill in the gaps. With `a = [1, 2, 3]` and `b = [4, 5, 6]`, `a + b` is `[___, ___, ___]`.

   <details><summary>Answer</summary>

   `[5, 7, 9]`. Addition is element-wise: 1 + 4, 2 + 5, 3 + 6.

   </details>

4. <!-- q: mcq id="871044bc" -->
   You try to add a vector of length 3 to a vector of length 4. What happens?

   - [ ] You get a vector of length 7
   - [ ] The shorter one is padded with zeros
   - [x] It is an error: both vectors must have the same dimensionality

   <details><summary>Answer</summary>

   It's an error. Adding, subtracting or taking a dot product needs both vectors to be the same length. Losing track of a vector's size is a common source of shape errors in real ML code.

   </details>

5. <!-- q: open id="baa46390" -->
   A vector can be read as a point or as an arrow. Why is the arrow reading useful when comparing two embeddings?

   <details><summary>Answer</summary>

   As an arrow, a vector has a direction. Vectors pointing in similar directions represent similar things, so "how similar are these two embeddings" becomes "how small is the angle between them". That is why similarity is usually measured by the angle (cosine similarity), not by raw length.

   </details>

## Related
<!-- bite: 62dbafa4-c999-4032-b382-9a573bf47eed -->
- [[03-dot-product|dot-product]]
- [[02-matrices|matrices]]
- [[ai-engineering/02-how-llms-work/index|llms]] — embeddings are vectors
