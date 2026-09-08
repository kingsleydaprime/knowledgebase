# Non-overlapping Intervals

**LeetCode 435** · Intervals · concepts: [[08-overlapping-intervals|overlapping-intervals]], [[10-greedy-algorithms|greedy]]

## Problem

Return the **minimum** number of intervals to remove so the rest don't overlap.

```
[[1,2],[2,3],[3,4],[1,3]]  ->  1   (remove [1,3])
```

## Approach — sort by end, greedily keep the earliest-ending (optimal)

This is the classic **activity-selection** greedy. **Sort by end time**; keep an interval whenever it starts at or after the last kept interval's end. Whenever one overlaps, remove it (count it) — and keep the one that ends earlier, since it leaves the most room for future intervals.

```python
def eraseOverlapIntervals(intervals):
    intervals.sort(key=lambda x: x[1])     # sort by END
    removals = 0
    prev_end = float("-inf")
    for start, end in intervals:
        if start >= prev_end:               # no overlap -> keep it
            prev_end = end
        else:
            removals += 1                   # overlaps -> remove this one
    return removals
```

**Time O(n log n), space O(1).**

## Why sort by *end*, not start

The interval that **ends earliest** always leaves the maximum room for the rest, so keeping it is never worse than keeping a later-ending overlapper. Sorting by end and greedily accepting the earliest-finishing compatible interval maximizes how many you keep — hence minimizes removals. Sorting by *start* here would give wrong greedy choices.

## Key insight

**"Maximize non-overlapping intervals kept" (= minimize removed) → sort by end, greedily take the earliest-finishing.** This is textbook activity selection; the end-time sort is the crucial, easily-mistaken detail that makes the greedy optimal.

## Related
- concepts: [[08-overlapping-intervals|overlapping-intervals]], [[10-greedy-algorithms|greedy]]
- prev: [[131-merge-intervals|Merge Intervals]] · next: [[133-meeting-rooms|Meeting Rooms]]
