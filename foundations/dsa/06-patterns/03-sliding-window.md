# Pattern: Sliding Window

**[Intermediate]** — A university-level introduction to the sliding-window pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.
- You should know what a hash map is. See [[03-hash-maps|hash maps]] for the variant below.
- You should understand the two-pointer pattern. See [[02-two-pointers|two-pointers]] if needed.

**What you will be able to do after this lesson:**

1. Define the sliding-window pattern and explain why it turns "recompute something over every contiguous subarray/substring" from O(n·k) or O(n²) into O(n).
2. Implement fixed-size and variable-size sliding windows independently.
3. Apply the pattern to classic problems like longest substring without repeating characters and minimum window substring.
4. Explain the amortized O(n) analysis despite nested-looking loops.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're building a real-time analytics dashboard that needs to track the maximum sum of any 3-day window in a time series of stock prices. You could check every possible 3-day window:

```python
# O(n·k) naive approach
max_sum = -inf
for i in range(len(prices) - 2):
    window_sum = prices[i] + prices[i+1] + prices[i+2]
    max_sum = max(max_sum, window_sum)
```

That's fine for a single query, but a dashboard needs to answer many questions: "maximum 3-day sum," "minimum 5-day sum," "average 7-day window," etc. Each query recomputes the same sliding sums over and over.

The sliding-window pattern solves this: compute the first window's sum once, then slide it one step at a time, updating the sum by adding the new element and subtracting the element that falls out. This turns O(n·k) into O(n) — each element enters and leaves the window at most once.

Codility's course material calls this the **"caterpillar method"** — same technique (a front and back index, each only ever moving forward), different name — worth recognizing if it comes up under that label.

---

## 2. Definitions and terminology

| Term                     | Plain-English definition                                                                                                                        | Example / analogy                                                                      |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Sliding window**       | A contiguous subarray/substring that moves one element at a time, maintaining a fixed or variable size                                          | A camera panning across a scene, one pixel at a time                                   |
| **Fixed-size window**    | Window size `k` is constant; slide it one step at a time, removing the element that falls out the back and adding the one that enters the front | A 3-day moving average in finance                                                      |
| **Variable-size window** | Window grows and shrinks depending on a condition — expand the right edge to include more, shrink the left edge when a constraint is violated   | Longest substring without repeating characters                                         |
| **Amortized O(1)**       | The average cost per operation across a long sequence of calls, even though some individual operations are expensive                            | Resizing a dynamic array: most appends are O(1), but resizing is O(n) — amortized O(1) |

---

## 3. How it works — step by step

### Fixed-size window

Window size `k` is constant; slide it one step at a time:

```python
def max_subarray_sum(nums, k):
    window_sum = sum(nums[:k])  # compute first window
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # add new, drop oldest — O(1) per step
        best = max(best, window_sum)
    return best
```

**Concrete example:** `nums = [2, 1, 5, 1, 3, 2], k = 3`

```
window [2,1,5] sum=8
        ^    ^    ^
slide:  [1,5,1] sum=8-2+1=7
        ^    ^    ^
slide:  [5,1,3] sum=7-1+3=9   <- best
        ^    ^    ^
slide:  [1,3,2] sum=9-5+2=6
        ^    ^    ^
```

### Variable-size window

Window grows and shrinks depending on a condition:

```python
def length_of_longest_substring(s):
    seen = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in seen:          # constraint violated -> shrink from the left
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        best = max(best, right - left + 1)
    return best
```

Each character is added to `seen` at most once and removed at most once across the whole run — that's what keeps this O(n) despite the nested-looking `while` inside the `for`.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `sliding_window_lab.py` and run `python3 sliding_window_lab.py`. It uses only Python's standard library and creates no external files.

```python
def fixed_size_sliding_window(nums, k):
    """Maximum sum of any contiguous subarray of size k."""
    if len(nums) < k:
        return None
    window_sum = sum(nums[:k])  # compute first window
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # add new, drop oldest
        best = max(best, window_sum)
    return best


def variable_size_sliding_window(nums):
    """Length of longest subarray with all unique elements."""
    seen = set()
    left = 0
    best = 0
    for right in range(len(nums)):
        while nums[right] in seen:          # constraint violated -> shrink from the left
            seen.remove(nums[left])
            left += 1
        seen.add(nums[right])
        best = max(best, right - left + 1)
    return best


if __name__ == "__main__":
    # Test case 1: fixed-size window
    nums1 = [2, 1, 5, 1, 3, 2]
    k1 = 3
    result1 = fixed_size_sliding_window(nums1, k1)
    print(f"nums={nums1}, k={k1} -> max sum {result1}")
    assert result1 == 9, f"Expected 9, got {result1}"

    # Test case 2: variable-size window
    nums2 = [1, 2, 3, 1, 2, 3, 1]
    result2 = variable_size_sliding_window(nums2)
    print(f"nums={nums2} -> longest unique substring length {result2}")
    assert result2 == 3, f"Expected 3, got {result2}"

    # Test case 3: edge case - all unique
    nums3 = [1, 2, 3, 4, 5]
    result3 = variable_size_sliding_window(nums3)
    print(f"nums={nums3} -> longest unique substring length {result3}")
    assert result3 == 5, f"Expected 5, got {result3}"

    print("sliding_window_lab: passed")
```

