# Backtracking — Question Bank

Micro-questions over [[14-backtracking|the backtracking pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. Give the Sudoku illustration.**

<details><summary>Answer</summary>

Fill in a number, check validity, move on. **At a dead end, undo the last choice and try a different number.**

</details>

**2. Define backtracking against DFS.**

<details><summary>Answer</summary>

**DFS with one addition: an explicit "undo" step after each recursive call returns**, so the same shared state can be reused across branches instead of being copied.

</details>

**3. What is pruning?**

<details><summary>Answer</summary>

**Cutting off branches that cannot lead to a valid solution** — eliminating invalid placements early.

</details>

---

## B. The template

**4. Write it.**

<details><summary>Answer</summary>

```python
def backtrack(path, choices):
    if is_complete(path):
        record(path)
        return
    for choice in choices:
        if not is_valid(choice, path):
            continue
        path.append(choice)      # make the choice
        backtrack(path, next_choices(choices, choice))
        path.pop()               # undo — this is the "backtrack"
```

</details>

**5. Which line is "the entire idea"?**

<details><summary>Answer</summary>

**`path.pop()` after the recursive call.** Without it, `path` keeps accumulating across sibling branches that have nothing to do with each other.

</details>

**6. Why is mutating one shared list better than building a new one per call?**

<details><summary>Answer</summary>

**It is asymptotically cheaper** — mutated forward on the way down and unmutated on the way back up, rather than copying at every recursive call.

</details>

---

## C. The copy trap

**7. Why `result.append(path[:])` and not `result.append(path)`?**

<details><summary>Answer</summary>

**`path` is the same mutable list object reused across the whole search.** Appending a reference means every entry in `result` points at the same list — **which is empty again once backtracking finishes.**

</details>

**8. What general trap is that an instance of?**

<details><summary>Answer</summary>

**Reference-type aliasing** — storing a pointer to mutable state instead of a snapshot of it.

</details>

**9. When is the copy *not* needed?**

<details><summary>Answer</summary>

**When you record something immutable** — a string built with `"".join(path)`, or a tuple — since those cannot be mutated afterwards.

</details>

---

## D. Permutations

**10. Trace `[1,2,3]` down the first branch.**

<details><summary>Answer</summary>

choose 1 → `[1]`; choose 2 → `[1,2]`; choose 3 → `[1,2,3]` complete, record; pop to `[1,2]`, no choices left, pop to `[1]`; choose 3 → `[1,3]`; choose 2 → `[1,3,2]` record; …

</details>

**11. How does the code stop a value being reused?**

<details><summary>Answer</summary>

It passes `remaining[:i] + remaining[i+1:]` — **the remaining choices with that one removed.**

</details>

**12. What is the alternative to slicing `remaining`?**

<details><summary>Answer</summary>

**A `used` boolean array** — avoids the $O(n)$ slice per call, at the cost of an extra structure to keep in sync.

</details>

---

## E. Complexity

**13. What is the typical complexity?**

<details><summary>Answer</summary>

**Exponential** — $O(n!)$ for permutations, $O(2^n)$ for subsets.

</details>

**14. Is that a sign of a bad implementation?**

<details><summary>Answer</summary>

**No — it is inherent to enumerating every valid arrangement.**

</details>

**15. What is the main practical lever?**

<details><summary>Answer</summary>

**Pruning** — checking `is_valid` early to cut whole invalid branches before recursing.

</details>

**16. Give the canonical example of pruning paying off.**

<details><summary>Answer</summary>

**N-Queens** — reject a queen placement immediately instead of completing the board and checking at the end.

</details>

---

## F. Trade-offs

**17. What is the recursion risk, and the fix?**

<details><summary>Answer</summary>

Large inputs **hit Python's recursion limit**. Use an iterative approach with an explicit stack.

</details>

**18. What is the most common bug?**

<details><summary>Answer</summary>

**Forgetting to undo a choice** — which silently produces incorrect results rather than an error.

</details>

**19. State the difference between backtracking and plain DFS.**

<details><summary>Answer</summary>

**DFS traverses a structure that already exists; backtracking explores a space of decisions it generates**, undoing each choice before trying the next.

</details>

**20. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Make a choice, recurse, undo it — and prune as early as you can, because the search space is exponential by nature.

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

- [[14-backtracking|Backtracking]] — the pattern
- [[11-dfs-pattern-qb|DFS Pattern — Question Bank]]
- [[dsa/03-algorithms/05-searching/03-state-space-search-qb|State-Space Search — Question Bank]] — the genuine-tree case
