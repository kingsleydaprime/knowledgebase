# Module: Maximum Slice Problem — Kadane's Algorithm

Welcome to the **Maximum Slice** module. The problem: given a sequence of integers (which may include negative numbers), find the **contiguous subarray (slice)** with the largest possible sum.

This is one of the most elegant problems in computer science, illustrating how a **dynamic programming insight** can slash a naïve $O(n^3)$ solution all the way down to a single-pass $O(n)$ algorithm.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine you're a **Stock Day Trader** analyzing daily profit/loss figures:

```
Day:     1    2    3    4    5    6    7    8
PnL:   -2   +3   +4   -1   +5   -8   +4   +1

Best trading window:  Days 2 through 6
  Sum = 3 + 4 + (-1) + 5 = 11  ← Maximum subarray sum!
```

You want to find the contiguous window of days that maximizes your cumulative profit.

### Real-World Applications:
1. **Financial Analysis**: Finding the optimal holding window for a stock position.
2. **Signal Processing**: Isolating the highest-amplitude segment of a noisy signal.
3. **Genomics**: Identifying the highest-density gene sequence region in a DNA strand.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Analogy |
| :--- | :--- | :--- |
| **Subarray / Slice** | A contiguous block of elements within the array. | A date range window on a calendar. |
| **`max_ending_here`** | The maximum sum achievable by any subarray that ends exactly at the current position. | Best P&L for any trade window ending today. |
| **`max_so_far`** | The global running maximum found across all positions so far. | The best trade window discovered at any point in history. |
| **Kadane's Algorithm** | A linear-time DP algorithm maintaining the best suffix subarray sum at each step. | Day-by-day profit tracking with automatic "cut your losses" reset. |

---

## 3. Three Solutions: Naïve → Optimal

### Approach 1: Brute Force ($O(n^3)$)

Check every possible slice `[p, q]` and sum each from scratch:

```python
def max_slice_brute(A: list) -> int:
    """O(n³): Checks every possible subarray and recomputes its sum."""
    n = len(A)
    result = 0
    for p in range(n):
        for q in range(p, n):
            result = max(result, sum(A[p:q + 1]))  # O(n) inner sum
    return result
```

**Why slow**: $O(n^2)$ possible subarrays, each summed in $O(n)$ → **$O(n^3)$ total**.

---

### Approach 2: Running Sum ($O(n^2)$)

Maintain a running sum for a fixed starting index `p`. When we move `q` forward by one, we extend the running sum by one addition instead of recomputing from scratch:

```python
def max_slice_quadratic(A: list) -> int:
    """O(n²): Eliminates redundant re-summing with a running total."""
    n = len(A)
    result = 0
    for p in range(n):
        running_sum = 0
        for q in range(p, n):
            running_sum += A[q]     # O(1) extension instead of O(n) re-sum
            result = max(result, running_sum)
    return result
```

---

### Approach 3: Kadane's Algorithm ($O(n)$, $O(1)$ Space)

> [!KEY-INSIGHT]
> **The Recurrence**: The best subarray ending at position $i$ is either:
> 1. The best subarray ending at position $i-1$, extended by one element (`max_ending_here + A[i]`), OR
> 2. Start a brand new subarray at position $i$ alone (`A[i]`)
> 
> In other words: **if carrying the negative baggage of a prior run makes things worse than starting fresh, cut and restart.**

```python
def max_slice_kadane(A: list) -> int:
    """O(n) time, O(1) space: Kadane's Algorithm."""
    max_ending_here = 0  # Best sum for subarrays ending AT current index
    max_so_far = 0       # Best sum found ANYWHERE so far
    
    for value in A:
        # Either extend the previous best suffix, or reset to 0 (empty slice)
        max_ending_here = max(0, max_ending_here + value)
        max_so_far = max(max_so_far, max_ending_here)
        
    return max_so_far
```

**Walkthrough on `[-2, 3, 4, -1, 5, -8, 4, 1]`:**
```
Value:           -2    3    4   -1    5   -8    4    1
max_ending_here:  0    3    7    6   11    3    7    8
max_so_far:       0    3    7    7   11   11   11   11

→ Maximum subarray sum = 11
```

The `max(0, ...)` is the key: by resetting to 0, we allow starting a completely new subarray from the next element, which is equivalent to "allowing the empty slice" as a baseline.

---

## 4. Why Kadane's is Dynamic Programming

Kadane's algorithm is a minimal, single-variable form of **Dynamic Programming**:

| DP Characteristic | Kadane's Algorithm |
| :--- | :--- |
| **Subproblem definition** | `max_ending_here[i]` = best subarray sum ending at index `i`. |
| **Recurrence relation** | `max_ending_here[i] = max(0, max_ending_here[i-1] + A[i])` |
| **Optimal substructure** | Global answer built from optimal answers to smaller problems. |
| **Space optimization** | Only the immediately previous subproblem value is ever needed → $O(1)$ space. |

---

## 5. Complexity Summary

| Approach | Time | Space | Key Idea |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(n^3)$ | $O(1)$ | Re-sum every subarray from scratch. |
| **Running Sum** | $O(n^2)$ | $O(1)$ | Extend running sum instead of re-summing. |
| **Kadane's Algorithm** | **$O(n)$** | **$O(1)$** | DP recurrence: extend or reset. |

---

## 6. Check Your Understanding (University Self-Assessment)

1. **Question**: Why does Kadane's algorithm reset `max_ending_here` to 0 (not to `A[i]`) when the running sum goes negative?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The problem allows the empty slice (sum = 0) as a valid baseline answer. Resetting to 0 is equivalent to saying "start a fresh subarray from the next element." Resetting to <code>A[i]</code> would force us to include at least one element, changing the problem definition.</details>

2. **Question**: What is the relationship between `max_ending_here` and the concept of a DP subproblem?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>max_ending_here</code> represents the optimal solution to the subproblem "what is the maximum sum subarray ending exactly at position i?" The solution at position <code>i</code> is computed directly from position <code>i-1</code>, following the DP recurrence.</details>

3. **Question**: On an all-negative array `[-5, -3, -8, -1]`, what does Kadane's algorithm return?
   - <details><summary>Click for Answer</summary><b>Answer:</b> It returns <b>0</b> (the empty slice sum), because <code>max_ending_here</code> resets to 0 at every step since every element is negative.</details>

---

## Related Modules
- [[01-algorithms|Algorithms & Complexity Analysis]] — Recurrence derivation and notation
- [[04-sorting|Sorting Algorithms]] — $O(n \log n)$ sort-first approaches
