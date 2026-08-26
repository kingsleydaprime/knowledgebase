# Pattern: Overlapping Intervals

Merge or otherwise reconcile a collection of `[start, end]` ranges. The whole pattern hinges on one setup step: sort by start time first, and everything after that becomes a single linear pass.

## When to use it

Any problem framed around intervals/ranges — merging overlapping meetings, inserting a new interval into an existing sorted set, counting how many intervals must be removed to make the rest non-overlapping.

## The overlap condition

Once sorted by start time, two intervals `[a, b]` and `[c, d]` (with `c` coming after `a`) overlap exactly when `b >= c` — the first interval hasn't ended before the second one begins.

## How it works

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda pair: pair[0])   # sort by start time — the step that makes this linear after
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:                   # overlaps with the last merged interval
            merged[-1] = [last_start, max(last_end, end)]
        else:
            merged.append([start, end])
    return merged
```

```
intervals = [[1,3], [2,6], [8,10], [15,18]]
sorted (already is)

[1,3] -> merged=[[1,3]]
[2,6] -> 2 <= 3, overlaps -> merged=[[1,6]]
[8,10] -> 8 > 6, no overlap -> merged=[[1,6],[8,10]]
[15,18] -> 15 > 10, no overlap -> merged=[[1,6],[8,10],[15,18]]
```

## Complexity

O(n log n) — dominated by the initial sort; the merge pass itself is O(n). This is the same shape as most patterns that need sorted input first: see [[09-modified-binary-search|modified-binary-search]] and [[04-sorting|sorting]].

## Gotchas

- The overlap check must compare against the **last merged interval**, not the previous *original* interval — after a merge, the effective end time may have grown past what the original list showed.
- `start <= last_end` (not `<`) — intervals that touch exactly at the boundary (`[1,3]` and `[3,5]`) count as overlapping in most problem definitions; check the specific problem's definition since this is a common off-by-one trap.

## Practice problems

All of these are written up in the [[foundations/dsa/neetcode-150/README|NeetCode 150]] — intervals are one of the patterns it covers end to end:

1. [[133-meeting-rooms|Meeting Rooms]] (LeetCode #252) — just "does any pair overlap?"; the smallest version of the pattern
2. [[131-merge-intervals|Merge Intervals]] (LeetCode #56)
3. [[130-insert-interval|Insert Interval]] (LeetCode #57)
4. [[132-non-overlapping-intervals|Non-overlapping Intervals]] (LeetCode #435) — minimum removals to eliminate all overlaps
5. [[134-meeting-rooms-ii|Meeting Rooms II]] (LeetCode #253) — count *maximum concurrent* overlaps, which wants a heap or a sweep line rather than a merge
6. [[135-minimum-interval-to-include-each-query|Minimum Interval to Include Each Query]] (LeetCode #1851) — the hard one

## Related
- [[04-sorting|sorting]]
