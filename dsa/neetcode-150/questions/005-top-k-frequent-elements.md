# Top K Frequent Elements

**LeetCode 347** · Arrays & Hashing · concepts: [[03-hash-maps|hash-maps]], [[07-top-k-elements|top-k]], [[08-heaps|heaps]]

## Problem

Given an array `nums` and integer `k`, return the `k` most frequent elements (any order).

```
nums = [1,1,1,2,2,3], k = 2  -> [1, 2]
```

## Step 0 — count frequencies

Every approach starts the same: a frequency map (O(n)).

```python
from collections import Counter
count = Counter(nums)          # {1: 3, 2: 2, 3: 1}
```

The question is only how to extract the top k from those counts.

## Approach 1 — sort by frequency

```python
def topKFrequent(nums, k):
    count = Counter(nums)
    return [x for x, _ in count.most_common(k)]   # or sorted(count, key=count.get)[-k:]
```

**Time O(n log n)** (dominated by the sort), space O(n). Simple; wasteful because you fully order everything just to read the top k.

## Approach 2 — heap of size k

Keep a [[08-heaps|min-heap]] of the k most frequent seen so far (the [[07-top-k-elements|Top-K pattern]]). `heapq.nlargest` wraps this.

```python
import heapq

def topKFrequent(nums, k):
    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)
```

**Time O(n log k)**, space O(n). Better than a full sort when k ≪ n, because you only ever maintain k elements in the heap.

## Approach 3 — bucket sort (optimal, O(n))

The key realization: a frequency can be **at most n** (an element can't appear more than the array's length). So make `n + 1` buckets indexed by frequency, drop each value into the bucket for its count, and read buckets from the high-frequency end until you have k.

```python
def topKFrequent(nums, k):
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]   # buckets[f] = values with frequency f
    for val, freq in count.items():
        buckets[freq].append(val)

    result = []
    for freq in range(len(buckets) - 1, 0, -1):    # high frequency -> low
        for val in buckets[freq]:
            result.append(val)
            if len(result) == k:
                return result
```

**Time O(n), space O(n).** Bucket sort works here precisely because the sort key (frequency) is a **bounded integer** in `[0, n]` — the same non-comparison-sort trick covered in [[04-sorting|sorting]]. It beats the O(n log n)/O(n log k) approaches by giving up on ordering *within* a frequency, which the problem doesn't require.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Sort by freq | O(n log n) | O(n) |
| Heap of size k | O(n log k) | O(n) |
| **Bucket sort** | **O(n)** | O(n) |

## Key insight

Two lessons stacked: (1) "k most/least frequent" → **count map + heap** is the general tool; (2) when the sort key is a **bounded integer** (here, frequency ≤ n), **bucket sort** beats any comparison-based method and hits O(n). Recognizing the bounded-key opportunity is what separates the optimal answer from the "good enough" heap.

## Related
- concepts: [[03-hash-maps|hash-maps]], [[07-top-k-elements|top-k]], [[08-heaps|heaps]], [[04-sorting|bucket sort]]
- prev: [[004-group-anagrams|Group Anagrams]] · next: [[006-encode-and-decode-strings|Encode and Decode Strings]]
