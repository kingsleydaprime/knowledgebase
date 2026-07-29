# Pattern: Modified Binary Search

Adapt the halving logic of [[05-searching|binary search]] to arrays that aren't fully sorted in the plain sense — most commonly, a sorted array that's been **rotated** at some unknown pivot. The core trick: even when the whole array isn't sorted, at least one of the two halves around any `mid` always is, and you can use that fact to decide which half to search.

## When to use it

"Sorted but rotated" arrays, or any search problem where a small modification to the standard sorted-array assumption still leaves enough structure to halve the search space each step.

## How it works

At each step, first figure out which half is the "normal" sorted one (compare `nums[left]` to `nums[mid]`), then check whether the target could be in that sorted half's range — if so, search there; otherwise, the target must be in the other (still-rotated) half.

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:            # left half is normally sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                   # right half is normally sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

```
nums = [4, 5, 6, 7, 0, 1, 2], target = 0

left=0 right=6 mid=3  nums[3]=7
  nums[0]=4 <= 7 -> left half [4,5,6,7] is sorted
  is 0 in [4, 7)? no -> search right half: left=4
left=4 right=6 mid=5  nums[5]=1
  nums[4]=0 <= 1 -> left half [0,1] is sorted
  is 0 in [0, 1)? yes -> search left half: right=4
left=4 right=4 mid=4  nums[4]=0 == target -> found at index 4
```

## Complexity

O(log n) — same as standard binary search; the extra "which half is sorted" check is O(1) work added to each step, not an extra pass over the data.

## Practice problems
1. Search in Rotated Sorted Array (LeetCode #33)
2. Find Minimum in Rotated Sorted Array (LeetCode #153) — the pivot-finding half of this pattern in isolation
3. Search a 2D Matrix II (LeetCode #240) — binary search generalized to two dimensions

## Related
- [[05-searching|searching]]
- [[04-sorting|sorting]]
