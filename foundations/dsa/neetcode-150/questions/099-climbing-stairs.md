# Climbing Stairs

**LeetCode 70** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

You climb `n` stairs, 1 or 2 steps at a time. How many distinct ways to reach the top?

```
n = 3  ->  3   (1+1+1, 1+2, 2+1)
```

## The recurrence — it's Fibonacci

To reach stair `i`, your last move came from stair `i−1` (a 1-step) or `i−2` (a 2-step). So `ways(i) = ways(i−1) + ways(i−2)` — the Fibonacci recurrence.

## Approach — bottom-up with two variables (optimal)

Only the last two results matter, so O(1) space.

```python
def climbStairs(n):
    prev, curr = 1, 1                      # ways(0)=1, ways(1)=1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr     # ways(i) = ways(i-1) + ways(i-2)
    return curr
```

**Time O(n), space O(1).** Naive recursion is O(2ⁿ) — the same overlapping-subproblem blowup [[15-dynamic-programming|DP]] exists to kill.

## Key insight

**Count paths where each step depends on a fixed number of previous states → a Fibonacci-style DP.** The whole skill is finding the recurrence ("the last move came from i−1 or i−2"); recognizing that many differently-worded problems share this exact recurrence is most of 1-D DP. The gateway problem for the category.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- next: [[100-min-cost-climbing-stairs|Min Cost Climbing Stairs]]
