# Maximum Subarray

**LeetCode 53** · Greedy · concepts: [[09-max-slice-algorithms|max-slice]], [[10-greedy-algorithms|greedy]]

## Problem

Return the largest sum of any contiguous subarray.

```
[-2,1,-3,4,-1,2,1,-5,4]  ->  6   ([4,-1,2,1])
```

## Approach — Kadane's algorithm (optimal)

Sweep once, keeping a **running sum**. The key greedy decision: if the running sum ever goes **negative**, drop it — a negative prefix can only hurt any subarray extending past it, so start fresh from the current element.

```python
def maxSubArray(nums):
    best = nums[0]
    running = 0
    for n in nums:
        if running < 0:
            running = 0            # a negative prefix is worse than starting over
        running += n
        best = max(best, running)
    return best
```

**Time O(n), space O(1).**

## Why dropping a negative prefix is safe

If the sum of everything before position `i` is negative, then any subarray that *includes* that prefix would be larger without it. So the optimal subarray never starts with a negative-sum prefix — resetting `running` to 0 discards exactly those useless prefixes. That local "throw away what can't help" choice is provably globally optimal — the essence of [[10-greedy-algorithms|greedy]].

## Key insight

**Maximum subarray → [[09-max-slice-algorithms|Kadane's]]: extend the running sum, reset it when it turns negative.** The one-line greedy insight ("a negative running total should be abandoned") is the whole algorithm, and the seed of the max/min-tracking variant in [[107-maximum-product-subarray|Maximum Product Subarray]].

## Related
- concepts: [[09-max-slice-algorithms|max-slice / Kadane's]], [[10-greedy-algorithms|greedy]]
- next: [[123-jump-game|Jump Game]]
