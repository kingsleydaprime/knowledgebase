# Two Sum II — Input Array Is Sorted

**LeetCode 167** · Two Pointers · concept: [[02-two-pointers|two-pointers]]

## Problem

Given a **sorted** (ascending) array and a `target`, return the 1-indexed positions of the two numbers that sum to `target`. Exactly one solution; **O(1) extra space** required.

```
numbers = [2, 7, 11, 15], target = 9  -> [1, 2]
```

## Why this differs from Two Sum

The original [[003-two-sum|Two Sum]] used a hash map (O(n) space) because the array was unsorted. Here the array is **sorted**, and that ordering is the whole gift — it lets a two-pointer sweep replace the hash map and hit O(1) space.

## Approach — two pointers, steered by the sum

Put one pointer at each end and read the sum. Because the array is sorted, the sum responds **monotonically** to moving either pointer:

- sum **too small** → move the **left** pointer right (only way to increase it)
- sum **too big** → move the **right** pointer left (only way to decrease it)
- sum **equal** → found it

```python
def twoSum(numbers, target):
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]    # 1-indexed
        elif s < target:
            l += 1                   # need a bigger sum
        else:
            r -= 1                   # need a smaller sum
    return []                        # (guaranteed not reached)
```

**Time O(n), space O(1).**

## Why it can't miss the answer

Each step provably eliminates a value that can't be in *any* solution: if `numbers[l] + numbers[r] < target`, then `numbers[l]` paired with the *largest* remaining value (`numbers[r]`) is still too small, so `numbers[l]` can't be part of the answer — discard it by advancing `l`. Symmetric logic for `r`. Every move rules out exactly one index that's provably useless, so the correct pair is never skipped. This "discard a provably-dead end" argument is the heart of two-pointer correctness.

## Complexity summary

| | Time | Space |
|---|---|---|
| Two pointers | O(n) | **O(1)** |

## Key insight

**Sorted input + "find a pair" → converging two pointers, O(1) space.** The sortedness makes the sum monotonic in each pointer's movement, which is what lets you always know *which* pointer to move. This is the seed of the 3Sum/4Sum family: fix one element, then two-pointer the rest.

## Related
- concept: [[02-two-pointers|two-pointers]]
- contrast: [[003-two-sum|Two Sum]] (unsorted → hash map)
- prev: [[010-valid-palindrome|Valid Palindrome]] · next: [[012-3sum|3Sum]]
