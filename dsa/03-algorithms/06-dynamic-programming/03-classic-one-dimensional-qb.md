# Classic One-Dimensional DP — Question Bank

Micro-questions over [[03-classic-one-dimensional|the 1-D DP module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. House robber

**1. State the problem.**

<details><summary>Answer</summary>

Houses in a row, each with some money. **You cannot rob two adjacent houses.** Maximise the total.

</details>

**2. What question produces the state?**

<details><summary>Answer</summary>

**At house $i$, what are my options?** Rob it, or skip it. That is the entire problem.

</details>

**3. Give state, transition and base.**

<details><summary>Answer</summary>

**STATE:** `best[i]` = most money obtainable from houses $0..i$.
**TRANSITION:** `best[i] = max(best[i-1], best[i-2] + nums[i])`.
**BASE:** `best[0] = nums[0]`, `best[1] = max(nums[0], nums[1])`.

</details>

**4. Justify the transition in words.**

<details><summary>Answer</summary>

Skipping house $i$ leaves the best for $0..i-1$; robbing it adds `nums[i]` to the best for $0..i-2$, **since $i-1$ is now forbidden**.

</details>

**5. On `[2,7,9,3,1]`, `best[3] = 11`, unchanged from `best[2]`. What does that mean?**

<details><summary>Answer</summary>

House 3 holds 3, and robbing it would mean giving up house 2's 9. **A cell whose value equals its predecessor is the table telling you "skip" won** — and that observation is what makes reconstruction possible.

</details>

**6. Write the $O(1)$-space version.**

<details><summary>Answer</summary>

```python
prev2 = prev1 = 0
for x in nums:
    prev2, prev1 = prev1, max(prev1, prev2 + x)
return prev1
```

</details>

**7. What does that version handle for free?**

<details><summary>Answer</summary>

**The empty list and the single-element list**, which the array version needs explicit guards for — a small illustration that **space optimisation occasionally simplifies rather than complicates**.

</details>

---

## B. Coin change

**8. State the problem.**

<details><summary>Answer</summary>

Coins of given denominations, unlimited supply. Make an exact amount with the **fewest** coins, or report impossibility.

</details>

**9. What is the decision at amount $a$?**

<details><summary>Answer</summary>

**Which coin do I use last?** You do not know, **so you try all of them**.

</details>

**10. Give state, transition and base.**

<details><summary>Answer</summary>

**STATE:** `best[a]` = fewest coins summing to exactly $a$.
**TRANSITION:** `best[a] = 1 + min(best[a - c])` over every coin $c \le a$.
**BASE:** `best[0] = 0`; everything else starts at **infinity**.

</details>

**11. Why does the infinity sentinel matter?**

<details><summary>Answer</summary>

For coins $\{2,5\}$ and amount 3, no combination works and `best[3]` stays infinite — **which is how the algorithm reports impossibility rather than returning a wrong small number.**

</details>

**12. What must you never initialise it to?**

<details><summary>Answer</summary>

**Zero.** Use a real infinity, or a value provably larger than any valid answer (`amount + 1` works).

</details>

**13. How do you recover which coins, not just how many?**

<details><summary>Answer</summary>

**Record the decision alongside each cell** — `choice[a] = c` when the cell improves — then walk backwards from `amount`, subtracting each recorded coin.

</details>

**14. How general is that pattern?**

<details><summary>Answer</summary>

**Store the decision, walk it backwards** — it is how *every* DP recovers a solution rather than a value, and it costs one array and no extra time.

</details>

**15. What is the complexity, and what is the catch?**

<details><summary>Answer</summary>

$O(n \cdot c)$ for amount $n$ and $c$ coins — but it is **pseudo-polynomial**: linear in the *value* of the amount, not its digit count. **An amount of $10^9$ is infeasible even though it is a small input to type.**

</details>

---

## C. Longest increasing subsequence

**16. The obvious state is "`lis[i]` = longest increasing subsequence within `nums[0..i]`". What goes wrong?**

<details><summary>Answer</summary>

**You cannot write the transition.** To decide whether `nums[i]` extends the best subsequence in $0..i-1$, you need to know **what that subsequence's last element was** — and the state does not record it.

</details>

**17. State the diagnosis precisely.**

<details><summary>Answer</summary>

**The state is not wrong because it is imprecise. It is wrong because it is not enough information to compute the next state from.** That is the general test for a candidate state — **the single most transferable idea in this folder.**

</details>

**18. Give the fixed state, transition, base and answer.**

<details><summary>Answer</summary>

**STATE:** `lis[i]` = longest increasing subsequence **ending exactly at index $i$**.
**TRANSITION:** `lis[i] = 1 + max(lis[j])` over $j < i$ with `nums[j] < nums[i]`; else 1.
**BASE:** every `lis[i]` starts at 1.
**ANSWER:** `max(lis)`, **not** `lis[n-1]`.

</details>

**19. Why is the answer `max(lis)`?**

<details><summary>Answer</summary>

**Because the state pins the ending position, no single cell holds the global answer** — you scan for it. That is a recurring consequence of pinning something in the state, and forgetting it is a common bug.

</details>

**20. What is the complexity?**

<details><summary>Answer</summary>

$n$ states × $O(n)$ transition = $O(n^2)$.

</details>

---

## D. The $O(n\log n)$ version

**21. What is `tails[k]`?**

<details><summary>Answer</summary>

The **smallest possible tail value** of any increasing subsequence of length $k+1$. For each element, binary-search its position and overwrite; the answer is `len(tails)`.

</details>

**22. On `[10,9,2,5,3,7,101,18]` the tails array is `[2,3,7,18]`. Is that the LIS?**

<details><summary>Answer</summary>

**No.** `3` appears before `5` in the LIS but after it in the array, and `18` comes after `101`. **Only the *length* of `tails` is meaningful.**

</details>

**23. What do you need to recover the actual subsequence?**

<details><summary>Answer</summary>

**An extra predecessor array.** The $O(n^2)$ DP gives it directly.

</details>

**24. State the general lesson.**

<details><summary>Answer</summary>

**An asymptotically better algorithm is not automatically the one to use.** If you need the subsequence and $n$ is small, the $O(n^2)$ DP is simpler and gives you more.

</details>

---

## E. The shared pattern

**25. Give the state and transition for all four 1-D problems.**

<details><summary>Answer</summary>

| Problem | State | Transition |
| :--- | :--- | :--- |
| Climbing stairs | ways to reach step $i$ | $w[i] = w[i-1]+w[i-2]$ |
| House robber | best from houses $0..i$ | $b[i] = \max(b[i-1], b[i-2]+v_i)$ |
| Coin change | fewest coins for $a$ | $c[a] = 1 + \min(c[a-\text{coin}])$ |
| LIS | longest ending **at** $i$ | $l[i] = 1 + \max(l[j]),\ j<i$ |

</details>

**26. What is every one of them?**

<details><summary>Answer</summary>

**Define what one cell means, then build it from cells with a smaller index.** The differences are only in what "smaller" means and how many earlier cells the transition consults — two for stairs, all of them for LIS.

</details>

**27. State the question that generates the state every time.**

<details><summary>Answer</summary>

**"What decision do I make at index $i$, and what do I need to know to make it?"**

</details>

**28. Apply it to all three.**

<details><summary>Answer</summary>

**House robber:** rob or skip, and you need the best totals two steps back. **Coin change:** which coin last, and you need every smaller amount. **LIS:** extend or start fresh, and you need the last element — **which is why it goes into the state**.

</details>

---

## F. Traps

**29. How do you test a candidate state?**

<details><summary>Answer</summary>

**Try to write the transition.** If you need a fact the state does not record, the state is wrong.

</details>

**30. What is the house robber base-case off-by-one?**

<details><summary>Answer</summary>

`best[1] = max(nums[0], nums[1])`, **not `nums[1]`** — with one house you take it, with two you take the better. The rolling version sidesteps this by starting both accumulators at 0.

</details>

**31. What can two variables never tell you?**

<details><summary>Answer</summary>

**Which houses were robbed.** Do not space-optimise before you know whether you need the solution.

</details>

**32. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Ask what decision you make at index $i$ and what you need to know to make it — that answer *is* the state, and if you cannot write the transition from it, you have the wrong one.

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

- [[03-classic-one-dimensional|Classic One-Dimensional DP]] — the module
- [[02-memoisation-and-tabulation-qb|Memoisation & Tabulation — Question Bank]]
- [[04-classic-two-dimensional-qb|Classic Two-Dimensional DP — Question Bank]]
