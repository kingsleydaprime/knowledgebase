# Meeting Rooms

**LeetCode 252** · Intervals · concept: [[08-overlapping-intervals|overlapping-intervals]]

## Problem

Given meeting time intervals, return whether a person can attend **all** of them (no two overlap).

```
[[0,30],[5,10],[15,20]]  ->  false   ([0,30] overlaps the others)
[[7,10],[2,4]]           ->  true
```

## Approach — sort by start, check adjacent pairs (optimal)

After sorting by start time, overlaps can only occur between **consecutive** meetings. So a single pass checking "does this meeting start before the previous one ends?" decides it.

```python
def canAttendMeetings(intervals):
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:   # starts before prev ends -> overlap
            return False
    return True
```

**Time O(n log n), space O(1).**

## Why adjacent checks suffice

Sorting by start guarantees that if any two meetings overlap, some **adjacent** pair does — a later meeting starting before an earlier one ends must clash with its immediate predecessor. So you never need all-pairs comparison. This is the minimal interval problem and the warm-up for its harder sibling.

## Key insight

**"Can all intervals coexist?" → sort by start, check each against its predecessor.** The sorted order localizes every potential conflict to neighbors — the same principle behind Merge Intervals, used here just to *detect* rather than merge.

## Related
- concept: [[08-overlapping-intervals|overlapping-intervals]]
- prev: [[132-non-overlapping-intervals|Non-overlapping Intervals]] · next: [[134-meeting-rooms-ii|Meeting Rooms II]]
