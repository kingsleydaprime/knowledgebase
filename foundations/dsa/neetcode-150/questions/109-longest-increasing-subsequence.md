# Longest Increasing Subsequence

**LeetCode 300** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return the length of the longest strictly increasing **subsequence** (not necessarily contiguous).

```
[10,9,2,5,3,7,101,18]  ->  4   ([2,3,7,101])
```

## Approach 1 — DP, O(n²)

`dp[i]` = length of the longest increasing subsequence **ending at** `i`. It's `1 + max(dp[j])` over all earlier `j` with `nums[j] < nums[i]`.

```python
def lengthOfLIS(nums):
    dp = [1] * len(nums)                   # each element alone is an LIS of length 1
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

**Time O(n²), space O(n).**

## Approach 2 — patience sorting + binary search, O(n log n)

Maintain `tails`, where `tails[k]` is the **smallest possible tail** of an increasing subsequence of length `k+1`. For each number, binary-search the first tail ≥ it and replace it (or append if it extends all). The length of `tails` is the answer.

```python
import bisect

def lengthOfLIS(nums):
    tails = []
    for n in nums:
        i = bisect.bisect_left(tails, n)   # first tail >= n
        if i == len(tails):
            tails.append(n)                # n extends the longest subsequence
        else:
            tails[i] = n                   # n gives a smaller tail for that length
    return len(tails)
```

**Time O(n log n), space O(n).** `tails` isn't a valid subsequence itself — only its *length* is meaningful.

## Key insight

**LIS has two canonical solutions: O(n²) "best ending here" DP, and O(n log n) patience-sorting with binary search.** The binary-search version — keeping the smallest tail per length — is the reusable trick, and a great example of [[09-modified-binary-search|binary search]] accelerating a DP.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]], [[09-modified-binary-search|modified-binary-search]]
- prev: [[108-word-break|Word Break]] · next: [[110-partition-equal-subset-sum|Partition Equal Subset Sum]]
