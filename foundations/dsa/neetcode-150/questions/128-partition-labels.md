# Partition Labels

**LeetCode 763** · Greedy · concepts: [[10-greedy-algorithms|greedy]], [[03-hash-maps|hash-maps]]

## Problem

Partition a string into as **many** parts as possible so that each letter appears in **at most one** part. Return the part sizes.

```
"ababcbacadefegdehijhklij"  ->  [9, 7, 8]
```

## Approach — extend each part to the last index of its letters (optimal)

Precompute the **last index** of every character. Sweep; a part can only close once you've passed the last occurrence of *every* letter seen so far. Track the running `end = max(last[c])`; when the current index reaches `end`, cut a part.

```python
def partitionLabels(s):
    last = {c: i for i, c in enumerate(s)}   # last index of each char
    res = []
    start = end = 0
    for i, c in enumerate(s):
        end = max(end, last[c])              # part must reach this letter's last use
        if i == end:                         # everything so far is contained
            res.append(i - start + 1)
            start = i + 1
    return res
```

**Time O(n), space O(1)** (26 letters).

## The greedy cut point

A part is valid only if no letter inside it appears outside it — so it must extend at least to the last occurrence of every letter it contains. Greedily stretching `end` to that farthest last-index, and cutting the moment the scan catches up to `end`, produces the **maximum** number of parts: you close each part as early as correctness allows.

## Key insight

**"Partition so no element spans two parts" → track the farthest last-occurrence and cut when the scan reaches it.** Precomputing last-indices turns the constraint into a running boundary — a merge-of-intervals idea (each letter is an interval from first to last use) expressed as a one-pass greedy.

## Related
- concepts: [[10-greedy-algorithms|greedy]], [[08-overlapping-intervals|overlapping-intervals]]
- prev: [[127-merge-triplets-to-form-target-triplet|Merge Triplets]] · next: [[129-valid-parenthesis-string|Valid Parenthesis String]]
