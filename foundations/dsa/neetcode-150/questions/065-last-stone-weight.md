# Last Stone Weight

**LeetCode 1046** · Heap / Priority Queue · concept: [[08-heaps|heaps]]

## Problem

Repeatedly smash the two **heaviest** stones; if unequal, the difference goes back. Return the weight of the last remaining stone (or 0).

```
[2,7,4,1,8,1]  ->  1
```

## Approach — max-heap (optimal)

You always need the two largest, repeatedly — the signature of a heap. Python only has a min-heap, so **negate** every value to simulate a max-heap.

```python
import heapq

def lastStoneWeight(stones):
    heap = [-s for s in stones]             # negate for a max-heap
    heapq.heapify(heap)
    while len(heap) > 1:
        first = -heapq.heappop(heap)        # heaviest
        second = -heapq.heappop(heap)       # second heaviest
        if first != second:
            heapq.heappush(heap, -(first - second))   # remainder goes back
    return -heap[0] if heap else 0
```

**Time O(n log n), space O(n).**

## The negation idiom

`heapq` is min-only, so `push(-x)` / `-pop()` gives max-heap behavior. It's the standard Python workaround and worth having automatic — just remember to negate on the way *out* too.

## Key insight

**"Repeatedly take the largest/smallest, then reinsert a derived value" → a heap.** The simulation would be O(n²) with re-sorting each round; the heap makes each "grab the top two, push one back" step O(log n). A clean, minimal max-heap drill.

## Related
- concept: [[08-heaps|heaps]]
- prev: [[064-kth-largest-element-in-a-stream|Kth Largest in a Stream]] · next: [[066-k-closest-points-to-origin|K Closest Points to Origin]]
