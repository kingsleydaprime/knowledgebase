# Insert Interval

**LeetCode 57** · Intervals · concept: [[08-overlapping-intervals|overlapping-intervals]]

## Problem

Given a list of **non-overlapping, sorted** intervals and a `newInterval`, insert it and merge any overlaps.

```
[[1,3],[6,9]], newInterval=[2,5]  ->  [[1,5],[6,9]]
```

## Approach — three phases (optimal)

Because the input is already sorted, one pass in three phases suffices:

1. **Before**: intervals ending before `newInterval` starts — copy as-is.
2. **Overlap**: intervals that touch `newInterval` — absorb them by expanding `newInterval` to the min start / max end; then add it once.
3. **After**: the rest — copy as-is.

```python
def insert(intervals, newInterval):
    res = []
    i, n = 0, len(intervals)
    # 1. intervals entirely before newInterval
    while i < n and intervals[i][1] < newInterval[0]:
        res.append(intervals[i]); i += 1
    # 2. merge all overlapping intervals into newInterval
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval = [min(newInterval[0], intervals[i][0]),
                       max(newInterval[1], intervals[i][1])]
        i += 1
    res.append(newInterval)
    # 3. the rest
    while i < n:
        res.append(intervals[i]); i += 1
    return res
```

**Time O(n), space O(n).**

## The overlap test

Two intervals overlap iff `a.start ≤ b.end` **and** `b.start ≤ a.end`. Phase 2's condition `intervals[i][0] <= newInterval[1]` (with phase 1 having cleared everything ending too early) captures exactly the touching intervals; expanding to the min-start/max-end absorbs each.

## Key insight

**Sorted intervals + insert → sweep in three phases (before / merge-overlaps / after).** The sortedness means all overlaps with the new interval are contiguous, so a single linear scan handles it — the foundation for the merge operations below.

## Related
- concept: [[08-overlapping-intervals|overlapping-intervals]]
- next: [[131-merge-intervals|Merge Intervals]]
