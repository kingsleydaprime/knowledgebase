# Number of Connected Components in an Undirected Graph

**LeetCode 323** · Graphs · concept: [[10-union-find|union-find]]

## Problem

Given `n` nodes and an edge list, count the connected components.

## Approach — Union-Find (optimal)

Start with `n` isolated components. Each edge that **joins two different** components reduces the count by one; an edge within an already-connected component changes nothing.

```python
def countComponents(n, edges):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count = n
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:                       # merged two distinct components
            parent[ra] = rb
            count -= 1
    return count
```

**Time O((n + e) · α(n)) ≈ O(n + e), space O(n).**

## Counting down from n

Every real merge (`union` of two different roots) drops the component count by one; redundant edges (same component) don't. Starting at `n` and decrementing on each successful union lands on the exact number of components — no final pass needed.

## Alternative — DFS/BFS

Loop over nodes, run a traversal from each unvisited one, count launches (like [[080-number-of-islands|Number of Islands]]). Also O(n + e). Union-Find shines when edges **stream in** or you interleave connectivity queries.

## Key insight

**Count components → Union-Find, starting at n and decrementing per successful merge** (or flood-fill and count launches). Union-Find is the natural choice for dynamic connectivity; a traversal is fine for a one-shot count.

## Related
- concept: [[10-union-find|union-find]]
- relative: [[080-number-of-islands|Number of Islands]] (traversal version)
- prev: [[089-redundant-connection|Redundant Connection]] · next: [[091-graph-valid-tree|Graph Valid Tree]]
