# Pattern: Two Pointers

Walk two positions through a structure at once instead of one, letting their relative movement do the work that a nested loop would otherwise do. On a sorted array, this turns an O(n²) pair-search into O(n).

## When to use it

Sorted arrays or lists where you need to find pairs (or a small fixed number of elements) satisfying some condition on their sum/difference. If the data isn't sorted, [[04-sorting|sort it]] first — the O(n log n) sort is still cheaper than the O(n²) brute-force pair check it replaces.

## How it works

Start one pointer at each end. Move whichever one moves you toward the target:

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        elif total < target:
            left += 1        # need a bigger sum -> move left pointer up
        else:
            right -= 1       # need a smaller sum -> move right pointer down
    return [-1, -1]
```

```
nums = [1, 2, 3, 4, 6], target = 6
left=0 right=4  1+6=7 > 6  -> right--
left=0 right=3  1+4=5 < 6  -> left++
left=1 right=3  2+4=6 == 6 -> found [1, 3]
```

The reason this works without checking every pair: at each step, one side of the comparison is eliminated entirely, not just one pair — moving `left` up rules out every pair that still includes the old, too-small `left` value paired with anything.

## Complexity

O(n) time, O(1) extra space — versus O(n²) for checking every pair, or O(n) time / O(n) space for the hash-map version of two-sum on unsorted input. Two pointers wins on space when the data is already sorted.

## Practice problems

All three are written up in the [[foundations/dsa/neetcode-150/README|NeetCode 150]]:

1. [[011-two-sum-ii|Two Sum II - Input Array is Sorted]] (LeetCode #167)
2. [[012-3sum|3Sum]] (LeetCode #15) — fix one element, two-pointer the rest
3. [[013-container-with-most-water|Container With Most Water]] (LeetCode #11)

Also in the 150 and built on this pattern: [[010-valid-palindrome|Valid Palindrome]] (#125), the simplest converging-pointer problem and a good warm-up, and [[014-trapping-rain-water|Trapping Rain Water]] (#42), the hard one.

## Related
- [[03-sliding-window|sliding-window]] — a specialization where both pointers move in the same direction
- [[04-sorting|sorting]]
- [[01-arrays|arrays]]
