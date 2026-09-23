# Paths, Cycles and Connectivity — Question Bank

Micro-questions over [[02-paths-cycles-and-connectivity|the paths and connectivity module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Routes

**1. What is a route?**

<details><summary>Answer</summary>

Any sequence of vertices where each one is joined to the next by an edge.

</details>

**2. What is a walk?**

<details><summary>Answer</summary>

The most general route — step along edges to neighbours, revisiting any vertex and reusing any edge you like. **Every route is a walk.**

</details>

**3. What is a trail?**

<details><summary>Answer</summary>

A walk that may **not reuse an edge**. You may still revisit a vertex, as long as you arrive by a road you have not driven before.

</details>

**4. What is a path?**

<details><summary>Answer</summary>

A walk that may **not revisit a vertex**. Since you never return to a vertex you can never reuse an edge either, so every path is also a trail.

</details>

**5. What is a simple path?**

<details><summary>Answer</summary>

Exactly the same thing as a path. "Simple" is added for emphasis, because some books use "path" loosely.

</details>

**6. State the containment relationship between the three.**

<details><summary>Answer</summary>

Every path is a trail, and every trail is a walk. The reverse is not true — a walk is usually not a path.

</details>

**7. Why is the word "path" dangerous when reading textbooks?**

<details><summary>Answer</summary>

Books disagree. Some use *path* to mean a walk and *simple path* for no repeated vertices. This course uses **path** = no repeated vertices, which is what algorithms literature almost always means. **The one word that is never ambiguous is "walk".**

</details>

---

## B. Closed routes

**8. What makes a route *closed*?**

<details><summary>Answer</summary>

It ends at the vertex it started from.

</details>

**9. What is a closed walk?**

<details><summary>Answer</summary>

A walk that ends where it started, with nothing else restricted — vertices and edges may be reused freely.

</details>

**10. What is a circuit?**

<details><summary>Answer</summary>

A closed trail: a closed walk that does not reuse an edge. You may pass through the same vertex twice, as long as you never drive the same road twice.

</details>

**11. What is a cycle?**

<details><summary>Answer</summary>

A closed route that does not revisit any vertex, apart from the start, which is also the finish. Also called a simple cycle.

</details>

**12. How many vertices does a cycle need in a simple graph, and why?**

<details><summary>Answer</summary>

At least three. With two you would have to drive back along the single joining edge, which makes it a walk rather than a cycle.

</details>

**13. What lengths of cycle exist in a non-simple graph?**

<details><summary>Answer</summary>

A self-loop is a cycle of length 1; a pair of parallel edges makes one of length 2. Which is one more reason algorithms usually ask for a simple graph.

</details>

**14. How is length counted?**

<details><summary>Answer</summary>

In **edges**, not vertices. A route through four vertices has length 3. Off-by-one mistakes here are extremely common.

</details>

**15. What extra condition do directed paths and cycles carry?**

<details><summary>Answer</summary>

Every edge must be followed **in the direction it points**.

</details>

**16. Can a directed graph contain a cycle when you ignore the arrows but no directed cycle?**

<details><summary>Answer</summary>

Yes, easily — e.g. $A \to B$, $A \to C$, $C \to B$. Undirected it is a triangle; directed it has no cycle at all.

</details>

---

## C. Connectivity, undirected

**17. When is an undirected graph connected?**

<details><summary>Answer</summary>

When you can get from any vertex to any other by some path.

</details>

**18. What is a connected component, and what does "maximal" mean here?**

<details><summary>Answer</summary>

A maximal group of vertices that can all reach each other. **Maximal** means you cannot add another vertex without breaking that property.

</details>

**19. What guarantee do components give about coverage?**

<details><summary>Answer</summary>

Every vertex belongs to **exactly one** component, so the components split the graph completely — nothing left over, nothing counted twice.

</details>

**20. How do you find the components, and at what cost?**

<details><summary>Answer</summary>

One BFS or DFS started from each vertex you have not yet visited. $O(V+E)$ altogether.

</details>

---

## D. Connectivity, directed

**21. What is strongly connected?**

<details><summary>Answer</summary>

For **every** pair $u, v$ there is a directed path from $u$ to $v$ **and** one back from $v$ to $u$. Everywhere reaches everywhere, following the arrows.

</details>

**22. What is weakly connected?**

<details><summary>Answer</summary>

The graph is connected once you rub out all the arrows and treat every edge as two-way. A much weaker promise.

</details>

**23. What is an SCC?**

<details><summary>Answer</summary>

A strongly connected component — a maximal group of vertices that can all reach each other following the arrows. The directed version of a connected component.

</details>

**24. Which implies which?**

<details><summary>Answer</summary>

Strong always implies weak. The reverse fails constantly.

</details>

**25. Give the real-world illustration of weak-but-not-strong.**

<details><summary>Answer</summary>

A one-way street system can look perfectly joined up on a map — weakly connected — while some junction cannot actually be left once you drive into it. That is a strong-connectivity failure and a real problem for anyone using it.

</details>

**26. What is condensing a directed graph, and what does it always produce?**

<details><summary>Answer</summary>

Collapsing each SCC down to a single point. It **always** produces a DAG.

</details>

**27. Why is that genuinely useful?**

<details><summary>Answer</summary>

Any tangle of circular dependencies becomes acyclic once each mutually-dependent group is treated as one unit — which is how a build tool reports "these five packages form a cycle" instead of looping forever.

</details>

---

## E. DAGs

**28. What is a DAG?**

<details><summary>Answer</summary>

A directed acyclic graph — a directed graph with no directed cycle anywhere. Follow the arrows as long as you like and you never arrive back where you started.

</details>

**29. What are DAGs the shape of? Give five examples.**

<details><summary>Answer</summary>

Dependency: build targets, task schedules, spreadsheet formulas, course prerequisites, git commits.

</details>

**30. What can a DAG — and only a DAG — be given?**

<details><summary>Answer</summary>

A **topological order**: a straight-line arrangement where every edge points forwards.

</details>

**31. Why does a directed cycle make topological order impossible?**

<details><summary>Answer</summary>

Each vertex on the cycle would have to come before itself.

</details>

---

## F. The prediction drill

**32. Take the triangle $A \to B \to C \to A$ and reverse one edge, giving $A \to B$, $C \to B$, $A \to C$. Is it strongly connected?**

<details><summary>Answer</summary>

No. $B$ has out-degree 0 — once you reach it you cannot leave, so $B$ cannot reach $A$ or $C$.

</details>

**33. Is it weakly connected?**

<details><summary>Answer</summary>

Yes. Rub out the arrows and it is a triangle, which is connected.

</details>

**34. Is it a DAG?**

<details><summary>Answer</summary>

Yes. There is no way to follow the arrows back to a starting vertex — $A$ is a source and $B$ is a sink.

</details>

**35. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

Three levels of strictness for routes (walk ⊃ trail ⊃ path), the same three closed (closed walk ⊃ circuit ⊃ cycle), and two different meanings of "connected" the moment edges get arrows.

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

- [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — the module
- [[01-what-a-graph-is-qb|What a Graph Is — Question Bank]] — the previous bank
- [[06-algorithms/01-topological-sort|Topological Sort]] — where DAGs are put to work
