# Trapping Rain Water

**LeetCode 42** · Two Pointers · concepts: [[02-two-pointers|two-pointers]], [[01-prefix-sum|prefix-sum]]

## Problem

Given an elevation map `height`, compute how much rainwater is trapped between the bars.

```
height = [0,1,0,2,1,0,1,3,2,1,2,1]  ->  6
```

## The key fact — water above a single bar

Water sitting on top of bar `i` is bounded by the **tallest wall to its left** and the **tallest wall to its right**; it fills to the lower of those two, minus the bar's own height:

```
water[i] = max(0, min(maxLeft[i], maxRight[i]) - height[i])
```

The total is the sum over all bars. Every solution is just a way of computing `maxLeft` and `maxRight` efficiently.

## Approach 1 — precompute left/right max arrays

Two passes fill `maxLeft` and `maxRight`; a third sums the trapped water.

```python
def trap(height):
    n = len(height)
    if n == 0: return 0
    maxLeft, maxRight = [0]*n, [0]*n
    maxLeft[0] = height[0]
    for i in range(1, n):
        maxLeft[i] = max(maxLeft[i-1], height[i])
    maxRight[-1] = height[-1]
    for i in range(n-2, -1, -1):
        maxRight[i] = max(maxRight[i+1], height[i])
    return sum(max(0, min(maxLeft[i], maxRight[i]) - height[i]) for i in range(n))
```

**Time O(n), space O(n).** Clear, and this is the [[01-prefix-sum|prefix/suffix-aggregate]] idea (directional running maxima) — same shape as [[007-product-of-array-except-self|Product Except Self]].

## Approach 2 — two pointers, O(1) space (optimal)

Carry running `leftMax` and `rightMax` in two variables while converging from both ends. The trick: **process whichever side has the smaller running max**, because on that side the water level is *definitely* determined by that smaller max — the opposite wall is guaranteed at least as tall, so it can't be the limiting factor.

```python
def trap(height):
    l, r = 0, len(height) - 1
    leftMax, rightMax = 0, 0
    total = 0
    while l < r:
        if height[l] < height[r]:            # left side is the shorter wall -> left bounds the water
            leftMax = max(leftMax, height[l])
            total += leftMax - height[l]
            l += 1
        else:
            rightMax = max(rightMax, height[r])
            total += rightMax - height[r]
            r -= 1
    return total
```

**Time O(n), space O(1).**

## Why "process the smaller side" is valid

When `height[l] < height[r]`, whatever the true right max is, it's ≥ `height[r]` > `height[l]`, hence ≥ everything on the left so far. So the water over the left pointer is limited **solely** by `leftMax` — you can commit to it without knowing the exact right max. Symmetric on the other side. That's what lets two scalars replace the two O(n) arrays.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Left/right max arrays | O(n) | O(n) |
| **Two pointers** | O(n) | **O(1)** |
| Monotonic stack | O(n) | O(n) |

(A [[06-monotonic-stack|monotonic stack]] solves it too, filling water layer by layer — good to mention as an alternative framing.)

## Key insight

**Water at a bar = min(left-max, right-max) − height.** The two-pointer optimization rests on a subtle proof: the side with the smaller running max is fully determined, so you can advance it and bank its water immediately. This is the hardest of the two-pointer problems precisely because the *correctness argument*, not the code, is the challenge.

## Related
- concepts: [[02-two-pointers|two-pointers]], [[01-prefix-sum|prefix-sum]], [[06-monotonic-stack|monotonic-stack]]
- relatives: [[007-product-of-array-except-self|Product Except Self]] (directional maxima), [[013-container-with-most-water|Container With Most Water]]
- prev: [[013-container-with-most-water|Container With Most Water]] — end of Two Pointers
- next category: Sliding Window
