# Pattern: Top 'K' Elements

Find the k largest (or smallest) elements in a collection without fully sorting it. A heap is the tool that makes this cheaper than sorting everything just to look at the top k of it.

## What's a heap, briefly

A heap is a [[01-trees|complete binary tree]] with one invariant: every parent is smaller than its children (min-heap) or larger than its children (max-heap) — so the smallest (or largest) element is always sitting at the root, accessible in O(1), with O(log n) insert/remove to maintain the invariant. Python's `heapq` module implements a min-heap on top of a plain list.

## When to use it

"Find the k largest/smallest," "k most frequent," "k closest points" — anything shaped like "give me the top k," where k is typically much smaller than n.

## How it works

To find the **k largest** elements, counterintuitively use a **min-heap** of size k: keep the k largest seen so far in the heap, and the smallest of *those* k sits at the root — so if a new element beats the root, it's bigger than the current worst of your top-k, and should replace it.

```python
import heapq

def kth_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)      # discard the current smallest of the top-k so far
    return heap[0]                   # root of the min-heap = k-th largest overall
```

```
nums = [3, 2, 1, 5, 6, 4], k = 2

push 3 -> heap=[3]
push 2 -> heap=[2,3]
push 1 -> heap=[1,2,3] -> size>2, pop smallest(1) -> heap=[2,3]
push 5 -> heap=[2,3,5] -> pop 2 -> heap=[3,5]
push 6 -> heap=[3,5,6] -> pop 3 -> heap=[5,6]
push 4 -> heap=[4,5,6] -> pop 4 -> heap=[5,6]

root = 5 -> the 2nd largest element
```

## Complexity

O(n log k) — n insertions/removals, each O(log k) because the heap never grows past size k. This beats sorting the whole array (O(n log n)) whenever k is meaningfully smaller than n.

## Practice problems

**In the [[foundations/dsa/neetcode-150/README|NeetCode 150]]** — written up here:

1. [[067-kth-largest-element-in-an-array|Kth Largest Element in an Array]] (LeetCode #215)
2. [[005-top-k-frequent-elements|Top K Frequent Elements]] (LeetCode #347) — heap keyed by frequency count instead of by value
3. [[066-k-closest-points-to-origin|K Closest Points to Origin]] (LeetCode #973) — heap keyed by a computed distance
4. [[064-kth-largest-element-in-a-stream|Kth Largest Element in a Stream]] (LeetCode #703) — the streaming version, where sorting isn't an option because the data hasn't all arrived yet
5. [[070-find-median-from-data-stream|Find Median from Data Stream]] (LeetCode #295) — two heaps balanced against each other; the hard one

**Not in the NeetCode 150:**

6. Find K Pairs with Smallest Sums (LeetCode #373)

## Related
- [[01-trees|trees]] — the shape a heap is built on
- [[04-sorting|sorting]] — the O(n log n) alternative this pattern beats when k << n
