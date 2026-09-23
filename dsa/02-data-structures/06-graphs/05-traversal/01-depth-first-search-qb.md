# Depth-First Search — Question Bank

Micro-questions over [[01-depth-first-search|the DFS module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. What is depth-first search?**

<details><summary>Answer</summary>

A traversal that commits to exploring one branch all the way to its end before looking at any alternative.

</details>

**2. Give the reading metaphor for depth-first.**

<details><summary>Answer</summary>

Reading one book cover to cover, versus reading page one of every book on the shelf (which is breadth-first).

</details>

**3. Describe the cave-explorer version.**

<details><summary>Answer</summary>

Walk down a tunnel as deep as you can. At a dead end, backtrack to the last junction and try the other direction. When that junction is exhausted, backtrack further.

</details>

**4. What is backtracking?**

<details><summary>Answer</summary>

What the search does on reaching a vertex with no unvisited neighbours — return to the previous decision point and try the next option there.

</details>

**5. Name three things DFS powers in software.**

<details><summary>Answer</summary>

Puzzle solvers (Sudoku, N-Queens), dependency ordering (build systems), and cycle detection.

</details>

---

## B. The vocabulary

**6. What is the call stack, and how does recursive DFS relate to it?**

<details><summary>Answer</summary>

The memory region holding one frame per started-and-not-yet-returned call, in **LIFO** order. Recursive DFS does not create a stack of its own — it **borrows** this one, which is why it is shorter to write and why it can run out of room.

</details>

**7. What is an explicit stack, and what is the one real difference?**

<details><summary>Answer</summary>

A stack you declare yourself, usually a plain list, holding the vertices still to examine. The difference: **a list grows into ordinary heap memory and the call stack does not.**

</details>

**8. What is the visited set?**

<details><summary>Answer</summary>

A set recording which vertices the search has already reached, consulted before descending into any vertex. The chalk mark on the cave wall.

</details>

**9. On a cyclic graph, is the visited set an optimisation?**

<details><summary>Answer</summary>

No. **Without it the search never terminates.** It is a correctness requirement, not a speed-up.

</details>

**10. What is pre-order work, and when do you want it?**

<details><summary>Answer</summary>

Work done for a vertex **on arrival**, before descending. Use it when a vertex's answer depends on what is **above** it — its depth, or the route taken to reach it.

</details>

**11. What is post-order work, and when do you want it?**

<details><summary>Answer</summary>

Work done **on departure**, after every neighbour is fully explored. Use it when a vertex's answer depends on what is **below** it — and it is the order [[../06-algorithms/01-topological-sort|topological sort]] is built on.

</details>

---

## C. The two implementations

**12. Write the shape of recursive DFS.**

<details><summary>Answer</summary>

```python
def dfs(graph, node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

</details>

**13. Write the shape of iterative DFS.**

<details><summary>Answer</summary>

```python
stack = [start]
while stack:
    node = stack.pop()          # LIFO drives depth-first
    if node in visited: continue
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            stack.append(neighbor)
```

</details>

**14. Which line makes iterative DFS depth-first rather than breadth-first?**

<details><summary>Answer</summary>

`stack.pop()` — taking the **most recently pushed** vertex. Change it to `popleft()` and the same code is BFS.

</details>

**15. Why does iterative DFS check `if node in visited: continue` after popping, rather than only before pushing?**

<details><summary>Answer</summary>

A vertex can be pushed several times before it is first popped — by several different neighbours — so it must be re-checked at pop time. The pre-push check is only an optimisation.

</details>

**16. When must you use the iterative version?**

<details><summary>Answer</summary>

On extremely deep graphs — beyond roughly 1,000 levels in Python, where recursion triggers a `RecursionError`.

</details>

**17. Do the recursive and iterative versions visit vertices in the same order?**

<details><summary>Answer</summary>

Not necessarily. Both are valid DFS orders, but the iterative version pushes all neighbours before popping any, so it typically explores the **last** neighbour first unless you reverse the push order.

</details>

---

## D. Applications

**18. How do you detect a cycle in a *directed* graph with DFS?**

<details><summary>Answer</summary>

Track the vertices currently in the active recursion — an `in_stack` set. Reaching a vertex already `in_stack` proves a cycle exists.

</details>

**19. Why isn't the plain `visited` set enough for directed cycle detection?**

<details><summary>Answer</summary>

`visited` tells you a vertex was seen at some point, including on a *finished* branch. A cycle needs a vertex that is seen while still **on the current path** — which is what `in_stack` tracks.

</details>

**20. How does DFS give a topological sort?**

<details><summary>Answer</summary>

Run a **post-order** DFS on a DAG and reverse the finishing order. A vertex finishes only after everything it depends on has finished.

</details>

**21. How do you count connected components with DFS?**

<details><summary>Answer</summary>

Loop over all vertices. If a vertex is not in `visited`, increment a counter and run DFS from it to mark everything reachable.

</details>

---

## E. Costs

**22. Time complexity, and why?**

<details><summary>Answer</summary>

$O(V + E)$ — every vertex is visited once and every edge examined once.

</details>

**23. Space complexity, and what makes it up?**

<details><summary>Answer</summary>

$O(V)$ — the `visited` set, plus stack depth $h \le V$ in the worst case (a linear graph).

</details>

**24. Why is the time not $O(V \times E)$ or $O(E \log E)$?**

<details><summary>Answer</summary>

Because the visited set means no vertex is expanded twice, so the total neighbour-scanning across the whole run sums to $\sum_v \deg(v) = 2E$.

</details>

---

## F. Traps

**25. What happens if you forget the visited set on a cyclic graph?**

<details><summary>Answer</summary>

Infinite recursion — the search goes round the cycle forever.

</details>

**26. What is Python's default recursion limit, and what are the two fixes?**

<details><summary>Answer</summary>

1,000. Either raise it with `sys.setrecursionlimit()`, or use the iterative implementation — which is the safer answer.

</details>

**27. Does DFS find shortest paths?**

<details><summary>Answer</summary>

**No.** It explores arbitrary deep paths first and may find a 10-hop route before ever considering a direct 1-hop one.

</details>

**28. Why does BFS succeed where DFS fails at this?**

<details><summary>Answer</summary>

BFS expands uniformly level by level, so the first path it finds is guaranteed to have the minimum number of edges.

</details>

---

## G. Going further

**29. How do you return the actual path rather than just whether one exists?**

<details><summary>Answer</summary>

Track a **parent map** during the search — `parent[child] = current` — then walk it backwards from the goal at the end and reverse.

</details>

**30. To find *all* paths, what must change, and why does it become exponential?**

<details><summary>Answer</summary>

The visited mark must be **un-marked on the way back out**, so a vertex can appear on a different path later. That turns one traversal into an enumeration of every route, and the number of routes can be exponential in $V$.

</details>

**31. What is iterative deepening?**

<details><summary>Answer</summary>

Depth-limited DFS run repeatedly with the limit increasing from 1. It finds the shortest path like BFS while using DFS's $O(d)$ memory.

</details>

**32. What does iterative deepening cost for that memory saving?**

<details><summary>Answer</summary>

Re-exploration — shallow levels are visited once per round. On a tree with branching factor $b$ the overhead is a constant factor of roughly $b/(b-1)$, because the last level dominates the total.

</details>

**33. Summarise DFS in one sentence.**

<details><summary>Answer</summary>

Go deep, backtrack at dead ends, and mark where you have been — $O(V+E)$, memory proportional to depth, and no guarantee whatsoever about path length.

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

- [[01-depth-first-search|Depth-First Search]] — the module
- [[02-breadth-first-search-qb|Breadth-First Search — Question Bank]] — the counterpart
- [[03-traversal-trees-and-edge-classification-qb|Traversal Trees & Edge Classification — Question Bank]]
