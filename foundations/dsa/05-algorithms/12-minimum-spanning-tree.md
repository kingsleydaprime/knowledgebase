# Minimum Spanning Tree (Prim's & Kruskal's)

A **spanning tree** of a connected, undirected graph is a subset of edges that connects all V vertices with exactly V−1 edges and no cycle — a tree that "spans" every node. The **minimum** spanning tree (MST) is the one whose total edge weight is smallest. It's the answer to "connect all these points/cities/nodes as cheaply as possible": network cabling, road/pipe layout, clustering.

## The key insight both algorithms exploit: the cut property

**Cut property:** for any way of splitting the vertices into two groups, the cheapest edge crossing that split is safe to include in *some* MST. Both classic algorithms are greedy and both are correct *because* of this property — they just apply it from different angles: Prim's grows one connected blob outward across the cut between "in the tree" and "not yet"; Kruskal's considers the globally cheapest remaining edge and takes it unless it's useless (forms a cycle).

An MST always has exactly **V−1 edges**. If the graph is disconnected, no spanning tree exists (you'd get a spanning *forest*).

## Prim's algorithm — grow one tree with a heap

Start from any vertex; repeatedly add the **cheapest edge that connects a new vertex to the tree you've built so far**. A [[foundations/dsa/04-data-structures/08-heaps|min-heap]] of candidate edges (keyed by weight) makes "cheapest edge leaving the tree" fast.

```python
import heapq

def prim(n, adj):                          # adj[u] = list of (weight, v)
    visited = set()
    heap = [(0, 0)]                        # (weight, start_node)
    total = 0
    while heap and len(visited) < n:
        w, u = heapq.heappop(heap)
        if u in visited:                   # lazy deletion — skip stale entries
            continue
        visited.add(u)
        total += w
        for weight, v in adj[u]:
            if v not in visited:
                heapq.heappush(heap, (weight, v))
    return total if len(visited) == n else -1   # -1 => disconnected
```

Note the **lazy deletion** — because `heapq` has no decrease-key, you push duplicate candidate edges and skip any popped node that's already in the tree. Same trick as [[06-dijkstra|Dijkstra]], which Prim's structurally resembles (the only difference: Dijkstra keys the heap by *distance from source*, Prim's by *edge weight to the tree*).

## Kruskal's algorithm — sort edges, union greedily

Sort **all** edges by weight ascending; walk them cheapest-first and add an edge iff its two endpoints are in **different** components (adding it would connect two blobs, not create a cycle). "Same component?" is exactly what [[foundations/dsa/04-data-structures/10-union-find|Union-Find]] answers in near-O(1).

```python
def kruskal(n, edges):                     # edges: list of (weight, u, v)
    uf = UnionFind(n)
    total, used = 0, 0
    for w, u, v in sorted(edges):          # cheapest first
        if uf.union(u, v):                 # returns False if u, v already connected (cycle)
            total += w
            used += 1
    return total if used == n - 1 else -1  # fewer than n-1 edges => disconnected
```

The whole algorithm is "sorted edges + Union-Find's cycle check." `union` returning `False` (already connected) is precisely "this edge would form a cycle, skip it."

## Prim's vs Kruskal's — which to reach for

| | Prim's | Kruskal's |
|---|---|---|
| Grows | one tree outward from a start | a forest that merges into one tree |
| Core structure | [[foundations/dsa/04-data-structures/08-heaps\|min-heap]] | [[foundations/dsa/04-data-structures/10-union-find\|Union-Find]] + sort |
| Complexity | O(E log V) | O(E log E) ≈ O(E log V) (dominated by the sort) |
| Best when | **dense** graphs (many edges), or edges given as adjacency | **sparse** graphs, or edges given as a flat list |

Both are O(E log V) with the standard structures, so the choice is usually about which representation you're handed. Given an edge list → Kruskal's is a two-liner over Union-Find. Given an adjacency list on a dense graph → Prim's.

## Canonical problem (NeetCode Advanced Graphs)

- **Min Cost to Connect All Points** — the points form a complete graph with Manhattan-distance edge weights; the minimum total cost to connect them all is exactly the MST. Solvable with either algorithm — Prim's avoids materializing all O(n²) edges up front, which is the small edge Prim's has here.

## Gotchas

- **MST is for undirected graphs.** The directed analogue (minimum arborescence) is a different, harder problem.
- **Disconnected graph → no MST** — check you actually used V−1 edges (Kruskal's) or visited all V vertices (Prim's).
- **Lazy deletion in Prim's** — without skipping stale heap entries you'll double-count or loop; without *any* visited check it never terminates.
- **MST minimizes total weight, not path lengths** — the path between two nodes *in* the MST is not necessarily their shortest path in the original graph. For shortest paths use [[06-dijkstra|Dijkstra]].
- **Ties don't matter for the total** — with distinct weights the MST is unique; with ties there can be several MSTs but they all share the same minimum total.

## Related
- [[foundations/dsa/04-data-structures/10-union-find|Union-Find]] — the engine of Kruskal's
- [[foundations/dsa/04-data-structures/08-heaps|Heaps]] — the engine of Prim's
- [[06-dijkstra|Dijkstra]] — near-identical heap loop, different key (shortest path vs MST)
- [[06-graphs|Graphs]] — weighted, undirected graphs
- [[10-greedy-algorithms|Greedy]] — both algorithms are greedy, proven correct by the cut property
