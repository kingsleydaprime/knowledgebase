---
id: d17eec55-f217-41e6-a8dd-e80cdb4c4ae7
---

# Dot Product

The dot product multiplies two vectors pair by pair and adds the results.

## What the dot product is
<!-- bite: 7372d249-b499-4cc3-8127-307f279b5c63 -->

The dot product of two vectors multiplies corresponding elements and sums the results: `[a,b,c] · [d,e,f] = a*d + b*e + c*f`. Mechanically it's one line of arithmetic; conceptually it's the single most-repeated operation in ML, because it measures **how much two vectors point in the same direction**.

Next: the computation, then what the number means.

## The computation
<!-- bite: 07e55561-6a1e-4b5f-ab1d-7ac6784f5dde -->

```python
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.dot(a, b)   # 1*4 + 2*5 + 3*6 = 32
```

## What it means
<!-- bite: bcc421cb-5b1e-4076-b365-44baf7f5d092 -->

A large positive dot product means the two [[01-vectors|vectors]] are strongly aligned (pointing in similar directions); near zero means they're roughly unrelated (perpendicular, in the geometric sense); negative means they point in opposing directions. This is why "similarity" between two embeddings — two pieces of text, two images, a search query and a document — is usually computed as a dot product (or its length-normalized cousin, **cosine similarity**, which divides out each vector's magnitude so only the angle between them matters, not their raw scale).

```text
similar meaning        -> embeddings point similar directions -> large dot product
unrelated meaning       -> embeddings roughly perpendicular    -> dot product near zero
opposite meaning/intent -> embeddings point opposite directions -> negative dot product
```

## Where this shows up in practice
<!-- bite: 1f421f8e-977f-4417-bf55-89056c655af4 -->

- **Semantic search / RAG** — comparing a query's embedding against every document's embedding via dot product to find the closest matches (see [[ai-engineering/03-the-model-landscape|other-model-types]] for embeddings more broadly).
- **Attention in transformers** — an LLM computing how much every token should influence every other token is, mechanically, a large batch of dot products between token vectors (see [[ai-engineering/02-how-llms-work/index|llms]]).
- **A single neuron's computation** — a layer's output for one unit is the dot product of the incoming vector with that unit's row of weights, plus a bias term — the building block that [[04-matrix-multiplication|matrix-multiplication]] batches across an entire layer at once.

## Gotchas
<!-- bite: 5166df00-c41d-48e0-b5d0-9d6b8f4d0da1 -->

- Raw dot product conflates **direction** and **magnitude** — two vectors can point in nearly the same direction but have very different dot products just because one has a larger magnitude. When you specifically want "how similar in meaning," cosine similarity (dot product divided by both vectors' magnitudes) is usually the more honest measure; raw dot product is used when magnitude is itself meaningful (e.g. some attention formulations).
- Dot product is only defined between vectors of the **same length** — a shape mismatch here is a common bug when embeddings from two different models (with different output dimensions) get compared directly.

## Related
<!-- bite: bc3aba98-86b6-44a0-a9f7-c35f26757cf7 -->
- [[01-vectors|vectors]]
- [[04-matrix-multiplication|matrix-multiplication]]
