# Palindrome Partitioning

**LeetCode 131** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Partition a string so **every** substring is a palindrome; return all such partitionings.

```
"aab"  ->  [["a","a","b"], ["aa","b"]]
```

## Approach — backtrack over cut positions (optimal)

At each start index, try every prefix `s[start:end]`; if that prefix is a palindrome, "cut" there, recurse on the rest, then undo. A partitioning is complete when `start` reaches the end.

```python
def partition(s):
    res = []
    path = []
    def is_pal(sub):
        return sub == sub[::-1]
    def backtrack(start):
        if start == len(s):
            res.append(path[:])
            return
        for end in range(start + 1, len(s) + 1):
            prefix = s[start:end]
            if is_pal(prefix):             # only cut where the prefix is a palindrome
                path.append(prefix)
                backtrack(end)             # partition the remainder
                path.pop()                 # undo the cut
    backtrack(0)
    return res
```

**Time O(n · 2ⁿ), space O(n).** There are up to 2^(n−1) cut placements; each palindrome check is O(n) (memoizable to speed up).

## The framing — choices are *cut points*

Unlike subsets (pick elements) or permutations (order elements), here each decision is **where to place the next cut**, and the constraint (prefix must be a palindrome) prunes illegal cuts. Same choose/recurse/undo spine, different notion of a "choice."

## Key insight

**"All ways to split subject to a per-piece constraint" → backtrack over split points, pruning pieces that fail the constraint.** Palindromic prefixes are the gate here; the pattern extends to word-break-style partitioning and expression splitting.

## Related
- concept: [[14-backtracking|backtracking]]
- prev: [[076-word-search|Word Search]] · next: [[078-letter-combinations-of-a-phone-number|Letter Combinations of a Phone Number]]
