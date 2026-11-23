---
id: cb9553b1-652d-40a8-b2f9-cc5532a98f1d
---

# Module: Searching Algorithms (Linear & Binary Search)

Welcome to the **Searching Algorithms** module. Searching is the process of locating a specific target value within a data structure.

The choice of search algorithm depends entirely on one fundamental question: **Is the data sorted?**

---

## Before you start
<!-- bite: 6bd4bc74-37de-4877-b73e-2623de929946 -->

- You know what sorted order buys you — [[05-sorting/index|sorting]].
- You can reason about a loop invariant — [[05-sorting/02-elementary-sorts|elementary sorts]].
- You know $O$ and $\log$ — [[01-growth-and-asymptotic-notation|complexity analysis]].

**After this lesson you will be able to:**

1. Write binary search **correctly**, including the boundary conditions that make most attempts wrong.
2. Find the **first** and **last** occurrence of a value, not just any occurrence.
3. Recognise and apply **binary search on the answer**, where the array being searched does not exist.
4. State the invariant your loop maintains, and use it to decide `<` versus `<=` and `mid` versus `mid+1`.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 tests the classic off-by-one bugs on purpose.

---

## 1. Real-World Motivation & Physical Metaphors
<!-- bite: 90a63025-9579-42bd-a151-98234ff578d0 -->

Imagine looking up a word in a **printed physical dictionary**:

```text
Search space: 1,000 pages

Step 1: Open dictionary directly to the middle (Page 500).
        Word is "M" (Target "R" comes AFTER "M").
        -> INSTANTLY DISCARD PAGES 1 TO 500! (500 pages eliminated in 1 step!)

Step 2: Open middle of remaining pages 501-1000 (Page 750).
        Word is "T" (Target "R" comes BEFORE "T").
        -> INSTANTLY DISCARD PAGES 750 TO 1000!
```

- If the dictionary pages were shuffled in random order, you would be forced to read every page one-by-one (**Linear Search**).
- Because the pages are **sorted**, you can halve the remaining search space with every single flip (**Binary Search**)!

### Production Applications:
1. **Database Index Lookups**: B-Tree indices finding records in $O(\log n)$ time.
2. **Git Bisect**: Finding the exact commit that introduced a bug using binary search over commit history.
3. **Libraries**: Python `bisect` module for finding insertion ranks in $O(\log n)$.

---

## 2. Plain-English Terminology & Concept Table
<!-- bite: fc952e23-9051-4251-aa68-8fce2f484f99 -->

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Linear Search** | Checking every element sequentially from index 0 to $N-1$. | Scanning a random pile of papers for a specific invoice. |
| **Binary Search** | Repeatedly checking the middle element and discarding the half that cannot contain target. | Flipping to the middle of a phonebook. |
| **Search Space** | The range of candidate indices `[low, high]` that could hold the target. | Pages 501 to 750 in a dictionary. |
| **Monotonic Function** | A function or sequence that only increases or only decreases. | Precondition for Binary Search. |

---

## 3. Technical Deep Dive: Linear vs. Binary Search
<!-- bite: d78d0c90-71e7-442f-bf08-67e7edc64987 -->

### 1. Linear Search ($O(n)$ Unsorted Fallback)
```python
def linear_search(arr: list, target: int) -> int:
    """Scans array sequentially. Returns index if found, else -1."""
    for index, value in enumerate(arr):
        if value == target:
            return index
    return -1
```

---

### 2. Binary Search ($O(\log n)$ Sorted Requirement)

```python
def binary_search(arr: list, target: int) -> int:
    """Finds target in a SORTED array using binary search. Returns index or -1."""
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        # Safe midpoint calculation (prevents integer overflow in C/Java)
        mid = low + (high - low) // 2
        
        if arr[mid] == target:
            return mid          # Target found!
        elif arr[mid] < target:
            low = mid + 1       # Target is in right half
        else:
            high = mid - 1      # Target is in left half
            
    return -1                   # Target does not exist
```

---

## 4. The Python `bisect` Built-in Module
<!-- bite: e6702278-84b9-4efb-9b16-25920158ed8f -->

Python includes a high-performance C-implemented binary search module called `bisect`:

```python
import bisect

arr = [1, 3, 4, 4, 6, 8]

# 1. bisect_left: Find index of FIRST (leftmost) occurrence
idx_left = bisect.bisect_left(arr, 4)   # Returns index 2

# 2. bisect_right: Find index where item should be inserted (after duplicates)
idx_right = bisect.bisect_right(arr, 4) # Returns index 4

# 3. insort: Insert item in-place while keeping list sorted (O(n) shift, O(log n) search)
bisect.insort(arr, 5)  # Resulting arr: [1, 3, 4, 4, 5, 6, 8]
```

