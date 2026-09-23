# Matrix Traversal — Question Bank

Micro-questions over [[13-matrix-traversal|the matrix traversal pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The reframing

**1. What is a grid, as a graph?**

<details><summary>Answer</summary>

**Each cell is a node, and each cell is connected to its neighbours** — usually 4, sometimes 8.

</details>

**2. What follows from that?**

<details><summary>Answer</summary>

**DFS and BFS apply directly. There is no new algorithm here, just a different way of expressing "neighbours".**

</details>

**3. What is an implicit graph?**

<details><summary>Answer</summary>

One where nodes and edges are **defined by the structure rather than explicitly stored** — neighbours are computed, not looked up.

</details>

**4. How are neighbours computed?**

<details><summary>Answer</summary>

From `(row, col)` using direction offsets: `[(0,1), (0,-1), (1,0), (-1,0)]`.

</details>

---

## B. What the pattern adds

**5. What is the one thing this pattern adds on top of plain graph traversal?**

<details><summary>Answer</summary>

**The bounds check** — `0 <= r < rows and 0 <= c < cols`.

</details>

**6. Why is it needed here and not in a normal graph?**

<details><summary>Answer</summary>

**There is no explicit neighbour list to bound the search**, so the traversal has to check for the grid's edges itself.

</details>

**7. What does marking a cell visited do here?**

<details><summary>Answer</summary>

**The same thing it does in any graph traversal** — avoids revisiting and infinite loops.

</details>

---

## C. Flood fill

**8. Describe it.**

<details><summary>Answer</summary>

From a start cell, **recursively visit all neighbours holding the old colour, overwriting each with the new one.**

</details>

**9. Why the early `if old_color == new_color: return`?**

<details><summary>Answer</summary>

**Otherwise overwriting does not change anything**, so nothing is ever "marked visited" and the recursion never terminates.

</details>

**10. What is the real-world name for flood fill?**

<details><summary>Answer</summary>

**The bucket fill tool** in paint programs.

</details>

---

## D. Counting regions

**11. How does Number of Islands differ from flood fill?**

<details><summary>Answer</summary>

Instead of one fill from a given start, **loop over every cell and start a new DFS/BFS from any unvisited land cell.**

</details>

**12. Why does that count correctly?**

<details><summary>Answer</summary>

**Each traversal you start from is a new island**, and it marks everything connected as visited so it is not counted twice.

</details>

**13. How would you do it with BFS instead?**

<details><summary>Answer</summary>

Identical structure — **replace the recursive call with a queue**, enqueueing each unvisited land neighbour and marking it visited **on enqueue**.

</details>

---

## E. Trade-offs

**14. What breaks on very large grids?**

<details><summary>Answer</summary>

**Recursion depth.** Use an iterative BFS/DFS with an explicit stack or queue.

</details>

**15. What changes for 8-directional problems?**

<details><summary>Answer</summary>

**Extend the `directions` list with the four diagonals.** Everything else is unchanged.

</details>

**16. When can you not mark visited by overwriting?**

<details><summary>Answer</summary>

**When the grid values must be preserved** — then you need a separate `visited` set.

</details>

**17. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

A grid is a graph whose edges you compute instead of store — so the only new code is the bounds check.

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

- [[13-matrix-traversal|Matrix Traversal]] — the pattern
- [[11-dfs-pattern-qb|DFS Pattern — Question Bank]]
- [[12-bfs-pattern-qb|BFS Pattern — Question Bank]]
- [[dsa/02-data-structures/06-graphs/04-representations-qb|Graph Representations — Question Bank]] — where implicit graphs are defined
