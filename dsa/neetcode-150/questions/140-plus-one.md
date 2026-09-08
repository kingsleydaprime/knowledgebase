# Plus One

**LeetCode 66** · Math & Geometry · concept: [[14-math-and-geometry|math-and-geometry]]

## Problem

A number is given as an array of digits (most-significant first). Add one and return the resulting digit array.

```
[1,2,3]  ->  [1,2,4]
[9,9,9]  ->  [1,0,0,0]
```

## Approach — carry from the right (optimal)

Walk from the **last** digit. If it's less than 9, increment and you're done — no carry propagates. If it's 9, it becomes 0 and the carry moves left. If every digit was 9, prepend a leading 1.

```python
def plusOne(digits):
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits              # no carry beyond here -> done
        digits[i] = 0                  # 9 -> 0, carry continues
    return [1] + digits                # all 9s: e.g. 999 -> 1000
```

**Time O(n), space O(1)** (or O(n) for the all-9s prepend).

## The all-nines case

The only time the array **grows** is `9…9 → 10…0`, needing a new leading digit. The early `return` on the first non-9 makes the common case cheap (stop as soon as the carry is absorbed); reaching the loop's end means every digit carried.

## Key insight

**Grade-school arithmetic on a digit array → propagate a carry from the least-significant end, handling the length-growth edge case.** Simple, but it's the base-10 version of the carry logic in [[040-add-two-numbers|Add Two Numbers]] and [[149-sum-of-two-integers|Sum of Two Integers]] — carrying is the unifying idea.

## Related
- concept: [[14-math-and-geometry|math-and-geometry]]
- relative: [[040-add-two-numbers|Add Two Numbers]]
- prev: [[139-happy-number|Happy Number]] · next: [[141-pow-x-n|Pow(x, n)]]
