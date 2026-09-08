# Module: Heaps & Priority Queues (Extreme Value Tracking)

Welcome to the **Heaps & Priority Queues** module. A **Heap** is a specialized tree structure designed to solve one specific problem with maximum efficiency: **constantly tracking and extracting the minimum (or maximum) element in a collection**.

A **Priority Queue** is an abstract data type where elements have priorities. A **Heap** is the high-performance data structure used to implement a Priority Queue under the hood.

> [!NOTE]
> **Terminology Disambiguation**: The "Heap" data structure described here is completely unrelated to the "Heap Memory" region of RAM used for dynamic memory allocation!

---

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

## 9. Check Your Understanding (University Self-Assessment)

1. **Question**: Given an array `[10, 20, 15, 30, 40]`, where is the left child of element `20` (index 1) located in the array?
   - <details><summary>Click for Answer</summary><b>Answer:</b> At index <b>3</b> (value <code>30</code>). Formula: <code>Left Child = 2 * i + 1 = 2(1) + 1 = 3</code>.</details>

2. **Question**: Why is `heapify()` on a 1,000,000-element array significantly faster ($O(n)$) than inserting 1,000,000 elements one by one ($O(n \log n)$)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>heapify()</code> processes the array bottom-up. The vast majority of nodes live near the bottom of the tree and require 0 or 1 swaps. Only the root node requires the full <code>log n</code> swaps.</details>

3. **Question**: How do you implement a Max-Heap in Python using the `heapq` module?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Python's <code>heapq</code> only supports min-heaps. To simulate a max-heap, multiply values by <code>-1</code> when pushing into the heap, and multiply by <code>-1</code> again when popping.</details>

---

## Related Modules
- [[01-arrays|Arrays]] — The flat 1D storage array underlying heaps
- [[06-dijkstra|Dijkstra's Algorithm]] — Priority queues driving weighted shortest path search
- [[04-sorting|Sorting]] — Heapsort ($O(n \log n)$ in-place sort)
