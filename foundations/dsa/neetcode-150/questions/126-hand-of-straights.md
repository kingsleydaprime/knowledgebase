# Hand of Straights

**LeetCode 846** · Greedy · concepts: [[10-greedy-algorithms|greedy]], [[03-hash-maps|hash-maps]]

## Problem

Can the hand be rearranged into groups of `groupSize` **consecutive** cards?

```
hand = [1,2,3,6,2,3,4,7,8], groupSize = 3  ->  true   ([1,2,3],[2,3,4],[6,7,8])
```

## Approach — count cards, greedily build from the smallest (optimal)

Count each value. Repeatedly take the **smallest remaining** card — it *must* start a group (nothing smaller exists to include it) — then consume the next `groupSize − 1` consecutive values. If any is missing, fail. A min-heap or a sorted map surfaces the smallest.

```python
import heapq
from collections import Counter

def isNStraightHand(hand, groupSize):
    if len(hand) % groupSize != 0:
        return False
    count = Counter(hand)
    heap = list(count.keys())
    heapq.heapify(heap)                    # min-heap of distinct values
    while heap:
        smallest = heap[0]
        for v in range(smallest, smallest + groupSize):
            if count[v] == 0:
                return False               # missing a needed consecutive card
            count[v] -= 1
            if count[v] == 0:
                if v != heap[0]:
                    return False           # a hole opened up in the middle
                heapq.heappop(heap)
    return True
```

**Time O(n log n), space O(n).**

## Why start from the smallest

The smallest card can only ever be the **left end** of a group — no smaller card exists to sit before it. So it's forced to start a straight, which forces the next `groupSize−1` values. This "the extreme element has no choice" is the greedy anchor; each forced group is provably part of any valid arrangement.

## Key insight

**"Partition into consecutive/constrained groups" → greedily commit the forced element (the smallest) and let it dictate its group.** Counting + always resolving the smallest first turns a combinatorial partition into a deterministic sweep. (Same idea solves Divide Array in Sets of K Consecutive Numbers.)

## Related
- concepts: [[10-greedy-algorithms|greedy]], [[08-heaps|heaps]], [[03-hash-maps|hash-maps]]
- prev: [[125-gas-station|Gas Station]] · next: [[127-merge-triplets-to-form-target-triplet|Merge Triplets to Form Target Triplet]]
