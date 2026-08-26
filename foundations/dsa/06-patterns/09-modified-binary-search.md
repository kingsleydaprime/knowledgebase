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

## Binary search on the answer — a different modification, worth knowing separately

The rotated-array case above still binary-searches *over the array*. A distinct and very commonly tested variant instead binary-searches **over the space of possible answers** — used whenever a problem asks for the optimal value satisfying some condition, and "is candidate value X good enough?" is cheap to check and has a **monotonic** answer (every value below some threshold fails, every value at or above it works, with no flip-flopping).

**Example:** given `n` holes in a roof and `k` boards, find the minimum board size that lets all holes be covered using at most `k` boards.
```python
def min_board_size(holes, k):
    def boards_needed(size):          # greedy check: how many boards of this size are needed?
        count, last_covered = 0, -1
        for i, has_hole in enumerate(holes):
            if has_hole and last_covered < i:
                count += 1
                last_covered = i + size - 1
        return count

    lo, hi, result = 1, len(holes), -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if boards_needed(mid) <= k:     # mid is "good enough" — try to do better
            result = mid
            hi = mid - 1
        else:                            # mid isn't enough — need a bigger size
            lo = mid + 1
    return result
```
The shape to recognize: `lo`/`hi` bound a range of **candidate answers**, not array indices; the "check" function (`boards_needed` here) is usually its own separate O(n) pass; and the overall complexity becomes **O(n log n)** — an O(n) check repeated O(log n) times — rather than the plain O(log n) of searching an already-built array. Other classic problems in this exact shape: "minimum ship capacity to deliver packages within D days," "Koko eating bananas" (minimum eating speed to finish within h hours), "split array into k parts minimizing the largest part's sum."

The tell that a problem wants this pattern: it asks for a minimum/maximum value satisfying a constraint, and you can imagine a "does value X work?" check that's monotonic (works for X implies works for every value past X in the same direction) — that monotonicity is precisely what makes binary search valid here, same as sortedness is what makes it valid on an array.

## Practice problems

**In the [[foundations/dsa/neetcode-150/README|NeetCode 150]]** — written up here:

1. [[028-binary-search|Binary Search]] (LeetCode #704) — the unmodified baseline; nail the loop invariant here first
2. [[032-search-in-rotated-sorted-array|Search in Rotated Sorted Array]] (LeetCode #33)
3. [[031-find-minimum-in-rotated-sorted-array|Find Minimum in Rotated Sorted Array]] (LeetCode #153) — the pivot-finding half of this pattern in isolation
4. [[029-search-a-2d-matrix|Search a 2D Matrix]] (LeetCode #74) — treat the grid as one flat sorted array
5. [[030-koko-eating-bananas|Koko Eating Bananas]] (LeetCode #875) — binary search on the answer
6. [[033-time-based-key-value-store|Time Based Key-Value Store]] (LeetCode #981) — binary search for the largest timestamp ≤ target
7. [[034-median-of-two-sorted-arrays|Median of Two Sorted Arrays]] (LeetCode #4) — binary search on the *partition point*; the hardest one here

**Not in the NeetCode 150:**

8. Search a 2D Matrix II (LeetCode #240) — rows and columns sorted but not globally, so it's a staircase walk from a corner rather than a true binary search
9. Capacity To Ship Packages Within D Days (LeetCode #1011) — binary search on the answer, same shape as Koko

## Related
- [[05-searching|searching]]
- [[04-sorting|sorting]]
