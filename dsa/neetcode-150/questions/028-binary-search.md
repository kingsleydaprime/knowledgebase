# Binary Search

**LeetCode 704** · Binary Search · concepts: [[05-searching|searching]], [[09-modified-binary-search|modified-binary-search]]

## Problem

Given a **sorted** array and a `target`, return its index, or −1 if absent. O(log n) required.

```
nums = [-1,0,3,5,9,12], target = 9  ->  4
```

## Approach — the canonical template

Maintain a `[l, r]` window of where the target could be. Compare the middle; because the array is sorted, one comparison discards **half** the remaining range.

```python
def search(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = l + (r - l) // 2         # avoids overflow in fixed-width languages
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            l = mid + 1                # target is in the right half
        else:
            r = mid - 1                # target is in the left half
    return -1
```

**Time O(log n), space O(1).**

## The three details people get wrong

- **`while l <= r`** (not `<`) — with `<`, a single-element window is never examined, missing targets.
- **`mid + 1` / `mid - 1`** — moving *past* `mid` (already checked) is what guarantees the window shrinks; `l = mid` can loop forever.
- **`l + (r - l) // 2`** — mathematically equal to `(l + r) // 2` but can't overflow a fixed-width int.

## Key insight

**Sorted data + one comparison that eliminates half → O(log n).** Every binary-search variant is this loop with a different "which half can I discard?" rule. Master the invariant (`target ∈ [l, r]`) and the boundary updates; the variations below only change the comparison.

## Related
- concepts: [[05-searching|searching]], [[09-modified-binary-search|modified-binary-search]]
- next: [[029-search-a-2d-matrix|Search a 2D Matrix]]
