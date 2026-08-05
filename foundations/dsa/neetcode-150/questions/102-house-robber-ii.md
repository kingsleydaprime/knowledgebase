# House Robber II

**LeetCode 213** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Same as [[101-house-robber|House Robber]], but the houses are in a **circle** — the first and last are adjacent, so you can't rob both.

## The idea — reduce the circle to two lines

The circular constraint has a clean split: the optimal either **excludes the first house** or **excludes the last** (it can't take both). So run the linear House Robber twice — on `nums[0:n-1]` and on `nums[1:n]` — and take the better. The edge case: a single house has no "circle."

```python
def rob(nums):
    if len(nums) == 1:
        return nums[0]

    def rob_line(houses):                  # linear House Robber
        prev, curr = 0, 0
        for n in houses:
            prev, curr = curr, max(curr, prev + n)
        return curr

    return max(rob_line(nums[:-1]),        # exclude the last house
               rob_line(nums[1:]))         # exclude the first house
```

**Time O(n), space O(1).**

## Why two linear passes cover it

Robbing both endpoints is the *only* thing the circle forbids beyond the linear rules. Any valid circular solution omits at least one endpoint — so it's a valid solution to one of the two linear subproblems. Taking the max over both covers every case. Reducing a circular constraint to "try each way of breaking the cycle" is a broadly useful trick.

## Key insight

**Circular DP → break the loop by fixing which endpoint is excluded, solve the linear version for each, take the best.** A constraint that couples the two ends is handled by enumerating the small number of ways to sever it.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- builds on: [[101-house-robber|House Robber]]
- prev: [[101-house-robber|House Robber]] · next: [[103-longest-palindromic-substring|Longest Palindromic Substring]]
