# Union-Find — Question Bank

Micro-questions over [[10-union-find|the union-find module]]. Answer in a full sentence before opening the toggle. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The object

**1. What is union-find?**

<details><summary>Answer</summary>

A structure for tracking which things are grouped together, **when groups can only ever merge and never split**. Also called disjoint set union (DSU).

</details>

**2. What are disjoint sets?**

<details><summary>Answer</summary>

A collection of groups where nothing belongs to more than one. Every element is in exactly one group at any moment.

</details>

**3. What is a representative, and what is the entire trick?**

<details><summary>Answer</summary>

One chosen member standing for the whole group — also called the root or leader. **Two elements are in the same group exactly when they have the same representative**, so membership is one comparison rather than a search.

</details>

**4. What is a parent pointer?**

<details><summary>Answer</summary>

A reference from each element to another in its group. Following parents repeatedly reaches the representative, **which is its own parent**.

</details>

**5. What is `find`?**

<details><summary>Answer</summary>

The operation returning an element's representative, by following parent pointers to the top.

</details>

**6. What is `union`?**

<details><summary>Answer</summary>

The operation merging two groups, by making one group's representative point at the other's.

</details>

---

## B. The two optimisations

**7. What is path compression?**

<details><summary>Answer</summary>

Applied during `find`: once you have walked up to the representative, go back and point every element you passed **directly** at it. **It makes the structure flatter every time you use it.**

</details>

**8. What is union by rank?**

<details><summary>Answer</summary>

When merging, always attach the **shorter** tree underneath the taller one, so the result never gets deeper than it needs to be.

</details>

**9. What is union by size, and how does it compare?**

<details><summary>Answer</summary>

Attach the **smaller** group under the larger. A close relative that works just as well.

</details>

**10. What happens without either optimisation?**

<details><summary>Answer</summary>

The trees degenerate into linear chains — effectively [[04-linked-lists|linked lists]] — and `find` becomes $O(n)$.

</details>

**11. What does union by rank alone bound the height to?**

<details><summary>Answer</summary>

$O(\log n)$.

</details>

**12. What does path compression alone achieve?**

<details><summary>Answer</summary>

It flattens the tree toward near-constant depth on repeated access — but without rank you can still build a tall tree before compressing it.

</details>

---

## C. The complexity

**13. What is the inverse Ackermann function?**

<details><summary>Answer</summary>

Written $\alpha(n)$ — the per-operation cost once both optimisations are used. It grows so extraordinarily slowly that it is **less than 5 for any $n$ you could ever store**.

</details>

**14. Is union-find genuinely $O(1)$?**

<details><summary>Answer</summary>

**No — strictly it is not.** It is treated as constant in practice, but the honest statement is $O(\alpha(n))$ amortised, which requires a potential argument to prove.

</details>

---

## D. The ADT

**15. List the union-find ADT.**

<details><summary>Answer</summary>

`make_set(x)` $O(1)$; `find(x)` $O(\alpha(n))$; `union(x, y)` $O(\alpha(n))$; `connected(x, y)` — just `find(x) == find(y)`; `count()` — separate groups remaining.

</details>

**16. How is `count()` maintained?**

<details><summary>Answer</summary>

Start it at the number of elements and **decrement on every successful union**.

</details>

**17. What should `union` return, and why does it matter?**

<details><summary>Answer</summary>

Whether a merge **actually happened**. If `x` and `y` were already together, that is a useful signal — and it is exactly how [[06-graphs/06-algorithms/06-minimum-spanning-tree|Kruskal's algorithm]] detects an edge that would create a cycle.

</details>

**18. Do you usually care about the representative's identity?**

<details><summary>Answer</summary>

No — only that two elements sharing one are in the same group. Which element is chosen is an implementation detail.

</details>

---

## E. The restriction

**19. Why is there no `split` operation, and why can there not be one?**

<details><summary>Answer</summary>

**Path compression works by discarding the history of how groups were built** — it rewires pointers straight to the representative — so the information needed to undo a merge is deliberately thrown away. **That is precisely what makes it so fast.**

</details>

**20. Name four problems where union-find is the right structure.**

<details><summary>Answer</summary>

Building a minimum spanning tree; detecting a cycle as edges arrive; counting connected components in a growing graph; grouping accounts as duplicates are discovered.

</details>

**21. What do those four have in common?**

<details><summary>Answer</summary>

**Connections are only ever added.**

</details>

**22. What do you do if connections can be removed?**

<details><summary>Answer</summary>

Recompute components with [[06-graphs/05-traversal/01-depth-first-search|DFS]] or BFS, or reach for a considerably more complex dynamic-connectivity structure.

</details>

---

## F. Cycle detection

**23. State the cycle-detection insight.**

<details><summary>Answer</summary>

**If `union(u, v)` returns `False`, `u` and `v` were already connected through another path — so adding edge `(u, v)` creates a cycle.**

</details>

**24. What two things does that single property power?**

<details><summary>Answer</summary>

Kruskal's MST (add cheapest edges, skip any where `union` returns `False`) and redundant-edge detection (find the single edge creating an unwanted cycle).

</details>

**25. Does this work for directed graphs?**

<details><summary>Answer</summary>

No. Union-find has no notion of direction — it only knows "connected". Directed cycle detection needs [[06-graphs/05-traversal/03-traversal-trees-and-edge-classification|DFS back edges]].

</details>

---

## G. Union-find vs traversal

**26. Compare the two across four rows.**

<details><summary>Answer</summary>

| Feature | Union-Find | DFS / BFS |
| :--- | :--- | :--- |
| Incremental edges | $O(\alpha(n))$ per edge | $O(V+E)$ per query |
| Check membership | $O(1)$ | $O(V+E)$ |
| Retrieve the path | **cannot** | **returns the exact path** |
| Edge deletion | cannot | must re-traverse |

</details>

**27. What is the one thing union-find fundamentally cannot give you?**

<details><summary>Answer</summary>

**The route.** It knows two things are connected; it has no idea how.

</details>

**28. Summarise union-find in one sentence.**

<details><summary>Answer</summary>

Track group membership by pointing everything at a representative and flattening as you go — effectively constant per operation, and permanently unable to un-merge or tell you the path.

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

- [[10-union-find|Union-Find]] — the module
- [[06-graphs/06-algorithms/00-connected-components-qb|Connected Components — Question Bank]]
- [[06-graphs/06-algorithms/06-minimum-spanning-tree-qb|MST — Question Bank]] — Kruskal's use of it
