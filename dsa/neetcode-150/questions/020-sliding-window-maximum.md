# Sliding Window Maximum

**LeetCode 239** · Sliding Window · concepts: [[03-sliding-window|sliding-window]], [[06-monotonic-stack|monotonic-stack]]

## Problem

Given `nums` and a window size `k`, return the maximum of each window as it slides left to right.

```
nums = [1,3,-1,-3,5,3,6,7], k = 3  ->  [3, 3, 5, 5, 6, 7]
```

## Approach 1 — recompute each window

For each of the `n − k + 1` windows, scan `k` elements. **O(n·k)** — too slow.

## Approach 2 — heap

A max-heap of `(value, index)`; pop entries that have fallen out of the window. **O(n log n)**, and the heap can hold stale entries. Works, but beaten below.

## Approach 3 — monotonic deque (optimal)

Keep a **deque of indices** whose values are **decreasing**. The front is always the current window's max. Two rules per step:

1. Before adding index `r`, pop from the **back** every index whose value is ≤ `nums[r]` — they can never be the max while `nums[r]` is in the window (a [[06-monotonic-stack|monotonic]] invariant).
2. Pop from the **front** any index that has slid out of the window (`< r - k + 1`).

```python
from collections import deque

def maxSlidingWindow(nums, k):
    dq = deque()          # indices, values decreasing front->back
    res = []
    for r in range(len(nums)):
        while dq and nums[dq[-1]] <= nums[r]:   # rule 1: smaller-or-equal are useless
            dq.pop()
        dq.append(r)
        if dq[0] <= r - k:                        # rule 2: front slid out of window
            dq.popleft()
        if r >= k - 1:                            # first full window reached
            res.append(nums[dq[0]])               # front = window max
    return res
```

**Time O(n), space O(k).** Each index is pushed and popped at most once → amortized O(1) per element.

## Why the deque stays small and correct

When a new large value arrives, every smaller value currently waiting is dominated — it's older *and* smaller, so it can never be a future window's max before expiring. Discarding them keeps the deque monotonic decreasing, so its front is the max by construction. This "a newer, bigger element makes older smaller ones irrelevant" is the monotonic-deque insight.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Recompute | O(n·k) | O(1) |
| Heap | O(n log n) | O(n) |
| **Monotonic deque** | **O(n)** | O(k) |

## Key insight

**"Max/min of every sliding window" → monotonic deque of candidate indices.** It's the sliding-window analogue of the [[06-monotonic-stack|monotonic stack]]: maintain only elements that could still be the answer, discarding those a newer element dominates.

## Related
- concepts: [[03-sliding-window|sliding-window]], [[06-monotonic-stack|monotonic-stack]], [[08-heaps|heaps]]
- prev: [[019-minimum-window-substring|Minimum Window Substring]] — end of Sliding Window
- next category: Stack
