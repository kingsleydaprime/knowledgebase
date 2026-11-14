# Elementary Sorts — Question Bank

Micro-questions over [[02-elementary-sorts|the elementary sorts module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why learn three quadratic sorts

**1. Give the three reasons.**

<details><summary>Answer</summary>

1. They are the sorts you can **prove correct on paper in a minute**, using an invariant — a skill that transfers to harder algorithms.
2. They differ on properties that matter more than asymptotics on small inputs.
3. **Insertion sort is genuinely in production** — Timsort and introsort both fall back to it below about 16 elements.

</details>

**2. State the general point about constants.**

<details><summary>Answer</summary>

**Asymptotic notation deliberately discards constants. On small inputs the constants are the whole story.**

</details>

**3. What is an invariant?**

<details><summary>Answer</summary>

A statement **true before and after every iteration**. It is what makes a loop provably correct rather than plausibly correct.

</details>

---

## B. Selection sort

**4. State its invariant.**

<details><summary>Answer</summary>

After $i$ passes, the **first $i$ positions hold the $i$ smallest elements, in order**.

</details>

**5. Describe the mechanism.**

<details><summary>Answer</summary>

Scan the unsorted remainder for the minimum, swap it into place, repeat.

</details>

**6. How many comparisons, and why can it not adapt?**

<details><summary>Answer</summary>

Always $\frac{n(n-1)}{2}$ — **it always scans the whole remainder**, so sortedness of the input buys it nothing.

</details>

**7. How many writes, and why is that its one real advantage?**

<details><summary>Answer</summary>

**Exactly $n-1$ swaps.** When a write is far more expensive than a read — flash memory, huge records — it **moves the least data of any of these**.

</details>

**8. Is it stable?**

<details><summary>Answer</summary>

**No** — the long-range swap can jump one equal element past another.

</details>

---

## C. Bubble sort

**9. State its invariant.**

<details><summary>Answer</summary>

After $i$ passes, the **last $i$ positions hold the $i$ largest elements, in order**.

</details>

**10. Describe the mechanism.**

<details><summary>Answer</summary>

Repeatedly sweep, swapping adjacent out-of-order pairs; the largest "bubbles" to the end each pass.

</details>

**11. What makes it adaptive, and what happens without that?**

<details><summary>Answer</summary>

An **early exit when a pass makes no swaps**, giving $O(n)$ on sorted input. Without the `swapped` flag it is $O(n^2)$ even on sorted input, **losing the one property that makes it tolerable**.

</details>

**12. Is it stable, and why?**

<details><summary>Answer</summary>

**Yes** — it only ever swaps *adjacent* out-of-order elements, never equal ones.

</details>

**13. What is its overall verdict?**

<details><summary>Answer</summary>

**The worst of the three** — $O(n^2)$ comparisons *and* $O(n^2)$ writes.

</details>

---

## D. Insertion sort

**14. State its invariant, precisely.**

<details><summary>Answer</summary>

After $i$ steps, the first $i+1$ elements are sorted **among themselves** — though not necessarily in final position.

</details>

**15. Describe the mechanism.**

<details><summary>Answer</summary>

Take the next element, shift larger elements right, drop it into the gap. **Exactly how you sort a hand of cards.**

</details>

**16. What is its cost on nearly-sorted input?**

<details><summary>Answer</summary>

$O(n)$ — and in general $O(n + d)$ where $d$ is the number of **inversions**. The most adaptive of the three.

</details>

**17. Why is it stable, and what one-character change breaks that?**

<details><summary>Answer</summary>

It shifts only **strictly greater** elements. Writing `<=` instead of `<` in the shift test shifts equal elements too and destroys stability.

</details>

---

## E. Why insertion sort wins small

**18. Count the work at $n = 10$ for each.**

<details><summary>Answer</summary>

Merge sort: ~33 comparisons **plus allocation, recursive call overhead, and copying to and from temporaries**. Insertion sort: at most 45 comparisons, **no allocation, no recursion, perfectly sequential memory access**.

</details>

**19. State the conclusion.**

<details><summary>Answer</summary>

**The asymptotics say merge sort wins; the constants say otherwise — and at $n = 10$ the constants are all there is.**

</details>

**20. Where is the crossover, and what follows from it?**

<details><summary>Answer</summary>

Usually between **10 and 32** elements. **That is why every serious library is a hybrid.**

</details>

**21. How does each hybrid use it?**

<details><summary>Answer</summary>

**Timsort** sorts short runs with *binary* insertion sort, then merges them. **Introsort** quicksorts until partitions are small, then finishes the whole array with one insertion-sort pass.

</details>

---

## F. Prediction drill

**22. On 1,000 already-sorted elements, roughly how many comparisons does each do?**

<details><summary>Answer</summary>

Selection: ~500,000 (it cannot adapt). Bubble with early exit: ~1,000 (one clean pass). Insertion: ~1,000 (each element compares once and stops).

</details>

**23. And on the same array reversed?**

<details><summary>Answer</summary>

All three do about ~500,000 — the reversed array is the worst case for every one of them.

</details>

---

## G. Traps

**24. Does $O(n^2)$ mean "never use it"?**

<details><summary>Answer</summary>

No. **For $n < 32$ these beat everything**, which is why they are in the libraries.

</details>

**25. When should you choose selection sort?**

<details><summary>Answer</summary>

**Only when *writes* are the expensive operation.** It is the slowest in comparisons and cannot adapt.

</details>

**26. Distinguish swaps from writes.**

<details><summary>Answer</summary>

**One swap is two writes.** Selection sort's $n-1$ swaps are $2(n-1)$ writes.

</details>

**27. Summarise the three in one sentence.**

<details><summary>Answer</summary>

All quadratic and all provable in a minute — selection minimises writes, bubble is adaptive only with its early exit, and insertion is adaptive, stable, and the one that survives inside real libraries.

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

- [[02-elementary-sorts|Elementary Sorts]] — the module
- [[01-the-lower-bound-qb|The Lower Bound — Question Bank]]
- [[03-merge-sort-qb|Merge Sort — Question Bank]]
