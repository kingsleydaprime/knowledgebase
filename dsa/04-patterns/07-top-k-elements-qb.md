# Top K Elements — Question Bank

Micro-questions over [[07-top-k-elements|the top-k pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. Top 10 from a million items — what does sorting cost?**

<details><summary>Answer</summary>

$O(n\log n)$ time and $O(n)$ space — **and you only need 10 of the million.**

</details>

**2. State the better idea.**

<details><summary>Answer</summary>

**Maintain a collection of the 10 largest seen so far.** If a new item beats the smallest in the collection, replace it. $O(n\log k)$ time, $O(k)$ space.

</details>

**3. Define the pattern.**

<details><summary>Answer</summary>

**Find the $k$ largest (or smallest) elements without fully sorting.** A heap is the tool that makes this cheaper than sorting everything just to look at the top of it.

</details>

---

## B. The counterintuitive part

**4. To find the $k$ *largest*, which heap do you use?**

<details><summary>Answer</summary>

**A min-heap of size $k$.**

</details>

**5. Why is that the right way round?**

<details><summary>Answer</summary>

**The root is the smallest of your current top-$k$** — so it is exactly the thing to compare against and evict. If a new element beats the root, it is bigger than the current worst of your top-$k$.

</details>

**6. To find the $k$ smallest?**

<details><summary>Answer</summary>

**A max-heap of size $k$** — mirror image. In Python, negate on the way in and out.

</details>

**7. Write the loop.**

<details><summary>Answer</summary>

```python
heap = []
for num in nums:
    heapq.heappush(heap, num)
    if len(heap) > k:
        heapq.heappop(heap)
return heap[0]        # k-th largest
```

</details>

**8. Trace `[3,2,1,5,6,4]`, $k = 2$.**

<details><summary>Answer</summary>

`[3]` → `[2,3]` → push 1, pop 1 → `[2,3]` → push 5, pop 2 → `[3,5]` → push 6, pop 3 → `[5,6]` → push 4, pop 4 → `[5,6]`. **Root = 5, the 2nd largest.**

</details>

**9. What does the root hold at the end?**

<details><summary>Answer</summary>

**The $k$-th largest element overall**, and the heap holds the top $k$ (in no particular order).

</details>

---

## C. Costs

**10. Why is it $O(n\log k)$ rather than $O(n\log n)$?**

<details><summary>Answer</summary>

$n$ insertions and removals, **each $O(\log k)$ because the heap never grows past size $k$.**

</details>

**11. When does it beat sorting?**

<details><summary>Answer</summary>

**Whenever $k$ is meaningfully smaller than $n$.**

</details>

**12. When does sorting win instead?**

<details><summary>Answer</summary>

**When $k$ is close to $n$** — sorting has better cache locality and lower constant overhead.

</details>

---

## D. Extensions

**13. What is quickselect, and what does it cost?**

<details><summary>Answer</summary>

A quicksort-style partition that **recurses into only the side containing the $k$-th element**. Expected $O(n)$.

</details>

**14. Why only one side?**

<details><summary>Answer</summary>

After partitioning, the pivot is in its final position — **so you know which side the $k$-th element is on and can discard the other entirely.**

</details>

**15. What is quickselect's worst case, and what fixes it?**

<details><summary>Answer</summary>

$O(n^2)$ with bad pivots. **Median of medians** — take medians of groups of 5, recursively find the median of those, and use it as pivot — guarantees $O(n)$ worst case.

</details>

**16. Quickselect is $O(n)$ and the heap is $O(n\log k)$. Why use the heap?**

<details><summary>Answer</summary>

**Quickselect mutates the array and needs it all in memory**; the heap is a **single streaming pass** with $O(k)$ space, so it works on data that never fits at once.

</details>

**17. What does k-most-frequent need in addition?**

<details><summary>Answer</summary>

**A hash map to count occurrences first**, then the heap over the `(count, item)` pairs.

</details>

**18. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Keep a size-$k$ heap ordered the *opposite* way to what you are looking for, so the root is always the weakest member and the thing to evict.

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

- [[07-top-k-elements|Top K Elements]] — the pattern
- [[dsa/02-data-structures/08-heaps-qb|Heaps — Question Bank]]
- [[dsa/03-algorithms/04-sorting/04-quicksort-qb|Quicksort — Question Bank]] — where quickselect's partition comes from
