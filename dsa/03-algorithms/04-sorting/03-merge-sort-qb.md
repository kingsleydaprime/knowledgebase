# Merge Sort — Question Bank

Micro-questions over [[03-merge-sort|the merge sort module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The insight

**1. Why are the elementary sorts quadratic, and how does merge sort attack that?**

<details><summary>Answer</summary>

Because each element is compared against many others. Merge sort **splits**: sort two halves independently, then combine them.

</details>

**2. Why is merging two sorted lists linear?**

<details><summary>Answer</summary>

Walk both with one pointer each, always taking the smaller head. **No element is ever compared twice against the same one, because progress is made on every comparison.**

</details>

**3. What guarantee does merge sort provide that no other common sort does?**

<details><summary>Answer</summary>

$O(n\log n)$ in the **worst** case, not just on average. Quicksort is usually faster in practice and can degrade to $O(n^2)$; **merge sort cannot**.

</details>

---

## B. The cost

**4. How much work does each level of the tree do?**

<details><summary>Answer</summary>

$O(n)$ — **every element is touched once per level** during merging.

</details>

**5. How many levels, and why?**

<details><summary>Answer</summary>

$\log_2 n$, because the size halves each time.

</details>

**6. Why does the bound hold for *every* input?**

<details><summary>Answer</summary>

**Because the split is by position, not by value.** Nothing about the data can unbalance it.

</details>

**7. What does that last point separate it from?**

<details><summary>Answer</summary>

**Quicksort**, whose split depends on the data and can therefore be unbalanced.

</details>

---

## C. Stability

**8. What single character makes merge sort stable?**

<details><summary>Answer</summary>

The `=` in `if left[i] <= right[j]` — **when the heads are equal, take from the left**.

</details>

**9. Why does taking from the left preserve order?**

<details><summary>Answer</summary>

**The left half came first in the original array**, so preferring it keeps the original relative order of equal elements.

</details>

**10. What happens with `<` instead?**

<details><summary>Answer</summary>

The sort becomes **unstable** — a one-character difference with a real consequence.

</details>

---

## D. External merge sort

**11. 100 GB to sort, 8 GB of RAM. Why does merge sort apply where others do not?**

<details><summary>Answer</summary>

**Because merging reads sequentially.**

</details>

**12. Describe the two phases.**

<details><summary>Answer</summary>

1. Read as much as fits, sort it in memory, write it out as a sorted **run**. Repeat — about 13 runs for 100 GB at 8 GB each.
2. Open all runs at once and do a **$k$-way merge**, repeatedly taking the smallest head across all runs.

</details>

**13. What structure makes each merge step efficient, and at what cost?**

<details><summary>Answer</summary>

A [[dsa/02-data-structures/08-heaps|min-heap]] over the run heads — $O(\log k)$ per step.

</details>

**14. Why does sequential access matter so much here?**

<details><summary>Answer</summary>

**Sequential disk reads are orders of magnitude faster than random ones** — which is exactly why quicksort, which jumps around during partitioning, is not used.

</details>

**15. Where does this actually run?**

<details><summary>Answer</summary>

A database doing a large `ORDER BY` that cannot use an index, and `sort(1)` on a large file.

</details>

---

## E. Traps

**16. If you allocate a fresh temporary inside every recursive call, does the asymptotic complexity change? Does the running time?**

<details><summary>Answer</summary>

**Complexity: no. Running time: yes, substantially.** It makes the constant much worse and stresses the allocator. Real implementations allocate **one buffer of size $n$ up front**.

</details>

**17. What is the tail copy, and what happens if you forget it?**

<details><summary>Answer</summary>

When one side is exhausted, **the rest of the other must still be appended**. Omitting it silently drops elements.

</details>

**18. Is merge sort in-place?**

<details><summary>Answer</summary>

No — it needs $O(n)$ extra. In-place variants exist and are **markedly slower and much more complex**.

</details>

**19. When should you not use it?**

<details><summary>Answer</summary>

Below about 16 elements, where insertion sort wins on constants. **Timsort switches for exactly this reason.**

</details>

**20. What changes on a linked list?**

<details><summary>Answer</summary>

Merge sort **is effectively in-place** — you relink nodes instead of copying — which makes it **the standard choice there**.

</details>

**21. Summarise merge sort in one sentence.**

<details><summary>Answer</summary>

Split by position so nothing can unbalance it, merge linearly taking from the left on ties — guaranteed $O(n\log n)$, stable, $O(n)$ extra space, and the only one that works off disk.

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

- [[03-merge-sort|Merge Sort]] — the module
- [[04-quicksort-qb|Quicksort — Question Bank]] — the faster, riskier one
- [[02-elementary-sorts-qb|Elementary Sorts — Question Bank]] — what it falls back to
