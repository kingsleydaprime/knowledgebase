# Pattern: Prefix Sum

Welcome to the **Arrays & Preprocessing** module. Computing running aggregates over sequential data is a core algorithmic technique. In this module, we explore the **Prefix Sum** pattern—a technique that trades a single preprocessing pass to answer range-aggregate queries in constant time.

---

## 1. Why Do We Need Prefix Sums? (Real-World Motivation)

Before diving into formal equations, let's understand why recalculating running sums iteratively is inefficient.

### The Problem in Practice

Imagine building a revenue dashboard for an e-commerce platform with several years of daily transaction data ($n \approx 1,000+$ days):

* **Interactive Queries**: A user drags a timeline slider asking: *"What was total revenue from Day 2 to Day 5?"*

* **Repeated Calculations**: Every dashboard load, cohort chart, and automated report repeatedly calculates sums over various arbitrary date windows.



Iterating through array slices for every incoming query requires $O(k)$ operations per query (where $k$ is the range length). If $q$ queries are executed, performance degrades to $O(q \cdot n)$ total time.

### The Core Idea: The Bank Statement Analogy

A bank account statement does not record pure isolated movements to display your month-end total; it tracks your **running balance** after every single transaction.

* To calculate net balance spent between **June 1** and **June 30**, you subtract the running balance on **June 1** from the running balance on **June 30**.


* **That single subtraction is the entire Prefix Sum pattern**.



```text
Day:              0      1      2      3      4       5
Daily Revenue:   120    340     90    210    400     150
Prefix Sums:     120    460    550    760   1160    1310   <-- Running totals

Revenue for Days 2 to 5:
  Total through Day 5  = 1310
- Total through Day 1  =  460
-----------------------------
  Revenue (Days 2..5)  =  850   (90 + 210 + 400 + 150 = 850)

```

---

## 2. Real-World Applications

The Prefix Sum algorithm is fundamental infrastructure across computer science:

1. **Databases & Analytics**: SQL window functions like `SUM(val) OVER (ORDER BY date)` pre-compute cumulative totals for streaming dashboard rollups.


2. **Computer Vision (Integral Images)**: 2D prefix sums (Summed-Area Tables) allow image filters (like Box Blurs) and real-time object detection algorithms to compute pixel intensity sums across any rectangular region in $O(1)$ time.


3. **Weighted Random Selection**: Games and ad servers use prefix sums of weights (`[5, 1, 3] -> [5, 6, 9]`) paired with binary search to sample weighted random choices in $O(\log n)$ time.


4. **GPU & Parallel Computing**: Known as the **Parallel Scan** primitive, prefix sums are used in stream compaction, radix sorting, and dynamic GPU memory allocation.



---

## 3. How It Works (1D Implementation & Sentinel Trick)

To implement a prefix sum array $P$, each element $P[i]$ represents the sum of all array elements up to index $i$.

### The Sentinel Boundary Trick

Adding a leading `0` (a **sentinel value**) at index `0` of the prefix array simplifies boundary checks. It handles queries that begin at index `0` without requiring conditional `if i == 0` statements.

```text
Original Array (A):      [ 1,  2,  3,  4,  5,  6 ]
Prefix Array   (P):   [0, 1,  3,  6, 10, 15, 21 ]
                       ^
                   Sentinel (Sum of empty prefix)

```

### Python Implementation

```python
def build_prefix_sums(nums: list[int]) -> list[int]:
    """Precomputes prefix sums with a leading 0 sentinel."""
    prefix = [0] * (len(nums) + 1)
    for i, num in enumerate(nums):
        prefix[i + 1] = prefix[i] + num
    return prefix

def range_sum(prefix: list[int], left: int, right: int) -> int:
    """Returns the sum of elements from index `left` to `right` inclusive in O(1) time."""
    return prefix[right + 1] - prefix[left]
```

---

## 4. The 2D Version: Summed-Area Tables

The prefix sum concept extends to 2D grids. Each coordinate $S[r][c]$ stores the sum of all elements in the rectangle from top-left $(0, 0)$ to bottom-right $(r, c)$.

```text
┌───────────────┬───────────────┐
│               │               │
│   S[r1-1]     │               │
│   [c1-1]      │  Top Strip    │
│  (Overlapping)│               │
├───────────────┼───────────────┤
│               │  Target       │
│  Left Strip   │  Sub-Grid     │
│               │ (r1,c1)..(r2,c2)
└───────────────┴───────────────┘
```

### Mathematical Formulas

