# Min Cost Climbing Stairs

**LeetCode 746** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Each stair `i` has a `cost[i]` paid to step off it. You may start at index 0 or 1 and climb 1 or 2 steps. Return the minimum cost to reach the top (past the last stair).

```
cost = [10,15,20]  ->  15   (start at 15, step 2 to the top)
```

## The recurrence

The cheapest way to *reach* stair `i` is `cost[i]` plus the cheaper of arriving from `i−1` or `i−2`: `dp[i] = cost[i] + min(dp[i-1], dp[i-2])`. The answer is `min(dp[n-1], dp[n-2])` (you can finish from either of the last two).

## Approach — two rolling variables (optimal)

```python
def minCostClimbingStairs(cost):
    prev, curr = 0, 0                      # min cost to reach the two "virtual" starts
    for c in cost:
        prev, curr = curr, c + min(prev, curr)
    return min(prev, curr)                 # reach the top from either last stair
```

**Time O(n), space O(1).**

## Reaching vs. leaving a state

The subtlety versus [[099-climbing-stairs|Climbing Stairs]]: here each state carries a *cost*, and you minimize rather than count. The recurrence shape (depends on `i−1` and `i−2`) is identical; only the combine operation changes (`min + cost` instead of a sum of counts). Seeing that "count ways" and "minimize cost" share a skeleton is the point.

## Key insight

**Same Fibonacci-shaped recurrence, different combine operator** — swap "sum of counts" for "cost + min of predecessors." Recognizing that a new problem reuses a known recurrence with a tweaked objective is the core 1-D-DP move.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- builds on: [[099-climbing-stairs|Climbing Stairs]]
- prev: [[099-climbing-stairs|Climbing Stairs]] · next: [[101-house-robber|House Robber]]
