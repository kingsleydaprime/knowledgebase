# Pattern: Top 'K' Elements

**[Intermediate]** — A university-level introduction to the top-k elements pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand heaps. See [[08-heaps|heaps]] if needed.
- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.

**What you will be able to do after this lesson:**

1. Define the top-k elements pattern and explain why it turns "fully sort the array" into a cheaper operation.
2. Implement finding the k largest/smallest elements using a heap.
3. Apply the pattern to related problems like k most frequent elements and k closest points.
4. Explain why the heap approach is more efficient than sorting when k << n.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're building a recommendation system and you need to find the top 10 most popular items from a list of 1 million items. You could sort the entire list by popularity and take the first 10: that's O(n log n) time and O(n) space.

But you only need the top 10, not the entire sorted list. You can do better: maintain a collection of the 10 largest items seen so far. As you process each item, if it's larger than the smallest item in your collection, replace the smallest with it. This is O(n log k) time and O(k) space — much cheaper when k is much smaller than n.

This is the top-k elements pattern: find the k largest (or smallest) elements in a collection without fully sorting it. A heap is the tool that makes this cheaper than sorting everything just to look at the top k of it.

---

## 2. Definitions and terminology

| Term               | Plain-English definition                                                          | Example / analogy                                               |
| ------------------ | --------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| **Top-k elements** | The k largest (or smallest) elements in a collection                              | The top 10 most popular products                                |
| **Heap**           | A complete binary tree with a heap property (parent smaller/larger than children) | A priority queue where the highest priority item is at the root |
| **Min-heap**       | Every parent is smaller than its children; smallest element at root               | A to-do list where the most urgent task is at the top           |
| **Max-heap**       | Every parent is larger than its children; largest element at root                 | A priority queue where the most important task is at the top    |

---

## 3. How it works — step by step

To find the **k largest** elements, counterintuitively use a **min-heap** of size k: keep the k largest seen so far in the heap, and the smallest of those k sits at the root — so if a new element beats the root, it's bigger than the current worst of your top-k, and should replace it.

```python
def kth_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)      # discard the current smallest of the top-k so far
    return heap[0]                   # root of the min-heap = k-th largest overall
```

**Concrete example:** `nums = [3, 2, 1, 5, 6, 4], k = 2`

```
push 3 -> heap=[3]
push 2 -> heap=[2,3]
push 1 -> heap=[1,2,3] -> size>2, pop smallest(1) -> heap=[2,3]
push 5 -> heap=[2,3,5] -> pop 2 -> heap=[3,5]
push 6 -> heap=[3,5,6] -> pop 3 -> heap=[5,6]
push 4 -> heap=[4,5,6] -> pop 4 -> heap=[5,6]

root = 5 -> the 2nd largest element
```

To find the **k smallest** elements, use a **max-heap** of size k:

```python
def kth_smallest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, -num)   # negate to simulate max-heap
        if len(heap) > k:
            heapq.heappop(heap)      # discard the current largest of the top-k so far
    return -heap[0]                 # root of the max-heap = k-th smallest overall
```

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `top_k_elements_lab.py` and run `python3 top_k_elements_lab.py`. It uses only Python's standard library and creates no external files.

