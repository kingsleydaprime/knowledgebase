# Coin Change

**LeetCode 322** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Given coin denominations and an `amount`, return the **fewest** coins to make it, or `-1` if impossible. Coins are **reusable**.

```
coins = [1,2,5], amount = 11  ->  3   (5+5+1)
```

## The recurrence — unbounded knapsack

`dp[a]` = fewest coins to make amount `a`. For each amount, try every coin `c ≤ a`: `dp[a] = 1 + min(dp[a - c])`. Coins reusable means you look *back* to `a − c` where the same coin could already have been used.

## Approach — bottom-up (optimal)

```python
def coinChange(coins, amount):
    dp = [0] + [float("inf")] * amount     # dp[0] = 0 coins for amount 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], 1 + dp[a - c])
    return dp[amount] if dp[amount] != float("inf") else -1
```

**Time O(amount · coins), space O(amount).**

## Why greedy fails, and the loop order

Greedily taking the largest coin is **wrong** (`coins=[1,3,4], amount=6`: greedy gives 4+1+1=3 coins, optimal is 3+3=2). You must consider all coins at each amount — that's what DP does. Iterating `amount` outermost with `dp[a-c]` allowing reuse is the **unbounded knapsack** structure (contrast [[110-partition-equal-subset-sum|0/1 knapsack]], where each item is used once).

## Key insight

**"Fewest/most items to hit a target, items reusable" → unbounded-knapsack DP: `dp[a] = best over coins of dp[a-c]`.** The reusability lives in looking back at `a−c` in the *same* dp array. A cornerstone DP shape.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- relative: [[114-coin-change-ii|Coin Change II]] (count combinations, not min coins)
- prev: [[105-decode-ways|Decode Ways]] · next: [[107-maximum-product-subarray|Maximum Product Subarray]]
