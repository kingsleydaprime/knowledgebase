# Module: Searching Algorithms (Linear & Binary Search)

Welcome to the **Searching Algorithms** module. Searching is the process of locating a specific target value within a data structure.

The choice of search algorithm depends entirely on one fundamental question: **Is the data sorted?**

---

## 1. Real-World Motivation & Physical Metaphors

Imagine looking up a word in a **printed physical dictionary**:

```
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

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Linear Search** | Checking every element sequentially from index 0 to $N-1$. | Scanning a random pile of papers for a specific invoice. |
| **Binary Search** | Repeatedly checking the middle element and discarding the half that cannot contain target. | Flipping to the middle of a phonebook. |
| **Search Space** | The range of candidate indices `[low, high]` that could hold the target. | Pages 501 to 750 in a dictionary. |
| **Monotonic Function** | A function or sequence that only increases or only decreases. | Precondition for Binary Search. |

---

## 3. Technical Deep Dive: Linear vs. Binary Search

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

| Algorithm | Precondition | Time Complexity | Auxiliary Space |
| :--- | :--- | :--- | :--- |
| **Linear Search** | None (Works on any dataset) | $O(n)$ | $O(1)$ |
| **Binary Search (Iterative)** | **Data MUST be sorted** | **$O(\log n)$** | $O(1)$ |
| **Binary Search (Recursive)** | **Data MUST be sorted** | **$O(\log n)$** | $O(\log n)$ call stack |

---

## 7. Common Pitfalls & Traps

1. **Unsorted Array Failure**: Running Binary Search on an unsorted array does NOT raise an exception—it silently returns incorrect/inconsistent answers!
2. **Integer Overflow in Midpoint**: Writing `mid = (low + high) // 2` can overflow maximum 32-bit integer limits in C/Java/C++ if `low + high > 2,147,483,647`. Always write `mid = low + (high - low) // 2`.
3. **Off-by-One Loop Bounds**: Mixing up `while low <= high` vs `while low < high` causes infinite loops or skips checking boundary elements.

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: How many comparisons will Binary Search make to find a target in a sorted array of 1,000,000 elements?
   - <details><summary>Click for Answer</summary><b>Answer:</b> At most <b>20 comparisons</b> ($O(\log_2 1,000,000) \approx 19.93$).</details>

2. **Question**: Why is `mid = low + (high - low) // 2` preferred over `mid = (low + high) // 2` in typed languages like C++ and Java?
   - <details><summary>Click for Answer</summary><b>Answer:</b> If <code>low</code> and <code>high</code> are both large integers (e.g. 1.5 billion), <code>low + high</code> exceeds the maximum 32-bit signed integer limit (2.14 billion), causing integer overflow. <code>low + (high - low) // 2</code> avoids adding the two large numbers together.</details>

3. **Question**: If an array is unsorted and you only need to perform a single search query, should you sort it first to run Binary Search?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>No!</b> Sorting takes $O(n \log n)$ time plus $O(\log n)$ search time = $O(n \log n)$ total. A single Linear Search takes only $O(n)$ time. Sorting first is only worth it if you perform <b>multiple</b> search queries.</details>

---

## Related Modules
- [[04-sorting|Sorting Algorithms]] — Precondition for binary search
- [[01-algorithms|Algorithms & Complexity Analysis]] — Logarithmic bounds derivation
- [[01-trees|Trees]] — Binary Search Trees (pointer-based binary search)
