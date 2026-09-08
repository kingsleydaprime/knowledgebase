# Contains Duplicate (LeetCode 217)

Welcome to the **Arrays & Hashing** series. In this module, we explore the core building blocks of array manipulation and lookup optimization.

---

## 1. Why Study "Contains Duplicate"? (Real-World Motivation)

Before looking at code, let's understand why tracking duplicate data is fundamental to software systems.

### The Problem in Practice

In system design, verifying uniqueness is a frequent requirement:

* **Database Constraints**: Checking if a newly entered username or email address already exists.
* **Data Ingestion**: Filtering out duplicate streaming events before writing to storage.
* **Fraud Detection**: Spotting rapid duplicate transaction attempts across an account.

### The Foundational Tradeoff

This problem serves as the primary example of the **time-space tradeoff**:

* **Naive Approach**: Minimal extra memory, but slow searching ($O(n^2)$ time).
* **Optimal Approach**: Sacrificing extra memory ($O(n)$ space) to make search operations instant ($O(1)$ time).

---

## 2. Problem Statement

Given an integer array `nums`, return `true` if any value appears **at least twice** in the array, and return `false` if every element is distinct.

### Examples

```
Input:  nums = [1, 2, 3, 1]
Output: true
Explanation: The element 1 appears twice (at index 0 and index 3).

Input:  nums = [1, 2, 3, 4]
Output: false
Explanation: All elements are distinct.

```

---

## 3. Approaches & Step-by-Step Solutions

We will analyze three distinct ways to solve this problem, moving from naive to optimal.

```
       [1, 2, 3, 1]
            │
            ├─► Approach 1: Brute Force (Compare all pairs) ───► O(n²) Time  │ O(1) Space
            ├─► Approach 2: Sort then Scan ────────────────────► O(n log n)  │ O(1) Space
            └─► Approach 3: Hash Set Lookup (Optimal) ────────► O(n) Time    │ O(n) Space

```

---

### Approach 1: Brute Force (Nested Loops)

#### Intuition & Mechanics

Compare every single element against every other element in the array using two nested loops. If a pair of matching values is encountered, return `true`.

#### Python Implementation

```python
def containsDuplicate(nums: list[int]) -> bool:
    """Brute-force approach: Compares every element against every other element."""
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] == nums[j]:
                return True
    return False

```

#### Complexity Analysis

* **Time Complexity**: $O(n^2)$ — For an array of size $n$, the total comparisons made equal $\frac{n(n-1)}{2}$. For $n = 10^4$, this requires approximately $5 \times 10^7$ operations, causing a **Time Limit Exceeded (TLE)** error on larger inputs.
* **Space Complexity**: $O(1)$ — Requires no additional memory allocations.

---

### Approach 2: Sorting First

#### Intuition & Mechanics

By sorting the array first, identical elements are brought together into adjacent positions. A single linear pass through the sorted array is then sufficient to detect duplicates.

#### Python Implementation

```python
def containsDuplicate(nums: list[int]) -> bool:
    """Sorting approach: Brings duplicates together side-by-side."""
    # Step 1: Sort the array in-place
    nums.sort()
    
    # Step 2: Perform a single pass to check adjacent elements
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1]:
            return True
            
    return False

```

#### Complexity Analysis

* **Time Complexity**: $O(n \log n)$ — Dominated by the sorting algorithm (e.g., Timsort in Python).
* **Space Complexity**: $O(1)$ or $O(n)$ — Memory usage depends on the language implementation. Mutating the input directly allows for $O(1)$ space, but sorting alters the original input ordering.

---

### Approach 3: Hash Set Lookup (Optimal)

#### Intuition & Mechanics

To optimize search speed, we introduce a **Hash Set**. As we iterate through the array, we ask a key question: *"Have I seen this number before?"*

* If the number is already present in our set, a duplicate exists.
* If it is not present, we add the number to the set and proceed.

Since hash set lookups and insertions operate in $O(1)$ average time, the overall processing time is drastically reduced.

#### Visual Walkthrough

```
Processing array: [1, 2, 3, 1]

Step 1: Element = 1 | Set = {}        | 1 in Set? False -> Add 1 -> Set = {1}
Step 2: Element = 2 | Set = {1}       | 2 in Set? False -> Add 2 -> Set = {1, 2}
Step 3: Element = 3 | Set = {1, 2}    | 3 in Set? False -> Add 3 -> Set = {1, 2, 3}
Step 4: Element = 1 | Set = {1, 2, 3} | 1 in Set? TRUE  -> Return True!

```

#### Python Implementation

```python
def containsDuplicate(nums: list[int]) -> bool:
    """Optimal approach: Uses a Hash Set for instantaneous lookup."""
    seen = set()
    for n in nums:
        if n in seen:        # O(1) average lookup time
            return True
        seen.add(n)          # O(1) average insertion time
    return False

```

> [!TIP]
> **One-Liner Alternative**: Python allows checking if unique elements equal the array length via `return len(set(nums)) != len(nums)`. While concise, this constructs the entire set in memory upfront ($O(n)$ space always), whereas the loop approach allows **early termination** as soon as the first duplicate is found.

#### Complexity Analysis

* **Time Complexity**: $O(n)$ — A single linear pass through the array with average $O(1)$ hash set operations.
* **Space Complexity**: $O(n)$ — In the worst-case scenario (all elements unique), the hash set holds $n$ elements.

---

## 4. Summary of Complexity

| Approach | Time Complexity | Space Complexity | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Brute Force** | $O(n^2)$ | $O(1)$ | Zero extra memory usage | Inefficient; fails on large datasets |
| **Sort + Scan** | $O(n \log n)$ | $O(1)^*$ | No additional dynamic data structure required | Mutates input order; sub-optimal execution speed |
| **Hash Set (Optimal)** | **$O(n)$** | **$O(n)$** | Fastest execution speed; stops early on duplicates | Requires additional memory allocation |

* *Assuming in-place sorting and ignoring language runtime stack space.*

---

## 5. Key Concept Takeaway

> **Pattern Recognition**: Whenever a problem asks *"Have I seen this element before?"* or requires identifying duplicate occurrences, utilize a **Hash Set** or **Hash Map**.
> Converting a nested search ($O(n)$ inner step) into a key-value/set lookup ($O(1)$ inner step) is the foundational pattern behind optimized array algorithms.

---

## 6. Self-Assessment Questions

1. **Question**: If memory constraints are severe and you are allowed to modify the input array, which approach should you select and why?

2. **Question**: Why is `len(set(nums)) != len(nums)` potentially less efficient in practice than iterating with a `for` loop, despite having the same theoretical asymptotic time complexity?


---

## Related

* Concept: [[03-hash-maps|Hash Maps & Sets]]
* Next: [[002-valid-anagram|Valid Anagram]] — Transitioning from basic set membership to key-value frequency tracking
* Patterns: [[009-longest-consecutive-sequence|Longest Consecutive Sequence]] and [[008-valid-sudoku|Valid Sudoku]]