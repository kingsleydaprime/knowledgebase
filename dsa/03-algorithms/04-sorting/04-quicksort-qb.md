# Quicksort — Question Bank

Micro-questions over [[04-quicksort|the quicksort module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. Compare quicksort with merge sort on memory.**

<details><summary>Answer</summary>

Merge sort needs $O(n)$ extra; quicksort needs only $O(\log n)$ of stack.

</details>

**2. Why is quicksort faster in practice despite a similar comparison count?**

<details><summary>Answer</summary>

**The reason is memory, not operation count.** Partitioning sweeps **sequentially** and swaps in place — friendly to caches and prefetchers. Merge sort copies into and out of a separate buffer, doubling memory traffic. **Constants win.**

</details>

**3. What is the price?**

<details><summary>Answer</summary>

**A genuine worst case.** Merge sort's split is by position and cannot be unbalanced; quicksort's split is by **value**, so an unlucky input makes every partition lopsided — $O(n^2)$.

</details>

---

## B. Partitioning

**4. What does partitioning do?**

<details><summary>Answer</summary>

Choose a **pivot**; rearrange so everything smaller is left of it and everything larger is right. **The pivot is now in its final position.** Recurse on both sides.

</details>

**5. Describe Lomuto partitioning.**

<details><summary>Answer</summary>

Pivot is the last element. Walk with `j`, keeping `i` as the boundary of the "smaller" region; swap into place whenever `a[j] <= pivot`. Finally swap the pivot to `i+1`.

</details>

**6. Where does Lomuto degrade badly, and why?**

<details><summary>Answer</summary>

On arrays of **equal elements** — every element satisfies `<= pivot`, so every partition is maximally lopsided and **the sort goes quadratic on input that is already trivially sorted**.

</details>

**7. Describe Hoare partitioning and its advantages.**

<details><summary>Answer</summary>

Two pointers move towards each other, swapping out-of-place pairs. It does about **three times fewer swaps** on average and handles duplicates far better, because elements equal to the pivot can end up on **either** side, which keeps partitions balanced.

</details>

**8. Why is Lomuto taught first?**

<details><summary>Answer</summary>

Only because Hoare's index handling is fiddlier.

</details>

---

## C. The worst case

**9. What quantity actually decides the complexity?**

<details><summary>Answer</summary>

**The recursion depth.** Balanced splits give depth $\log_2 n$ and $O(n\log n)$; maximally lopsided splits give depth $n$ and $O(n^2)$.

</details>

**10. With a last-element pivot, what is the worst case?**

<details><summary>Answer</summary>

**Already-sorted input** — the pivot is always the maximum, so one side gets everything.

</details>

**11. Why is that damning rather than a curiosity?**

<details><summary>Answer</summary>

**It is not a rare adversarial input; it is the most common input shape there is.**

</details>

**12. Give the five fixes and what each does.**

<details><summary>Answer</summary>

| Fix | What it does |
| :--- | :--- |
| Median-of-three | pivot on median of first/middle/last — kills sorted input cheaply |
| Randomised pivot | no fixed input is worst-case; an adversary cannot predict it |
| Introsort | past depth $2\log n$, switch to **heapsort** — a hard $O(n\log n)$ ceiling |
| Three-way partition | split into `< = >`; makes duplicate-heavy arrays linear |
| Insertion sort below ~16 | better constants on small partitions |

</details>

**13. What is `std::sort`?**

<details><summary>Answer</summary>

**Introsort with all five.** That is why the standard library never exhibits the worst case even though the underlying algorithm has one.

</details>

**14. Rank these three for a last-element pivot: random, reverse-sorted, all-identical.**

<details><summary>Answer</summary>

Random is fine ($n\log n$). Reverse-sorted is $O(n^2)$ — the pivot is always the minimum. **All-identical is also $O(n^2)$ under Lomuto** and is the case people forget, because the array is already "sorted".

</details>

---

## D. Stability

**15. Why is quicksort not stable?**

<details><summary>Answer</summary>

**Partitioning swaps elements across long distances.** Two equal elements can be exchanged or jumped past one another, and their original order is lost.

</details>

**16. Why do libraries not just fix it?**

<details><summary>Answer</summary>

Making it stable requires extra space, **which surrenders quicksort's main advantage**.

</details>

**17. What do libraries offer instead?**

<details><summary>Answer</summary>

A choice: `sort` (quicksort-family, unstable, fast) and `stable_sort` (merge-family, stable, $O(n)$ memory). **Python's `list.sort` is Timsort and always stable — a deliberate different trade.**

</details>

---

## E. Traps

**18. What is the Hoare off-by-one?**

<details><summary>Answer</summary>

Hoare returns `j` and you recurse on `[lo, j]` and `[j+1, hi]` — **not `[lo, j-1]`**. Getting it wrong causes infinite recursion.

</details>

**19. How do you cap the stack depth at $O(\log n)$?**

<details><summary>Answer</summary>

**Recurse into the smaller side and loop on the larger.** The recursed side at most halves each time.

</details>

**20. Does randomisation make the worst case impossible?**

<details><summary>Answer</summary>

No — **it makes it improbable and input-independent.** It is still reachable, just not by an adversary choosing the input.

</details>

**21. Summarise quicksort in one sentence.**

<details><summary>Answer</summary>

Partition in place around a pivot and recurse — the fastest in practice because it stays in cache, and safe only because libraries median-of-three it, randomise it, and cap its depth with heapsort.

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

- [[04-quicksort|Quicksort]] — the module
- [[03-merge-sort-qb|Merge Sort — Question Bank]] — the guaranteed alternative
- [[dsa/02-data-structures/08-heaps-qb|Heaps — Question Bank]] — introsort's fallback
