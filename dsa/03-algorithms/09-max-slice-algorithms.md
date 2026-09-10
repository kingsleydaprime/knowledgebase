# Module: Maximum Slice Problem — Kadane's Algorithm

Welcome to the **Maximum Slice** module. The problem: given a sequence of integers (which may include negative numbers), find the **contiguous subarray (slice)** with the largest possible sum.

This is one of the most elegant problems in computer science, illustrating how a **dynamic programming insight** can slash a naïve $O(n^3)$ solution all the way down to a single-pass $O(n)$ algorithm.

---

## Before you start

- You can reason about prefix sums — [[04-patterns/01-prefix-sum|prefix sum]].
- You know what $O(n^2)$ and $O(n)$ mean in practice — [[01-algorithms|complexity analysis]].

**After this lesson you will be able to:**

1. Implement **Kadane's algorithm** in one pass and explain its single decision.
2. Handle the **all-negative** case correctly — the edge case most implementations get wrong.
3. Return the slice **indices**, not just the sum.
4. Explain why Kadane's is simultaneously a greedy algorithm and a dynamic program.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 3 is the edge case.

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

## Implementation — complete runnable example

**Runnable example:** save as `max_slice.py` in any empty directory and run `python3 max_slice.py`. Standard library only; writes no files.

```python
"""Kadane's algorithm: one pass, one decision, and the edge case that breaks it."""
import random


def brute_force(xs):
    """Every slice, exhaustively. O(n^2) - the oracle."""
    if not xs:
        return None, None, None
    best = float("-inf")
    bi = bj = 0
    for i in range(len(xs)):
        total = 0
        for j in range(i, len(xs)):
            total += xs[j]
            if total > best:
                best, bi, bj = total, i, j
    return best, bi, bj


def kadane_broken(xs):
    """The version you will find in half the tutorials. It has a bug."""
    best = 0                                   # BUG: assumes the answer is never negative
    current = 0
    for v in xs:
        current = max(0, current + v)
        best = max(best, current)
    return best


def kadane(xs):
    """Correct for all inputs, including all-negative. Returns (sum, start, end)."""
    if not xs:
        return None, None, None
    best = current = xs[0]
    bi = bj = ci = 0
    for j in range(1, len(xs)):
        v = xs[j]
        # THE decision: extend the running slice, or start fresh here?
        if current + v >= v:
            current = current + v
        else:
            current, ci = v, j
        if current > best:
            best, bi, bj = current, ci, j
    return best, bi, bj


def max_slice_prefix(xs):
    """The same answer via prefix sums: best[j] = prefix[j] - min prefix before j."""
    if not xs:
        return None
    best = float("-inf")
    running = 0
    min_prefix = 0
    for j, v in enumerate(xs):
        running += v
        if j == 0:
            best = v
            min_prefix = min(0, running)
            continue
        best = max(best, running - min_prefix)
        min_prefix = min(min_prefix, running)
    return best


if __name__ == "__main__":
    print("Block 1 - the running decision, traced")
    xs = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    print(f"  input {xs}")
    print("     j   value   extend?   current   best")
    best = current = xs[0]
    for j in range(1, len(xs)):
        v = xs[j]
        extend = current + v >= v
        current = current + v if extend else v
        best = max(best, current)
        print(f"    {j:2}   {v:5}   {str(extend):7}   {current:7}   {best:4}")
    total, i, j = kadane(xs)
    print(f"  answer {total} from index {i} to {j}: {xs[i:j+1]}")
    assert (total, i, j) == (6, 3, 6)

    print()
    print("Block 2 - checked against exhaustive search")
    rng = random.Random(20260910)
    for _ in range(3000):
        n = rng.randint(1, 25)
        arr = [rng.randint(-15, 15) for _ in range(n)]
        k_sum, ki, kj = kadane(arr)
        b_sum, _, _ = brute_force(arr)
        assert k_sum == b_sum, (arr, k_sum, b_sum)
        assert sum(arr[ki:kj + 1]) == k_sum, "the returned indices must produce the sum"
    print("  3,000 random arrays: sum matches brute force, and the indices are valid")

    print()
    print("Block 3 - the all-negative case, where the common version fails")
    cases = [[-2, -3, -1, -5], [-7], [-1, -1], [3, -1, 2], [0, -1]]
    print("     input             correct   'max(0, ...)' version")
    for arr in cases:
        good, _, _ = kadane(arr)
        bad = kadane_broken(arr)
        flag = "" if good == bad else "   <-- WRONG"
        print(f"   {str(arr):18} {good:8}   {bad:19}{flag}")
    assert kadane([-2, -3, -1, -5])[0] == -1
    assert kadane_broken([-2, -3, -1, -5]) == 0
    print("  the broken version returns 0 by choosing the EMPTY slice.")
    print("  Whether that is right depends on the problem statement: if a slice must")
    print("  be non-empty, 0 is wrong and the answer is the largest single element.")
    print("  Read the constraints - this is a specification question, not a bug in")
    print("  Kadane's, and it is the most common way this problem is failed.")

    print()
    print("Block 4 - the same answer, three ways")
    for arr in ([-2, 1, -3, 4, -1, 2, 1, -5, 4], [1, 2, 3], [-5, -2, -8]):
        k, _, _ = kadane(arr)
        b, _, _ = brute_force(arr)
        p = max_slice_prefix(arr)
        print(f"  {str(arr):32} kadane {k:4}  brute {b:4}  prefix-sum {p:4}")
        assert k == b == p
    print("  the prefix-sum view: the best slice ending at j is prefix[j] minus the")
    print("  SMALLEST prefix before j - so track the running minimum instead of an array.")
    print("  Kadane's is that idea with the bookkeeping folded away.")

    print()
    print("Block 5 - why it is greedy AND dynamic programming")
    print("   DP framing:     best_ending_here[j] = max(xs[j], best_ending_here[j-1] + xs[j])")
    print("                   answer = max over j")
    print("   greedy framing: if the running total is not helping, abandon it")
    print("   they are the same rule. The DP table has one row and each entry depends")
    print("   only on the previous, so it collapses to a single variable - which is")
    print("   what makes it O(1) space.")
    n = 200000
    big = [rng.randint(-50, 50) for _ in range(n)]
    total, i, j = kadane(big)
    print(f"  {n:,} elements: best slice sum {total:,} spanning indices {i:,}..{j:,}")
    assert sum(big[i:j + 1]) == total
    print("  one pass, two variables, no allocation")

    print()
    print("max_slice: passed")
```

