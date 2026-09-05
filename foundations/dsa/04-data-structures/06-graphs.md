# Module: Graphs (Networks, Connections & Dependencies)

Welcome to the **Graphs** module. A **Graph** is a set of **Vertices** (nodes) connected by **Edges** (relationships).

Graphs are the ultimate generalized data structure. In fact, earlier structures you studied are simply restricted graphs:
- A [[01-trees|Tree]] is a graph with no cycles and exactly one path between any two nodes.
- A [[04-linked-lists|Linked List]] is a tree where every node has at most one child.

By removing all restrictions, graphs allow any node to connect to any other node, allow loops (cycles), and allow disconnected components.

---

## 1. Why Graphs Matter (Real-World Motivation)

An enormous number of real-world software systems are **graph problems in disguise**:

```
[ New York ] ===== (2,800 miles) ===== [ Los Angeles ]   <-- Flight Networks / GPS Maps
     |                                        |
     + ------------- (215 miles) ------------ + [ Washington D.C. ]
```

1. **GPS Navigation & Google Maps**: Intersections are vertices; roads are weighted edges (where weights represent distance or traffic delay).
2. **Social Networks (LinkedIn / Twitter)**: Users are vertices. Two-way "Friends" are undirected edges; one-way "Followers" are directed edges.
3. **Build Systems & Course Prerequisites (DAGs)**: Package `A` depends on Package `B`, which depends on Package `C`.
4. **2D Grid Mazes**: Every grid cell `(r, c)` is a vertex connected to its 4 cardinal neighbors (`up, down, left, right`).

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Real-World Example |
| :--- | :--- | :--- |
| **Vertex (Node)** | An individual entity or point in the graph. | A city, user, web page, or grid cell. |
| **Edge** | A connection or link between two vertices. | Flight path, friendship, hyperlink. |
| **Adjacent (Neighbor)** | Two vertices connected directly by an edge. | Cities sharing a direct highway. |
| **Degree** | Total edges touching a vertex. Directed graphs split this into **In-Degree** (arriving) and **Out-Degree** (leaving). | Twitter followers (In-degree) vs accounts followed (Out-degree). |
| **Path** | A sequence of connected vertices from Start $\rightarrow$ End. | Flight itinerary with layovers. |
| **Cycle** | A path that loops back to its starting vertex. | Round-trip flight `A -> B -> C -> A`. |
| **DAG** | Directed Acyclic Graph: A directed graph with **zero cycles**. | Task schedules, build systems, Git commits. |

---

## 3. The 4 Dimensions of Graphs

To pick the correct algorithm, you must identify your graph's 4 core dimensions:

```
Undirected (2-Way Street):       Directed (1-Way Street):
   (A) <----------> (B)              (A) -----------> (B)

Unweighted (Equal Cost):        Weighted (Cost Added):
   (A) ------------ (B)              (A) --[50 miles]-> (B)
```

1. **Directed vs. Undirected**:
   - **Undirected**: Edges work both ways (`A <-> B`). *Code Rule*: Must add the edge twice in code (`graph[A].append(B)` and `graph[B].append(A)`).
   - **Directed**: Edges work one-way (`A -> B`).
