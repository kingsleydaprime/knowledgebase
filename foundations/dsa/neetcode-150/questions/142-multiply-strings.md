# Multiply Strings

**LeetCode 43** · Math & Geometry · concept: [[14-math-and-geometry|math-and-geometry]]

## Problem

Multiply two non-negative integers given as **strings**, without converting them to native integers (they may be huge).

```
"123" * "456"  ->  "56088"
```

## Approach — grade-school multiplication into a digit array (optimal)

Digit `i` of one number times digit `j` of the other lands in positions `i+j` and `i+j+1` of the result (the carry position). Accumulate all products into an `m+n` digit array, then resolve carries.

```python
def multiply(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"
    m, n = len(num1), len(num2)
    res = [0] * (m + n)
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            mul = int(num1[i]) * int(num2[j])
            p1, p2 = i + j, i + j + 1              # positions of the product
            total = mul + res[p2]
            res[p2] = total % 10                   # digit
            res[p1] += total // 10                 # carry into the higher position
    result = "".join(map(str, res)).lstrip("0")    # drop leading zeros
    return result or "0"
```

**Time O(m·n), space O(m+n).**

## The position arithmetic

The key fact: multiplying the digit at index `i` (from the right, in reversed thinking) by the digit at index `j` contributes to result positions `i+j` (carry) and `i+j+1` (units). Laying every partial product into a fixed-size array and carrying at the end mirrors exactly how you multiply by hand — no big-integer type needed.

## Key insight

**Big-number arithmetic without native ints → simulate the schoolbook algorithm, tracking digit positions and carries in an array.** The `i+j` / `i+j+1` placement rule is the crux; it generalizes to any base and is the arithmetic cousin of [[141-pow-x-n|Pow]]'s and [[149-sum-of-two-integers|Sum of Two Integers]]' manual computation.

## Related
- concept: [[14-math-and-geometry|math-and-geometry]]
- prev: [[141-pow-x-n|Pow(x, n)]] · next: [[143-detect-squares|Detect Squares]]