```python
import heapq
from typing import List


def kth_largest(nums: List[int], k: int) -> int:
    """Find the k-th largest element in an array."""
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)      # discard the current smallest of the top-k so far
    return heap[0]                   # root of the min-heap = k-th largest overall


def kth_smallest(nums: List[int], k: int) -> int:
    """Find the k-th smallest element in an array."""
    heap = []
    for num in nums:
        heapq.heappush(heap, -num)   # negate to simulate max-heap
        if len(heap) > k:
            heapq.heappop(heap)      # discard the current largest of the top-k so far
    return -heap[0]                 # root of the max-heap = k-th smallest overall


def top_k_frequent(nums: List[int], k: int) -> List[int]:
    """Find the k most frequent elements."""
    # Count frequencies
    freq = {}
    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    # Use min-heap of size k
    heap = []
    for num, count in freq.items():
        heapq.heappush(heap, (count, num))
        if len(heap) > k:
            heapq.heappop(heap)      # discard the least frequent

    # Extract elements, most frequent first
    return [num for count, num in sorted(heap, reverse=True)]


def k_closest_points(points: List[List[int]], k: int) -> List[List[int]]:
    """Find the k closest points to the origin (0, 0)."""
    # Calculate squared distances
    def distance_sq(point):
        return point[0] ** 2 + point[1] ** 2

    # Use min-heap of size k
    heap = []
    for point in points:
        dist = distance_sq(point)
        heapq.heappush(heap, (-dist, point))   # negate: max-heap by distance
        if len(heap) > k:
            heapq.heappop(heap)      # root is the farthest so far -> discard it

    # Extract points from heap
    return [point for neg_dist, point in heap]


if __name__ == "__main__":
    # Test case 1: kth largest
    nums1 = [3, 2, 1, 5, 6, 4]
    k1 = 2
    result1 = kth_largest(nums1, k1)
    print(f"Test 1 - kth largest:")
    print(f"nums={nums1}, k={k1} -> {result1}")
    assert result1 == 5, f"Expected 5, got {result1}"

    # Test case 2: kth smallest
    nums2 = [3, 2, 1, 5, 6, 4]
    k2 = 2
    result2 = kth_smallest(nums2, k2)
    print(f"\nTest 2 - kth smallest:")
    print(f"nums={nums2}, k={k2} -> {result2}")
    assert result2 == 2, f"Expected 2, got {result2}"

    # Test case 3: top k frequent
    nums3 = [1, 1, 1, 2, 2, 3]
    k3 = 2
    result3 = top_k_frequent(nums3, k3)
    print(f"\nTest 3 - top k frequent:")
    print(f"nums={nums3}, k={k3} -> {result3}")
    expected3 = [1, 2]
    assert set(result3) == set(expected3), f"Expected {expected3}, got {result3}"

    # Test case 4: k closest points
    points4 = [[1, 3], [3, 4], [2, -1]]
    k4 = 2
    result4 = k_closest_points(points4, k4)
    print(f"\nTest 4 - k closest points:")
    print(f"points={points4}, k={k4} -> {result4}")
    expected4 = [[1, 3], [2, -1]]
    assert sorted(result4) == sorted(expected4), f"Expected {expected4}, got {result4}"

    print("\ntop_k_elements_lab: passed")
```

Expected output:

```
Test 1 - kth largest:
nums=[3, 2, 1, 5, 6, 4], k=2 -> 5

Test 2 - kth smallest:
nums=[3, 2, 1, 5, 6, 4], k=2 -> 2

Test 3 - top k frequent:
nums=[1, 1, 1, 2, 2, 3], k=2 -> [1, 2]

Test 4 - k closest points:
points=[[1, 3], [3, 4], [2, -1]], k=2 -> [[1, 3], [2, -1]]

top_k_elements_lab: passed
```

---

## 5. Related patterns and extensions

### Quickselect algorithm

A variation that finds the k-th smallest element in expected O(n) time:

```python
def quickselect(nums, k):
    def select(left, right, k_smallest):
        if left == right:
            return nums[left]

        pivot_index = partition(left, right, left)
        if k_smallest == pivot_index:
            return nums[k_smallest]
        elif k_smallest < pivot_index:
            return select(left, pivot_index - 1, k_smallest)
        else:
            return select(pivot_index + 1, right, k_smallest)

    def partition(left, right, pivot_index):
        pivot_value = nums[pivot_index]
        # Move pivot to end
        nums[pivot_index], nums[right] = nums[right], nums[pivot_index]

        store_index = left
        for i in range(left, right):
            if nums[i] < pivot_value:
                nums[store_index], nums[i] = nums[i], nums[store_index]
                store_index += 1

        # Move pivot to its final place
        nums[right], nums[store_index] = nums[store_index], nums[right]
        return store_index

    return select(0, len(nums) - 1, k - 1)
```

### Median of medians

An improvement to Quickselect that guarantees O(n) worst-case time:

```python
def median_of_medians(nums, k):
    # Find median of groups of 5, then recursively find median of medians
    # Use as pivot for Quickselect
    pass  # Implementation omitted for brevity
```

---

## 6. Complexity

O(n log k) — n insertions/removals, each O(log k) because the heap never grows past size k. This beats sorting the whole array (O(n log n)) whenever k is meaningfully smaller than n.

---

## 7. Tradeoffs and limitations

- **Heap overhead.** Using a heap adds overhead compared to simple array operations, but the log k factor is usually small.
- **Not suitable for very large k.** When k is close to n, sorting might be more efficient due to better cache locality.
- **Requires additional data structures.** For frequency counting, you need a hash map to count occurrences first.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `nums = [3, 2, 1, 5, 6, 4]` and `k = 2`, trace through the kth largest algorithm step by step.
2. **Question:** Why does the heap approach use a min-heap for finding the k largest elements?
3. **Question:** How would you modify the algorithm to find the k most frequent elements when there are ties?

