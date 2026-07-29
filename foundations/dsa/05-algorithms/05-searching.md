# Searching

Searching means finding whether (and where) a target value exists in a structure. The whole story here is one tradeoff: linear search works on anything but costs O(n); binary search costs only O(log n) but demands the data be sorted first. Which one applies is almost always decided by that one question — is the data sorted?

## Linear search

Check every element, in order, until you find the target or run out.

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

O(n) — no assumptions about the data required, which is exactly why it's the fallback when data isn't sorted and sorting it first wouldn't pay off (e.g. a single one-off search on unsorted data isn't worth an O(n log n) sort beforehand).

## Binary search

Requires sorted data. Repeatedly check the middle element and discard the half that can't contain the target.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

```
Search for 7 in [1, 3, 4, 6, 7, 9, 12, 15]:

lo=0 hi=7  mid=3  arr[3]=6 < 7  -> search right half
lo=4 hi=7  mid=5  arr[5]=9 > 7  -> search left half
lo=4 hi=4  mid=4  arr[4]=7 == 7 -> found at index 4
```

Each comparison eliminates half of the remaining search space, which is exactly what produces O(log n) — this is the same halving logic that makes a [[01-trees|BST]] fast, just applied to a sorted array via index math instead of pointers.

## Complexity

| | Linear search | Binary search |
|---|---|---|
| Precondition | none | data must be sorted |
| Time | O(n) | O(log n) |
| Space | O(1) | O(1) iterative / O(log n) recursive (call stack) |

If the data isn't already sorted and you'll only search it once, sorting first costs O(n log n) — more expensive than just doing one O(n) linear search. Binary search only pays off when the data is already sorted, or when you'll search it many times (sort once, search repeatedly for cheap).

## Common variants

- **Find first/leftmost occurrence** of a target among duplicates — instead of returning immediately on a match, keep searching the left half to find an earlier one.
- **Find insertion point** (where a value *would* go to keep the array sorted) — Python's `bisect.bisect_left`/`bisect_right` do exactly this in O(log n).
- **Search in a rotated sorted array** — a sorted array that's been rotated at an unknown pivot; one half of any given split is still guaranteed sorted, so you can figure out which half to search using that fact. This is a genuinely common interview pattern — worth its own attention when we get into problem patterns.

```python
import bisect
bisect.bisect_left([1, 3, 4, 4, 6], 4)   # 2 — leftmost position a 4 could be inserted
bisect.bisect_right([1, 3, 4, 4, 6], 4)  # 4 — rightmost
```

## Gotchas

- **`mid = (lo + hi) // 2` can overflow** in fixed-width-integer languages (C, Java) when `lo + hi` exceeds the max int — the safe form is `mid = lo + (hi - lo) // 2`. Not an issue in Python (arbitrary precision ints), but worth knowing since it's a classic "correct-looking code that's actually buggy" example.
- **Off-by-one errors on the loop bounds** (`<=` vs `<`, `mid + 1` vs `mid`) are the most common binary search bug — decide up front whether `hi` is inclusive or exclusive and stay consistent.
- Binary search on unsorted data doesn't error — it just silently returns wrong/inconsistent results, since the algorithm has no way to detect that its core assumption is violated.

## Related
- [[04-sorting|sorting]] — the precondition for binary search
- [[01-trees|trees]] — a BST is binary search generalized to a pointer structure
- [[01-algorithms|algorithms]] — why halving the search space gives O(log n)
