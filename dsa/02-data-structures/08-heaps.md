# Module: Heaps & Priority Queues (Extreme Value Tracking)

Welcome to the **Heaps & Priority Queues** module. A **Heap** is a specialized tree structure designed to solve one specific problem with maximum efficiency: **constantly tracking and extracting the minimum (or maximum) element in a collection**.

A **Priority Queue** is an abstract data type where elements have priorities. A **Heap** is the high-performance data structure used to implement a Priority Queue under the hood.

> [!NOTE]
> **Terminology Disambiguation**: The "Heap" data structure described here is completely unrelated to the "Heap Memory" region of RAM used for dynamic memory allocation!

---

## Before you start

- You understand arrays and index arithmetic. See [[01-arrays|arrays]].
- You understand tree shape and height. See [[01-trees|trees]].

**What you will be able to do after this lesson:**

1. Explain how a complete binary tree is stored in an array with no pointers.
2. Explain why the heap property is weaker than sorting, and why that is the point.
3. Implement push and pop with bubble-up and bubble-down.
4. Explain why finding the k largest uses a min-heap.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

## 1. Real-World Motivation & Physical Metaphors

Imagine an **Hospital Emergency Room Triage Desk**:

```
                       [ ER Triage Desk ]
                                |
          +---------------------+---------------------+
          |                                           |
[ Critical Heart Patient ]                  [ Broken Arm Patient ]
  Priority 1 (Treat NEXT!)                   Priority 3 (Wait)
```

- When patients arrive, they are not treated strictly First-In, First-Out (FIFO).
- Patients are assigned a **Triage Score (Priority)**. The doctors must **always treat the highest-urgency patient next**, regardless of when they walked through the door.

### Why Not Just Use an Array?
1. **Unsorted Array**: Inserting a new patient is fast ($O(1)$), but finding the most critical patient requires scanning every person in the waiting room ($O(n)$).
2. **Sorted Array**: Finding the most critical patient is instant ($O(1)$ at index 0), but inserting a new patient requires shifting people in memory ($O(n)$).
3. **Heap (The Ideal Compromise)**: Maintaining a **partial order** allows you to peek at the extreme in **$O(1)$** time, and insert or remove items in **$O(\log n)$** time!

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Min-Heap** | A tree where every parent node is $\le$ its children. | The root (top) is ALWAYS the absolute global minimum. |
| **Max-Heap** | A tree where every parent node is $\ge$ its children. | The root (top) is ALWAYS the absolute global maximum. |
| **Complete Binary Tree** | A binary tree where every level is fully filled except possibly the last level (filled left-to-right). | Allows storing a tree inside a flat array with zero pointers! |
| **Sift-Up (Bubble-Up)** | Moving a newly inserted element UP the tree until heap property is restored. | Moving a critical patient to the front of triage. |
| **Sift-Down (Bubble-Down)** | Moving a node DOWN the tree after replacing the root to restore heap property. | Re-sorting triage after top patient enters operating room. |
| **Heapify** | Converting an unsorted array into a valid heap in **$O(n)$ time**. | Organizing a raw batch of ER patients at once. |

---

## 3. The Array Representation (Zero Pointers Required!)

Because a Heap is guaranteed to be a **Complete Binary Tree**, it can be stored inside a standard **1D Array** without allocating Node objects or memory pointers!

```
Tree Representation:                  Array Representation:
        ( 1 )                         Index:   0   1   2   3   4   5
       /     \                        Value: [ 1 | 3 | 5 | 8 | 9 | 7 ]
     ( 3 )   ( 5 )                             ^   ^---^   ^-------^
    /   \     /                               Root  L1        L2
  ( 8 ) ( 9 ) ( 7 )
```

### The Index Arithmetic Formula
For any element at index $i$:
$$\text{Parent Index} = \lfloor \frac{i - 1}{2} \rfloor$$
$$\text{Left Child Index} = 2i + 1$$
$$\text{Right Child Index} = 2i + 2$$

---

## 4. How Heap Operations Work ($O(\log n)$)

### 1. `Push` Operation (Sift-Up) — $O(\log n)$
1. Append the new item to the very end of the array (maintaining complete tree shape).
2. Compare the item with its parent. If it violates the heap property (e.g. smaller than parent in a min-heap), **swap** them.
3. Repeat swapping UP until the parent is smaller (or it reaches the root).

