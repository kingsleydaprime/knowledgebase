# Heaps (Priority Queues)

A heap is the data structure behind a **priority queue**: a collection where you repeatedly need the smallest (or largest) element *right now*, but don't care about the full ordering of everything else. It gives you the min (or max) in O(1) and insert/remove in O(log n) — strictly better than keeping a sorted [[02-dynamic-arrays|array]] (O(n) insert) or sorting on demand (O(n log n) every time) when all you ever look at is the extreme.

"Heap" here is unrelated to the "heap" region of memory where objects are allocated — same word, different concept.

## Why it exists

Two operations pull in opposite directions in a plain array: keeping data sorted makes "get the min" O(1) but "insert" O(n) (you shift to make room); keeping it unsorted makes insert O(1) but "get the min" O(n) (you scan). A heap is the compromise — it maintains a *partial* order that's just strong enough to keep the extreme at the front, and no stronger, so nothing pays the full sorting cost.

## The structure: a complete binary tree in an array

A heap is a **complete binary tree** — every level full except possibly the last, which fills left to right. That completeness is the trick: it lets the tree live in a flat array with no pointers, because the shape is fully predictable. For the node at index `i`:

```
parent(i)     = (i - 1) // 2
left_child(i) = 2*i + 1
right_child(i) = 2*i + 2
```

The **heap property** is the single invariant:

- **Min-heap**: every parent ≤ its children → the global minimum sits at the root (index 0).
- **Max-heap**: every parent ≥ its children → the global maximum sits at the root.

Note what the heap does *not* guarantee: siblings are unordered, and a node deep in the tree can be smaller than a node on the other side one level up. The only promise is root-to-leaf ordering along each path. That weaker promise is exactly why it's cheaper than a fully sorted structure.

## The two operations, and why they're O(log n)

Both work by moving one element along a single root-to-leaf path, and the tree's height is ⌊log₂ n⌋ because it's complete — so each is O(log n).

**Push (sift-up / bubble-up):** append the new element at the end of the array (the next open leaf, preserving completeness), then swap it upward while it violates the heap property against its parent.

**Pop-min (sift-down / bubble-down):** the min is at index 0. You can't just remove it (that leaves a hole), so swap it with the *last* leaf, shrink the array by one, then push that moved-up element back **down**, repeatedly swapping with its smaller child until the property holds again.

```python
import heapq

heap = []
heapq.heappush(heap, 5)     # O(log n)  — sift-up
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
heapq.heappop(heap)         # 1 — removes and returns the min, O(log n)  — sift-down
heap[0]                     # peek at the min without removing — O(1)
```

## Build-heap (heapify) is O(n), not O(n log n)

Turning an unordered array into a heap by pushing n elements one at a time is O(n log n). But **heapify in place** — sift-*down* every non-leaf node starting from the last parent and moving toward the root — is O(n). The counterintuitive result comes from the work distribution: half the nodes are leaves (zero work), a quarter are one level up (at most one swap each), and only the handful near the root do the full log-n work. The sum ∑ (n / 2^h) · h converges to O(n).

```python
nums = [5, 3, 8, 1, 9, 2]
heapq.heapify(nums)         # O(n) — nums is now a valid min-heap in place
```

The practical lesson: if you have all the elements up front, `heapify` once (O(n)); only push one-at-a-time when they arrive as a stream.

## Min-heap vs max-heap in practice

Python's `heapq` is a **min-heap only**. To get a max-heap, negate on the way in and out (`heapq.heappush(h, -x)` / `-heapq.heappop(h)`), or store tuples `(priority, item)` where the first element is what you're ordering by. Java has `PriorityQueue` (min-heap by default; pass a `Comparator` for max). Store `(key, value)` tuples when the sort key differs from the payload — Python compares tuples lexicographically, so put the priority first (and provide a tiebreaker to avoid comparing unorderable payloads).

## Heapsort

Heapify the array (O(n)), then repeatedly pop the min (n times × O(log n)) → **O(n log n)** total, in-place, not stable. It's the "sort by draining a heap" algorithm, and the reason a heap is sometimes called a "selection tree." See [[04-sorting|sorting]] for where it sits among the comparison sorts.

## The two-heap pattern

Keeping a running **median** of a stream needs the middle element(s) fast. Split the numbers into a **max-heap of the smaller half** and a **min-heap of the larger half**, balanced to within one element. The median is then either the top of the larger heap or the average of the two tops — each insert rebalances in O(log n). This is the *Find Median from Data Stream* solution, and the archetype for "track the middle of a stream."

## Complexity

| Operation | Cost |
|---|---|
| Peek min/max | O(1) |
| Push | O(log n) |
| Pop | O(log n) |
| Build-heap (heapify) | O(n) |
| Heapsort | O(n log n) |
| Search for an arbitrary element | O(n) — heaps aren't for lookup |

Space is O(n). Note the last row: a heap is **not** a search structure — finding a value that isn't the extreme means scanning. If you need ordered lookup, that's a [[01-trees|BST]], not a heap.

## Canonical problems (NeetCode Heap / Priority Queue)

- **Kth Largest Element in a Stream** — keep a **min-heap of size k**; its root is always the k-th largest seen so far. This is the [[07-top-k-elements|Top-K pattern]].
- **Last Stone Weight** — max-heap; repeatedly pop the two heaviest, push back the difference.
- **K Closest Points to Origin** — heap keyed by squared distance (no need for the sqrt).
- **Kth Largest Element in an Array** — a heap solves it in O(n log k); **Quickselect** does it in O(n) average (see [[05-searching|searching]]) — know both and the tradeoff.
- **Task Scheduler** — max-heap of task counts + a cooldown queue; greedily run the most frequent available task.
- **Design Twitter** — merge each followee's recent tweets with a heap (a k-way merge).
- **Find Median from Data Stream** — the two-heap pattern above.
- **Merge K Sorted Lists** — a min-heap of the k list heads is the classic k-way merge, O(n log k). See [[04-linked-lists|linked lists]].

## Gotchas

- **Heapify is O(n); building by repeated push is O(n log n).** Interviewers probe this.
- **Python `heapq` is min-only** — negate for a max-heap, and remember to negate again on the way out.
- **Comparing tuples with equal priorities** throws if the payloads aren't orderable — add a unique tiebreaker (e.g. an incrementing counter) as the second tuple element.
- **A heap gives you the extreme, not sorted order** — peeking repeatedly without popping always returns the same root; you must pop to advance.
- **No efficient "decrease-key" in `heapq`** — the textbook Dijkstra/Prim optimization isn't directly available, so the standard workaround is to push a new entry and skip stale ones when popped ("lazy deletion"). See [[06-dijkstra|Dijkstra]].

## Related
- [[07-top-k-elements|Top-K Elements pattern]] — the most common heap application
- [[01-trees|Trees]] — a heap is a complete binary tree; contrast with a BST
- [[06-dijkstra|Dijkstra]] and [[12-minimum-spanning-tree|Minimum Spanning Tree]] — both drive a min-heap by edge weight
- [[04-sorting|Sorting]] — heapsort
- [[02-dynamic-arrays|Dynamic arrays]] — the array a heap is stored in