1. **Construction Formula**:
   $$S[r][c] = \text{grid}[r][c] + S[r-1][c] + S[r][c-1] - S[r-1][c-1]$$

2. **Range Query Formula (Inclusion-Exclusion Principle)**:
   $$\text{Sum} = S[r_2][c_2] - S[r_1-1][c_2] - S[r_2][c_1-1] + S[r_1-1][c_1-1]$$


---

## 5. The Hash-Map Variant: "Subarray Sum Equals K"

Standard prefix sums answer *"What is the sum of range $[i, j]$?"* The inverse problem asks: *"Does any subarray sum to a target value $k$?"*

### Algebraic Transformation
A subarray between index $i$ and $j$ sums to $k$ if:

$$\text{prefix}[j] - \text{prefix}[i] = k \implies \text{prefix}[i] = \text{prefix}[j] - k$$


While traversing the array, if we maintain a **Hash Map** tracking the frequency of previously seen prefix sums, we can check whether $\text{running\_sum} - k$ exists in $O(1)$ time.

```python
def subarray_sum(nums: list[int], k: int) -> int:
    """Finds total number of continuous subarrays whose sum equals k."""
    seen = {0: 1}  # Seed map with 0 sum to handle subarrays starting at index 0
    running_sum = 0
    count = 0
    
    for num in nums:
        running_sum += num
        # If (running_sum - k) was seen before, it completes a target subarray ending here
        count += seen.get(running_sum - k, 0)
        seen[running_sum] = seen.get(running_sum, 0) + 1
        
    return count
```

---

## 6. Important Tradeoffs & Failure Modes

- **Invertibility Requirement**: Prefix operations require mathematical **invertibility** (e.g., addition/subtraction or XOR). Non-invertible operations like `max()` or `min()` **cannot** use prefix subtraction, as knowing $\max(A[0..5])$ and $\max(A[0..1])$ gives no information about $\max(A[2..5])$.
- **Dynamic Updates**: Modifying a single element in the original array invalidates all subsequent entries in the prefix array, requiring an $O(n)$ rebuild. For frequent dynamic updates, use a **Binary Indexed Tree (Fenwick Tree)** or a **Segment Tree** ($O(\log n)$ update/query time).
- **Single-Query Overhead**: If you only need to process a single range query once, building a prefix array adds unnecessary $O(n)$ space memory overhead.

---

## 7. Summary of Complexity

| Operation | Standard Iterative Search | Prefix Sum Approach | Segment / Fenwick Tree |
| :--- | :--- | :--- | :--- |
| **Preprocessing Time** | $O(1)$ | **$O(n)$** | $O(n)$ |
| **Range Query Time** | $O(n)$ | **$O(1)$** | $O(\log n)$ |
| **Single-Element Update** | $O(1)$ | $O(n)$ *(Invalidates array)* | **$O(\log n)$** |
| **Auxiliary Space** | $O(1)$ | **$O(n)$** | $O(n)$ |

---

## 8. Check Your Understanding (Self-Assessment)

1. **Question**: Why do we place a `0` sentinel value at the beginning of a prefix sum array?
   * <details><summary>Click for Answer</summary><b>Answer:</b> The sentinel eliminates edge cases for range queries starting at index 0. It ensures <code>range_sum(left, right)</code> works uniformly via <code>prefix[right + 1] - prefix[left]</code> without needing conditional branch statements.</details>

2. **Question**: Can you use the prefix subtraction technique to answer range-maximum queries in $O(1)$ time?
   * <details><summary>Click for Answer</summary><b>Answer:</b> <b>No</b>. Maximum operations are non-invertible—you cannot "subtract" or invert a maximum value from an aggregate to determine the max of a sub-window. Range-maximum queries require data structures like Sparse Tables or Segment Trees.</details>

3. **Question**: How does a Hash Map convert the $O(n^2)$ search for subarrays summing to $k$ into an $O(n)$ algorithm?
   * <details><summary>Click for Answer</summary><b>Answer:</b> By rewriting the condition $\text{prefix}[j] - \text{prefix}[i] = k$ into $\text{prefix}[i] = \text{prefix}[j] - k$, the problem reduces to looking up if a specific prior prefix value exists in a hash map in $O(1)$ average time.</details>

---

## Related
* [[01-arrays|Arrays]] — Underlying contiguous memory storage
* [[03-hash-maps|Hash Maps]] — Key lookup mechanism for subarray target problems
* [[03-sliding-window|Sliding Window]] — Alternative technique for contiguous subarray problems without negative values
* [[007-product-of-array-except-self|Product of Array Except Self]] — Multiplicative prefix/suffix array pattern

```