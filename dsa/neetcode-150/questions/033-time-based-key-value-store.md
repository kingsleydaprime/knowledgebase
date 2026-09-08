# Time Based Key-Value Store

**LeetCode 981** · Binary Search · concepts: [[09-modified-binary-search|modified-binary-search]], [[03-hash-maps|hash-maps]]

## Problem

Design a store with `set(key, value, timestamp)` and `get(key, timestamp)` that returns the value with the **largest stored timestamp ≤ the queried one** (or `""` if none).

```
set("foo","bar",1); get("foo",1) -> "bar"; get("foo",3) -> "bar"
set("foo","bar2",4); get("foo",4) -> "bar2"; get("foo",5) -> "bar2"
```

## The idea — hash map to sorted lists + binary search

Timestamps for a key **arrive in increasing order**, so store each key's history as an append-only list of `(timestamp, value)` — already sorted. `get` is then "find the rightmost timestamp ≤ target," a binary search for the **floor** (upper-bound-minus-one).

```python
class TimeMap:
    def __init__(self):
        self.store = {}                       # key -> list of (timestamp, value), ascending

    def set(self, key, value, timestamp):
        self.store.setdefault(key, []).append((timestamp, value))

    def get(self, key, timestamp):
        arr = self.store.get(key, [])
        l, r = 0, len(arr) - 1
        res = ""
        while l <= r:
            mid = l + (r - l) // 2
            if arr[mid][0] <= timestamp:
                res = arr[mid][1]             # candidate; try for a later valid one
                l = mid + 1
            else:
                r = mid - 1
        return res
```

**`set` O(1); `get` O(log n)** for n entries under that key; space O(total entries).

## The binary-search flavor here

This is a **floor / rightmost-true** search: among all timestamps ≤ target, take the largest. The pattern — "keep the best candidate seen so far, then keep searching the side that might improve it" — is the template for boundary/predicate binary searches (equivalent to `bisect_right(target) - 1`).

## Key insight

**Combine a hash map (group by key) with binary search (locate within a sorted per-key history).** Because inserts are monotone in time, no sorting is ever needed — the structure stays sorted for free, and `get` is a floor query.

## Related
- concepts: [[09-modified-binary-search|modified-binary-search]], [[03-hash-maps|hash-maps]]
- prev: [[032-search-in-rotated-sorted-array|Search in Rotated Sorted Array]] · next: [[034-median-of-two-sorted-arrays|Median of Two Sorted Arrays]]
