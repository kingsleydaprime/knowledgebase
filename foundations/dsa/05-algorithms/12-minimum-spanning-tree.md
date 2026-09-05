# Module: Minimum Spanning Tree (Prim's & Kruskal's)

Welcome to the **Minimum Spanning Tree (MST)** module. Given a connected, undirected graph with weighted edges, a **Spanning Tree** is a sub-graph that connects all $V$ vertices using **exactly $V - 1$ edges without forming any cycles**.

A **Minimum Spanning Tree (MST)** is the spanning tree that achieves the **minimum possible sum of total edge weights**.

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
from foundations.dsa.04-data-structures.10-union-find import UnionFind

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

## Related Modules
- [[10-union-find|Union-Find]] — Core engine powering Kruskal's algorithm
- [[08-heaps|Heaps & Priority Queues]] — Core engine powering Prim's algorithm
- [[06-dijkstra|Dijkstra's Algorithm]] — Contrast between shortest path vs. minimum spanning tree
