# House Robber

**LeetCode 198** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Rob houses along a street for maximum money, but you **can't rob two adjacent houses**.

```
[2,7,9,3,1]  ->  12   (rob houses 0, 2, 4: 2+9+1)
```

## The recurrence — take it or skip it

At house `i` you choose: **rob it** (add `nums[i]` to the best through `i−2`, since `i−1` is off-limits) or **skip it** (keep the best through `i−1`). So `dp[i] = max(dp[i-1], nums[i] + dp[i-2])`.

## Approach — two rolling variables (optimal)

```python
def rob(nums):
    prev, curr = 0, 0                      # dp[i-2], dp[i-1]
    for n in nums:
        prev, curr = curr, max(curr, prev + n)
    return curr
```

**Time O(n), space O(1).**

## The decision structure

`max(skip, rob)` where "rob" must reach back **two** houses (not one) because of the adjacency ban. That single "reach back past the forbidden neighbor" is what distinguishes this from a plain running sum, and it's the reusable idea behind any "no two adjacent" selection problem.

## Key insight

**"Best subset with a no-adjacent constraint" → `dp[i] = max(skip, take + dp[i-2])`.** The adjacency rule forces the recurrence to skip one predecessor. This exact pattern reappears in [[102-house-robber-ii|House Robber II]] (circular) and deletion/streak DP variants.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- prev: [[100-min-cost-climbing-stairs|Min Cost Climbing Stairs]] · next: [[102-house-robber-ii|House Robber II]]
