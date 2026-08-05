# K Closest Points to Origin

**LeetCode 973** · Heap / Priority Queue · concepts: [[08-heaps|heaps]], [[07-top-k-elements|top-k]]

## Problem

Return the `k` points closest to the origin `(0,0)`.

## Approach — max-heap of size k (optimal for k ≪ n)

Distance is `√(x² + y²)`, but since you only **compare** distances, skip the square root and use `x² + y²`. Keep a size-k **max-heap** keyed by that squared distance; the farthest of your current k sits on top, ready to be evicted when a closer point arrives.

```python
import heapq

def kClosest(points, k):
    heap = []
    for x, y in points:
        dist = x*x + y*y
        heapq.heappush(heap, (-dist, x, y))    # negate -> max-heap by distance
        if len(heap) > k:
            heapq.heappop(heap)                # drop the farthest
    return [[x, y] for _, x, y in heap]
```

**Time O(n log k), space O(k).**

## Alternatives and the tradeoff

- **Sort by distance**, take the first k → O(n log n). Simpler, fine when k ≈ n.
- **Quickselect** on distance → **O(n) average**, the fastest, but harder to write and not stable.

The size-k heap is the sweet spot when k ≪ n: O(n log k) and O(k) space.

## The no-sqrt point

`√` is monotonic, so ordering by `x² + y²` is identical to ordering by true distance — dropping the sqrt avoids float error and a needless operation. A small but frequently-tested detail.

## Key insight

**"K closest/smallest by a metric" → size-k heap on that metric** (max-heap when finding the *smallest* k). Compare on the cheapest monotonic proxy (squared distance) rather than the exact value.

## Related
- concepts: [[08-heaps|heaps]], [[07-top-k-elements|top-k]]; Quickselect in [[05-searching|searching]]
- prev: [[065-last-stone-weight|Last Stone Weight]] · next: [[067-kth-largest-element-in-an-array|Kth Largest Element in an Array]]
