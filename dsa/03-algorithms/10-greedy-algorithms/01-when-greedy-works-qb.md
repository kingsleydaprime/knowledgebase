# When Greedy Works — Question Bank

Micro-questions over [[01-when-greedy-works|the greedy module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The failure mode

**1. Give the mountain trail illustration.**

<details><summary>Answer</summary>

Two branches: +150m, or +200m leading to −300m. Greedy takes +200 and ends at **−100m**; the optimal choice takes +150. **A locally attractive choice locks out a better long-term outcome.**

</details>

**2. Name two problems where greedy works and two where it fails.**

<details><summary>Answer</summary>

✅ **Activity selection** (take the job that finishes earliest) and **Huffman coding** (merge the two lowest-frequency nodes).
❌ **Coin change with arbitrary denominations** and **0/1 knapsack** (value-per-weight ignores capacity interactions).

</details>

---

## B. The vocabulary

**3. What is a greedy choice?**

<details><summary>Answer</summary>

The locally optimal decision made at each step **without reconsidering past choices**.

</details>

**4. What is an exchange argument?**

<details><summary>Answer</summary>

A proof showing that **swapping any greedy choice for any alternative can never improve the outcome**.

</details>

**5. Is a greedy algorithm a heuristic?**

<details><summary>Answer</summary>

**No.** A greedy algorithm is an **exact** algorithm producing the globally optimal answer *when applicable* — not an approximation.

</details>

**6. What property do both greedy and DP require?**

<details><summary>Answer</summary>

**Optimal substructure** — an optimal solution composed of optimal solutions to subproblems.

</details>

---

## C. The coin change trap

**7. Coins $\{1,2,5\}$, amount 11 — does greedy work?**

<details><summary>Answer</summary>

Yes: $5+5+1$ = 3 coins, which is optimal.

</details>

**8. Coins $\{1,3,4\}$, amount 6 — what happens?**

<details><summary>Answer</summary>

Greedy takes 4 first, leaving 2, needing two 1s — **3 coins. Optimal is $3+3$ = 2.**

</details>

**9. State the failure precisely.**

<details><summary>Answer</summary>

**Taking 4 greedily closes off the $3+3$ path.** The locally largest coin blocks the globally best combination.

</details>

**10. What does that tell you about the problem statement?**

<details><summary>Answer</summary>

**Nothing in it distinguishes the two coin sets** — which is why greedy must be proved, not felt.

</details>

---

## D. A provably correct greedy

**11. State the canoe pairing problem.**

<details><summary>Answer</summary>

Pair $N$ people of known weights into canoes of maximum capacity $k$. **Minimise the number of canoes.**

</details>

**12. State the greedy strategy.**

<details><summary>Answer</summary>

**Always try to pair the heaviest remaining person with the lightest remaining person.** If they exceed capacity, the heaviest goes alone.

</details>

**13. Give the exchange argument.**

<details><summary>Answer</summary>

Consider the heaviest person $H$. **If $H$ can share with anyone, they can share with the lightest person $L$** — because if an optimal solution pairs $H$ with a heavier $X$, swapping $X$ and $L$ can only maintain or improve the result, since $L$ fits anywhere $X$ did.

</details>

**14. What does that licence you to do?**

<details><summary>Answer</summary>

**Commit to the greedy choice and reduce the problem to the remaining people** — which is exactly the inductive proof structure for correctness.

</details>

**15. What familiar pattern does the implementation use?**

<details><summary>Answer</summary>

**Two pointers** — left at the lightest, right at the heaviest, converging from both ends of the sorted array.

</details>

**16. Why does `right -= 1` happen unconditionally?**

<details><summary>Answer</summary>

**The heaviest person is always seated** — either paired with the lightest, or alone. Only the left pointer is conditional.

</details>

---

## E. Choosing

**17. Give the three-row decision guide.**

<details><summary>Answer</summary>

| Signal | Use |
| :--- | :--- |
| Locally best provably **never worse** (exchange argument holds) | **Greedy** — fastest when it applies |
| Choices interact — "best now" can block a better future | **Dynamic programming** |
| Small problem, need a correct baseline | **Brute force** |

</details>

**18. State the key test.**

<details><summary>Answer</summary>

**"Can I prove the greedy choice is at least as good as any alternative using an exchange argument?"** If yes, greedy is safe. If not, switch to DP.

</details>

**19. What is the typical complexity of a greedy algorithm?**

<details><summary>Answer</summary>

**$O(n\log n)$ time** — dominated by the sort that establishes the greedy criterion — and **$O(1)$ auxiliary space**, since no memo table is needed.

</details>

**20. What step do people most often miss?**

<details><summary>Answer</summary>

**The sort.** Most greedy algorithms require first sorting by the greedy criterion — finishing time, weight, cost-per-unit.

</details>

**21. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

Greedy is exact when an exchange argument shows the local choice is never worse — and without that proof it is just a guess that happens to work on your examples.

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

- [[01-when-greedy-works|When Greedy Works]] — the module
- [[02-selection-and-scheduling-qb|Selection & Scheduling — Question Bank]]
- [[../06-dynamic-programming/01-what-makes-a-problem-dp-qb|What Makes a Problem DP — Question Bank]]