### 2. `Pop` Operation (Sift-Down) — $O(\log n)$
1. The extreme item (min or max) is always at `array[0]`.
2. Replace `array[0]` with the **last item** in the array, then remove the last item.
3. Compare the new root with its children. **Swap** with the smaller child (in a min-heap).
4. Repeat swapping DOWN until both children are larger (or it hits a leaf).

---

## 5. Python Implementation (`heapq` Module)

Python provides the built-in `heapq` module, which implements a **Min-Heap**:

```python
import heapq

# 1. Initialize an empty heap
heap = []

# 2. Push elements: O(log n) each
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)

# 3. Peek at the minimum element: O(1)
min_val = heap[0]  # Returns 1

# 4. Pop the minimum element: O(log n)
smallest = heapq.heappop(heap)  # Returns 1, remaining heap is [3, 5]

# 5. Convert an existing list into a heap in-place: O(n)!
numbers = [9, 2, 7, 4, 1]
heapq.heapify(numbers)  # In-place transform: numbers is now [1, 2, 7, 4, 9]
```

### The Max-Heap Trick in Python
Since Python's `heapq` is strictly a Min-Heap, negate values when inserting and popping to simulate a Max-Heap:

```python
# To store values [10, 50, 20] in a Max-Heap:
max_heap = []
heapq.heappush(max_heap, -10)
heapq.heappush(max_heap, -50)
heapq.heappush(max_heap, -20)

# Pop largest element:
largest = -heapq.heappop(max_heap)  # Returns 50!
```

---

## 6. Mathematical Proof: Why `heapify()` is $O(n)$ (Not $O(n \log n)$!)

Converting an unsorted array of size $N$ into a heap by repeatedly calling `heappush()` takes $N \times O(\log n) = O(n \log n)$.

However, calling `heapq.heapify(arr)` takes **$O(n)$ linear time**!

### Why?
`heapify()` works bottom-up:
- Half of the elements ($\approx N/2$) are leaves at the bottom of the tree. Sifting them down takes **0 swaps**!
- $N/4$ nodes are one level above leaves $\rightarrow$ at most **1 swap**.
- $N/8$ nodes are two levels above $\rightarrow$ at most **2 swaps**.

$$\text{Total Work} = \sum_{h=0}^{\log n} \frac{N}{2^{h+1}} \times h = O(N)$$

---

## 7. Time & Space Complexity Summary

| Operation | Time Complexity | Notes |
| :--- | :--- | :--- |
| **Peek Min / Max (`heap[0]`)** | **$O(1)$** | Direct index access to root. |
| **Push (`heappush`)** | **$O(\log n)$** | Swaps along tree height $h = \log n$. |
| **Pop (`heappop`)** | **$O(\log n)$** | Swaps along tree height $h = \log n$. |
| **Build Heap (`heapify`)** | **$O(n)$** | Bottom-up sift-down algorithm. |
| **Search Arbitrary Element** | $O(n)$ | Heaps do NOT maintain sorted search order! |
| **Space Complexity** | $O(n)$ | Stored in a flat 1D array. |

---

## 8. Common Pitfalls & Traps

1. **Heaps Are NOT Search Trees**: Do not use a Heap to look up an arbitrary value (e.g. "Does 42 exist?"). Searching a heap requires scanning every element ($O(n)$). Use a [[03-hash-maps|Hash Map]] or [[01-trees|Binary Search Tree]] for lookups!
2. **Tuple Comparison Crashes**: Storing `(priority, item)` tuples in Python throws a `TypeError` if two priorities are equal and `item` is an unorderable object (like a custom class).
   - *Fix*: Include an incrementing counter tiebreaker: `(priority, counter, item)`.
3. **Repeated Push vs. Heapify**: Building a heap from an initial array by pushing one element at a time is $O(n \log n)$. Use `heapify(arr)` for $O(n)$ speed!

---

## Implementation - complete runnable example

