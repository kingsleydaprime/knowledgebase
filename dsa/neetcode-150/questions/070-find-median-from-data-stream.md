# Find Median from Data Stream

**LeetCode 295** · Heap / Priority Queue · concept: [[08-heaps|heaps]]

## Problem

Design a structure with `addNum(x)` and `findMedian()` over a growing stream.

## Approach — two balanced heaps (optimal)

Split the numbers into two halves and keep the boundary elements instantly reachable:

- a **max-heap** `small` holding the lower half (its top = largest of the low half),
- a **min-heap** `large` holding the upper half (its top = smallest of the high half).

Keep the sizes within 1 of each other. The median is then the top of the bigger heap (odd count) or the average of the two tops (even count) — both O(1).

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.small = []      # max-heap (negated): lower half
        self.large = []      # min-heap: upper half

    def addNum(self, num):
        heapq.heappush(self.small, -num)              # tentatively into low half
        # ensure every low <= every high
        if self.small and self.large and -self.small[0] > self.large[0]:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        # rebalance sizes (differ by at most 1)
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        elif len(self.large) > len(self.small) + 1:
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        if len(self.large) > len(self.small):
            return self.large[0]
        return (-self.small[0] + self.large[0]) / 2
```

**`addNum` O(log n), `findMedian` O(1), space O(n).**

## The two invariants

1. **Ordering** — every element in `small` ≤ every element in `large` (so the two tops straddle the median).
2. **Balance** — sizes differ by at most 1 (so the median is always at the heap tops).

Each `addNum` restores both with at most a couple of pushes/pops. Sorting on every query would be O(n log n) per call; the two-heap structure makes the median O(1) to read.

## Key insight

**Track the middle of a stream → two heaps guarding the median from below and above.** The max-heap/min-heap pair keeps the two central elements at the tops in O(1). The archetypal two-heap problem — reach for it on any running-median / "balance around a pivot" task.

## Related
- concept: [[08-heaps|heaps]]
- prev: [[069-design-twitter|Design Twitter]] — end of Heap / Priority Queue
- next category: Backtracking
