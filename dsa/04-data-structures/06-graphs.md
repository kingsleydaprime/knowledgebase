# Module: Graphs (Networks, Connections & Dependencies)

Welcome to the **Graphs** module. A **Graph** is a set of **Vertices** (nodes) connected by **Edges** (relationships).

Graphs are the ultimate generalized data structure. In fact, earlier structures you studied are simply restricted graphs:
- A [[01-trees|Tree]] is a graph with no cycles and exactly one path between any two nodes.
- A [[04-linked-lists|Linked List]] is a tree where every node has at most one child.

By removing all restrictions, graphs allow any node to connect to any other node, allow loops (cycles), and allow disconnected components.

---

## Before you start

- You can traverse a tree with both a stack and a queue. See [[02-traversal|traversal]].
- You understand hash maps, used here for adjacency and visited sets. See [[03-hash-maps|hash maps]].

**What you will be able to do after this lesson:**

1. Explain why graph traversal needs a visited set and tree traversal does not.
2. Explain why BFS finds shortest paths in unweighted graphs and DFS does not.
3. Choose between an adjacency list and a matrix from the graph's density.
4. Detect a cycle in a directed graph and say where that is used in practice.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

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

## Implementation - complete runnable example

**Runnable example:** save as `graphs_lab.py` and run `python3 graphs_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Graphs: representation, traversal, and why the choice of storage matters."""
from collections import deque

class Graph:
    """Adjacency list. The other option -- a matrix -- is compared below."""
    def __init__(self, directed=False):
        self.adj, self.directed = {}, directed

    def add_edge(self, u, v):
        self.adj.setdefault(u, []).append(v)
        self.adj.setdefault(v, [])
        if not self.directed:
            self.adj[v].append(u)

    def nodes(self):
        return sorted(self.adj)

    def bfs(self, start):
        """Queue -> explores by distance. First arrival is the shortest path."""
        seen, order, q = {start}, [], deque([start])
        while q:
            n = q.popleft(); order.append(n)
            for m in self.adj[n]:
                if m not in seen:
                    seen.add(m); q.append(m)
        return order

    def dfs(self, start):
        """Stack -> explores one branch to its end before backtracking."""
        seen, order, stack = set(), [], [start]
        while stack:
            n = stack.pop()
            if n in seen: continue
            seen.add(n); order.append(n)
            for m in reversed(self.adj[n]):
                if m not in seen: stack.append(m)
        return order

    def shortest_path(self, start, goal):
        """BFS, remembering how each node was reached."""
        if start == goal: return [start]
        came_from, q = {start: None}, deque([start])
        while q:
            n = q.popleft()
            for m in self.adj[n]:
                if m not in came_from:
                    came_from[m] = n
                    if m == goal:
                        path = [goal]
                        while came_from[path[-1]] is not None:
                            path.append(came_from[path[-1]])
                        return path[::-1]
                    q.append(m)
        return None

    def has_cycle_directed(self):
        """A back-edge to a node still on the current path means a cycle."""
        WHITE, GREY, BLACK = 0, 1, 2
        colour = {n: WHITE for n in self.adj}
        def visit(n):
            colour[n] = GREY
            for m in self.adj[n]:
                if colour[m] == GREY: return True
                if colour[m] == WHITE and visit(m): return True
            colour[n] = BLACK
            return False
        return any(colour[n] == WHITE and visit(n) for n in self.adj)

def storage_cost(n_nodes, n_edges):
    """Adjacency list vs matrix, in 'slots' of storage."""
    return {"list": n_nodes + 2 * n_edges, "matrix": n_nodes * n_nodes}

if __name__ == "__main__":
    g = Graph()
    for u, v in [("A","B"), ("A","C"), ("B","D"), ("C","D"), ("D","E"), ("E","F")]:
        g.add_edge(u, v)
    print("GRAPH:  A-B, A-C, B-D, C-D, D-E, E-F")
    print(f"  adjacency list: { {k: v for k, v in sorted(g.adj.items())} }")
    print()

    print("BFS vs DFS -- same graph, same start, different order")
    print(f"  BFS from A: {g.bfs('A')}   (by distance: A, then neighbours, ...)")
    print(f"  DFS from A: {g.dfs('A')}   (down one branch, then back up)")
    print()

    print("SHORTEST PATH -- why BFS and not DFS")
    print(f"  A to F via BFS: {g.shortest_path('A','F')}  ({len(g.shortest_path('A','F'))-1} edges)")
    print("  BFS reaches every node by the FEWEST edges, because it finishes")
    print("  distance k entirely before starting distance k+1. DFS offers no")
    print("  such guarantee -- it returns whatever path it wandered down.")
    print()

    print("CYCLE DETECTION (directed)")
    dag = Graph(directed=True)
    for u, v in [("a","b"), ("b","c"), ("a","c")]:
        dag.add_edge(u, v)
    cyc = Graph(directed=True)
    for u, v in [("a","b"), ("b","c"), ("c","a")]:
        cyc.add_edge(u, v)
    print(f"  a->b, b->c, a->c   has cycle: {dag.has_cycle_directed()}")
    print(f"  a->b, b->c, c->a   has cycle: {cyc.has_cycle_directed()}")
    print("  -> this is how build systems and package managers detect")
    print("     circular dependencies.")
    print()

    print("STORAGE -- list vs matrix, and when each wins")
    print(f"  {'nodes':>7s} {'edges':>9s} {'list':>10s} {'matrix':>10s} {'winner':>9s}")
    for n, e in [(1000, 2000), (1000, 100000), (1000, 499500)]:
        c = storage_cost(n, e)
        w = "list" if c["list"] < c["matrix"] else "matrix"
        density = "sparse" if e < n*n/10 else "dense"
        print(f"  {n:7d} {e:9,d} {c['list']:10,d} {c['matrix']:10,d} {w:>9s}  ({density})")
    print("  -> real graphs (roads, social, web) are SPARSE, which is why")
    print("     adjacency lists are the default.")

    assert g.bfs("A")[0] == "A" and set(g.bfs("A")) == set(g.nodes())
    assert g.shortest_path("A", "F") == ["A", "B", "D", "E", "F"]
    assert len(g.shortest_path("A", "F")) - 1 == 4
    assert g.shortest_path("A", "A") == ["A"]
    assert not dag.has_cycle_directed() and cyc.has_cycle_directed()
    assert storage_cost(1000, 2000)["list"] < storage_cost(1000, 2000)["matrix"]
    print()
    print("graphs_lab: passed")
```

