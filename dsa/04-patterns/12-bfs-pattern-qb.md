# BFS Pattern — Question Bank

Micro-questions over [[12-bfs-pattern|the BFS pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

This bank is about **recognising** the problem shape. The mechanics are in [[dsa/02-data-structures/06-graphs/05-traversal/02-breadth-first-search-qb|the BFS bank]].

---

## A. The shape

**1. What phrasing almost always means BFS?**

<details><summary>Answer</summary>

**"Minimum steps / levels / time to reach X"** in an **unweighted** setting.

</details>

**2. Give the physical metaphor.**

<details><summary>Answer</summary>

**Ripples expanding outward** from a pebble dropped in water.

</details>

**3. Give the social-network illustration.**

<details><summary>Answer</summary>

Finding the shortest connection path between two people — check all paths of length 1, then length 2, and so on.

</details>

---

## B. Level-order

**4. What is the key trick that turns plain BFS into level-order BFS?**

<details><summary>Answer</summary>

**`level_size = len(queue)`** — a snapshot of exactly how many nodes are in this level, taken before processing any of them.

</details>

**5. What happens without it?**

<details><summary>Answer</summary>

**You process the nodes but lose track of which level each one belonged to.**

</details>

**6. Why is `len(queue)` exactly the level width at that moment?**

<details><summary>Answer</summary>

Because at the top of the iteration the queue holds **every node of the current level and nothing else** — the previous level has all been popped and the next level has not been enqueued yet.

</details>

---

## C. Multi-source BFS

**7. What is multi-source BFS?**

<details><summary>Answer</summary>

**Starting BFS from all initial sources simultaneously** — putting all of them in the queue at distance 0 before the loop begins.

</details>

**8. What does it compute?**

<details><summary>Answer</summary>

For every cell, **the distance to the *nearest* source** — in one pass, at the same cost as a single-source run.

</details>

**9. Give the canonical problem.**

<details><summary>Answer</summary>

**Rotting Oranges** — every rotten orange starts in the queue at once, and they spread simultaneously.

</details>

**10. Why would running single-source BFS from each source be wrong as well as slow?**

<details><summary>Answer</summary>

Slow because it is $k$ passes — **and you would then have to take the minimum across all of them per cell**, which multi-source gives you for free by construction.

</details>

**11. What must you check at the end of Rotting Oranges?**

<details><summary>Answer</summary>

**Whether any fresh oranges remain** — if so, they were unreachable and the answer is $-1$, not the elapsed minutes.

</details>

---

## D. Trade-offs

**12. What does BFS guarantee that DFS does not?**

<details><summary>Answer</summary>

**Shortest paths in unweighted graphs.**

</details>

**13. Why does BFS guarantee that?**

<details><summary>Answer</summary>

**It exhausts distance $d$ entirely before touching $d+1$**, so the first time it reaches a node it has done so by the fewest possible edges.

</details>

**14. What is BFS's memory cost, and on what shape is it worst?**

<details><summary>Answer</summary>

**The queue can grow to $O(V)$** — worst on **wide** graphs, where DFS would use far less.

</details>

**15. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

If the question is "how few steps", expand in rings with a queue — snapshot the level size when levels matter, and seed every source at once when the answer is a distance to the nearest of many.

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

- [[12-bfs-pattern|BFS Pattern]] — the pattern
- [[dsa/02-data-structures/06-graphs/05-traversal/02-breadth-first-search-qb|Breadth-First Search — Question Bank]] — the mechanics
- [[11-dfs-pattern-qb|DFS Pattern — Question Bank]]
- [[13-matrix-traversal-qb|Matrix Traversal — Question Bank]]
