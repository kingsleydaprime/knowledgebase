# Search in Rotated Sorted Array

**LeetCode 33** · Binary Search · concept: [[09-modified-binary-search|modified-binary-search]]

## Problem

Search for `target` in a rotated sorted array of distinct values. O(log n).

```
[4,5,6,7,0,1,2], target = 0  ->  4
[4,5,6,7,0,1,2], target = 3  -> -1
```

## The idea — find the sorted half, then bound the target

At each step **one half `[l,mid]` or `[mid,r]` is fully sorted** (building on [[031-find-minimum-in-rotated-sorted-array|Find Minimum]]). Identify it, then check whether `target` lies within that sorted half's value range: if yes, search there; if no, search the other half.

```python
def search(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = l + (r - l) // 2
        if nums[mid] == target:
            return mid
        if nums[l] <= nums[mid]:                   # left half [l..mid] is sorted
            if nums[l] <= target < nums[mid]:
                r = mid - 1                        # target within the sorted left
            else:
                l = mid + 1
        else:                                      # right half [mid..r] is sorted
            if nums[mid] < target <= nums[r]:
                l = mid + 1                        # target within the sorted right
            else:
                r = mid - 1
    return -1
```

**Time O(log n), space O(1).**

## The reasoning

You can only reason about a range whose endpoints you trust — and the sorted half is exactly that. Once you know, say, the left half spans `[nums[l], nums[mid]]` in sorted order, a simple range check tells you whether `target` is inside it. The rotation is handled entirely by first asking "which half is the clean, sorted one?"

## Key insight

**Rotated search = (identify the sorted half) + (range-check the target against it).** It composes plainly with the previous problem: the same "one half is always sorted" fact, now used to place a specific value rather than find the pivot.

## Related
- concept: [[09-modified-binary-search|modified-binary-search]]
- builds on: [[031-find-minimum-in-rotated-sorted-array|Find Minimum in Rotated Sorted Array]]
- prev: [[031-find-minimum-in-rotated-sorted-array|Find Minimum]] · next: [[033-time-based-key-value-store|Time Based Key-Value Store]]
