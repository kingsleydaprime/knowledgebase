# Merge Intervals

**LeetCode 56** · Intervals · concept: [[08-overlapping-intervals|overlapping-intervals]]

## Problem

Merge all overlapping intervals.

```
[[1,3],[2,6],[8,10],[15,18]]  ->  [[1,6],[8,10],[15,18]]
```

## Approach — sort by start, then sweep (optimal)

**Sort by start time** so overlapping intervals become adjacent. Walk through; if the current interval starts at or before the last merged interval's end, they overlap — extend the last one's end. Otherwise start a new interval.

```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])     # sort by start
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:          # overlaps the last merged interval
            merged[-1][1] = max(merged[-1][1], end)   # extend its end
        else:
            merged.append([start, end])     # disjoint -> new interval
    return merged
```

**Time O(n log n)** (the sort dominates), **space O(n).**

## Why sorting by start is the enabler

After sorting by start, any interval that overlaps an earlier one must overlap the **most recent** merged interval (all earlier ones start no later). So a single "does this overlap the last?" check per interval is enough — no need to compare against all previous. This "sort, then one linear merge pass" is *the* interval template.

## Key insight

**Interval merging → sort by start, then extend-or-append in one pass.** Almost every interval problem opens with this sort; overlapping candidates become neighbors, collapsing an O(n²) all-pairs comparison to O(n log n).

## Related
- concept: [[08-overlapping-intervals|overlapping-intervals]], [[04-sorting|sorting]]
- prev: [[130-insert-interval|Insert Interval]] · next: [[132-non-overlapping-intervals|Non-overlapping Intervals]]
