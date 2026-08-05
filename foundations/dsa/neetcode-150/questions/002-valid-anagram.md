# Valid Anagram

**LeetCode 242** · Arrays & Hashing · concept: [[03-hash-maps|hash-maps]]

## Problem

Given two strings `s` and `t`, return `true` if `t` is an anagram of `s` — same characters, same counts, any order.

```
s = "anagram", t = "nagaram"  -> true
s = "rat",     t = "car"      -> false
```

## Approach 1 — sort both

Two strings are anagrams iff their sorted forms are identical.

```python
def isAnagram(s, t):
    return sorted(s) == sorted(t)
```

**Time O(n log n), space O(n)** (sorting builds new lists). Clean one-liner, but the sort is unnecessary work — anagram is about *counts*, not order.

## Approach 2 — count characters (optimal)

Tally each character in `s`, then spend those tallies down as you walk `t`. If lengths differ, or any count goes negative / doesn't reach zero, it's not an anagram.

```python
def isAnagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for ch in s:
        count[ch] = count.get(ch, 0) + 1
    for ch in t:
        if ch not in count or count[ch] == 0:
            return False
        count[ch] -= 1
    return True
```

**Time O(n), space O(1)** — space is bounded by the alphabet (≤ 26 for lowercase English, or ≤ 128 ASCII), a constant, not O(n). `collections.Counter(s) == Counter(t)` is the same logic in one line.

## The length short-circuit

`if len(s) != len(t): return False` isn't just an optimization — without it, `s = "a"`, `t = "ab"` would pass the first loop's checks against the shared prefix and give a wrong answer. Different lengths can never be anagrams, so check it first.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Sort both | O(n log n) | O(n) |
| **Char count** | **O(n)** | **O(1)** (alphabet-bounded) |

## Key insight

Anagram = **equal character multisets**. The moment a problem is about "same elements, order irrelevant," a **count map** (frequency dictionary) is the tool — the single most common hashing pattern in this category. It reappears in [[004-group-anagrams|Group Anagrams]] (where the count *is* the grouping key) and [[005-top-k-frequent-elements|Top K Frequent]].

## Related
- concept: [[03-hash-maps|hash-maps]]
- prev: [[001-contains-duplicate|Contains Duplicate]] · next: [[003-two-sum|Two Sum]]
- [[004-group-anagrams|Group Anagrams]] — the count map becomes a bucket key
