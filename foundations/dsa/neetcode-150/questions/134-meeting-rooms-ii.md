# Meeting Rooms II

**LeetCode 253** · Intervals · concepts: [[08-overlapping-intervals|overlapping-intervals]], [[08-heaps|heaps]]

## Problem

Return the **minimum number of rooms** needed so no two meetings share a room — i.e. the maximum number of meetings overlapping at any instant.

```
[[0,30],[5,10],[15,20]]  ->  2
```

## Approach 1 — min-heap of end times (optimal)

Sort by start. A [[08-heaps|min-heap]] holds the **end times of rooms currently in use**. For each meeting, if the earliest-ending room (heap top) is free by its start, reuse that room (pop); otherwise allocate a new one (don't pop). The heap size peaks at the answer.

```python
import heapq

def minMeetingRooms(intervals):
    intervals.sort(key=lambda x: x[0])
    heap = []                              # end times of in-use rooms
    for start, end in intervals:
        if heap and heap[0] <= start:      # earliest room freed up -> reuse it
            heapq.heappop(heap)
        heapq.heappush(heap, end)
    return len(heap)
```

**Time O(n log n), space O(n).**

## Approach 2 — sweep line (two sorted arrays)

Sort start times and end times separately; sweep both with two pointers, incrementing a counter on a start and decrementing on an end. The **peak** counter is the answer — this counts maximum simultaneous overlap directly.

## The reframing

"Minimum rooms" = "maximum overlap at any point in time." The heap tracks concurrently-running meetings by their end times so you always know whether any room is free; the sweep line counts overlaps as events on a timeline. Both are O(n log n) and hinge on that reframing.

## Key insight

**"Minimum resources for overlapping intervals" = "peak concurrent overlap" → min-heap of end times (reuse the earliest-freeing) or a sweep line of start/end events.** The heap-of-end-times is the canonical interval-scheduling-with-resources pattern.

## Related
- concepts: [[08-overlapping-intervals|overlapping-intervals]], [[08-heaps|heaps]]
- prev: [[133-meeting-rooms|Meeting Rooms]] · next: [[135-minimum-interval-to-include-each-query|Minimum Interval to Include Each Query]]