2. **Weighted vs. Unweighted**:
   - **Unweighted**: All edges have equal cost. (Use **[[03-bfs|BFS]]** for shortest path).
   - **Weighted**: Edges carry distances/costs. (Use **[[06-dijkstra|Dijkstra's Algorithm]]** for shortest path).
3. **Cyclic vs. Acyclic (DAG)**:
   - **Cyclic**: Contains loops. Must track a `visited` set during traversal!
   - **Acyclic (DAG)**: No loops. Can be **Topologically Sorted** (e.g. build dependencies).
4. **Sparse vs. Dense**:
   - **Sparse**: Edges ($E$) is close to Vertices ($V$). (Use **Adjacency List**).
   - **Dense**: Edges ($E$) approaches $V^2$. (Use **Adjacency Matrix**).

---

## 4. Graph Data Representations (How to Store a Graph)

There are 3 standard ways to store a graph in code:

### 1. Adjacency List (The Universal Default)
A dictionary mapping each vertex to a list of its neighbors.

```python
# Adjacency List representation in Python
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"]
}
```
- **Space**: $O(V + E)$ (Optimal for sparse graphs).
- **Pros**: Fast neighbor iteration; low memory usage.

---

### 2. Adjacency Matrix (Dense $V \times V$ Grid)
A 2D matrix where `matrix[u][v] = 1` (or weight) if an edge connects $u$ to $v$.

```
     A  B  C  D
A  [ 0, 1, 1, 0 ]
B  [ 1, 0, 0, 1 ]
C  [ 1, 0, 0, 0 ]
D  [ 0, 1, 0, 0 ]
```
- **Space**: $O(V^2)$ (Heavy memory penalty for sparse graphs).
- **Pros**: Instant $O(1)$ check to see if edge `(u, v)` exists.

---

### 3. Edge List (Array of Tuples)
A simple array storing edge tuples: `[("A", "B", 5), ("A", "C", 2), ("B", "D", 7)]`.
- **Primary Use**: Algorithms that process edges globally, like **Kruskal's Minimum Spanning Tree**.

---

## 5. Implicit Graphs (Grid Mazes Without Graph Objects)

> [!TIP]
> A 2D Grid array is secretly a Graph! You don't need to build an Adjacency List object—calculate neighbor coordinates arithmetically.

```python
def get_neighbors(r: int, c: int, rows: int, cols: int):
    """Calculates cardinal neighbors (Up, Down, Left, Right) on the fly."""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    neighbors = []
    
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        # Check boundary constraints
        if 0 <= nr < rows and 0 <= nc < cols:
            neighbors.append((nr, nc))
            
    return neighbors
```

Every grid maze problem (Islands, Flood Fill, Pathfinding) uses this implicit graph technique!

---

## 6. Graph Algorithm Decision Cheat-Sheet

| Question / Goal | Algorithm to Reach For |
| :--- | :--- |
| **Is there any path between A and B?** | **DFS** or **BFS** |
| **Shortest Path (Unweighted Graph / Grid)** | **BFS** (Breadth-First Search) |
| **Shortest Path (Weighted Graph, Non-Negative)** | **Dijkstra's Algorithm** (BFS + Min-Heap) |
| **Valid Order of Dependencies (DAG)** | **Topological Sort** |
| **Detect Cycles in Undirected Graph** | **Union-Find** or DFS |
| **Connect all points with minimum total cost** | **Minimum Spanning Tree (Prim's / Kruskal's)** |

---

## 7. Common Pitfalls & Traps

1. **Forgetting `visited` Sets**: Unlike trees, graph paths can loop. Omitting a `visited = set()` causes infinite recursive loops.
2. **Marking Visited on Dequeue vs Enqueue in BFS**: In BFS, always add a node to `visited` **immediately when enqueuing it**. Marking it on dequeue allows duplicate nodes to flood the queue.
3. **Using BFS on Weighted Graphs**: BFS assumes fewer edges = shorter path. On a weighted graph, a path with 2 edges (weights: $10+10 = 20$) can be slower than a path with 3 edges (weights: $1+1+1 = 3$). Use **Dijkstra** for weighted graphs!

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: Why is an Adjacency List preferred over an Adjacency Matrix for storing a social network like Twitter (800 million users, average 500 follows per user)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Twitter's graph is extremely <b>sparse</b>. An Adjacency Matrix requires an 800M x 800M grid (640,000 trillion cells, mostly zeros!). An Adjacency List consumes space proportional to actual edges <b>O(V + E)</b>, taking only a few gigabytes.</details>

2. **Question**: What is a DAG (Directed Acyclic Graph), and why is it required for Topological Sorting?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A DAG is a directed graph with <b>zero cycles</b>. Topological sorting orders tasks by dependencies. If a cycle exists (A depends on B, B depends on C, C depends on A), a valid topological order is logically impossible (circular dependency deadlock).</details>

3. **Question**: In an undirected graph, what critical step must be taken when populating an Adjacency List from an edge `(u, v)`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> You must append the edge in <b>both directions</b>: <code>graph[u].append(v)</code> AND <code>graph[v].append(u)</code>.</details>

---

## Related Modules
- [[01-trees|Trees]] — Cycle-free connected graphs
- [[02-dfs|Depth-First Search (DFS)]] — Graph traversal using stack/recursion
- [[03-bfs|Breadth-First Search (BFS)]] — Shortest path in unweighted graphs
- [[06-dijkstra|Dijkstra's Algorithm]] — Shortest path in weighted graphs
- [[10-union-find|Union-Find]] — Disjoint sets and cycle detection
