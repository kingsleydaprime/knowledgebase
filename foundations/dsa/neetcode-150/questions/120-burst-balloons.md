# Burst Balloons

**LeetCode 312** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Bursting balloon `i` yields `nums[i-1] * nums[i] * nums[i+1]` coins (out-of-range = 1). Maximize total coins from bursting all of them.

## The key reframing — think *last* balloon burst, not first

If you pick which balloon to burst **first**, its neighbors keep changing as others pop — the subproblems overlap messily. Instead, in an interval `(l, r)`, consider which balloon `k` is burst **last**. When `k` is last, its neighbors are exactly the interval's boundaries `l` and `r` (everything between is already gone), so its coins are `nums[l]*nums[k]*nums[r]`, plus the best of the two now-independent subintervals.

```python
def maxCoins(nums):
    nums = [1] + nums + [1]                # padding balloons of value 1
    n = len(nums)
    dp = [[0] * n for _ in range(n)]       # dp[l][r] = best for the OPEN interval (l, r)
    for length in range(2, n):             # interval widths
        for l in range(0, n - length):
            r = l + length
            for k in range(l + 1, r):      # k = last balloon burst in (l, r)
                dp[l][r] = max(dp[l][r],
                               nums[l]*nums[k]*nums[r] + dp[l][k] + dp[k][r])
    return dp[0][n - 1]
```

**Time O(n³), space O(n²).**

## Interval DP and the "last" trick

Choosing the **last** action makes the subproblems independent — the left interval `(l, k)` and right `(k, r)` no longer interact, because `k`'s neighbors at burst time are fixed to the interval ends. This "decide the last operation, split into independent halves" is **interval DP**, filling the table by increasing interval length.

## Key insight

**When picking the *first* action entangles subproblems, pick the *last* one — it often decouples them.** Burst Balloons is the canonical interval DP; the boundary balloons (`k`'s neighbors = the interval ends when it bursts last) are what make the split clean.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- prev: [[119-edit-distance|Edit Distance]] · next: [[121-regular-expression-matching|Regular Expression Matching]]