---

## 5. Advanced Pattern: Search in Rotated Sorted Array
<!-- bite: 92229eb0-1fa9-4300-96c8-b8eea281df6a -->

What if a sorted array was rotated at a pivot point (e.g. `[4, 5, 6, 7, 0, 1, 2]`)?

Even though the array is rotated, **at least one half (left or right) is guaranteed to be strictly sorted** at any split:

```python
def search_rotated(nums: list, target: int) -> int:
    low, high = 0, len(nums) - 1
    
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return mid
            
        # Check if left half is sorted
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1  # Target in sorted left half
            else:
                low = mid + 1   # Target in right half
        # Otherwise, right half MUST be sorted
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1   # Target in sorted right half
            else:
                high = mid - 1  # Target in left half
                
    return -1
```

---

## 6. Time & Space Complexity Summary
<!-- bite: 9c004efe-ae3b-4dbf-829c-e61d53990053 -->

| Algorithm | Precondition | Time Complexity | Auxiliary Space |
| :--- | :--- | :--- | :--- |
| **Linear Search** | None (Works on any dataset) | $O(n)$ | $O(1)$ |
| **Binary Search (Iterative)** | **Data MUST be sorted** | **$O(\log n)$** | $O(1)$ |
| **Binary Search (Recursive)** | **Data MUST be sorted** | **$O(\log n)$** | $O(\log n)$ call stack |

---

## Implementation — complete runnable example
<!-- bite: 6245ef69-4195-4b33-a10a-a29254024544 -->

**Runnable example:** save as `searching.py` in any empty directory and run `python3 searching.py`. Standard library only; writes no files.

