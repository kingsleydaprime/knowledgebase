# Minimum Interval to Include Each Query

**LeetCode 1851** · Intervals · concepts: [[08-overlapping-intervals|overlapping-intervals]], [[08-heaps|heaps]]

## Problem

For each query `q`, return the size of the **smallest** interval `[l, r]` that contains `q` (`l ≤ q ≤ r`), or `-1` if none.

## Approach — sort queries + heap of intervals by size (optimal)

Sort both intervals (by start) and queries (ascending). Process queries in order; for each, **add all intervals that have started** (`l ≤ q`) into a [[08-heaps|min-heap keyed by interval size]], and **remove** intervals that have already ended (`r < q`). The heap top is then the smallest still-containing interval.

```python
import heapq

def minInterval(intervals, queries):
    intervals.sort()                       # by start
    heap = []                              # (size, end)
    res = {}
    i = 0
    for q in sorted(queries):
        while i < len(intervals) and intervals[i][0] <= q:
            l, r = intervals[i]
            heapq.heappush(heap, (r - l + 1, r))    # size, end
            i += 1
        while heap and heap[0][1] < q:     # top interval already ended before q
            heapq.heappop(heap)
        res[q] = heap[0][0] if heap else -1
    return [res[q] for q in queries]
```

**Time O(n log n + m log m), space O(n).**

## Why sorting queries lets the heap work

By answering queries in increasing order, intervals are added **once** (when their start is reached) and only stale ones (`r < q`) are pruned from the heap top. The smallest valid interval containing `q` is always the heap's minimum after pruning. Offline processing — sorting the queries so shared work accumulates — is the key idea.

## Key insight

**Answer range-queries offline: sort queries, maintain a heap of currently-relevant intervals keyed by the quantity you want to minimize.** Combining interval sweeping with a size-ordered heap is the advanced interval pattern — the payoff of the whole category.

## Related
- concepts: [[08-overlapping-intervals|overlapping-intervals]], [[08-heaps|heaps]]
- prev: [[134-meeting-rooms-ii|Meeting Rooms II]] — end of Intervals
- next category: Math & Geometry
