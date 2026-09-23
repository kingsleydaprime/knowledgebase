# Sliding Window — Question Bank

Micro-questions over [[03-sliding-window|the sliding window pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. What does the naive approach cost, and why is that wasteful?**

<details><summary>Answer</summary>

$O(n \cdot k)$ — **each query recomputes the same sliding sums over and over** from scratch.

</details>

**2. State the fix.**

<details><summary>Answer</summary>

**Compute the first window's sum once, then slide it one step at a time**, adding the new element and subtracting the one that falls out.

</details>

**3. Why is the result $O(n)$?**

<details><summary>Answer</summary>

**Each element enters and leaves the window at most once.**

</details>

**4. What does Codility call this?**

<details><summary>Answer</summary>

**The caterpillar method** — same technique, a front and back index each only ever moving forward.

</details>

---

## B. The vocabulary

**5. Define a sliding window.**

<details><summary>Answer</summary>

A contiguous subarray or substring that **moves one element at a time**, maintaining a fixed or variable size — a camera panning across a scene.

</details>

**6. Fixed-size versus variable-size?**

<details><summary>Answer</summary>

**Fixed**: size $k$ is constant; slide by removing the element that falls out the back and adding the one entering the front. **Variable**: the window grows and shrinks depending on a condition.

</details>

**7. Give an example of each.**

<details><summary>Answer</summary>

Fixed: a 3-day moving average. Variable: longest substring without repeating characters.

</details>

---

## C. Fixed-size windows

**8. Write the update step.**

<details><summary>Answer</summary>

```python
window_sum += nums[i] - nums[i - k]   # add new, drop oldest — O(1)
```

</details>

**9. Trace `[2,1,5,1,3,2]`, $k = 3$.**

<details><summary>Answer</summary>

`[2,1,5]` = 8 → `[1,5,1]` = 7 → `[5,1,3]` = **9** (best) → `[1,3,2]` = 6.

</details>

**10. Does it still work with negative numbers?**

<details><summary>Answer</summary>

**Yes.** `new_sum = old_sum - nums[i-k] + nums[i]` is valid regardless of sign — **the algorithm does not assume positivity.**

</details>

---

## D. Variable-size windows

**11. Describe the longest-substring-without-repeats loop.**

<details><summary>Answer</summary>

Expand the right edge each iteration; **while the constraint is violated, shrink from the left**, removing characters from `seen`. Record the best length each step.

</details>

**12. Why is it $O(n)$ despite the nested `while` inside the `for`?**

<details><summary>Answer</summary>

**Each character is added to `seen` at most once and removed at most once across the whole run** — total operations bounded by $2n$, not $n^2$.

</details>

**13. What familiar analysis is that?**

<details><summary>Answer</summary>

**The same amortised argument as dynamic array resizing** — the loop looks nested, but the total work across the run is linear.

</details>

**14. Describe minimum window substring.**

<details><summary>Answer</summary>

Track a `need` counter of required characters and a `missing` count. Expand right; **whenever `missing == 0` the window is valid**, so record it and shrink from the left until it stops being valid.

</details>

---

## E. When the aggregate is not invertible

**15. Why can sliding window maximum not use add-one-drop-one?**

<details><summary>Answer</summary>

**Max is not invertible.** Knowing the old max and the element that left tells you nothing about the new max if the departing element *was* the max.

</details>

**16. What structure does it use instead?**

<details><summary>Answer</summary>

A **monotonic deque** storing indices with decreasing values.

</details>

**17. Describe its two `while` loops.**

<details><summary>Answer</summary>

1. **Pop from the front** any index that has fallen out of the window.
2. **Pop from the back** any index whose value is $\le$ the incoming one — it can never be the max again.

</details>

**18. Where is the answer at each step?**

<details><summary>Answer</summary>

**`nums[dq[0]]`** — the front of the deque, once the window is full.

</details>

---

## F. Trade-offs

**19. What is the fixed-size window's precondition?**

<details><summary>Answer</summary>

**An invertible aggregate.** Sum and count work; max, min and median do not.

</details>

**20. When should you use prefix sums instead?**

<details><summary>Answer</summary>

When the problem requires **checking every possible window** — e.g. "find all subarrays with sum equals $k$". A window cannot help there, especially with negative values, because shrinking is no longer monotone.

</details>

**21. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Maintain a contiguous span and update it incrementally as it moves — linear because every element enters and leaves exactly once, however nested the loops look.

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

- [[03-sliding-window|Sliding Window]] — the pattern
- [[02-two-pointers-qb|Two Pointers — Question Bank]]
- [[06-monotonic-stack-qb|Monotonic Stack — Question Bank]] — the deque variant
- [[01-prefix-sum-qb|Prefix Sum — Question Bank]] — what to use when the window cannot shrink monotonically
