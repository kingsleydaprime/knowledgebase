# Graph Theory

**[Intermediate]** — The single most reusable modelling tool in the subject, and the vocabulary behind half the algorithms you already use.

## Definitions

**A graph $G = (V, E)$ is a set of vertices and a set of edges between them.**

That's it. **Everything else is a qualifier**, and the reason graphs are everywhere is that "things and connections between them" describes an enormous amount of the world.

| Term | Meaning |
|---|---|
| **Directed / undirected** | edges have a direction, or don't |
| **Weighted** | edges carry a value (distance, cost, capacity) |
| **Degree** | edges at a vertex. Directed: **in-degree** and **out-degree** |
| **Path** | a sequence of vertices connected by edges |
| **Cycle** | a path returning to its start |
| **Connected** | a path exists between every pair |
| **Simple** | no self-loops, no multi-edges |

**The handshake lemma**, which is the first thing to prove and immediately useful:

$$\sum_{v \in V}\deg(v) = 2|E|$$

Each edge contributes 1 to each of its two endpoints. **Corollary: the number of odd-degree vertices is always even.** That fact alone settles the Königsberg bridge problem.

## The special shapes

Recognising these tells you which algorithms apply:

**Tree** — connected and acyclic. **Exactly $|V| - 1$ edges**, and a unique path between any two vertices. Adding any edge creates exactly one cycle; removing any edge disconnects it.

**DAG** — directed, acyclic. **The shape of every dependency structure**: build systems, task schedulers, git history, spreadsheet formulas, neural network computation graphs, Makefiles. **A DAG always has a topological order**, and the existence of that order is equivalent to acyclicity. → [[foundations/dsa/05-algorithms/11-topological-sort|Topological Sort]]

**Bipartite** — vertices split into two sets with edges only between them. **Equivalent to having no odd-length cycle**, and equivalent to being 2-colourable. Matching problems (job assignment, stable marriage, ad auctions) live here.

**Complete ($K_n$)** — every pair connected. $\binom{n}{2}$ edges, which is where "$O(n^2)$ messages" in a fully-connected cluster comes from.

**Planar** — drawable without crossings. **Euler's formula:** $V - E + F = 2$. Circuit board routing, and it implies $E \leq 3V - 6$, so planar graphs are sparse.

## Representation

**The choice that determines your complexity**, and it's the first decision in any graph problem:

| | Adjacency matrix | Adjacency list |
|---|---|---|
| Space | $O(V^2)$ | $O(V+E)$ |
| Edge exists? | $O(1)$ | $O(\deg v)$ |
| Iterate neighbours | $O(V)$ | $O(\deg v)$ |
| Best for | **dense**, frequent edge queries | **sparse** — almost everything real |

> **Real graphs are overwhelmingly sparse.** A social network has billions of users and hundreds of friends each, not billions. **Adjacency list is the default**; reach for a matrix only when the graph is dense or you need matrix operations (as in [[foundations/dsa/04-data-structures/06-graphs|Floyd–Warshall]] or spectral methods).

## Traversal

**BFS** — explore level by level with a queue. **Finds shortest paths in unweighted graphs**, because it reaches every vertex at its minimum edge-distance first. → [[foundations/dsa/05-algorithms/03-bfs|BFS]]

**DFS** — go deep with a stack or recursion. **Finds cycles, topological order, connected components, and bridges.** → [[foundations/dsa/05-algorithms/02-dfs|DFS]]

**Both are $O(V + E)$** — you touch each vertex and each edge a constant number of times. **That bound is worth internalising**, because it means traversal is essentially free relative to anything more complex.

**Which to use:** BFS when you want *shortest* or *nearest*. DFS when you want *structure* — cycles, ordering, components. **The only difference in the code is queue versus stack**, which is a nice illustration that the data structure is the algorithm.

## The classic problems

**Shortest path**

| Algorithm | Handles | Complexity |
|---|---|---|
| **BFS** | unweighted | $O(V+E)$ |
| **Dijkstra** | non-negative weights | $O((V+E)\log V)$ |
| **Bellman–Ford** | **negative weights**, detects negative cycles | $O(VE)$ |
| **A\*** | with a heuristic | faster in practice |
| **Floyd–Warshall** | all pairs | $O(V^3)$ |

**Dijkstra fails on negative edges** — it commits to a vertex when first finalised, and a negative edge could improve it later. **This is a real trap**, and Bellman–Ford is the fix. → [[foundations/dsa/05-algorithms/06-dijkstra|Dijkstra]]

**Minimum spanning tree** — Kruskal (sort edges, union-find) or Prim (grow from a vertex). Network design, clustering. → [[foundations/dsa/05-algorithms/12-minimum-spanning-tree|MST]]

