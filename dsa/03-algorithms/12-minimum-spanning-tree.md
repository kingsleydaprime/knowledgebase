# Module: Minimum Spanning Tree (Prim's & Kruskal's)

Welcome to the **Minimum Spanning Tree (MST)** module. Given a connected, undirected graph with weighted edges, a **Spanning Tree** is a sub-graph that connects all $V$ vertices using **exactly $V - 1$ edges without forming any cycles**.

A **Minimum Spanning Tree (MST)** is the spanning tree that achieves the **minimum possible sum of total edge weights**.

---

## Before you start

- You know what a spanning tree is and that a connected graph has many — [[06-graphs/03-subgraphs-trees-and-forests|subgraphs, trees and forests]].
- You know union-find — [[10-union-find|union-find]] — and heaps — [[08-heaps|heaps]].
- You have seen a greedy argument — [[10-greedy-algorithms|greedy algorithms]].

**After this lesson you will be able to:**

1. Implement **Prim's** and **Kruskal's**, and say which data structure each one needs and why.
2. State the **cut property**, which is the single fact making both correct.
3. Verify an MST is genuinely minimal, by exhaustive search on a small graph.
4. Explain when the MST is **unique**, and what happens when edge weights tie.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 2 checks minimality exhaustively.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine laying **Fiber-Optic Internet Cables** between 5 regional cities:

```
                  [ City B ]
                 /    |    \
     $10M       /     |     \  $15M
               /      |      \
    [ City A ]       $5M      [ City C ]
               \      |      /
     $12M       \     |     /  $8M
                 \    |    /
                  [ City D ]
```

- Connecting every single pair of cities with direct cable lines would cost tens of millions of dollars in redundant wires.
- An **MST** finds the cheapest total cable layout that ensures every city can communicate with every other city without creating redundant closed loops (cycles).

### Production Applications:
1. **Telecommunications & Utilities**: Designing water pipe networks, electrical grids, and internet cabling.
2. **Cluster Analysis**: Single-linkage hierarchical clustering in Machine Learning.
3. **Road System Construction**: Planning highway connections between towns with minimal asphalt cost.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Spanning Tree** | A tree that touches every vertex in a graph using $V - 1$ edges. | A barebones highway map connecting all cities. |
| **MST** | The spanning tree with the absolute smallest total edge weight sum. | The cheapest possible highway map. |
| **Cut Property** | The mathematical rule proving that the cheapest edge crossing any boundary split belongs in the MST. | Greedily choosing the cheapest bridge across a river. |
| **Kruskal's Algorithm** | Global edge sorting + [[10-union-find|Union-Find]] to build the MST edge-by-edge. | Adding cheapest roads one-by-one unless they form a loop. |
| **Prim's Algorithm** | Local tree expansion using a [[08-heaps|Min-Heap]] to grow one MST from a starting node. | Expanding an electrical grid outward from a power station. |

---

## 3. Technical Deep Dive: The Two Classic MST Algorithms

### 1. Kruskal's Algorithm (Sort Edges + Union-Find)

**Strategy**: Sort **all edges** globally by weight. Greedily add the cheapest edge unless both endpoints are already connected (which would create a cycle!).

```python
from foundations.dsa.02-data-structures.10-union-find import UnionFind

def kruskal_mst(num_nodes: int, edges: list) -> int:
    """Calculates MST total cost using Kruskal's Algorithm.
    
    edges format: [(weight, u, v)]
    """
    # 1. Sort edges globally by weight ascending: O(E log E)
    edges.sort()
    
    uf = UnionFind(num_nodes)
    total_cost = 0
    edges_used = 0
    
    # 2. Iterate through cheapest edges first
    for weight, u, v in edges:
        # Union-Find returns True if u and v were NOT connected (no cycle)
        if uf.union(u, v):
            total_cost += weight
            edges_used += 1
            if edges_used == num_nodes - 1:
                break  # MST is complete!
                
    return total_cost if edges_used == num_nodes - 1 else -1
```

---

### 2. Prim's Algorithm (Min-Heap Tree Growth)

**Strategy**: Start from any vertex. Use a **Min-Heap** to repeatedly attach the cheapest edge connecting an unvisited vertex to the growing tree.

