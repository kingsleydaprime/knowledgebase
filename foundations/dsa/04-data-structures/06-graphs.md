# Graphs

A graph is a set of **vertices** (nodes) connected by **edges**. It's the most general structure in this folder, and the others are special cases of it: a [[01-trees|tree]] is a graph with no cycles and exactly one path between any two nodes; a [[04-linked-lists|linked list]] is a tree where every node has exactly one child. Graphs drop those restrictions — any node can connect to any other, cycles are allowed, and there needn't be a single root.

The reason graphs matter more than that framing suggests: **an enormous number of problems are graph problems wearing a disguise.** Road networks, social follows, package dependencies, build targets, web links, state machines, course prerequisites, currency exchange rates, and 2-D grids are all graphs. Learning to *notice* that is worth more than any individual graph algorithm.

## Vocabulary

- **Vertex / node** — a thing. **Edge** — a relationship between two things.
- **Adjacent** — two vertices with an edge between them. The **neighbours** of `v` are all vertices adjacent to it.
- **Degree** of a vertex — how many edges touch it. Directed graphs split this into **in-degree** (edges arriving) and **out-degree** (edges leaving); in-degree is what [[11-topological-sort|topological sort]] counts.
- **Path** — a sequence of vertices each connected to the next. **Cycle** — a path that returns to its start.
- **Connected** — there's a path between every pair of vertices. A **component** is a maximal connected chunk; a graph can be several disconnected components.

## The kinds of graph

Four independent properties. Any combination is possible, and each one changes which algorithms apply — which is why the first thing to establish about a graph problem is which boxes it ticks.

### Directed vs undirected

Does an edge `A → B` imply `B → A`? A one-way street versus a two-way street.

```
undirected:  A —— B        directed:  A ——> B
             friendship               "follows on Twitter"
```

The practical consequence is in how you build the adjacency list: undirected means **every edge gets added twice**, once in each direction. Forgetting that second `append` is the most common graph-construction bug there is.

### Weighted vs unweighted

Do edges carry a cost — distance, time, price, capacity — or are they all equivalent?

This is the single most important distinction for **shortest path**, because it decides your algorithm outright. Unweighted: [[03-bfs|BFS]] finds the shortest path, because "fewest edges" and "lowest cost" are the same thing. Weighted: BFS is simply *wrong* — a two-edge route can be cheaper than a one-edge route — and you need [[06-dijkstra|Dijkstra]] (or Bellman-Ford if any weight is negative, since Dijkstra assumes adding an edge never makes a path cheaper).

### Cyclic vs acyclic

Can you follow edges and end up back where you started?

A **DAG** (directed acyclic graph) is the directed, cycle-free case, and it's worth naming because so much real infrastructure is one: build dependencies, task schedules, course prerequisites, spreadsheet formula references, git commit history. **A DAG is exactly the class of graph you can [[11-topological-sort|topologically sort]]** — and the "is there a cycle?" check and the sort are the same algorithm, since a topological sort is possible if and only if no cycle exists.

Note the trap: **acyclic is not the same as tree.** A DAG can have multiple paths between two nodes — the diamond A→B, A→C, B→D, C→D has no cycle but isn't a tree.

### Simple vs multigraph

A **simple graph** has at most one edge between any pair of vertices and no **self-loops** (an edge from a vertex to itself). Most problems assume this without saying so.

A **multigraph** allows **parallel edges** — two cities with both a cheap slow train and an expensive fast one between them. This matters more than it sounds: an adjacency *matrix* fundamentally can't represent parallel edges (one cell, one value), so a multigraph forces an adjacency list or edge list.

### Named shapes worth recognising

- **Complete graph** — every vertex connected to every other. `V(V-1)/2` edges undirected; the densest a simple graph gets.
- **Bipartite graph** — vertices split into two groups with edges only *between* groups, never within. Students↔courses, jobs↔machines, users↔products. Checking bipartiteness is a two-colouring BFS, and it's the setup for matching problems.
- **Tree** — connected, acyclic, undirected, exactly `V-1` edges. **Forest** — a collection of trees, i.e. acyclic but not necessarily connected.
- **Strongly connected** (directed only) — every vertex can reach every other *following edge directions*. Distinct from **weakly connected**, which only requires connectivity if you ignore direction.

### Dense vs sparse

Not a formal category but the one that drives your representation choice. With `V` vertices, a simple undirected graph has at most `V(V-1)/2` edges — call it `V²`.

- **Sparse**: `E` is closer to `V` than to `V²`. A social network — you follow hundreds of people, not eight billion.
- **Dense**: `E` approaches `V²`. A currency-conversion table where every currency has a rate against every other.

**Most real and interview graphs are sparse**, which is why the adjacency list is the default.

## Representations

Three ways to store a graph, and the choice materially affects performance.

**Adjacency list** — for each vertex, its neighbours. The default.

```python
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"],
}
# weighted: store tuples -> {"A": [("B", 5), ("C", 2)]}
```

**Adjacency matrix** — a V×V grid, `matrix[i][j] = 1` when an edge exists (or the weight, when weighted).

```
    A  B  C  D
A [ 0, 1, 1, 0 ]
B [ 1, 0, 0, 1 ]
C [ 1, 0, 0, 0 ]
D [ 0, 1, 0, 0 ]
```

