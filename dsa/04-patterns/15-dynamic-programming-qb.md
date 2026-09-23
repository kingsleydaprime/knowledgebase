# Dynamic Programming Pattern — Question Bank

Micro-questions over [[15-dynamic-programming|the DP pattern note]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

This bank is about **recognising recurrence shapes**. The theory is in [[dsa/03-algorithms/06-dynamic-programming/01-what-makes-a-problem-dp-qb|what makes a problem DP]].

---

## A. The value proposition

**1. State DP's entire value proposition.**

<details><summary>Answer</summary>

**Eliminating redundant recomputation** — break a problem into overlapping subproblems, solve each exactly once, and reuse the answers.

</details>

**2. What two properties must hold?**

<details><summary>Answer</summary>

**Overlapping subproblems** (the same smaller question gets asked repeatedly) and **optimal substructure** (the best answer to the big problem is built from the best answers to its subproblems).

</details>

**3. Without both, what do you have?**

<details><summary>Answer</summary>

**Plain recursion.** DP is specifically the *caching* of that recursion's repeated work.

</details>

---

## B. The two applications

**4. What is memoisation, in one line?**

<details><summary>Answer</summary>

**Top-down** — keep the natural recursive structure, cache results the first time each subproblem is solved.

</details>

**5. What is tabulation?**

<details><summary>Answer</summary>

**Bottom-up** — build the answer iteratively from the smallest subproblems up, with no recursion at all.

</details>

**6. Give the trade-off.**

<details><summary>Answer</summary>

**Bottom-up avoids call-stack overhead entirely; top-down is often easier to derive first**, since it mirrors the natural recursive definition.

</details>

**7. Fibonacci can beat $O(n)$. How, and should you?**

<details><summary>Answer</summary>

$O(\log n)$ via **matrix exponentiation** ($[[1,1],[1,0]]^n$) or Binet's closed form. **Neither is worth reaching for by default** — they are a footnote once $O(n)$ DP stops being fast enough.

</details>

---

## C. The real skill

**8. What single question does every DP problem come down to?**

<details><summary>Answer</summary>

**How does the answer to a state depend on smaller states?**

</details>

**9. Fibonacci and Climbing Stairs share a recurrence. Why?**

<details><summary>Answer</summary>

**The question is structurally identical** — `dp[i] = dp[i-1] + dp[i-2]` in both.

</details>

**10. State what "getting good at DP" actually means.**

<details><summary>Answer</summary>

**Recognising that two differently-worded problems share a recurrence.**

</details>

---

## D. The six sub-patterns

**11. Name all six and what distinguishes each.**

<details><summary>Answer</summary>

**Fibonacci-style** — `dp[i]` depends on a fixed few previous states. **0/1 knapsack** — subset under a capacity, each item once. **LCS** — two sequences, `dp[i][j]` from three neighbours. **LIS** — best ending at $i$, depends on all earlier $j$. **Subset sum** — knapsack variant asking only "does any subset hit the target?". **Matrix chain** — `dp[i][j]` tries every split point between $i$ and $j$.

</details>

**12. How does NeetCode split them, and why is that split useful?**

<details><summary>Answer</summary>

**1-D DP** (state is one index) versus **2-D DP** (state is two indices — a grid or a pair of sequences). **The dimension of the state is the first thing to decide.**

</details>

---

## E. 1-D

**13. House Robber — recurrence and space?**

<details><summary>Answer</summary>

`dp[i] = max(dp[i-1], dp[i-2] + nums[i])`. **Only the last two states matter, so it collapses to $O(1)$ space.**

</details>

**14. Coin change — which knapsack shape is it, and what is the recurrence?**

<details><summary>Answer</summary>

**Unbounded knapsack** (coins reusable). `dp[a] = 1 + min(dp[a - c])` over every coin $c \le a$.

</details>

**15. Where exactly is the 0/1 versus unbounded distinction?**

<details><summary>Answer</summary>

**Entirely in the loop order.** Reuse-allowed iterates **capacity outermost**; each-item-once iterates **items outermost and capacity descending**, so an item is not counted twice.

</details>

**16. LIS — recurrence, cost, and the improvement?**

<details><summary>Answer</summary>

`dp[i] = 1 + max(dp[j])` over $j < i$ with `nums[j] < nums[i]` — $O(n^2)$. A **binary-search-on-patience-piles** trick gets it to $O(n\log n)$.

</details>

---

## F. 2-D

**17. When does the table become 2-D?**

<details><summary>Answer</summary>

**When the answer depends on two moving parts** — a position in a grid, or an index into *each* of two sequences.

</details>

**18. Unique Paths — recurrence and base case?**

<details><summary>Answer</summary>

`dp[r][c] = dp[r-1][c] + dp[r][c-1]` — each cell is reached from above or from the left. **Base case: the first row and column are all 1.**

</details>

**19. LCS — the two branches?**

<details><summary>Answer</summary>

**Characters match** → extend the diagonal, `dp[i-1][j-1] + 1`. **They do not** → take the better of dropping one character from either string.

</details>

---

## G. Traps

**20. What is the cost of reaching for DP without confirming overlap?**

<details><summary>Answer</summary>

**Memoisation adds overhead for no benefit** — it is just plain recursion or divide and conquer. Merge sort is the canonical recursion *without* overlapping subproblems.

</details>

**21. What is the most common DP bug?**

<details><summary>Answer</summary>

**Off-by-one errors in the base cases** (`dp[0]`, `dp[1]`). **Get the smallest one or two states right by hand before trusting the recurrence for larger $n$.**

</details>

**22. What is the usual space optimisation?**

<details><summary>Answer</summary>

**Keeping only the last row or last few states** — often $O(n^2) \to O(n)$, or $O(n) \to O(1)$.

</details>

**23. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Find the recurrence, decide whether the state is one index or two, and recognise that most problems are one of six shapes you have already seen.

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

- [[15-dynamic-programming|Dynamic Programming Pattern]] — the pattern
- [[dsa/03-algorithms/06-dynamic-programming/01-what-makes-a-problem-dp-qb|What Makes a Problem DP — Question Bank]]
- [[dsa/03-algorithms/06-dynamic-programming/03-classic-one-dimensional-qb|Classic 1-D DP — Question Bank]]
- [[dsa/03-algorithms/06-dynamic-programming/04-classic-two-dimensional-qb|Classic 2-D DP — Question Bank]]
