# Leader Algorithm (Majority Element / Boyer-Moore Voting)

> Added after reviewing Codility's own course PDFs in `pdfs/` (Chapter 8, `6-Leader.pdf`) — not covered anywhere in this vault. Codility calls this "Leader"; it's more widely known elsewhere (LeetCode, general CS literature) as the **majority element problem**, solved by the **Boyer-Moore voting algorithm** — same technique, different name, worth recognizing both.

Part of [[foundations/dsa/README|DSA fundamentals]]. **Problem:** given a sequence, find the **leader** — the single value that occurs in *more than half* the elements — or determine none exists. A sequence can have at most one leader (two values each occurring more than half the time would together need more elements than the sequence actually has).

This is a good one to sit with because the same problem gets progressively faster across three genuinely different approaches — each teaching a distinct idea, not just a micro-optimization of the last.

---

## O(n²) — the obvious approach

For every candidate value, count how often it actually occurs:
```python
def slow_leader(A):
    n = len(A)
    leader = -1
    for k in range(n):
        candidate = A[k]
        count = sum(1 for x in A if x == candidate)
        if count > n // 2:
            leader = candidate
    return leader
```
Correct, but re-scans the whole array once per candidate — quadratic.

---

## O(n log n) — sort first, then check just one position

Sort the array. If a leader exists, identical values become adjacent, and critically: **the leader must land at the middle index** after sorting. Why: since it occupies more than half the array, there's no way to arrange the rest of the elements such that the middle position *isn't* one of the leader's occurrences — there simply aren't enough other elements to push it out of the middle.

```python
def fast_leader(A):
    n = len(A)
    A.sort()
    candidate = A[n // 2]
    count = sum(1 for x in A if x == candidate)
    return candidate if count > n // 2 else -1
```
This turns "check every possible candidate" into "check exactly one, specific candidate" — the cost is now dominated entirely by the sort, O(n log n).

---

## O(n) — the elegant one: cancel out mismatched pairs

The key insight: **if you remove any two elements with *different* values, the leader (if one exists) is still the leader of what's left.** Removing a mismatched pair can only ever remove at most one occurrence of the actual leader, and the leader's share of the (now smaller) sequence only grows relatively — it never stops being a majority.

Simulate "removing mismatched pairs" with a simple counter, no actual stack needed for anything but the current running value:
```python
def golden_leader(A):
    n = len(A)
    size = 0
    for a in A:
        if size == 0:
            size, value = 1, a
        elif value == a:
            size += 1
        else:
            size -= 1
    candidate = value if size > 0 else -1

    count = sum(1 for x in A if x == candidate)
    return candidate if count > n // 2 else -1
```
Walk the array once, keeping a running "stack" that's really just a `(value, count)` pair: matching the current top increments it, a mismatch decrements it (conceptually canceling one occurrence of each), and hitting zero starts fresh with whatever comes next. Whatever value survives to the end is the **only possible candidate** — one final linear pass confirms whether it's actually a majority or not (the survival process finds a candidate even when *no* leader exists, which is exactly why that confirmation pass is mandatory, not optional).

Both passes are O(n), giving **O(n) time, O(1) extra space** overall — no sorting, no counting every candidate, just two linear scans.

---

## The pattern worth taking away

This progression — brute force, then "sort to expose structure," then "cancel out what can't matter" — recurs constantly in interview-style problems: whenever a problem's answer is guaranteed to be a majority/dominant element, Boyer-Moore-style pairwise cancellation is worth reaching for before assuming you need to sort or hash-count.

## Related
- [[foundations/dsa/06-patterns/07-top-k-elements|top-k-elements]] — a related but distinct family of problems (frequency-based, not majority-based)