```python
"""Binary search done right: boundaries, first/last, and search on the answer."""
import math
import random


def linear_search(xs, target, c):
    for i, v in enumerate(xs):
        c[0] += 1
        if v == target:
            return i
    return -1


def binary_search(xs, target, c):
    """Invariant: if target is present, it lies in xs[lo..hi] inclusive."""
    lo, hi = 0, len(xs) - 1
    while lo <= hi:                      # <= because lo==hi is still one candidate
        c[0] += 1
        mid = lo + (hi - lo) // 2        # avoids overflow in fixed-width languages
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1                 # mid is ruled out, so +1
        else:
            hi = mid - 1
    return -1


def lower_bound(xs, target):
    """First index with xs[i] >= target. Invariant: answer is in [lo, hi]."""
    lo, hi = 0, len(xs)                  # hi is len, not len-1: 'not found' is a valid answer
    while lo < hi:                       # < because hi is exclusive here
        mid = lo + (hi - lo) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid                     # NOT mid-1: mid may itself be the answer
    return lo


def upper_bound(xs, target):
    """First index with xs[i] > target."""
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if xs[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def search_on_answer(feasible, lo, hi):
    """Smallest x in [lo, hi] with feasible(x) true, given feasible is monotonic."""
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def min_ship_capacity(weights, days):
    def can_ship(capacity):
        if capacity < max(weights):
            return False
        needed, load = 1, 0
        for w in weights:
            if load + w > capacity:
                needed += 1
                load = 0
            load += w
        return needed <= days
    return search_on_answer(can_ship, max(weights), sum(weights))


if __name__ == "__main__":
    print("Block 1 - linear vs binary, counted")
    print("        n   linear worst   binary worst   log2(n)")
    for n in (10, 100, 10000, 1000000):
        xs = list(range(n))
        cl, cb = [0], [0]
        linear_search(xs, n - 1, cl)          # worst case: last element
        binary_search(xs, -1, cb)             # worst case: absent
        print(f"  {n:7,}   {cl[0]:12,}   {cb[0]:12}   {math.log2(n):7.1f}")
    xs = list(range(1000000))
    c = [0]
    binary_search(xs, -1, c)
    assert c[0] <= math.ceil(math.log2(1000000)) + 1
    print("  a million elements in 20 comparisons - each step halves what is left")

    print()
    print("Block 2 - correctness on every position, and every absent value")
    rng = random.Random(20260910)
    for _ in range(500):
        n = rng.randint(0, 40)
        xs = sorted(rng.randint(-20, 20) for _ in range(n))
        for target in range(-22, 23):
            got = binary_search(xs, target, [0])
            if target in xs:
                assert got != -1 and xs[got] == target, (xs, target, got)
            else:
                assert got == -1, (xs, target, got)
    print("  500 random arrays x 45 targets: found when present, -1 when absent")

    print()
    print("Block 3 - first and last occurrence, via lower/upper bound")
    xs = [1, 2, 2, 2, 3, 5, 5, 8]
    print(f"  array: {xs}")
    for t in (2, 5, 4, 0, 9):
        lo, hi = lower_bound(xs, t), upper_bound(xs, t)
        count = hi - lo
        first = lo if count else None
        last = hi - 1 if count else None
        print(f"    target {t}: first={str(first):4} last={str(last):4} count={count}")
    assert lower_bound(xs, 2) == 1 and upper_bound(xs, 2) == 4
    assert upper_bound(xs, 2) - lower_bound(xs, 2) == 3
    assert lower_bound(xs, 4) == upper_bound(xs, 4) == 5   # 4 is absent: both point past the 3
    print("  count = upper_bound - lower_bound, and equal bounds mean 'absent'.")
    print("  Note lower_bound uses hi = len (not len-1) and hi = mid (not mid-1):")
    print("  the answer may be one past the end, and mid may itself be the answer.")

    print()
    print("Block 4 - the three classic bugs, each shown failing")

    def bug_infinite(xs, target, limit=100):
        """hi = mid instead of mid - 1, with lo <= hi: never terminates."""
        lo, hi, steps = 0, len(xs) - 1, 0
        while lo <= hi and steps < limit:
            steps += 1
            mid = (lo + hi) // 2
            if xs[mid] == target:
                return mid, steps
            if xs[mid] < target:
                lo = mid + 1
            else:
                hi = mid                  # BUG: mid is never excluded
        return -1, steps

    _, steps = bug_infinite([1, 3, 5, 7], 2)
    print(f"  'hi = mid' with 'lo <= hi': ran {steps} steps and never terminated")
    assert steps == 100

    def bug_strict(xs, target):
        """lo < hi instead of lo <= hi: misses a single-candidate range."""
        lo, hi = 0, len(xs) - 1
        while lo < hi:                    # BUG: stops with one candidate unchecked
            mid = (lo + hi) // 2
            if xs[mid] == target:
                return mid
            if xs[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

    print(f"  'lo < hi' on [5], searching 5: {bug_strict([5], 5)}  (should be 0)")
    assert bug_strict([5], 5) == -1
    assert binary_search([5], 5, [0]) == 0
    print("  the correct version returns 0 - the single element was never examined")

    big = (1 << 62) - 1
    naive_mid = (big + big) // 2
    safe_mid = big + (big - big) // 2
    print(f"  overflow: (lo+hi)//2 on two values near 2^62 gives {naive_mid:,}")
    print(f"            lo+(hi-lo)//2 gives {safe_mid:,}")
    print("  Python integers are unbounded so this is safe here; in C, Java or Rust")
    print("  the first form overflows, and it was a real bug in the JDK for nine years.")

    print()
    print("Block 5 - binary search where there is no array")
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for days in (1, 3, 5, 10):
        cap = min_ship_capacity(weights, days)
        print(f"  ship {weights} in {days:2} days -> minimum capacity {cap}")
    assert min_ship_capacity(weights, 5) == 15
    assert min_ship_capacity(weights, 1) == sum(weights)
    assert min_ship_capacity(weights, 10) == max(weights)
    print("  nothing here is sorted, and no array is searched. What makes it work is")
    print("  MONOTONICITY: if capacity c suffices then so does c+1, so the feasible")
    print("  values form a prefix, and you can binary search for its boundary.")

    print()
    print("searching: passed")
```

Expected output:

