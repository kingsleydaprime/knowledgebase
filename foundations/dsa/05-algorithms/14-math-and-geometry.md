# Math & Geometry

A grab-bag category, unified less by a shared algorithm than by a shared demand: **manipulate numbers or grid coordinates directly and carefully**, often *in place* and often with an arithmetic trick that avoids the obvious extra space. Interviews use these to test precision with indices, overflow, and simulation — the kind of bug-prone code that separates "knows the idea" from "can actually write it."

## In-place matrix manipulation

The recurring theme: transform a grid **without allocating a second grid**, by reasoning about which cells swap or which markers you can reuse.

**Rotate Image (90° clockwise, in place).** The clean decomposition: **transpose** (swap `m[i][j]` with `m[j][i]`), then **reverse each row**. Together those equal a 90° clockwise rotation, and both steps are in-place swaps.

```python
def rotate(matrix):
    n = len(matrix)
    for i in range(n):                          # transpose across the main diagonal
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:                          # reverse each row
        row.reverse()
```

**Spiral Matrix.** Walk the grid in rings, maintaining four shrinking boundaries — `top, bottom, left, right` — and peel off one edge at a time (top row L→R, right column T→B, bottom row R→L, left column B→T), moving the boundary inward after each. The whole difficulty is not double-visiting the last row/column when the remaining region is a single line.

**Set Matrix Zeroes.** The naive fix uses O(m+n) marker arrays to record which rows/columns to zero. The O(1)-space trick: **use the first row and first column of the matrix itself as those marker arrays**, with two extra booleans to remember whether the first row/column were themselves originally zero. A classic "reuse the input as your scratch space" move.

## Number tricks

**Pow(x, n) — fast (binary) exponentiation.** Computing `xⁿ` by multiplying x by itself n times is O(n). **Exponentiation by squaring** is O(log n): `xⁿ = (x²)^(n/2)` when n is even, `x · x^(n-1)` when odd — halving the exponent each step. This same "square to halve the exponent" idea is what makes Fibonacci-by-matrix-power O(log n) (see [[../06-patterns/15-dynamic-programming|DP]]).

```python
def my_pow(x, n):
    if n < 0:
        x, n = 1 / x, -n
    result = 1
    while n:
        if n & 1:            # if the current lowest bit is set, fold x in
            result *= x
        x *= x               # square the base
        n >>= 1              # drop the lowest bit
    return result
```

The bit test (`n & 1`, `n >>= 1`) ties this directly to [[13-bit-manipulation|bit manipulation]] — you're walking the binary digits of the exponent.

**Happy Number — cycle detection on a number sequence.** Repeatedly replacing a number by the sum of the squares of its digits either reaches 1 (happy) or loops forever. Detect the loop with a `seen` set, or with **Floyd's fast/slow pointers** ([[../06-patterns/04-fast-slow-pointers|fast-slow]]) — the sequence is functionally a linked list where "next" is the digit-square-sum, so a cycle there is the same cycle a linked list has.

**Plus One / Multiply Strings — grade-school arithmetic by hand.** When the number is too big for a native int (or you're told not to convert), simulate addition/multiplication digit by digit, right to left, carrying — the same full-adder logic as [[13-bit-manipulation|Sum of Two Integers]] but in base 10.

**Detect Squares — counting via a hash map of points.** Geometry that's really [[../04-data-structures/03-hash-maps|hashing]]: to count axis-aligned squares through a query point, for each point sharing a diagonal, check whether the other two corners exist — using a point-count map for O(1) corner lookups.

## Complexity notes

The theme across the category is **beating the obvious bound with a trick**, and being able to name it:

| Problem | Naive | Trick | Result |
|---|---|---|---|
| Pow(x, n) | O(n) | exponent halving | O(log n) |
| Rotate / Set Zeroes | O(n²) space | in-place reuse | O(1) space |
| Happy Number | — | cycle detection | O(1) space (fast/slow) |

## Gotchas

- **Integer overflow** — the ever-present hazard (Reverse Integer, Multiply Strings, Pow). Check bounds *before* the operation that would overflow; in fixed-width languages, mask or use a wider type.
- **In-place means order-of-operations matters** — in Rotate/Set-Zeroes, doing steps in the wrong order corrupts data you still need to read.
- **Off-by-one on shrinking boundaries** (Spiral) — the single-row/single-column remainder is where the bug lives; test on non-square grids.
- **Negative/zero exponents** (Pow) — handle `n < 0` (reciprocal) and `n == 0` (→ 1) explicitly.

## Canonical problems (NeetCode Math & Geometry)

Rotate Image · Spiral Matrix · Set Matrix Zeroes · Happy Number · Plus One · Pow(x, n) · Multiply Strings · Detect Squares.

## Related
- [[13-bit-manipulation|Bit manipulation]] — the binary-exponent and grade-school-arithmetic cousins
- [[07-number-theory-basics|Number theory basics]] — GCD, primes, modular arithmetic
- [[../06-patterns/04-fast-slow-pointers|Fast & slow pointers]] — Happy Number's cycle detection
- [[../06-patterns/13-matrix-traversal|Matrix traversal]] — the *graph* view of a grid (connectivity), as opposed to the *geometry* view here