```python
import heapq

def prim_mst(num_nodes: int, adj_list: dict) -> int:
    """Calculates MST total cost using Prim's Algorithm.
    
    adj_list format: { u: [(weight, v), ...] }
    """
    visited = set()
    min_heap = [(0, 0)]  # (weight, start_node)
    total_cost = 0
    
    while min_heap and len(visited) < num_nodes:
        weight, u = heapq.heappop(min_heap)
        
        if u in visited:
            continue  # Skip stale heap entries
            
        visited.add(u)
        total_cost += weight
        
        for edge_weight, neighbor in adj_list[u]:
            if neighbor not in visited:
                heapq.heappush(min_heap, (edge_weight, neighbor))
                
    return total_cost if len(visited) == num_nodes else -1
```

---

## 4. Prim's vs. Kruskal's Comparison

| Feature | Kruskal's Algorithm | Prim's Algorithm |
| :--- | :--- | :--- |
| **Execution Approach** | Processes edges globally across entire graph. | Grows a single connected tree outward from a root node. |
| **Core Data Structures** | **Union-Find** + Edge Array Sorting. | **Min-Heap** + Visited Set. |
| **Time Complexity** | **$O(E \log E)$** | **$O(E \log V)$** |
| **Best Graph Domain** | **Sparse Graphs** ($E \approx V$). | **Dense Graphs** ($E \approx V^2$). |

---

## 5. Time & Space Complexity Summary

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | **$O(E \log V)$** | Dominant work is edge sorting ($O(E \log E) = O(E \log V)$) or Heap operations. |
| **Space Complexity** | **$O(V + E)$** | Memory for Union-Find parent array, Heap, and adjacency structures. |

---

## Implementation — complete runnable example

**Runnable example:** save as `mst.py` in any empty directory and run `python3 mst.py`. Standard library only; writes no files.