Expected output:

```
Block 1 - the running decision, traced
  input [-2, 1, -3, 4, -1, 2, 1, -5, 4]
     j   value   extend?   current   best
     1       1   False           1      1
     2      -3   True           -2      1
     3       4   False           4      4
     4      -1   True            3      4
     5       2   True            5      5
     6       1   True            6      6
     7      -5   True            1      6
     8       4   True            5      6
  answer 6 from index 3 to 6: [4, -1, 2, 1]

Block 2 - checked against exhaustive search
  3,000 random arrays: sum matches brute force, and the indices are valid

Block 3 - the all-negative case, where the common version fails
     input             correct   'max(0, ...)' version
   [-2, -3, -1, -5]         -1                     0   <-- WRONG
   [-7]                     -7                     0   <-- WRONG
   [-1, -1]                 -1                     0   <-- WRONG
   [3, -1, 2]                4                     4
   [0, -1]                   0                     0
  the broken version returns 0 by choosing the EMPTY slice.
  Whether that is right depends on the problem statement: if a slice must
  be non-empty, 0 is wrong and the answer is the largest single element.
  Read the constraints - this is a specification question, not a bug in
  Kadane's, and it is the most common way this problem is failed.

Block 4 - the same answer, three ways
  [-2, 1, -3, 4, -1, 2, 1, -5, 4]  kadane    6  brute    6  prefix-sum    6
  [1, 2, 3]                        kadane    6  brute    6  prefix-sum    6
  [-5, -2, -8]                     kadane   -2  brute   -2  prefix-sum   -2
  the prefix-sum view: the best slice ending at j is prefix[j] minus the
  SMALLEST prefix before j - so track the running minimum instead of an array.
  Kadane's is that idea with the bookkeeping folded away.

Block 5 - why it is greedy AND dynamic programming
   DP framing:     best_ending_here[j] = max(xs[j], best_ending_here[j-1] + xs[j])
                   answer = max over j
   greedy framing: if the running total is not helping, abandon it
   they are the same rule. The DP table has one row and each entry depends
   only on the previous, so it collapses to a single variable - which is
   what makes it O(1) space.
  200,000 elements: best slice sum 18,620 spanning indices 44,619..190,562
  one pass, two variables, no allocation

max_slice: passed
```

