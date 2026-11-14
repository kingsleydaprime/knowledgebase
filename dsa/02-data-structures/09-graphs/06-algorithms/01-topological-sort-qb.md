# Topological Sort — Question Bank

Micro-questions over [[01-topological-sort|the topological sort module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. What is a topological order?**

<details><summary>Answer</summary>

A linear list where every prerequisite node comes before every node that depends on it — equivalently, an arrangement in which **every edge points forwards**.

</details>

**2. Give the getting-dressed illustration.**

<details><summary>Answer</summary>

Underwear → Pants → Shoes, and Socks → Shoes. You cannot put shoes on before socks and pants, nor pants before underwear.

</details>

**3. Give two valid orderings for that graph.**

<details><summary>Answer</summary>

`[Underwear, Socks, Pants, Shoes]` and `[Socks, Underwear, Pants, Shoes]`.

</details>

**4. What does that show?**

<details><summary>Answer</summary>

**A graph can have multiple valid topological orderings.** Where the constraints do not order two tasks, either may come first.

</details>

**5. Name four production applications.**

<details><summary>Answer</summary>

Build systems (Make, Bazel, Webpack), package managers (npm, pip, cargo), university course registration around prerequisites, and spreadsheet recalculation engines.

</details>

---

## B. The vocabulary

**6. What is a DAG?**

<details><summary>Answer</summary>

A directed acyclic graph — directed edges with no circular loops. A prerequisites flowchart.

</details>

**7. What is in-degree, in plain terms?**

<details><summary>Answer</summary>

The number of incoming directed edges pointing into a node — **the number of uncompleted prerequisites a course has**.

</details>

**8. Why does a cycle make topological ordering impossible?**

<details><summary>Answer</summary>

Each vertex on the cycle would have to come before itself. Circular reasoning deadlocks.

</details>

**9. What kind of graph does topological sort require?**

<details><summary>Answer</summary>

Directed **and** acyclic. Both conditions — it is meaningless on an undirected graph and impossible with a cycle.

</details>

---

## C. Kahn's algorithm

**10. Give Kahn's algorithm in six steps.**

<details><summary>Answer</summary>

1. Compute the in-degree of every vertex.
2. Push all vertices with `in_degree == 0` into a FIFO queue.
3. Pop `u`, append it to the order.
4. For every neighbour `v` of `u`, decrement `in_degree[v]`.
5. If `in_degree[v]` hits 0, push `v`.
6. Repeat until the queue is empty.

</details>

**11. What does `in_degree == 0` mean semantically?**

<details><summary>Answer</summary>

Every prerequisite of that task is already done, so it is safe to do now.

</details>

**12. Why does decrementing on the way out model "completing" a task?**

<details><summary>Answer</summary>

Emitting `u` means `u` is finished, so each dependent of `u` now has one fewer outstanding prerequisite.

</details>

**13. State the cycle detection guarantee.**

<details><summary>Answer</summary>

**If `len(topological_order) < V`, a cycle exists.** Circular dependencies prevent in-degrees from ever reaching 0, so those vertices never enter the queue.

</details>

**14. Does Kahn's algorithm need a separate cycle-detection pass?**

<details><summary>Answer</summary>

No — the length check is the cycle test, and it costs nothing extra.

</details>

**15. Kahn's uses a queue. Does it have to?**

<details><summary>Answer</summary>

No — any container works, and the choice only changes *which* valid order you get. A **min-heap** gives the lexicographically smallest topological order, which is what problems asking for a deterministic answer want.

</details>

---

## D. The DFS alternative

**16. How does the DFS variant produce a topological order?**

<details><summary>Answer</summary>

Run DFS and push each vertex onto a list **when it finishes**; reverse the list at the end. Equivalently, sort by **decreasing finish time**.

</details>

**17. Why does decreasing finish time work?**

<details><summary>Answer</summary>

A vertex finishes only after everything reachable from it has finished, so anything it points to already has a smaller finish time and therefore lands later in the reversed list.

</details>

**18. How does the DFS variant detect a cycle?**

<details><summary>Answer</summary>

It looks for a **back edge** — an edge to a grey (still-open) vertex. A directed graph is a DAG iff DFS produces no back edges. See [[../05-traversal/03-traversal-trees-and-edge-classification|edge classification]].

</details>

**19. Which variant would you reach for, and why?**

<details><summary>Answer</summary>

Kahn's, usually — it is iterative (no recursion limit), the cycle check is a length comparison, and the queue can be swapped for a heap to control ties. The DFS variant is neater when you already need finish times for something else.

</details>

---

## E. Costs

**20. Time complexity, and why?**

<details><summary>Answer</summary>

$O(V + E)$ — every vertex is enqueued once and every directed edge is decremented once.

</details>

**21. Space complexity, and what makes it up?**

<details><summary>Answer</summary>

$O(V + E)$ — the adjacency list is $O(V+E)$, plus the in-degree array and queue at $O(V)$.

</details>

---

## F. Traps

**22. What happens if you flip the edge direction?**

<details><summary>Answer</summary>

You get the **reverse** topological order. Be precise about which way dependency points — `u → v` here means "u must happen before v".

</details>

**23. Why must you never assert a single fixed output array in a test?**

<details><summary>Answer</summary>

Multiple valid orders usually exist. Assert the **property** instead: for every edge `u → v`, `u` appears before `v`.

</details>

**24. What is the one check you must always perform?**

<details><summary>Answer</summary>

`len(order) == num_nodes`. Without it, a cyclic graph silently returns a partial order that looks plausible.

</details>

**25. Summarise topological sort in one sentence.**

<details><summary>Answer</summary>

Repeatedly emit whatever has no remaining prerequisites — $O(V+E)$, with cycle detection falling out of the count for free.

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

- [[01-topological-sort|Topological Sort]] — the module
- [[../05-traversal/03-traversal-trees-and-edge-classification-qb|Edge Classification — Question Bank]] — why the DFS variant is correct
- [[../02-paths-cycles-and-connectivity-qb|Paths, Cycles and Connectivity — Question Bank]] — what a DAG is