An undirected graph's matrix is symmetric across the diagonal; the diagonal itself is self-loops.

**Edge list** — just the edges, no per-vertex grouping.

```python
edges = [("A", "B", 5), ("A", "C", 2), ("B", "D", 7)]
```

Useless for "who are `A`'s neighbours?" — that's a full scan — but it's the right shape when an algorithm wants to consider *every edge in some order*, which is exactly what [[12-minimum-spanning-tree|Kruskal's]] does (sort all edges by weight, add the cheapest that doesn't form a cycle). Bellman-Ford also just relaxes every edge repeatedly. It's also how graphs almost always arrive in a problem statement, so `edges → adjacency list` is a conversion worth being able to write without thinking.

| | Adjacency list | Adjacency matrix | Edge list |
|---|---|---|---|
| Space | O(V + E) | O(V²) | O(E) |
| Edge `(u,v)` exists? | O(degree of u) | **O(1)** | O(E) |
| Iterate neighbours of `u` | **O(degree of u)** | O(V) — scan the row | O(E) |
| Iterate all edges | O(V + E) | O(V²) | **O(E)** |
| Add an edge | O(1) | O(1) | O(1) |
| Parallel edges | ✓ | ✗ | ✓ |
| Best for | sparse graphs — **the default** | dense graphs, O(1) edge lookup | edge-centric algorithms (Kruskal, Bellman-Ford) |

## Implicit graphs — the ones with no graph object

Not every graph is built. Often the graph is **implied by the rules of the problem**, and constructing it explicitly would be wasted work. Recognising this is worth more in practice than any representation detail.

**A 2-D grid is a graph.** Each cell is a vertex; each cell is adjacent to its four (or eight) neighbours. There's no adjacency list anywhere — the neighbours are computed arithmetically:

```python
for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != WALL:
        ...   # this is "for neighbour in graph[node]"
```

That loop *is* the adjacency lookup. Every grid problem — islands, flood fill, shortest path through a maze, rotting oranges — is a standard [[02-dfs|DFS]]/[[03-bfs|BFS]] over an implicit graph, which is why [[13-matrix-traversal|matrix traversal]] is a graph pattern rather than an array one.

The same idea generalises: in **Word Ladder** the vertices are words and the edges are "differs by one letter" — computed, never stored. In a **state-space search** the vertices are configurations (a puzzle position, a game state) and the edges are legal moves. **If you can enumerate a node's neighbours on demand, you have a graph, and every graph algorithm applies** — no data structure required.

## How you actually do things with a graph

A graph on its own is just a shape; the useful work is in the algorithms that walk it. [[02-dfs|DFS]] and [[03-bfs|BFS]] are the foundation, and nearly everything else is one of them with something added:

| Question | Tool |
|---|---|
| Is there a path from A to B? | DFS or BFS |
| Shortest path, **unweighted** | BFS |
| Shortest path, **weighted, non-negative** | [[06-dijkstra|Dijkstra]] — BFS + a min-heap |
| Shortest path, **negative weights** | Bellman-Ford |
| How many connected components? | DFS/BFS from every unvisited vertex, or [[10-union-find|union-find]] |
| Is there a cycle? | DFS tracking the recursion stack (directed), or union-find (undirected) |
| Valid ordering of dependencies? | [[11-topological-sort|Topological sort]] — DAG only |
| Cheapest way to connect everything? | [[12-minimum-spanning-tree|MST]] — Prim's or Kruskal's |
| Can it be two-coloured? | BFS assigning alternating colours (bipartite check) |

## Gotchas

- **Cycles break naive traversal.** Unlike a tree, a graph can loop back on itself, so every traversal needs a `visited` set. Without one, DFS/BFS runs forever. This is the number-one graph bug, and the reason tree code doesn't port to graphs unchanged.
- **Mark visited when you *enqueue*, not when you dequeue.** In BFS, marking on dequeue lets a vertex be added to the queue several times before it's first processed — still correct, but it can blow up the queue and the runtime.
- **Disconnected graphs.** One DFS/BFS call only reaches the start vertex's component. To cover the whole graph you must loop over all vertices and start fresh from each unvisited one — forgetting this quietly gives an answer for one component instead of the graph.
- **Undirected edges must be added twice.** `graph[u].append(v)` *and* `graph[v].append(u)`. Half a graph produces plausible-looking wrong answers rather than a crash.
- **BFS on a weighted graph is wrong**, even though it runs and returns something. Fewest edges ≠ lowest cost.
- **Acyclic ≠ tree** — see the diamond above.
- **A dense graph in an adjacency list still costs O(V²) to traverse**, and a sparse graph in a matrix wastes O(V²) space to hold almost entirely zeros. The representation has to match the density.

## Related
- [[01-trees|trees]] — the constrained case: connected, acyclic, `V-1` edges
- [[04-linked-lists|linked lists]] — the maximally constrained case: one child each
- [[02-dfs|dfs]] and [[03-bfs|bfs]] — the two traversals everything else is built from
- [[06-dijkstra|dijkstra]] — weighted shortest path
- [[11-topological-sort|topological-sort]] — ordering a DAG
- [[12-minimum-spanning-tree|minimum-spanning-tree]] — Prim's and Kruskal's
- [[10-union-find|union-find]] — components and cycle detection without traversal
- [[13-matrix-traversal|matrix-traversal]] — grids as implicit graphs
