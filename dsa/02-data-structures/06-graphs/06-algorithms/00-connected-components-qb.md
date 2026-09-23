# Connected Components — Question Bank

Micro-questions over [[00-connected-components|the connected components module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The vocabulary

**1. What is a connected component?**

<details><summary>Answer</summary>

A **maximal** set of vertices that can all reach one another — maximal meaning you cannot add another vertex without breaking the property.

</details>

**2. What guarantee do components give about coverage?**

<details><summary>Answer</summary>

**Every vertex is in exactly one component**, so the components partition the graph — nothing left over, nothing counted twice.

</details>

**3. What is an isolated vertex?**

<details><summary>Answer</summary>

A vertex with no edges. **It forms a component by itself.**

</details>

**4. What is flood fill?**

<details><summary>Answer</summary>

Starting at one vertex and traversing everything reachable, marking as you go. One flood fill discovers exactly one component, so **the number of times you must start a fresh one *is* the component count**.

</details>

**5. What is union-find?**

<details><summary>Answer</summary>

Also disjoint-set union (DSU) — a structure maintaining a partition under `find` (which group is this in?) and `union` (merge these two groups). See [[10-union-find|union-find]].

</details>

**6. What is a redundant edge, and what does it mean?**

<details><summary>Answer</summary>

An edge whose endpoints are already in the same component. It merges nothing. **In a graph built only from merging edges, a redundant edge is exactly a cycle.**

</details>

**7. What is incremental / dynamic connectivity?**

<details><summary>Answer</summary>

The setting where edges arrive over time and you must answer after each one. **It is the case that decides between traversal and union-find.**

</details>

---

## B. Flood fill

**8. How do you count components with DFS or BFS?**

<details><summary>Answer</summary>

Loop over **all vertices**. For each one not yet visited, increment a counter and flood-fill from it.

</details>

**9. What is the cost?**

<details><summary>Answer</summary>

$O(V + E)$ in total, regardless of how many components there are.

</details>

**10. Why must the outer loop run over vertices and not edges?**

<details><summary>Answer</summary>

Isolated vertices have no edges, so iterating over edges never sees them and you undercount.

</details>

**11. Does DFS or BFS give a different answer?**

<details><summary>Answer</summary>

No — same components, same count. BFS additionally gives you the **fewest-edges path** between vertices for free, which is the only reason to prefer it here.

</details>

---

## C. Union-find and the counting identity

**12. What does union-find assume at the start?**

<details><summary>Answer</summary>

That nothing is connected: $V$ components, everyone alone.

</details>

**13. What happens per edge?**

<details><summary>Answer</summary>

Either it joins two different groups — the count drops by one — or it joins two vertices already together and changes nothing.

</details>

**14. State the counting identity.**

<details><summary>Answer</summary>

$$\text{components} = V - (\text{number of edges that actually merged two groups})$$

</details>

**15. Seven teams, three merging meetings — how many clusters?**

<details><summary>Answer</summary>

$7 - 3 = 4$.

</details>

**16. What is the first thing that falls out of the same counter for free?**

<details><summary>Answer</summary>

**Cycle detection.** `union` returning `False` *is* "this edge creates a cycle" — which is exactly how [[06-minimum-spanning-tree|Kruskal's algorithm]] avoids them.

</details>

**17. What is the second?**

<details><summary>Answer</summary>

**"Is this a tree?"** — a graph is a tree iff the count reaches 1 **and** every edge merged (i.e. connected with $V-1$ edges).

</details>

**18. What is the cost per union-find operation?**

<details><summary>Answer</summary>

With path compression and union by rank, effectively $O(\alpha(V))$ — an amortised result needing a potential argument to prove, and **below 5 for any $V$ that will ever exist**.

</details>

---

## D. Choosing a method

**19. 2,000 teams, meetings arriving one at a time, report clusters after each — is re-running DFS acceptable?**

<details><summary>Answer</summary>

No. The lab measures union-find at 0.0026s against DFS re-runs at 1.2407s over 600 edges — **about 500× slower**, and the gap grows with both $V$ and $E$.

</details>

**20. Why is the gap structural rather than a constant factor?**

<details><summary>Answer</summary>

Re-running DFS is $O(V+E)$ **per edge**, so $O(E(V+E))$ overall. Union-find pays $O(\alpha(V))$ per edge and **never recomputes anything**.

</details>

**21. Give the full decision table.**

<details><summary>Answer</summary>

| Situation | Use |
| :--- | :--- |
| All edges known, one answer needed | DFS or BFS |
| Edges arrive over time | union-find |
| Need the path between two vertices | BFS |
| On a grid | DFS/BFS flood fill |
| Edges are also **removed** | neither |

</details>

**22. Why is "edges removed" the real limitation?**

<details><summary>Answer</summary>

**Union-find cannot un-merge.** There is no `split`, because path compression has destroyed the information about *which* edge joined what.

</details>

**23. What do you need instead if edges can disappear?**

<details><summary>Answer</summary>

Dynamic connectivity — considerably heavier machinery (link-cut trees, Euler tour trees) or a rebuild from scratch.

</details>

**24. Why prefer a traversal when you need the actual members?**

<details><summary>Answer</summary>

Union-find works but you must group by root afterwards; a single DFS hands you the groups directly and is simpler.

</details>

---

## E. Directed graphs

**25. What two questions does "connected" split into once edges have direction?**

<details><summary>Answer</summary>

**Weakly connected** — components computed by ignoring direction. **Strongly connected** — sets that can all reach each other **respecting** direction.

</details>

**26. On `a→b, b→c, c→a, c→d, d→e, e→d`, give both answers.**

<details><summary>Answer</summary>

Weak: **1** component, `[a, b, c, d, e]`. Strong: **2** — `[a, b, c]` and `[d, e]`, because `d` and `e` are reachable from the others but cannot get back.

</details>

**27. Is choosing between them an algorithmic or a modelling question?**

<details><summary>Answer</summary>

**A modelling question.** "Which teams share information at all?" is weak; "which teams can all reach each other?" is strong. Asking for "the connected components" of a directed graph without saying which is ambiguous — and a reasonable thing to ask an interviewer to clarify.

</details>

**28. How do you compute weak components?**

<details><summary>Answer</summary>

Just run the undirected algorithm on the underlying undirected graph.

</details>

**29. Describe Kosaraju's algorithm.**

<details><summary>Answer</summary>

One DFS to order vertices by **decreasing finish time**, then a second DFS on the **reversed** graph. Each tree of that second forest is one SCC. $O(V+E)$.

</details>

---

## F. Traps

**30. Seven teams, three meetings — why is "two clusters" wrong?**

<details><summary>Answer</summary>

Because lone vertices are components too. The answer is four.

</details>

**31. What breaks on a 5,000-vertex chain?**

<details><summary>Answer</summary>

Recursive DFS — about 1,000 frames in CPython, so one component and one `RecursionError`. Use the explicit stack.

</details>

**32. What must `union` report, and what breaks if it does not?**

<details><summary>Answer</summary>

Whether it **actually merged**. Incrementing blindly breaks both the component count and the cycle detection built on it.

</details>

**33. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

Count components by flood fill when the graph is fixed and by union-find when edges arrive — and the moment edges can also be removed, neither works.

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

- [[00-connected-components|Connected Components]] — the module
- [[10-union-find|Union-Find]] — the incremental structure
- [[06-minimum-spanning-tree|Minimum Spanning Tree]] — where `union` returning False becomes cycle avoidance
