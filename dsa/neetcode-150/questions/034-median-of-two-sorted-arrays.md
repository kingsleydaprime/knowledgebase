# Median of Two Sorted Arrays

**LeetCode 4** · Binary Search · concept: [[09-modified-binary-search|modified-binary-search]]

## Problem

Given two sorted arrays, return the median of their combined set in **O(log(m+n))**.

```
[1,3], [2]     -> 2.0
[1,2], [3,4]   -> 2.5
```

## Why it's hard

Merging is O(m+n) — easy but too slow for the required bound. The log bound forces a binary search, and the twist is that you binary-search a **partition point**, not a value.

## Approach — binary search the partition (optimal)

The median splits the combined array into a left half and a right half of equal size, with **every** left element ≤ **every** right element. Choose how many elements of the **smaller** array (`A`) go left; the count from `B` is then forced (to make the halves balance). Binary search `A`'s split so the four boundary elements satisfy `Aleft ≤ Bright` and `Bleft ≤ Aright`.

```python
def findMedianSortedArrays(A, B):
    if len(A) > len(B):
        A, B = B, A                          # binary search the shorter array
    m, n = len(A), len(B)
    half = (m + n + 1) // 2
    l, r = 0, m
    while l <= r:
        i = (l + r) // 2                     # elements of A on the left
        j = half - i                         # elements of B on the left (forced)
        Aleft  = A[i-1] if i > 0 else float("-inf")
        Aright = A[i]   if i < m else float("inf")
        Bleft  = B[j-1] if j > 0 else float("-inf")
        Bright = B[j]   if j < n else float("inf")

        if Aleft <= Bright and Bleft <= Aright:      # correct partition
            if (m + n) % 2:
                return max(Aleft, Bleft)             # odd: median is the left max
            return (max(Aleft, Bleft) + min(Aright, Bright)) / 2
        elif Aleft > Bright:
            r = i - 1                        # took too many from A -> fewer
        else:
            l = i + 1                        # took too few from A -> more
    return 0.0
```

**Time O(log(min(m,n))), space O(1).**

## The partition insight

You never merge — you only need the **four elements straddling the cut**. A valid partition is one where the left side's two maxima don't exceed the right side's two minima. `±inf` sentinels handle a cut at either array's edge, so no special-casing. Searching only the shorter array bounds it at O(log(min(m,n))).

## Key insight

**Binary search the *split point* between two sorted arrays, not a value.** The median is defined by a balanced partition, and the correctness test is local (four boundary elements) — the hardest binary search in the set, and a clinic in "search the structure, not the data."

## Related
- concept: [[09-modified-binary-search|modified-binary-search]]
- prev: [[033-time-based-key-value-store|Time Based Key-Value Store]] — end of Binary Search
- next category: Linked List