**Runnable example:** save as `heaps_lab.py` and run `python3 heaps_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Heaps: a tree stored in an array, and why that is the whole trick."""

class MinHeap:
    """A complete binary tree with no pointers -- the array IS the tree."""
    def __init__(self):
        self.data, self.swaps = [], 0

    @staticmethod
    def parent(i): return (i - 1) // 2
    @staticmethod
    def left(i):   return 2 * i + 1
    @staticmethod
    def right(i):  return 2 * i + 2

    def push(self, x):
        """Add at the end, then bubble UP while smaller than the parent."""
        self.data.append(x)
        i = len(self.data) - 1
        while i > 0 and self.data[i] < self.data[self.parent(i)]:
            p = self.parent(i)
            self.data[i], self.data[p] = self.data[p], self.data[i]
            self.swaps += 1
            i = p

    def pop(self):
        """Take the root, move the last item there, bubble DOWN."""
        if not self.data: raise IndexError("pop from empty heap")
        smallest = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            i = 0
            while True:
                l, r, best = self.left(i), self.right(i), i
                if l < len(self.data) and self.data[l] < self.data[best]: best = l
                if r < len(self.data) and self.data[r] < self.data[best]: best = r
                if best == i: break
                self.data[i], self.data[best] = self.data[best], self.data[i]
                self.swaps += 1
                i = best
        return smallest

    def peek(self): return self.data[0] if self.data else None
    def __len__(self): return len(self.data)

def top_k(values, k):
    """Keep a MIN-heap of size k to find the k LARGEST.

    The smallest of your current best sits at the root, so it is the
    cheapest to evict -- which is why the heap is a min-heap."""
    h = MinHeap()
    for v in values:
        h.push(v)
        if len(h) > k:
            h.pop()
    return sorted(h.data, reverse=True)

if __name__ == "__main__":
    print("THE ARRAY IS THE TREE -- no pointers anywhere")
    h = MinHeap()
    for v in [5, 3, 8, 1, 9, 2]:
        h.push(v)
    print(f"  pushed 5 3 8 1 9 2")
    print(f"  array: {h.data}")
    print("  index: 0  1  2  3  4  5")
    print("         └─ children of i are at 2i+1 and 2i+2, parent at (i-1)//2")
    print(f"  root (the minimum) = {h.peek()}")
    print()
    print("  as a tree:")
    print("        1")
    print("      /   \\")
    print("     3     2")
    print("    / \\   /")
    print("   5   9 8")
    print()

    print("THE HEAP PROPERTY IS WEAKER THAN SORTING")
    print(f"  heap array : {h.data}")
    print(f"  sorted     : {sorted(h.data)}")
    print("  -> a heap only guarantees parent <= children. It does NOT")
    print("     sort. That weaker promise is why push and pop are")
    print("     O(log n) instead of O(n log n).")
    print()

    print("POPPING YIELDS SORTED ORDER")
    order = [h.pop() for _ in range(len(h))]
    print(f"  {order}")
    print()

    print("TOP-K -- the pattern heaps exist for")
    values = [7, 2, 9, 4, 1, 8, 3, 6, 5]
    for k in (1, 3, 5):
        print(f"  top {k} of {values}: {top_k(values, k)}")
    print()
    print(f"  {'n':>8s} {'k':>5s} {'sort: n log n':>15s} {'heap: n log k':>15s}")
    import math
    for n, k in [(1_000_000, 10), (1_000_000, 1000)]:
        print(f"  {n:8,d} {k:5d} {n*math.log2(n):15,.0f} {n*math.log2(k):15,.0f}")
    print("  -> the win only matters when k is much smaller than n.")

    assert h.data == []
    assert order == sorted(order)
    assert top_k([7,2,9,4,1,8,3,6,5], 3) == [9, 8, 7]
    assert top_k([1], 5) == [1]
    h2 = MinHeap()
    for v in [9, 8, 7, 6, 5]: h2.push(v)
    assert h2.peek() == 5
    assert [h2.pop() for _ in range(5)] == [5, 6, 7, 8, 9]
    print()
    print("heaps_lab: passed")
```

Expected output:

