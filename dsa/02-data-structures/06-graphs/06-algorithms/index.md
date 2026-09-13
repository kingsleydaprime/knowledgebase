# Graph Algorithms

**The procedures that answer questions about a graph**, as opposed to the vocabulary that lets you state the question ([[01-what-a-graph-is|lessons 01–04]]) or the two searches everything is built from ([[05-traversal/index|05-traversal]]).

> **These live here rather than in `03-algorithms/` on purpose.** The general rule in this course is that a *procedure* is filed under [[03-algorithms/index|03-algorithms]]. Graphs are the exception, because there are enough of these that they form their own body of knowledge, they all assume the same vocabulary, and every one of them is a modification of DFS or BFS rather than a fresh idea. Keeping them next to the structure they operate on is what makes that visible.
>
> **For the general theory — what an algorithm is, how to count its cost, $O$ / $\Omega$ / $\Theta$, recurrences and amortised analysis — go to [[01-complexity-analysis/index|03-algorithms/01-complexity-analysis]] first.** Everything below is quoted in that vocabulary and none of it is re-explained here.

## Reading order

> **Start with lesson 00.** It is numbered `00` because it is the simplest algorithm here and the right first one to read — counting clusters is the first thing anyone does with a traversal.

### Grouping

0. [[00-connected-components|Connected Components]] — **[Intermediate]** — how many separate clusters, and who is in each. Flood fill with DFS or BFS, union-find and the identity **components = V − merges**, why an isolated vertex counts, and the measured ~500× gap when edges arrive over time. Plus weak versus strong connectivity for directed graphs.

### Ordering

1. [[01-topological-sort|Topological Sort]] — **[Intermediate]** — a valid order for a set of dependencies. Kahn's algorithm with in-degree counts, and the DFS variant that is just "decreasing finish time". Both detect a cycle for free, and a cycle is exactly when no order exists.

### Shortest paths

2. [[02-dijkstra|Dijkstra's Algorithm]] — **[Advanced]** — the shortest path when edges have non-negative weights. BFS with the queue replaced by a [[08-heaps|min-heap]], plus a lab showing it return $0$ where the true distance is $-9$ on a graph with one negative edge.

3. [[03-bellman-ford|Bellman–Ford]] — **[Advanced]** — shortest paths that survive **negative weights**, in $O(VE)$, with no priority queue and no finalisation. Why $V-1$ rounds, and the extra pass that detects a negative cycle — including a lab where Dijkstra silently returns 3 for a distance that is really 1.
4. [[04-floyd-warshall|Floyd–Warshall]] — **[Advanced]** — **every** pair at once in $\Theta(V^3)$, by permitting one more intermediate vertex per round. Negative cycles on the diagonal, path recovery via a `next` matrix, and a lab showing the wrong loop order failing on **105 of 200** random graphs.
5. [[05-a-star|A\*]] — **[Advanced]** — Dijkstra with the queue keyed on $f = g + h$. Admissible versus consistent, building a heuristic by relaxing the problem, weighted A\*, and **tie-breaking** — which takes the lab from 233 expanded cells to 38 for the identical path.

### Structure

6. [[06-minimum-spanning-tree|Minimum Spanning Tree]] — **[Advanced]** — connecting everything at minimum total cost. Prim's and Kruskal's, the cut property that makes both correct, and why one wants a heap and the other a [[10-union-find|union-find]].

## Which algorithm answers which question

| Question | Reach for | Cost |
| :--- | :--- | :--- |
| Is there **any** path from A to B? | [[01-depth-first-search\|DFS]] or [[02-breadth-first-search\|BFS]] | $O(V+E)$ |
| Shortest path, **unweighted** graph or grid | [[02-breadth-first-search\|BFS]] | $O(V+E)$ |
| Shortest path, **non-negative** weights | [[02-dijkstra\|Dijkstra]] | $O(E \log V)$ |
| Shortest path, weights may be **negative** | [[03-bellman-ford\|Bellman–Ford]] | $O(VE)$ |
| Shortest path between **every** pair | [[04-floyd-warshall\|Floyd–Warshall]] | $\Theta(V^3)$ |
| Shortest path with a **known goal and a distance estimate** | [[05-a-star\|A\*]] | depends on the heuristic |
| **All pairs**, sparse graph, negative weights | Johnson's — [[04-floyd-warshall\|see lesson 04]] | $O(VE\log V)$ |
| A valid **dependency order** | [[01-topological-sort\|Topological sort]] | $O(V+E)$ |
| Does a **directed cycle** exist? | DFS back edges, or Kahn's leftover count | $O(V+E)$ |
| Does an **undirected cycle** exist? | [[10-union-find\|Union-find]], or DFS ignoring the parent edge | $O(E\,\alpha(V))$ |
| Connect everything at **minimum total cost** | [[06-minimum-spanning-tree\|MST]] | $O(E \log V)$ |
| **How many separate clusters?** | [[00-connected-components\|Connected components]] | $O(V+E)$ |
| Which vertices are **mutually reachable**? | SCCs — [[00-connected-components\|lesson 00]] | $O(V+E)$ |

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

**Bellman–Ford and Floyd–Warshall are the two that break the pattern**: they are dynamic programs over the graph rather than traversals — no frontier, no finalisation, just repeated relaxation — and that is exactly why they tolerate negative weights. A\* is the opposite extreme: a traversal so aggressively steered that it may touch only a tenth of the graph.

## What is verified

| Lesson | What the lab demonstrates |
| :--- | :--- |
| [[00-connected-components\|connected components]] | DFS, BFS and union-find agreeing on **400/400** random graphs; union-find beating a re-run traversal by ~**500x** when edges arrive incrementally |
| [[03-bellman-ford\|Bellman–Ford]] | Dijkstra returning **3** where the true distance is **1**, silently; the $V-1$ bound being tight under a worst-case edge order and finishing in one round under a good one |
| [[04-floyd-warshall\|Floyd–Warshall]] | the wrong loop order disagreeing with Bellman–Ford ground truth on **105 of 200** random graphs; negative cycles appearing on the diagonal |
| [[05-a-star\|A\*]] | tie-breaking alone cutting expansions from **233 to 38**; weighted A\* trading a cost-18 path for a cost-20 one while halving the work; and admissibility violations at $w{=}1.2$ that do **not** yet cost optimality |

## Related

- [[06-graphs/index|the graphs folder]] — the vocabulary and representations these assume
- [[05-traversal/index|traversal]] — DFS and BFS, which all of these modify
- [[01-complexity-analysis/index|complexity analysis]] — what $O(E \log V)$ means and how it was derived
- [[08-heaps|Heaps]] · [[10-union-find|Union-Find]] — the two structures these lean on
- [[03-algorithms/index|03-algorithms]] — the non-graph algorithms
