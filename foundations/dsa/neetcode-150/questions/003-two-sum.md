# Two Sum

**LeetCode 1** · Arrays & Hashing · concept: [[03-hash-maps|hash-maps]]

## Problem

Given an array `nums` and a `target`, return the **indices** of the two numbers that add up to `target`. Exactly one solution exists; you can't reuse the same element twice.

```
nums = [2, 7, 11, 15], target = 9  -> [0, 1]   (2 + 7)
nums = [3, 2, 4],       target = 6  -> [1, 2]
```

The most famous interview problem there is, and the template for "find a pair with property X."

## Approach 1 — brute force (all pairs)

```python
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
```

**Time O(n²), space O(1).** Checks every pair.

## Approach 2 — hash map of value → index (optimal)

The insight: for each number `x`, its partner is fixed — `target - x`. So instead of searching for the partner, **remember every number you've seen** (mapped to its index) and ask the map, in O(1), whether the partner is already there.

```python
def twoSum(nums, target):
    seen = {}                       # value -> index
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:            # partner already passed -> done
            return [seen[need], i]
        seen[x] = i                 # record x for a future partner
```

**Time O(n), space O(n).** One pass. The subtlety that makes it correct in a single pass: check for the complement **before** inserting the current number, so you never pair an element with itself, and you naturally return the earlier index first.

## Why one pass suffices

You might think you need to build the whole map first, then search. You don't: if `i` and `j` (with `i < j`) are the answer, then when the loop reaches `j`, `nums[i]` is already in `seen` (it was inserted on an earlier iteration), so `need = target - nums[j] = nums[i]` is found immediately. Every valid pair is discovered at its *second* element.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Brute force | O(n²) | O(1) |
| **Hash map** | **O(n)** | **O(n)** |

## Key insight

**"Find the pair that sums to a target" → store what you've seen and look up the complement.** The hash map turns "search for a partner" (O(n)) into "ask if the partner exists" (O(1)). Note the contrast with *Two Sum II* (sorted input): there, a [[02-two-pointers|two-pointer]] sweep gets O(1) space *because* the array is sorted — here it isn't, and the problem wants original indices, so hashing wins.

## Related
- concept: [[03-hash-maps|hash-maps]]
- prev: [[002-valid-anagram|Valid Anagram]] · next: [[004-group-anagrams|Group Anagrams]]
- the complement-lookup idea generalizes to 3Sum / 4Sum (see [[02-two-pointers|two-pointers]])
