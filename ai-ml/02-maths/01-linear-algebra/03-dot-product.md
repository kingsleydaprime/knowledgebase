# Dot Product

The dot product of two vectors multiplies corresponding elements and sums the results: `[a,b,c] · [d,e,f] = a*d + b*e + c*f`. Mechanically it's one line of arithmetic; conceptually it's the single most-repeated operation in ML, because it measures **how much two vectors point in the same direction**.

## The computation

```python
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.dot(a, b)   # 1*4 + 2*5 + 3*6 = 32
```

## What it means

A large positive dot product means the two [[01-vectors|vectors]] are strongly aligned (pointing in similar directions); near zero means they're roughly unrelated (perpendicular, in the geometric sense); negative means they point in opposing directions. This is why "similarity" between two embeddings — two pieces of text, two images, a search query and a document — is usually computed as a dot product (or its length-normalized cousin, **cosine similarity**, which divides out each vector's magnitude so only the angle between them matters, not their raw scale).

```
similar meaning        -> embeddings point similar directions -> large dot product
unrelated meaning       -> embeddings roughly perpendicular    -> dot product near zero
opposite meaning/intent -> embeddings point opposite directions -> negative dot product
```

## Where this shows up in practice

- **Semantic search / RAG** — comparing a query's embedding against every document's embedding via dot product to find the closest matches (see [[04-other-model-types|other-model-types]] for embeddings more broadly).
- **Attention in transformers** — an LLM computing how much every token should influence every other token is, mechanically, a large batch of dot products between token vectors (see [[03-llms|llms]]).
- **A single neuron's computation** — a layer's output for one unit is the dot product of the incoming vector with that unit's row of weights, plus a bias term — the building block that [[04-matrix-multiplication|matrix-multiplication]] batches across an entire layer at once.

## Gotchas

- Raw dot product conflates **direction** and **magnitude** — two vectors can point in nearly the same direction but have very different dot products just because one has a larger magnitude. When you specifically want "how similar in meaning," cosine similarity (dot product divided by both vectors' magnitudes) is usually the more honest measure; raw dot product is used when magnitude is itself meaningful (e.g. some attention formulations).
- Dot product is only defined between vectors of the **same length** — a shape mismatch here is a common bug when embeddings from two different models (with different output dimensions) get compared directly.

## Related
- [[01-vectors|vectors]]
- [[04-matrix-multiplication|matrix-multiplication]]