Block 3 is the one that matters. `max(0, ...)` silently answers a *different question* — "the best slice, or the empty one" — and whether that is correct depends entirely on the problem statement.

## 6. Check Your Understanding (University Self-Assessment)

1. **Question**: Why does Kadane's algorithm reset `max_ending_here` to 0 (not to `A[i]`) when the running sum goes negative?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The problem allows the empty slice (sum = 0) as a valid baseline answer. Resetting to 0 is equivalent to saying "start a fresh subarray from the next element." Resetting to <code>A[i]</code> would force us to include at least one element, changing the problem definition.</details>

2. **Question**: What is the relationship between `max_ending_here` and the concept of a DP subproblem?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>max_ending_here</code> represents the optimal solution to the subproblem "what is the maximum sum subarray ending exactly at position i?" The solution at position <code>i</code> is computed directly from position <code>i-1</code>, following the DP recurrence.</details>

3. **Question**: On an all-negative array `[-5, -3, -8, -1]`, what does Kadane's algorithm return?
   - <details><summary>Click for Answer</summary><b>Answer:</b> It returns <b>0</b> (the empty slice sum), because <code>max_ending_here</code> resets to 0 at every step since every element is negative.</details>

---

## Practice — independent task

Extend Kadane's to the **maximum sum rectangle** in a 2-D grid.

1. Fix a pair of rows, top and bottom. Collapse the columns between them into a 1-D array of column sums, then run Kadane's on it. The best rectangle for that row pair is the best slice of that array.
2. Repeat over all $O(R^2)$ row pairs. Total cost $O(R^2 C)$.
3. Return the rectangle's **coordinates** as well as its sum, and verify by summing the region directly.
4. Check against a brute force over all $O(R^2C^2)$ rectangles on grids up to $6\times6$.
5. **Then optimise the collapse.** Recomputing column sums for each row pair is $O(RC)$ per pair, giving $O(R^3C)$. Maintain a running column-sum array as the bottom row advances instead, restoring $O(R^2C)$. Measure the difference at $R = C = 120$ and report the ratio.

**Edge cases:** an all-negative grid (the same specification question as block 3 — decide and document); a single row; a single column; a $1\times1$ grid.

**Done when:** your coordinates reproduce the reported sum, brute force agrees on every small grid, and your step-5 optimisation shows the speed-up you predicted.

## Before moving on

You can implement Kadane's, return indices, handle all-negative input, and explain the DP/greedy duality.

**Recap:** at each element, either extend the running slice or start fresh — whichever is larger; $O(n)$ time, $O(1)$ space; initialise with `xs[0]`, **not** 0, unless the empty slice is explicitly allowed; return indices by tracking where the current slice started; equivalently, the best slice ending at $j$ is $\text{prefix}[j]$ minus the smallest earlier prefix.

**Next:** [[13-bit-manipulation|Bit Manipulation]], or back to [[index|the algorithms index]].

## Related Modules
- [[01-algorithms|Algorithms & Complexity Analysis]] — Recurrence derivation and notation
- [[04-sorting/index|Sorting Algorithms]] — $O(n \log n)$ sort-first approaches
