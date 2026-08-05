# Search a 2D Matrix

**LeetCode 74** · Binary Search · concept: [[09-modified-binary-search|modified-binary-search]]

## Problem

An `m × n` matrix where each row is sorted and the first value of each row exceeds the last of the previous row. Return whether `target` is present. O(log(m·n)) required.

```
[[1, 3, 5, 7],
 [10,11,16,20],
 [23,30,34,60]], target = 3  ->  true
```

## The idea — one sorted array in disguise

The constraints mean the matrix, read row by row, is a **single sorted sequence** of `m·n` elements. So binary search over the virtual index `0 … m·n − 1` and map it back to 2D coordinates: `row = idx // n`, `col = idx % n`.

```python
def searchMatrix(matrix, target):
    m, n = len(matrix), len(matrix[0])
    l, r = 0, m * n - 1
    while l <= r:
        mid = l + (r - l) // 2
        val = matrix[mid // n][mid % n]        # map flat index -> (row, col)
        if val == target:
            return True
        elif val < target:
            l = mid + 1
        else:
            r = mid - 1
    return False
```

**Time O(log(m·n)), space O(1).**

## The index mapping

`divmod(mid, n)` converts a flat index to `(row, col)`: integer-divide by the row width for the row, take the remainder for the column. This is the inverse of the row-major layout arrays use in memory ([[01-arrays|arrays]]) — the same trick behind treating any 2D grid as 1D.

## Alternative — two binary searches / staircase

Binary search the column of first-elements to find the candidate row, then binary search within it (also O(log m + log n)). A different matrix ("row- and column-sorted", LC 240) instead uses a **staircase** walk from the top-right in O(m + n).

## Key insight

**A fully-sorted matrix is a 1D sorted array with a coordinate transform.** Recognizing the flattening lets you reuse plain binary search; the only new idea is the `divmod` index mapping.

## Related
- concept: [[09-modified-binary-search|modified-binary-search]]; layout in [[01-arrays|arrays]]
- prev: [[028-binary-search|Binary Search]] · next: [[030-koko-eating-bananas|Koko Eating Bananas]]
