# Partition Equal Subset Sum

**LeetCode 416** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return whether an array can be split into two subsets with **equal sum**.

```
[1,5,11,5]  ->  true   ([1,5,5] and [11])
[1,2,3,5]   ->  false
```

## The reframing — subset sum to total/2

Two equal halves means each sums to `total / 2`. If `total` is odd, impossible. Otherwise the question is: **does some subset sum to `target = total / 2`?** — the classic **0/1 knapsack** (subset-sum) problem.

## Approach — boolean DP over achievable sums (optimal)

`dp[s]` = "can we form sum `s` from some subset seen so far?" Process each number; for 0/1 knapsack (each item once), iterate sums **downward** so an item isn't reused within its own pass.

```python
def canPartition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True                           # sum 0 is always achievable (empty subset)
    for n in nums:
        for s in range(target, n - 1, -1): # DOWNWARD -> each item used once
            dp[s] = dp[s] or dp[s - n]
    return dp[target]
```

**Time O(n · target), space O(target).**

## The downward loop = 0/1 knapsack

Iterating sums **high to low** ensures each number updates `dp` based on states from *before* this number was considered — so it's used at most once. (Iterating upward would allow reuse, giving unbounded knapsack, as in [[106-coin-change|Coin Change]].) This loop-direction distinction is the crux of knapsack DP.

## Key insight

**"Split into equal parts" / "reach a target with a subset" → 0/1 subset-sum DP, iterating the capacity downward.** Recognizing a partition problem *is* subset-sum, and getting the loop direction right (once vs. reusable), is the transferable knapsack skill.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- contrast: [[106-coin-change|Coin Change]] (unbounded, upward loop)
- prev: [[109-longest-increasing-subsequence|Longest Increasing Subsequence]] — end of 1-D DP
- next category: 2-D Dynamic Programming