Expected output:

```
GRAPH:  A-B, A-C, B-D, C-D, D-E, E-F
  adjacency list: {'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['A', 'D'], 'D': ['B', 'C', 'E'], 'E': ['D', 'F'], 'F': ['E']}

BFS vs DFS -- same graph, same start, different order
  BFS from A: ['A', 'B', 'C', 'D', 'E', 'F']   (by distance: A, then neighbours, ...)
  DFS from A: ['A', 'B', 'D', 'C', 'E', 'F']   (down one branch, then back up)

SHORTEST PATH -- why BFS and not DFS
  A to F via BFS: ['A', 'B', 'D', 'E', 'F']  (4 edges)
  BFS reaches every node by the FEWEST edges, because it finishes
  distance k entirely before starting distance k+1. DFS offers no
  such guarantee -- it returns whatever path it wandered down.

CYCLE DETECTION (directed)
  a->b, b->c, a->c   has cycle: False
  a->b, b->c, c->a   has cycle: True
  -> this is how build systems and package managers detect
     circular dependencies.

STORAGE -- list vs matrix, and when each wins
    nodes     edges       list     matrix    winner
     1000     2,000      5,000  1,000,000      list  (sparse)
     1000   100,000    201,000  1,000,000      list  (dense)
     1000   499,500  1,000,000  1,000,000    matrix  (dense)
  -> real graphs (roads, social, web) are SPARSE, which is why
     adjacency lists are the default.

graphs_lab: passed
```

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: Why is an Adjacency List preferred over an Adjacency Matrix for storing a social network like Twitter (800 million users, average 500 follows per user)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Twitter's graph is extremely <b>sparse</b>. An Adjacency Matrix requires an 800M x 800M grid (640,000 trillion cells, mostly zeros!). An Adjacency List consumes space proportional to actual edges <b>O(V + E)</b>, taking only a few gigabytes.</details>

2. **Question**: What is a DAG (Directed Acyclic Graph), and why is it required for Topological Sorting?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A DAG is a directed graph with <b>zero cycles</b>. Topological sorting orders tasks by dependencies. If a cycle exists (A depends on B, B depends on C, C depends on A), a valid topological order is logically impossible (circular dependency deadlock).</details>

3. **Question**: In an undirected graph, what critical step must be taken when populating an Adjacency List from an edge `(u, v)`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> You must append the edge in <b>both directions</b>: <code>graph[u].append(v)</code> AND <code>graph[v].append(u)</code>.</details>

---

## Practice - independent task

Implement **topological sort** - ordering tasks so every dependency comes first.

- Use either Kahn's algorithm (repeatedly take a node with no remaining incoming edges) or a post-order DFS with the result reversed.
- Your function must **detect a cycle** and report that no ordering exists, rather than returning a wrong answer.
- Test on a realistic dependency graph of at least eight nodes, and on a graph containing a cycle.
- **Then verify properly:** for every edge u to v in your output ordering, check that u appears before v. That check is the definition, and it is stronger than eyeballing the result.

**Done when:** your sort produces a valid ordering verified edge by edge, and correctly refuses a cyclic graph.

<details><summary>Hint - open only after an attempt</summary>
With Kahn's algorithm, count incoming edges for every node, start with those at zero, and each time you output a node decrement its neighbours' counts - adding any that reach zero.<br>
<strong>The cycle detection falls out for free:</strong> if you finish and have output fewer nodes than the graph contains, the remainder are all stuck waiting on each other, which is exactly a cycle. This is how build systems, package managers and spreadsheet recalculation all detect circular dependencies.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] Explain why a visited set is mandatory on a graph and unnecessary on a tree.
- [ ] Explain why BFS gives shortest paths in unweighted graphs.
- [ ] Compare adjacency list and matrix storage and say which suits sparse graphs.
- [ ] Describe how a directed cycle is detected and name a real use.

**Recap:** A graph is nodes plus edges, with no restriction on cycles - which is why traversal must track visited nodes or loop forever. BFS explores by distance using a queue, so the first time it reaches a node it has used the fewest edges, giving shortest paths in unweighted graphs; DFS follows one branch to its end using a stack and offers no such guarantee. Adjacency lists cost O(V + E) and suit the sparse graphs that occur in practice; matrices cost O(V^2) but give O(1) edge lookup.

**Next:** [[07-stacks-and-queues|Stacks and Queues]] - the two containers that made DFS and BFS differ, examined on their own terms.

## Related Modules
- [[01-trees|Trees]] — Cycle-free connected graphs
- [[02-dfs|Depth-First Search (DFS)]] — Graph traversal using stack/recursion
- [[03-bfs|Breadth-First Search (BFS)]] — Shortest path in unweighted graphs
- [[06-dijkstra|Dijkstra's Algorithm]] — Shortest path in weighted graphs
- [[10-union-find|Union-Find]] — Disjoint sets and cycle detection
