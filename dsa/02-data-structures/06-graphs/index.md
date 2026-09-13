# Graphs

**The structure for when the relationships matter as much as the things.** Four vocabulary lessons plus two sub-folders — [[05-traversal/index|traversal]] and [[06-algorithms/index|algorithms]] — written to [[COURSE-STANDARD|the course standard]] — prerequisites, observable outcomes, worked derivations, a runnable lab whose output was generated from an actual run, practice with hidden answers, and a demonstrable finish line.

> **Why this is a folder and not one note.** Graphs carry more vocabulary than any other structure here, and nearly every later confusion traces back to a term used loosely: *path* meaning two different things in two textbooks, *connected* meaning four different things in a directed graph, *spanning* and *induced* being opposite kinds of subgraph. The terms come first, precisely, and the algorithms are stated in them.

## Reading order

1. [[01-what-a-graph-is|What a Graph Is]] — **[Beginner]** — vertex, edge, incident, adjacent, degree, self-loop, parallel edges, simple graph vs multigraph, the four dimensions, and the handshake lemma
2. [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — **[Intermediate]** — walk / trail / path / simple path and their closed counterparts; connected components; **strongly vs weakly connected**; SCCs; DAGs
3. [[03-subgraphs-trees-and-forests|Subgraphs, Trees and Forests]] — **[Intermediate]** — subgraph, induced, spanning; forest and tree; **six equivalent definitions of a tree**; spanning trees; how this relates to the rooted trees of [[05-trees/01-trees|05-trees]]
4. [[04-representations|Representations]] — **[Intermediate]** — edge list, adjacency list, adjacency map, adjacency matrix, incidence matrix; costs and how to choose; implicit graphs
5. [[05-traversal/index|Traversal]] — **[Intermediate]** — a folder, mirroring [[04-traversal/index|the one under trees]]: depth-first search, breadth-first search, and what the search leaves behind — traversal trees, discovery/finish times, and the four edge kinds
6. [[06-algorithms/index|Graph Algorithms]] — **[Intermediate → Advanced]** — a folder: topological sort, Dijkstra, minimum spanning trees, and the rest of the shortest-path family

> **Lessons 1–4 are the vocabulary; 5 and 6 are what you do with it.** Nothing in the two folders introduces a graph term that is not defined in the first four lessons, which is the whole reason they are ordered this way.

## The vocabulary, in one place

Use this to find which lesson defines a term.

| Term | Lesson |
| :--- | :--- |
| vertex, edge, incident, adjacent, degree, in/out-degree | 01 |
| self-loop, parallel edges, simple graph, multigraph, weighted | 01 |
| complete graph, dense, sparse, handshake lemma | 01 |
| walk, trail, path, simple path | 02 |
| closed walk, circuit, cycle, simple cycle | 02 |
| directed path, directed cycle, DAG | 02 |
| connected, connected component | 02 |
| strongly connected, weakly connected, SCC, condensation | 02 |
| subgraph, induced subgraph, spanning subgraph, clique | 03 |
| forest, tree, spanning tree | 03 |
| edge list, adjacency list, adjacency map | 04 |
| adjacency matrix, incidence matrix, implicit graph | 04 |
| visited set, traversal tree, traversal forest | 05 |
| discovery time, finish time, ancestor, descendant | 05 |
| tree edge, back edge, forward edge, cross edge | 05 |
| white / grey / black colouring, parenthesis theorem | 05 |

## Which algorithm for which question

| Question / goal | Reach for |
| :--- | :--- |
| **Is there any path between A and B?** | [[01-depth-first-search|DFS]] or [[02-breadth-first-search|BFS]] — folder 05 |
| **Shortest path, unweighted graph or grid** | [[02-breadth-first-search|BFS]] — folder 05 |
| **Shortest path, weighted with non-negative weights** | [[02-dijkstra|Dijkstra]] — BFS plus a [[08-heaps|min-heap]] |
| **A valid order of dependencies** | [[01-topological-sort|Topological sort]] — needs a DAG |
| **Detect a cycle, directed** | DFS back edges — [[03-traversal-trees-and-edge-classification|folder 05, lesson 3]] |
| **Detect a cycle, undirected** | [[10-union-find|Union-find]], or DFS ignoring the parent edge |
| **Connect everything at minimum total cost** | [[06-minimum-spanning-tree|Minimum spanning tree]] |
| **Which groups are mutually reachable?** | SCCs — lesson 02, computed with finish times |
| **Is the graph bipartite?** | BFS levels — no edge may join two vertices on the same level |

## What is verified

Every lab was executed and its expected output generated from that run:

- **The handshake lemma**, including that a self-loop adds two to a degree.
- **Six route types distinguished** on one bowtie graph — walk, trail, path, cycle, circuit, and a sequence that is not even a walk.
- **Condensing SCCs always yields a DAG**, checked on a graph with two separate cycles.
- **Four definitions of a tree computed independently** on six graphs, agreeing every time.
- **Cayley's formula** $n^{n-2}$, confirmed by exhaustive search up to $K_5$.
- **$M^k$ counts walks of length $k$**, and the measured cost gap between edge list, adjacency list and adjacency map on a 2,000-vertex graph.

## Related

- [[02-data-structures/index|02-data-structures]] — the parent folder
- [[05-trees/01-trees|Trees]] — the special case: connected and acyclic, plus a root
- [[10-union-find|Union-Find]] — connected components, maintained incrementally
- [[02-discrete-math/07-graph-theory|Discrete maths: graph theory]] — the proofs behind these facts
- [[05-traversal/index|Traversal]] · [[06-algorithms/index|Graph Algorithms]] — the two sub-folders
- [[04-patterns/11-dfs-pattern|DFS pattern]] · [[04-patterns/12-bfs-pattern|BFS pattern]] — the problem-solving layer above
