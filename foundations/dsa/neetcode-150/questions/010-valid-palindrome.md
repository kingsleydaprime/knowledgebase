# Valid Palindrome

**LeetCode 125** · Two Pointers · concept: [[02-two-pointers|two-pointers]]

## Problem

Return `true` if a string is a palindrome, considering **only alphanumeric characters** and ignoring case.

```
"A man, a plan, a canal: Panama"  -> true   (reads "amanaplanacanalpanama")
"race a car"                      -> false
```

## Approach 1 — clean then compare to its reverse

Strip non-alphanumerics, lowercase, and check against the reverse.

```python
def isPalindrome(s):
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]
```

**Time O(n), space O(n)** — the cleaned copy and its reverse are extra arrays. Perfectly acceptable, but it allocates two O(n) buffers.

## Approach 2 — two pointers in place (optimal space)

Walk one pointer in from each end. Skip anything non-alphanumeric on either side, compare the two characters case-insensitively, and step both inward. A mismatch means it's not a palindrome.

```python
def isPalindrome(s):
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum():   # skip junk on the left
            l += 1
        while l < r and not s[r].isalnum():   # skip junk on the right
            r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l, r = l + 1, r - 1
    return True
```

**Time O(n), space O(1).** Same linear time, but no allocation — the classic reason to prefer two pointers over build-and-reverse.

## Why the inner `l < r` guards matter

The skip loops need their own `l < r` check, or on an all-punctuation string (`",.,"`) a pointer can run past the other end and index out of bounds. Guarding inside every skip keeps the two pointers from crossing.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Clean + reverse | O(n) | O(n) |
| **Two pointers** | O(n) | **O(1)** |

## Key insight

**A palindrome check is symmetric — compare from both ends inward.** That's the purest form of the two-pointer idea: two indices moving toward each other, O(1) space. The "skip characters that don't count" variation (here, non-alphanumerics) recurs whenever you filter while scanning.

## Related
- concept: [[02-two-pointers|two-pointers]]
- next: [[011-two-sum-ii|Two Sum II]] — two pointers driven by a sum comparison
