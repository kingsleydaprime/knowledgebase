# Valid Parenthesis String

**LeetCode 678** · Greedy · concept: [[10-greedy-algorithms|greedy]]

## Problem

A string of `(`, `)`, and `*` (where `*` is `(`, `)`, or empty). Return whether it can be a valid parenthesis string.

```
"(*))"  ->  true
"(*)"   ->  true
")("    ->  false
```

## Approach — track the min/max possible open count (optimal)

Each `*` makes the number of unmatched `(` a **range**, not a single value. Track the interval `[low, high]` of possible open counts:

- `(` → both `low` and `high` increase.
- `)` → both decrease.
- `*` → `low` decreases (treat as `)`), `high` increases (treat as `(`).

Clamp `low` at 0 (you can't have negative open brackets — the `*`s that would've caused it just act as empty), and if `high` ever goes negative there are too many `)` → invalid. Valid iff `low` can reach 0 at the end.

```python
def checkValidString(s):
    low = high = 0
    for ch in s:
        if ch == "(":
            low += 1; high += 1
        elif ch == ")":
            low -= 1; high -= 1
        else:                      # '*'
            low -= 1; high += 1
        if high < 0:
            return False           # too many ')' even treating every '*' as '('
        low = max(low, 0)          # can't have fewer than 0 open
    return low == 0                # some assignment closes everything
```

**Time O(n), space O(1).**

## Why a range, not a stack

The `*` wildcard means you can't commit to one open-count — so you carry the **whole feasible range** and prune it (clamp `low ≥ 0`, fail if `high < 0`). If 0 stays within `[low, high]` throughout and `low` ends at 0, some concrete assignment of the `*`s balances the string. Tracking bounds instead of branching over every `*` is what keeps it O(n) rather than exponential.

## Key insight

**Wildcards over a counted constraint → track the min/max feasible count as an interval, clamping and failing on its bounds.** Instead of trying every `*` interpretation, the reachable-range collapses them into two numbers — a broadly useful greedy for "some assignment works" questions.

## Related
- concept: [[10-greedy-algorithms|greedy]]; contrast the stack in [[021-valid-parentheses|Valid Parentheses]]
- prev: [[128-partition-labels|Partition Labels]] — end of Greedy
- next category: Intervals
