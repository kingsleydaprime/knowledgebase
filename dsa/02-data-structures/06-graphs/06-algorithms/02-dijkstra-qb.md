# Dijkstra's Algorithm — Question Bank

Micro-questions over [[02-dijkstra|the Dijkstra module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. What problem does Dijkstra solve?**

<details><summary>Answer</summary>

Single-source shortest paths in a **weighted** graph — smallest total weight, not fewest edges.

</details>

**2. Give the GPS illustration of why BFS is not enough.**

<details><summary>Answer</summary>

A 1-hop highway (90 minutes) versus a 2-hop route through a village (30 minutes). BFS picks the fewest-hops highway; Dijkstra evaluates total cost and picks the faster two-hop route.

</details>

**3. State the difference between BFS and Dijkstra in one sentence.**

<details><summary>Answer</summary>

BFS counts edges with a queue; Dijkstra sums weights with a min-heap.

</details>

**4. Name three production applications.**

<details><summary>Answer</summary>

GPS navigation (Google Maps, Waze), network IP routing (OSPF, on latency), and flight booking search for cheapest combinations.

</details>

---

## B. The vocabulary

**5. What is an edge weight?**

<details><summary>Answer</summary>

The numeric cost of travelling across an edge — distance, time, fee.

</details>

**6. What is relaxation?**

<details><summary>Answer</summary>

Updating the shortest known distance to a node when a cheaper path is discovered. Finding a shortcut road.

</details>

**7. What does the min-heap do here?**

<details><summary>Answer</summary>

Always pops the unvisited node with the **smallest cumulative distance** — i.e. always processes the closest node next.

</details>

**8. What is a stale entry?**

<details><summary>Answer</summary>

An outdated `(distance, node)` pair left in the heap after a shorter path to that node was found. An expired route suggestion.

</details>

**9. Why do stale entries exist at all?**

<details><summary>Answer</summary>

Because a binary heap has no cheap "decrease-key". Instead of updating an entry in place you **push a new, better one** and let the old one sit there — lazy deletion.

</details>

---

## C. The algorithm

**10. Give Dijkstra in five steps.**

<details><summary>Answer</summary>

1. `distances[source] = 0`, everything else infinity.
2. Push `(0, source)` into a min-heap.
3. Pop the smallest `(dist, node)`. If `dist > distances[node]`, skip it — stale.
4. For each neighbour: `new_dist = dist + weight`.
5. If `new_dist < distances[neighbor]`, relax and push `(new_dist, neighbor)`.

</details>

**11. What is the stale check line, exactly?**

<details><summary>Answer</summary>

```python
if current_dist > distances[current_node]:
    continue
```

</details>

**12. Why is the popped node's distance final?**

<details><summary>Answer</summary>

Because every remaining route to it must pass through some node still in the heap, whose distance is **at least** as large — and all weights are non-negative, so it can only grow from there.

</details>

**13. What is the greedy assumption, stated precisely?**

<details><summary>Answer</summary>

**Once a node is popped from the heap, its distance is final and will never decrease.**

</details>

---

## D. Negative weights

**14. Why does Dijkstra fail on negative edge weights?**

<details><summary>Answer</summary>

The greedy assumption breaks: a longer path with 10 hops could suddenly become cheaper later if it contains a $-100$ edge. Dijkstra has already finalised the node and will never revisit it.

</details>

**15. What do you use instead?**

<details><summary>Answer</summary>

[[03-bellman-ford|Bellman-Ford]], at $O(V \cdot E)$.

</details>

**16. Can you just add a constant to every weight to make them positive?**

<details><summary>Answer</summary>

No. Adding $c$ to every edge penalises paths with more edges by $c$ per edge, which changes which path is cheapest. (The correct reweighting is Johnson's algorithm, which uses Bellman-Ford potentials.)

</details>

---

## E. Costs

**17. Time complexity, and where each part comes from?**

<details><summary>Answer</summary>

$O((V + E) \log V)$ — every vertex is popped from the heap, and every edge can trigger a push, each costing $O(\log V)$.

</details>

**18. Space complexity?**

<details><summary>Answer</summary>

$O(V + E)$ — the adjacency list plus heap storage.

</details>

**19. How large can the heap get with lazy deletion?**

<details><summary>Answer</summary>

Up to $O(E)$ entries, since each relaxation pushes one. That is why the bound is often written $O(E \log V)$.

</details>

---

## F. Traps

**20. What happens if you skip the stale entry check?**

<details><summary>Answer</summary>

**The answers stay correct**, but you waste massive CPU re-exploring outdated paths. It is a performance bug, not a correctness bug.

</details>

**21. Why must you never use Dijkstra with negative edges "just to see"?**

<details><summary>Answer</summary>

It fails **silently** — it returns plausible-looking distances that are simply wrong, with no error.

</details>

**22. Summarise the BFS/Dijkstra distinction in structures and costs.**

<details><summary>Answer</summary>

BFS: simple queue, $O(V+E)$, unweighted graphs. Dijkstra: min-heap, $O((V+E)\log V)$, non-negative weighted graphs.

</details>

**23. When is BFS the right choice even on a weighted graph?**

<details><summary>Answer</summary>

When all weights are equal — fewest edges then *is* cheapest, and BFS is strictly faster.

</details>

**24. Summarise Dijkstra in one sentence.**

<details><summary>Answer</summary>

Always expand the cheapest-known node next, relax its edges, and trust that non-negative weights make the first arrival final.

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

- [[02-dijkstra|Dijkstra's Algorithm]] — the module
- [[03-bellman-ford-qb|Bellman-Ford — Question Bank]] — what to use with negative weights
- [[05-a-star-qb|A* — Question Bank]] — Dijkstra plus a heuristic
- [[08-heaps|Heaps]] — the structure that makes it work
