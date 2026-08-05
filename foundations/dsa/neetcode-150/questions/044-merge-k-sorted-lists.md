# Merge K Sorted Lists

**LeetCode 23** · Linked List · concepts: [[08-heaps|heaps]], [[04-linked-lists|linked-lists]]

## Problem

Merge `k` sorted linked lists into one sorted list.

## Approach 1 — merge one at a time

Fold list 2 into list 1, then list 3, etc. If all lists have ~n nodes, the accumulated list keeps growing, giving **O(k²·n)** — too slow.

## Approach 2 — min-heap of the k heads (optimal)

At any moment the next output node is the **smallest among the current heads** of all lists — exactly what a [[08-heaps|min-heap]] gives in O(log k). Pop the smallest, append it, and push its successor.

```python
import heapq

def mergeKLists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))   # i breaks ties (nodes aren't comparable)
    dummy = tail = ListNode()
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

**Time O(N log k)** for N total nodes, **space O(k)** for the heap.

## Approach 3 — divide and conquer

Pair up lists and merge them ([[036-merge-two-sorted-lists|Merge Two Lists]]), halving the count each round: `log k` rounds × O(N) per round = **O(N log k)**, O(1) extra space. Same time as the heap, less space.

## The tie-breaker detail

Heap entries are `(val, i, node)` — the middle `i` is essential: when two heads share a value, Python would try to compare the `ListNode`s (unorderable → `TypeError`). A unique index as the second key prevents that.

## Key insight

**"Merge k sorted things" → min-heap of the k frontier elements**, popping the global min each step. It's the k-way generalization of the two-list merge, and the archetypal heap application (also the shape of external merge sort).

## Related
- concepts: [[08-heaps|heaps]], [[04-linked-lists|linked-lists]]
- builds on: [[036-merge-two-sorted-lists|Merge Two Sorted Lists]]
- prev: [[043-lru-cache|LRU Cache]] · next: [[045-reverse-nodes-in-k-group|Reverse Nodes in k-Group]]
