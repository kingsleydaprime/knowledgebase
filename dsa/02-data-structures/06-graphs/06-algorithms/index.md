# Graph Algorithms

**The procedures that answer questions about a graph**, as opposed to the vocabulary that lets you state the question ([[01-what-a-graph-is|lessons 01–04]]) or the two searches everything is built from ([[05-traversal/index|05-traversal]]).

> **These live here rather than in `03-algorithms/` on purpose.** The general rule in this course is that a *procedure* is filed under [[03-algorithms/index|03-algorithms]]. Graphs are the exception, because there are enough of these that they form their own body of knowledge, they all assume the same vocabulary, and every one of them is a modification of DFS or BFS rather than a fresh idea. Keeping them next to the structure they operate on is what makes that visible.
>
> **For the general theory — what an algorithm is, how to count its cost, $O$ / $\Omega$ / $\Theta$, recurrences and amortised analysis — go to [[01-complexity-analysis/index|03-algorithms/01-complexity-analysis]] first.** Everything below is quoted in that vocabulary and none of it is re-explained here.

## Reading order

### Ordering

1. [[01-topological-sort|Topological Sort]] — **[Intermediate]** — a valid order for a set of dependencies. Kahn's algorithm with in-degree counts, and the DFS variant that is just "decreasing finish time". Both detect a cycle for free, and a cycle is exactly when no order exists.

### Shortest paths

2. [[02-dijkstra|Dijkstra's Algorithm]] — **[Advanced]** — the shortest path when edges have non-negative weights. BFS with the queue replaced by a [[08-heaps|min-heap]], plus a lab showing it return $0$ where the true distance is $-9$ on a graph with one negative edge.

Three more belong in this section and are **not yet written**: **Bellman–Ford** (slower, but survives negative weights and detects negative cycles), **Floyd–Warshall** (all pairs at once, in $O(V^3)$, and the cleanest three-line dynamic program in the subject), and **A\*** (Dijkstra plus a heuristic that aims the search at the goal, with admissibility and consistency as the conditions for it staying correct).

### Structure

3. [[06-minimum-spanning-tree|Minimum Spanning Tree]] — **[Advanced]** — connecting everything at minimum total cost. Prim's and Kruskal's, the cut property that makes both correct, and why one wants a heap and the other a [[10-union-find|union-find]].

## Which algorithm answers which question

| Question | Reach for | Cost |
| :--- | :--- | :--- |
| Is there **any** path from A to B? | [[01-depth-first-search\|DFS]] or [[02-breadth-first-search\|BFS]] | $O(V+E)$ |
| Shortest path, **unweighted** graph or grid | [[02-breadth-first-search\|BFS]] | $O(V+E)$ |
| Shortest path, **non-negative** weights | [[02-dijkstra\|Dijkstra]] | $O(E \log V)$ |
| Shortest path, weights may be **negative** | Bellman–Ford *(not yet written)* | $O(VE)$ |
| Shortest path between **every** pair | Floyd–Warshall *(not yet written)* | $O(V^3)$ |
| Shortest path with a **known goal and a distance estimate** | A\* *(not yet written)* | depends on the heuristic |
| A valid **dependency order** | [[01-topological-sort\|Topological sort]] | $O(V+E)$ |
| Does a **directed cycle** exist? | DFS back edges, or Kahn's leftover count | $O(V+E)$ |
| Does an **undirected cycle** exist? | [[10-union-find\|Union-find]], or DFS ignoring the parent edge | $O(E\,\alpha(V))$ |
| Connect everything at **minimum total cost** | [[06-minimum-spanning-tree\|MST]] | $O(E \log V)$ |
| Which vertices are **mutually reachable**? | SCCs — [[02-paths-cycles-and-connectivity\|lesson 02]] | $O(V+E)$ |

**The row that catches people out is the third versus the fourth.** "Dijkstra is the shortest-path algorithm" is a half-truth; it is the shortest-path algorithm *for non-negative weights*, and it fails silently — returning a wrong number rather than an error — the moment that assumption breaks.

## The pattern underneath all of them

Every algorithm in this folder is a traversal with one thing changed:

| Algorithm | Is BFS/DFS with... |
| :--- | :--- |
| BFS | a queue |
| DFS | a stack |
| Dijkstra | a min-heap keyed by distance |
| A\* | a min-heap keyed by distance **plus an estimate of what remains** |
| Prim | a min-heap keyed by edge weight, not path length |
| Kahn's topological sort | a queue, fed by vertices whose in-degree has dropped to zero |

Bellman–Ford and Floyd–Warshall are the two that break the pattern: they are dynamic programs over the graph rather than traversals, which is exactly why they tolerate negative weights.

## Related

- [[06-graphs/index|the graphs folder]] — the vocabulary and representations these assume
- [[05-traversal/index|traversal]] — DFS and BFS, which all of these modify
- [[01-complexity-analysis/index|complexity analysis]] — what $O(E \log V)$ means and how it was derived
- [[08-heaps|Heaps]] · [[10-union-find|Union-Find]] — the two structures these lean on
- [[03-algorithms/index|03-algorithms]] — the non-graph algorithms
