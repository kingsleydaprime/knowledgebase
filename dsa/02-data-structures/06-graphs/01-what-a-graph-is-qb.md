# What a Graph Is — Question Bank

Micro-questions over [[01-what-a-graph-is|the graph fundamentals module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The core vocabulary

**1. What is a vertex?**

<details><summary>Answer</summary>

Also called a node — a point in a graph that can be connected to other points by edges. If the graph is a map, a vertex is a city.

</details>

**2. What is an edge?**

<details><summary>Answer</summary>

Also called an arc or link — a connection between two vertices. If a vertex is a city, an edge is a road.

</details>

**3. What are endpoints?**

<details><summary>Answer</summary>

The two vertices connected by a particular edge. **Every edge has exactly two**, and that fact gets used more often than you would expect.

</details>

**4. What does *incident* mean?**

<details><summary>Answer</summary>

The relationship between a **vertex and an edge**: if the vertex is an endpoint of the edge, the two are incident.

</details>

**5. What does *adjacent* mean?**

<details><summary>Answer</summary>

The relationship between **two vertices** connected by the same edge (or two edges meeting at the same vertex). Also called neighbours.

</details>

**6. Why must you not use incident and adjacent interchangeably?**

<details><summary>Answer</summary>

They relate different kinds of thing — incident is edge-to-vertex, adjacent is vertex-to-vertex. Textbooks and exam questions are strict about it.

</details>

**7. What is the degree of a vertex, and what is the one exception?**

<details><summary>Answer</summary>

The number of edges connected to it, written $\deg(v)$. The exception: a **self-loop counts twice**, because both its ends attach to the same vertex.

</details>

**8. What are in-degree and out-degree, and when do they mean anything?**

<details><summary>Answer</summary>

Edges coming in, and edges going out. They only mean something in a **directed** graph.

</details>

**9. What is a self-loop?**

<details><summary>Answer</summary>

An edge connecting a vertex to itself — a web page that links to itself.

</details>

**10. What are parallel edges?**

<details><summary>Answer</summary>

Multiple edges connecting the same pair of vertices — two separate roads between the same two towns.

</details>

**11. What is a simple graph, and why does it matter?**

<details><summary>Answer</summary>

No self-loops and no parallel edges. **Most algorithms quietly assume they are given one**, so it is worth checking your input really is simple before trusting them.

</details>

**12. What is a multigraph?**

<details><summary>Answer</summary>

A graph allowing both parallel edges and self-loops. Road networks and circuit diagrams usually are.

</details>

**13. What is a weighted graph?**

<details><summary>Answer</summary>

One where each edge carries a number — a distance, cost, capacity or travel time, depending on what you are modelling.

</details>

**14. What are order and size?**

<details><summary>Answer</summary>

Order is the number of **vertices**, $\lvert V \rvert$; size is the number of **edges**, $\lvert E \rvert$. Often shortened to $n$ and $m$.

</details>

**15. What do dense and sparse mean, and what do they decide?**

<details><summary>Answer</summary>

Dense: edges close to the maximum possible. Sparse: relatively few edges for the number of vertices. Which you have decides **how you should store the graph** — the whole subject of [[04-representations|lesson 4]].

</details>

---

## B. The four dimensions

**16. Name the four dimensions that must be fixed before choosing an algorithm.**

<details><summary>Answer</summary>

Direction, weight, cycles, connectivity. Get one wrong and the algorithm you choose is wrong.

</details>

**17. What does direction decide?**

<details><summary>Answer</summary>

Whether an edge can be traversed both ways or only one.

</details>

**18. Undirected vs directed — notation and meaning.**

<details><summary>Answer</summary>

Undirected: $\{u,v\}$, curly brackets — both ways; if you can get from $u$ to $v$ you can get back. Directed (digraph): $(u,v)$, round brackets — $u$ to $v$ only, and it says **nothing at all** about going back.

</details>

**19. Give the social media illustration of each.**

<details><summary>Answer</summary>

Friendship is undirected — if I am your friend, you are mine. Following is directed — you following them does not mean they follow you.

</details>

**20. What does weight decide?**

<details><summary>Answer</summary>

Whether BFS suffices or you need [[02-dijkstra|Dijkstra]].

</details>

**21. What does "shortest path" mean in an unweighted graph? In a weighted one?**

<details><summary>Answer</summary>

Unweighted: **fewest edges**, which BFS answers directly. Weighted: **smallest total weight**, a different question entirely — a route with more edges can easily be cheaper.

</details>

**22. What does the presence of cycles force you to do?**

<details><summary>Answer</summary>

Keep a **visited set**. Without one, a traversal goes round the cycle forever and never terminates.

</details>

**23. What is a DAG, and what is it the shape of?**

<details><summary>Answer</summary>

A directed acyclic graph. It is the shape of **dependency** — build steps, task schedules, course prerequisites, spreadsheet formulas.

</details>

**24. Connected vs disconnected — and what does that force?**

<details><summary>Answer</summary>

Connected: one traversal from anywhere reaches everything. Disconnected: a traversal only covers its own piece, so you must **start a fresh traversal from each unreached vertex**. Those pieces are connected components.

</details>

---

## C. The handshake lemma

**25. State the handshaking lemma.**

<details><summary>Answer</summary>

$$\sum_{v \in V} \deg(v) = 2\lvert E\rvert$$

In any undirected graph, the degrees sum to exactly twice the number of edges.

</details>

**26. Why is it true?**

<details><summary>Answer</summary>

Every edge contributes exactly two edge-ends, one at each endpoint, so summing degrees counts every edge twice. A self-loop puts both ends on the same vertex, which is why it adds 2 there.

</details>

**27. What immediately follows about odd-degree vertices?**

<details><summary>Answer</summary>

**The number of odd-degree vertices is always even.** The total is even and the even-degree vertices contribute an even amount, so the odd ones must pair up.

</details>

**28. Can a graph have exactly three vertices of odd degree?**

<details><summary>Answer</summary>

No — three is odd, and the count of odd-degree vertices must be even.

</details>

**29. What is the maximum number of edges in a simple undirected graph on 6 vertices?**

<details><summary>Answer</summary>

$\binom{6}{2} = 15$. In general $\frac{n(n-1)}{2}$ — every pair joined once, no self-loops, no parallels.

</details>

**30. And for a simple directed graph on $n$ vertices?**

<details><summary>Answer</summary>

$n(n-1)$ — each ordered pair once, because $(u,v)$ and $(v,u)$ are different edges.

</details>

---

## D. The graph ADT

**31. What is an ADT, and why read it before the code?**

<details><summary>Answer</summary>

A description of *what* a structure does, written before deciding *how* to build it. The code answers "how"; the ADT answers "what" and "why", and you cannot reliably work those out by reading an implementation.

</details>

**32. Name the four building operations.**

<details><summary>Answer</summary>

`add_vertex(v)`, `add_edge(u, v)`, `remove_edge(u, v)`, `remove_vertex(v)`.

</details>

**33. What must `remove_vertex(v)` also do, and why is that not optional?**

<details><summary>Answer</summary>

Remove **every edge attached to it**. An edge with only one endpoint is not a thing.

</details>

**34. Name the query operations.**

<details><summary>Answer</summary>

`adjacent(u, v)`, `neighbours(v)`, `degree(v)`, `vertices()`, `edges()`, `order()`, `size()`.

</details>

**35. What two operations do weighted graphs add?**

<details><summary>Answer</summary>

`set_weight(u, v, w)` and `weight(u, v)`.

</details>

**36. How do `adjacent(u, v)` and `neighbours(v)` differ as questions?**

<details><summary>Answer</summary>

`adjacent` asks about **one specific pair** — "is there a direct flight from Lagos to Accra?". `neighbours` asks for **a whole list** — "standing here, where can I go?".

</details>

**37. Why can no single representation make both cheap?**

<details><summary>Answer</summary>

An adjacency matrix answers `adjacent` instantly but must scan a whole row for `neighbours`; an adjacency list is the other way round.

</details>

**38. So what is "choosing a representation" really choosing?**

<details><summary>Answer</summary>

**Which of these operations you are willing to make slow** — a choice you can only make once you know which ones your algorithm actually calls.

</details>

**39. Which ADT operation do traversals actually run on?**

<details><summary>Answer</summary>

`neighbours(v)` — which is why it is the one worth making fast.

</details>

**40. Which algorithm wants `edges()` and never asks for neighbours?**

<details><summary>Answer</summary>

[[06-minimum-spanning-tree|Kruskal's algorithm]] — it sorts the whole edge list and never asks a single vertex for its neighbours.

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

- [[01-what-a-graph-is|What a Graph Is]] — the module
- [[02-paths-cycles-and-connectivity-qb|Paths, Cycles and Connectivity — Question Bank]] — the next bank
- [[04-representations|Graph Representations]] — where the ADT costs are tabulated
