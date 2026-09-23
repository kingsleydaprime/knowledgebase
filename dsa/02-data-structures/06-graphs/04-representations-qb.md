# Graph Representations — Question Bank

Micro-questions over [[04-representations|the graph representations module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

Reference graph throughout: edges `A-B, A-C, B-C, B-D, C-D`.

---

## A. Edge list

**1. What is an edge list?**

<details><summary>Answer</summary>

Just the edges, as pairs: `[("A","B"), ("A","C"), ("B","C"), ("B","D"), ("C","D")]`.

</details>

**2. What space does it use?**

<details><summary>Answer</summary>

$O(E)$ — the smallest of the five.

</details>

**3. What is it good at?**

<details><summary>Answer</summary>

Iterating every edge, in $O(E)$ — exactly what **Kruskal's** algorithm wants, since it sorts all edges by weight.

</details>

**4. What is it bad at?**

<details><summary>Answer</summary>

Finding one vertex's neighbours — you must scan everything, $O(E)$.

</details>

---

## B. Adjacency list

**5. What is an adjacency list?**

<details><summary>Answer</summary>

For each vertex, the list of its neighbours: `{"A": ["B","C"], "B": ["A","C","D"], ...}`.

</details>

**6. Space, and cost of `neighbours(v)`?**

<details><summary>Answer</summary>

Space $O(V + E)$; neighbours in $O(\deg v)$ — **optimal**, you touch exactly what you need.

</details>

**7. Cost of checking one specific edge?**

<details><summary>Answer</summary>

$O(\deg v)$ — you scan the list.

</details>

**8. Why is this the default?**

<details><summary>Answer</summary>

Because BFS, DFS, Dijkstra and topological sort all **iterate neighbours** and never ask about a random pair.

</details>

---

## C. Adjacency map

**9. What is an adjacency map?**

<details><summary>Answer</summary>

The same idea as an adjacency list, but each neighbour collection is a **hash map or set** rather than a list: `{"A": {"B": 1, "C": 1}, ...}`.

</details>

**10. What does it gain?**

<details><summary>Answer</summary>

Edge lookup and edge deletion become $O(1)$ average instead of $O(\deg v)$, and edge weights get a natural home.

</details>

**11. What does it cost?**

<details><summary>Answer</summary>

Still $O(V+E)$ space, but with a larger constant — hash sets are heavier than plain lists.

</details>

**12. When is it the right default?**

<details><summary>Answer</summary>

For a graph that **changes**. It is what NetworkX uses.

</details>

---

## D. Adjacency matrix

**13. What is an adjacency matrix?**

<details><summary>Answer</summary>

A $V \times V$ grid with $M[i][j] = 1$ when the edge exists.

</details>

**14. What space does it use, and what is the crucial qualifier?**

<details><summary>Answer</summary>

$O(V^2)$ — **regardless of edge count**. An empty graph costs the same as a complete one.

</details>

**15. Cost of edge lookup and of listing neighbours?**

<details><summary>Answer</summary>

Edge lookup: a genuine $O(1)$ array index. Neighbours: $O(V)$ — you scan a whole row even if the vertex has two neighbours.

</details>

**16. What is true of the matrix for an undirected graph?**

<details><summary>Answer</summary>

It is **symmetric**, and the diagonal is non-zero exactly where self-loops are.

</details>

**17. What is its real algebraic payoff?**

<details><summary>Answer</summary>

$M^k[i][j]$ counts the **walks of length $k$** from $i$ to $j$.

</details>

**18. Why walks and not paths?**

<details><summary>Answer</summary>

Matrix multiplication sums over all intermediate sequences, including ones that revisit vertices. Counting paths is a much harder problem.

</details>

---

## E. Incidence matrix

**19. What is an incidence matrix?**

<details><summary>Answer</summary>

A $V \times E$ grid — rows are vertices, columns are edges, and an entry marks that the vertex is an endpoint of that edge.

</details>

**20. What space does it use?**

<details><summary>Answer</summary>

$O(V \times E)$ — the largest of all, and rarely used for computation.

</details>

**21. What are its two genuine uses?**

<details><summary>Answer</summary>

1. It handles **parallel edges** naturally, where an adjacency matrix cannot distinguish them.
2. For directed graphs, with $-1$ for the tail and $+1$ for the head, it is the matrix whose **null space is the cycle space** — the foundation of network-flow and electrical-circuit formulations.

</details>

**22. What does each column sum to in the undirected case, and why?**

<details><summary>Answer</summary>

2 — because every edge has two endpoints. That is the handshake lemma again.

</details>

---

## F. Choosing one

**23. Give the space of all five.**

<details><summary>Answer</summary>

Edge list $O(E)$; adjacency list $O(V+E)$; adjacency map $O(V+E)$; adjacency matrix $O(V^2)$; incidence matrix $O(VE)$.

</details>

**24. Cost of `adjacent(u,v)` in each?**

<details><summary>Answer</summary>

Edge list $O(E)$; adjacency list $O(\deg u)$; adjacency map $O(1)$; adjacency matrix $O(1)$; incidence matrix $O(E)$.

</details>

**25. Cost of `neighbours(u)` in each?**

<details><summary>Answer</summary>

Edge list $O(E)$; adjacency list $O(\deg u)$; adjacency map $O(\deg u)$; adjacency matrix $O(V)$; incidence matrix $O(E)$.

</details>

**26. Read those two rows together — what is the single trade?**

<details><summary>Answer</summary>

The adjacency **matrix** wins `adjacent` and loses `neighbours`; the adjacency **list** does the opposite. That trade *is* what choosing a representation means — which is why "which is best?" has no answer until you know which operation your algorithm calls most.

</details>

**27. Cost of `remove_edge` in edge list vs adjacency map?**

<details><summary>Answer</summary>

Edge list $O(E)$ — find it first. Adjacency map $O(1)$ average.

</details>

**28. Give the five practical decisions.**

<details><summary>Answer</summary>

- Sparse ($E \approx V$) and you traverse → **adjacency list** (most real graphs).
- The graph changes, or you need edge lookup → **adjacency map**.
- Dense ($E \approx V^2$), small $V$, or matrix algebra → **adjacency matrix**.
- Sorting edges (Kruskal) or a file format → **edge list**.
- Parallel edges, or the cycle space → **incidence matrix**.

</details>

**29. Where is the crossover between list and matrix?**

<details><summary>Answer</summary>

Roughly $E \sim V^2/32$ if you store matrix bits — or simply where $V^2$ stops fitting in memory.

</details>

**30. Why is a matrix not an option at $V = 10^6$, at any density?**

<details><summary>Answer</summary>

$10^{12}$ entries. Even one bit each is 125 GB.

</details>

**31. A social network has $10^6$ users averaging 200 friends. Compare list and matrix storage.**

<details><summary>Answer</summary>

Adjacency list: $\approx 2 \times 10^8$ entries. Adjacency matrix: $10^{12}$ entries. About **5,000× more** for the matrix — and the matrix is 99.98% zeros.

</details>

---

## G. Implicit graphs

**32. What is an implicit graph?**

<details><summary>Answer</summary>

One you never store at all — the neighbours are **computed on demand** rather than looked up.

</details>

**33. Give the grid-maze example.**

<details><summary>Answer</summary>

Each cell is a vertex and each open orthogonal neighbour is an edge. You generate neighbours by adding the four offsets and bounds-checking, instead of building any adjacency structure.

</details>

**34. Where else does this apply?**

<details><summary>Answer</summary>

State-space search — puzzle configurations, word ladders, game positions — where the graph is astronomically large but each node's neighbours are cheap to generate.

</details>

**35. State the idea in one sentence.**

<details><summary>Answer</summary>

**You traverse the graph without ever holding it.**

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[04-representations|Graph Representations]] — the module
- [[01-what-a-graph-is-qb|What a Graph Is — Question Bank]] — where the ADT is defined
- [[05-traversal/index|Graph Traversal]] — the algorithms that consume `neighbours()`
