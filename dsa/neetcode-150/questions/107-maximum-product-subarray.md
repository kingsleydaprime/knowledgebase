# Maximum Product Subarray

**LeetCode 152** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return the largest product of any contiguous subarray.

```
[2,3,-2,4]   ->  6   ([2,3])
[-2,3,-4]    -> 24   ([-2,3,-4] = 24)
```

## Why max-only (Kadane) fails

For sums, [[09-max-slice-algorithms|Kadane's]] tracks a single running max. Products break that: a **negative × negative = positive**, so the *smallest* (most negative) running product can suddenly become the largest when multiplied by another negative. You must track both.

## Approach — track running max AND min (optimal)

At each element, the new max/min product ending here is one of: the element alone, element × previous max, or element × previous min. Carry both.

```python
def maxProduct(nums):
    result = cur_max = cur_min = nums[0]
    for n in nums[1:]:
        candidates = (n, cur_max * n, cur_min * n)
        cur_max = max(candidates)
        cur_min = min(candidates)          # keep the most-negative around
        result = max(result, cur_max)
    return result
```

**Time O(n), space O(1).**

## Why the min matters

A large negative running product is a *latent maximum* — one more negative number flips it positive and possibly largest. Tracking `cur_min` preserves that potential. Zeros reset both (starting fresh with `n`), which the `n`-alone candidate handles. This "carry the min because signs flip" is the signature twist.

## Key insight

**With products (or any sign-flipping operation), track both the max and the min running value.** The optimum can hide in the most-negative state until a sign flip reveals it — a refinement of the single-state Kadane pattern.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]; contrast [[09-max-slice-algorithms|Kadane's]]
- prev: [[106-coin-change|Coin Change]] · next: [[108-word-break|Word Break]]
