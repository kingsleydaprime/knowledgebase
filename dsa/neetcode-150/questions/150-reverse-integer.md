# Reverse Integer

**LeetCode 7** · Bit Manipulation · concept: [[14-math-and-geometry|math-and-geometry]]

## Problem

Reverse the digits of a signed 32-bit integer. If reversing **overflows** the 32-bit range `[−2³¹, 2³¹−1]`, return 0.

```
123   ->  321
-123  ->  -321
120   ->  21
```

## Approach — pop and push digits, checking overflow *before* it happens

Peel the last digit with `% 10`, append it to the reversed number with `* 10 +`. The real problem is **overflow detection without a 64-bit type**: check *before* each multiply-and-add whether it would exceed the bounds.

```python
def reverse(x):
    INT_MAX, INT_MIN = 2**31 - 1, -2**31
    sign = -1 if x < 0 else 1
    x = abs(x)
    result = 0
    while x:
        digit = x % 10
        x //= 10
        # would result * 10 + digit overflow the positive bound?
        if result > (INT_MAX - digit) // 10:
            return 0
        result = result * 10 + digit
    return sign * result
```

**Time O(log x) (digit count), space O(1).**

## The overflow check is the whole problem

The digit reversal is trivial; the interview point is catching overflow **before** it corrupts the value. Rearranging `result * 10 + digit > INT_MAX` into `result > (INT_MAX - digit) // 10` tests the danger *without* actually computing the overflowing quantity — essential in fixed-width languages (Python wouldn't overflow, but the check models the constraint). Grouped with bit manipulation because it lives and dies by integer-bound reasoning.

## Key insight

**Digit reversal is easy; the skill is pre-emptive overflow checking** — test whether the next operation *would* exceed the bound and bail, rather than overflowing and detecting after. A discipline that applies to any bounded-integer arithmetic.

## Related
- concepts: [[14-math-and-geometry|math-and-geometry]], [[13-bit-manipulation|bit-manipulation]]
- relative: [[147-reverse-bits|Reverse Bits]] (same pop/push, on bits)
- prev: [[149-sum-of-two-integers|Sum of Two Integers]] — **end of the NeetCode 150** 🎉
