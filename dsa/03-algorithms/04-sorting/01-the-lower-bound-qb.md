# The Sorting Lower Bound — Question Bank

Micro-questions over [[01-the-lower-bound|the lower bound module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why six algorithms

**1. Sorting is solved. Why does it need six algorithms?**

<details><summary>Answer</summary>

Because **"sorted" is not the only requirement** — you may need stability, no spare memory, adaptivity on almost-sorted input, or keys of a special kind. **The constraints conflict**, so there is no single winner.

</details>

**2. What rare kind of result does this lesson contain?**

<details><summary>Answer</summary>

**A proof about every possible algorithm**, not just the ones we have thought of.

</details>

---

## B. The vocabulary

**3. What is a comparison sort?**

<details><summary>Answer</summary>

One that decides order **only by comparing pairs**. It is the kind the lower bound applies to.

</details>

**4. What does stable mean?**

<details><summary>Answer</summary>

Equal elements keep their **original relative order**.

</details>

**5. Give the concrete reason stability matters.**

<details><summary>Answer</summary>

Sort employees by name, then by department. **If the second sort is stable, people stay alphabetical within each department. If it is not, the first sort was wasted.**

</details>

**6. Which standard library sorts are stable?**

<details><summary>Answer</summary>

Python's `sorted()` and Java's `Arrays.sort` for objects. It is **the single most-overlooked property**.

</details>

**7. What does in-place mean here?**

<details><summary>Answer</summary>

Uses $O(1)$ or $O(\log n)$ extra space. It matters when data barely fits.

</details>

**8. What does adaptive mean, and why does it matter?**

<details><summary>Answer</summary>

Faster on partly-sorted input — and **real data is often partly sorted**.

</details>

**9. Internal versus external?**

<details><summary>Answer</summary>

Fits in memory versus does not. **External sorting is a different problem.**

</details>

---

## C. The proof

**10. State the claim.**

<details><summary>Answer</summary>

Any comparison-based sorting algorithm needs $\Omega(n\log n)$ comparisons **in the worst case**.

</details>

**11. What is a decision tree here?**

<details><summary>Answer</summary>

Each internal node is **one comparison**, with two branches for the two outcomes; **each leaf is a final ordering** the algorithm can output.

</details>

**12. Give the three steps of the proof.**

<details><summary>Answer</summary>

1. To be correct, the algorithm must produce **every** one of the $n!$ permutations, so the tree has at least $n!$ leaves.
2. A binary tree of height $h$ has at most $2^h$ leaves.
3. So $2^h \ge n!$, giving $h \ge \log_2(n!)$.

</details>

**13. Finish it.**

<details><summary>Answer</summary>

By Stirling's approximation, $\log_2(n!) = \Theta(n\log n)$. And $h$ **is** the worst-case number of comparisons — the longest root-to-leaf path. $\blacksquare$

</details>

**14. What did the proof not assume?**

<details><summary>Answer</summary>

**Nothing about the strategy, the data structure, or the cleverness.** It applies to every comparison sort that exists or ever will.

</details>

**15. How close is merge sort to the bound?**

<details><summary>Answer</summary>

**Essentially optimal** — its actual comparison count tracks $\log_2(n!)$ closely.

</details>

**16. Counting sort runs in $O(n + k)$, beating $n\log n$. Does that disprove the theorem?**

<details><summary>Answer</summary>

**No.** Counting sort is not a comparison sort — it **reads the keys themselves** rather than comparing pairs, so the bound does not apply to it.

</details>

---

## D. The map

**17. Give best/average/worst, space, stable and adaptive for the three elementary sorts.**

<details><summary>Answer</summary>

| | Best | Avg | Worst | Space | Stable | Adaptive |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| Bubble | $n$ | $n^2$ | $n^2$ | 1 | ✅ | ✅ |
| Selection | $n^2$ | $n^2$ | $n^2$ | 1 | ❌ | ❌ |
| Insertion | $n$ | $n^2$ | $n^2$ | 1 | ✅ | ✅ |

</details>

**18. Same for the three $n\log n$ sorts.**

<details><summary>Answer</summary>

| | Best | Avg | Worst | Space | Stable |
| :--- | :--- | :--- | :--- | :--- | :---: |
| Merge | $n\log n$ | $n\log n$ | $n\log n$ | $n$ | ✅ |
| Quick | $n\log n$ | $n\log n$ | **$n^2$** | $\log n$ | ❌ |
| Heap | $n\log n$ | $n\log n$ | $n\log n$ | **1** | ❌ |

</details>

**19. Same for the non-comparison sorts.**

<details><summary>Answer</summary>

Counting: $n+k$ throughout, space $n+k$, stable. Radix: $nd$ throughout, space $n+k$, stable.

</details>

**20. Why is selection sort $n^2$ even in the best case?**

<details><summary>Answer</summary>

It **always scans the whole remaining array** to find the minimum, regardless of how sorted the input already is. It has no early exit to take.

</details>

---

## E. What real libraries do

**21. What is Timsort?**

<details><summary>Answer</summary>

Python's sort — **merge sort exploiting existing runs, falling back to insertion sort on small pieces**. Stable and adaptive.

</details>

**22. What is introsort?**

<details><summary>Answer</summary>

C++'s `std::sort` — **quicksort, switching to heapsort when recursion goes too deep**, so the $n^2$ worst case cannot happen.

</details>

**23. Why do both hybrids exist?**

<details><summary>Answer</summary>

For the same two reasons: **insertion sort has the smallest constant on tiny inputs**, and **quicksort's worst case must be prevented rather than hoped against**.

</details>

---

## F. Traps

**24. Is quicksort always fastest?**

<details><summary>Answer</summary>

It has the best constants in practice **and an $O(n^2)$ worst case**. Library implementations guard against it rather than trusting it.

</details>

**25. Why is $O(n\log n)$ not automatically "fast enough"?**

<details><summary>Answer</summary>

For $n = 10^9$ it is $3\times10^{10}$ comparisons. **Sorting is often the thing to avoid** — via a hash map or a heap.

</details>

**26. You need the $k$th largest element. What should you not do?**

<details><summary>Answer</summary>

**Sort first.** That is $O(n\log n)$; quickselect is $O(n)$ and a heap is $O(n\log k)$. Finding the plain maximum is $O(n)$.

</details>

**27. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

Comparison sorting cannot beat $n\log n$ because it must distinguish $n!$ outcomes with binary questions — and everything else about choosing a sort is stability, space and adaptivity, not speed.

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

- [[01-the-lower-bound|The Lower Bound]] — the module
- [[02-elementary-sorts-qb|Elementary Sorts — Question Bank]]
- [[05-non-comparison-sorts-qb|Non-Comparison Sorts — Question Bank]] — what escapes the bound