```python
"""Prim's and Kruskal's, checked against exhaustive search."""
import heapq
from collections import defaultdict
from itertools import combinations


class DSU:
    def __init__(self, items):
        self.parent = {i: i for i in items}
        self.rank = {i: 0 for i in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]      # path compression
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                       # already connected: a cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def vertices_of(edges):
    return sorted({v for u, w, _ in edges for v in (u, w)})


def kruskal(edges):
    """Sort every edge, take it if it joins two different components."""
    dsu = DSU(vertices_of(edges))
    chosen, total = [], 0
    for u, v, w in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
        if dsu.union(u, v):
            chosen.append((u, v, w))
            total += w
    return chosen, total


def prim(edges, start=None):
    """Grow one tree, always taking the cheapest edge leaving it."""
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    start = start or vertices_of(edges)[0]
    seen = {start}
    pq = sorted(adj[start])
    heapq.heapify(pq)
    chosen, total = [], 0
    while pq and len(seen) < len(adj):
        w, v = heapq.heappop(pq)
        if v in seen:
            continue
        seen.add(v)
        total += w
        chosen.append(v)
        for nw, nv in adj[v]:
            if nv not in seen:
                heapq.heappush(pq, (nw, nv))
    return chosen, total


def brute_force_mst(edges):
    """Every spanning tree, exhaustively. The oracle."""
    verts = vertices_of(edges)
    n = len(verts)
    best = float("inf")
    for combo in combinations(edges, n - 1):
        dsu = DSU(verts)
        if all(dsu.union(u, v) for u, v, _ in combo):          # n-1 edges, no cycle
            best = min(best, sum(w for _, _, w in combo))
    return best


if __name__ == "__main__":
    E = [("A", "B", 4), ("A", "C", 8), ("B", "C", 11), ("B", "D", 8),
         ("C", "E", 7), ("D", "E", 2), ("D", "F", 4), ("E", "F", 14),
         ("D", "G", 9), ("F", "G", 10)]

    print("Block 1 - both algorithms, same total weight")
    k_edges, k_total = kruskal(E)
    _, p_total = prim(E)
    print(f"  Kruskal chose {len(k_edges)} edges, total weight {k_total}")
    for u, v, w in k_edges:
        print(f"      {u}-{v} ({w})")
    print(f"  Prim's total weight: {p_total}")
    assert k_total == p_total
    assert len(k_edges) == len(vertices_of(E)) - 1
    print(f"  n-1 = {len(vertices_of(E))-1} edges, as any spanning tree must have")

    print()
    print("Block 2 - is it actually minimal? Checked exhaustively")
    best = brute_force_mst(E)
    print(f"  exhaustive search over all spanning trees: minimum {best}")
    print(f"  Kruskal: {k_total}   Prim: {p_total}   agree: {best == k_total == p_total}")
    assert best == k_total == p_total
    print("  not a proof, but it rules out the obvious way to be wrong")

    print()
    print("  and Prim's answer does not depend on where it starts:")
    for s in vertices_of(E):
        _, t = prim(E, s)
        print(f"    from {s}: total {t}", end="")
    print()
    assert len({prim(E, s)[1] for s in vertices_of(E)}) == 1

    print()
    print("Block 3 - the cut property, which is why greedy works here")
    print("  Split the vertices into any two groups. The CHEAPEST edge crossing")
    print("  that split is in some MST. Both algorithms are applications of this:")
    print("    Kruskal: the cheapest edge joining two different components")
    print("    Prim:    the cheapest edge leaving the tree built so far")
    cut = {"A", "B"}
    crossing = [(u, v, w) for u, v, w in E if (u in cut) != (v in cut)]
    cheapest = min(crossing, key=lambda e: e[2])
    print(f"  cut {sorted(cut)} | rest: crossing edges {[(u,v,w) for u,v,w in crossing]}")
    print(f"    cheapest crossing edge: {cheapest}")
    print(f"    is it in Kruskal's tree? "
          f"{any((u,v)==(cheapest[0],cheapest[1]) for u,v,_ in k_edges)}")
    assert any((u, v) == (cheapest[0], cheapest[1]) for u, v, _ in k_edges)

    print()
    print("Block 4 - uniqueness, and what ties do")
    distinct = [("A", "B", 1), ("B", "C", 2), ("A", "C", 3)]
    tied = [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)]
    for label, es in [("all distinct weights", distinct), ("all weights equal", tied)]:
        verts = vertices_of(es)
        trees = []
        for combo in combinations(es, len(verts) - 1):
            dsu = DSU(verts)
            if all(dsu.union(u, v) for u, v, _ in combo):
                trees.append((sum(w for _, _, w in combo), combo))
        best_w = min(t[0] for t in trees)
        minimal = [t for t in trees if t[0] == best_w]
        print(f"  {label}: {len(trees)} spanning trees, {len(minimal)} of minimum weight {best_w}")
    assert len([1 for c in combinations(distinct, 2)
                if all(DSU(vertices_of(distinct)).union(u, v) for u, v, _ in c)]) >= 1
    print("  with all weights DISTINCT the MST is unique.")
    print("  With ties there can be several, all equally minimal - so an MST")
    print("  algorithm's exact edge set is not something to assert on.")

    print()
    print("Block 5 - which to reach for")
    print("   Kruskal: sort all edges once, union-find     -> O(E log E), wants an EDGE LIST")
    print("   Prim:    grow from one vertex, min-heap      -> O(E log V), wants an ADJACENCY LIST")
    print("   sparse graph (E ~ V)  -> Kruskal is usually simpler and fine")
    print("   dense graph  (E ~ V^2) -> Prim, especially with a better heap")
    sparse = len(E) <= 2 * len(vertices_of(E))
    print(f"  this graph: V={len(vertices_of(E))}, E={len(E)}, sparse={sparse}")

    print()
    print("mst: passed")
```

Expected output:

```
Block 1 - both algorithms, same total weight
  Kruskal chose 6 edges, total weight 34
      D-E (2)
      A-B (4)
      D-F (4)
      C-E (7)
      A-C (8)
      D-G (9)
  Prim's total weight: 34
  n-1 = 6 edges, as any spanning tree must have

Block 2 - is it actually minimal? Checked exhaustively
  exhaustive search over all spanning trees: minimum 34
  Kruskal: 34   Prim: 34   agree: True
  not a proof, but it rules out the obvious way to be wrong

  and Prim's answer does not depend on where it starts:
    from A: total 34    from B: total 34    from C: total 34    from D: total 34    from E: total 34    from F: total 34    from G: total 34

Block 3 - the cut property, which is why greedy works here
  Split the vertices into any two groups. The CHEAPEST edge crossing
  that split is in some MST. Both algorithms are applications of this:
    Kruskal: the cheapest edge joining two different components
    Prim:    the cheapest edge leaving the tree built so far
  cut ['A', 'B'] | rest: crossing edges [('A', 'C', 8), ('B', 'C', 11), ('B', 'D', 8)]
    cheapest crossing edge: ('A', 'C', 8)
    is it in Kruskal's tree? True

Block 4 - uniqueness, and what ties do
  all distinct weights: 3 spanning trees, 1 of minimum weight 3
  all weights equal: 3 spanning trees, 3 of minimum weight 2
  with all weights DISTINCT the MST is unique.
  With ties there can be several, all equally minimal - so an MST
  algorithm's exact edge set is not something to assert on.

Block 5 - which to reach for
   Kruskal: sort all edges once, union-find     -> O(E log E), wants an EDGE LIST
   Prim:    grow from one vertex, min-heap      -> O(E log V), wants an ADJACENCY LIST
   sparse graph (E ~ V)  -> Kruskal is usually simpler and fine
   dense graph  (E ~ V^2) -> Prim, especially with a better heap
  this graph: V=7, E=10, sparse=True

mst: passed
```

