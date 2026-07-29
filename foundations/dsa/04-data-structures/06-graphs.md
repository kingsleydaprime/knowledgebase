# Graphs

A graph is a set of **vertices** (nodes) connected by **edges**. It's the most general structure in this folder — a [[01-trees|tree]] is just a graph with no cycles and exactly one path between any two nodes; a [[04-linked-lists|linked list]] is a tree where every node has one child. Graphs drop those restrictions: any node can connect to any other node, cycles are allowed, and there doesn't have to be a single root.

## Vocabulary

- **Directed vs undirected** — does an edge `A -> B` imply `B -> A`? A one-way street vs a two-way street.
- **Weighted vs unweighted** — do edges have a cost/distance attached, or are they all equal?
- **Cyclic vs acyclic** — can you follow edges and end up back where you started? A DAG (directed acyclic graph) is the directed, cycle-free case — this is what task scheduling / build dependency graphs are.
- **Degree** of a vertex — number of edges touching it (in-degree/out-degree separately, if directed).
- **Connected** — a graph (or component of one) is connected if there's a path between every pair of vertices.

## Representations

Two standard ways to store a graph, and the choice materially affects performance:

**Adjacency list** — for each vertex, keep a list of its neighbors.

```python
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"],
}
```

**Adjacency matrix** — a V×V grid, `matrix[i][j] = 1` if an edge exists between `i` and `j`.

```
    A  B  C  D
A [ 0, 1, 1, 0 ]
B [ 1, 0, 0, 1 ]
C [ 1, 0, 0, 0 ]
D [ 0, 1, 0, 0 ]
```

| | Adjacency list | Adjacency matrix |
|---|---|---|
| Space | O(V + E) | O(V²) |
| Check if edge (u, v) exists | O(degree of u) | O(1) |
| Iterate all neighbors of u | O(degree of u) | O(V) — scan the whole row |
| Best for | sparse graphs (E << V²) | dense graphs, or when O(1) edge lookup matters |

Most real-world and interview graphs are sparse (a social network doesn't have every user connected to every other user) — adjacency list is the default choice unless you have a specific reason to want O(1) edge lookups.

## How you actually do things with a graph

A graph on its own is just a shape — the useful work is in the algorithms that walk it: [[02-dfs|dfs]] and [[03-bfs|bfs]] for traversal, which underpin cycle detection, shortest paths (BFS, unweighted), topological sort, and connected components. Weighted shortest-path (Dijkstra, Bellman-Ford) and minimum spanning tree algorithms build directly on top of that same traversal foundation, layering in a priority queue — worth its own note later rather than folding in here.

## Gotchas

- **Cycles break naive recursive traversal.** Unlike a tree, a graph can loop back on itself, so every traversal needs a `visited` set — without one, DFS/BFS can recurse or loop forever.
- **Disconnected graphs**: a single DFS/BFS call from one starting vertex only reaches that vertex's connected component. If you need to process the whole graph, you have to loop over all vertices and start a fresh traversal from any unvisited one.
- Confusing "acyclic" with "tree" — a DAG can still have multiple paths between two nodes (a diamond shape: A→B, A→C, B→D, C→D), which a tree can never have.
- Directed edges are easy to get backwards when hand-building an adjacency list — double-check whether `graph[u].append(v)` should also add `graph[v].append(u)` (undirected) or not (directed).

## Related
- [[01-trees|trees]] — a tree is a constrained graph
- [[02-dfs|dfs]]
- [[03-bfs|bfs]]
- [[02-traversal|traversal]]
