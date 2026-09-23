# Minimum Spanning Tree — Question Bank

Micro-questions over [[06-minimum-spanning-tree|the MST module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The problem

**1. What is a spanning tree?**

<details><summary>Answer</summary>

A tree touching **every** vertex, using $V-1$ edges. A barebones highway map connecting all cities.

</details>

**2. What is a minimum spanning tree?**

<details><summary>Answer</summary>

The spanning tree with the **smallest total edge weight**. The cheapest possible highway map.

</details>

**3. Give the motivating illustration.**

<details><summary>Answer</summary>

Laying fibre-optic cable between cities. Connecting every pair directly wastes millions in redundant wire; an MST finds the cheapest layout where everyone can still reach everyone, with no closed loops.

</details>

**4. Name three production applications.**

<details><summary>Answer</summary>

Telecommunications and utilities (water pipes, electrical grids, cabling); single-linkage hierarchical clustering in ML; road system construction with minimal asphalt.

</details>

**5. Why does an MST have no cycles?**

<details><summary>Answer</summary>

A cycle means one edge is redundant — everything is still connected without it — so dropping the heaviest edge of any cycle gives a cheaper connected graph. A minimum-weight solution therefore cannot contain one.

</details>

---

## B. The cut property

**6. State the cut property.**

<details><summary>Answer</summary>

**The cheapest edge crossing any boundary split belongs in the MST.** Greedily choosing the cheapest bridge across a river.

</details>

**7. Why does it hold?**

<details><summary>Answer</summary>

Any spanning tree must cross the cut somewhere. If it crosses by a more expensive edge, swap that edge for the cheapest crossing one — still spanning, still connected, and strictly cheaper. So the minimum must use the cheapest crossing edge.

</details>

**8. What do both classic algorithms have in common?**

<details><summary>Answer</summary>

Both are **greedy**, and both are correct for the same reason: the cut property. They differ only in which cut they apply it to.

</details>

---

## C. Kruskal's algorithm

**9. State Kruskal's strategy.**

<details><summary>Answer</summary>

Sort **all edges** globally by weight, then greedily add the cheapest edge unless both endpoints are already connected — which would create a cycle.

</details>

**10. What two structures does it need?**

<details><summary>Answer</summary>

A sorted **edge array** and [[10-union-find|union-find]].

</details>

**11. How does union-find detect a cycle?**

<details><summary>Answer</summary>

`union(u, v)` returns `True` only if `u` and `v` were **not** already connected. Returning `False` means the edge would close a cycle, so you skip it.

</details>

**12. When can you stop early?**

<details><summary>Answer</summary>

Once `edges_used == V - 1`. The tree is complete and the remaining edges cannot improve it.

</details>

**13. How do you detect a disconnected graph?**

<details><summary>Answer</summary>

You run out of edges with `edges_used < V - 1`. No spanning tree exists.

</details>

**14. What is Kruskal's time complexity, and what dominates?**

<details><summary>Answer</summary>

$O(E \log E)$ — the **sort** dominates; the union-find operations are effectively $O(\alpha(V))$ each.

</details>

**15. Which graph representation does Kruskal want?**

<details><summary>Answer</summary>

An **edge list**. It never asks for a vertex's neighbours, so an adjacency list buys it nothing.

</details>

---

## D. Prim's algorithm

**16. State Prim's strategy.**

<details><summary>Answer</summary>

Start from any vertex. Use a **min-heap** to repeatedly attach the cheapest edge connecting an unvisited vertex to the growing tree.

</details>

**17. Give the physical metaphor.**

<details><summary>Answer</summary>

Expanding an electrical grid outward from a power station — one connected blob that grows.

</details>

**18. What two structures does it need?**

<details><summary>Answer</summary>

A **min-heap** and a **visited set**.

</details>

**19. Why does it need a stale entry check?**

<details><summary>Answer</summary>

The same vertex can be pushed by several tree vertices at different weights. On pop, `if u in visited: continue` discards the outdated ones — exactly as in [[02-dijkstra|Dijkstra]].

</details>

**20. What is Prim's time complexity?**

<details><summary>Answer</summary>

$O(E \log V)$ with a binary heap.

</details>

**21. What does the starting vertex affect?**

<details><summary>Answer</summary>

Nothing about the total cost. It may change *which* MST you get when weights tie, but not the weight.

</details>

---

## E. Prim's vs Dijkstra

**22. The two algorithms look almost identical. What is the one difference?**

<details><summary>Answer</summary>

**What you push.** Dijkstra pushes `dist[u] + weight` — cumulative distance from the source. Prim pushes `weight` alone — the cost of *this one edge* into the tree.

</details>

**23. Why does that one change produce a completely different object?**

<details><summary>Answer</summary>

Dijkstra minimises distance **from a source to each vertex**; Prim minimises the **total weight of edges used to connect everything**. Different objective, same skeleton.

</details>

---

## F. Choosing

**24. Compare Kruskal and Prim across four rows.**

<details><summary>Answer</summary>

| | Kruskal | Prim |
| :--- | :--- | :--- |
| Approach | edges globally | grows one tree from a root |
| Structures | union-find + sort | min-heap + visited set |
| Time | $O(E \log E)$ | $O(E \log V)$ |
| Best for | **sparse** ($E \approx V$) | **dense** ($E \approx V^2$) |

</details>

**25. Why does Kruskal suit sparse graphs?**

<details><summary>Answer</summary>

Its cost is dominated by sorting $E$ edges, so few edges means little work. On a dense graph you sort $V^2$ edges and most of them get rejected.

</details>

**26. Space complexity of either?**

<details><summary>Answer</summary>

$O(V + E)$ — the union-find parent array, the heap, and the adjacency or edge structures.

</details>

**27. What if the graph is already given as an edge list from a file?**

<details><summary>Answer</summary>

Kruskal, without hesitation — it consumes that representation directly, while Prim would need you to build an adjacency structure first.

</details>

---

## G. Traps

**28. Does MST apply to directed graphs?**

<details><summary>Answer</summary>

No. Directed graphs need a **minimum arborescence**, via Edmonds' algorithm — a completely different and more complex construction.

</details>

**29. Does an MST contain the shortest path between two vertices?**

<details><summary>Answer</summary>

**Not necessarily.** An MST minimises **total global edge weight**, not individual path lengths. A path between two nodes in the MST can be far longer than their shortest path in the original graph. Use [[02-dijkstra|Dijkstra]] for shortest paths.

</details>

**30. What happens on a disconnected graph?**

<details><summary>Answer</summary>

No spanning tree exists — you cannot place $V-1$ edges. What you get instead is a **minimum spanning forest**, one tree per component.

</details>

**31. Is the MST unique?**

<details><summary>Answer</summary>

Only if all edge weights are **distinct**. With ties, several MSTs of equal total weight can exist — which is why tests should assert the total cost, not a specific edge set.

</details>

**32. Summarise MST in one sentence.**

<details><summary>Answer</summary>

Connect everything as cheaply as possible with no redundancy — greedily, by the cut property, either sorting all edges (Kruskal) or growing one blob (Prim).

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

- [[06-minimum-spanning-tree|Minimum Spanning Tree]] — the module
- [[10-union-find|Union-Find]] — what makes Kruskal work
- [[02-dijkstra-qb|Dijkstra — Question Bank]] — the near-identical algorithm with a different push