### Answers — after your attempt

1. `push 3 -> heap=[3]`
   `push 2 -> heap=[2,3]`
   `push 1 -> heap=[1,2,3] -> size>2, pop 1 -> heap=[2,3]`
   `push 5 -> heap=[2,3,5] -> pop 2 -> heap=[3,5]`
   `push 6 -> heap=[3,5,6] -> pop 3 -> heap=[5,6]`
   `push 4 -> heap=[4,5,6] -> pop 4 -> heap=[5,6]`
   Root = 5 -> 2nd largest element
2. The min-heap keeps the k largest elements seen so far, with the smallest of those k at the root. When a new element is larger than the root, it should replace the root (the current worst of the top-k). If we used a max-heap, we'd have to remove the largest element instead of the smallest.
3. To handle ties, you could use a max-heap (negate values) and keep track of the frequency count. When popping, you need to consider both frequency and value to break ties appropriately.

---

## 9. Practice — independent task

**Task:** Implement a function `k_most_frequent(nums, k)` that returns the k most frequent elements in the array. Use the top-k elements pattern. Test it with the following cases:

- `nums = [1, 1, 1, 2, 2, 3]` → expected `[1, 2]` (1 appears 3 times, 2 appears 2 times)
- `nums = [1]` → expected `[1]`

**Done when:** your function returns the correct most frequent elements for both test cases.

---

## Practice problems

**In the [[foundations/dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[005-top-k-frequent-elements|Top K Frequent Elements]] (LeetCode #347) — count, then heap — though bucket sort beats the heap here, which is worth seeing.
2. [[067-kth-largest-element-in-an-array|Kth Largest Element in an Array]] (LeetCode #215) — the size-$k$ heap versus Quickselect trade discussed above.
3. [[066-k-closest-points-to-origin|K Closest Points to Origin]] (LeetCode #973) — the problem the lab's `k_closest_points` implements.
4. [[064-kth-largest-element-in-a-stream|Kth Largest Element in a Stream]] (LeetCode #703) — where a heap is genuinely necessary, since the data arrives over time.
5. [[065-last-stone-weight|Last Stone Weight]] (LeetCode #1046) — a max-heap with nothing else going on.
6. [[068-task-scheduler|Task Scheduler]] (LeetCode #621) — max-heap by count, plus a cooldown queue.
7. [[070-find-median-from-data-stream|Find Median from Data Stream]] (LeetCode #295) — two heaps facing each other; the standard extension.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they vary the comparator, which is where most heap bugs live:

8. Top K Frequent Words (#692) — #347 with a tie-break that makes the comparator interesting.
9. Reorganize String (#767) — greedy by frequency, driven by a max-heap.
10. Kth Smallest Element in a Sorted Matrix (#378) — heap over rows, or binary search on the answer.
11. Minimum Cost to Connect Sticks (#1167) — repeatedly merge the two smallest.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Explain why a min-heap of size k finds the k *largest*, which feels backwards.
- [ ] State the complexity and compare it with sorting the whole input.
- [ ] Implement top-k independently using a heap rather than a sort.
- [ ] Say when sorting is actually the better choice.

**Recap:** Maintaining a heap of size k gives the top k in O(n log k) rather than O(n log n) for a full sort. For the k largest you use a *min*-heap, so the smallest of your current best is at the top and cheapest to evict. The win only matters when k is much smaller than n; otherwise sort.

**Next:** [[08-overlapping-intervals|overlapping-intervals]] — a pattern where sorting *is* the right first move, and the whole problem collapses to one linear pass afterwards.

## 10. Related

- [[01-trees|trees]] — the heap data structure
- [[04-sorting|sorting]] — the O(n log n) alternative this pattern beats when k << n
- [[03-hash-maps|hash maps]] — used for frequency counting
- [[01-algorithms|algorithms]] — where the O(n log k) vs O(n log n) comparison comes from
- [[07-top-k-elements|top-k-elements]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Search engines:** Finding top k search results
- **Recommendation systems:** Finding top k recommended items
- **Network routing:** Finding top k shortest paths
- **Database systems:** Finding top k query results

The core idea — maintaining a collection of the k best elements seen so far — is a fundamental algorithmic technique that appears whenever you need to find the top k elements without sorting the entire collection.
