# Memoisation & Tabulation — Question Bank

Micro-questions over [[02-memoisation-and-tabulation|the memoisation and tabulation module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The three declarations

**1. What are the three things every dynamic program must name?**

<details><summary>Answer</summary>

1. **STATE** — what one cell of the table *means*, written as a sentence.
2. **TRANSITION** — how a cell is computed from cells with smaller indices. The recurrence.
3. **BASE CASE** — the cells filled directly, because nothing smaller builds them.

</details>

**2. Give all three for climbing stairs.**

<details><summary>Answer</summary>

**STATE:** `ways[i]` = the number of distinct ways to reach step $i$.
**TRANSITION:** `ways[i] = ways[i-1] + ways[i-2]` — you arrived from $i-1$ with a 1-step or from $i-2$ with a 2-step, and those are disjoint.
**BASE:** `ways[0] = 1`, `ways[1] = 1`.

</details>

**3. When should you write those three lines?**

<details><summary>Answer</summary>

**Before writing any code.** They are the design; everything after is transcription.

</details>

**4. What makes the state the hard one?**

<details><summary>Answer</summary>

**Making it a complete sentence.** "`dp[i]` is about index `i`" is not a state; "`dp[i]` is the number of ways to reach step `i`" is. **If you cannot finish the sentence, you do not yet have a DP.**

</details>

---

## B. The vocabulary

**5. What is the state space, and what is it the first factor in?**

<details><summary>Answer</summary>

The set of all subproblems. **Its size is the first factor in the complexity.**

</details>

**6. What is the transition's role in the complexity?**

<details><summary>Answer</summary>

**Its cost is the second factor** — complexity is states × transition.

</details>

**7. What dictates the fill order?**

<details><summary>Answer</summary>

**The transition.** Every cell a transition reads must already hold its final value.

</details>

**8. What is a rolling array?**

<details><summary>Answer</summary>

Space optimisation — keeping only the last row (or last few cells) of a table, when the transition never reaches further back.

</details>

**9. What is reconstruction?**

<details><summary>Answer</summary>

Recovering the actual solution — the path, subset or string — rather than just its value, usually by **walking the table backwards from the answer cell**.

</details>

---

## C. Filling the table

**10. What single requirement fixes the fill order?**

<details><summary>Answer</summary>

**Every new cell reads only cells already filled.** That is the whole of what "bottom-up" means.

</details>

**11. Climbing stairs produces Fibonacci numbers. Coincidence?**

<details><summary>Answer</summary>

**No — the recurrence is identical.** Climbing stairs *is* Fibonacci with different base cases, which matters because **the same table shape solves problems that sound unrelated**.

</details>

---

## D. Four implementations

**12. Compare operation counts at $n = 30$.**

<details><summary>Answer</summary>

Naive 2,692,537; memoised 59; tabulated 29; rolling 29. **Naive is exponential; the other three are linear.**

</details>

**13. Why is memoisation's count about $2n$ and tabulation's about $n$?**

<details><summary>Answer</summary>

**Each state is entered once as a miss and once as a hit** under memoisation; tabulation has no lookups at all.

</details>

**14. What is notable about the memoised code?**

<details><summary>Answer</summary>

**The recursion is unchanged from the naive version** — three lines were added. That is why memoisation is the right first move: **you write the recurrence exactly as you reasoned about it, then cache.**

</details>

**15. Why `memo=None` rather than `memo={}`?**

<details><summary>Answer</summary>

A mutable default **shares one dictionary across every call for the lifetime of the process**, including calls from unrelated code.

</details>

---

## E. Which one to use

**16. Give the six-row comparison.**

<details><summary>Answer</summary>

| | Memoisation | Tabulation |
| :--- | :--- | :--- |
| Write it as | the recurrence, directly | a loop |
| Computes | only states **needed** | **every** state |
| Fill order | the call stack handles it | **you** choose it |
| Depth limit | ~1,000 frames | none |
| Space optimisation | awkward | easy |
| Debugging | print on cache miss | print the table |

</details>

**17. What happens to memoised vs tabulated at $n = 50{,}000$?**

<details><summary>Answer</summary>

Memoised raises `RecursionError` — **the recursion depth, not the cache**. Tabulated is fine, because it is a loop.

</details>

**18. State the rule for choosing.**

<details><summary>Answer</summary>

**Sparse state space** — you need only a small fraction of reachable states — **memoise**, because tabulation would compute all of them. **Dense**, or deeper than ~1,000 — **tabulate**.

</details>

**19. What is the practical order of work?**

<details><summary>Answer</summary>

**Write the memoised version first** — it is the recurrence you already reasoned about and it is hard to get the order wrong. **Convert to tabulation only if you need the depth or the space optimisation.**

</details>

---

## F. Fill order

**20. Tabulate climbing stairs right-to-left. Right answer, wrong answer, or error?**

<details><summary>Answer</summary>

**A wrong answer, silently — 0.**

</details>

**21. Why exactly?**

<details><summary>Answer</summary>

It computes `ways[n]` first, which reads `ways[n-1]` and `ways[n-2]` — **both still zero, because they have not been computed**. The zeros propagate. **No exception, no warning.**

</details>

**22. State the rule that generates the order for every DP.**

<details><summary>Answer</summary>

**The transition dictates the order — every cell a transition reads must already be final.** Read your recurrence, note which indices it reads, choose the loop direction that guarantees those come first.

</details>

**23. What does memoisation handle automatically here?**

<details><summary>Answer</summary>

**The call stack cannot get the order wrong**, because it computes a dependency at the moment it is needed.

</details>

---

## G. Cutting the memory

**24. Where do most DP tutorials stop, and what is the step after?**

<details><summary>Answer</summary>

They stop at a working table. **The step after is noticing how little of it you still need.**

</details>

**25. Reduce climbing stairs to $O(1)$ space. Why is it possible?**

<details><summary>Answer</summary>

It reads only `ways[i-1]` and `ways[i-2]` — **never anything further back** — so two variables suffice:

```python
prev2, prev1 = 1, 1
for _ in range(2, n + 1):
    prev2, prev1 = prev1, prev1 + prev2
```

</details>

**26. Apply the same move to unique grid paths.**

<details><summary>Answer</summary>

`table[i][j] = table[i-1][j] + table[i][j-1]` reads **the row above and the cell to the left, never anything higher** — so **one row suffices**, giving $O(c)$ instead of $O(rc)$.

</details>

---

## H. Traps

**27. What is the most common failed-DP symptom?**

<details><summary>Answer</summary>

**A state you cannot write as a sentence.** It presents as a transition that "almost works".

</details>

**28. When is tabulation actively wasteful?**

<details><summary>Answer</summary>

**When the state space is sparse.** If only 200 of $10^6$ states are reachable, tabulation does 5,000× the necessary work.

</details>

**29. When should you optimise space, and why not before?**

<details><summary>Answer</summary>

**After the DP is correct.** The rolling array is harder to debug **and destroys reconstruction**.

</details>

**30. What are mutually exclusive?**

<details><summary>Answer</summary>

**Space optimisation and reconstruction.** Decide which you need before choosing.

</details>

**31. What must you count first, and why?**

<details><summary>Answer</summary>

**The state space.** Complexity is states × transition cost — **if that product is too big, no implementation detail rescues it; you need a different state.**

</details>

**32. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

Name the state as a sentence, write the transition, fill in the order the transition demands — memoise first, tabulate when you need depth or space.

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

- [[02-memoisation-and-tabulation|Memoisation & Tabulation]] — the module
- [[01-what-makes-a-problem-dp-qb|What Makes a Problem DP — Question Bank]]
- [[03-classic-one-dimensional-qb|Classic 1-D DP — Question Bank]]