```text
Block 1 - linear vs binary, counted
        n   linear worst   binary worst   log2(n)
       10             10              3       3.3
      100            100              6       6.6
   10,000         10,000             13      13.3
  1,000,000      1,000,000             19      19.9
  a million elements in 20 comparisons - each step halves what is left

Block 2 - correctness on every position, and every absent value
  500 random arrays x 45 targets: found when present, -1 when absent

Block 3 - first and last occurrence, via lower/upper bound
  array: [1, 2, 2, 2, 3, 5, 5, 8]
    target 2: first=1    last=3    count=3
    target 5: first=5    last=6    count=2
    target 4: first=None last=None count=0
    target 0: first=None last=None count=0
    target 9: first=None last=None count=0
  count = upper_bound - lower_bound, and equal bounds mean 'absent'.
  Note lower_bound uses hi = len (not len-1) and hi = mid (not mid-1):
  the answer may be one past the end, and mid may itself be the answer.

Block 4 - the three classic bugs, each shown failing
  'hi = mid' with 'lo <= hi': ran 100 steps and never terminated
  'lo < hi' on [5], searching 5: -1  (should be 0)
  the correct version returns 0 - the single element was never examined
  overflow: (lo+hi)//2 on two values near 2^62 gives 4,611,686,018,427,387,903
            lo+(hi-lo)//2 gives 4,611,686,018,427,387,903
  Python integers are unbounded so this is safe here; in C, Java or Rust
  the first form overflows, and it was a real bug in the JDK for nine years.

Block 5 - binary search where there is no array
  ship [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] in  1 days -> minimum capacity 55
  ship [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] in  3 days -> minimum capacity 21
  ship [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] in  5 days -> minimum capacity 15
  ship [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] in 10 days -> minimum capacity 10
  nothing here is sorted, and no array is searched. What makes it work is
  MONOTONICITY: if capacity c suffices then so does c+1, so the feasible
  values form a prefix, and you can binary search for its boundary.

searching: passed
```

Block 4 runs each classic bug and shows it failing — an infinite loop, a missed single element, and the overflow that sat in the JDK's binary search for nine years.

## 7. Common Pitfalls & Traps
<!-- bite: 2f31401a-2ade-49c5-a064-5c3cae56d756 -->

1. **Unsorted Array Failure**: Running Binary Search on an unsorted array does NOT raise an exception—it silently returns incorrect/inconsistent answers!
2. **Integer Overflow in Midpoint**: Writing `mid = (low + high) // 2` can overflow maximum 32-bit integer limits in C/Java/C++ if `low + high > 2,147,483,647`. Always write `mid = low + (high - low) // 2`.
3. **Off-by-One Loop Bounds**: Mixing up `while low <= high` vs `while low < high` causes infinite loops or skips checking boundary elements.

---

## Check your understanding
<!-- bite: 16013cbb-b808-4aaf-a3b0-a1502d7cdc85 -->

Try each one before you open the answer.

1. <!-- q: exact id="578f6b74" answer="20" -->
   At most how many loop iterations (middle checks) does binary search need on a sorted array of 1,000,000 elements?

   <details><summary>Answer</summary>

   20. Each check halves the range, and log₂ 1,000,000 ≈ 19.93, so 20 halvings are enough to shrink it to nothing.

   </details>

2. <!-- q: mcq id="2f8169aa" -->
   Why do C++ and Java programmers write `mid = low + (high - low) / 2` instead of `mid = (low + high) / 2`?

   - [ ] It is faster
   - [x] `low + high` can overflow a 32-bit integer when both are large
   - [ ] It rounds up instead of down
   - [ ] It works on unsorted arrays

   <details><summary>Answer</summary>

   With low and high around 1.5 billion, their sum passes the 32-bit limit of about 2.14 billion and wraps to a negative number. `high - low` never overflows.

   </details>

3. <!-- q: mcq id="f2850301" -->
   An array is unsorted and you need to search it once. Should you sort it first and then use binary search?

   - [ ] Yes, binary search is always faster
   - [x] No, sorting costs O(n log n), which is more than one O(n) linear search
   - [ ] Yes, if n is larger than 1,000
   - [ ] No, binary search cannot run on numbers

   <details><summary>Answer</summary>

   Sorting plus one search is O(n log n). One linear search is O(n). Sorting first only pays off when you will search many times.

   </details>

4. <!-- q: gap id="fd28e038" answers="left;right" -->
   Fill in the gaps. In a rotated sorted array such as [4, 5, 6, 7, 0, 1, 2], at every split at least one half is sorted. If nums[low] ≤ nums[mid], the ___ half is sorted; otherwise the ___ half is.

   <details><summary>Answer</summary>

   Left, then right. Once you know which half is sorted, you can check with two comparisons whether the target lies inside it.

   </details>

5. <!-- q: mcq id="20affb7b" -->
   What does `bisect.bisect_left(arr, x)` return for a sorted list that contains x several times?

   - [x] The index of the first (leftmost) x
   - [ ] The index just after the last x
   - [ ] The number of times x appears
   - [ ] −1

   <details><summary>Answer</summary>

   bisect_left gives the leftmost position where x could be inserted, which is the first occurrence. bisect_right gives the position after the last occurrence.

   </details>

