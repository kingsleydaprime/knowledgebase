# Graph Valid Tree

**LeetCode 261** · Graphs · concept: [[10-union-find|union-find]]

## Problem

Given `n` nodes and an edge list, return whether they form a **valid tree** — connected and acyclic.

## The two conditions

A graph on `n` nodes is a tree iff **both** hold:

1. Exactly **n − 1 edges** (fewer → disconnected; more → guaranteed cycle).
2. **No cycle** (equivalently, fully connected — with n−1 edges, acyclic ⇔ connected).

## Approach — Union-Find (optimal)

Check the edge count, then `union` every edge; if any edge connects two **already-connected** nodes, there's a cycle → not a tree.

```python
def validTree(n, edges):
    if len(edges) != n - 1:                # necessary condition for a tree
        return False
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False                   # cycle detected
        parent[ra] = rb
    return True                            # n-1 edges + no cycle => connected tree
```

**Time O(n · α(n)) ≈ O(n), space O(n).**

## Why n−1 edges + no cycle ⇒ connected

With the edge count fixed at exactly n−1, "acyclic" and "connected" become equivalent — you can't have n−1 edges, no cycle, *and* a disconnected graph (that would need fewer edges in some component). So checking the count plus no-cycle is sufficient; you don't separately verify connectivity.

## Key insight

**Tree = (n−1 edges) + (no cycle).** Union-Find delivers the cycle check; the edge-count guard makes connectivity automatic. A compact synthesis of counting and cycle detection.

## Related
- concept: [[10-union-find|union-find]]
- relatives: [[089-redundant-connection|Redundant Connection]], [[090-number-of-connected-components|Connected Components]]
- prev: [[090-number-of-connected-components|Number of Connected Components]] · next: [[092-word-ladder|Word Ladder]]
