# Sorting

Sorting is arranging elements into a defined order. It gets its own note (rather than being a footnote on [[01-arrays|arrays]]) because it's a genuine trade-space — no single sorting algorithm wins on every axis (speed, memory, stability, behavior on nearly-sorted data), and picking the right one is a real decision, not a formality. It's also a prerequisite for a lot of other techniques: [[05-searching|binary search]] only works on sorted data, and a surprising number of problems become easy the moment the input is sorted.

## Why comparison sorts have a floor

Any sorting algorithm that works by comparing elements pairwise cannot beat O(n log n) in the worst case — this isn't an implementation limitation, it's an information-theoretic one (there are n! possible orderings, and each comparison gives at most one bit of information, so you need at least log₂(n!) ≈ n log n comparisons to distinguish between them). This is why merge sort and quicksort's O(n log n) is considered "optimal" for comparison-based sorting, and why the simple O(n²) sorts below are considered naive rather than just "less optimized."

## The simple O(n²) sorts

**Bubble sort** — repeatedly swap adjacent out-of-order pairs, bubbling the largest unsorted element to the end each pass:

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
```

**Insertion sort** — build up a sorted prefix one element at a time, inserting each new element where it belongs:

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
```

These exist mainly as teaching tools and for one real niche: insertion sort is genuinely fast (close to O(n)) on data that's *already nearly sorted*, which is why production sorts (see Timsort below) actually fall back to something like it on small/nearly-sorted runs.

## Merge sort — divide and conquer, guaranteed O(n log n)

Split the array in half recursively until pieces are single elements (trivially sorted), then merge sorted halves back together.

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:      # <= (not <) keeps it stable
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

O(n log n) every time — no worst-case surprise like quicksort has — but it needs O(n) extra space for the merge step, since merging in place isn't practical.

## Quicksort — usually faster in practice, but a worse worst case

Pick a pivot, partition everything smaller to its left and larger to its right, recurse on each side.

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + mid + quicksort(right)
```

Average case O(n log n), but worst case O(n²) — happens when the pivot choice is consistently bad (e.g. always picking the first element on already-sorted input, so every partition is maximally unbalanced). Randomizing the pivot choice makes the worst case astronomically unlikely in practice, which is why real quicksort implementations do this.

## Comparing them

| Algorithm | Best | Average | Worst | Space | Stable? |
|---|---|---|---|---|---|
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quicksort | O(n log n) | O(n log n) | O(n²) | O(log n) | No (typically) |

**Stable** means equal elements keep their original relative order after sorting — matters when you're sorting by one key but want ties broken by original order (e.g. sorting students by grade, wanting ties to stay in the order they were entered).

## Beating the O(n log n) floor — non-comparison sorts

The O(n log n) floor above applies specifically to algorithms that sort by **comparing** elements pairwise. Sidestep comparison entirely — using actual structural knowledge about the data, like "every value is an integer between 0 and m" — and the floor doesn't apply anymore.

**Counting sort**: if every element is known to fall in a small, bounded range `0..m`, build an array of counters instead of comparing anything:
```python
def counting_sort(A, m):
    count = [0] * (m + 1)
    for x in A:
        count[x] += 1
    result = []
    for value, freq in enumerate(count):
        result.extend([value] * freq)
    return result
```
Each element is placed by using its own **value as an array index**, not by comparing it against other elements — that's what makes this **O(n + m)** rather than O(n log n): m is a property of the data's range, not its length, so when m is small relative to n this genuinely beats comparison-based sorting. The real limitation is memory, not time — counting sort needs an array of size m+1, so it stops being practical once the value range gets large (a range of a billion needs a billion-entry array regardless of how few elements you're actually sorting).

The same counting-array technique is useful for more than sorting — anywhere you need fast frequency lookups on bounded values. For example: given two arrays A and B, can swapping one element between them make their sums equal? Build a counting array for A once, then for each candidate swap value, check its count in O(1) instead of re-scanning A — turning an O(n²) "try every pair" approach into O(n + m) overall.

## What languages actually give you

Python's `sorted()`/`list.sort()` and Java's `Collections.sort()` use **Timsort** — a hybrid that runs insertion sort on small chunks (where it's genuinely fast) and merges those chunks the way merge sort does, specifically because it's stable and does very well on partially-sorted real-world data. In an interview, "just use the built-in sort" (O(n log n), stable, well-tested) is almost always the right call unless the question is specifically about implementing a sort.

```python
sorted([3, 1, 2])                       # [1, 2, 3]
sorted(people, key=lambda p: p.age)     # sort by a derived key
sorted(people, key=lambda p: p.age, reverse=True)
```

## Gotchas

- Quicksort's worst case isn't just theoretical — naive pivot selection (always first or last element) on already-sorted or reverse-sorted input hits it directly, which is a common reason interviewers ask "what's your pivot strategy."
- In-place partitioning schemes (Lomuto, Hoare) are fiddly to get exactly right — off-by-one errors in the partition boundary are the most common quicksort implementation bug.
- Sorting a list of objects/dicts without specifying a `key` will either error or sort by an arbitrary/unhelpful default comparison — always be explicit about what you're sorting by.

## Related
- [[05-searching|searching]] — binary search requires sorted input
- [[01-algorithms|algorithms]] — where the O(n log n) comparison-sort lower bound comes from
