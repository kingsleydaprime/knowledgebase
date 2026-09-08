# Coin Change II

**LeetCode 518** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Given coins and an `amount`, return the **number of combinations** that make the amount. Coins are reusable; `[1,2]` and `[2,1]` count as the **same** combination.

## The key — loop coins on the outside

The trap: counting *permutations* instead of *combinations*. To count combinations only, iterate **coins in the outer loop** and amounts inner. This fixes an order in which coins are considered, so each combination is generated exactly once (never `[1,2]` *and* `[2,1]`).

```python
def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1                              # one way to make 0: use nothing
    for coin in coins:                     # OUTER loop = coins -> combinations
        for a in range(coin, amount + 1):  # INNER, upward -> reuse allowed
            dp[a] += dp[a - coin]
    return dp[amount]
```

**Time O(amount · coins), space O(amount).**

## Loop order changes the meaning

- **Coins outer, amount inner** → **combinations** (each coin's contribution is added once, in a fixed order).
- **Amount outer, coins inner** → **permutations** (every order recounted) — that's the shape [[106-coin-change|Coin Change]] uses for *min coins*, where order doesn't affect the count.

Same two nested loops, swapped order, completely different answer. This is the single most important subtlety in counting-knapsack DP.

## Key insight

**Counting combinations (order-insensitive) → iterate items in the outer loop; counting sequences (order matters) → iterate the target outer.** Recognizing which the problem wants, and setting the loop nesting accordingly, is the whole game.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- contrast: [[106-coin-change|Coin Change]] (fewest coins)
- prev: [[113-best-time-to-buy-and-sell-stock-with-cooldown|Buy/Sell with Cooldown]] · next: [[115-target-sum|Target Sum]]