Block 2 is the check worth having: exhaustive search over every spanning tree confirms both greedy algorithms found a genuinely minimum one.

## 6. Common Pitfalls & Traps

1. **MST is for Undirected Graphs**: Directed graphs use a completely different, more complex structure called a *Minimum Arborescence* (Edmonds' Algorithm).
2. **MST vs. Shortest Path**: An MST minimizes **total global edge weight**, NOT individual path lengths between nodes! A path between two nodes in an MST can be much longer than their shortest path in the original graph (use [[06-dijkstra|Dijkstra]] for shortest paths).
3. **Disconnected Graphs**: If a graph has isolated components, no single spanning tree exists ($V - 1$ edges cannot be placed).

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: How many edges are in a Minimum Spanning Tree of a connected graph with $V$ vertices?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Exactly <b>$V - 1$ edges</b>. Adding an $V$-th edge would create a cycle, and having fewer than $V - 1$ edges leaves vertices disconnected.</details>

2. **Question**: Why is Kruskal's Algorithm preferred over Prim's Algorithm for sparse graphs with an explicit edge list?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Kruskal's operates directly on a flat edge list using simple sorting and ultra-fast <b>Union-Find</b> operations, making it extremely easy to implement and fast on sparse graphs.</details>

3. **Question**: Does an MST guarantee the shortest travel path between two specific cities?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>No!</b> An MST minimizes total infrastructure cost for the whole network, not individual origin-to-destination paths. Use <b>Dijkstra's Algorithm</b> for point-to-point shortest paths.</details>

---

## Practice — independent task

Implement `clustering(points, k)` — single-linkage clustering, which is an MST in disguise.

1. Build the complete graph on the points, weighted by Euclidean distance.
2. Run Kruskal's, but **stop when exactly $k$ components remain** instead of 1. Those components are your clusters.
3. Report the **spacing**: the weight of the next edge Kruskal would have taken. That is the distance between the two closest clusters, and single-linkage clustering maximises it.
4. Verify against a direct definition: for your clustering, compute the minimum distance between any two points in different clusters, and confirm it equals the spacing you reported.
5. Then show the method's known weakness — **chaining**. Construct points in two obvious blobs joined by a thin line of intermediate points, and show single-linkage merging the blobs rather than separating them. Explain why the MST-based criterion causes that.

**Edge cases:** $k = 1$ (the whole MST); $k = n$ (every point its own cluster, spacing is the smallest edge); duplicate points at distance 0; $k > n$.

**Done when:** your spacing matches the direct inter-cluster minimum for several random point sets, and your chaining example demonstrably produces the clustering you predicted before running it.

## Before moving on

You can implement both algorithms, state the cut property, and verify minimality.

**Recap:** an MST is a spanning tree of minimum total weight, with $n-1$ edges; **Kruskal** sorts all edges and adds any that joins two components, using union-find, $O(E\log E)$, wants an edge list; **Prim** grows one tree taking the cheapest leaving edge, using a min-heap, $O(E\log V)$, wants an adjacency list; both are justified by the **cut property** — the cheapest edge across any cut belongs to some MST; the MST is unique when all weights are distinct.

**Next:** [[13-bit-manipulation|Bit Manipulation]], or back to [[index|the algorithms index]].

## Related Modules
- [[10-union-find|Union-Find]] — Core engine powering Kruskal's algorithm
- [[08-heaps|Heaps & Priority Queues]] — Core engine powering Prim's algorithm
- [[06-dijkstra|Dijkstra's Algorithm]] — Contrast between shortest path vs. minimum spanning tree