**Max flow / min cut** — Ford–Fulkerson, Edmonds–Karp, Dinic. **The max-flow min-cut theorem** says the maximum flow equals the minimum cut capacity, which is a beautiful duality and turns "how much can I push through" into "where's the bottleneck". Bipartite matching reduces to max flow.

**Graph colouring** — assign colours so no adjacent vertices match. **Register allocation in a [[foundations/compilers/08-code-generation|compiler]] is graph colouring** on the interference graph. **NP-hard in general** for $k \geq 3$, which is why compilers use heuristics.

**Four colour theorem:** every planar graph is 4-colourable. **The first major theorem proved by computer** (1976), and it caused a genuine philosophical argument about what counts as a proof.

## The hard ones

**Where graph theory meets [[foundations/theory-of-computation/07-complexity-classes|complexity]]**, and the pairs are instructive:

| Problem | Complexity |
|---|---|
| **Eulerian path** (every *edge* once) | **$O(E)$ — easy** |
| **Hamiltonian path** (every *vertex* once) | **NP-complete** |
| Shortest path | polynomial |
| **Longest simple path** | **NP-hard** |
| 2-colouring (bipartite check) | $O(V+E)$ |
| **3-colouring** | **NP-complete** |

> **These pairs are the best illustration in the subject that tiny changes to a problem statement change everything.** Euler's condition is local and checkable (all degrees even, connected). Hamilton's has no such characterisation, and 250 years of effort haven't found one. **"Edges" vs "vertices", "shortest" vs "longest", "2" vs "3" — each flips a polynomial problem into an intractable one.**

**Travelling salesman** — shortest cycle visiting every vertex. NP-hard, and the canonical hard optimisation problem. Solved in practice by heuristics, LP relaxation, and simulated annealing, not exactly.

**Clique, vertex cover, independent set** — all NP-complete, all reducible to each other, which is exactly what "NP-complete" means. → [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]]

## Where graphs model real systems

**The list is the argument for the domain.**

- **Networks** — routers and links. **Routing protocols are literally running Dijkstra (OSPF) or Bellman–Ford (RIP, BGP's path vector)** on the internet graph → [[foundations/networking/04-routing|Routing]]
- **Dependencies** — package managers, build systems, module imports. Cycle detection is why your build tool complains
- **Version control** — [[git/01-how-git-works|git's commit DAG]]. `git log --graph` draws it, merge-base is a lowest-common-ancestor query
- **Compilers** — control flow graphs, call graphs, [[foundations/compilers/06-intermediate-representations|SSA]], interference graphs
- **Databases** — query plans are DAGs; deadlock detection is cycle detection in the wait-for graph
- **Distributed systems** — the happens-before relation is a DAG, consensus depends on the connectivity of the node graph → [[architecture/04-distributed-systems/03-time-and-ordering|Time and Ordering]]
- **Social and web graphs** — PageRank is an eigenvector computation on the link graph
- **ML** — computation graphs for autodiff, and graph neural networks operating on the structure directly
- **Robotics** — [[robotics/12-localisation-and-slam|graph-based SLAM]] is literally optimising a pose graph
- **Filesystems** — a tree, except symlinks and hard links make it a general graph, which is why `find` needs cycle protection

## Practical notes

**Model it as a graph early.** "Is this a graph problem?" is one of the highest-value questions in problem solving — the answer is yes more often than people expect, and once it's yes you have fifty years of algorithms available. → [[problem-solving/thinking-patterns|Thinking Patterns]]

**Ask three questions** to pick your algorithm: directed or not, weighted or not, can weights be negative. **Those three answers determine most of your choice.**

**Watch density.** $O(V^2)$ is fine at $V = 1{,}000$ and hopeless at $V = 10^6$. For large sparse graphs, anything touching all pairs is out.

**Check for cycles before assuming a DAG.** Dependency cycles are common and the failure mode is an infinite loop.

**Disconnected graphs are the case people forget.** Traversal from one vertex doesn't reach everything — loop over all vertices, skipping visited ones, if you need full coverage.

**Real graphs aren't random.** Power-law degree distributions, small-world properties, community structure. **A few vertices have enormous degree**, which breaks average-case analyses and matters for load balancing and cache behaviour.

---

## Related
- [[foundations/dsa/04-data-structures/06-graphs|Graphs (data structure)]] — the implementation view
- [[foundations/dsa/05-algorithms/06-dijkstra|Dijkstra]] · [[foundations/dsa/05-algorithms/11-topological-sort|Topological Sort]] — the algorithms
- [[foundations/discrete-math/04-sets-relations-and-functions|Sets, Relations and Functions]] — a graph is a relation
- [[foundations/discrete-math/README|Discrete maths map]]
