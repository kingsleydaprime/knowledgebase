# Redundant Connection

**LeetCode 684** · Graphs · concept: [[10-union-find|union-find]]

## Problem

A tree of `n` nodes had **one extra edge** added, forming exactly one cycle. Return that edge (the last one in the input that completes the cycle).

## Approach — Union-Find, catch the cycle-closing edge (optimal)

Process edges in order, `union`-ing their endpoints. The edge whose two endpoints are **already connected** is the one that closes the cycle — the redundant edge. [[10-union-find|Union-Find]]'s `union` returns `False` in exactly that case.

```python
def findRedundantConnection(edges):
    parent = list(range(len(edges) + 1))   # 1-indexed nodes
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False                   # already connected -> this edge makes a cycle
        parent[ra] = rb
        return True

    for a, b in edges:
        if not union(a, b):
            return [a, b]                  # first cycle-closing edge (last such in input)
```

**Time O(n · α(n)) ≈ O(n), space O(n).**

## Why Union-Find nails this

Adding an edge between two nodes **already in the same component** must create a cycle — there was already a path between them. Union-Find answers "same component?" in near-O(1), so the redundant edge is spotted the instant its `union` fails. A DFS cycle-detection works too but is clumsier for "which edge."

## Key insight

**"The edge that creates a cycle" → Union-Find, where a failed `union` (endpoints already connected) *is* that edge.** This is the poster-child use of Union-Find and the same cycle logic behind Graph Valid Tree and Kruskal's MST.

## Related
- concept: [[10-union-find|union-find]]
- relatives: [[091-graph-valid-tree|Graph Valid Tree]], [[090-number-of-connected-components|Connected Components]]
- prev: [[088-course-schedule-ii|Course Schedule II]] · next: [[090-number-of-connected-components|Number of Connected Components]]
