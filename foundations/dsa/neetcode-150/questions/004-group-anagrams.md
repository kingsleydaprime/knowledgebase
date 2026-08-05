# Group Anagrams

**LeetCode 49** · Arrays & Hashing · concept: [[03-hash-maps|hash-maps]]

## Problem

Given an array of strings, group the ones that are anagrams of each other.

```
["eat","tea","tan","ate","nat","bat"]
-> [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

## The core idea — a canonical key

All anagrams of a word share something unique to their group. If you can compute a **canonical signature** that's identical for anagrams and different otherwise, you just bucket words by that signature in a hash map. Two natural signatures:

## Approach 1 — sorted string as the key

Sorting any anagram yields the same string (`"eat"`, `"tea"`, `"ate"` all → `"aet"`).

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = "".join(sorted(word))     # canonical signature
        groups[key].append(word)
    return list(groups.values())
```

**Time O(n · k log k)** for n words of length up to k (each sort is k log k), **space O(n·k)**.

## Approach 2 — character-count tuple as the key (optimal)

Building on [[002-valid-anagram|Valid Anagram]]: anagrams share a character-count vector. A 26-length count tuple is a signature you can build in O(k) instead of O(k log k) — no sort.

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        count = [0] * 26
        for ch in word:
            count[ord(ch) - ord("a")] += 1
        groups[tuple(count)].append(word)   # tuple is hashable; list isn't
    return list(groups.values())
```

**Time O(n · k), space O(n·k).** Faster asymptotically because the key is built in linear time.

## Why `tuple`, not `list`

A dict key must be **hashable**, which in Python means immutable — a `list` raises `TypeError: unhashable type`, a `tuple` doesn't. This is exactly the hashability constraint from [[03-data-type-classification|data-type-classification]]: a mutable key could change after hashing and corrupt the table.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Sorted-string key | O(n·k log k) | O(n·k) |
| **Count-tuple key** | **O(n·k)** | O(n·k) |

## Key insight

**Grouping = hashing by a canonical key.** The skill is designing a signature that's identical within a group and unique across groups — sorted string or count vector here. `defaultdict(list)` is the idiomatic "append into buckets" container. This "bucket by a computed key" move recurs whenever a problem says "group / partition these by some equivalence."

## Related
- concept: [[03-hash-maps|hash-maps]]
- builds on: [[002-valid-anagram|Valid Anagram]] (same count signature)
- prev: [[003-two-sum|Two Sum]] · next: [[005-top-k-frequent-elements|Top K Frequent Elements]]
