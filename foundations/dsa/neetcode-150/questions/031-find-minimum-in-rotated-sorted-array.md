# Find Minimum in Rotated Sorted Array

**LeetCode 153** · Binary Search · concept: [[09-modified-binary-search|modified-binary-search]]

## Problem

A sorted array of distinct values rotated at some pivot. Find the minimum in O(log n).

```
[3,4,5,1,2]    -> 1
[4,5,6,7,0,1,2] -> 0
```

## The idea — which half is sorted?

Rotation leaves the array as two sorted runs; the minimum is the start of the second run (the single "drop" point). Compare `mid` to the **right** end to locate which side holds the pivot:

- `nums[mid] > nums[r]` → the drop is to the **right** of mid → search `[mid+1, r]`
- `nums[mid] ≤ nums[r]` → mid's half (through r) is sorted, so the min is at mid or to its **left** → search `[l, mid]`

```python
def findMin(nums):
    l, r = 0, len(nums) - 1
    while l < r:
        mid = l + (r - l) // 2
        if nums[mid] > nums[r]:
            l = mid + 1            # minimum is strictly right of mid
        else:
            r = mid                # minimum is mid or left (keep mid!)
    return nums[l]
```

**Time O(log n), space O(1).**

## Why compare to `r`, not `l`

Comparing `mid` to `nums[r]` cleanly identifies the sorted side; comparing to `nums[l]` is ambiguous when the array isn't rotated. Also note `r = mid` (not `mid - 1`) — `mid` might *be* the minimum, so you can't discard it. Pairing that with `while l < r` avoids an infinite loop.

## Key insight

**In a rotated sorted array, one half is always fully sorted — use that to decide which half to keep.** The pivot/minimum sits at the unique inversion point, and "is `mid` above or below the right end?" localizes it. This "identify the sorted half" idea directly powers the next problem.

## Related
- concept: [[09-modified-binary-search|modified-binary-search]]
- prev: [[030-koko-eating-bananas|Koko Eating Bananas]] · next: [[032-search-in-rotated-sorted-array|Search in Rotated Sorted Array]]
