# Modified Binary Search — Question Bank

Micro-questions over [[09-modified-binary-search|the modified binary search pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The problem

**1. Why does plain binary search fail on `[4,5,6,7,0,1,2]`?**

<details><summary>Answer</summary>

**The array is not fully sorted** — it is sorted and then rotated at an unknown pivot, so comparing against `nums[mid]` no longer tells you which side the target is on.

</details>

**2. State the key insight.**

<details><summary>Answer</summary>

**Even when the whole array is not sorted, at least one of the two halves around any `mid` is guaranteed to be sorted.**

</details>

**3. Why is that true?**

<details><summary>Answer</summary>

**There is exactly one rotation point**, so it falls in one half and the other half is untouched.

</details>

**4. What is a rotated sorted array?**

<details><summary>Answer</summary>

A sorted array rotated at an unknown pivot — `[4,5,6,7,0,1,2]` is `[0,1,2,4,5,6,7]` rotated at index 4.

</details>

---

## B. The rotated search

**5. How do you decide which half is sorted?**

<details><summary>Answer</summary>

**Compare `nums[left]` with `nums[mid]`.** If `nums[left] <= nums[mid]`, the left half is normally sorted; otherwise the right half is.

</details>

**6. Once you know, what do you check?**

<details><summary>Answer</summary>

**Whether the target falls inside that sorted half's range.** If so, search there; otherwise the target must be in the other, still-rotated half.

</details>

**7. Write the two branches.**

<details><summary>Answer</summary>

```python
if nums[left] <= nums[mid]:               # left sorted
    if nums[left] <= target < nums[mid]: right = mid - 1
    else:                                 left = mid + 1
else:                                     # right sorted
    if nums[mid] < target <= nums[right]: left = mid + 1
    else:                                 right = mid - 1
```

</details>

**8. Trace target 0 on `[4,5,6,7,0,1,2]`.**

<details><summary>Answer</summary>

`mid=3` (7); left half `[4,5,6,7]` sorted; 0 not in `[4,7)` → go right, `left=4`. `mid=5` (1); left half `[0,1]` sorted; 0 in `[0,1)` → go left, `right=4`. `mid=4` (0) → **found at index 4.**

</details>

**9. Why do the range checks use half-open intervals (`<` on one end)?**

<details><summary>Answer</summary>

**`nums[mid]` has already been tested and rejected**, so it must be excluded from both candidate ranges or the search can fail to shrink.

</details>

---

## C. Binary search on the answer

**10. What is the distinct variant?**

<details><summary>Answer</summary>

**Binary searching over the space of possible answers**, not over array indices.

</details>

**11. When does it apply?**

<details><summary>Answer</summary>

When a problem asks for **the optimal value satisfying a condition**, and **"is candidate X good enough?" is cheap to check and monotonic.**

</details>

**12. Define a monotonic predicate.**

<details><summary>Answer</summary>

**A condition that, once true, stays true for all larger values** — every value below a threshold fails, every value at or above it works, with no flip-flopping.

</details>

**13. Give two canonical examples.**

<details><summary>Answer</summary>

Koko's minimum eating speed to finish in $H$ hours; the minimum ship capacity to deliver in $D$ days. Also the minimum board size covering all holes with $k$ boards.

</details>

**14. What is the cost?**

<details><summary>Answer</summary>

$O(\text{check} \times \log R)$ where $R$ is the size of the answer range — and $\log R$ is small even for enormous ranges.

</details>

---

## D. Trade-offs

**15. What does rotated search assume?**

<details><summary>Answer</summary>

**That the array is sorted and rotated — not arbitrary unsorted data — and that there is exactly one rotation point.**

</details>

**16. What does binary search on the answer require?**

<details><summary>Answer</summary>

**A monotonic predicate.** Not all optimisation problems have this property, and **the technique returns a plausible wrong number when it is absent.**

</details>

**17. What happens with duplicates in a rotated array?**

<details><summary>Answer</summary>

`nums[left] == nums[mid]` becomes ambiguous — you cannot tell which half is sorted. **The worst case degrades to $O(n)$**, and the standard fix is to shrink `left` by one and retry.

</details>

**18. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Binary search needs only a way to discard half the space — not sortedness — so find the half you can reason about, whether that half is in an array or in a range of candidate answers.

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

- [[09-modified-binary-search|Modified Binary Search]] — the pattern
- [[dsa/03-algorithms/05-searching/01-linear-and-binary-search-qb|Linear & Binary Search — Question Bank]]
- [[dsa/03-algorithms/05-searching/02-binary-search-on-the-answer-qb|Binary Search on the Answer — Question Bank]] — the variant in depth
