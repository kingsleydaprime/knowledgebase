# Maximum Subarray

**LeetCode 53** · Greedy · concepts: [[09-max-slice-algorithms|max-slice]], [[10-greedy-algorithms|greedy]], [[01-prefix-sum|prefix-sum]]

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

### The same argument in prefix-sum terms

The subarray `nums[i..j]` sums to `prefix[j+1] − prefix[i]`, so the best subarray *ending at j* is `prefix[j+1]` minus the **smallest prefix sum before it**. Maximum subarray is therefore "maximise `prefix[j] − min(earlier prefixes)`" — the [[01-prefix-sum|prefix-sum]] pattern with a running minimum, exactly like [[015-best-time-to-buy-and-sell-stock|Best Time to Buy and Sell Stock]].

Kadane's reset *is* that running minimum, in disguise: setting `running = 0` when it goes negative is the same as re-anchoring to the smallest prefix seen so far. Neither the prefix array nor the min needs storing, which is why this lands at O(1) space. Worth holding both views — the greedy one is faster to code, the prefix-sum one is what generalises to "subarray summing to exactly k" and its relatives.

## Key insight

**Maximum subarray → [[09-max-slice-algorithms|Kadane's]]: extend the running sum, reset it when it turns negative.** The one-line greedy insight ("a negative running total should be abandoned") is the whole algorithm, and the seed of the max/min-tracking variant in [[107-maximum-product-subarray|Maximum Product Subarray]].

## Related
- concepts: [[09-max-slice-algorithms|max-slice / Kadane's]], [[10-greedy-algorithms|greedy]], [[01-prefix-sum|prefix-sum]]
- next: [[123-jump-game|Jump Game]]
