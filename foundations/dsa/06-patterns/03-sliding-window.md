# Pattern: Sliding Window

A specialization of [[02-two-pointers|two-pointers]] where both pointers move in the same direction, maintaining a contiguous "window" over the data instead of converging from opposite ends. It turns "recompute something over every contiguous subarray/substring" from O(n·k) or O(n²) into O(n), by updating the window incrementally instead of recomputing it from scratch each time it shifts. Codility's own course material calls this the **"caterpillar method"** — same technique (a front and back index, each only ever moving forward), different name — worth recognizing if it comes up under that label.

## When to use it

Problems about a contiguous subarray or substring — "longest," "shortest," "maximum sum," "contains all of X" — where recomputing the answer for each window from scratch would be wasteful, because consecutive windows overlap almost entirely.

## Fixed-size window

Window size `k` is constant; slide it one step at a time, removing the element that falls out the back and adding the one that enters the front.

```python
def max_subarray_sum(nums, k):
    window_sum = sum(nums[:k])
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]   # add new, drop oldest — O(1) per step
        best = max(best, window_sum)
    return best
```

```
nums = [2, 1, 5, 1, 3, 2], k = 3
window [2,1,5] sum=8
slide:  [1,5,1] sum=8-2+1=7
slide:  [5,1,3] sum=7-1+3=9   <- best
slide:  [1,3,2] sum=9-5+2=6
```

## Variable-size window

Window grows and shrinks depending on a condition — expand the right edge to include more, shrink the left edge when a constraint is violated:

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

## Complexity

O(n) — every element enters and leaves the window at most once, regardless of window type. Compare to the naive approach of checking every substring/subarray, which is O(n²) or worse.

## Practice problems
1. Maximum Average Subarray I (LeetCode #643) — fixed window
2. Longest Substring Without Repeating Characters (LeetCode #3) — variable window
3. Minimum Window Substring (LeetCode #76) — variable window, the hardest common variant

## Related
- [[02-two-pointers|two-pointers]]
- [[01-algorithms|algorithms]] — why the "amortized O(n) despite nested loops" argument holds
