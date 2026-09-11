# Graphs

**The structure for when the relationships matter as much as the things.** Four lessons, written to [[COURSE-STANDARD|the course standard]] — prerequisites, observable outcomes, worked derivations, a runnable lab whose output was generated from an actual run, practice with hidden answers, and a demonstrable finish line.

> **Why this is a folder and not one note.** Graphs carry more vocabulary than any other structure here, and nearly every later confusion traces back to a term used loosely: *path* meaning two different things in two textbooks, *connected* meaning four different things in a directed graph, *spanning* and *induced* being opposite kinds of subgraph. The terms come first, precisely, and the algorithms are stated in them.

## Reading order

1. [[01-what-a-graph-is|What a Graph Is]] — **[Beginner]** — vertex, edge, incident, adjacent, degree, self-loop, parallel edges, simple graph vs multigraph, the four dimensions, and the handshake lemma
2. [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — **[Intermediate]** — walk / trail / path / simple path and their closed counterparts; connected components; **strongly vs weakly connected**; SCCs (strongly connected components); DAGs
3. [[03-subgraphs-trees-and-forests|Subgraphs, Trees and Forests]] — **[Intermediate]** — subgraph, induced, spanning; forest and tree; **six equivalent definitions of a tree**; spanning trees; how this relates to the rooted trees of [[05-trees/01-trees|05-trees]]
4. [[04-representations|Representations]] — **[Intermediate]** — edge list, adjacency list, adjacency map, adjacency matrix, incidence matrix; costs and how to choose; implicit graphs

## The vocabulary, in one place

Use this to find which lesson defines a term.

| Term | Lesson |
| :--- | :--- |
| vertex, edge, incident, adjacent, degree, in/out-degree | 01 |
| self-loop, parallel edges, simple graph, multigraph, weighted | 01 |
| complete graph, dense, sparse, handshake lemma | 01 |
| walk, trail, path, simple path | 02 |
| closed walk, circuit, cycle, simple cycle | 02 |
| directed path, directed cycle, DAG (directed acyclic graph) | 02 |
| connected, connected component | 02 |
| strongly connected, weakly connected, SCC (strongly connected component), condensation | 02 |
| subgraph, induced subgraph, spanning subgraph, clique | 03 |
| forest, tree, spanning tree | 03 |
| edge list, adjacency list, adjacency map | 04 |
| adjacency matrix, incidence matrix, implicit graph | 04 |

## Which algorithm for which question

| Question / goal | Reach for |
| :--- | :--- |
| **Is there any path between A and B?** | [[02-dfs|DFS (depth-first search)]] or [[03-bfs|BFS (breadth-first search)]] |
| **Shortest path, unweighted graph or grid** | [[03-bfs|BFS (breadth-first search)]] |
| **Shortest path, weighted with non-negative weights** | [[06-dijkstra|Dijkstra]] — BFS (breadth-first search) plus a [[08-heaps|min-heap]] |
| **A valid order of dependencies** | [[11-topological-sort|Topological sort]] — needs a DAG (directed acyclic graph) |
| **Detect a cycle, undirected** | [[10-union-find|Union-find]], or DFS (depth-first search) |
| **Detect a cycle, directed** | DFS (depth-first search) with three colours — lesson 02 |
| **Connect everything at minimum total cost** | [[12-minimum-spanning-tree|Minimum spanning tree]] |
| **Which groups are mutually reachable?** | SCCs (strongly connected components) — lesson 02 |

## What is verified

Every lab was executed and its expected output generated from that run:

- **The handshake lemma**, including that a self-loop adds two to a degree.
- **Six route types distinguished** on one bowtie graph — walk, trail, path, cycle, circuit, and a sequence that is not even a walk.
- **Condensing SCCs (strongly connected components) always yields a DAG (directed acyclic graph)**, checked on a graph with two separate cycles.
- **Four definitions of a tree computed independently** on six graphs, agreeing every time.
- **Cayley's formula** $n^{n-2}$, confirmed by exhaustive search up to $K_5$.
- **$M^k$ counts walks of length $k$**, and the measured cost gap between edge list, adjacency list and adjacency map on a 2,000-vertex graph.

## Related

- [[index|02-data-structures]] — the parent folder
- [[05-trees/01-trees|Trees]] — the special case: connected and acyclic, plus a root
- [[10-union-find|Union-Find]] — connected components, maintained incrementally
- [[02-discrete-math/07-graph-theory|Discrete maths: graph theory]] — the proofs behind these facts
- [[04-patterns/11-dfs-pattern|DFS (depth-first search) pattern]] · [[04-patterns/12-bfs-pattern|BFS (breadth-first search) pattern]] — the problem-solving layer above
