# Pow(x, n)

**LeetCode 50** · Math & Geometry · concepts: [[14-math-and-geometry|math-and-geometry]], [[13-bit-manipulation|bit-manipulation]]

## Problem

Compute `x` raised to the power `n` (`n` may be negative).

## Approach — fast (binary) exponentiation (optimal)

Multiplying `x` by itself `n` times is O(n). **Exponentiation by squaring** is O(log n): `xⁿ = (x²)^(n/2)` for even `n`, and `x · x^(n−1)` for odd `n` — halving the exponent each step. Reading the exponent's **binary digits**, you square the base each step and multiply it into the result whenever the current bit is set.

```python
def myPow(x, n):
    if n < 0:                          # x^-n = (1/x)^n
        x, n = 1 / x, -n
    result = 1
    while n:
        if n & 1:                      # current lowest bit set -> include this power of x
            result *= x
        x *= x                         # square the base for the next bit
        n >>= 1                        # move to the next bit
    return result
```

**Time O(log n), space O(1).**

## Why squaring halves the work

Each squaring doubles the exponent that `x` represents (`x`, `x²`, `x⁴`, `x⁸`, …). The binary representation of `n` says which of those powers to multiply together — so you need only `log₂ n` multiplications instead of `n`. The `n & 1` / `n >>= 1` walk over `n`'s bits is why this ties directly to [[13-bit-manipulation|bit manipulation]].

## Key insight

**Exponentiation (or any associative "repeat k times") → binary exponentiation, O(log n) via squaring.** The same doubling idea powers matrix exponentiation (O(log n) Fibonacci) and modular exponentiation in cryptography.

## Related
- concepts: [[14-math-and-geometry|math-and-geometry]], [[13-bit-manipulation|bit-manipulation]]
- prev: [[140-plus-one|Plus One]] · next: [[142-multiply-strings|Multiply Strings]]
