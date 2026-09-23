# Max Slice Algorithms — Question Bank

Micro-questions over [[09-max-slice-algorithms|the max slice module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The problem

**1. State the problem in trading terms.**

<details><summary>Answer</summary>

Given daily profit/loss figures, find **the contiguous window of days maximising cumulative profit**.

</details>

**2. What is a subarray / slice?**

<details><summary>Answer</summary>

A **contiguous** block of elements — a date range window on a calendar. Contiguity is what makes it a different problem from "pick any subset".

</details>

**3. Name three applications.**

<details><summary>Answer</summary>

Optimal stock holding window; isolating the highest-amplitude segment of a noisy signal; identifying the highest-density gene region in a DNA strand.

</details>

---

## B. The two naive approaches

**4. Why is brute force $O(n^3)$?**

<details><summary>Answer</summary>

There are $O(n^2)$ possible subarrays, and **each is summed from scratch in $O(n)$**.

</details>

**5. What single change gives $O(n^2)$?**

<details><summary>Answer</summary>

**Maintain a running sum** for a fixed start `p`. Moving `q` forward extends it by one addition instead of recomputing.

</details>

**6. What is the general lesson from that step?**

<details><summary>Answer</summary>

**Recomputing what you already knew is the usual source of an extra factor of $n$** — the same move that turns many cubic solutions quadratic.

</details>

---

## C. Kadane's algorithm

**7. State the recurrence in words.**

<details><summary>Answer</summary>

The best subarray **ending at position $i$** is either the best ending at $i-1$ extended by one element, or **a brand new subarray starting at $i$ alone**.

</details>

**8. State it as a rule of thumb.**

<details><summary>Answer</summary>

**If carrying the negative baggage of a prior run makes things worse than starting fresh, cut and restart.**

</details>

**9. What do `max_ending_here` and `max_so_far` mean?**

<details><summary>Answer</summary>

`max_ending_here` = the best sum achievable by any subarray **ending exactly at the current position**. `max_so_far` = the global running maximum **across all positions so far**.

</details>

**10. Write the loop.**

<details><summary>Answer</summary>

```python
max_ending_here = max_so_far = 0
for value in A:
    max_ending_here = max(0, max_ending_here + value)
    max_so_far = max(max_so_far, max_ending_here)
```

</details>

**11. What is the `max(0, ...)` doing?**

<details><summary>Answer</summary>

**Resetting to 0 allows starting a completely new subarray from the next element** — equivalent to allowing the empty slice as a baseline.

</details>

**12. Trace it on `[-2,3,4,-1,5,-8,4,1]`.**

<details><summary>Answer</summary>

`max_ending_here`: 0, 3, 7, 6, 11, 3, 7, 8. `max_so_far`: 0, 3, 7, 7, 11, 11, 11, 11. **Answer 11.**

</details>

**13. What are its costs?**

<details><summary>Answer</summary>

$O(n)$ time, **$O(1)$ space** — one pass, two variables.

</details>

**14. What does this version return for an all-negative array, and is that right?**

<details><summary>Answer</summary>

**0** — because the empty slice is allowed. If the problem requires a **non-empty** subarray, initialise both to `A[0]` and drop the `max(0, ...)` clamp. **Read the problem statement for which variant is wanted.**

</details>

---

## D. Why it is DP

**15. What is the subproblem?**

<details><summary>Answer</summary>

`max_ending_here[i]` = the best subarray sum **ending at index $i$**.

</details>

**16. Why must the state pin the ending index?**

<details><summary>Answer</summary>

Because otherwise you cannot tell whether the next element can extend the best run — **the same reason LIS pins its ending element.**

</details>

**17. Where is the optimal substructure?**

<details><summary>Answer</summary>

The global answer is built from optimal answers to smaller problems — **`max_so_far` is the max over all `max_ending_here` values.**

</details>

**18. Why is the space $O(1)$ rather than $O(n)$?**

<details><summary>Answer</summary>

**Only the immediately previous subproblem value is ever needed**, so the table collapses to one variable.

</details>

**19. Where is the global answer, and why not the last cell?**

<details><summary>Answer</summary>

It is the **maximum over all cells**, not the last one — because the state pins the ending position, no single cell holds the global answer.

</details>

**20. Summarise Kadane's in one sentence.**

<details><summary>Answer</summary>

Carry the best run ending here, drop it the moment it turns negative, and remember the best you ever saw — dynamic programming compressed into two variables.

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

- [[09-max-slice-algorithms|Max Slice Algorithms]] — the module
- [[06-dynamic-programming/03-classic-one-dimensional-qb|Classic 1-D DP — Question Bank]] — the same "pin the ending index" move
- [[03-divide-and-conquer-qb|Divide and Conquer — Question Bank]] — the $O(n\log n)$ solution this one beats
