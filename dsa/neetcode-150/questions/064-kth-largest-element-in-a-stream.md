# Kth Largest Element in a Stream

**LeetCode 703** · Heap / Priority Queue · concepts: [[08-heaps|heaps]], [[07-top-k-elements|top-k]]

## Problem

Design a class that, given `k`, returns the **k-th largest** element seen so far after each `add(val)`.

## Approach — a min-heap of size k (optimal)

Keep only the **k largest** values in a [[08-heaps|min-heap]]. The smallest of those k — the heap's root — is exactly the k-th largest overall. On each `add`, push and, if the heap exceeds size k, pop the smallest.

```python
import heapq

class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums
        heapq.heapify(self.heap)            # O(n)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)        # drop the smallest of the top-k
        return self.heap[0]                 # root = k-th largest
```

**`add` O(log k), space O(k).**

## Why a *min*-heap for the *largest*

Counterintuitive but exact: to track the k largest, you must know which of them is weakest (to evict when a bigger one arrives). A min-heap keeps that weakest at the root in O(1), so a new value only displaces it when it beats it. A max-heap would put the wrong element on top for eviction.

## Key insight

**"K-th largest / smallest, especially in a stream" → a size-k heap of the opposite polarity.** Bounding the heap at k gives O(log k) updates and O(k) space regardless of stream length — the defining [[07-top-k-elements|Top-K]] pattern.

## Related
- concepts: [[08-heaps|heaps]], [[07-top-k-elements|top-k]]
- next: [[065-last-stone-weight|Last Stone Weight]]