```
THE ARRAY IS THE TREE -- no pointers anywhere
  pushed 5 3 8 1 9 2
  array: [1, 3, 2, 5, 9, 8]
  index: 0  1  2  3  4  5
         └─ children of i are at 2i+1 and 2i+2, parent at (i-1)//2
  root (the minimum) = 1

  as a tree:
        1
      /   \
     3     2
    / \   /
   5   9 8

THE HEAP PROPERTY IS WEAKER THAN SORTING
  heap array : [1, 3, 2, 5, 9, 8]
  sorted     : [1, 2, 3, 5, 8, 9]
  -> a heap only guarantees parent <= children. It does NOT
     sort. That weaker promise is why push and pop are
     O(log n) instead of O(n log n).

POPPING YIELDS SORTED ORDER
  [1, 2, 3, 5, 8, 9]

TOP-K -- the pattern heaps exist for
  top 1 of [7, 2, 9, 4, 1, 8, 3, 6, 5]: [9]
  top 3 of [7, 2, 9, 4, 1, 8, 3, 6, 5]: [9, 8, 7]
  top 5 of [7, 2, 9, 4, 1, 8, 3, 6, 5]: [9, 8, 7, 6, 5]

         n     k   sort: n log n   heap: n log k
  1,000,000    10      19,931,569       3,321,928
  1,000,000  1000      19,931,569       9,965,784
  -> the win only matters when k is much smaller than n.

heaps_lab: passed
```

## 9. Check Your Understanding (University Self-Assessment)

1. **Question**: Given an array `[10, 20, 15, 30, 40]`, where is the left child of element `20` (index 1) located in the array?
   - <details><summary>Click for Answer</summary><b>Answer:</b> At index <b>3</b> (value <code>30</code>). Formula: <code>Left Child = 2 * i + 1 = 2(1) + 1 = 3</code>.</details>

2. **Question**: Why is `heapify()` on a 1,000,000-element array significantly faster ($O(n)$) than inserting 1,000,000 elements one by one ($O(n \log n)$)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>heapify()</code> processes the array bottom-up. The vast majority of nodes live near the bottom of the tree and require 0 or 1 swaps. Only the root node requires the full <code>log n</code> swaps.</details>

3. **Question**: How do you implement a Max-Heap in Python using the `heapq` module?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Python's <code>heapq</code> only supports min-heaps. To simulate a max-heap, multiply values by <code>-1</code> when pushing into the heap, and multiply by <code>-1</code> again when popping.</details>

---

## Practice - independent task

Implement **heapify** - building a heap from an unsorted array in O(n), not O(n log n).

- The obvious way pushes each element one at a time: n pushes at O(log n) each.
- The better way starts at the last non-leaf node and bubbles **down**, working backwards to the root.
- Implement both. Count swaps for arrays of 1,000, 10,000 and 100,000 elements.
- **The surprising result:** bottom-up heapify is O(n), not O(n log n). Most nodes are near the bottom and barely move.
- Then implement **heapsort**: heapify, then repeatedly pop the root.

**Done when:** both constructions produce valid heaps, your swap counts show bottom-up growing linearly while repeated-push grows faster, and heapsort matches Python's `sorted()`.

<details><summary>Hint - open only after an attempt</summary>
The intuition for O(n): half the nodes are leaves and cannot move at all; a quarter are one level up and move at most one step; an eighth move at most two. The total is n times the sum of k/2^k, which converges to a constant.<br>
<strong>Repeated push is the opposite</strong> - it adds each element at the bottom where the tree is deepest, so it pays close to the full log n every time. Same final structure, different construction cost, and the difference is a genuinely surprising piece of arithmetic.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] Explain the index arithmetic linking a node to its parent and children.
- [ ] Explain why a heap does not sort, and why that weaker promise is useful.
- [ ] Trace a push that bubbles up and a pop that bubbles down.
- [ ] Explain why the k largest elements are found with a min-heap.

**Recap:** A heap is a complete binary tree stored in an array, with children of index i at 2i+1 and 2i+2 - so the structure is implied by arithmetic and needs no pointers. It guarantees only that each parent beats its children, which is far weaker than sorting and is exactly why push and pop cost O(log n) rather than O(n log n). Keeping a min-heap of size k finds the k largest in O(n log k), which beats sorting when k is much smaller than n.

**Next:** [[09-tries|Tries]] - a structure where the shape of the key itself becomes the path through the tree.

## Related Modules
- [[01-arrays|Arrays]] — The flat 1D storage array underlying heaps
- [[06-dijkstra|Dijkstra's Algorithm]] — Priority queues driving weighted shortest path search
- [[04-sorting/index|Sorting]] — Heapsort ($O(n \log n)$ in-place sort)
