# Merge Triplets to Form Target Triplet

**LeetCode 1899** · Greedy · concept: [[10-greedy-algorithms|greedy]]

## Problem

Merging two triplets replaces each with the element-wise **max**. Given triplets and a `target`, can repeated merges produce exactly `target`?

## Approach — keep only "safe" triplets, check coverage (optimal)

Since merging takes element-wise maxima, any triplet with **some component larger than the target's** would push that component too high forever — it's **unusable**. Discard those. Among the safe triplets (all components ≤ target), you just need each target position `i` to be achievable: some safe triplet whose `i`-th value **equals** `target[i]`.

```python
def mergeTriplets(triplets, target):
    matched = set()                        # which target positions are hit exactly
    for t in triplets:
        if t[0] <= target[0] and t[1] <= target[1] and t[2] <= target[2]:   # safe
            for i in range(3):
                if t[i] == target[i]:
                    matched.add(i)
    return len(matched) == 3
```

**Time O(n), space O(1).**

## Why "safe + each position matched" suffices

A triplet exceeding the target in any component can never be merged in (max is monotonic — it would overshoot permanently), so it's out. Merging all the safe triplets together takes the max per position; if every position `i` has at least one safe triplet hitting `target[i]` exactly, the combined max equals the target. Merging *all* safe ones is harmless because none exceeds the target anywhere.

## Key insight

**Element-wise-max merges → discard anything that would overshoot, then check each coordinate is achievable.** The greedy realization "an over-target component is permanently disqualifying" filters the input, after which the answer is a simple per-position coverage check.

## Related
- concept: [[10-greedy-algorithms|greedy]]
- prev: [[126-hand-of-straights|Hand of Straights]] · next: [[128-partition-labels|Partition Labels]]