Expected output:

```
nums=[2, 1, 5, 1, 3, 2], k=3 -> max sum 9
nums=[1, 2, 3, 1, 2, 3, 1] -> longest unique substring length 3
nums=[1, 2, 3, 4, 5] -> longest unique substring length 5
sliding_window_lab: passed
```

---

## 5. Why it's O(n) despite nested-looking loops

The key insight: **each element enters and leaves the window at most once across the entire run.**

- In fixed-size windows, each element is added once (when it enters the window) and removed once (when it leaves the window).
- In variable-size windows, each element is added to `seen` at most once and removed at most once.

This means the total number of operations is bounded by `2n`, not `n²`. The same amortized argument as [[02-dynamic-arrays|dynamic array resizing]]: the loop looks nested, but the total work across the whole run is linear.

---

## 6. Related patterns and extensions

### Sliding window maximum (harder variant)

Fixed window where the aggregate _isn't_ invertible, so it needs a [[06-monotonic-stack|monotonic]] deque instead of the add-one-drop-one update:

```python
def sliding_window_maximum(nums, k):
    from collections import deque
    dq = deque()  # stores indices, values decreasing
    result = []
    for i, num in enumerate(nums):
        # remove indices out of window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # maintain decreasing order
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

### Minimum window substring (harder variant)

```python
def min_window_substring(s, t):
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = 0
    min_len = float('inf')
    min_start = 0
    for right, ch in enumerate(s):
        if ch in need:
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1
        while missing == 0:  # window satisfies t
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_start = left
            left_ch = s[left]
            if left_ch in need:
                need[left_ch] += 1
                if need[left_ch] > 0:
                    missing += 1
            left += 1
    return s[min_start:min_start + min_len] if min_len != float('inf') else ""
```

---

## 7. Tradeoffs and limitations

- **Fixed-size windows only work for invertible operations.** The add-one-drop-one update assumes you can compute the new sum from the old sum, the new element, and the element that fell out. For non-invertible aggregates (max, min, median), you need a different data structure (deque, heap, etc.).
- **Variable-size windows need careful condition handling.** The `while` loop inside the `for` can be confusing; understanding why it's still O(n) is key.
- **Not all contiguous subarray problems fit this pattern.** Some problems require checking every possible window (e.g., "find all subarrays with sum equals k") — prefix sums are better there.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `nums = [1, 2, 3, 1, 2, 3, 1]` and `k = 3`, trace through the fixed-size sliding window algorithm step by step.
2. **Question:** Why is the variable-size sliding window algorithm O(n) despite the nested-looking `while` loop?
3. **Question:** What happens if the input contains negative numbers? Does the fixed-size sliding window still work?

### Answers — after your attempt

1. `window [1,2,3] sum=6` -> `window [2,3,1] sum=6-1+1=6` -> `window [3,1,2] sum=6-2+2=6` -> `window [1,2,3] sum=6-3+3=6` -> `window [2,3,1] sum=6-1+1=6`. Maximum is 6.
2. Each element is added to `seen` at most once and removed at most once across the entire run. The total number of additions and removals is bounded by `2n`, so the total work is O(n) even though there's a nested-looking loop.
3. Yes, the fixed-size sliding window still works with negative numbers. The add-one-drop-one update is still valid: `new_sum = old_sum - nums[i-k] + nums[i]`. The algorithm doesn't assume positivity.

---

## 9. Practice — independent task

**Task:** Implement a function `longest_substring_without_repeating(s)` that returns the length of the longest substring without repeating characters. Use the variable-size sliding window pattern. Test it with the following cases:

- `s = "abcabcbb"` → expected `3` (substring "abc")
- `s = "bbbbb"` → expected `1` (substring "b")
- `s = "pwwkew"` → expected `3` (substring "wke")

**Done when:** your function returns the correct lengths for all test cases.

---

## 10. Related

- [[02-two-pointers|two-pointers]] — sliding window is a specialization where both pointers move in the same direction
- [[03-hash-maps|hash maps]] — used in variable-size windows for fast membership testing
- [[06-monotonic-stack|monotonic-stack]] — alternative for sliding window maximum
- [[01-algorithms|algorithms]] — where the amortized O(n) framing comes from
- [[03-sliding-window|sliding-window]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Time series analysis:** moving averages, rolling statistics
- **Network traffic monitoring:** bandwidth usage over sliding time windows
- **Genomics:** sliding window alignment in sequence analysis
- **Financial engineering:** risk calculations over rolling periods

The core idea — maintain a summary of the current window and update it incrementally — is a fundamental algorithmic technique that appears whenever you need to process data in chunks that slide across a larger dataset.
