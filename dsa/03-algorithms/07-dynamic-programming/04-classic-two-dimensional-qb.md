# Classic Two-Dimensional DP — Question Bank

Micro-questions over [[04-classic-two-dimensional|the 2-D DP module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Longest common subsequence

**1. State the problem.**

<details><summary>Answer</summary>

Given two sequences, find the longest sequence appearing in both, **in order but not necessarily contiguously**.

</details>

**2. What is the decision?**

<details><summary>Answer</summary>

**Look at the last character of each. Do they match?**

</details>

**3. Give state, transition and base.**

<details><summary>Answer</summary>

**STATE:** `L[i][j]` = LCS length of `a[:i]` and `b[:j]`.
**TRANSITION:** if `a[i-1] == b[j-1]`, `L[i][j] = L[i-1][j-1] + 1`; else `L[i][j] = max(L[i-1][j], L[i][j-1])`.
**BASE:** `L[0][j] = L[i][0] = 0`.

</details>

**4. Justify the mismatch branch.**

<details><summary>Answer</summary>

**One of the two characters cannot be in the LCS**, and you take the better of dropping each.

</details>

**5. Where does the answer sit?**

<details><summary>Answer</summary>

**The bottom-right cell.**

</details>

**6. What is the only place the table grows, and why does that matter?**

<details><summary>Answer</summary>

**The `+1` on the diagonal.** Everywhere else it copies the better neighbour — **which is why the diagonal steps, traced backwards, spell out the subsequence.**

</details>

**7. Describe reconstruction.**

<details><summary>Answer</summary>

Start bottom-right and walk backwards, asking which rule produced each cell: on a character match take the diagonal and emit it; otherwise move to whichever neighbour holds the larger value.

</details>

**8. Is the LCS unique?**

<details><summary>Answer</summary>

**No** — several may share the maximum length. **The tie-break in the `>=` comparison decides which one you get**, and that comparison is your lever if the problem demands a specific one.

</details>

---

## B. 0/1 knapsack

**9. State the problem.**

<details><summary>Answer</summary>

Items with weights and values, a capacity. **Each item may be taken at most once.** Maximise value.

</details>

**10. Give state, transition and base.**

<details><summary>Answer</summary>

**STATE:** `K[i][w]` = best value using only the first $i$ items within capacity $w$.
**TRANSITION:** `K[i][w] = max(K[i-1][w], K[i-1][w - wt[i]] + val[i])`.
**BASE:** `K[0][w] = 0`.

</details>

**11. Which part of the transition is the "0/1"?**

<details><summary>Answer</summary>

**The `K[i-1][...]` on *both* branches.** Both options consult the row above — the state with item $i$ not yet considered — **which is exactly what stops the item being used twice.**

</details>

**12. How do you reconstruct which items were taken?**

<details><summary>Answer</summary>

`K[i][w] != K[i-1][w]` means the value changed when item $i$ became available, so **item $i$ was taken**. Subtract its weight and continue up. **Same backwards walk as LCS, asking a different question.**

</details>

---

## C. The loop direction

**13. Collapsing knapsack to one row, which inner loop direction is correct?**

<details><summary>Answer</summary>

**Downwards** — `for w in range(cap, wt - 1, -1)`.

</details>

**14. Explain precisely why.**

<details><summary>Answer</summary>

Going downwards, larger indices are written first, so when you read `row[w - wt]` — a **smaller** index — it has not yet been touched this iteration and **still holds the previous row's value**, the state before item $i$ was available.

</details>

**15. What does the upward loop do instead?**

<details><summary>Answer</summary>

`row[w - wt]` was **already updated this iteration**, so it may already include item $i$ — and adding `val` again uses the item twice.

</details>

**16. Is the upward loop simply broken?**

<details><summary>Answer</summary>

**No — it is the correct solution to the *unbounded* knapsack**, where items may be reused. **Two problems, one line of difference, and the line is a loop direction.**

</details>

**17. Why is "which way does the loop go?" a real interview question?**

<details><summary>Answer</summary>

Because it silently changes which problem you solved, and **the bug survives casual testing** — the lab's first instance gives 9 either way.

</details>

**18. Give an instance that exposes it.**

<details><summary>Answer</summary>

Weight `[3]`, value `[5]`, capacity 9: 0/1 gives **5**, the upward loop gives **15** — the single item used three times.

</details>

---

## D. Edit distance

**19. What is edit distance, and what is it built into?**

<details><summary>Answer</summary>

Fewest single-character insertions, deletions and replacements turning one string into another — **Levenshtein distance**, what spell-checkers and `diff` are built on.

</details>

**20. Give state, transition and base.**

<details><summary>Answer</summary>

**STATE:** `D[i][j]` = edits to turn `a[:i]` into `b[:j]`.
**TRANSITION:** if characters match, `D[i][j] = D[i-1][j-1]` (free); else `D[i][j] = 1 + min(D[i-1][j], D[i][j-1], D[i-1][j-1])`.
**BASE:** `D[i][0] = i`, `D[0][j] = j`.

</details>

**21. Why do these base cases carry real content, unlike LCS's?**

<details><summary>Answer</summary>

Turning `"kit"` into `""` costs **3 deletions**, so the first column counts upward. LCS's row of zeros says only "an empty sequence shares nothing".

</details>

**22. What does each of the three neighbours correspond to?**

<details><summary>Answer</summary>

**Above is a deletion, left is an insertion, diagonal is a replacement** (or a free match).

</details>

**23. Why does that correspondence matter?**

<details><summary>Answer</summary>

**It is what turns a number into a usable edit script** — which is what `diff` prints.

</details>

---

## E. Traps

**24. What is the off-by-one between table and strings?**

<details><summary>Answer</summary>

The table is $(n{+}1)\times(m{+}1)$, so **`L[i][j]` concerns `a[i-1]` and `b[j-1]`**. Mixing conventions mid-function is the most common source of a table that is almost right.

</details>

**25. What happens if you copy one problem's base row into another's solution?**

<details><summary>Answer</summary>

**A plausible wrong table.** LCS's row 0 is all zeros; edit distance's is `0,1,2,3,…`.

</details>

**26. Distinguish LCS from longest common substring.**

<details><summary>Answer</summary>

**Substring must be contiguous**, and it is a different recurrence — **on a mismatch the value resets to 0** rather than taking a max, and **the answer is the largest cell anywhere** rather than the bottom-right.

</details>

**27. Is knapsack polynomial?**

<details><summary>Answer</summary>

**No.** $O(n \cdot \text{cap})$ is **pseudo-polynomial**, linear in the capacity's *value*. A capacity of $10^9$ is infeasible, and **0/1 knapsack is NP-hard**.

</details>

**28. What is the testing lesson?**

<details><summary>Answer</summary>

**One passing example is not a test** — which is why the lab runs 300 random instances against brute force.

</details>

**29. Summarise 2-D DP in one sentence.**

<details><summary>Answer</summary>

A table indexed by two prefixes, where the decision at each cell is a small fixed set of moves — and the direction you fill it in is the difference between two different problems.

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

- [[04-classic-two-dimensional|Classic Two-Dimensional DP]] — the module
- [[03-classic-one-dimensional-qb|Classic 1-D DP — Question Bank]]
- [[02-memoisation-and-tabulation-qb|Memoisation & Tabulation — Question Bank]]
