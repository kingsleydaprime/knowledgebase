# Linear & Binary Search — Question Bank

Micro-questions over [[01-linear-and-binary-search|the search module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The idea

**1. Give the dictionary illustration.**

<details><summary>Answer</summary>

Open a 1,000-page dictionary to page 500, see "M", and **discard pages 1–500 in one step**. Open the middle of what remains, see "T", discard 750–1000. Each flip halves the space.

</details>

**2. What single property makes that possible?**

<details><summary>Answer</summary>

**The pages are sorted.** Shuffle them and you are forced to read every page one by one.

</details>

**3. Name three production uses.**

<details><summary>Answer</summary>

Database B-tree index lookups; **`git bisect`**, finding the commit that introduced a bug; Python's `bisect` module for insertion ranks.

</details>

---

## B. The vocabulary

**4. What is the search space?**

<details><summary>Answer</summary>

The range of candidate indices `[low, high]` that could still hold the target.

</details>

**5. What is a monotonic function, and why is it here?**

<details><summary>Answer</summary>

One that only increases or only decreases. **It is the precondition for binary search** — sortedness is just monotonicity of the array.

</details>

---

## C. The algorithm

**6. Write iterative binary search.**

<details><summary>Answer</summary>

```python
low, high = 0, len(arr) - 1
while low <= high:
    mid = low + (high - low) // 2
    if arr[mid] == target: return mid
    elif arr[mid] < target: low = mid + 1
    else: high = mid - 1
return -1
```

</details>

**7. Why `mid = low + (high - low) // 2` rather than `(low + high) // 2`?**

<details><summary>Answer</summary>

**Integer overflow.** In C/Java/C++, `low + high` can exceed 2,147,483,647 and wrap negative. Python is immune, but the habit is worth keeping.

</details>

**8. Why `low = mid + 1` and not `low = mid`?**

<details><summary>Answer</summary>

`arr[mid]` has already been tested and rejected. Leaving it in the range means the space may not shrink, **which is how infinite loops happen**.

</details>

**9. Costs of linear versus binary search?**

<details><summary>Answer</summary>

Linear: $O(n)$, $O(1)$ space, **no precondition**. Binary iterative: $O(\log n)$, $O(1)$ space, **requires sorted data**. Binary recursive: $O(\log n)$ time but $O(\log n)$ call stack.

</details>

---

## D. `bisect`

**10. What does `bisect_left` return?**

<details><summary>Answer</summary>

The index of the **first (leftmost)** position where the value could be inserted — i.e. the first occurrence if present. On `[1,3,4,4,6,8]` with 4, it returns **2**.

</details>

**11. What does `bisect_right` return?**

<details><summary>Answer</summary>

The index **after** all equal values. Same array and value: **4**.

</details>

**12. What does the difference between them give you?**

<details><summary>Answer</summary>

**The count of occurrences** — `bisect_right(a,v) - bisect_left(a,v)`.

</details>

**13. What is `insort`, and what is its real cost?**

<details><summary>Answer</summary>

Inserts in place keeping the list sorted. **$O(\log n)$ to find the spot but $O(n)$ to shift** — the search is not the expensive part.

</details>

---

## E. Rotated arrays

**14. What is the key fact about a rotated sorted array?**

<details><summary>Answer</summary>

**At any split, at least one half — left or right — is guaranteed to be strictly sorted.**

</details>

**15. How do you use that?**

<details><summary>Answer</summary>

Identify which half is sorted (`nums[low] <= nums[mid]` means the left is). Then check whether the target lies **within that sorted half's range**; if so search it, otherwise search the other.

</details>

**16. Why can you not simply compare against `nums[mid]` as usual?**

<details><summary>Answer</summary>

Because the array is not globally monotonic — **a value greater than `nums[mid]` may still lie to the left of it**, across the rotation point.

</details>

---

## F. Traps

**17. What happens if you binary search an unsorted array?**

<details><summary>Answer</summary>

**No exception is raised.** It silently returns incorrect and inconsistent answers.

</details>

**18. What is the `<=` versus `<` loop-bound trap?**

<details><summary>Answer</summary>

Mixing them up causes **infinite loops or skipped boundary elements**. `while low <= high` with `mid ± 1` updates is the form that terminates and checks everything.

</details>

**19. Summarise in one sentence.**

<details><summary>Answer</summary>

Halve the space on every comparison — $O(\log n)$, but only on monotonic data, and silently wrong on anything else.

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

- [[01-linear-and-binary-search|Linear & Binary Search]] — the module
- [[02-binary-search-on-the-answer-qb|Binary Search on the Answer — Question Bank]] — the generalisation
- [[dsa/04-patterns/09-modified-binary-search|Modified Binary Search]] — the pattern
