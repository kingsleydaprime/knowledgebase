# DFS Pattern — Question Bank

Micro-questions over [[11-dfs-pattern|the DFS pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

This bank is about **recognising** the problem shape. The mechanics are in [[dsa/02-data-structures/06-graphs/05-traversal/01-depth-first-search-qb|the DFS bank]].

---

## A. The shape

**1. What shape of problem is DFS the right tool for?**

<details><summary>Answer</summary>

**Anything that asks you to explore every path or branch of a tree or graph** — not just find one answer and stop.

</details>

**2. Give the maze illustration.**

<details><summary>Answer</summary>

Walk down each path until a dead end, then backtrack and try another.

</details>

---

## B. The three recognitions

**3. "Find all paths from root to leaves" — why DFS?**

<details><summary>Answer</summary>

**You need to explore every branch**, so preorder-style DFS that builds up a path as it descends is a direct fit.

</details>

**4. "Clone a graph" — why DFS?**

<details><summary>Answer</summary>

You need to **visit every node and edge exactly once**, which is exactly what DFS with a `visited` map guarantees.

</details>

**5. "Order tasks with dependencies" — why DFS?**

<details><summary>Answer</summary>

DFS **finishes exploring everything a node depends on before the node itself is done** — so appending nodes as they *finish* (postorder) gives a valid ordering.

</details>

---

## C. Backtracking inside DFS

**6. In `path_sum_ii`, what does `path.pop()` do?**

<details><summary>Answer</summary>

**Undoes the choice before returning to the parent call** — the backtracking step.

</details>

**7. What happens without it?**

<details><summary>Answer</summary>

The path keeps growing across sibling branches, so **every recorded path contains nodes from branches you already left.**

</details>

**8. How does this relate to the backtracking pattern?**

<details><summary>Answer</summary>

Here the undo is **a side detail**; in [[14-backtracking|backtracking]] the "undo the choice before returning" mechanic **is the main point of the algorithm.**

</details>

---

## D. Cycle detection

**9. What two sets does the topological sort keep, and why?**

<details><summary>Answer</summary>

**`visited`** — finished nodes, so you never redo work. **`visiting`** — nodes currently on the recursion path, **which is what detects cycles.**

</details>

**10. Why does `visiting` catch cycles when `visited` cannot?**

<details><summary>Answer</summary>

**`visited` means "seen at some point", including on a branch already finished.** A cycle needs a node seen while **still on the current path** — which is precisely what `visiting` records.

</details>

**11. Trace edges `[[0,1],[1,2],[2,3]]`.**

<details><summary>Answer</summary>

Visit 0 → 1 → 2 → 3; 3 has nothing left, append 3; backtrack appending 2, 1, 0. **Reverse the finishing order: `[0,1,2,3]`.**

</details>

---

## E. Trade-offs

**12. When should you not use DFS?**

<details><summary>Answer</summary>

**When you need the shortest path** — DFS explores deeply before broadly, so use BFS.

</details>

**13. What is the recursion risk, and the fix?**

<details><summary>Answer</summary>

**Very deep graphs hit Python's recursion limit.** Use an iterative DFS with an explicit stack.

</details>

**14. What is the difference between DFS and backtracking?**

<details><summary>Answer</summary>

**DFS traverses a structure that already exists; backtracking explores a space of decisions it generates**, undoing each choice before trying the next. Backtracking is DFS over an implicit tree of choices.

</details>

**15. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Reach for DFS when the question is about whole paths or about finishing dependencies — and keep a second set when you need to know you are still standing on the path.

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

- [[11-dfs-pattern|DFS Pattern]] — the pattern
- [[dsa/02-data-structures/06-graphs/05-traversal/01-depth-first-search-qb|Depth-First Search — Question Bank]] — the mechanics
- [[14-backtracking-qb|Backtracking — Question Bank]]
