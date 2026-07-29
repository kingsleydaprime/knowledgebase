# Pattern: Prefix Sum

Preprocess an [[01-arrays|array]] once so that any range-sum query afterward is O(1) instead of O(n). The trade is a single O(n) pass and O(n) extra space up front, paid once, to make every query after that nearly free.

## When to use it

Any time you need to answer **multiple** range-sum queries (or cumulative-sum questions) on a static array. If you only need one range sum, just sum it directly — prefix sum only pays off when the preprocessing cost is amortized across repeated queries.

## How it works

Build an array `P` where `P[i]` = sum of everything in the original array from index 0 to i:

```
A → [1, 2, 3, 4, 5, 6]
P → [1, 3, 6, 10, 15, 21]
```

To get the sum of `A[i..j]` inclusive, it's just `P[j] - P[i-1]` (handle `i == 0` as a special case, or pad `P` with a leading 0 to sidestep it entirely).

```python
def build_prefix_sums(nums):
    prefix = [0] * (len(nums) + 1)   # prefix[0] = 0 sentinel avoids the i==0 special case
    for i, num in enumerate(nums):
        prefix[i + 1] = prefix[i] + num
    return prefix

def range_sum(prefix, i, j):          # sum of nums[i..j] inclusive
    return prefix[j + 1] - prefix[i]
```

## Complexity

O(n) to build, O(1) per query — versus O(n) per query if you sum the range directly every time. For q queries, that's O(n + q) total instead of O(n·q).

## Practice problems
1. Range Sum Query - Immutable (LeetCode #303)
2. Contiguous Array (LeetCode #525)
3. Subarray Sum Equals K (LeetCode #560) — the trickier variant: uses a hash map of prefix-sum → count instead of a plain array, to find subarrays summing to k in O(n)

## Related
- [[01-arrays|arrays]]
- [[01-algorithms|algorithms]]
