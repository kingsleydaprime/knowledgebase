# Kth Largest Element in an Array

**LeetCode 215** · Heap / Priority Queue · concepts: [[08-heaps|heaps]], [[05-searching|searching]]

## Problem

Return the k-th largest element in an unsorted array (the k-th in sorted-descending order, not the k-th distinct).

```
[3,2,1,5,6,4], k=2  ->  5
```

## Approach 1 — heap

A size-k min-heap gives O(n log k); or `heapq.nlargest(k, nums)[-1]`. Reliable, easy.

## Approach 2 — Quickselect (optimal average)

Quickselect is [[04-sorting|quicksort]]'s partition without the full recursion: pick a pivot, partition so smaller elements go one side and larger the other, and recurse into **only** the side containing the target rank. It reaches the k-th element in **O(n) average**.

```python
import random

def findKthLargest(nums, k):
    target = len(nums) - k                  # k-th largest = index (n-k) in ascending order
    def quickselect(l, r):
        pivot = nums[random.randint(l, r)]
        # 3-way partition into < pivot, == pivot, > pivot
        lt = [x for x in nums[l:r+1] if x < pivot]
        eq = [x for x in nums[l:r+1] if x == pivot]
        gt = [x for x in nums[l:r+1] if x > pivot]
        if target < l + len(lt):
            return quickselect(l, l + len(lt) - 1)
        elif target < l + len(lt) + len(eq):
            return pivot                    # target lands in the pivot block
        else:
            return quickselect(l + len(lt) + len(eq), r)
    return quickselect(0, len(nums) - 1)
```

**Time O(n) average, O(n²) worst** (mitigated by a random pivot); **space O(n)** here (in-place partitioning gets O(1)).

## Heap vs Quickselect

| | Heap | Quickselect |
|---|---|---|
| Time | O(n log k) | **O(n)** avg, O(n²) worst |
| Space | O(k) | O(1) in-place |
| Streaming input | **yes** | no (needs all data) |
| Stable / simple | simpler | trickier, has worst case |

## Key insight

**Selection (k-th order statistic) doesn't need a full sort — partition toward the target rank (Quickselect), or bound a size-k heap.** Random pivoting keeps Quickselect near-linear; the heap wins when data streams in.

## Related
- concepts: [[08-heaps|heaps]], [[05-searching|searching]], [[04-sorting|sorting]]
- prev: [[066-k-closest-points-to-origin|K Closest Points to Origin]] · next: [[068-task-scheduler|Task Scheduler]]
