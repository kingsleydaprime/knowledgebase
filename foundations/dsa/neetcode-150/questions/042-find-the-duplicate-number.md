# Find the Duplicate Number

**LeetCode 287** · Linked List (Floyd's) · concept: [[04-fast-slow-pointers|fast-slow-pointers]]

## Problem

An array of `n + 1` integers, each in `[1, n]`. Exactly one value repeats (possibly many times). Find it **without modifying the array** and in **O(1) space**.

```
[1,3,4,2,2]  -> 2
[3,1,3,4,2]  -> 3
```

## The reframing — the array is a linked list with a cycle

Read `nums[i]` as "the next index to visit." Since values are in `[1, n]`, following `i → nums[i]` is a traversal of a linked list over indices. Because two indices share a value (the duplicate), two nodes point to the **same** next node — a cycle, whose **entrance is the duplicate value**. So this is [[041-linked-list-cycle|Linked List Cycle]]'s follow-up in disguise.

```python
def findDuplicate(nums):
    slow = fast = 0
    while True:                       # phase 1: find a meeting point in the cycle
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow2 = 0                         # phase 2: find the cycle entrance = duplicate
    while slow != slow2:
        slow = nums[slow]
        slow2 = nums[slow2]
    return slow
```

**Time O(n), space O(1).**

## Why other approaches are ruled out

- Sorting → modifies the array (banned).
- Hash set → O(n) space (banned).
- Binary search on value + counting (`count of values ≤ mid`) → O(n log n), allowed but slower.

Floyd's hits both constraints: read-only and O(1) space.

## Key insight

**"Array values as pointers" turns a duplicate into a cycle, solvable by Floyd's.** The leap is *seeing* the array as a linked list; once you do, phase-2 of cycle detection lands exactly on the repeated value. A favorite because the reduction is so non-obvious.

## Related
- concept: [[04-fast-slow-pointers|fast-slow-pointers]]
- builds on: [[041-linked-list-cycle|Linked List Cycle]]
- prev: [[041-linked-list-cycle|Linked List Cycle]] · next: [[043-lru-cache|LRU Cache]]
