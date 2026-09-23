# What Makes a Problem DP — Question Bank

Micro-questions over [[01-what-makes-a-problem-dp|the DP recognition module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. State dynamic programming in one sentence.**

<details><summary>Answer</summary>

**Recognise that a recursion is recomputing, and stop it.**

</details>

**2. Where is the actual skill?**

<details><summary>Answer</summary>

**The technique is trivial once you see it. The skill is deciding whether it applies** — and for that there are exactly two questions.

</details>

**3. Why is the name unhelpful?**

<details><summary>Answer</summary>

Bellman chose it in the 1950s partly because it sounded impressive to a research sponsor. **It means neither "dynamic" nor "programming".** Read it as **"careful recursion with a cache"**.

</details>

---

## B. The vocabulary

**4. What is a subproblem, and what act is identifying one?**

<details><summary>Answer</summary>

A smaller instance of the same problem. **Identifying what counts as a subproblem is the same act as choosing the state.**

</details>

**5. What are overlapping subproblems, and what is notable about the property?**

<details><summary>Answer</summary>

The recursion solves the *same* subproblem more than once. **It is measurable** — count total calls and distinct arguments and compare.

</details>

**6. What is optimal substructure?**

<details><summary>Answer</summary>

An optimal solution to the whole is built out of optimal solutions to its subproblems. **Without it, caching sub-answers is useless because they cannot legitimately be combined.**

</details>

**7. Memoisation versus tabulation?**

<details><summary>Answer</summary>

**Memoisation** caches results as the recursion runs — top-down, shape unchanged, you add a dictionary. **Tabulation** fills a table in a deliberate order with loops — bottom-up, no recursion.

</details>

**8. What is the state space, and what does it give you?**

<details><summary>Answer</summary>

The set of distinct subproblems. **Its size times the cost of one transition is the complexity of the DP** — which is how you predict the cost before writing anything.

</details>

---

## C. Measuring overlap

**9. What should you do instead of guessing?**

<details><summary>Answer</summary>

**Instrument the recursion, count total calls and distinct arguments, and divide.**

</details>

**10. What is `fib(30)`'s redundancy?**

<details><summary>Answer</summary>

2,692,537 calls over 31 distinct subproblems — **86,856×**.

</details>

**11. What is merge sort's redundancy, and why?**

<details><summary>Answer</summary>

**Exactly 1.0** — every recursive call receives a different slice, so no subproblem is ever repeated.

</details>

**12. What follows about memoising merge sort?**

<details><summary>Answer</summary>

**It would add hashing and storage and save nothing.** That is why merge sort is divide and conquer, not DP, despite both being recursive.

</details>

**13. State the overlap test.**

<details><summary>Answer</summary>

**If distinct subproblems $\ll$ total calls, you have overlap**, and memoisation collapses the exponential tree into a linear or polynomial walk over the state space.

</details>

---

## D. Optimal substructure

**14. Why does shortest path have it?**

<details><summary>Answer</summary>

**Every subpath of a shortest path is itself a shortest path** — if it were not, you could substitute the better subpath and improve the whole, contradicting optimality.

</details>

**15. What does that property enable?**

<details><summary>Answer</summary>

It is **precisely what lets Dijkstra and Floyd–Warshall compose sub-answers.**

</details>

**16. Show that longest *simple* path lacks it.**

<details><summary>Answer</summary>

On the lab's graph: longest A→D = 3, longest A→B = 3, longest B→D = 3. Composing gives 6, but the true longest A→D is 3 — **the composed walk repeats a vertex.**

</details>

**17. State the failure precisely.**

<details><summary>Answer</summary>

**The sub-answers are each optimal and mutually incompatible.** The best A→B uses up C and D; the best B→D needs them again. So no DP formulation exists — and longest simple path is NP-hard.

</details>

**18. State the test for optimal substructure.**

<details><summary>Answer</summary>

**Take an optimal solution and cut it in half. Is each half optimal *for the subproblem it solves*?** If forcing a half to be optimal can make the whole worse, you do not have it.

</details>

---

## E. Greedy versus DP

**19. Coins $\{1,3,4\}$, amount 6. What does greedy give, and what is optimal?**

<details><summary>Answer</summary>

Greedy: $4 + 1 + 1$ = **three coins**. Optimal: $3 + 3$ = **two**.

</details>

**20. Does that mean coin change lacks optimal substructure?**

<details><summary>Answer</summary>

**No.** If the optimal solution for 6 uses coin $c$, the rest is an optimal solution for $6-c$ — and it is: the 2-coin solution uses a 3, and $\{3\}$ is optimal for amount 3.

</details>

**21. What does greedy assume that is stronger and false?**

<details><summary>Answer</summary>

**That you can determine *which* coin to use by a local rule, without solving the subproblems.** Optimal substructure says the sub-answers compose; it does not say which sub-answer to compose with.

</details>

**22. State the difference in one line.**

<details><summary>Answer</summary>

**DP tries every coin and lets the table decide; greedy guesses and commits.**

</details>

**23. Greedy is right for US coins and wrong for $\{1,3,4\}$. What follows?**

<details><summary>Answer</summary>

**Nothing about the problem statement tells you which case you are in — which is why "greedy feels right" is not an argument.**

</details>

---

## F. The grid

**24. Give the four-cell grid.**

<details><summary>Answer</summary>

| Overlapping? | Optimal substructure? | Technique |
| :--- | :--- | :--- |
| no | yes | divide and conquer |
| **yes** | **yes** | **dynamic programming** |
| yes | no | no efficient method known (NP-hard) |
| no | no | brute force / backtracking |

</details>

**25. What is the fifth case?**

<details><summary>Answer</summary>

Inside row two: **when a *local* rule provably picks the right subproblem**, skip the table and use a greedy algorithm — faster, but it needs **a proof, not a feeling**.

</details>

---

## G. Traps

**26. What if the state space is exponential?**

<details><summary>Answer</summary>

**Memoising an exponential recursion gives you an exponential DP.** Caching does not create efficiency; it only removes redundancy.

</details>

**27. What is the "sounds similar" trap?**

<details><summary>Answer</summary>

Assuming optimal substructure by analogy. **Shortest path has it; longest simple path does not, and they differ by one word.**

</details>

**28. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

Measure the redundancy and check that optimal halves compose — overlap plus optimal substructure is DP, overlap alone is nothing, and substructure alone is divide and conquer.

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

- [[01-what-makes-a-problem-dp|What Makes a Problem DP]] — the module
- [[02-memoisation-and-tabulation-qb|Memoisation & Tabulation — Question Bank]] — the next bank
- [[../10-greedy-algorithms/01-when-greedy-works|When Greedy Works]] — the fifth case
