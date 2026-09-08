# Target Sum

**LeetCode 494** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Assign `+` or `−` to each number so the expression equals `target`. Count the ways.

```
nums = [1,1,1,1,1], target = 3  ->  5
```

## Approach 1 — DP over (index, running sum)

`dp[(i, total)]` = ways to reach `total` using the first `i` numbers. At each number, branch into adding and subtracting it. Memoize on `(index, running sum)` — the same sum recurs via different sign choices, which is where DP beats the O(2ⁿ) brute force.

```python
from collections import defaultdict

def findTargetSumWays(nums, target):
    dp = {0: 1}                            # running_sum -> count of ways
    for n in nums:
        nxt = defaultdict(int)
        for s, cnt in dp.items():
            nxt[s + n] += cnt              # choose +n
            nxt[s - n] += cnt              # choose -n
        dp = nxt
    return dp[target]
```

**Time O(n · totalSumRange), space O(totalSumRange).**

## Approach 2 — reduce to subset sum

A slick reduction: let `P` be the positives and `N` the negatives. `P − N = target` and `P + N = totalSum`, so `P = (target + totalSum) / 2`. The problem becomes "how many subsets sum to `P`?" — a [[110-partition-equal-subset-sum|subset-sum count]]. (Valid only if `target + totalSum` is even and non-negative.)

## Key insight

**Sign-assignment counting → DP over the running sum (or an algebraic reduction to subset-sum).** Memoizing on `(index, current sum)` collapses the exponential sign-choice tree, since many sign combinations reach the same partial sum. The reduction to subset-sum is the elegant alternative worth knowing.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- reduces to: [[110-partition-equal-subset-sum|Partition Equal Subset Sum]]
- prev: [[114-coin-change-ii|Coin Change II]] · next: [[116-interleaving-string|Interleaving String]]
