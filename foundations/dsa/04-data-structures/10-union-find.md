# Union-Find (Disjoint Set Union)

Union-Find (a.k.a. Disjoint Set Union, DSU) answers one question incredibly fast, over and over, as a graph grows: **"are these two elements in the same connected group?"** — and lets you **merge two groups** in near-constant time. It maintains a partition of n elements into disjoint sets, supporting `find(x)` (which set is x in?) and `union(x, y)` (merge x's and y's sets), each in effectively O(1) once optimized.

## Why it exists — the problem it beats

You *could* answer "are x and y connected?" with a [[02-dfs|DFS/BFS]] from x. But if edges arrive **incrementally** and you must answer connectivity queries *between* insertions, re-running a traversal after every edge is O(V+E) per query — quadratic overall. Union-Find maintains connectivity **online**: each new edge is a `union`, each query a `find`, both near-constant. It's the right tool whenever the graph only ever *gains* edges (never loses them) and you care about grouping, not paths.

## The core idea: a forest of "who's my representative"

Each set is represented as a tree, and every element points to a **parent**; follow parents up and you reach a **root**, which is the set's canonical representative. Two elements are in the same set iff they share the same root.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))    # each element starts as its own root
        self.rank = [1] * n             # approximate tree height / size, for balancing

    def find(self, x):                  # which set? -> the root
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]   # path compression (halving)
            x = self.parent[x]
        return x

    def union(self, x, y):              # merge -> True if they were separate
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False                # already connected — this edge is redundant
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx             # attach the smaller tree under the larger
        self.parent[ry] = rx
        self.rank[rx] += self.rank[ry]
        return True
```

The naive version — `find` walks to the root, `union` points one root at the other — is correct but can degrade into a linked-list-shaped tree with O(n) `find`. Two optimizations fix that, and they're what make Union-Find fast:

## The two optimizations

**Union by rank/size** — always attach the *shorter* (or smaller) tree under the taller one, so the combined tree stays shallow. Without this, unions can build a degenerate O(n)-tall chain.

**Path compression** — during `find`, re-point nodes directly at (closer to) the root, so future `find`s on the same elements are faster. The version above does *path halving* (point each node at its grandparent), which is simpler than full two-pass compression and just as effective asymptotically.

Together they bring the amortized cost of each operation down to **O(α(n))**, where α is the inverse Ackermann function — which is ≤ 4 for any n you could store in the universe. Effectively constant. Using only *one* of the two optimizations gives O(log n); using neither gives O(n).

## Complexity

| Operation | Naive | + one optimization | + both |
|---|---|---|---|
| find | O(n) | O(log n) | O(α(n)) ≈ O(1) |
| union | O(n) | O(log n) | O(α(n)) ≈ O(1) |

Space is O(n) for the parent (and rank) arrays. `α(n)` is the closest thing to a "smaller than constant" you'll meet in an interview — worth being able to name.

## What it can and can't do

Union-Find is **incremental only**: it handles adding edges and querying, but has **no efficient "un-union"** (removing an edge). Problems that delete edges are usually solved by *reversing time* — process deletions in reverse so they become unions. It also tells you *whether* two nodes are connected, never the *path* between them (that's what a traversal is for).

The `union` return value is quietly powerful: it returns `False` when the two endpoints were **already connected**, which means the edge you just tried to add **closes a cycle**. That single fact powers cycle detection, redundant-edge finding, and Kruskal's MST.

## Canonical problems (NeetCode Graphs / Advanced Graphs)

- **Number of Connected Components in an Undirected Graph** — `union` every edge; the answer is the count of distinct roots (start at n, decrement each time a `union` actually merges).
- **Redundant Connection** — the first edge whose `union` returns `False` is the one that creates the cycle → the edge to remove.
- **Graph Valid Tree** — a valid tree has exactly n−1 edges and no cycle: if any `union` returns `False`, there's a cycle → not a tree.
- **Accounts Merge** — union accounts sharing any email, then group emails by root; the textbook "merge things that share an attribute" use.
- **Kruskal's MST** (*Min Cost to Connect All Points*) — sort edges by weight, `union` greedily, skip edges that would form a cycle. See [[12-minimum-spanning-tree|Minimum Spanning Tree]].

## Union-Find vs. DFS for connectivity

| | Union-Find | DFS/BFS |
|---|---|---|
| Edges arrive incrementally, query between adds | **O(α) per op** | O(V+E) per query |
| All edges known up front, one-shot component count | works | equally fine, often simpler |
| Need the actual path / traversal order | no | **yes** |
| Edge deletions | no (reverse-time trick) | recompute |

Rule of thumb: **dynamic connectivity or "group by shared property" → Union-Find; explore/path/one-shot → DFS.**

## Gotchas

- **Skipping the optimizations** turns it into a linked list — always do union-by-rank *and* path compression in interviews.
- **`union` returning `False` = cycle** — this is the detail most people forget and the key to half the problems.
- It answers **connectivity, not distance or path** — don't reach for it when you need the route.
- No efficient decremental (edge-removal) form — recognize when reverse-time processing is required.

## Related
- [[06-graphs|Graphs]] — connectivity, the problem domain
- [[12-minimum-spanning-tree|Minimum Spanning Tree]] — Kruskal's is Union-Find + sorted edges
- [[02-dfs|DFS]] / [[03-bfs|BFS]] — the traversal alternative for connectivity
- [[01-trees|Trees]] — the forest-of-trees representation
