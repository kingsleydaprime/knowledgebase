# Breadth-First Search — Question Bank

Micro-questions over [[02-breadth-first-search|the BFS module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. What is breadth-first search?**

<details><summary>Answer</summary>

Expanding uniformly across every neighbour at the current distance before considering anything further away.

</details>

**2. Give the physical metaphor.**

<details><summary>Answer</summary>

Concentric ripples from a pebble dropped in water — the wave reaches everything one metre away before it reaches anything two metres away.

</details>

**3. What is the entire difference between BFS and DFS?**

<details><summary>Answer</summary>

The scheduling structure: BFS uses a **queue** (FIFO), DFS uses a **stack** (LIFO). Same code otherwise.

</details>

---

## B. The vocabulary

**4. What is a queue?**

<details><summary>Answer</summary>

A FIFO collection — things leave in the order they arrived, like a supermarket line.

</details>

**5. What is the frontier?**

<details><summary>Answer</summary>

Also called the open set — the vertices discovered but not yet expanded. In BFS it is exactly the contents of the queue: the advancing outer edge of the wave.

</details>

**6. What determines BFS's memory use?**

<details><summary>Answer</summary>

The **size of the frontier** — how wide the wave gets, not how far it travels.

</details>

**7. What is a level?**

<details><summary>Answer</summary>

Also called the layer or distance from the source — the number of edges on the shortest route from the start. Source is level 0, its neighbours level 1, and so on.

</details>

**8. What is the whole reason BFS exists?**

<details><summary>Answer</summary>

**BFS assigns every vertex its correct level the first time it reaches it.** The first arrival is the shortest arrival.

</details>

**9. What is an unweighted graph, and why does it matter here?**

<details><summary>Answer</summary>

One where every edge counts the same. **BFS's shortest-path guarantee holds only here**, because BFS counts edges and nothing else.

</details>

**10. What is a parent map?**

<details><summary>Answer</summary>

Also the predecessor map — a dictionary recording, for each vertex, which vertex the search arrived from. It lets you recover an actual **path** rather than only a distance.

</details>

**11. What is multi-source BFS?**

<details><summary>Answer</summary>

BFS started from several vertices at once, by putting all of them in the queue at distance 0 before the loop begins. It computes, for every vertex, the distance to the **nearest** source — in one pass, at the same $O(V+E)$ cost.

</details>

---

## C. The implementation

**12. State the Golden BFS Rule.**

<details><summary>Answer</summary>

**Mark a vertex visited immediately when ENQUEUING it, not when dequeuing it.**

</details>

**13. What goes wrong if you mark on dequeue?**

<details><summary>Answer</summary>

Multiple neighbours enqueue duplicate copies of the same vertex before it is ever popped, blowing up memory and runtime.

</details>

**14. Write the BFS skeleton.**

<details><summary>Answer</summary>

```python
visited = {start}
queue = deque([start])
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        if neighbor not in visited:
            visited.add(neighbor)      # on enqueue
            queue.append(neighbor)
```

</details>

**15. How do you reconstruct the shortest path at the end?**

<details><summary>Answer</summary>

Record `parent[neighbor] = current` as you enqueue. On reaching the target, walk backwards through `parent` to the source and reverse the list.

</details>

**16. What does `parent[start]` hold, and why?**

<details><summary>Answer</summary>

`None` — it is the sentinel that stops the backwards walk.

</details>

**17. How do you make BFS report distances instead of paths?**

<details><summary>Answer</summary>

Keep a `dist` dict: `dist[neighbor] = dist[current] + 1` at enqueue time. Because the first arrival is the shortest, that value is never revised.

</details>

---

## D. Costs

**18. Time complexity, and why?**

<details><summary>Answer</summary>

$O(V + E)$ — every vertex is enqueued once and every edge examined once.

</details>

**19. Space complexity, and what drives it?**

<details><summary>Answer</summary>

$O(V)$ — the visited set plus the queue. On wide graphs the queue alone can hold $O(V)$ vertices.

</details>

**20. On which shape of graph is BFS memory-cheaper than DFS, and on which is it worse?**

<details><summary>Answer</summary>

BFS is cheaper on a long thin graph (frontier of one) and much worse on a wide shallow one (frontier of $O(V)$). DFS is the reverse — their worst cases are opposite shapes.

</details>

---

## E. Traps

**21. Why must you never write `queue.pop(0)` on a Python list?**

<details><summary>Answer</summary>

It is $O(n)$ — every remaining element shifts down. That turns BFS into $O(V^2 + E)$. Use `collections.deque.popleft()`, which is $O(1)$.

</details>

**22. Why is BFS wrong on a weighted graph?**

<details><summary>Answer</summary>

BFS counts **edges**, not cost. A path with 2 heavy edges can cost more than one with 3 light ones, so the fewest-edges answer is not the cheapest. Use [[../06-algorithms/02-dijkstra|Dijkstra]].

</details>

**23. Is there a weighted case where BFS is still correct?**

<details><summary>Answer</summary>

Yes — when all edges have **equal** weight, since fewest edges then means cheapest. (And 0/1 weights have their own variant, 0-1 BFS with a deque.)

</details>

---

## F. Choosing between BFS and DFS

**24. When do you want BFS?**

<details><summary>Answer</summary>

When the answer depends on **distance from the source** — shortest path in an unweighted graph, nearest match, level-by-level output, flood fill from multiple sources.

</details>

**25. When do you want DFS?**

<details><summary>Answer</summary>

When the answer depends on a whole path or on subtree results — cycle detection, topological sort, backtracking search, connected components (either works, but DFS is lighter here).

</details>

**26. Both are $O(V+E)$. So what actually decides?**

<details><summary>Answer</summary>

The **guarantee** you need (first-found = shortest, or not) and the **memory shape** of your graph (frontier width versus path depth).

</details>

**27. Summarise BFS in one sentence.**

<details><summary>Answer</summary>

Expand in rings using a queue, mark on enqueue, and the first time you touch a vertex you have already found its shortest unweighted distance.

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

- [[02-breadth-first-search|Breadth-First Search]] — the module
- [[01-depth-first-search-qb|Depth-First Search — Question Bank]] — the counterpart
- [[../06-algorithms/02-dijkstra|Dijkstra]] — what to use when edges carry weights