## Check your understanding: worked problems
<!-- bite: 7c39366d-2bce-4536-bf52-acfc6c601151 -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="e2f11116" answers="5;8" -->
   Fill in the gaps. Binary search with `mid = low + (high - low) // 2` looks for 61 in this sorted array (indexes 0 to 10):

   | index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
   |---|---|---|---|---|---|---|---|---|---|---|---|
   | value | 3 | 8 | 15 | 21 | 27 | 34 | 40 | 52 | 61 | 75 | 88 |

   The first mid is ___ and the second mid is ___, where 61 is found.

   <details><summary>Answer</summary>

   mid = 5 holds 34, which is less than 61, so low becomes 6. Then mid = 6 + (10 − 6) // 2 = 8, which holds 61.

   </details>

2. <!-- q: gap id="c1267d30" answers="5;2;0;1" -->
   Fill in the gaps. Array: [3, 8, 15, 21, 27, 34, 40, 52, 61, 75, 88], indexes 0 to 10, with `mid = low + (high - low) // 2`. Searching for 10, which is not there, the mids checked are ___, ___, ___, ___, and then the search returns −1.

   <details><summary>Answer</summary>

   5 (34, go left), 2 (15, go left), 0 (3, go right), 1 (8, go right). Now low = 2 > high = 1, so the loop ends: not found.

   </details>

3. <!-- q: gap id="8e1817a5" answers="1;4;4" -->
   Fill in the gaps. For b = [2, 5, 5, 5, 9, 12, 12, 20], `bisect_left(b, 5)` = ___, `bisect_right(b, 5)` = ___ and `bisect_left(b, 7)` = ___.

   <details><summary>Answer</summary>

   The first 5 is at index 1, and the last 5 is at index 3, so bisect_right returns 4. 7 is not present; it would go before 9, at index 4.

   </details>

4. <!-- q: exact id="71cd4c75" answer="5" -->
   The rotated search (check which half is sorted, then whether the target lies inside it) looks for 20 in [30, 40, 50, 60, 10, 20, 25]. At which index does it find 20?

   <details><summary>Answer</summary>

   Index 5. mid = 3 holds 60; the left half 30..60 is sorted and 20 is not in it, so low = 4. Then mid = 5 holds 20.

   </details>

## Practice — independent task
<!-- bite: 34380c7e-fa9b-4906-bab5-02ba07f890c3 -->

Implement `search_rotated(nums, target)` — binary search on a sorted array that has been rotated at an unknown pivot.

1. At each step, one half is guaranteed to be **normally sorted**. Identify which by comparing `nums[lo]` with `nums[mid]`, then decide whether the target lies inside it.
2. State your loop invariant in a comment before writing the loop, and check every branch preserves it.
3. Verify exhaustively: for every array length up to 12, every rotation, and every target present or absent, assert the result matches a linear scan. That is a few hundred thousand cases and runs in seconds.
4. **Then handle duplicates.** With duplicates allowed, `nums[lo] == nums[mid]` no longer tells you which half is sorted. Implement the fix, and show with a concrete input that the worst case degrades to $O(n)$ — then explain why no better bound is possible.
5. Also implement `find_rotation_point(nums)` returning the index of the minimum, and use it to solve the original problem differently: find the pivot, then binary search the correct half. Compare comparison counts between the two approaches.

**Edge cases:** no rotation at all; rotation by exactly `len(nums)`; a single element; all elements equal; target at the pivot itself.

**Done when:** your exhaustive test passes for every length up to 12, your duplicate-handling version is correct, and you can explain with a specific input why duplicates force $O(n)$.

## Before moving on
<!-- bite: 3603153d-7244-420d-b52e-0cda67e5d027 -->

You can write binary search correctly, find first and last occurrences, and recognise search-on-the-answer.

**Recap:** binary search needs **sorted** input and is $O(\log n)$; `lo <= hi` with `hi = mid - 1`, or `lo < hi` with `hi = mid` — mixing the two conventions is what causes infinite loops and missed elements; use `lo + (hi-lo)//2` out of habit; `lower_bound` gives the first index $\ge$ target and `upper_bound` the first $>$, so their difference is the count; **search on the answer** works whenever the feasibility predicate is monotonic, and needs no array at all.

**Next:** [[02-dijkstra|Dijkstra's Algorithm]] — BFS plus a priority queue, for when edges have weights.

## Related Modules
<!-- bite: faf452d9-8167-4c69-8c4b-fc5e37c0bfe2 -->
- [[05-sorting/index|Sorting Algorithms]] — Precondition for binary search
- [[01-growth-and-asymptotic-notation|Algorithms & Complexity Analysis]] — Logarithmic bounds derivation
- [[01-trees|Trees]] — Binary Search Trees (pointer-based binary search)
